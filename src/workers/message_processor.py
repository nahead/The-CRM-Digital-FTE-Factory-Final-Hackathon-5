"""
Unified Message Processor Worker
Consumes messages from Kafka and processes them with the AI agent
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from kafka_client import FTEKafkaConsumer, FTEKafkaProducer, TOPICS
from agent.openai_agent import get_agent, Channel
from channels.email_handler import EmailHandler
from channels.whatsapp_handler import WhatsAppHandler
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedMessageProcessor:
    """Process incoming messages from all channels through the FTE agent."""

    def __init__(self):
        self.agent = get_agent()
        self.producer = FTEKafkaProducer()
        self.db_pool = None

        # Initialize channel handlers
        try:
            self.email_handler = EmailHandler()
            logger.info("Email handler initialized")
        except Exception as e:
            logger.warning(f"Email handler not available: {e}")
            self.email_handler = None

        try:
            self.whatsapp_handler = WhatsAppHandler()
            logger.info("WhatsApp handler initialized")
        except Exception as e:
            logger.warning(f"WhatsApp handler not available: {e}")
            self.whatsapp_handler = None

    async def start(self):
        """Start the message processor."""
        logger.info("Starting Unified Message Processor...")

        # Initialize database pool
        await self._init_db_pool()

        # Start Kafka producer
        await self.producer.start()
        logger.info("Kafka producer started")

        # Start Kafka consumer
        consumer = FTEKafkaConsumer(
            topics=[TOPICS['tickets_incoming']],
            group_id='fte-message-processor'
        )
        await consumer.start()

        logger.info("Message processor started, listening for tickets...")
        logger.info(f"Consuming from topic: {TOPICS['tickets_incoming']}")

        # Start consuming messages
        await consumer.consume(self.process_message)

    async def _init_db_pool(self):
        """Initialize database connection pool"""
        try:
            self.db_pool = await asyncpg.create_pool(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=int(os.getenv('POSTGRES_PORT', 5433)),
                database=os.getenv('POSTGRES_DB', 'fte_db'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres123'),
                min_size=2,
                max_size=10
            )
            logger.info("Database pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise

    async def process_message(self, event: Dict[str, Any]):
        """Process a single incoming message from any channel."""
        try:
            start_time = datetime.utcnow()

            # Extract message from event
            message = event
            topic = event.get('topic', '')

            logger.info(f"Processing message from {message.get('channel')}: {message.get('subject', 'No subject')}")

            # Extract channel
            channel = Channel(message['channel'])

            # Get or create customer
            customer_id = await self.resolve_customer(message)
            logger.info(f"Customer resolved: {customer_id}")

            # Get or create conversation
            conversation_id = await self.get_or_create_conversation(
                customer_id=customer_id,
                channel=channel,
                message=message
            )
            logger.info(f"Conversation: {conversation_id}")

            # Store incoming message
            await self.store_message(
                conversation_id=conversation_id,
                channel=channel,
                direction='inbound',
                role='customer',
                content=message['content'],
                channel_message_id=message.get('channel_message_id')
            )

            # Load conversation history
            history = await self.load_conversation_history(conversation_id)

            # Run agent
            logger.info("Invoking AI agent...")
            result = await self.agent.run(
                messages=history,
                context={
                    'customer_id': customer_id,
                    'conversation_id': conversation_id,
                    'channel': channel.value,
                    'ticket_subject': message.get('subject', 'Support Request'),
                    'metadata': message.get('metadata', {})
                }
            )

            # Calculate metrics
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Store agent response
            await self.store_message(
                conversation_id=conversation_id,
                channel=channel,
                direction='outbound',
                role='agent',
                content=result.get('output', ''),
                latency_ms=int(latency_ms),
                tool_calls=result.get('tool_calls', [])
            )

            # Send response via appropriate channel
            await self.send_response(message, result.get('output', ''), channel)

            # Publish metrics
            await self.producer.publish(TOPICS['metrics'], {
                'event_type': 'message_processed',
                'channel': channel.value,
                'latency_ms': latency_ms,
                'escalated': result.get('escalated', False),
                'tool_calls_count': len(result.get('tool_calls', []))
            })

            logger.info(f"✅ Processed {channel.value} message in {latency_ms:.0f}ms")

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()
            await self.handle_error(message, e)

    async def resolve_customer(self, message: Dict[str, Any]) -> str:
        """Resolve or create customer from message identifiers."""
        async with self.db_pool.acquire() as conn:
            # Try to find by email first
            if email := message.get('customer_email'):
                customer = await conn.fetchrow(
                    "SELECT id FROM customers WHERE email = $1", email
                )
                if customer:
                    return str(customer['id'])

                # Create new customer
                customer_id = await conn.fetchval("""
                    INSERT INTO customers (email, name, created_at, updated_at)
                    VALUES ($1, $2, NOW(), NOW())
                    RETURNING id
                """, email, message.get('customer_name', ''))

                # Add email identifier
                await conn.execute("""
                    INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
                    VALUES ($1, 'email', $2)
                """, customer_id, email)

                return str(customer_id)

            # Try phone for WhatsApp
            if phone := message.get('customer_phone'):
                identifier = await conn.fetchrow("""
                    SELECT customer_id FROM customer_identifiers
                    WHERE identifier_type = 'whatsapp' AND identifier_value = $1
                """, phone)

                if identifier:
                    return str(identifier['customer_id'])

                # Create new customer with phone
                customer_id = await conn.fetchval("""
                    INSERT INTO customers (phone, created_at, updated_at)
                    VALUES ($1, NOW(), NOW())
                    RETURNING id
                """, phone)

                await conn.execute("""
                    INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
                    VALUES ($1, 'whatsapp', $2)
                """, customer_id, phone)

                return str(customer_id)

        raise ValueError("Could not resolve customer from message")

    async def get_or_create_conversation(
        self,
        customer_id: str,
        channel: Channel,
        message: Dict[str, Any]
    ) -> str:
        """Get active conversation or create new one."""
        async with self.db_pool.acquire() as conn:
            # Check for active conversation (within last 24 hours)
            active = await conn.fetchrow("""
                SELECT id FROM conversations
                WHERE customer_id = $1
                  AND status = 'active'
                  AND started_at > NOW() - INTERVAL '24 hours'
                ORDER BY started_at DESC
                LIMIT 1
            """, customer_id)

            if active:
                return str(active['id'])

            # Create new conversation
            conversation_id = await conn.fetchval("""
                INSERT INTO conversations (customer_id, initial_channel, status, started_at)
                VALUES ($1, $2, 'active', NOW())
                RETURNING id
            """, customer_id, channel.value)

            return str(conversation_id)

    async def store_message(
        self,
        conversation_id: str,
        channel: Channel,
        direction: str,
        role: str,
        content: str,
        channel_message_id: str = None,
        latency_ms: int = None,
        tool_calls: list = None
    ):
        """Store message in database."""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO messages (
                    conversation_id, channel, direction, role, content,
                    channel_message_id, latency_ms, tool_calls, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
            """, conversation_id, channel.value, direction, role, content,
                channel_message_id, latency_ms, tool_calls or [])

    async def load_conversation_history(self, conversation_id: str) -> list:
        """Load conversation history for agent context."""
        async with self.db_pool.acquire() as conn:
            messages = await conn.fetch("""
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at ASC
                LIMIT 20
            """, conversation_id)

            return [
                {
                    'role': msg['role'],
                    'content': msg['content']
                }
                for msg in messages
            ]

    async def send_response(self, original_message: Dict, response: str, channel: Channel):
        """Send response via appropriate channel."""
        try:
            if channel == Channel.EMAIL and self.email_handler:
                await self.email_handler.send_email(
                    to_email=original_message['customer_email'],
                    subject=f"Re: {original_message.get('subject', 'Support Request')}",
                    body=response,
                    thread_id=original_message.get('thread_id')
                )
                logger.info(f"✉️  Email response sent to {original_message['customer_email']}")

            elif channel == Channel.WHATSAPP and self.whatsapp_handler:
                await self.whatsapp_handler.send_message(
                    to_phone=original_message['customer_phone'],
                    body=response
                )
                logger.info(f"💬 WhatsApp response sent to {original_message['customer_phone']}")

            else:
                # Web form - response stored in database, email notification sent
                logger.info(f"🌐 Web form response stored (email notification would be sent)")

        except Exception as e:
            logger.error(f"Failed to send response via {channel.value}: {e}")

    async def handle_error(self, message: Dict[str, Any], error: Exception):
        """Handle processing errors gracefully."""
        channel = Channel(message['channel'])
        apology = "I'm sorry, I'm having trouble processing your request right now. A human agent will follow up shortly."

        try:
            # Send apologetic response
            if channel == Channel.EMAIL and self.email_handler:
                await self.email_handler.send_email(
                    to_email=message['customer_email'],
                    subject=message.get('subject', 'Support Request'),
                    body=apology
                )
            elif channel == Channel.WHATSAPP and self.whatsapp_handler:
                await self.whatsapp_handler.send_message(
                    to_phone=message['customer_phone'],
                    body=apology
                )
        except Exception as e:
            logger.error(f"Failed to send error response: {e}")

        # Publish for human review
        await self.producer.publish(TOPICS['escalations'], {
            'event_type': 'processing_error',
            'original_message': message,
            'error': str(error),
            'requires_human': True,
            'timestamp': datetime.utcnow().isoformat()
        })


async def main():
    """Main entry point for the worker."""
    logger.info("=" * 60)
    logger.info("Customer Success FTE - Message Processor Worker")
    logger.info("=" * 60)

    processor = UnifiedMessageProcessor()

    try:
        await processor.start()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
