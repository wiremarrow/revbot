#!/bin/bash
# RevBot Debug Mode - macOS/Linux

echo "Starting RevBot in Debug Mode..."
echo

# Check if virtual environment exists
if [ ! -d "revbot" ]; then
    echo "❌ Virtual environment 'revbot' not found."
    echo "   Run setup first: ./run.sh"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source revbot/bin/activate

# Start the main server in background
echo "🚀 Starting RevBot server on http://localhost:8000"
python main.py &
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Start debug frontend
echo "🌐 Starting debug frontend on http://localhost:3000"
echo
echo "📊 Debug Interface: http://localhost:3000/debug_frontend.html"
echo "🔍 API Documentation: http://localhost:8000/docs"
echo "📡 Main API: http://localhost:8000"
echo
echo "Press Ctrl+C to stop debug server"
echo "Both servers need to be running for debugging"

# Trap Ctrl+C to clean up background process
trap "echo 'Stopping servers...'; kill $SERVER_PID 2>/dev/null; exit" INT

python serve_debug.py

# Clean up if we get here
kill $SERVER_PID 2>/dev/null