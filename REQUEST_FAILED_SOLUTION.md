# Request Failed Error - Solution Guide

## The Problem

You were seeing a **"Request failed"** error when trying to log in or interact with the application. 

This happens because:
- The **frontend** (Next.js on port 3000) tries to communicate with the **backend** (FastAPI on port 8000)
- But the **backend server is not running**
- So all API requests fail with `ECONNREFUSED`

## The Fix

You now have **3 ways** to start both servers:

### Option 1: One-Command Startup (Recommended)

**macOS/Linux:**
```bash
./start-dev.sh
```

**Windows:**
```batch
start-dev.bat
```

This automatically:
- Installs all dependencies
- Starts the backend on port 8000
- Starts the frontend on port 3000
- Verifies both servers are running

### Option 2: Manual Startup (Two Terminals)

**Terminal 1 - Backend:**
```bash
cd cloudops-ai-copilot/backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd cloudops-ai-copilot/frontend
npm install
npm run dev
```

### Option 3: Using npm scripts

**Terminal 1 - Backend:**
```bash
cd cloudops-ai-copilot/backend
pip install -r requirements.txt
npm run dev:backend
```

**Terminal 2 - Frontend:**
```bash
cd cloudops-ai-copilot/frontend
npm run dev
```

## What Gets Fixed

Once both servers are running:

✓ Frontend can communicate with backend
✓ API requests succeed
✓ Login works
✓ Chat sessions load
✓ Code review features work
✓ Architecture analysis works

## Verify Everything Works

### Check Backend is Running:
```bash
curl http://localhost:8000/api/v1/health
# Expected response: {"status":"healthy"}
```

### Check Frontend is Running:
```bash
curl http://localhost:3000
# Expected response: HTML page
```

### Access the Application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Troubleshooting

### Port 8000 is already in use:
```bash
# Find and kill the process
lsof -ti :8000 | xargs kill -9

# Or use a different port:
cd cloudops-ai-copilot/backend
uvicorn app.main:app --port 8001
```

### Port 3000 is already in use:
```bash
# Find and kill the process
lsof -ti :3000 | xargs kill -9

# Or use a different port:
cd cloudops-ai-copilot/frontend
npm run dev -- -p 3001
```

### Dependencies not installed:

**Backend:**
```bash
cd cloudops-ai-copilot/backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd cloudops-ai-copilot/frontend
npm install
```

### Still getting "Request failed"?

1. Verify backend is running: `curl http://localhost:8000/api/v1/health`
2. Check frontend is on port 3000: `curl http://localhost:3000`
3. Check browser console for specific errors (F12)
4. Check backend logs for server errors

## New Features Added

### Startup Scripts

**start-dev.sh** (macOS/Linux)
- Auto-detects missing dependencies
- Installs requirements
- Starts both servers in parallel
- Color-coded output
- Health checks before launching
- Auto-cleanup on Ctrl+C

**start-dev.bat** (Windows)
- Same features as bash script
- Works in Command Prompt
- Starts servers in separate windows

### Documentation

**GETTING_STARTED.md**
- Complete setup guide
- Step-by-step instructions
- Troubleshooting section
- API reference
- Development commands
- Deployment guides

**BACKEND_REPORT.md**
- Architecture analysis
- Security review
- Performance notes

**TESTING_RESULTS.md**
- Test results summary
- Deployment checklist

**BACKEND_TESTING_SUMMARY.md**
- Detailed test results
- Bug fixes applied
- Setup instructions

## Next Steps

1. Run the startup script: `./start-dev.sh` or `start-dev.bat`
2. Wait for both servers to start (should see confirmation messages)
3. Open http://localhost:3000 in your browser
4. Register for an account or log in
5. Start using the CloudOps AI Copilot!

## Additional Resources

- Full getting started guide: See `GETTING_STARTED.md`
- Backend reference: See `cloudops-ai-copilot/backend/QUICK_START.md`
- Architecture details: See `BACKEND_REPORT.md`
- API documentation: http://localhost:8000/docs (when servers are running)

---

**Summary**: The "Request failed" error appeared because the backend wasn't running. You now have convenient scripts to start both servers with one command. Use `./start-dev.sh` (Mac/Linux) or `start-dev.bat` (Windows) and you're good to go!
