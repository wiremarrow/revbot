#!/bin/bash

# RevBot Backend Startup Script for macOS/Linux

echo "Starting RevBot Backend..."

# Check Python installation
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found. Please install Python 3.8+."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "Using Python: $PYTHON_CMD"

# Check if virtual environment exists
if [ ! -d "revbot" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv revbot
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment."
        echo "   Try: sudo apt install python3-venv (Linux) or install Python from python.org"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source revbot/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your Anthropic API key!"
    echo "   Your API key should replace 'your_anthropic_api_key_here'"
    exit 1
fi

# Verify setup
echo "Verifying setup..."
python test_setup.py
if [ $? -ne 0 ]; then
    echo "❌ Setup verification failed. Please check the issues above."
    exit 1
fi

# Run the application
echo "🚀 Starting FastAPI server..."
echo "   Server will be available at: http://localhost:8000"
echo "   API docs available at: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"
python main.py