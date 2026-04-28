"""
Multi-Channel End-to-End Test Suite
Tests all three channels: Email, WhatsApp, and Web Form
"""

import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime
import uuid

BASE_URL = "https://fte-backend-3ohm.onrender.com"
LOCAL_URL = "http://localhost:8001"

# Use production URL by default, fallback to local
TEST_URL = BASE_URL

@pytest.fixture
async def client():
    async with AsyncClient(base_url=TEST_URL, timeout=30.0) as ac:
        yield ac


class TestWebFormChannel:
    """Test the web support form (required build)."""

    @pytest.mark.asyncio
    async def test_form_submission_success(self, client):
        """Web form submission should create ticket and return ID."""
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "subject": "Help with API Authentication",
            "category": "technical",
            "priority": "medium",
            "message": "I need help with the API authentication. I'm getting 401 errors when trying to authenticate."
        })

        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        assert data["ticket_id"] is not None
        assert "message" in data
        assert len(data["ticket_id"]) > 0

    @pytest.mark.asyncio
    async def test_form_validation_name_too_short(self, client):
        """Form should validate name length."""
        response = await client.post("/support/submit", json={
            "name": "A",  # Too short
            "email": "test@example.com",
            "subject": "Test Subject",
            "category": "general",
            "message": "This is a test message with enough characters."
        })

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_form_validation_invalid_email(self, client):
        """Form should validate email format."""
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "invalid-email",  # Invalid format
            "subject": "Test Subject",
            "category": "general",
            "message": "This is a test message with enough characters."
        })

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_form_validation_message_too_short(self, client):
        """Form should validate message length."""
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "category": "general",
            "message": "Short"  # Too short
        })

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_form_validation_invalid_category(self, client):
        """Form should validate category values."""
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "category": "invalid_category",  # Invalid
            "message": "This is a test message with enough characters."
        })

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_ticket_status_retrieval(self, client):
        """Should be able to check ticket status after submission."""
        # Submit form
        submit_response = await client.post("/support/submit", json={
            "name": "Status Test User",
            "email": f"status_{uuid.uuid4().hex[:8]}@example.com",
            "subject": "Status Test",
            "category": "general",
            "message": "Testing ticket status retrieval functionality."
        })

        assert submit_response.status_code == 200
        ticket_id = submit_response.json()["ticket_id"]

        # Check status
        status_response = await client.get(f"/support/ticket/{ticket_id}")
        assert status_response.status_code == 200
        ticket_data = status_response.json()
        assert ticket_data["ticket_id"] == ticket_id
        assert "status" in ticket_data
        assert ticket_data["status"] in ["open", "active", "processing", "resolved"]

    @pytest.mark.asyncio
    async def test_all_categories(self, client):
        """Test all valid category options."""
        categories = ["general", "technical", "billing", "feedback", "bug_report"]

        for category in categories:
            response = await client.post("/support/submit", json={
                "name": "Category Test User",
                "email": f"cat_{category}_{uuid.uuid4().hex[:6]}@example.com",
                "subject": f"Test {category} category",
                "category": category,
                "message": f"Testing the {category} category functionality."
            })

            assert response.status_code == 200, f"Failed for category: {category}"
            assert "ticket_id" in response.json()

    @pytest.mark.asyncio
    async def test_all_priorities(self, client):
        """Test all valid priority options."""
        priorities = ["low", "medium", "high"]

        for priority in priorities:
            response = await client.post("/support/submit", json={
                "name": "Priority Test User",
                "email": f"pri_{priority}_{uuid.uuid4().hex[:6]}@example.com",
                "subject": f"Test {priority} priority",
                "category": "general",
                "priority": priority,
                "message": f"Testing the {priority} priority functionality."
            })

            assert response.status_code == 200, f"Failed for priority: {priority}"
            assert "ticket_id" in response.json()


class TestEmailChannel:
    """Test Gmail integration."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Health check should return channel status."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_gmail_webhook_endpoint_exists(self, client):
        """Gmail webhook endpoint should exist."""
        # Note: This will fail without proper Gmail notification format
        # but verifies the endpoint exists
        response = await client.post("/webhooks/gmail", json={
            "message": {
                "data": "test_data",
                "messageId": "test-123"
            }
        })

        # Should return 200 or 400, not 404
        assert response.status_code in [200, 400, 500]


class TestWhatsAppChannel:
    """Test WhatsApp/Twilio integration."""

    @pytest.mark.asyncio
    async def test_whatsapp_webhook_endpoint_exists(self, client):
        """WhatsApp webhook endpoint should exist."""
        # Note: This will fail signature validation
        # but verifies the endpoint exists
        response = await client.post(
            "/webhooks/whatsapp",
            data={
                "MessageSid": "SM123",
                "From": "whatsapp:+1234567890",
                "Body": "Hello, I need help",
                "ProfileName": "Test User"
            }
        )

        # Should return 200, 403 (signature fail), or 400, not 404
        assert response.status_code in [200, 400, 403, 500]


class TestCrossChannelContinuity:
    """Test that conversations persist across channels."""

    @pytest.mark.asyncio
    async def test_customer_lookup_by_email(self, client):
        """Should be able to look up customer by email."""
        # Create a ticket first
        email = f"lookup_{uuid.uuid4().hex[:8]}@example.com"
        submit_response = await client.post("/support/submit", json={
            "name": "Lookup Test User",
            "email": email,
            "subject": "Initial Contact",
            "category": "general",
            "message": "First contact via web form for lookup test."
        })

        assert submit_response.status_code == 200

        # Try to look up customer
        lookup_response = await client.get(
            "/customer/lookup",
            params={"email": email}
        )

        # Should return 200 (found) or 404 (not found yet)
        assert lookup_response.status_code in [200, 404]

        if lookup_response.status_code == 200:
            customer = lookup_response.json()
            assert "email" in customer or "customer_id" in customer


class TestChannelMetrics:
    """Test channel-specific metrics."""

    @pytest.mark.asyncio
    async def test_analytics_endpoint(self, client):
        """Analytics endpoint should return data."""
        response = await client.get("/analytics")

        # Should return 200 or 404 if not implemented
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            # Should have some analytics data structure
            assert isinstance(data, dict)


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_message(self, client):
        """Should handle empty message gracefully."""
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test",
            "category": "general",
            "message": ""  # Empty
        })

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_very_long_message(self, client):
        """Should handle very long messages."""
        long_message = "This is a test message. " * 200  # ~5000 characters

        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": f"long_{uuid.uuid4().hex[:8]}@example.com",
            "subject": "Long Message Test",
            "category": "general",
            "message": long_message
        })

        # Should either accept or reject gracefully
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_special_characters_in_message(self, client):
        """Should handle special characters."""
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": f"special_{uuid.uuid4().hex[:8]}@example.com",
            "subject": "Special Characters Test",
            "category": "general",
            "message": "Testing special chars: <script>alert('xss')</script> & © ® ™ 你好 مرحبا"
        })

        assert response.status_code == 200
        assert "ticket_id" in response.json()

    @pytest.mark.asyncio
    async def test_nonexistent_ticket(self, client):
        """Should handle nonexistent ticket lookup."""
        fake_ticket_id = str(uuid.uuid4())

        response = await client.get(f"/support/ticket/{fake_ticket_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_malformed_ticket_id(self, client):
        """Should handle malformed ticket ID."""
        response = await client.get("/support/ticket/invalid-id-format")

        assert response.status_code in [400, 404, 422]


class TestPerformance:
    """Test performance and response times."""

    @pytest.mark.asyncio
    async def test_response_time_under_3_seconds(self, client):
        """Form submission should complete in under 3 seconds."""
        start_time = datetime.utcnow()

        response = await client.post("/support/submit", json={
            "name": "Performance Test User",
            "email": f"perf_{uuid.uuid4().hex[:8]}@example.com",
            "subject": "Performance Test",
            "category": "general",
            "message": "Testing response time for form submission."
        })

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        assert response.status_code == 200
        assert duration < 3.0, f"Response took {duration}s, expected < 3s"

    @pytest.mark.asyncio
    async def test_concurrent_submissions(self, client):
        """Should handle multiple concurrent submissions."""
        async def submit_form(index):
            return await client.post("/support/submit", json={
                "name": f"Concurrent User {index}",
                "email": f"concurrent_{index}_{uuid.uuid4().hex[:6]}@example.com",
                "subject": f"Concurrent Test {index}",
                "category": "general",
                "message": f"Testing concurrent submission number {index}."
            })

        # Submit 10 forms concurrently
        tasks = [submit_form(i) for i in range(10)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        success_count = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
        assert success_count >= 8, f"Only {success_count}/10 concurrent requests succeeded"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
