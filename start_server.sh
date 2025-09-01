#!/bin/bash

# PMIS AI Allocation Engine - Start Server Script
# This script starts the Flask server for the PMIS AI Allocation Engine

echo "🚀 Starting PMIS AI Allocation Engine..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if port 5000 is already in use
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 5000 is already in use. Please stop the existing server first."
    echo "   Run: ./restart_server.sh"
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
