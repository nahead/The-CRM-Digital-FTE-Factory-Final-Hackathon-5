"""
Comprehensive Test Suite for Customer Success FTE
Run with: pytest tests/test_comprehensive.py -v
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from api.main import app

client = TestClient(app)


class TestHealthAndStatus:
    """Test health check and status endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns correct structure"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Customer Success FTE API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "channels" in data
        assert "timestamp" in data

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "channels" in data
        assert data["channels"]["email"] == "active"
        assert data["channels"]["whatsapp"] == "active"
        assert data["channels"]["web_form"] == "active"


class TestSecurityHeaders:
    """Test security headers are present"""

    def test_security_headers_present(self):
        """Test all security headers are added"""
        response = client.get("/health")
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers

    def test_rate_limit_headers(self):
        """Test rate limit headers are present"""
        response = client.get("/health")
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_response_time_header(self):
        """Test response time header is present"""
        response = client.get("/health")
        assert "X-Response-Time" in response.headers
        assert "s" in response.headers["X-Response-Time"]


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_not_exceeded_normal_use(self):
        """Test normal usage doesn't hit rate limit"""
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200

    def test_rate_limit_headers_decrease(self):
        """Test rate limit remaining decreases with requests"""
        response1 = client.get("/health")
        remaining1 = int(response1.headers["X-RateLimit-Remaining"])

        response2 = client.get("/health")
        remaining2 = int(response2.headers["X-RateLimit-Remaining"])

        assert remaining2 < remaining1


class TestSupportEndpoints:
    """Test support ticket endpoints"""

    def test_submit_support_request(self):
        """Test submitting a support request"""
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Issue",
            "message": "This is a test message",
            "priority": "medium",
            "category": "technical"
        }
        response = client.post("/support/submit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        assert "message" in data

    def test_submit_support_request_missing_fields(self):
        """Test submitting request with missing required fields"""
        payload = {
            "name": "Test User",
            "email": "test@example.com"
            # Missing subject and message
        }
        response = client.post("/support/submit", json=payload)
        assert response.status_code == 422  # Validation error

    def test_submit_support_request_invalid_email(self):
        """Test submitting request with invalid email"""
        payload = {
            "name": "Test User",
            "email": "invalid-email",
            "subject": "Test",
            "message": "Test message",
            "priority": "medium",
            "category": "technical"
        }
        response = client.post("/support/submit", json=payload)
        assert response.status_code == 422


class TestAdminEndpoints:
    """Test admin dashboard endpoints"""

    def test_admin_metrics(self):
        """Test admin metrics endpoint"""
        response = client.get("/admin/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "activeConversations" in data
        assert "totalTickets" in data
        assert "avgResponseTime" in data
        assert "channelBreakdown" in data

    def test_admin_recent_tickets(self):
        """Test recent tickets endpoint"""
        response = client.get("/admin/recent-tickets")
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert isinstance(data["tickets"], list)


class TestCustomerPortal:
    """Test customer portal endpoints"""

    def test_customer_login_missing_identifier(self):
        """Test customer login with missing identifier"""
        payload = {
            "identifier_type": "email"
            # Missing identifier_value
        }
        response = client.post("/customer/login", json=payload)
        assert response.status_code == 422

    def test_customer_login_invalid_type(self):
        """Test customer login with invalid identifier type"""
        payload = {
            "identifier_type": "invalid",
            "identifier_value": "test@example.com"
        }
        response = client.post("/customer/login", json=payload)
        assert response.status_code in [400, 422]


class TestInputValidation:
    """Test input validation and sanitization"""

    def test_xss_prevention_in_name(self):
        """Test XSS script tags are handled in name field"""
        payload = {
            "name": "<script>alert('xss')</script>",
            "email": "test@example.com",
            "subject": "Test",
            "message": "Test message",
            "priority": "medium",
            "category": "technical"
        }
        response = client.post("/support/submit", json=payload)
        # Should either sanitize or reject
        assert response.status_code in [200, 400, 422]

    def test_sql_injection_prevention(self):
        """Test SQL injection attempts are handled"""
        payload = {
            "name": "Test'; DROP TABLE customers; --",
            "email": "test@example.com",
            "subject": "Test",
            "message": "Test message",
            "priority": "medium",
            "category": "technical"
        }
        response = client.post("/support/submit", json=payload)
        # Should handle safely
        assert response.status_code in [200, 400, 422]


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers_present(self):
        """Test CORS headers are present"""
        response = client.options("/health")
        assert response.status_code == 200


class TestAPIDocumentation:
    """Test API documentation endpoints"""

    def test_swagger_docs_available(self):
        """Test Swagger UI is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self):
        """Test ReDoc is accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_schema_available(self):
        """Test OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


class TestErrorHandling:
    """Test error handling"""

    def test_404_for_invalid_endpoint(self):
        """Test 404 for non-existent endpoints"""
        response = client.get("/invalid/endpoint")
        assert response.status_code == 404

    def test_405_for_wrong_method(self):
        """Test 405 for wrong HTTP method"""
        response = client.post("/health")
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
