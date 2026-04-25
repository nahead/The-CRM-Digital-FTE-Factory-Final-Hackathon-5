"""
End-to-End Test Suite for Customer Success FTE
Tests complete workflows across all channels
"""

import pytest
import asyncio
import httpx
import json
from datetime import datetime
import asyncpg

# Test Configuration
API_BASE_URL = "http://localhost:8001"
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "fte_db",
    "user": "postgres",
    "password": "postgres123"
}

class TestE2EWebForm:
    """Test complete web form submission workflow"""

    @pytest.mark.asyncio
    async def test_web_form_submission_creates_ticket(self):
        """Test: Web form submission -> API -> Database -> Ticket created"""

        # Step 1: Submit form via API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/support/submit",
                json={
                    "name": "E2E Test User",
                    "email": "e2e_test@example.com",
                    "subject": "E2E Test Submission",
                    "category": "technical",
                    "priority": "medium",
                    "message": "This is an end-to-end test message"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        ticket_id = data["ticket_id"]

        # Step 2: Verify ticket in database
        conn = await asyncpg.connect(**DB_CONFIG)
        try:
            ticket = await conn.fetchrow(
                "SELECT * FROM tickets WHERE id = $1",
                ticket_id
            )
            assert ticket is not None
            assert ticket["subject"] == "E2E Test Submission"
            assert ticket["status"] == "open"
            assert ticket["source_channel"] == "web_form"

            # Step 3: Verify customer created
            customer = await conn.fetchrow(
                "SELECT * FROM customers WHERE id = $1",
                ticket["customer_id"]
            )
            assert customer is not None
            assert customer["email"] == "e2e_test@example.com"

        finally:
            await conn.close()

    @pytest.mark.asyncio
    async def test_web_form_validation_errors(self):
        """Test: Invalid form data returns proper error"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/support/submit",
                json={
                    "name": "Test",
                    "email": "invalid-email",  # Invalid email
                    "subject": "Test",
                    "category": "Technical Support",
                    "priority": "Medium",
                    "message": "Test"
                }
            )

        assert response.status_code == 422  # Validation error


class TestE2ECrossChannel:
    """Test cross-channel customer identification"""

    @pytest.mark.asyncio
    async def test_customer_identification_across_channels(self):
        """Test: Same customer identified across email and web form"""

        test_email = f"crosschannel_{datetime.now().timestamp()}@example.com"

        # Step 1: Submit via web form
        async with httpx.AsyncClient() as client:
            response1 = await client.post(
                f"{API_BASE_URL}/support/submit",
                json={
                    "name": "Cross Channel User",
                    "email": test_email,
                    "subject": "First Contact",
                    "category": "general",
                    "priority": "low",
                    "message": "Initial message via web form"
                }
            )

        assert response1.status_code == 200
        ticket1_id = response1.json()["ticket_id"]

        # Step 2: Get customer ID from first ticket
        conn = await asyncpg.connect(**DB_CONFIG)
        try:
            ticket1 = await conn.fetchrow(
                "SELECT customer_id FROM tickets WHERE id = $1",
                ticket1_id
            )
            customer_id_1 = ticket1["customer_id"]

            # Step 3: Submit again via web form (simulating email channel)
            async with httpx.AsyncClient() as client:
                response2 = await client.post(
                    f"{API_BASE_URL}/support/submit",
                    json={
                        "name": "Cross Channel User",
                        "email": test_email,
                        "subject": "Second Contact",
                        "category": "technical",
                        "priority": "medium",
                        "message": "Follow-up message"
                    }
                )

            assert response2.status_code == 200
            ticket2_id = response2.json()["ticket_id"]

            # Step 4: Verify same customer ID
            ticket2 = await conn.fetchrow(
                "SELECT customer_id FROM tickets WHERE id = $1",
                ticket2_id
            )
            customer_id_2 = ticket2["customer_id"]

            assert customer_id_1 == customer_id_2, "Customer should be identified as same person"

            # Step 5: Verify both tickets linked to same customer
            tickets = await conn.fetch(
                "SELECT id FROM tickets WHERE customer_id = $1 ORDER BY created_at",
                customer_id_1
            )
            assert len(tickets) >= 2

        finally:
            await conn.close()


class TestE2ETicketLifecycle:
    """Test complete ticket lifecycle"""

    @pytest.mark.asyncio
    async def test_ticket_lifecycle_open_to_resolved(self):
        """Test: Ticket creation -> status updates -> resolution"""

        # Step 1: Create ticket
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/support/submit",
                json={
                    "name": "Lifecycle Test",
                    "email": "lifecycle@example.com",
                    "subject": "Lifecycle Test",
                    "category": "technical",
                    "priority": "medium",
                    "message": "Testing ticket lifecycle"
                }
            )

        ticket_id = response.json()["ticket_id"]

        conn = await asyncpg.connect(**DB_CONFIG)
        try:
            # Step 2: Verify initial status is 'open'
            ticket = await conn.fetchrow(
                "SELECT status FROM tickets WHERE id = $1",
                ticket_id
            )
            assert ticket["status"] == "open"

            # Step 3: Update to 'pending'
            await conn.execute(
                "UPDATE tickets SET status = 'pending' WHERE id = $1",
                ticket_id
            )

            ticket = await conn.fetchrow(
                "SELECT status FROM tickets WHERE id = $1",
                ticket_id
            )
            assert ticket["status"] == "pending"

            # Step 4: Update to 'resolved'
            await conn.execute(
                "UPDATE tickets SET status = 'resolved', resolved_at = NOW() WHERE id = $1",
                ticket_id
            )

            ticket = await conn.fetchrow(
                "SELECT status, resolved_at FROM tickets WHERE id = $1",
                ticket_id
            )
            assert ticket["status"] == "resolved"
            assert ticket["resolved_at"] is not None

        finally:
            await conn.close()


class TestE2EPerformance:
    """Test performance requirements"""

    @pytest.mark.asyncio
    async def test_response_time_under_3_seconds(self):
        """Test: API response time < 3 seconds"""

        start_time = datetime.now()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/support/submit",
                json={
                    "name": "Performance Test",
                    "email": "perf@example.com",
                    "subject": "Performance Test",
                    "category": "general",
                    "priority": "low",
                    "message": "Testing response time"
                }
            )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        assert response.status_code == 200
        assert duration < 3.0, f"Response took {duration}s, should be < 3s"

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test: Handle 10 concurrent requests"""

        async def submit_form(index):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE_URL}/support/submit",
                    json={
                        "name": f"Concurrent User {index}",
                        "email": f"concurrent{index}@example.com",
                        "subject": f"Concurrent Test {index}",
                        "category": "general",
                        "priority": "low",
                        "message": f"Concurrent test message {index}"
                    }
                )
                return response.status_code

        # Submit 10 requests concurrently
        tasks = [submit_form(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(status == 200 for status in results)


class TestE2EHealthCheck:
    """Test system health endpoints"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test: Health check returns 200"""

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "channels" in data


class TestE2EDataIntegrity:
    """Test data integrity and constraints"""

    @pytest.mark.asyncio
    async def test_duplicate_email_same_customer(self):
        """Test: Same email creates same customer"""

        test_email = f"duplicate_{datetime.now().timestamp()}@example.com"

        # Create two tickets with same email
        async with httpx.AsyncClient() as client:
            response1 = await client.post(
                f"{API_BASE_URL}/support/submit",
                json={
                    "name": "Duplicate Test 1",
                    "email": test_email,
                    "subject": "First",
                    "category": "general",
                    "priority": "low",
                    "message": "First message"
                }
            )

            response2 = await client.post(
                f"{API_BASE_URL}/support/submit",
                json={
                    "name": "Duplicate Test 2",
                    "email": test_email,
                    "subject": "Second",
                    "category": "technical",
                    "priority": "medium",
                    "message": "Second message"
                }
            )

        ticket1_id = response1.json()["ticket_id"]
        ticket2_id = response2.json()["ticket_id"]

        conn = await asyncpg.connect(**DB_CONFIG)
        try:
            # Get customer IDs
            ticket1 = await conn.fetchrow(
                "SELECT customer_id FROM tickets WHERE id = $1",
                ticket1_id
            )
            ticket2 = await conn.fetchrow(
                "SELECT customer_id FROM tickets WHERE id = $1",
                ticket2_id
            )

            assert ticket1["customer_id"] == ticket2["customer_id"]

            # Verify only one customer record
            customers = await conn.fetch(
                "SELECT id FROM customers WHERE email = $1",
                test_email
            )
            assert len(customers) == 1

        finally:
            await conn.close()


# Test runner configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
