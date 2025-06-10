@echo off
REM RevBot Debug Mode - Windows

echo Starting RevBot in Debug Mode...
echo.

REM Check if virtual environment exists
if not exist "revbot" (
    echo ❌ Virtual environment 'revbot' not found.
    echo    Run setup first: run.bat
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call revbot\Scripts\activate.bat

REM Start the main server in background
echo 🚀 Starting RevBot server on http://localhost:8000
start "RevBot Server" cmd /k "python main.py"

REM Wait a moment for server to start
timeout /t 3 /nobreak >nul

REM Start debug frontend
echo 🌐 Starting debug frontend on http://localhost:3000
echo.
echo 📊 Debug Interface: http://localhost:3000/debug_frontend.html
echo 🔍 API Documentation: http://localhost:8000/docs
echo 📡 Main API: http://localhost:8000
echo.
echo Press Ctrl+C to stop debug server
echo Both servers need to be running for debugging

python serve_debug.py