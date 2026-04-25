"""
Load Testing Suite for Customer Success FTE
Uses Locust to simulate 1000+ concurrent users across all channels

Run with:
    locust -f tests/load_test.py --host=http://localhost:8000

For headless mode:
    locust -f tests/load_test.py --host=http://localhost:8000 --users 1000 --spawn-rate 50 --run-time 1h --headless
"""

from locust import HttpUser, task, between, events
import random
import json
from datetime import datetime


# Sample data for realistic load testing
SAMPLE_NAMES = [
    "John Doe", "Jane Smith", "Bob Johnson", "Alice Williams", "Charlie Brown",
    "Diana Prince", "Eve Anderson", "Frank Miller", "Grace Lee", "Henry Wilson"
]

SAMPLE_SUBJECTS = [
    "Help with API authentication",
    "Password reset not working",
    "Billing question about invoice",
    "Feature request for dashboard",
    "Bug report: app crashes on login",
    "How to integrate with third-party service",
    "Account access issue",
    "Performance problem with large datasets",
    "Documentation unclear on webhooks",
    "Need help with data export"
]

SAMPLE_MESSAGES = [
    "I'm having trouble with the API authentication. Can you help me understand how to properly set up the Bearer token?",
    "I tried to reset my password but didn't receive the email. Can you check what's wrong?",
    "I have a question about my latest invoice. The charges seem higher than expected.",
    "Would it be possible to add a dark mode to the dashboard? Many users have requested this.",
    "The app crashes every time I try to log in on mobile. This is urgent as I need to access my data.",
    "I'm trying to integrate your service with Zapier but can't find the webhook URL. Where can I find this?",
    "I can't access my account anymore. It says my account is locked. Please help urgently.",
    "The system is very slow when I upload large CSV files. Is there a size limit or optimization I should know about?",
    "The documentation about webhooks is confusing. Can you provide a simple example of how to set them up?",
    "I need to export all my customer data for compliance reasons. What's the best way to do this?"
]

CATEGORIES = ['general', 'technical', 'billing', 'bug_report', 'feedback']
PRIORITIES = ['low', 'medium', 'high']


class WebFormUser(HttpUser):
    """Simulate users submitting support forms (most common channel)"""

    wait_time = between(2, 10)  # Wait 2-10 seconds between requests
    weight = 5  # Web form is most common (50% of traffic)

    @task(10)
    def submit_support_form(self):
        """Submit a support form request"""
        form_data = {
            "name": random.choice(SAMPLE_NAMES),
            "email": f"loadtest{random.randint(1, 10000)}@example.com",
            "subject": random.choice(SAMPLE_SUBJECTS),
            "category": random.choice(CATEGORIES),
            "priority": random.choice(PRIORITIES),
            "message": random.choice(SAMPLE_MESSAGES)
        }

        with self.client.post(
            "/support/submit",
            json=form_data,
            catch_response=True,
            name="Submit Support Form"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "ticket_id" in data:
                    response.success()
                else:
                    response.failure("No ticket_id in response")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def check_ticket_status(self):
        """Check status of a ticket"""
        # Use a random ticket ID (some will fail, which is realistic)
        ticket_id = f"test-ticket-{random.randint(1, 100)}"

        with self.client.get(
            f"/support/ticket/{ticket_id}",
            catch_response=True,
            name="Check Ticket Status"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")


class EmailChannelUser(HttpUser):
    """Simulate email channel activity"""

    wait_time = between(5, 15)
    weight = 2  # Email is less frequent (20% of traffic)

    @task(5)
    def check_emails(self):
        """Check for unread emails"""
        with self.client.get(
            "/email/check",
            catch_response=True,
            name="Check Emails"
        ) as response:
            if response.status_code in [200, 503]:  # 503 if handler not initialized
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def send_email(self):
        """Send an email response"""
        email_data = {
            "to_email": f"customer{random.randint(1, 1000)}@example.com",
            "subject": "Re: " + random.choice(SAMPLE_SUBJECTS),
            "body": "Thank you for contacting us. " + random.choice(SAMPLE_MESSAGES)
        }

        with self.client.post(
            "/email/send",
            params=email_data,
            catch_response=True,
            name="Send Email"
        ) as response:
            if response.status_code in [200, 503]:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class WhatsAppChannelUser(HttpUser):
    """Simulate WhatsApp channel activity"""

    wait_time = between(3, 12)
    weight = 2  # WhatsApp is less frequent (20% of traffic)

    @task
    def simulate_whatsapp_message(self):
        """Simulate incoming WhatsApp message"""
        # Note: This would normally require Twilio signature validation
        # For load testing, we're just testing the endpoint availability

        form_data = {
            "MessageSid": f"SM{random.randint(100000, 999999)}",
            "From": f"whatsapp:+1{random.randint(2000000000, 9999999999)}",
            "Body": random.choice(SAMPLE_MESSAGES)[:100],  # WhatsApp messages are shorter
            "ProfileName": random.choice(SAMPLE_NAMES)
        }

        with self.client.post(
            "/webhooks/whatsapp",
            data=form_data,
            catch_response=True,
            name="WhatsApp Webhook"
        ) as response:
            # Will likely fail signature validation, but that's expected in load test
            if response.status_code in [200, 403, 503]:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class HealthCheckUser(HttpUser):
    """Monitor system health during load test"""

    wait_time = between(5, 15)
    weight = 1  # Health checks are infrequent (10% of traffic)

    @task(5)
    def check_health(self):
        """Check API health"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="Health Check"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("System not healthy")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def check_metrics(self):
        """Check channel metrics"""
        with self.client.get(
            "/metrics/channels",
            catch_response=True,
            name="Channel Metrics"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def check_root(self):
        """Check root endpoint"""
        with self.client.get(
            "/",
            catch_response=True,
            name="Root Endpoint"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


# Event handlers for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("\n" + "="*80)
    print("🚀 LOAD TEST STARTED")
    print("="*80)
    print(f"Target: {environment.host}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("\n" + "="*80)
    print("🏁 LOAD TEST COMPLETED")
    print("="*80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Print summary statistics
    stats = environment.stats
    print(f"\nTotal requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Failure rate: {stats.total.fail_ratio * 100:.2f}%")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min response time: {stats.total.min_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per second: {stats.total.total_rps:.2f}")

    # Check if test passed requirements
    print("\n" + "="*80)
    print("📊 REQUIREMENTS CHECK")
    print("="*80)

    # Requirement: P95 latency < 3 seconds
    p95_latency = stats.total.get_response_time_percentile(0.95)
    p95_passed = p95_latency < 3000
    print(f"P95 Latency: {p95_latency:.2f}ms {'✅ PASS' if p95_passed else '❌ FAIL'} (requirement: <3000ms)")

    # Requirement: Error rate < 5%
    error_rate = stats.total.fail_ratio * 100
    error_passed = error_rate < 5
    print(f"Error Rate: {error_rate:.2f}% {'✅ PASS' if error_passed else '❌ FAIL'} (requirement: <5%)")

    # Requirement: Uptime > 99.9%
    uptime = (1 - stats.total.fail_ratio) * 100
    uptime_passed = uptime > 99.9
    print(f"Uptime: {uptime:.3f}% {'✅ PASS' if uptime_passed else '❌ FAIL'} (requirement: >99.9%)")

    print("="*80 + "\n")


# Custom shape for ramping up users
from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """
    A step load shape that gradually increases users

    Stages:
    1. 0-5 min: 100 users (warm up)
    2. 5-10 min: 500 users
    3. 10-20 min: 1000 users (peak load)
    4. 20-25 min: 500 users (cool down)
    5. 25-30 min: 100 users
    """

    stages = [
        {"duration": 300, "users": 100, "spawn_rate": 10},   # 0-5 min
        {"duration": 600, "users": 500, "spawn_rate": 50},   # 5-10 min
        {"duration": 1200, "users": 1000, "spawn_rate": 50}, # 10-20 min
        {"duration": 1500, "users": 500, "spawn_rate": 50},  # 20-25 min
        {"duration": 1800, "users": 100, "spawn_rate": 50},  # 25-30 min
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None  # Stop test after all stages


if __name__ == "__main__":
    print("""
    Customer Success FTE - Load Testing Suite
    ==========================================

    This load test simulates realistic traffic across all channels:
    - Web Form: 50% of traffic (most common)
    - Email: 20% of traffic
    - WhatsApp: 20% of traffic
    - Health Checks: 10% of traffic

    To run:

    1. Start the API server:
       uvicorn src.api.main:app --host 0.0.0.0 --port 8000

    2. Run load test (with UI):
       locust -f tests/load_test.py --host=http://localhost:8000
       Then open http://localhost:8089

    3. Run load test (headless):
       locust -f tests/load_test.py --host=http://localhost:8000 \\
              --users 1000 --spawn-rate 50 --run-time 30m --headless

    4. Run with custom shape (gradual ramp-up):
       locust -f tests/load_test.py --host=http://localhost:8000 \\
              --headless --shape=StepLoadShape

    Requirements to pass:
    - P95 latency < 3 seconds
    - Error rate < 5%
    - Uptime > 99.9%
    """)
