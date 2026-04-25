"""
Agent Tools Implementation
Functions that the Gemini agent can call
"""

import asyncpg
import os
from typing import Optional, List, Dict
from datetime import datetime
import json


# Database connection pool (will be initialized on startup)
_db_pool = None


async def get_db_pool():
    """Get or create database connection pool"""
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            database=os.getenv('POSTGRES_DB', 'fte_db'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres123'),
            min_size=5,
            max_size=20
        )
    return _db_pool


async def search_knowledge_base(query: str, max_results: int = 5) -> str:
    """
    Search product documentation for relevant information.

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        Formatted search results
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Simple text search (in production, use vector embeddings)
            results = await conn.fetch("""
                SELECT title, content, category
                FROM knowledge_base
                WHERE
                    title ILIKE $1 OR
                    content ILIKE $1
                ORDER BY
                    CASE
                        WHEN title ILIKE $1 THEN 1
                        ELSE 2
                    END
                LIMIT $2
            """, f"%{query}%", max_results)

            if not results:
                return "No relevant documentation found. Consider escalating to human support."

            # Format results
            formatted = []
            for r in results:
                formatted.append(
                    f"**{r['title']}** (Category: {r['category']})\n{r['content'][:300]}..."
                )

            return "\n\n---\n\n".join(formatted)

    except Exception as e:
        return f"Knowledge base temporarily unavailable: {str(e)}"


async def create_ticket(
    customer_id: str,
    issue: str,
    channel: str,
    priority: str = "medium",
    category: Optional[str] = None
) -> str:
    """
    Create a support ticket in the system.

    Args:
        customer_id: Customer UUID
        issue: Brief description of issue
        channel: Source channel (email, whatsapp, web_form)
        priority: Priority level
        category: Issue category

    Returns:
        Ticket ID
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Get or create conversation
            conversation_id = await conn.fetchval("""
                INSERT INTO conversations (customer_id, initial_channel, status)
                VALUES ($1, $2, 'active')
                RETURNING id
            """, customer_id, channel)

            # Create ticket
            ticket_id = await conn.fetchval("""
                INSERT INTO tickets (
                    conversation_id,
                    customer_id,
                    source_channel,
                    subject,
                    category,
                    priority,
                    status
                )
                VALUES ($1, $2, $3, $4, $5, $6, 'open')
                RETURNING id
            """, conversation_id, customer_id, channel, issue[:500], category, priority)

            return f"Ticket created: {ticket_id}"

    except Exception as e:
        return f"Failed to create ticket: {str(e)}"


async def get_customer_history(customer_id: str) -> str:
    """
    Get customer's interaction history across ALL channels.

    Args:
        customer_id: Customer UUID

    Returns:
        Formatted customer history
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            history = await conn.fetch("""
                SELECT
                    c.initial_channel,
                    c.started_at,
                    c.status,
                    m.content,
                    m.role,
                    m.channel,
                    m.created_at
                FROM conversations c
                JOIN messages m ON m.conversation_id = c.id
                WHERE c.customer_id = $1
                ORDER BY m.created_at DESC
                LIMIT 20
            """, customer_id)

            if not history:
                return "No previous interactions found for this customer."

            # Format history
            formatted = ["## Customer History\n"]
            for h in history:
                channel_icon = {
                    'email': '📧',
                    'whatsapp': '📱',
                    'web_form': '🌐'
                }.get(h['channel'], '💬')

                formatted.append(
                    f"{channel_icon} **{h['channel'].upper()}** - {h['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
                    f"{h['role'].upper()}: {h['content'][:200]}...\n"
                )

            return "\n".join(formatted)

    except Exception as e:
        return f"Failed to retrieve history: {str(e)}"


async def escalate_to_human(
    ticket_id: str,
    reason: str,
    urgency: str = "normal"
) -> str:
    """
    Escalate conversation to human support.

    Args:
        ticket_id: Ticket UUID
        reason: Reason for escalation
        urgency: Urgency level

    Returns:
        Escalation confirmation
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE tickets
                SET
                    status = 'escalated',
                    resolution_notes = $1
                WHERE id = $2
            """, f"Escalation reason: {reason} (Urgency: {urgency})", ticket_id)

            # TODO: Publish to Kafka for human agents

            return f"Escalated to human support. Reference: {ticket_id}"

    except Exception as e:
        return f"Failed to escalate: {str(e)}"


async def send_response(
    ticket_id: str,
    message: str,
    channel: str
) -> str:
    """
    Send response to customer via appropriate channel.

    Args:
        ticket_id: Ticket UUID
        message: Response message
        channel: Target channel

    Returns:
        Delivery status
    """
    try:
        # Format response for channel
        formatted = await format_for_channel(message, channel)

        # TODO: Actually send via channel (Gmail API, Twilio, etc.)
        # For now, just log it

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Get ticket info
            ticket = await conn.fetchrow("""
                SELECT conversation_id FROM tickets WHERE id = $1
            """, ticket_id)

            if ticket:
                # Store outbound message
                await conn.execute("""
                    INSERT INTO messages (
                        conversation_id,
                        channel,
                        direction,
                        role,
                        content,
                        delivery_status
                    )
                    VALUES ($1, $2, 'outbound', 'agent', $3, 'sent')
                """, ticket['conversation_id'], channel, formatted)

        return f"Response sent via {channel}"

    except Exception as e:
        return f"Failed to send response: {str(e)}"


async def format_for_channel(response: str, channel: str) -> str:
    """Format response appropriately for the channel"""

    if channel == "email":
        return f"""Dear Customer,

Thank you for reaching out to TechCorp Support.

{response}

If you have any further questions, please don't hesitate to reply to this email.

Best regards,
TechCorp AI Support Team
---
This response was generated by our AI assistant.
"""

    elif channel == "whatsapp":
        # Keep it short for WhatsApp
        if len(response) > 300:
            response = response[:297] + "..."
        return f"{response}\n\n📱 Reply for more help or type 'human' for live support."

    else:  # web_form
        return f"""{response}

---
Need more help? Reply to this message or visit our support portal.
"""
