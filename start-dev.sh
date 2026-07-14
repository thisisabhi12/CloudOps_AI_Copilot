#!/bin/bash

# CloudOps AI Copilot - Development Server Startup Script
# This script starts both the frontend and backend servers in parallel

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/cloudops-ai-copilot/backend"
FRONTEND_DIR="$PROJECT_ROOT/cloudops-ai-copilot/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     CloudOps AI Copilot - Development Environment Startup      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}Cleanup complete${NC}"
}

trap cleanup EXIT INT TERM

# Check if backend dependencies are installed
echo -e "${BLUE}[1/4]${NC} Checking backend dependencies..."
cd "$BACKEND_DIR"
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install -q -r requirements.txt
    echo -e "${GREEN}Backend dependencies installed${NC}"
else
    echo -e "${GREEN}Backend dependencies already installed${NC}"
fi

# Check if frontend dependencies are installed
echo -e "${BLUE}[2/4]${NC} Checking frontend dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install --silent
    echo -e "${GREEN}Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}Frontend dependencies already installed${NC}"
fi

echo ""
echo -e "${BLUE}[3/4]${NC} Starting backend server..."
cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}Backend started (PID: $BACKEND_PID)${NC}"
echo -e "         Logs: /tmp/backend.log"
echo -e "         URL: ${BLUE}http://localhost:8000${NC}"
echo -e "         API Docs: ${BLUE}http://localhost:8000/docs${NC}"

# Wait a moment for backend to start
sleep 2

# Check if backend started successfully
if ! ps -p $BACKEND_PID > /dev/null; then
    echo -e "${RED}✗ Backend failed to start${NC}"
    cat /tmp/backend.log
    exit 1
fi

echo ""
echo -e "${BLUE}[4/4]${NC} Starting frontend server..."
cd "$FRONTEND_DIR"
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "         Logs: /tmp/frontend.log"
echo -e "         URL: ${BLUE}http://localhost:3000${NC}"

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${RED}✗ Frontend failed to start${NC}"
    cat /tmp/frontend.log
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✓ Both servers are running!                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Access the application:${NC}"
echo -e "  Frontend:    ${BLUE}http://localhost:3000${NC}"
echo -e "  Backend:     ${BLUE}http://localhost:8000${NC}"
echo -e "  API Docs:    ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo -e "  Backend:     tail -f /tmp/backend.log"
echo -e "  Frontend:    tail -f /tmp/frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Keep the script running
wait $BACKEND_PID $FRONTEND_PID
