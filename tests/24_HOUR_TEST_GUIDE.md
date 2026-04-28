# 24-Hour Stability Test - Customer Success FTE

**Purpose:** Verify system can run continuously for 24 hours under realistic load  
**Target:** https://fte-backend-3ohm.onrender.com  
**Duration:** 24 hours  
**Users:** 50 concurrent users  

---

## 🎯 Test Configuration

### Load Profile
- **Concurrent Users:** 50
- **Spawn Rate:** 5 users/second
- **Duration:** 24 hours (86,400 seconds)
- **Traffic Pattern:** Realistic (60% web form, 30% portal, 10% health checks)

### Expected Metrics
- **Total Requests:** ~150,000-200,000 requests
- **Requests/Second:** ~2-3 req/s average
- **Success Rate Target:** > 95%
- **Response Time Target:** < 3 seconds (P95)
- **Uptime Target:** > 99.9%

---

## 🚀 How to Run

### Option 1: Run in Background (Recommended)
```bash
cd tests
nohup locust -f load_test.py \
       --host=https://fte-backend-3ohm.onrender.com \
       --users 50 --spawn-rate 5 --run-time 24h \
       --csv=24h_test_results --headless \
       > 24h_test.log 2>&1 &

echo $! > 24h_test.pid
echo "24-hour test started. PID saved to 24h_test.pid"
```

### Option 2: Run in Terminal (Foreground)
```bash
cd tests
locust -f load_test.py \
       --host=https://fte-backend-3ohm.onrender.com \
       --users 50 --spawn-rate 5 --run-time 24h \
       --csv=24h_test_results --headless
```

### Option 3: Run with Web UI (Monitor Progress)
```bash
cd tests
locust -f load_test.py \
       --host=https://fte-backend-3ohm.onrender.com \
       --users 50 --spawn-rate 5 --run-time 24h \
       --csv=24h_test_results

# Then open: http://localhost:8089
```

---

## 📊 Monitoring During Test

### Check Test Status
```bash
# Check if test is running
ps aux | grep locust

# Check PID
cat 24h_test.pid

# View live logs
tail -f 24h_test.log

# Check backend health
curl https://fte-backend-3ohm.onrender.com/health
```

### Monitor Backend (Render Dashboard)
1. Go to: https://dashboard.render.com
2. Select: fte-backend-3ohm
3. Monitor:
   - CPU usage
   - Memory usage
   - Request rate
   - Error rate
   - Logs

### Stop Test Early (If Needed)
```bash
# Get PID
cat 24h_test.pid

# Stop test
kill $(cat 24h_test.pid)

# Or force stop
pkill -f "locust.*load_test.py"
```

---

## 📈 Success Criteria

### From Requirements:
1. **Uptime:** > 99.9% (max 86 seconds downtime)
2. **P95 Latency:** < 3 seconds
3. **Success Rate:** > 95%
4. **No Message Loss:** All submissions processed
5. **Stability:** No crashes or memory leaks

### Additional Metrics:
- **Average Response Time:** < 2 seconds
- **Error Rate:** < 5%
- **Backend Restarts:** 0 (should not crash)
- **Database Connections:** Stable (no leaks)

---

## 📋 Test Scenarios

### Traffic Distribution (Realistic)
- **60% Web Form Submissions** (~120,000 requests)
  - New support tickets
  - Various categories and priorities
  
- **30% Customer Portal** (~60,000 requests)
  - Customer lookups
  - Ticket status checks
  - Follow-up submissions
  
- **10% Health Checks** (~20,000 requests)
  - System monitoring
  - Uptime verification

### Peak Hours Simulation
The test will maintain constant load, but in production you'd see:
- **Peak:** 9 AM - 5 PM (higher traffic)
- **Off-Peak:** 6 PM - 8 AM (lower traffic)
- **Weekend:** Reduced traffic

---

## 🔍 What to Watch For

### Red Flags 🚨
- Response time increasing over time (memory leak)
- Error rate increasing (system degradation)
- Backend crashes or restarts
- Database connection errors
- Timeout errors increasing

### Good Signs ✅
- Stable response times throughout
- Consistent success rate
- No backend restarts
- CPU/Memory usage stable
- Error rate < 5%

---

## 📊 Results Analysis

### After 24 Hours, Check:

1. **CSV Results Files:**
   - `24h_test_results_stats.csv` - Summary statistics
   - `24h_test_results_failures.csv` - All failures
   - `24h_test_results_stats_history.csv` - Time-series data

2. **Key Metrics to Extract:**
   ```bash
   # Total requests
   tail -1 24h_test_results_stats.csv | cut -d',' -f3
   
   # Success rate
   # Calculate: (Total - Failures) / Total * 100
   
   # Average response time
   tail -1 24h_test_results_stats.csv | cut -d',' -f6
   
   # 95th percentile
   tail -1 24h_test_results_stats.csv | cut -d',' -f16
   ```

3. **Backend Metrics (Render):**
   - Total uptime
   - Number of restarts
   - Peak CPU usage
   - Peak memory usage
   - Total requests served

---

## 📝 Results Template

After 24 hours, document results:

```
24-Hour Stability Test Results
==============================
Start Time: [timestamp]
End Time: [timestamp]
Duration: 24 hours

LOAD PROFILE
- Concurrent Users: 50
- Total Requests: [number]
- Requests/Second: [avg]

PERFORMANCE
- Average Response Time: [time]
- Median Response Time: [time]
- 95th Percentile: [time]
- Max Response Time: [time]

RELIABILITY
- Success Rate: [percentage]
- Failed Requests: [number]
- Error Rate: [percentage]
- Uptime: [percentage]

BACKEND HEALTH
- Restarts: [number]
- Peak CPU: [percentage]
- Peak Memory: [MB]
- Database Errors: [number]

SUCCESS CRITERIA
✅/❌ Uptime > 99.9%: [actual]
✅/❌ P95 < 3s: [actual]
✅/❌ Success Rate > 95%: [actual]
✅/❌ No Crashes: [yes/no]

OVERALL STATUS: [✅ PASSED / ⚠️ PARTIAL / ❌ FAILED]
```

---

## 🎯 Expected Outcomes

### Best Case Scenario ✅
- 99.9%+ uptime
- <2s average response time
- >98% success rate
- 0 backend crashes
- Stable performance throughout

### Acceptable Scenario ⚠️
- 99%+ uptime
- <3s P95 response time
- >95% success rate
- 1-2 backend restarts (Render free tier)
- Minor performance degradation

### Failure Scenario ❌
- <99% uptime
- >3s P95 response time
- <95% success rate
- Multiple crashes
- Significant performance degradation

---

## 🔧 Troubleshooting During Test

### Issue: High Error Rate

**Check:**
```bash
# View recent errors
tail -100 24h_test.log | grep ERROR

# Check backend logs
# Go to Render dashboard > Logs
```

**Action:**
- If errors > 10%: Consider stopping test
- If backend crashed: Restart and resume
- If database errors: Check connection pool

### Issue: Slow Response Times

**Check:**
```bash
# Monitor response times
tail -f 24h_test.log | grep "Aggregated"
```

**Action:**
- If increasing over time: Memory leak suspected
- If consistently high: Backend under-resourced
- If spiky: Database query issues

### Issue: Backend Crash

**Action:**
1. Note the time of crash
2. Check Render logs for error
3. Restart backend
4. Resume test or start new test
5. Document in results

---

## 📅 Timeline

| Time | Checkpoint | Action |
|------|------------|--------|
| 0:00 | Start | Launch 24-hour test |
| 1:00 | 1 hour | Check initial metrics |
| 6:00 | 6 hours | Verify stability |
| 12:00 | 12 hours | Mid-point check |
| 18:00 | 18 hours | Monitor for degradation |
| 24:00 | Complete | Analyze results |

---

## 🚀 Quick Start Commands

### Start Test Now
```bash
cd D:/Coding/Q4/hackathons/Hackathon-5/tests

# Background mode (recommended)
nohup locust -f load_test.py \
       --host=https://fte-backend-3ohm.onrender.com \
       --users 50 --spawn-rate 5 --run-time 24h \
       --csv=24h_test_results --headless \
       > 24h_test.log 2>&1 &

echo $! > 24h_test.pid
echo "Test started! Check status with: tail -f 24h_test.log"
```

### Monitor Test
```bash
# Live logs
tail -f 24h_test.log

# Check if running
ps aux | grep locust

# Backend health
curl https://fte-backend-3ohm.onrender.com/health
```

---

**Test Duration:** 24 hours  
**Start Time:** [When you run the command]  
**End Time:** [24 hours later]  
**Status:** Ready to start  
**Estimated Cost:** $0 (using free tier)
