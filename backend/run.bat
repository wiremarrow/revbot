@echo off
REM RevBot Backend Startup Script for Windows

echo Starting RevBot Backend...

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Error: Python not found. Please install Python 3.8+.
        echo    Download from: https://python.org or Microsoft Store
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo Using Python: %PYTHON_CMD%

REM Check if virtual environment exists
if not exist "revbot" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv revbot
    if errorlevel 1 (
        echo ❌ Error: Failed to create virtual environment.
        echo    Ensure Python is properly installed and in PATH.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call revbot\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Error: Failed to activate virtual environment.
    echo    Try running as Administrator or check antivirus settings.
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error: Failed to install dependencies.
    echo    Check internet connection and try running as Administrator.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo 📝 Please edit .env file and add your Anthropic API key!
    echo    Your API key should replace 'your_anthropic_api_key_here'
    pause
    exit /b 1
)

REM Verify setup
echo Verifying setup...
python test_setup.py
if errorlevel 1 (
    echo ❌ Setup verification failed. Please check the issues above.
    pause
    exit /b 1
)

REM Run the application
echo 🚀 Starting FastAPI server...
echo    Server will be available at: http://localhost:8000
echo    API docs available at: http://localhost:8000/docs
echo    Press Ctrl+C to stop
python main.py