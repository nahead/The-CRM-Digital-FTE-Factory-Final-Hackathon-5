# Troubleshooting Guide - Customer Success FTE

## 🔧 Common Issues and Solutions

---

## 🚨 Backend Issues

### Issue 1: Backend Not Starting

**Symptoms:**
- Service fails to start
- Error: "Application startup failed"
- Port binding errors

**Solutions:**

```bash
# Check if port is already in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process using port
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Check environment variables
python -c "import os; print(os.getenv('DATABASE_URL'))"

# Verify Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue 2: Database Connection Failed

**Symptoms:**
- Error: "could not connect to server"
- Error: "password authentication failed"
- Timeout errors

**Solutions:**

```bash
# Test database connection
psql $DATABASE_URL

# Check connection string format
# Correct: postgresql://user:pass@host:5432/dbname
# Wrong: postgres://... (should be postgresql://)

# Verify database exists
psql -U postgres -c "\l"

# Check database credentials
echo $DATABASE_URL

# Test with Python
python -c "
import psycopg2
conn = psycopg2.connect('$DATABASE_URL')
print('Connection successful!')
conn.close()
"

# Initialize database schema
python src/database/init_db.py
```

### Issue 3: Gmail API Not Working

**Symptoms:**
- Error: "invalid_grant"
- Error: "Token has been expired or revoked"
- Emails not being received

**Solutions:**

```bash
# Regenerate Gmail token
python src/channels/email_handler.py

# Check credentials file exists
ls credentials/gmail_credentials.json

# Verify environment variables
echo $GMAIL_CLIENT_ID
echo $GMAIL_CLIENT_SECRET
echo $GMAIL_REFRESH_TOKEN

# Test Gmail API
python -c "
from src.channels.email_handler import EmailHandler
handler = EmailHandler()
messages = handler.get_unread_messages(max_results=1)
print(f'Found {len(messages)} messages')
"

# Common fixes:
# 1. Regenerate OAuth token
# 2. Enable Gmail API in Google Cloud Console
# 3. Check OAuth consent screen settings
# 4. Verify redirect URI matches
```

### Issue 4: Gemini AI Not Responding

**Symptoms:**
- Error: "API key not valid"
- Error: "quota exceeded"
- Slow or no responses

**Solutions:**

```bash
# Verify API key
echo $GOOGLE_API_KEY

# Test API key
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=$GOOGLE_API_KEY"

# Check quota
# Go to: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas

# Common fixes:
# 1. Generate new API key
# 2. Enable Generative Language API
# 3. Check billing is enabled
# 4. Wait for quota reset (daily limit)
```

### Issue 5: WhatsApp Not Working

**Symptoms:**
- Messages not received
- Error: "Invalid Twilio credentials"
- Webhook validation failed

**Solutions:**

```bash
# Verify Twilio credentials
echo $TWILIO_ACCOUNT_SID
echo $TWILIO_AUTH_TOKEN
echo $TWILIO_WHATSAPP_NUMBER

# Test Twilio API
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID.json" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"

# Check webhook URL
# Should be: https://your-backend.onrender.com/webhooks/whatsapp

# Verify webhook in Twilio Console
# Go to: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox

# Test webhook locally with ngrok
ngrok http 8000
# Update Twilio webhook to ngrok URL

# Common fixes:
# 1. Verify webhook URL is publicly accessible
# 2. Check HTTPS is enabled
# 3. Verify Twilio signature validation
# 4. Join WhatsApp sandbox if testing
```

---

## 🌐 Frontend Issues

### Issue 6: Frontend Not Loading

**Symptoms:**
- Blank white screen
- Error: "Failed to fetch"
- CORS errors

**Solutions:**

```bash
# Check browser console for errors
# Press F12 → Console tab

# Verify API endpoint
# Check src/web-form/src/App.jsx
# apiEndpoint should match backend URL

# Test API connectivity
curl https://your-backend.onrender.com/health

# Clear browser cache
# Chrome: Ctrl+Shift+Delete
# Firefox: Ctrl+Shift+Delete

# Rebuild frontend
cd src/web-form
rm -rf node_modules dist
npm install
npm run build

# Check for JavaScript errors
npm run build 2>&1 | grep -i error
```

### Issue 7: CORS Errors

**Symptoms:**
- Error: "Access-Control-Allow-Origin"
- Error: "CORS policy blocked"
- API calls failing from browser

**Solutions:**

```python
# Update CORS settings in src/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.onrender.com",
        "http://localhost:3000"  # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# For development only (not production):
allow_origins=["*"]

# Verify CORS headers
curl -H "Origin: https://your-frontend.onrender.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS \
  https://your-backend.onrender.com/support/submit -v
```

### Issue 8: Voice Support Not Working

**Symptoms:**
- Microphone not detected
- Error: "Speech recognition not supported"
- No audio output

**Solutions:**

```javascript
// Check browser support
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  console.log('Speech recognition supported');
} else {
  console.log('Speech recognition NOT supported');
}

// Supported browsers:
// ✅ Chrome/Edge (desktop & mobile)
// ✅ Safari (desktop & mobile)
// ❌ Firefox (not supported)

// Check microphone permissions
navigator.permissions.query({ name: 'microphone' })
  .then(result => console.log('Microphone:', result.state));

// Common fixes:
// 1. Use Chrome or Safari
// 2. Allow microphone permissions
// 3. Use HTTPS (required for mic access)
// 4. Check system microphone settings
```

---

## 📊 Performance Issues

### Issue 9: Slow Response Times

**Symptoms:**
- API calls taking >5 seconds
- Timeout errors
- High latency

**Solutions:**

```bash
# Check backend health
curl -w "@-" -o /dev/null -s https://your-backend.onrender.com/health <<'EOF'
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
EOF

# Monitor database queries
# Add logging to slow queries

# Check database connection pool
# Increase pool size if needed

# Enable caching
# Add Redis for frequently accessed data

# Optimize database indexes
CREATE INDEX idx_tickets_customer ON tickets(customer_id);
CREATE INDEX idx_messages_ticket ON messages(ticket_id);

# Use database query profiling
EXPLAIN ANALYZE SELECT * FROM tickets WHERE customer_id = 'xxx';
```

### Issue 10: High Memory Usage

**Symptoms:**
- Out of memory errors
- Service crashes
- Slow performance

**Solutions:**

```bash
# Check memory usage
free -h  # Linux
top  # macOS/Linux
taskmgr  # Windows

# Monitor Python memory
pip install memory_profiler
python -m memory_profiler src/api/main.py

# Optimize database connections
# Close connections after use
# Use connection pooling

# Limit result set sizes
# Add pagination to queries
# Use LIMIT in SQL queries

# Clear caches periodically
# Implement cache expiration
```

---

## 🔐 Security Issues

### Issue 11: Rate Limit Exceeded

**Symptoms:**
- Error: "429 Too Many Requests"
- "Rate limit exceeded" message

**Solutions:**

```bash
# Check rate limit headers
curl -I https://your-backend.onrender.com/health

# Headers:
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 45
# X-RateLimit-Reset: 1234567890

# Wait for rate limit reset
# Or increase rate limit in middleware

# Adjust rate limit
# Edit src/api/middleware.py
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)

# Implement API key-based rate limiting
# Different limits for authenticated users
```

### Issue 12: Authentication Errors

**Symptoms:**
- Customer login fails
- "Customer not found" errors
- Session expired

**Solutions:**

```bash
# Verify customer exists in database
psql $DATABASE_URL -c "SELECT * FROM customers WHERE email = 'test@example.com';"

# Check customer login endpoint
curl -X POST https://your-backend.onrender.com/customer/login \
  -H "Content-Type: application/json" \
  -d '{"identifier_type":"email","identifier_value":"test@example.com"}'

# Clear browser localStorage
localStorage.clear();

# Verify email/phone format
# Email: valid email format
# Phone: include country code (+1234567890)
```

---

## 🗄️ Database Issues

### Issue 13: Database Migration Failed

**Symptoms:**
- Schema mismatch errors
- Missing tables
- Column not found errors

**Solutions:**

```bash
# Check current schema
psql $DATABASE_URL -c "\dt"

# Backup database first
pg_dump $DATABASE_URL > backup.sql

# Drop and recreate (CAUTION: loses data)
psql $DATABASE_URL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Reinitialize schema
python src/database/init_db.py

# Restore from backup if needed
psql $DATABASE_URL < backup.sql

# Verify schema
python src/database/verify_schema.py
```

### Issue 14: Database Locks

**Symptoms:**
- Queries hanging
- Timeout errors
- Deadlock detected

**Solutions:**

```sql
-- Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Check active queries
SELECT pid, query, state, wait_event
FROM pg_stat_activity
WHERE state != 'idle';

-- Kill blocking query (CAUTION)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active' AND pid != pg_backend_pid();

-- Prevent locks
-- Use shorter transactions
-- Add proper indexes
-- Use SELECT FOR UPDATE carefully
```

---

## 📱 Mobile Issues

### Issue 15: Mobile Layout Broken

**Symptoms:**
- Content overflowing
- Buttons too small
- Text unreadable

**Solutions:**

```css
/* Ensure viewport meta tag */
<meta name="viewport" content="width=device-width, initial-scale=1">

/* Use responsive units */
.container {
  width: 100%;
  max-width: 1200px;
  padding: 1rem;
}

/* Minimum touch target size */
.button {
  min-width: 44px;
  min-height: 44px;
}

/* Test on multiple devices */
/* Chrome DevTools → Toggle device toolbar (Ctrl+Shift+M) */
```

---

## 🔍 Debugging Tools

### Backend Debugging

```bash
# Enable debug mode
export DEBUG=True
uvicorn src.api.main:app --reload --log-level debug

# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")

# Use pdb debugger
import pdb; pdb.set_trace()

# Check logs
tail -f /var/log/app.log
```

### Frontend Debugging

```javascript
// Browser console
console.log('Debug:', variable);
console.table(arrayData);
console.error('Error:', error);

// React DevTools
// Install: https://react.dev/learn/react-developer-tools

// Network tab
// Check API calls, status codes, response times

// Performance profiling
// Chrome DevTools → Performance tab
```

---

## 📞 Getting Help

### Before Asking for Help

1. **Check logs**
   - Backend: Service logs
   - Frontend: Browser console
   - Database: PostgreSQL logs

2. **Reproduce the issue**
   - Document exact steps
   - Note error messages
   - Check if consistent

3. **Gather information**
   - Environment (dev/prod)
   - Browser/OS version
   - Timestamp of issue
   - Affected users

### Where to Get Help

- **Documentation**: `/docs` endpoint
- **GitHub Issues**: Report bugs
- **Stack Overflow**: Tag with `customer-success-fte`
- **Email Support**: support@yourdomain.com

### Issue Report Template

```markdown
## Issue Description
Brief description of the problem

## Steps to Reproduce
1. Go to...
2. Click on...
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows 10
- Browser: Chrome 120
- Backend URL: https://...
- Frontend URL: https://...

## Error Messages
```
Paste error messages here
```

## Screenshots
Attach screenshots if applicable
```

---

## 🎯 Quick Fixes

### Reset Everything (Development)

```bash
# Backend
cd src/api
rm -rf __pycache__
pip install -r requirements.txt --force-reinstall

# Frontend
cd src/web-form
rm -rf node_modules dist .next
npm install
npm run build

# Database
python src/database/init_db.py

# Restart services
# Backend: uvicorn src.api.main:app --reload
# Frontend: npm run dev
```

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

echo "Checking backend..."
curl -f https://your-backend.onrender.com/health || echo "❌ Backend down"

echo "Checking frontend..."
curl -f https://your-frontend.onrender.com || echo "❌ Frontend down"

echo "Checking database..."
psql $DATABASE_URL -c "SELECT 1;" || echo "❌ Database down"

echo "✅ All systems operational"
```

---

**Last Updated**: 2026-04-28
**Version**: 1.0.0
