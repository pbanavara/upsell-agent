#!/bin/bash

# Startup script for Upsell Agent with FastAPI backend and Next.js frontend

echo "🚀 Starting Upsell Agent..."

# Check if we're in the right directory
if [ ! -f "api_server.py" ]; then
    echo "❌ Please run this script from the upsell-agent root directory"
    exit 1
fi

# Create uploads directory
mkdir -p uploads

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "📦 Installing Next.js dependencies..."
cd frontend
npm install
cd ..

echo "🔧 Starting FastAPI backend server..."
python api_server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

echo "🎨 Starting Next.js frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Upsell Agent is running!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
