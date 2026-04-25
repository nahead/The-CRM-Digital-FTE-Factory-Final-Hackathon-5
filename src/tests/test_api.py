"""
Basic tests for the Customer Success FTE
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.main import app

client = TestClient(app)


class TestAPI:
    """Test FastAPI endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns service info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Customer Success FTE API"
        assert "channels" in data

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "channels" in data


class TestWebForm:
    """Test web support form"""

    def test_form_submission_valid(self):
        """Test valid form submission"""
        response = client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Issue",
            "category": "technical",
            "message": "This is a test message for the support system"
        })
        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        assert data["message"] is not None

    def test_form_validation_short_name(self):
        """Test form validation rejects short names"""
        response = client.post("/support/submit", json={
            "name": "A",
            "email": "test@example.com",
            "subject": "Test",
            "category": "general",
            "message": "Test message"
        })
        assert response.status_code == 422

    def test_form_validation_invalid_email(self):
        """Test form validation rejects invalid emails"""
        response = client.post("/support/submit", json={
            "name": "Test User",
            "email": "invalid-email",
            "subject": "Test",
            "category": "general",
            "message": "Test message"
        })
        assert response.status_code == 422

    def test_form_validation_short_message(self):
        """Test form validation rejects short messages"""
        response = client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test",
            "category": "general",
            "message": "Short"
        })
        assert response.status_code == 422

    def test_form_validation_invalid_category(self):
        """Test form validation rejects invalid categories"""
        response = client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test",
            "category": "invalid_category",
            "message": "This is a test message"
        })
        assert response.status_code == 422


class TestMetrics:
    """Test metrics endpoints"""

    def test_channel_metrics(self):
        """Test channel metrics endpoint"""
        response = client.get("/metrics/channels")
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "whatsapp" in data
        assert "web_form" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
