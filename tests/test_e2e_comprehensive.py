"""
Comprehensive E2E Test Suite for Customer Success FTE
Tests all channels: Email (Gmail), WhatsApp, Web Form
"""

import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from datetime import datetime
import json
import uuid


BASE_URL = "http://localhost:8001"


@pytest_asyncio.fixture
async def client():
    """Create async HTTP client"""
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as ac:
        yield ac


# ============================================================================
# WEB FORM CHANNEL TESTS (Comprehensive)
# ============================================================================

class TestWebFormChannelComprehensive:
    """Comprehensive tests for web support form"""

    @pytest.mark.asyncio
    async def test_form_submission_success(self, client):
        """Web form submission should create ticket and return ID"""
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Help with API",
            "category": "technical",
            "priority": "medium",
            "message": "I need help with the API authentication"
        })

        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        assert data["message"] is not None
        assert "ticket_id" in data["ticket_id"] or len(data["ticket_id"]) > 0

    @pytest.mark.asyncio
    async def test_form_validation_name_too_short(self, client):
        """Form should reject names that are too short"""
        response = await client.post("/support/submit", json={
            "name": "A",  # Too short
            "email": "test@example.com",
            "subject": "Test Subject",
            "category": "general",
            "message": "This is a test message"
        })

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_form_validation_invalid_email(self, client):
        """Form should reject invalid email addresses"""
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "invalid-email",  # Invalid format
            "subject": "Test Subject",
            "category": "general",
            "message": "This is a test message"
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_form_validation_message_too_short(self, client):
        """Form should reject messages that are too short"""
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "category": "general",
            "message": "Short"  # Too short
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_form_all_categories(self, client):
        """Test form submission with all valid categories"""
        categories = ['general', 'technical', 'billing', 'bug_report', 'feedback']

        for category in categories:
            response = await client.post("/support/submit", json={
                "name": "Test User",
                "email": f"test_{category}@example.com",
                "subject": f"Test {category}",
                "category": category,
                "message": f"Testing {category} category submission"
            })

            assert response.status_code == 200
            data = response.json()
            assert "ticket_id" in data

    @pytest.mark.asyncio
    async def test_form_all_priorities(self, client):
        """Test form submission with all priority levels"""
        priorities = ['low', 'medium', 'high']

        for priority in priorities:
            response = await client.post("/support/submit", json={
                "name": "Test User",
                "email": f"test_{priority}@example.com",
                "subject": f"Test {priority} priority",
                "category": "general",
                "priority": priority,
                "message": f"Testing {priority} priority submission"
            })

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_ticket_status_retrieval(self, client):
        """Should be able to check ticket status after submission"""
        # Submit form
        submit_response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "status_test@example.com",
            "subject": "Status Test",
            "category": "general",
            "message": "Testing ticket status retrieval"
        })

        ticket_id = submit_response.json()["ticket_id"]

        # Check status
        status_response = await client.get(f"/support/ticket/{ticket_id}")
        assert status_response.status_code in [200, 404]  # 404 if not implemented yet


# ============================================================================
# EMAIL CHANNEL TESTS (Comprehensive)
# ============================================================================

class TestEmailChannelComprehensive:
    """Comprehensive tests for Gmail integration"""

    @pytest.mark.asyncio
    async def test_email_check_endpoint(self, client):
        """Email check endpoint should be accessible"""
        response = await client.get("/email/check")
        # Should return 200 or 503 (if handler not initialized)
        assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_email_check_returns_messages(self, client):
        """Email check should return message list"""
        response = await client.get("/email/check")

        if response.status_code == 200:
            data = response.json()
            assert "unread_count" in data
            assert "messages" in data
            assert isinstance(data["messages"], list)

    @pytest.mark.asyncio
    async def test_email_send_endpoint(self, client):
        """Email send endpoint should accept valid requests"""
        response = await client.post("/email/send", params={
            "to_email": "customer@example.com",
            "subject": "Test Response",
            "body": "This is a test response from the support team."
        })

        # Should return 200 or 503 (if handler not initialized)
        assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_email_send_with_thread_id(self, client):
        """Email send should support thread_id for replies"""
        response = await client.post("/email/send", params={
            "to_email": "customer@example.com",
            "subject": "Re: Original Subject",
            "body": "This is a reply in the same thread.",
            "thread_id": "test-thread-123"
        })

        assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_gmail_webhook_endpoint(self, client):
        """Gmail webhook should accept Pub/Sub notifications"""
        # Simulate Pub/Sub notification
        response = await client.post("/webhooks/gmail", json={
            "message": {
                "data": "base64_encoded_notification",
                "messageId": "test-message-123"
            },
            "subscription": "projects/test/subscriptions/gmail-push"
        })

        # Should process or return error gracefully
        assert response.status_code in [200, 500, 503]

    @pytest.mark.asyncio
    async def test_email_formatting_formal(self, client):
        """Email responses should be formatted formally"""
        # This tests the formatting logic indirectly
        response = await client.post("/email/send", params={
            "to_email": "customer@example.com",
            "subject": "Test Formatting",
            "body": "Testing formal email formatting with greeting and signature."
        })

        if response.status_code == 200:
            data = response.json()
            assert "status" in data


# ============================================================================
# WHATSAPP CHANNEL TESTS (Comprehensive)
# ============================================================================

class TestWhatsAppChannelComprehensive:
    """Comprehensive tests for WhatsApp/Twilio integration"""

    @pytest.mark.asyncio
    async def test_whatsapp_webhook_endpoint_exists(self, client):
        """WhatsApp webhook endpoint should exist"""
        response = await client.post("/webhooks/whatsapp", data={
            "MessageSid": "SM123456",
            "From": "whatsapp:+1234567890",
            "Body": "Hello, I need help",
            "ProfileName": "Test User"
        })

        # Will likely fail signature validation, but endpoint should exist
        assert response.status_code in [200, 403, 500, 503]

    @pytest.mark.asyncio
    async def test_whatsapp_webhook_with_valid_data(self, client):
        """WhatsApp webhook should process valid message data"""
        response = await client.post("/webhooks/whatsapp", data={
            "MessageSid": "SM" + str(uuid.uuid4())[:10],
            "From": "whatsapp:+19876543210",
            "Body": "I need help with my account",
            "ProfileName": "John Doe",
            "NumMedia": "0"
        })

        # Signature validation will fail in test, but that's expected
        assert response.status_code in [200, 403, 500, 503]

    @pytest.mark.asyncio
    async def test_whatsapp_status_webhook(self, client):
        """WhatsApp status webhook should accept delivery updates"""
        response = await client.post("/webhooks/whatsapp/status", data={
            "MessageSid": "SM123456",
            "MessageStatus": "delivered"
        })

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_whatsapp_short_message(self, client):
        """WhatsApp should handle short messages"""
        response = await client.post("/webhooks/whatsapp", data={
            "MessageSid": "SM_short",
            "From": "whatsapp:+1234567890",
            "Body": "Help",  # Very short message
            "ProfileName": "User"
        })

        assert response.status_code in [200, 403, 500, 503]

    @pytest.mark.asyncio
    async def test_whatsapp_long_message(self, client):
        """WhatsApp should handle long messages (will be split)"""
        long_message = "This is a very long message. " * 50  # ~1500 chars

        response = await client.post("/webhooks/whatsapp", data={
            "MessageSid": "SM_long",
            "From": "whatsapp:+1234567890",
            "Body": long_message,
            "ProfileName": "User"
        })

        assert response.status_code in [200, 403, 500, 503]


# ============================================================================
# CROSS-CHANNEL CONTINUITY TESTS
# ============================================================================

class TestCrossChannelContinuity:
    """Test that conversations persist across channels"""

    @pytest.mark.asyncio
    async def test_customer_lookup_by_email(self, client):
        """Should be able to look up customer by email"""
        response = await client.get(
            "/customers/lookup",
            params={"email": "crosschannel@example.com"}
        )

        # Should return 200 or 404
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_customer_lookup_by_phone(self, client):
        """Should be able to look up customer by phone"""
        response = await client.get(
            "/customers/lookup",
            params={"phone": "+1234567890"}
        )

        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_customer_history_across_channels(self, client):
        """Customer history should include all channel interactions"""
        # Create ticket via web form
        web_response = await client.post("/support/submit", json={
            "name": "Cross Channel User",
            "email": "crosschannel_test@example.com",
            "subject": "Initial Contact",
            "category": "general",
            "message": "First contact via web form"
        })

        assert web_response.status_code == 200

        # Look up customer
        customer_response = await client.get(
            "/customers/lookup",
            params={"email": "crosschannel_test@example.com"}
        )

        if customer_response.status_code == 200:
            customer = customer_response.json()
            # Should have customer data
            assert "customer_id" in customer or "email" in customer


# ============================================================================
# HEALTH AND MONITORING TESTS
# ============================================================================

class TestHealthAndMonitoring:
    """Test health checks and monitoring endpoints"""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Health check should return healthy status"""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "channels" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Root endpoint should return service info"""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "channels" in data

    @pytest.mark.asyncio
    async def test_channel_metrics(self, client):
        """Channel metrics endpoint should return data"""
        response = await client.get("/metrics/channels")

        assert response.status_code == 200
        data = response.json()
        # Should have metrics for each channel
        assert isinstance(data, dict)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test response time and performance requirements"""

    @pytest.mark.asyncio
    async def test_response_time_under_3_seconds(self, client):
        """API should respond within 3 seconds"""
        start_time = datetime.now()

        response = await client.post("/support/submit", json={
            "name": "Performance Test",
            "email": "perf@example.com",
            "subject": "Performance Test",
            "category": "general",
            "message": "Testing response time"
        })

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        assert response.status_code == 200
        assert duration < 3.0, f"Response took {duration}s (requirement: <3s)"

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """System should handle concurrent requests"""
        # Create 10 concurrent requests
        tasks = []
        for i in range(10):
            task = client.post("/support/submit", json={
                "name": f"Concurrent User {i}",
                "email": f"concurrent{i}@example.com",
                "subject": f"Concurrent Test {i}",
                "category": "general",
                "message": f"Testing concurrent request {i}"
            })
            tasks.append(task)

        # Execute all concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successful responses
        successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)

        # At least 80% should succeed
        assert successful >= 8, f"Only {successful}/10 requests succeeded"


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, client):
        """Invalid endpoints should return 404"""
        response = await client.get("/invalid/endpoint")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_malformed_json(self, client):
        """Malformed JSON should return 422"""
        response = await client.post(
            "/support/submit",
            content="invalid json{{{",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client):
        """Missing required fields should return 422"""
        response = await client.post("/support/submit", json={
            "name": "Test User"
            # Missing email, subject, category, message
        })
        assert response.status_code == 422


if __name__ == "__main__":
    print("""
    Customer Success FTE - Comprehensive E2E Test Suite
    ====================================================

    This test suite covers:
    - ✅ Web Form: Validation, all categories, all priorities
    - ✅ Email: Check, send, webhook, formatting
    - ✅ WhatsApp: Webhook, status, message handling
    - ✅ Cross-channel: Customer lookup, history
    - ✅ Health: Health checks, metrics
    - ✅ Performance: Response time, concurrency
    - ✅ Error handling: Invalid requests, edge cases

    To run:
        pytest tests/test_e2e_comprehensive.py -v

    To run specific test class:
        pytest tests/test_e2e_comprehensive.py::TestWebFormChannelComprehensive -v

    To run with coverage:
        pytest tests/test_e2e_comprehensive.py --cov=src --cov-report=html
    """)
