# Setup Instructions

## Prerequisites

### 1. Docker Desktop (REQUIRED)
**Status:** ⚠️ NOT RUNNING

Docker Desktop must be running before starting the infrastructure.

**To Start:**
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon in system tray)
3. Then run: `docker-compose up -d`

### 2. Python Dependencies (ISSUE DETECTED)

Some packages require C++ compilation on Windows. 

**Solutions:**

**Option A: Install Visual Studio Build Tools (Recommended)**
1. Download: https://visualstudio.microsoft.com/downloads/
2. Install "Desktop development with C++" workload
3. Restart terminal
4. Run: `venv\Scripts\pip install -r requirements.txt`

**Option B: Use WSL2 (Easier)**
1. Install WSL2: `wsl --install`
2. Install Ubuntu from Microsoft Store
3. Run all commands in WSL2 terminal

**Option C: Skip problematic packages for now**
Install only essential packages:
```bash
venv\Scripts\pip install fastapi uvicorn google-generativeai python-dotenv twilio google-api-python-client httpx pytest
```

## Current Setup Status

✅ Project structure created
✅ Context files created (company-profile, product-docs, sample-tickets, escalation-rules, brand-voice)
✅ Database schema created
✅ Docker compose file created
✅ .env file created
✅ .gitignore created

⚠️ Docker Desktop not running
⚠️ Python dependencies need C++ build tools
⏳ Web form setup pending
⏳ Agent code pending

## Next Steps

1. **Start Docker Desktop** (manual step required)
2. **Install Python dependencies** (choose option A, B, or C above)
3. Continue with web form setup
4. Build agent implementation

## API Keys Needed

Add these to `.env` file:

1. **Gemini API Key** (FREE)
   - Get from: https://makersuite.google.com/app/apikey
   - Add to .env: `GEMINI_API_KEY=your_key_here`

2. **Twilio Account** (FREE Sandbox)
   - Sign up: https://www.twilio.com/try-twilio
   - Get: Account SID, Auth Token, WhatsApp Number
   - Add to .env

3. **Gmail API Credentials** (FREE)
   - Create project: https://console.cloud.google.com/
   - Enable Gmail API
   - Download credentials.json to `credentials/` folder
