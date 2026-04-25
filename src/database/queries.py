"""
Database Queries Helper
Common database operations for the FTE system
"""

import asyncpg
import os
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid


async def get_db_pool():
    """Get or create database connection pool"""
    return await asyncpg.create_pool(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        database=os.getenv('POSTGRES_DB', 'fte_db'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres123'),
        min_size=5,
        max_size=20
    )


async def get_or_create_customer(
    pool: asyncpg.Pool,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None
) -> str:
    """
    Get or create customer by email or phone

    Args:
        pool: Database connection pool
        email: Customer email
        phone: Customer phone
        name: Customer name

    Returns:
        Customer UUID
    """
    async with pool.acquire() as conn:
        # Try to find by email
        if email:
            customer = await conn.fetchrow(
                "SELECT id FROM customers WHERE email = $1", email
            )
            if customer:
                return str(customer['id'])

            # Create new customer
            customer_id = await conn.fetchval("""
                INSERT INTO customers (email, name)
                VALUES ($1, $2)
                RETURNING id
            """, email, name or '')
            return str(customer_id)

        # Try to find by phone
        if phone:
            identifier = await conn.fetchrow("""
                SELECT customer_id FROM customer_identifiers
                WHERE identifier_type = 'phone' AND identifier_value = $1
            """, phone)

            if identifier:
                return str(identifier['customer_id'])

            # Create new customer with phone
            customer_id = await conn.fetchval("""
                INSERT INTO customers (phone, name) VALUES ($1, $2) RETURNING id
            """, phone, name or '')

            await conn.execute("""
                INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
                VALUES ($1, 'phone', $2)
            """, customer_id, phone)

            return str(customer_id)

    raise ValueError("Either email or phone must be provided")


async def create_conversation(
    pool: asyncpg.Pool,
    customer_id: str,
    channel: str
) -> str:
    """
    Create a new conversation

    Args:
        pool: Database connection pool
        customer_id: Customer UUID
        channel: Channel name

    Returns:
        Conversation UUID
    """
    async with pool.acquire() as conn:
        conversation_id = await conn.fetchval("""
            INSERT INTO conversations (customer_id, initial_channel, status)
            VALUES ($1, $2, 'active')
            RETURNING id
        """, customer_id, channel)
        return str(conversation_id)


async def store_message(
    pool: asyncpg.Pool,
    conversation_id: str,
    channel: str,
    direction: str,
    role: str,
    content: str,
    channel_message_id: Optional[str] = None
) -> str:
    """
    Store a message in the database

    Args:
        pool: Database connection pool
        conversation_id: Conversation UUID
        channel: Channel name
        direction: 'inbound' or 'outbound'
        role: 'customer', 'agent', or 'system'
        content: Message content
        channel_message_id: External message ID

    Returns:
        Message UUID
    """
    async with pool.acquire() as conn:
        message_id = await conn.fetchval("""
            INSERT INTO messages (
                conversation_id,
                channel,
                direction,
                role,
                content,
                channel_message_id
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """, conversation_id, channel, direction, role, content, channel_message_id)
        return str(message_id)


async def load_conversation_history(
    pool: asyncpg.Pool,
    conversation_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Load conversation history

    Args:
        pool: Database connection pool
        conversation_id: Conversation UUID
        limit: Maximum number of messages

    Returns:
        List of message dicts
    """
    async with pool.acquire() as conn:
        messages = await conn.fetch("""
            SELECT
                id,
                channel,
                direction,
                role,
                content,
                created_at,
                channel_message_id
            FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at ASC
            LIMIT $2
        """, conversation_id, limit)

        return [dict(msg) for msg in messages]


async def update_delivery_status(
    pool: asyncpg.Pool,
    channel_message_id: str,
    status: str
):
    """
    Update message delivery status

    Args:
        pool: Database connection pool
        channel_message_id: External message ID
        status: Delivery status
    """
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE messages
            SET delivery_status = $1
            WHERE channel_message_id = $2
        """, status, channel_message_id)


async def record_metric(
    pool: asyncpg.Pool,
    metric_name: str,
    metric_value: float,
    channel: Optional[str] = None,
    dimensions: Optional[Dict] = None
):
    """
    Record a performance metric

    Args:
        pool: Database connection pool
        metric_name: Metric name
        metric_value: Metric value
        channel: Optional channel name
        dimensions: Optional additional dimensions
    """
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO agent_metrics (
                metric_name,
                metric_value,
                channel,
                dimensions
            )
            VALUES ($1, $2, $3, $4)
        """, metric_name, metric_value, channel, dimensions or {})
