#!/bin/bash

echo "Stopping Trading Dashboard..."

# Kill processes by port
echo "Killing processes on port 3000..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "No processes found on port 3000"

echo "Killing processes on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No processes found on port 8000"

# Kill by process name as backup
pkill -f "react-scripts start" 2>/dev/null || echo "No React processes found"
pkill -f "uvicorn main:app" 2>/dev/null || echo "No uvicorn processes found"

echo "✅ All servers stopped"