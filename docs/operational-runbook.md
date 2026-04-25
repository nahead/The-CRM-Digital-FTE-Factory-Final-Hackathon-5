# Operational Runbook - Customer Success FTE

## Purpose
This runbook provides step-by-step procedures for operating and troubleshooting the Customer Success FTE system.

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Startup Procedures](#startup-procedures)
3. [Shutdown Procedures](#shutdown-procedures)
4. [Common Incidents](#common-incidents)
5. [Escalation Procedures](#escalation-procedures)
6. [Maintenance Tasks](#maintenance-tasks)
7. [Emergency Contacts](#emergency-contacts)

---

## System Architecture

### Components
- **API Server**: FastAPI on port 8001
- **Database**: PostgreSQL on port 5433
- **Web Form**: Next.js on port 3000
- **AI Engine**: Google Gemini 1.5 Flash
- **Message Queue**: Apache Kafka (optional)

### Dependencies
- Docker Desktop (for PostgreSQL)
- Python 3.9+
- Node.js 18+
- Internet connection (for Gemini API)

---

## Startup Procedures

### Full System Startup (5 minutes)

**Step 1: Start Docker Desktop**
```bash
# Windows: Open Docker Desktop from Start menu
# Wait for whale icon to turn green in system tray

# Verify Docker is running
docker ps
```

**Step 2: Start PostgreSQL Container**
```bash
# Start existing container
docker start fte-postgres

# Verify it's running
docker ps | grep fte-postgres

# Expected output: fte-postgres ... Up ... 0.0.0.0:5433->5432/tcp
```

**Step 3: Start API Server**
```bash
# Navigate to project directory
cd D:\Coding\Q4\hackathons\Hackathon-5\src

# Start API server
python -m uvicorn api.main:app --port 8001

# Keep this terminal open
```

**Step 4: Start Web Form (New Terminal)**
```bash
# Navigate to web form directory
cd D:\Coding\Q4\hackathons\Hackathon-5\src\web-form

# Start development server
npm run dev

# Keep this terminal open
```

**Step 5: Verify System Health**
```bash
# Check API health
curl http://localhost:8001/health

# Check web form
curl http://localhost:3000

# Check database
docker exec fte-postgres psql -U postgres -d fte_db -c "SELECT COUNT(*) FROM tickets;"
```

### Quick Status Check
```bash
echo "=== SYSTEM STATUS ===" && \
docker ps | grep fte-postgres && \
curl -s http://localhost:8001/health | grep status && \
curl -s http://localhost:3000 | grep -o "<title>.*</title>"
```

---

## Shutdown Procedures

### Graceful Shutdown

**Step 1: Stop Web Form**
```bash
# In web form terminal, press Ctrl+C
# Wait for "Gracefully shutting down" message
```

**Step 2: Stop API Server**
```bash
# In API terminal, press Ctrl+C
# Wait for "Shutting down" message
```

**Step 3: Stop PostgreSQL (Optional)**
```bash
# Only if you want to stop database
docker stop fte-postgres
```

**Step 4: Stop Docker Desktop (Optional)**
```bash
# Right-click whale icon in system tray
# Select "Quit Docker Desktop"
```

---

## Common Incidents

### Incident 1: API Server Not Responding

**Symptoms:**
- `curl http://localhost:8001/health` returns connection refused
- Web form shows "Failed to submit" errors

**Diagnosis:**
```bash
# Check if API process is running
netstat -ano | findstr :8001

# Check API logs
# Look at terminal where API is running
```

**Resolution:**
1. Check if API terminal was closed accidentally
2. Restart API server:
   ```bash
   cd D:\Coding\Q4\hackathons\Hackathon-5\src
   python -m uvicorn api.main:app --port 8001
   ```
3. Verify health: `curl http://localhost:8001/health`

**Prevention:**
- Keep API terminal open
- Use process manager (PM2, systemd) in production

---

### Incident 2: Database Connection Failed

**Symptoms:**
- API returns 500 errors
- Logs show: "password authentication failed" or "connection refused"

**Diagnosis:**
```bash
# Check if PostgreSQL container is running
docker ps | grep fte-postgres

# Check PostgreSQL logs
docker logs fte-postgres --tail 50

# Test connection
docker exec fte-postgres psql -U postgres -d fte_db -c "SELECT 1;"
```

**Resolution:**

**Option A: Container not running**
```bash
docker start fte-postgres
# Wait 10 seconds
docker ps | grep fte-postgres
```

**Option B: Wrong credentials**
```bash
# Check .env file
cat D:\Coding\Q4\hackathons\Hackathon-5\.env | grep POSTGRES

# Should show:
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5433
# POSTGRES_DB=fte_db
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres123
```

**Option C: Port conflict**
```bash
# Check if port 5433 is in use
netstat -ano | findstr :5433

# If occupied by another process, either:
# 1. Stop that process
# 2. Change PostgreSQL port in docker-compose
```

**Prevention:**
- Always start Docker before API
- Keep PostgreSQL container running
- Monitor database connections

---

### Incident 3: Web Form Not Loading

**Symptoms:**
- Browser shows "This site can't be reached"
- `curl http://localhost:3000` fails

**Diagnosis:**
```bash
# Check if Next.js is running
netstat -ano | findstr :3000

# Check for errors in web form terminal
```

**Resolution:**
1. Check if web form terminal was closed
2. Restart web form:
   ```bash
   cd D:\Coding\Q4\hackathons\Hackathon-5\src\web-form
   npm run dev
   ```
3. Wait for "Ready in 3s" message
4. Open browser: http://localhost:3000

**Prevention:**
- Keep web form terminal open
- Use PM2 or similar in production

---

### Incident 4: Port Already in Use

**Symptoms:**
- Error: "EADDRINUSE: address already in use :::8001"
- Error: "EADDRINUSE: address already in use :::3000"

**Diagnosis:**
```bash
# Find process using port 8001
netstat -ano | findstr :8001

# Find process using port 3000
netstat -ano | findstr :3000
```

**Resolution:**
```bash
# Kill process (replace <PID> with actual PID from netstat)
taskkill /F /PID <PID>

# Then restart the service
```

**Prevention:**
- Properly shut down services before restarting
- Use different ports if needed

---

### Incident 5: High Error Rate (>5%)

**Symptoms:**
- Multiple 500 errors in API logs
- Prometheus alert: "HighErrorRate"

**Diagnosis:**
```bash
# Check recent errors in database
docker exec fte-postgres psql -U postgres -d fte_db -c \
  "SELECT COUNT(*), category FROM tickets WHERE status = 'error' 
   AND created_at > NOW() - INTERVAL '1 hour' GROUP BY category;"

# Check API logs for stack traces
# Look for patterns in error messages
```

**Resolution:**
1. Identify error pattern (database, API, external service)
2. If database errors: Check connection pool, restart PostgreSQL
3. If API errors: Check Gemini API key, restart API server
4. If external service: Wait for service recovery or disable feature

**Escalation:**
- If error rate >10% for >5 minutes: Page on-call engineer
- If data loss suspected: Escalate to senior engineer immediately

---

### Incident 6: Slow Response Time (>5s)

**Symptoms:**
- Users report slow form submissions
- Prometheus alert: "HighResponseTime"

**Diagnosis:**
```bash
# Check database query performance
docker exec fte-postgres psql -U postgres -d fte_db -c \
  "SELECT query, mean_exec_time, calls FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC LIMIT 10;"

# Check API server load
# Look at CPU/memory usage in task manager
```

**Resolution:**
1. **Slow database queries:**
   ```bash
   # Add missing indexes
   docker exec fte-postgres psql -U postgres -d fte_db -c \
     "CREATE INDEX IF NOT EXISTS idx_tickets_customer_id ON tickets(customer_id);"
   ```

2. **High API load:**
   - Scale up: Add more API server instances
   - Restart API server to clear memory leaks

3. **Gemini API slow:**
   - Check Gemini API status
   - Implement caching for common queries

**Prevention:**
- Monitor query performance regularly
- Set up auto-scaling
- Cache frequent responses

---

### Incident 7: Gemini API Quota Exceeded

**Symptoms:**
- API returns: "Quota exceeded"
- Agent responses fail

**Diagnosis:**
```bash
# Check Gemini API usage
# Visit: https://aistudio.google.com/app/apikey

# Check recent API calls
grep "Gemini API" logs/fte-api.log | tail -50
```

**Resolution:**
1. **Immediate:** Switch to fallback responses
   ```python
   # In src/agent/gemini_agent.py
   # Use template responses instead of AI generation
   ```

2. **Short-term:** Upgrade Gemini API plan
3. **Long-term:** Implement response caching

**Prevention:**
- Monitor API usage daily
- Set up quota alerts
- Cache common responses

---

## Escalation Procedures

### Severity Levels

**P0 - Critical (Page Immediately)**
- System completely down (>5 minutes)
- Data loss detected
- Security breach
- Error rate >50%

**P1 - High (Respond within 30 minutes)**
- Partial system outage
- Error rate >10%
- Response time >10s
- Database connection issues

**P2 - Medium (Respond within 4 hours)**
- Error rate 5-10%
- Response time 5-10s
- Single channel down
- Non-critical feature broken

**P3 - Low (Respond within 24 hours)**
- Minor bugs
- Performance degradation
- Feature requests
- Documentation issues

### Escalation Contacts

**On-Call Engineer:**
- Primary: [Your Name] - [Phone]
- Secondary: [Backup Name] - [Phone]

**Escalation Path:**
1. On-call engineer (0-30 min)
2. Team lead (30-60 min)
3. Engineering manager (60+ min)

---

## Maintenance Tasks

### Daily Tasks

**Morning Health Check (5 minutes)**
```bash
# Run status check
cd D:\Coding\Q4\hackathons\Hackathon-5
bash scripts/health_check.sh

# Check overnight tickets
docker exec fte-postgres psql -U postgres -d fte_db -c \
  "SELECT COUNT(*), status FROM tickets 
   WHERE created_at > NOW() - INTERVAL '24 hours' 
   GROUP BY status;"

# Review error logs
tail -100 logs/fte-api.log | grep ERROR
```

### Weekly Tasks

**Database Maintenance (15 minutes)**
```bash
# Vacuum database
docker exec fte-postgres psql -U postgres -d fte_db -c "VACUUM ANALYZE;"

# Check database size
docker exec fte-postgres psql -U postgres -d fte_db -c \
  "SELECT pg_size_pretty(pg_database_size('fte_db'));"

# Archive old tickets (>90 days)
docker exec fte-postgres psql -U postgres -d fte_db -c \
  "UPDATE tickets SET status = 'archived' 
   WHERE created_at < NOW() - INTERVAL '90 days' 
   AND status = 'closed';"
```

**Performance Review**
```bash
# Generate weekly report
python scripts/generate_weekly_report.py

# Review metrics:
# - Total tickets by channel
# - Escalation rate
# - Average response time
# - Customer satisfaction
```

### Monthly Tasks

**System Updates (30 minutes)**
```bash
# Update Python dependencies
pip install --upgrade -r requirements.txt

# Update Node.js dependencies
cd src/web-form
npm update

# Update Docker images
docker pull postgres:15
```

**Backup Verification**
```bash
# Test database backup restore
docker exec fte-postgres pg_dump -U postgres fte_db > backup_test.sql

# Verify backup file
ls -lh backup_test.sql
```

---

## Emergency Procedures

### Complete System Failure

**Step 1: Assess Damage**
- Check all components (Docker, API, Web, Database)
- Identify root cause
- Estimate recovery time

**Step 2: Communicate**
- Notify stakeholders
- Post status update
- Set expectations

**Step 3: Recover**
```bash
# Stop everything
docker stop fte-postgres
# Kill API and web form processes

# Restart from scratch
docker start fte-postgres
# Wait 30 seconds

# Start API
cd D:\Coding\Q4\hackathons\Hackathon-5\src
python -m uvicorn api.main:app --port 8001 &

# Start web form
cd src/web-form
npm run dev &

# Verify health
curl http://localhost:8001/health
```

**Step 4: Post-Mortem**
- Document what happened
- Identify root cause
- Create prevention plan
- Update runbook

---

## Backup and Recovery

### Database Backup

**Manual Backup:**
```bash
# Create backup
docker exec fte-postgres pg_dump -U postgres fte_db > backup_$(date +%Y%m%d).sql

# Verify backup
ls -lh backup_*.sql
```

**Restore from Backup:**
```bash
# Stop API server first
# Then restore
cat backup_20260422.sql | docker exec -i fte-postgres psql -U postgres -d fte_db
```

**Automated Backup (Cron):**
```bash
# Add to crontab
0 2 * * * docker exec fte-postgres pg_dump -U postgres fte_db > /backups/fte_db_$(date +\%Y\%m\%d).sql
```

---

## Performance Tuning

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tickets_customer_id ON tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- Update statistics
ANALYZE tickets;
ANALYZE customers;
ANALYZE messages;
```

### API Optimization

```python
# Enable response caching
# Add to src/api/main.py

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())
```

---

## Monitoring Checklist

**Daily:**
- [ ] Check system health
- [ ] Review error logs
- [ ] Check ticket volume
- [ ] Verify backups

**Weekly:**
- [ ] Review performance metrics
- [ ] Check escalation rate
- [ ] Database maintenance
- [ ] Update dependencies

**Monthly:**
- [ ] System updates
- [ ] Backup verification
- [ ] Cost review
- [ ] Capacity planning

---

## Version History

- **v1.0** - Initial runbook
  - Startup/shutdown procedures
  - Common incidents
  - Escalation procedures
  - Maintenance tasks
