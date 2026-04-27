"""
Web Form Handler for FastAPI
Handles support form submissions from the website
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, List
import uuid
import asyncpg
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import Kafka client and OpenAI agent
import sys
sys.path.append(str(Path(__file__).parent.parent))
from kafka_client import FTEKafkaProducer, TOPICS
from agent.openai_agent import get_agent

# Initialize Kafka producer (singleton)
_kafka_producer = None

async def get_kafka_producer():
    """Get or create Kafka producer instance"""
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = FTEKafkaProducer()
        try:
            await _kafka_producer.start()
        except Exception as e:
            print(f"Warning: Kafka not available: {e}")
    return _kafka_producer


router = APIRouter(prefix="/support", tags=["support-form"])


# Database connection pool
_db_pool = None


async def get_db_pool():
    """Get or create database connection pool"""
    global _db_pool
    if _db_pool is None:
        db_host = os.getenv('POSTGRES_HOST', 'localhost')
        db_port = int(os.getenv('POSTGRES_PORT', 5432))
        db_name = os.getenv('POSTGRES_DB', 'fte_db')
        db_user = os.getenv('POSTGRES_USER', 'postgres')
        db_password = os.getenv('POSTGRES_PASSWORD', 'postgres123')

        print(f"Connecting to database: {db_host}:{db_port}/{db_name} as {db_user}")
        print(f"Password loaded: {'Yes' if db_password else 'No'}")

        _db_pool = await asyncpg.create_pool(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            min_size=2,
            max_size=10
        )
    return _db_pool


async def create_or_get_customer(email: str, name: str):
    """Create customer if not exists, return customer_id"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Check if customer exists
        customer = await conn.fetchrow(
            "SELECT id FROM customers WHERE email = $1",
            email
        )

        if customer:
            return customer['id']

        # Create new customer
        customer_id = await conn.fetchval(
            """
            INSERT INTO customers (email, name, created_at, updated_at)
            VALUES ($1, $2, NOW(), NOW())
            RETURNING id
            """,
            email, name
        )

        # Add email identifier
        await conn.execute(
            """
            INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
            VALUES ($1, 'email', $2)
            """,
            customer_id, email
        )

        return customer_id


async def create_ticket(ticket_id: str, customer_id: str, submission):
    """Create ticket in database with conversation"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Convert string IDs to UUID
        ticket_uuid = uuid.UUID(ticket_id) if isinstance(ticket_id, str) else ticket_id
        customer_uuid = uuid.UUID(customer_id) if isinstance(customer_id, str) else customer_id

        # First create conversation
        conversation_id = await conn.fetchval(
            """
            INSERT INTO conversations (
                customer_id, initial_channel, started_at, status
            )
            VALUES ($1, 'web_form', NOW(), 'active')
            RETURNING id
            """,
            customer_uuid
        )

        # Then create ticket with conversation_id
        await conn.execute(
            """
            INSERT INTO tickets (
                id, customer_id, conversation_id, subject, status,
                priority, source_channel, category, created_at
            )
            VALUES ($1, $2, $3, $4, 'open', $5, 'web_form', $6, NOW())
            """,
            ticket_uuid, customer_uuid, conversation_id,
            submission.subject, submission.priority, submission.category
        )

        # Store customer's initial message
        await conn.execute(
            """
            INSERT INTO messages (
                conversation_id, channel, direction, role, content, created_at
            )
            VALUES ($1, 'web_form', 'inbound', 'customer', $2, NOW())
            """,
            conversation_id, submission.message
        )

    return ticket_id


class SupportFormSubmission(BaseModel):
    """Support form submission model with validation"""
    name: str
    email: EmailStr
    subject: str
    category: str  # 'general', 'technical', 'billing', 'feedback', 'bug_report'
    message: str
    priority: Optional[str] = 'medium'
    attachments: Optional[List[str]] = []

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()

    @validator('message')
    def message_must_have_content(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters')
        return v.strip()

    @validator('category')
    def category_must_be_valid(cls, v):
        valid_categories = ['general', 'technical', 'billing', 'feedback', 'bug_report']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v


class SupportFormResponse(BaseModel):
    """Response model for form submission"""
    ticket_id: str
    message: str
    estimated_response_time: str


@router.post("/submit", response_model=SupportFormResponse)
async def submit_support_form(submission: SupportFormSubmission, background_tasks: BackgroundTasks):
    """
    Handle support form submission.

    This endpoint:
    1. Validates the submission
    2. Creates a ticket in the system
    3. Publishes to Kafka for agent processing
    4. Returns confirmation to user
    """
    try:
        ticket_id = str(uuid.uuid4())
        print(f"Creating ticket {ticket_id} for {submission.email}")

        # Create or get customer
        customer_id = await create_or_get_customer(submission.email, submission.name)
        print(f"Customer ID: {customer_id}")

        # Create ticket in database
        await create_ticket(ticket_id, customer_id, submission)
        print(f"Ticket created successfully in database")

        # Create normalized message for agent
        message_data = {
            'channel': 'web_form',
            'channel_message_id': ticket_id,
            'customer_email': submission.email,
            'customer_name': submission.name,
            'subject': submission.subject,
            'content': submission.message,
            'category': submission.category,
            'priority': submission.priority,
            'received_at': datetime.utcnow().isoformat(),
            'metadata': {
                'form_version': '1.0',
                'attachments': submission.attachments
            }
        }

        # Process with agent AND publish to Kafka (parallel)
        async def process_with_agent():
            # 1. Publish to Kafka for event streaming
            try:
                producer = await get_kafka_producer()
                await producer.publish(TOPICS['tickets_incoming'], message_data)
                print(f"[OK] Published ticket {ticket_id} to Kafka")
            except Exception as kafka_error:
                print(f"[WARN] Kafka publish failed: {kafka_error}")

            # 2. ALWAYS process with agent for immediate response
            try:
                agent = get_agent()

                # Process with agent
                result = await agent.run(
                    messages=[
                        {"role": "user", "content": submission.message}
                    ],
                    context={
                        'customer_id': customer_id,
                        'channel': 'web_form',
                        'subject': submission.subject,
                        'category': submission.category,
                        'priority': submission.priority,
                        'ticket_id': ticket_id
                    }
                )

                print(f"[OK] Agent processed ticket {ticket_id}")
                print(f"Response: {result.get('output', '')[:100]}...")

                # Store agent response in database
                db_pool = await get_db_pool()
                async with db_pool.acquire() as conn:
                    # Get conversation_id
                    conversation = await conn.fetchrow("""
                        SELECT c.id FROM conversations c
                        JOIN tickets t ON t.conversation_id = c.id
                        WHERE t.id = $1
                    """, uuid.UUID(ticket_id))

                    if conversation:
                        # Store agent's response
                        await conn.execute("""
                            INSERT INTO messages (conversation_id, channel, direction, role, content, created_at)
                            VALUES ($1, 'web_form', 'outbound', 'agent', $2, NOW())
                        """, conversation['id'], result.get('output', ''))

                        print(f"[OK] Stored agent response in database")

                        # Send email notification to customer
                        try:
                            from channels.email_handler import EmailHandler
                            email_handler = EmailHandler()

                            email_subject = f"Re: {submission.subject}"
                            email_body = f"""Dear {submission.name},

Thank you for contacting TechCorp Support.

{result.get('output', '')}

If you have any further questions, please don't hesitate to reply to this email or submit another request through our support portal.

Best regards,
TechCorp AI Support Team

---
Ticket Reference: {ticket_id}
This response was generated by our AI assistant. For complex issues, you can request human support by replying to this email.
"""

                            email_result = email_handler.send_email(
                                to_email=submission.email,
                                subject=email_subject,
                                body=email_body
                            )

                            print(f"[OK] Email sent to {submission.email}: {email_result.get('delivery_status', 'sent')}")

                        except Exception as email_error:
                            print(f"[WARN] Email notification failed (response still stored): {email_error}")
                            # Don't fail the whole process if email fails

            except Exception as agent_error:
                print(f"❌ Agent processing failed: {agent_error}")
                import traceback
                traceback.print_exc()

        background_tasks.add_task(process_with_agent)

        return SupportFormResponse(
            ticket_id=ticket_id,
            message="Thank you for contacting us! Our AI assistant will respond shortly.",
            estimated_response_time="Usually within 5 minutes"
        )

    except Exception as e:
        print(f"Error creating ticket: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to create ticket")


@router.get("/ticket/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """Get status and conversation history for a ticket"""
    try:
        # Validate ticket_id format (must be valid UUID)
        try:
            ticket_uuid = uuid.UUID(ticket_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ticket ID format. Must be a valid UUID.")

        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            # Get ticket details
            ticket = await conn.fetchrow("""
                SELECT t.id, t.status, t.category, t.priority, t.created_at,
                       c.id as conversation_id, c.initial_channel,
                       cu.name as customer_name, cu.email as customer_email
                FROM tickets t
                JOIN conversations c ON t.conversation_id = c.id
                JOIN customers cu ON t.customer_id = cu.id
                WHERE t.id = $1
            """, ticket_uuid)

            if not ticket:
                raise HTTPException(status_code=404, detail="Ticket not found")

            # Get all messages in the conversation
            messages = await conn.fetch("""
                SELECT role, content, channel, direction, created_at
                FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at ASC
            """, ticket['conversation_id'])

            # Format messages
            formatted_messages = [
                {
                    'role': msg['role'],
                    'content': msg['content'],
                    'channel': msg['channel'],
                    'direction': msg['direction'],
                    'timestamp': msg['created_at'].isoformat()
                }
                for msg in messages
            ]

            return {
                'ticket_id': ticket_id,
                'status': ticket['status'],
                'category': ticket['category'],
                'priority': ticket['priority'],
                'customer_name': ticket['customer_name'],
                'customer_email': ticket['customer_email'],
                'channel': ticket['initial_channel'],
                'messages': formatted_messages,
                'created_at': ticket['created_at'].isoformat(),
                'last_updated': messages[-1]['created_at'].isoformat() if messages else ticket['created_at'].isoformat()
            }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching ticket: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch ticket status")
