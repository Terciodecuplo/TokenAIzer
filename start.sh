#!/bin/bash

# TokenAIzer startup script
export ANTHROPIC_BASE_URL=http://localhost:8090

echo "🔑 ANTHROPIC_BASE_URL set to http://localhost:8090"

# Trap CTRL+C to clean up
cleanup() {
    echo ""
    echo "🛑 Shutting down TokenAIzer..."
    unset ANTHROPIC_BASE_URL
    kill $BACKEND_PID $DASHBOARD_PID 2>/dev/null
    echo "✅ Done. ANTHROPIC_BASE_URL restored."
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend
echo "🚀 Starting backend..."
cd /Users/josemurciabelmonte/Documents/TokenAIzer/backend
source .venv/bin/activate
python main.py &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2

# Start dashboard
echo "🎨 Starting dashboard..."
cd /Users/josemurciabelmonte/Documents/TokenAIzer/dashboard
npm run dev &
DASHBOARD_PID=$!

echo ""
echo "✅ TokenAIzer running"
echo "   Backend:   http://localhost:8002"
echo "   Dashboard: http://localhost:5173"
echo "   Proxy:     http://localhost:8090 (start from dashboard)"
echo ""
echo "Press CTRL+C to stop everything"

# Wait
wait
