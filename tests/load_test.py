"""
Load Testing Suite for Customer Success FTE
Uses Locust to simulate realistic load across all channels

Run with: locust -f tests/load_test.py --host=https://fte-backend-3ohm.onrender.com
"""

from locust import HttpUser, task, between, events
import random
import uuid
from datetime import datetime

# Sample data for realistic load testing
SAMPLE_NAMES = [
    "John Smith", "Jane Doe", "Michael Johnson", "Sarah Williams",
    "David Brown", "Emily Davis", "Robert Miller", "Lisa Wilson",
    "James Moore", "Mary Taylor", "Christopher Anderson", "Patricia Thomas"
]

SAMPLE_SUBJECTS = [
    "Help with password reset",
    "API authentication issues",
    "Cannot access my account",
    "Billing question about invoice",
    "Feature request for dashboard",
    "Bug report: page not loading",
    "How to export my data?",
    "Integration with third-party service",
    "Performance issues with API",
    "Need help with configuration",
    "Account upgrade question",
    "Technical support needed"
]

SAMPLE_MESSAGES = [
    "I'm having trouble accessing my account. Can you help me reset my password?",
    "I'm getting 401 errors when trying to authenticate with the API. I've checked my credentials and they seem correct.",
    "The dashboard is loading very slowly. Is there a known issue?",
    "I need to export all my data for compliance purposes. What's the best way to do this?",
    "I'm trying to integrate your service with our internal system but the webhook isn't working.",
    "I received an invoice but the amount doesn't match what I expected. Can you review it?",
    "Is there a way to customize the notification settings? I can't find the option.",
    "The mobile app keeps crashing when I try to upload files. I'm using iOS 15.",
    "I'd like to upgrade my plan but I'm not sure which tier is best for my needs.",
    "Can you explain how the rate limiting works on the API? I'm hitting limits unexpectedly."
]

CATEGORIES = ["general", "technical", "billing", "feedback", "bug_report"]
PRIORITIES = ["low", "medium", "high"]


class WebFormUser(HttpUser):
    """Simulates users submitting support forms (60% of traffic)."""
    wait_time = between(2, 10)
    weight = 6

    @task(10)
    def submit_support_form(self):
        self.client.post("/support/submit", json={
            "name": random.choice(SAMPLE_NAMES),
            "email": f"loadtest_{uuid.uuid4().hex[:8]}@example.com",
            "subject": random.choice(SAMPLE_SUBJECTS),
            "category": random.choice(CATEGORIES),
            "priority": random.choice(PRIORITIES),
            "message": random.choice(SAMPLE_MESSAGES)
        }, name="/support/submit")

    @task(2)
    def check_ticket_status(self):
        ticket_id = str(uuid.uuid4())
        self.client.get(f"/support/ticket/{ticket_id}", name="/support/ticket/[id]")


class HealthCheckUser(HttpUser):
    """Simulates monitoring systems (10% of traffic)."""
    wait_time = between(5, 15)
    weight = 1

    @task
    def check_health(self):
        self.client.get("/health", name="/health")


class CustomerPortalUser(HttpUser):
    """Simulates customers checking history (30% of traffic)."""
    wait_time = between(5, 20)
    weight = 3

    @task(5)
    def lookup_customer(self):
        email = f"customer_{random.randint(1, 1000)}@example.com"
        self.client.get("/customer/lookup", params={"email": email}, name="/customer/lookup")

    @task(1)
    def submit_followup(self):
        self.client.post("/support/submit", json={
            "name": random.choice(SAMPLE_NAMES),
            "email": f"customer_{random.randint(1, 1000)}@example.com",
            "subject": "Follow-up: " + random.choice(SAMPLE_SUBJECTS),
            "category": random.choice(CATEGORIES),
            "priority": "medium",
            "message": "Following up on my previous request. " + random.choice(SAMPLE_MESSAGES)
        }, name="/support/submit (follow-up)")
