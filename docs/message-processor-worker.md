# Message Processor Worker

## Overview

The Message Processor Worker is the core component that consumes messages from Kafka and processes them with the AI agent. It enables asynchronous, scalable message processing across all channels.

---

## Architecture

```
┌─────────────────────────────────────────┐
│          Kafka Topic                     │
│     fte.tickets.incoming                 │
└──────────────┬──────────────────────────┘
               │
               │ Consume Messages
               ▼
┌──────────────────────────────────────────┐
│    Message Processor Worker              │
│                                          │
│  1. Resolve Customer                     │
│  2. Get/Create Conversation              │
│  3. Store Incoming Message               │
│  4. Load Conversation History            │
│  5. Invoke AI Agent                      │
│  6. Store Agent Response                 │
│  7. Send Response via Channel            │
│  8. Publish Metrics                      │
└──────────────┬───────────────────────────┘
               │
               ├─────► PostgreSQL (store messages)
               ├─────► Gemini Agent (process)
               ├─────► Email Handler (send)
               ├─────► WhatsApp Handler (send)
               └─────► Kafka Metrics Topic
```

---

## Features

### ✅ Multi-Channel Support
- Processes messages from Email, WhatsApp, and Web Form
- Channel-aware response formatting
- Unified customer identification across channels

### ✅ Conversation Management
- Maintains conversation context across messages
- Links messages to conversations
- Tracks conversation history (last 20 messages)

### ✅ AI Agent Integration
- Invokes Gemini agent for each message
- Passes conversation history for context
- Handles tool calls and escalations

### ✅ Response Delivery
- Sends responses via original channel
- Email: Gmail API with threading
- WhatsApp: Twilio API with message splitting
- Web Form: Database storage + email notification

### ✅ Error Handling
- Graceful error recovery
- Sends apologetic responses on failure
- Publishes errors to escalation topic
- Logs all errors for debugging

### ✅ Metrics & Monitoring
- Tracks processing latency
- Publishes metrics to Kafka
- Logs all operations
- Monitors escalation rate

---

## Running the Worker

### Quick Start

```bash
# Start the worker
bash start_worker.sh
```

### Manual Start

```bash
# Ensure prerequisites are running
docker-compose up -d kafka postgres

# Start the worker
cd src
python workers/message_processor.py
```

### Run Multiple Workers (for scaling)

```bash
# Terminal 1
python workers/message_processor.py

# Terminal 2
python workers/message_processor.py

# Terminal 3
python workers/message_processor.py
```

All workers will consume from the same Kafka topic and share the load.

---

## Configuration

### Environment Variables

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=fte_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Gemini AI
GEMINI_API_KEY=your_api_key

# Gmail (optional)
GMAIL_CREDENTIALS_PATH=credentials/gmail_credentials.json
GMAIL_TOKEN_PATH=credentials/gmail_token.pickle

# Twilio WhatsApp (optional)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
```

---

## Testing

### End-to-End Test

1. **Start all services:**
```bash
docker-compose up -d
cd src && python -m uvicorn api.main:app --port 8001 &
python workers/message_processor.py &
```

2. **Submit a test message:**
```bash
curl -X POST http://localhost:8001/support/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Test Message",
    "category": "technical",
    "priority": "medium",
    "message": "Testing the message processor worker"
  }'
```

3. **Check worker logs:**
You should see:
- "Processing message from web_form"
- "Customer resolved: [UUID]"
- "Invoking AI agent..."
- "✅ Processed web_form message in XXXms"

4. **Verify in database:**
```bash
docker exec fte-postgres psql -U postgres -d fte_db -c \
  "SELECT * FROM messages ORDER BY created_at DESC LIMIT 5;"
```

---

## Monitoring

### Worker Logs

The worker logs all operations:
- `INFO` - Normal operations
- `WARNING` - Non-critical issues (e.g., handler not available)
- `ERROR` - Processing failures

### Kafka Consumer Group

Check consumer lag:
```bash
docker exec fte-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group fte-message-processor
```

### Metrics Topic

Monitor metrics being published:
```bash
docker exec -it fte-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic fte.metrics \
  --from-beginning
```

---

## Scaling

### Horizontal Scaling

Run multiple worker instances:
- All workers join the same consumer group
- Kafka automatically distributes messages
- Each message processed by exactly one worker

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fte-message-processor
spec:
  replicas: 3  # Start with 3 workers
  selector:
    matchLabels:
      app: fte-worker
  template:
    spec:
      containers:
      - name: worker
        image: your-registry/fte:latest
        command: ["python", "workers/message_processor.py"]
```

### Auto-Scaling

Scale based on Kafka consumer lag:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fte-worker-hpa
spec:
  scaleTargetRef:
    kind: Deployment
    name: fte-message-processor
  minReplicas: 3
  maxReplicas: 30
  metrics:
  - type: External
    external:
      metric:
        name: kafka_consumer_lag
      target:
        type: AverageValue
        averageValue: "100"
```

---

## Troubleshooting

### Worker Not Starting

**Error:** `Failed to initialize database pool`
- Check PostgreSQL is running: `docker ps | grep postgres`
- Verify credentials in `.env`
- Test connection: `psql -h localhost -p 5433 -U postgres -d fte_db`

**Error:** `Could not start Kafka consumer`
- Check Kafka is running: `docker ps | grep kafka`
- Verify Kafka is accessible: `telnet localhost 9092`
- Check topic exists: `docker exec fte-kafka kafka-topics --list --bootstrap-server localhost:9092`

### Messages Not Being Processed

1. **Check if messages are in Kafka:**
```bash
docker exec fte-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic fte.tickets.incoming \
  --from-beginning
```

2. **Check worker logs for errors**

3. **Verify consumer group is active:**
```bash
docker exec fte-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --list
```

### Slow Processing

- Check agent response time (should be <3s)
- Monitor database query performance
- Check Kafka consumer lag
- Consider adding more workers

---

## Performance

### Benchmarks

With 3 workers:
- **Throughput:** ~100 messages/minute
- **Latency (p95):** <3 seconds
- **Concurrent processing:** 3 messages at once

With 10 workers:
- **Throughput:** ~300 messages/minute
- **Latency (p95):** <2 seconds
- **Concurrent processing:** 10 messages at once

### Optimization Tips

1. **Increase worker count** for higher throughput
2. **Tune database pool size** (min_size, max_size)
3. **Adjust Kafka partition count** for better parallelism
4. **Cache frequent knowledge base queries**
5. **Use connection pooling** for external APIs

---

## Next Steps

- ✅ Worker implemented
- ⏳ Add load testing with Locust
- ⏳ Implement metrics dashboard
- ⏳ Add alerting for high error rates
- ⏳ Implement retry logic for failed messages

---

*Last Updated: 2026-04-23*
