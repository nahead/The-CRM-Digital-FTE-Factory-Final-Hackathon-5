"""
In-Memory Event Streaming (Kafka Replacement)
Provides Kafka-like functionality without external dependencies
Production-ready for hackathon demonstration
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Callable, List, Optional
from collections import defaultdict
import os


# Kafka topics for multi-channel FTE
TOPICS = {
    # Incoming tickets from all channels
    'tickets_incoming': 'fte.tickets.incoming',

    # Channel-specific inbound
    'email_inbound': 'fte.channels.email.inbound',
    'whatsapp_inbound': 'fte.channels.whatsapp.inbound',
    'webform_inbound': 'fte.channels.webform.inbound',

    # Channel-specific outbound
    'email_outbound': 'fte.channels.email.outbound',
    'whatsapp_outbound': 'fte.channels.whatsapp.outbound',

    # Escalations
    'escalations': 'fte.escalations',

    # Metrics and monitoring
    'metrics': 'fte.metrics',

    # Dead letter queue for failed processing
    'dlq': 'fte.dlq'
}


class InMemoryEventBus:
    """In-memory event bus that mimics Kafka functionality"""

    def __init__(self):
        self.topics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.running = False

    async def publish(self, topic: str, event: Dict[str, Any]):
        """Publish event to topic"""
        event["timestamp"] = datetime.utcnow().isoformat()
        event["topic"] = topic

        # Store event
        self.topics[topic].append(event)

        # Notify subscribers
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                try:
                    await callback(event)
                except Exception as e:
                    print(f"Error in subscriber callback: {e}")

        print(f"✅ Event published to {topic}")

    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to topic"""
        self.subscribers[topic].append(callback)
        print(f"✅ Subscribed to {topic}")

    def get_events(self, topic: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events from topic"""
        return self.topics[topic][-limit:]

    def clear_topic(self, topic: str):
        """Clear all events from topic"""
        self.topics[topic].clear()


# Global event bus instance
_event_bus = InMemoryEventBus()


class FTEKafkaProducer:
    """Kafka producer (in-memory implementation)"""

    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.producer = _event_bus
        self.connected = True

    async def start(self):
        """Start the Kafka producer"""
        print(f"✅ In-memory event bus initialized (Kafka replacement)")
        self.connected = True

    async def stop(self):
        """Stop the Kafka producer"""
        self.connected = False

    async def publish(self, topic: str, event: Dict[str, Any]):
        """
        Publish event to Kafka topic

        Args:
            topic: Topic name
            event: Event data
        """
        if not self.connected:
            raise Exception("Event bus not connected")

        await self.producer.publish(topic, event)


class FTEKafkaConsumer:
    """Kafka consumer (in-memory implementation)"""

    def __init__(self, topics: List[str], group_id: str):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topics = topics
        self.group_id = group_id
        self.consumer = _event_bus
        self.running = False

    async def start(self):
        """Start the Kafka consumer"""
        print(f"✅ Consumer started for topics: {', '.join(self.topics)}")
        self.running = True

    async def stop(self):
        """Stop the Kafka consumer"""
        self.running = False

    async def consume(self, callback: Callable):
        """
        Consume messages from subscribed topics

        Args:
            callback: Async function to process each message
        """
        # Subscribe to all topics
        for topic in self.topics:
            self.consumer.subscribe(topic, callback)

        print(f"✅ Consuming from topics: {', '.join(self.topics)}")

        # Keep running
        while self.running:
            await asyncio.sleep(1)

    def subscribe_to_topics(self, topics: List[str]):
        """Subscribe to additional topics"""
        self.topics.extend(topics)


# Convenience function to get event bus
def get_event_bus() -> InMemoryEventBus:
    """Get global event bus instance"""
    return _event_bus
