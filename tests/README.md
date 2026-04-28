# Testing Guide - Customer Success FTE

## Overview
This guide covers all testing procedures for the multi-channel Customer Success FTE system.

## Test Suites

### 1. End-to-End Tests (`test_e2e_multichannel.py`)
Comprehensive tests covering all three channels: Email, WhatsApp, and Web Form.

**Test Coverage:**
- ✅ Web Form submission and validation
- ✅ Email channel integration
- ✅ WhatsApp channel integration
- ✅ Cross-channel customer continuity
- ✅ Channel-specific metrics
- ✅ Edge cases and error handling
- ✅ Performance testing

**Run E2E Tests:**
```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all E2E tests
pytest tests/test_e2e_multichannel.py -v

# Run specific test class
pytest tests/test_e2e_multichannel.py::TestWebFormChannel -v

# Run with coverage
pytest tests/test_e2e_multichannel.py --cov=src --cov-report=html

# Generate HTML report
pytest tests/test_e2e_multichannel.py --html=test-report.html --self-contained-html
```

### 2. Load Tests (`load_test.py`)
Simulates realistic traffic patterns across all channels using Locust.

**Load Test Scenarios:**
- **Light Load:** 10-20 users (normal business hours)
- **Medium Load:** 50-100 users (peak hours)
- **Heavy Load:** 200+ users (high-traffic events)
- **24-Hour Test:** Continuous operation test

**Run Load Tests:**
```bash
# Install Locust
pip install locust

# Light load test (10 users, 5 minutes)
locust -f tests/load_test.py \
       --host=https://fte-backend-3ohm.onrender.com \
       --users 10 --spawn-rate 2 --run-time 5m --headless

# Medium load test (50 users, 30 minutes)
locust -f tests/load_test.py \
       --host=https://fte-backend-3ohm.onrender.com \
       --users 50 --spawn-rate 5 --run-time 30m --headless

# Heavy load test (200 users, 1 hour)
locust -f tests/load_test.py \
       --host=https://fte-backend-3ohm.onrender.com \
       --users 200 --spawn-rate 10 --run-time 1h --headless

# 24-hour continuous test
locust -f tests/load_test.py \
       --host=https://fte-backend-3ohm.onrender.com \
       --users 50 --spawn-rate 5 --run-time 24h --headless

# Interactive web UI
locust -f tests/load_test.py \
       --host=https://fte-backend-3ohm.onrender.com
# Then open http://localhost:8089
```

## Test Results Interpretation

### E2E Test Success Criteria
- ✅ All web form validation tests pass
- ✅ Form submissions return valid ticket IDs
- ✅ Ticket status retrieval works
- ✅ All categories and priorities accepted
- ✅ Edge cases handled gracefully
- ✅ Response times < 3 seconds
- ✅ Concurrent submissions succeed

### Load Test Success Criteria (from requirements)
- ✅ **Uptime:** > 99.9%
- ✅ **P95 Latency:** < 3 seconds (all channels)
- ✅ **Success Rate:** > 95%
- ✅ **Escalation Rate:** < 25%
- ✅ **No Message Loss:** All submissions processed

## 24-Hour Continuous Operation Test

### Requirements
The system must survive a 24-hour test with:
- 100+ web form submissions
- 50+ email messages processed
- 50+ WhatsApp messages processed
- 10+ cross-channel customer interactions
- Random pod kills every 2 hours (chaos testing)

### Running the 24-Hour Test

**Step 1: Start the load test**
```bash
locust -f tests/load_test.py \
       --host=https://fte-backend-3ohm.onrender.com \
       --users 50 --spawn-rate 5 --run-time 24h \
       --csv=24h-test-results --headless
```

**Step 2: Monitor metrics**
```bash
# Check health endpoint
curl https://fte-backend-3ohm.onrender.com/health

# Check analytics
curl https://fte-backend-3ohm.onrender.com/analytics

# Monitor Render logs
# Go to: https://dashboard.render.com/web/srv-xxx/logs
```

**Step 3: Analyze results**
After 24 hours, check:
- `24h-test-results_stats.csv` - Request statistics
- `24h-test-results_failures.csv` - Failed requests
- `24h-test-results_stats_history.csv` - Time-series data

## Test Data

### Sample Test Emails
Use these for manual email testing:
- Send to: `naheadahmed@gmail.com`
- Subject: "Test Support Request"
- Body: "I need help with [issue description]"

### Sample Test Categories
- `general` - General questions
- `technical` - Technical support
- `billing` - Billing inquiries
- `feedback` - Product feedback
- `bug_report` - Bug reports

### Sample Test Priorities
- `low` - Not urgent
- `medium` - Need help soon
- `high` - Urgent issue

## Continuous Integration

### GitHub Actions (Optional)
Create `.github/workflows/test.yml`:
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/requirements.txt
      - name: Run E2E tests
        run: pytest tests/test_e2e_multichannel.py -v
```

## Troubleshooting

### Common Issues

**Issue: Tests timing out**
- Solution: Increase timeout in test client
- Check backend is running and accessible

**Issue: 422 Validation errors**
- Solution: Check request payload matches schema
- Verify all required fields are present

**Issue: 404 Not Found**
- Solution: Verify endpoint URLs are correct
- Check backend deployment is active

**Issue: Load test connection errors**
- Solution: Check backend URL is accessible
- Verify rate limits aren't being hit

## Test Coverage Report

Generate coverage report:
```bash
pytest tests/test_e2e_multichannel.py \
       --cov=src \
       --cov-report=html \
       --cov-report=term

# Open coverage report
open htmlcov/index.html
```

## Performance Benchmarks

### Expected Performance
- **Web Form Submission:** < 2 seconds
- **Ticket Status Lookup:** < 500ms
- **Customer Lookup:** < 1 second
- **Analytics Query:** < 2 seconds
- **Health Check:** < 100ms

### Monitoring Performance
```bash
# Run performance test
pytest tests/test_e2e_multichannel.py::TestPerformance -v

# Check response times in Locust
locust -f tests/load_test.py --host=https://fte-backend-3ohm.onrender.com
```

## Next Steps

1. ✅ Run E2E tests to verify all functionality
2. ✅ Run light load test (5 minutes)
3. ✅ Run medium load test (30 minutes)
4. ⏳ Run 24-hour continuous test
5. ⏳ Document results in `docs/24-hour-test-results.md`
6. ⏳ Fix any issues discovered
7. ⏳ Re-run tests until all pass

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Locust Documentation](https://docs.locust.io/)
- [HTTPX Documentation](https://www.python-httpx.org/)
- [Requirements Document](../The%20CRM%20Digital%20FTE%20Factory%20Final%20Hackathon%205.md)
