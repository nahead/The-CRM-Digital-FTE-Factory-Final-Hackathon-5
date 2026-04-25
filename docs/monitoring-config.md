# Monitoring Configuration for Customer Success FTE

## Overview
This document defines monitoring, metrics, and alerting for the Customer Success FTE system.

---

## Prometheus Metrics

### Application Metrics

```python
# Add to src/api/main.py

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Ticket metrics
tickets_created_total = Counter(
    'tickets_created_total',
    'Total tickets created',
    ['channel', 'category', 'priority']
)

tickets_escalated_total = Counter(
    'tickets_escalated_total',
    'Total tickets escalated',
    ['reason', 'channel']
)

tickets_resolved_total = Counter(
    'tickets_resolved_total',
    'Total tickets resolved',
    ['channel', 'category']
)

# Sentiment metrics
sentiment_score_gauge = Gauge(
    'sentiment_score',
    'Current sentiment score',
    ['customer_id', 'channel']
)

negative_sentiment_total = Counter(
    'negative_sentiment_total',
    'Total negative sentiment detections',
    ['channel']
)

# Performance metrics
knowledge_base_search_duration = Histogram(
    'knowledge_base_search_duration_seconds',
    'Knowledge base search duration',
    ['category']
)

database_query_duration = Histogram(
    'database_query_duration_seconds',
    'Database query duration',
    ['operation']
)

# Agent metrics
agent_responses_total = Counter(
    'agent_responses_total',
    'Total agent responses generated',
    ['channel', 'escalated']
)

agent_response_duration = Histogram(
    'agent_response_duration_seconds',
    'Agent response generation time',
    ['channel']
)

# Error metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['type', 'component']
)

# Active connections
active_connections = Gauge(
    'active_connections',
    'Number of active connections',
    ['type']
)

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

---

## Grafana Dashboards

### Dashboard 1: System Overview

**Panels:**

1. **Request Rate**
   - Metric: `rate(http_requests_total[5m])`
   - Type: Graph
   - Alert: > 1000 req/s

2. **Response Time (p95)**
   - Metric: `histogram_quantile(0.95, http_request_duration_seconds)`
   - Type: Graph
   - Alert: > 3s

3. **Error Rate**
   - Metric: `rate(errors_total[5m])`
   - Type: Graph
   - Alert: > 5%

4. **Active Connections**
   - Metric: `active_connections`
   - Type: Gauge
   - Alert: > 900

### Dashboard 2: Business Metrics

**Panels:**

1. **Tickets Created by Channel**
   - Metric: `sum by (channel) (tickets_created_total)`
   - Type: Stacked graph

2. **Escalation Rate**
   - Metric: `tickets_escalated_total / tickets_created_total * 100`
   - Type: Gauge
   - Target: < 20%

3. **Resolution Rate**
   - Metric: `tickets_resolved_total / tickets_created_total * 100`
   - Type: Gauge
   - Target: > 60%

4. **Average Sentiment Score**
   - Metric: `avg(sentiment_score)`
   - Type: Graph
   - Alert: < 0.4

### Dashboard 3: Performance

**Panels:**

1. **Database Query Time**
   - Metric: `histogram_quantile(0.95, database_query_duration_seconds)`
   - Type: Graph
   - Alert: > 100ms

2. **Knowledge Base Search Time**
   - Metric: `histogram_quantile(0.95, knowledge_base_search_duration_seconds)`
   - Type: Graph
   - Alert: > 500ms

3. **Agent Response Time**
   - Metric: `histogram_quantile(0.95, agent_response_duration_seconds)`
   - Type: Graph
   - Alert: > 2s

---

## Alert Rules

### Critical Alerts (Page Immediately)

```yaml
# prometheus-alerts.yml

groups:
  - name: critical
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: SystemDown
        expr: up{job="fte-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "FTE API is down"
          description: "API has been down for 1 minute"

      - alert: DatabaseConnectionFailed
        expr: active_connections{type="database"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "Database connection lost"
          description: "No active database connections"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Response time > 10s"
          description: "p95 response time is {{ $value }}s"
```

### Warning Alerts (Investigate Soon)

```yaml
  - name: warnings
    interval: 1m
    rules:
      - alert: ElevatedErrorRate
        expr: rate(errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Elevated error rate"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: HighEscalationRate
        expr: (tickets_escalated_total / tickets_created_total) > 0.25
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Escalation rate > 25%"
          description: "{{ $value }}% of tickets are being escalated"

      - alert: LowSentimentScore
        expr: avg(sentiment_score) < 0.4
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Low average sentiment"
          description: "Average sentiment is {{ $value }}"

      - alert: SlowDatabaseQueries
        expr: histogram_quantile(0.95, database_query_duration_seconds) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow database queries"
          description: "p95 query time is {{ $value }}s"
```

---

## Logging Configuration

### Log Levels

```python
# src/api/main.py

import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'logs/fte-api.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Log Events

**INFO Level:**
- Ticket created
- Customer identified
- Response sent
- Escalation triggered

**WARNING Level:**
- Negative sentiment detected
- Slow query (>100ms)
- High error rate
- Escalation threshold exceeded

**ERROR Level:**
- Database connection failed
- External API timeout
- Invalid data format
- Unhandled exception

**Example:**
```python
logger.info(f"Ticket created: {ticket_id} for customer {customer_id} via {channel}")
logger.warning(f"Negative sentiment detected: {sentiment_score} for ticket {ticket_id}")
logger.error(f"Database query failed: {error_message}")
```

---

## Health Checks

### Kubernetes Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8001
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Kubernetes Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /health
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns 200 if system is healthy
    """
    checks = {
        "database": await check_database(),
        "gemini_api": await check_gemini_api(),
        "kafka": await check_kafka()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "checks": checks
        }
    )
```

---

## Performance Monitoring

### Key Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Response Time (p95) | < 3s | > 5s |
| Response Time (p99) | < 5s | > 10s |
| Error Rate | < 1% | > 5% |
| Escalation Rate | < 20% | > 25% |
| Database Query Time | < 100ms | > 200ms |
| Knowledge Base Search | < 500ms | > 1s |
| Sentiment Score | > 0.5 | < 0.4 |
| Uptime | 99.9% | < 99% |

---

## Deployment Monitoring

### Kubernetes Metrics

```bash
# Pod status
kubectl get pods -n fte-production

# Resource usage
kubectl top pods -n fte-production

# Logs
kubectl logs -f deployment/fte-api -n fte-production

# Events
kubectl get events -n fte-production --sort-by='.lastTimestamp'
```

### Auto-Scaling Metrics

```yaml
# HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fte-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fte-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Monitoring Tools Setup

### Prometheus Installation

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --create-namespace \
  --set server.persistentVolume.size=50Gi
```

### Grafana Installation

```bash
# Add Grafana Helm repo
helm repo add grafana https://grafana.github.io/helm-charts

# Install Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set persistence.enabled=true \
  --set persistence.size=10Gi \
  --set adminPassword=admin123
```

### Access Grafana

```bash
# Port forward
kubectl port-forward -n monitoring svc/grafana 3000:80

# Access at http://localhost:3000
# Username: admin
# Password: admin123
```

---

## Cost Monitoring

### Monthly Cost Breakdown

| Component | Cost/Month | Notes |
|-----------|------------|-------|
| Kubernetes (3 nodes) | $150 | GKE/EKS standard |
| PostgreSQL | $50 | Managed instance |
| Gemini API | $0-50 | Free tier + usage |
| Monitoring | $20 | Prometheus/Grafana |
| **Total** | **$220-270** | vs $6,250 human FTE |

### Cost Alerts

```yaml
# Set budget alerts in cloud provider
- Budget: $300/month
- Alert at: 80% ($240)
- Alert at: 100% ($300)
```

---

## Success Metrics Dashboard

### Daily Report

```sql
-- Generate daily metrics report
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_tickets,
    COUNT(*) FILTER (WHERE status = 'escalated') as escalated,
    COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
    AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))) as avg_resolution_time_seconds,
    source_channel
FROM tickets
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY DATE(created_at), source_channel;
```

### Weekly Summary

- Total tickets handled
- Escalation rate by channel
- Average sentiment score
- Response time percentiles
- Cost per ticket
- Customer satisfaction (if available)

---

## Version History

- **v1.0** - Initial monitoring configuration
  - Prometheus metrics
  - Grafana dashboards
  - Alert rules
  - Health checks
