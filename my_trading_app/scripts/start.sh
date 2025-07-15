#!/bin/bash

# Kill any existing processes on ports 3000 and 8000
echo "Cleaning up existing processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "Port 3000 already free"
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "Port 8000 already free"

echo "Starting backend server..."
cd deliverables/src/backend
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "🚀 Trading Dashboard starting..."
echo "📊 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo "All servers stopped."
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup INT

# Wait for both processes
wait