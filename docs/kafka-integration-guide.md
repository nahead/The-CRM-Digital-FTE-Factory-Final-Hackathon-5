# Kafka Integration Guide

## Overview

The Customer Success FTE now uses Apache Kafka for event streaming across all three channels (Email, WhatsApp, Web Form). This enables:

- **Asynchronous processing** - API responds immediately, agent processes in background
- **Scalability** - Multiple workers can consume from the same topic
- **Reliability** - Messages are persisted and can be replayed
- **Decoupling** - Channels publish events without knowing about consumers

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Incoming Channels                     │
├──────────────┬──────────────────┬────────────────────────┤
│   📧 Email   │  💬 WhatsApp     │   🌐 Web Form         │
│   (Gmail)    │   (Twilio)       │   (Next.js)           │
└──────┬───────┴────────┬─────────┴──────────┬────────────┘
       │                │                     │
       └────────────────┼─────────────────────┘
                        │
                ┌───────▼────────┐
                │   FastAPI      │
                │  (Port 8001)   │
                └───────┬────────┘
                        │
                        │ Publish Events
                        ▼
                ┌───────────────┐
                │     Kafka     │
                │  (Port 9092)  │
                └───────┬───────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │ Worker  │    │ Worker  │    │ Worker  │
   │    1    │    │    2    │    │    3    │
   └─────────┘    └─────────┘    └─────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
                ┌───────▼────────┐
                │  Gemini Agent  │
                │   Processing   │
                └────────────────┘
```

---

## Kafka Topics

### Incoming Tickets
- **Topic:** `fte.tickets.incoming`
- **Purpose:** All incoming customer messages from any channel
- **Consumers:** Message processor workers
- **Message Format:**
```json
{
  "channel": "email|whatsapp|web_form",
  "channel_message_id": "unique-id",
  "customer_email": "customer@example.com",
  "customer_name": "Customer Name",
  "subject": "Issue subject",
  "content": "Message content",
  "category": "technical|billing|general",
  "priority": "low|medium|high|urgent",
  "received_at": "2026-04-23T10:30:00Z",
  "metadata": {}
}
```

### Channel-Specific Topics
- **Email Inbound:** `fte.channels.email.inbound`
- **WhatsApp Inbound:** `fte.channels.whatsapp.inbound`
- **Web Form Inbound:** `fte.channels.webform.inbound`
- **Email Outbound:** `fte.channels.email.outbound`
- **WhatsApp Outbound:** `fte.channels.whatsapp.outbound`

### System Topics
- **Escalations:** `fte.escalations` - Messages requiring human intervention
- **Metrics:** `fte.metrics` - Performance and monitoring data
- **Dead Letter Queue:** `fte.dlq` - Failed message processing

---

## Setup

### 1. Start Kafka with Docker Compose

```bash
# Start Kafka and Zookeeper
docker-compose up -d zookeeper kafka

# Verify Kafka is running
docker ps | grep kafka

# Check Kafka logs
docker logs fte-kafka
```

### 2. Verify Topics Created

```bash
# List all topics
docker exec fte-kafka kafka-topics --list --bootstrap-server localhost:9092

# Create topics manually if needed
docker exec fte-kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic fte.tickets.incoming \
  --partitions 3 \
  --replication-factor 1
```

### 3. Start the API

```bash
cd src
python -m uvicorn api.main:app --port 8001
```

The API will automatically:
- Initialize Kafka producer on startup
- Publish events to Kafka when messages arrive
- Handle Kafka unavailability gracefully (continues without Kafka)

---

## Testing Kafka Integration

### Test Script

```bash
# Run the automated test
bash test_kafka_integration.sh
```

### Manual Testing

#### 1. Monitor Kafka Messages

Open a terminal and start consuming messages:

```bash
docker exec -it fte-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic fte.tickets.incoming \
  --from-beginning
```

#### 2. Submit a Web Form

In another terminal:

```bash
curl -X POST http://localhost:8001/support/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Test Message",
    "category": "technical",
    "priority": "medium",
    "message": "Testing Kafka integration"
  }'
```

You should see the message appear in the Kafka consumer terminal.

#### 3. Test Email Channel

```bash
curl -X POST http://localhost:8001/email/check
```

Any unread emails will be published to Kafka.

#### 4. Test WhatsApp Channel

Send a WhatsApp message to your Twilio number. The webhook will publish to Kafka.

---

## Message Flow

### Web Form Submission

1. User submits form at `http://localhost:3000`
2. Next.js sends POST to `/support/submit`
3. FastAPI creates ticket in PostgreSQL
4. FastAPI publishes event to `fte.tickets.incoming` (background task)
5. Returns ticket ID to user immediately
6. Worker consumes message from Kafka
7. Worker invokes Gemini agent
8. Agent processes and responds

### Email Received

1. Gmail receives email
2. Pub/Sub notifies webhook at `/webhooks/gmail`
3. FastAPI fetches email via Gmail API
4. FastAPI publishes to `fte.tickets.incoming`
5. Worker processes asynchronously

### WhatsApp Message

1. Customer sends WhatsApp message
2. Twilio webhook calls `/webhooks/whatsapp`
3. FastAPI validates signature and parses message
4. FastAPI publishes to `fte.tickets.incoming`
5. Returns empty TwiML (agent responds later)
6. Worker processes and sends response via Twilio

---

## Monitoring

### Check Kafka Consumer Lag

```bash
docker exec fte-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group fte-message-processor
```

### View Topic Details

```bash
docker exec fte-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic fte.tickets.incoming
```

### Count Messages in Topic

```bash
docker exec fte-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic fte.tickets.incoming \
  --time -1
```

---

## Configuration

### Environment Variables

```bash
# .env file
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### Kafka Client Settings

In `src/kafka_client.py`:

```python
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
```

---

## Troubleshooting

### Kafka Not Starting

```bash
# Check Zookeeper is running first
docker ps | grep zookeeper

# Restart Kafka
docker-compose restart kafka

# Check logs
docker logs fte-kafka --tail 100
```

### Messages Not Being Published

1. Check API logs for Kafka errors
2. Verify Kafka is accessible: `telnet localhost 9092`
3. Check if topic exists: `docker exec fte-kafka kafka-topics --list --bootstrap-server localhost:9092`

### API Continues Without Kafka

This is expected behavior. The API will:
- Log a warning: "Kafka not available"
- Continue processing requests
- Store tickets in database
- Skip event publishing

To enable Kafka, ensure it's running and restart the API.

---

## Production Considerations

### 1. Kafka Cluster

Use a managed Kafka service:
- **Confluent Cloud** - Fully managed, easy setup
- **AWS MSK** - Managed Streaming for Kafka
- **Azure Event Hubs** - Kafka-compatible

### 2. Topic Configuration

```bash
# Production settings
--partitions 10              # More partitions for parallelism
--replication-factor 3       # High availability
--config retention.ms=604800000  # 7 days retention
--config compression.type=snappy # Compression
```

### 3. Consumer Groups

Multiple workers in same consumer group = load balancing
Different consumer groups = independent processing

### 4. Monitoring

- Set up Kafka metrics in Prometheus
- Monitor consumer lag
- Alert on DLQ messages
- Track processing latency

---

## Next Steps

1. ✅ Kafka producer integrated in API
2. ⏳ Implement message processor worker (see `workers/message_processor.py`)
3. ⏳ Add metrics publishing to `fte.metrics` topic
4. ⏳ Implement escalation event publishing
5. ⏳ Add dead letter queue handling

---

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [aiokafka Documentation](https://aiokafka.readthedocs.io/)
- [Confluent Kafka Best Practices](https://docs.confluent.io/platform/current/kafka/deployment.html)

---

*Last Updated: 2026-04-23*
