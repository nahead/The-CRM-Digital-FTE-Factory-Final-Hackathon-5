# 🚀 QUICK START GUIDE

## Get Running in 5 Minutes

### Prerequisites Check
```bash
# Check these are installed:
python --version    # Should be 3.11+
node --version      # Should be 18+
docker --version    # Should work
```

---

## 🎯 FASTEST PATH TO RUNNING

### 1. Start Docker Desktop (Manual)
**Open Docker Desktop app and wait for it to start**

### 2. Get Gemini API Key (2 minutes)
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Open `.env` file
5. Replace `your_gemini_api_key_here` with your actual key

### 3. Start Infrastructure (1 command)
```bash
docker-compose up -d
```

### 4. Install Python Essentials (1 command)
```bash
# Windows:
venv\Scripts\activate
pip install fastapi uvicorn google-generativeai python-dotenv httpx

# Linux/Mac:
source venv/bin/activate
pip install fastapi uvicorn google-generativeai python-dotenv httpx
```

### 5. Start API (1 command)
```bash
cd src
python -m uvicorn api.main:app --reload --port 8000
```

### 6. Test It (1 command)
```bash
# In another terminal:
curl http://localhost:8000/health
```

**✅ If you see `{"status":"healthy"}` - YOU'RE DONE!**

---

## 📝 Test Form Submission

```bash
curl -X POST http://localhost:8000/support/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Test Issue",
    "category": "technical",
    "message": "This is a test message to verify the system works"
  }'
```

Expected response:
```json
{
  "ticket_id": "some-uuid",
  "message": "Thank you for contacting us!...",
  "estimated_response_time": "Usually within 5 minutes"
}
```

---

## 🌐 Optional: Start Web Form

```bash
cd src/web-form
npm install
npm run dev
```

Visit: http://localhost:3000

---

## 🧪 Run Test Suite

```bash
python test_api.py
```

---

## 🐛 Common Issues

### Issue: Docker not starting
**Fix:** Start Docker Desktop manually

### Issue: Port 8000 already in use
**Fix:** 
```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Issue: Gemini API errors
**Fix:** Check `.env` has correct `GEMINI_API_KEY`

### Issue: Database connection failed
**Fix:** 
```bash
docker-compose ps  # Check containers are running
docker-compose restart postgres
```

---

## 📊 Verify Everything Works

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Root endpoint
curl http://localhost:8000/

# 3. Metrics
curl http://localhost:8000/metrics/channels

# 4. Submit test ticket
curl -X POST http://localhost:8000/support/submit \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","subject":"Test","category":"technical","message":"Test message for verification"}'
```

---

## 🎯 What You've Built

- ✅ Multi-channel AI support (Email, WhatsApp, Web Form)
- ✅ Google Gemini AI agent (FREE)
- ✅ PostgreSQL CRM database
- ✅ Kafka event streaming
- ✅ FastAPI REST API
- ✅ React/Next.js web form
- ✅ Kubernetes-ready deployment
- ✅ Auto-scaling (3-20 pods)

**Cost:** $0-10/month (only Gemini API usage)

---

## 📚 Full Documentation

- `README.md` - Complete project documentation
- `SETUP.md` - Detailed setup instructions
- `PROJECT_STATUS.md` - Current status
- `FINAL_SUMMARY.md` - Complete summary
- `PROJECT_COMPLETE.txt` - Checklist

---

## 🚀 Deploy to Kubernetes

```bash
# 1. Build image
docker build -t customer-success-fte:latest .

# 2. Push to registry
docker tag customer-success-fte:latest your-registry/customer-success-fte:latest
docker push your-registry/customer-success-fte:latest

# 3. Update k8s/deployment.yaml with your image

# 4. Deploy
kubectl apply -f k8s/deployment.yaml

# 5. Check status
kubectl get pods -n customer-success-fte
kubectl get svc -n customer-success-fte
```

---

## 🎓 Architecture Overview

```
┌─────────────────────────────────────────┐
│         MULTI-CHANNEL INTAKE            │
│  Gmail  │  WhatsApp  │  Web Form        │
└────────────────┬────────────────────────┘
                 │
                 ▼
         ┌──────────────┐
         │    Kafka     │
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐
         │ Gemini Agent │
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐
         │  PostgreSQL  │
         │    (CRM)     │
         └──────────────┘
```

---

## 💡 Pro Tips

1. **Use WSL2 on Windows** for easier Python dependency installation
2. **Keep Docker Desktop running** while developing
3. **Check logs** if something fails:
   ```bash
   docker-compose logs -f postgres
   docker-compose logs -f kafka
   ```
4. **Use the test script** to verify everything:
   ```bash
   python test_api.py
   ```

---

## 🎉 You're Ready!

Your Customer Success Digital FTE is now running 24/7!

**Next Steps:**
1. Add more sample data to knowledge base
2. Configure Gmail API (optional)
3. Configure Twilio WhatsApp (optional)
4. Deploy to Kubernetes
5. Run 24-hour test
6. Submit for hackathon evaluation

**Questions?** Check the full documentation in README.md

---

**Built with:** Python • FastAPI • React • PostgreSQL • Kafka • Docker • Kubernetes • Google Gemini AI
