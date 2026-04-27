"""
FastAPI Main Application
Multi-channel Customer Success FTE API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import channel handlers
import sys
from pathlib import Path
# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from channels.web_form_handler import router as web_form_router
from channels.email_handler import EmailHandler
from channels.whatsapp_handler import WhatsAppHandler

# Import agent
from agent.openai_agent import get_agent

# Import Kafka client
from kafka_client import FTEKafkaProducer, TOPICS

# Initialize WhatsApp handler
try:
    whatsapp_handler = WhatsAppHandler()
    print("WhatsApp handler initialized successfully")
except Exception as e:
    print(f"WhatsApp handler initialization failed: {e}")
    whatsapp_handler = None

# Initialize Email handler
try:
    import os
    # __file__ is src/api/main.py, so go up 3 levels to project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    email_handler = EmailHandler(
        credentials_path=os.path.join(project_root, 'credentials', 'gmail_credentials.json'),
        token_path=os.path.join(project_root, 'credentials', 'gmail_token.pickle')
    )
    print("Email handler initialized successfully")
except Exception as e:
    print(f"Email handler initialization failed: {e}")
    email_handler = None

# Initialize Kafka producer
kafka_producer = FTEKafkaProducer()


app = FastAPI(
    title="Customer Success FTE API",
    description="24/7 AI-powered customer support across Email, WhatsApp, and Web",
    version="1.0.0"
)

# CORS for web form
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include web form router
app.include_router(web_form_router)


@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    print("Starting Customer Success FTE API...")
    print(f"Time: {datetime.utcnow().isoformat()}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Initialize agent
    try:
        agent = get_agent()
        print("Gemini agent initialized")
    except Exception as e:
        print(f"Warning: Could not initialize agent: {e}")

    # Initialize Kafka producer
    try:
        await kafka_producer.start()
        print("Kafka producer initialized successfully")
    except Exception as e:
        print(f"Warning: Kafka producer initialization failed: {e}")
        print("API will continue without Kafka event streaming")

    print("API ready to accept requests")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("Shutting down Customer Success FTE API...")

    # Close Kafka producer
    try:
        await kafka_producer.stop()
        print("Kafka producer stopped")
    except Exception as e:
        print(f"Error stopping Kafka producer: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Customer Success FTE API",
        "version": "1.0.0",
        "status": "running",
        "channels": ["email", "whatsapp", "web_form"],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "channels": {
            "email": "active",
            "whatsapp": "active",
            "web_form": "active"
        }
    }


@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle Gmail push notifications via Pub/Sub.
    """
    try:
        body = await request.json()

        # Process Gmail notification
        if email_handler:
            # In production, this would decode the Pub/Sub message and fetch new emails
            # For now, we'll check for unread messages
            messages = email_handler.get_unread_messages(max_results=5)

            # Publish each message to Kafka
            for message in messages:
                background_tasks.add_task(
                    kafka_producer.publish,
                    TOPICS['tickets_incoming'],
                    message
                )

            return {"status": "processed", "count": len(messages)}
        else:
            return {"status": "error", "message": "Email handler not initialized"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming WhatsApp messages via Twilio webhook.
    """
    try:
        if not whatsapp_handler:
            raise HTTPException(status_code=503, detail="WhatsApp handler not initialized")

        # Validate Twilio signature
        if not await whatsapp_handler.validate_webhook(request):
            raise HTTPException(status_code=403, detail="Invalid signature")

        form_data = await request.form()
        message = await whatsapp_handler.process_webhook(dict(form_data))

        print(f"Received WhatsApp message from {message['customer_phone']}: {message['content']}")

        # Process with agent immediately (like web_form does)
        async def process_and_respond():
            try:
                # 1. Publish to Kafka for event streaming
                try:
                    await kafka_producer.publish(TOPICS['tickets_incoming'], message)
                    print(f"[OK] Published WhatsApp message to Kafka")
                except Exception as kafka_error:
                    print(f"[WARN] Kafka publish failed: {kafka_error}")

                # 2. Create or get customer in database
                from channels.web_form_handler import get_db_pool, create_or_get_customer
                import uuid

                customer_id = await create_or_get_customer(
                    email=f"{message['customer_phone']}@whatsapp.temp",  # Temporary email for WhatsApp users
                    name=message.get('customer_name', message['customer_phone'])
                )
                print(f"[OK] Customer ID: {customer_id}")

                # 3. Create conversation and store customer message
                db_pool = await get_db_pool()
                async with db_pool.acquire() as conn:
                    # Create conversation
                    conversation_id = await conn.fetchval("""
                        INSERT INTO conversations (customer_id, initial_channel, started_at, status)
                        VALUES ($1, 'whatsapp', NOW(), 'active')
                        RETURNING id
                    """, uuid.UUID(customer_id))

                    # Store customer's message
                    await conn.execute("""
                        INSERT INTO messages (conversation_id, channel, direction, role, content, created_at)
                        VALUES ($1, 'whatsapp', 'inbound', 'customer', $2, NOW())
                    """, conversation_id, message['content'])

                    print(f"[OK] Conversation created: {conversation_id}")

                # 4. Process with agent
                agent = get_agent()
                result = await agent.run(
                    messages=[{"role": "user", "content": message['content']}],
                    context={
                        'channel': 'whatsapp',
                        'customer_phone': message['customer_phone'],
                        'customer_name': message.get('customer_name', ''),
                        'customer_id': customer_id,
                        'conversation_id': str(conversation_id)
                    }
                )

                print(f"[OK] Agent processed WhatsApp message")
                print(f"Response: {result.get('output', '')[:100]}...")

                # 5. Store agent response in database
                response_text = result.get('output', '')
                async with db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO messages (conversation_id, channel, direction, role, content, created_at)
                        VALUES ($1, 'whatsapp', 'outbound', 'agent', $2, NOW())
                    """, conversation_id, response_text)
                    print(f"[OK] Agent response stored in database")

                # 6. Send response via WhatsApp
                send_result = await whatsapp_handler.send_message(
                    to_phone=message['customer_phone'],
                    body=response_text
                )
                print(f"[OK] WhatsApp response sent to {message['customer_phone']}: {send_result.get('delivery_status', 'sent')}")

            except Exception as process_error:
                print(f"❌ WhatsApp processing failed: {process_error}")
                import traceback
                traceback.print_exc()

        background_tasks.add_task(process_and_respond)

        # Return TwiML response (empty = no immediate reply, agent will respond)
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )

    except Exception as e:
        print(f"WhatsApp webhook error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/whatsapp/status")
async def whatsapp_status_webhook(request: Request):
    """Handle WhatsApp message status updates (delivered, read, etc.)"""
    form_data = await request.form()

    # TODO: Update message delivery status
    # await update_delivery_status(
    #     channel_message_id=form_data.get('MessageSid'),
    #     status=form_data.get('MessageStatus')
    # )

    return {"status": "received"}


# Removed duplicate endpoint - using the one at line 502 instead


@app.post("/email/send")
async def send_email(
    to_email: str,
    subject: str,
    body: str,
    thread_id: str = None
):
    """Send email via Gmail API"""
    if not email_handler:
        raise HTTPException(status_code=503, detail="Email handler not initialized")

    try:
        result = email_handler.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            thread_id=thread_id
        )

        return {
            "status": "success",
            "message_id": result.get('channel_message_id'),
            "delivery_status": result.get('delivery_status')
        }

    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle Gmail push notifications via Google Cloud Pub/Sub.
    """
    try:
        # For now, we'll implement a simpler approach
        # In production, this would verify Pub/Sub signature

        # Get the Pub/Sub message
        data = await request.json()

        # Decode the message (Pub/Sub sends base64 encoded data)
        import base64
        if 'message' in data and 'data' in data['message']:
            message_data = base64.b64decode(data['message']['data']).decode('utf-8')
            print(f"Received Gmail notification: {message_data}")

        # Process in background
        background_tasks.add_task(check_and_process_new_emails)

        return {"status": "received"}

    except Exception as e:
        print(f"Gmail webhook error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


async def check_and_process_new_emails():
    """Check for new emails and process them"""
    try:
        if not email_handler:
            print("Email handler not available")
            return

        # Check for new emails
        new_emails = email_handler.check_inbox(max_results=5)

        if not new_emails:
            print("No new emails found")
            return

        print(f"Found {len(new_emails)} new emails")

        for email_data in new_emails:
            await process_email_message(email_data)

    except Exception as e:
        print(f"Error checking emails: {e}")
        import traceback
        traceback.print_exc()


async def process_email_message(email_data: dict):
    """Process a single email message"""
    try:
        from channels.web_form_handler import get_db_pool, create_or_get_customer
        import uuid

        sender_email = email_data.get('customer_email')
        sender_name = email_data.get('customer_name', sender_email)
        subject = email_data.get('subject', 'No Subject')
        body = email_data.get('content', '')
        thread_id = email_data.get('thread_id')
        message_id = email_data.get('channel_message_id')

        print(f"Processing email from {sender_email}: {subject}")

        # Create or get customer
        customer_id = await create_or_get_customer(sender_email, sender_name)
        print(f"Customer ID: {customer_id}")

        # Create conversation and ticket
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            # Create conversation - convert customer_id to UUID
            conversation_id = await conn.fetchval("""
                INSERT INTO conversations (customer_id, initial_channel, started_at, status)
                VALUES ($1, 'email', NOW(), 'active')
                RETURNING id
            """, uuid.UUID(customer_id) if isinstance(customer_id, str) else customer_id)

            # Create ticket - ensure customer_id is UUID
            ticket_id = uuid.uuid4()
            await conn.execute("""
                INSERT INTO tickets (id, customer_id, conversation_id, subject, status, priority, source_channel, category, created_at)
                VALUES ($1, $2, $3, $4, 'open', 'medium', 'email', 'general', NOW())
            """, ticket_id, uuid.UUID(customer_id) if isinstance(customer_id, str) else customer_id, conversation_id, subject)

            # Store customer's email message
            await conn.execute("""
                INSERT INTO messages (conversation_id, channel, direction, role, content, channel_message_id, created_at)
                VALUES ($1, 'email', 'inbound', 'customer', $2, $3, NOW())
            """, conversation_id, body, message_id)

            print(f"Ticket created: {ticket_id}")

        # Publish to Kafka
        try:
            await kafka_producer.publish(TOPICS['email_inbound'], {
                'channel': 'email',
                'channel_message_id': message_id,
                'customer_email': sender_email,
                'customer_name': sender_name,
                'subject': subject,
                'content': body,
                'thread_id': thread_id,
                'ticket_id': str(ticket_id),
                'received_at': datetime.utcnow().isoformat()
            })
            print(f"[OK] Published email to Kafka")
        except Exception as kafka_error:
            print(f"[WARN] Kafka publish failed: {kafka_error}")

        # Process with AI agent
        agent = get_agent()
        result = await agent.run(
            messages=[{"role": "user", "content": body}],
            context={
                'channel': 'email',
                'customer_email': sender_email,
                'customer_name': sender_name,
                'subject': subject,
                'ticket_id': str(ticket_id)
            }
        )

        print(f"[OK] Agent processed email")
        response_text = result.get('output', '')

        # Store agent response
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO messages (conversation_id, channel, direction, role, content, created_at)
                VALUES ($1, 'email', 'outbound', 'agent', $2, NOW())
            """, conversation_id, response_text)

        # Send email response
        email_result = email_handler.send_email(
            to_email=sender_email,
            subject=f"Re: {subject}",
            body=response_text,
            thread_id=thread_id
        )

        print(f"[OK] Email response sent to {sender_email}: {email_result.get('delivery_status', 'sent')}")

    except Exception as e:
        print(f"Error processing email: {e}")
        import traceback
        traceback.print_exc()


@app.get("/email/check")
async def check_emails_manually():
    """Manually trigger email check (for testing/demo)"""
    try:
        if not email_handler:
            raise HTTPException(status_code=503, detail="Email handler not available")

        # Fetch emails WITHOUT marking as read yet
        new_emails = email_handler.get_unread_messages(max_results=10)

        if not new_emails:
            return {
                "status": "success",
                "message": "No new emails found",
                "unread_count": 0
            }

        print(f"Found {len(new_emails)} unread emails")

        # Process each email synchronously for immediate feedback
        processed = []
        for email_data in new_emails:
            try:
                await process_email_message(email_data)
                processed.append({
                    "from": email_data['customer_email'],
                    "subject": email_data['subject'],
                    "status": "processed"
                })
            except Exception as e:
                print(f"Error processing email: {e}")
                processed.append({
                    "from": email_data.get('customer_email', 'unknown'),
                    "subject": email_data.get('subject', 'unknown'),
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "status": "success",
            "message": f"Processed {len(processed)} emails",
            "unread_count": len(new_emails),
            "emails": processed
        }

    except Exception as e:
        print(f"Error triggering email check: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get full conversation history with cross-channel context"""
    # TODO: Load conversation history
    # history = await load_conversation_history(conversation_id)
    # if not history:
    #     raise HTTPException(status_code=404, detail="Conversation not found")
    # return history

    return {
        "conversation_id": conversation_id,
        "messages": [],
        "status": "active"
    }


@app.get("/admin/metrics")
async def get_admin_metrics():
    """Get real-time dashboard metrics for admin panel"""
    try:
        from channels.web_form_handler import get_db_pool
        import uuid

        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            # Active conversations (last 24 hours)
            active_conversations = await conn.fetchval("""
                SELECT COUNT(*) FROM conversations
                WHERE status = 'active' AND started_at > NOW() - INTERVAL '24 hours'
            """)

            # Total tickets
            total_tickets = await conn.fetchval("""
                SELECT COUNT(*) FROM tickets
            """)

            # Average response time (in seconds)
            avg_response_time = await conn.fetchval("""
                SELECT COALESCE(AVG(latency_ms), 0) / 1000.0
                FROM messages
                WHERE role = 'agent' AND latency_ms IS NOT NULL
            """)

            # Channel breakdown
            channel_breakdown = await conn.fetch("""
                SELECT initial_channel as channel, COUNT(*) as count
                FROM conversations
                GROUP BY initial_channel
            """)

            channels = {
                'email': 0,
                'whatsapp': 0,
                'web_form': 0
            }

            for row in channel_breakdown:
                channels[row['channel']] = row['count']

            return {
                "activeConversations": active_conversations or 0,
                "totalTickets": total_tickets or 0,
                "avgResponseTime": round(float(avg_response_time or 0), 2),
                "channelBreakdown": channels
            }

    except Exception as e:
        print(f"Error fetching admin metrics: {e}")
        import traceback
        traceback.print_exc()
        # Return default values on error
        return {
            "activeConversations": 0,
            "totalTickets": 0,
            "avgResponseTime": 0,
            "channelBreakdown": {"email": 0, "whatsapp": 0, "web_form": 0}
        }


@app.get("/admin/recent-tickets")
async def get_recent_tickets(limit: int = 10):
    """Get recent tickets for admin dashboard"""
    try:
        from channels.web_form_handler import get_db_pool
        import uuid

        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            tickets = await conn.fetch("""
                SELECT
                    t.id,
                    t.subject,
                    t.status,
                    t.priority,
                    t.category,
                    t.created_at,
                    c.initial_channel as channel,
                    cu.name as customer_name,
                    cu.email as customer_email,
                    cu.phone as customer_phone
                FROM tickets t
                JOIN conversations c ON t.conversation_id = c.id
                JOIN customers cu ON t.customer_id = cu.id
                ORDER BY t.created_at DESC
                LIMIT $1
            """, limit)

            return {
                "tickets": [
                    {
                        "id": str(ticket['id']),
                        "subject": ticket['subject'],
                        "status": ticket['status'],
                        "priority": ticket['priority'],
                        "category": ticket['category'],
                        "channel": ticket['channel'],
                        "customer_name": ticket['customer_name'],
                        "customer_email": ticket['customer_email'],
                        "customer_phone": ticket['customer_phone'],
                        "created_at": ticket['created_at'].isoformat()
                    }
                    for ticket in tickets
                ]
            }

    except Exception as e:
        print(f"Error fetching recent tickets: {e}")
        import traceback
        traceback.print_exc()
        return {"tickets": []}


@app.get("/customers/lookup")
async def lookup_customer(email: str = None, phone: str = None):
    """Look up customer by email or phone across all channels"""
    if not email and not phone:
        raise HTTPException(status_code=400, detail="Provide email or phone")

    # TODO: Find customer
    # customer = await find_customer(email=email, phone=phone)
    # if not customer:
    #     raise HTTPException(status_code=404, detail="Customer not found")
    # return customer

    return {
        "customer_id": "sample-id",
        "email": email,
        "phone": phone
    }


@app.get("/metrics/channels")
async def get_channel_metrics():
    """Get performance metrics by channel"""
    # TODO: Get actual metrics from database
    return {
        "email": {
            "total_conversations": 0,
            "avg_sentiment": 0.0,
            "escalations": 0
        },
        "whatsapp": {
            "total_conversations": 0,
            "avg_sentiment": 0.0,
            "escalations": 0
        },
        "web_form": {
            "total_conversations": 0,
            "avg_sentiment": 0.0,
            "escalations": 0
        }
    }


@app.post("/customer/login")
async def customer_login(request: dict):
    """Customer portal login"""
    try:
        from channels.web_form_handler import get_db_pool

        identifier_type = request.get('identifier_type')
        identifier_value = request.get('identifier_value')

        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            if identifier_type == 'email':
                customer = await conn.fetchrow("""
                    SELECT id, name, email, phone, created_at
                    FROM customers
                    WHERE email = $1
                """, identifier_value)
            else:
                customer = await conn.fetchrow("""
                    SELECT id, name, email, phone, created_at
                    FROM customers
                    WHERE phone = $1
                """, identifier_value)

            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")

            return {
                "customer_id": str(customer['id']),
                "name": customer['name'],
                "email": customer['email'],
                "phone": customer['phone'],
                "created_at": customer['created_at'].isoformat()
            }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@app.get("/customer/tickets")
async def get_customer_tickets(identifier: str):
    """Get all tickets for a customer"""
    try:
        from channels.web_form_handler import get_db_pool

        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            tickets = await conn.fetch("""
                SELECT
                    t.id as ticket_id,
                    t.subject,
                    t.status,
                    t.priority,
                    t.category,
                    t.created_at,
                    c.initial_channel as channel,
                    COUNT(m.id) as message_count
                FROM tickets t
                JOIN conversations c ON t.conversation_id = c.id
                JOIN customers cu ON t.customer_id = cu.id
                LEFT JOIN messages m ON m.conversation_id = c.id
                WHERE cu.email = $1 OR cu.phone = $1
                GROUP BY t.id, t.subject, t.status, t.priority, t.category, t.created_at, c.initial_channel
                ORDER BY t.created_at DESC
            """, identifier)

            return {
                "tickets": [
                    {
                        "ticket_id": str(ticket['ticket_id']),
                        "subject": ticket['subject'],
                        "status": ticket['status'],
                        "priority": ticket['priority'],
                        "category": ticket['category'],
                        "channel": ticket['channel'],
                        "created_at": ticket['created_at'].isoformat(),
                        "messages": [{"count": ticket['message_count']}]
                    }
                    for ticket in tickets
                ]
            }

    except Exception as e:
        print(f"Error fetching customer tickets: {e}")
        return {"tickets": []}


@app.post("/chat/send")
async def send_chat_message(request: dict):
    """Send a message in live chat"""
    try:
        ticket_id = request.get('ticket_id')
        message = request.get('message')

        # Process with agent
        agent = get_agent()
        result = await agent.run(
            messages=[{"role": "user", "content": message}],
            context={
                'channel': 'web_form',
                'ticket_id': ticket_id
            }
        )

        return {
            "status": "success",
            "response": result.get('output', '')
        }

    except Exception as e:
        print(f"Chat send error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@app.post("/ticket/{ticket_id}/rate")
async def rate_ticket(ticket_id: str, request: dict):
    """Rate a ticket response"""
    try:
        from channels.web_form_handler import get_db_pool
        import uuid

        rating = request.get('rating')

        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE tickets
                SET rating = $1, updated_at = NOW()
                WHERE id = $2
            """, rating, uuid.UUID(ticket_id))

        return {"status": "success", "rating": rating}

    except Exception as e:
        print(f"Rating error: {e}")
        raise HTTPException(status_code=500, detail="Failed to rate ticket")


@app.post("/ticket/{ticket_id}/escalate")
async def escalate_ticket(ticket_id: str):
    """Escalate ticket to human agent"""
    try:
        from channels.web_form_handler import get_db_pool
        import uuid

        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE tickets
                SET status = 'escalated', updated_at = NOW()
                WHERE id = $1
            """, uuid.UUID(ticket_id))

        # Publish escalation event
        await kafka_producer.publish(TOPICS['escalations'], {
            'ticket_id': ticket_id,
            'escalated_at': datetime.utcnow().isoformat(),
            'reason': 'customer_request'
        })

        return {"status": "success", "message": "Ticket escalated to human agent"}

    except Exception as e:
        print(f"Escalation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to escalate ticket")


@app.post("/test/email/send-direct")
async def test_email_send_direct(to_email: str, test_message: str = "Test email from backend"):
    """Test email sending directly - for debugging"""
    try:
        if not email_handler:
            return {"status": "error", "message": "Email handler not initialized"}

        result = email_handler.send_email(
            to_email=to_email,
            subject="Test Email - Backend Check",
            body=f"{test_message}\n\nThis is a test email to verify Gmail API sending works.\n\nTimestamp: {datetime.utcnow().isoformat()}"
        )

        return {
            "status": "success" if result.get('delivery_status') == 'sent' else "failed",
            "result": result,
            "message": "Email sent successfully" if result.get('delivery_status') == 'sent' else "Email sending failed"
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/analytics")
async def get_analytics(range: str = '7d'):
    """Get analytics data for dashboard"""
    # Return mock data for demo
    return {
        "responseTimeData": [
            {"time": "00:00", "avgTime": 2.3},
            {"time": "04:00", "avgTime": 1.8},
            {"time": "08:00", "avgTime": 3.2},
            {"time": "12:00", "avgTime": 2.9},
            {"time": "16:00", "avgTime": 3.5},
            {"time": "20:00", "avgTime": 2.1}
        ],
        "satisfactionTrend": [
            {"date": "Mon", "score": 4.5},
            {"date": "Tue", "score": 4.7},
            {"date": "Wed", "score": 4.6},
            {"date": "Thu", "score": 4.8},
            {"date": "Fri", "score": 4.9},
            {"date": "Sat", "score": 4.7},
            {"date": "Sun", "score": 4.8}
        ],
        "commonIssues": [
            {"category": "Password Reset", "count": 145},
            {"category": "API Authentication", "count": 98},
            {"category": "Data Export", "count": 76},
            {"category": "Technical Issues", "count": 54},
            {"category": "Billing", "count": 32}
        ],
        "peakHours": [
            {"hour": "9 AM", "volume": 45},
            {"hour": "10 AM", "volume": 67},
            {"hour": "11 AM", "volume": 89},
            {"hour": "12 PM", "volume": 72},
            {"hour": "1 PM", "volume": 58},
            {"hour": "2 PM", "volume": 81},
            {"hour": "3 PM", "volume": 95},
            {"hour": "4 PM", "volume": 73},
            {"hour": "5 PM", "volume": 52}
        ],
        "channelPerformance": [
            {"channel": "Email", "tickets": 234, "avgTime": 2.8, "satisfaction": 4.7},
            {"channel": "WhatsApp", "tickets": 189, "avgTime": 1.9, "satisfaction": 4.9},
            {"channel": "Web Form", "tickets": 156, "avgTime": 2.3, "satisfaction": 4.8}
        ],
        "escalationRatio": {"ai": 97, "human": 3}
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
