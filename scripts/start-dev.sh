#!/bin/bash

# Kashar AI Development Startup Script

echo "🚀 Starting Kashar AI Development Environment..."

# Check if required environment files exist
if [ ! -f "backend/.env" ]; then
    echo "❌ Backend .env file not found. Please copy backend/.env.example to backend/.env and configure it."
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check required ports
echo "🔍 Checking required ports..."
check_port 3000 || echo "   Frontend (React) port 3000 is busy"
check_port 8000 || echo "   Backend (FastAPI) port 8000 is busy"
check_port 5001 || echo "   Parsing Service (Flask) port 5001 is busy"

echo ""

# Start services in background
echo "🔧 Starting Backend Services..."

# Start FastAPI backend
echo "   Starting FastAPI backend on port 8000..."
cd backend
if [ ! -d "venv" ]; then
    echo "     Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "     Installing Python dependencies..."
pip install -r requirements.txt >/dev/null 2>&1
echo "     Starting FastAPI server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start Flask parsing service
echo "   Starting Flask parsing service on port 5001..."
cd parsing-service
if [ ! -d "venv" ]; then
    echo "     Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "     Installing Python dependencies..."
pip install -r requirements.txt >/dev/null 2>&1
echo "     Starting Flask server..."
python3 app.py &
PARSING_PID=$!
cd ..

# Start React frontend
echo "   Starting React frontend on port 3000..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "     Installing Node.js dependencies..."
    npm install >/dev/null 2>&1
fi
echo "     Starting React development server..."
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All services started successfully!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📄 API Docs: http://localhost:8000/docs"
echo "🔍 Parsing Service: http://localhost:5001"
echo ""
echo "💡 To stop all services, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $PARSING_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait
