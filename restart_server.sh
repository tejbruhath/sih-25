#!/bin/bash

# PMIS AI Allocation Engine - Restart Server Script
# This script stops any existing Flask server and starts a fresh one

echo "🔄 Restarting PMIS AI Allocation Engine..."

# Function to stop Flask processes
stop_flask() {
    echo "🛑 Stopping existing Flask server..."
    
    # Kill Flask processes
    pkill -f "flask run" 2>/dev/null
    pkill -f "python.*app.py" 2>/dev/null
    
    # Wait for processes to stop
    sleep 3
    
    # Check if port is still in use
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port 5000 is still in use. Force killing processes..."
        # Force kill processes using port 5000
        sudo lsof -ti:5000 | xargs kill -9 2>/dev/null
        sleep 2
    fi
    
    echo "✅ Server stopped successfully"
}

# Function to start Flask server
start_flask() {
    echo "🚀 Starting Flask server..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found. Please run setup first."
        echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
    
    # Activate virtual environment
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    
    # Check if required packages are installed
    if ! python -c "import flask" 2>/dev/null; then
        echo "📥 Installing required packages..."
        pip install -r requirements.txt
    fi
    
    # Create necessary directories
    echo "📁 Creating necessary directories..."
    mkdir -p uploads/resumes
    mkdir -p results
    mkdir -p templates
    
    # Start the Flask server
    echo "🌐 Starting Flask server..."
    echo "   Server will be available at:"
    echo "   - http://localhost:5000"
    echo "   - http://127.0.0.1:5000"
    echo "   - http://192.168.1.23:5000"
    echo ""
    echo "   Press Ctrl+C to stop the server"
    echo ""
    
    # Start the server
    FLASK_APP=app.py flask run --host=0.0.0.0 --port=5000
}

# Main execution
echo "🎯 PMIS AI Allocation Engine Restart Script"
echo "=========================================="

# Stop existing server
stop_flask

# Start new server
start_flask
