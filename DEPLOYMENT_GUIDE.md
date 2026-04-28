# Deployment Guide - Customer Success FTE

## 🚀 Complete Deployment Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 14+
- Git
- Render.com account (or alternative cloud provider)

---

## 📦 Backend Deployment (Render.com)

### Step 1: Prepare Environment Variables
Create a `.env` file with the following variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Google Gemini AI
GOOGLE_API_KEY=your_gemini_api_key

# Gmail API (for email channel)
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token
SUPPORT_EMAIL=support@yourdomain.com

# Twilio (for WhatsApp channel)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Environment
ENVIRONMENT=production
```

### Step 2: Create Render Web Service

1. **Connect GitHub Repository**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   ```yaml
   Name: fte-backend
   Environment: Python 3
   Region: Oregon (US West)
   Branch: main
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Add Environment Variables**
   - Go to "Environment" tab
   - Add all variables from `.env` file
   - Click "Save Changes"

4. **Deploy**
   - Click "Manual Deploy" → "Deploy latest commit"
   - Wait for deployment to complete (5-10 minutes)
   - Note your backend URL: `https://your-service.onrender.com`

### Step 3: Setup PostgreSQL Database

1. **Create Database on Render**
   - Click "New +" → "PostgreSQL"
   - Name: `fte-database`
   - Region: Same as web service
   - Plan: Free or Starter

2. **Get Connection String**
   - Copy "Internal Database URL"
   - Add to web service environment variables as `DATABASE_URL`

3. **Initialize Database Schema**
   ```bash
   # Run locally or via Render shell
   python src/database/init_db.py
   ```

---

## 🌐 Frontend Deployment (Render.com)

### Step 1: Configure Frontend

1. **Update API Endpoint**
   - Edit `src/web-form/src/App.jsx`
   - Update `apiEndpoint` to your backend URL:
   ```javascript
   const apiEndpoint = 'https://your-backend.onrender.com';
   ```

2. **Build Frontend**
   ```bash
   cd src/web-form
   npm install
   npm run build
   ```

### Step 2: Deploy to Render

1. **Create Static Site**
   - Click "New +" → "Static Site"
   - Connect same GitHub repository
   - Configure:
   ```yaml
   Name: fte-frontend
   Branch: main
   Build Command: cd src/web-form && npm install && npm run build
   Publish Directory: src/web-form/dist
   ```

2. **Deploy**
   - Click "Create Static Site"
   - Wait for deployment
   - Note your frontend URL: `https://your-frontend.onrender.com`

---

## 🔧 Alternative Deployment Options

### Option 1: Vercel (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd src/web-form
vercel --prod
```

### Option 2: Heroku (Backend)

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create fte-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set GOOGLE_API_KEY=your_key
heroku config:set GMAIL_CLIENT_ID=your_id
# ... add all other variables

# Deploy
git push heroku main
```

### Option 3: AWS (Full Stack)

**Backend (Elastic Beanstalk):**
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.9 fte-backend

# Create environment
eb create fte-production

# Deploy
eb deploy
```

**Frontend (S3 + CloudFront):**
```bash
# Build
cd src/web-form
npm run build

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

### Option 4: Docker Deployment

**Backend Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY credentials/ ./credentials/

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:16-alpine as build

WORKDIR /app

COPY src/web-form/package*.json ./
RUN npm install

COPY src/web-form/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on:
      - db

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=fte_db
      - POSTGRES_USER=fte_user
      - POSTGRES_PASSWORD=fte_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 🔐 Security Checklist

- [ ] Change all default passwords
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure CORS for production domains only
- [ ] Set up rate limiting (already configured)
- [ ] Enable database backups
- [ ] Set up monitoring and alerts
- [ ] Configure firewall rules
- [ ] Enable API key rotation
- [ ] Set up logging and audit trails
- [ ] Configure CSP headers (already configured)

---

## 📊 Monitoring Setup

### Health Check Monitoring
```bash
# Add to cron or monitoring service
*/5 * * * * curl https://your-backend.onrender.com/health
```

### Uptime Monitoring Services
- UptimeRobot (Free)
- Pingdom
- StatusCake
- Better Uptime

### Application Monitoring
- Sentry (Error tracking)
- LogRocket (Session replay)
- DataDog (Full stack monitoring)

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: pytest tests/ -v

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node
        uses: actions/setup-node@v2
        with:
          node-version: 16
      - name: Build
        run: |
          cd src/web-form
          npm install
          npm run build
      - name: Deploy
        run: |
          # Add your frontend deployment command
```

---

## 🧪 Testing Before Production

### 1. Run All Tests
```bash
# Backend tests
pytest tests/ -v

# Load tests
python tests/load_test.py

# E2E tests
pytest tests/test_e2e_multichannel.py -v
```

### 2. Manual Testing Checklist
- [ ] Submit support request via web form
- [ ] Send email to support address
- [ ] Send WhatsApp message
- [ ] Check admin dashboard loads
- [ ] Verify customer portal login
- [ ] Test voice support
- [ ] Check analytics dashboard
- [ ] Verify all navigation links work

### 3. Performance Testing
```bash
# Use Apache Bench
ab -n 1000 -c 10 https://your-backend.onrender.com/health

# Use Locust
locust -f tests/load_test.py --host=https://your-backend.onrender.com
```

---

## 📝 Post-Deployment

### 1. Verify Deployment
```bash
# Check backend health
curl https://your-backend.onrender.com/health

# Check frontend loads
curl https://your-frontend.onrender.com

# Check API documentation
open https://your-backend.onrender.com/docs
```

### 2. Monitor Logs
```bash
# Render logs
render logs -s your-service-name -f

# Or via dashboard
# Go to service → Logs tab
```

### 3. Set Up Alerts
- Configure email alerts for downtime
- Set up Slack notifications for errors
- Monitor response times

---

## 🆘 Troubleshooting

### Backend Not Starting
```bash
# Check logs
render logs -s fte-backend

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port binding issues
```

### Frontend Not Loading
```bash
# Check build logs
# Verify API endpoint is correct
# Check CORS configuration
# Verify static files are served
```

### Database Connection Issues
```bash
# Verify DATABASE_URL is correct
# Check database is running
# Verify network connectivity
# Check connection pool settings
```

---

## 💰 Cost Estimation

### Render.com (Recommended)
- **Backend**: $7/month (Starter plan)
- **Database**: $7/month (Starter plan)
- **Frontend**: Free (Static site)
- **Total**: ~$14/month

### AWS
- **EC2 (t3.small)**: ~$15/month
- **RDS (db.t3.micro)**: ~$15/month
- **S3 + CloudFront**: ~$1/month
- **Total**: ~$31/month

### Heroku
- **Dyno (Hobby)**: $7/month
- **Postgres (Hobby)**: $9/month
- **Total**: ~$16/month

---

## 📞 Support

For deployment issues:
- Check documentation: `/docs`
- Review logs: Service dashboard
- GitHub Issues: [Repository URL]
- Email: support@yourdomain.com

---

**Last Updated**: 2026-04-28
**Version**: 1.0.0
