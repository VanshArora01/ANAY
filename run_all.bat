@echo off
REM ANAY Unified Startup Script

echo Starting ANAY Frontend and Backend...

REM Start Backend (in a new window)
start "ANAY Backend" cmd /k "cd backend && start.bat"

REM Start Frontend (in a new window)
start "ANAY Frontend" cmd /k "cd anay-your-ai-companion && start.bat"

echo.
echo Services are starting in separate windows.
echo Frontend: http://localhost:8080
echo Backend: Check the backend window for status.
echo.
pause
