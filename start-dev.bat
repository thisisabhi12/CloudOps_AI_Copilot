@echo off
REM CloudOps AI Copilot - Development Server Startup Script (Windows)
REM This script starts both the frontend and backend servers in parallel

setlocal enabledelayedexpansion

cd /d "%~dp0"
set PROJECT_ROOT=%cd%
set BACKEND_DIR=%PROJECT_ROOT%\cloudops-ai-copilot\backend
set FRONTEND_DIR=%PROJECT_ROOT%\cloudops-ai-copilot\frontend

echo.
echo ════════════════════════════════════════════════════════════════
echo     CloudOps AI Copilot - Development Environment Startup      
echo ════════════════════════════════════════════════════════════════
echo.

REM Check if backend dependencies are installed
echo [1/4] Checking backend dependencies...
cd /d "%BACKEND_DIR%"
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing backend dependencies...
    pip install -q -r requirements.txt
    echo Backend dependencies installed
) else (
    echo Backend dependencies already installed
)

REM Check if frontend dependencies are installed
echo [2/4] Checking frontend dependencies...
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install --silent
    echo Frontend dependencies installed
) else (
    echo Frontend dependencies already installed
)

echo.
echo [3/4] Starting backend server...
cd /d "%BACKEND_DIR%"
start /B "CloudOps Backend" python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo Backend started
echo         URL: http://localhost:8000
echo         API Docs: http://localhost:8000/docs
timeout /t 2 /nobreak >nul

echo.
echo [4/4] Starting frontend server...
cd /d "%FRONTEND_DIR%"
start /B "CloudOps Frontend" cmd /c "npm run dev"
echo Frontend started
echo         URL: http://localhost:3000
timeout /t 3 /nobreak >nul

echo.
echo ════════════════════════════════════════════════════════════════
echo                   Both servers are running!                     
echo ════════════════════════════════════════════════════════════════
echo.
echo Access the application:
echo   Frontend:    http://localhost:3000
echo   Backend:     http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo.
echo Close this window to stop all servers
echo.
pause
