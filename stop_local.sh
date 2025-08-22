#!/usr/bin/env zsh
set -euo pipefail

echo "🛑 Stopping Reisekostenabrechnung..."

# Kill any process using port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Stopping server on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

# Remove PID file if it exists
if [ -f ".api_pid" ]; then
    API_PID=$(cat .api_pid)
    kill $API_PID 2>/dev/null || true
    rm -f .api_pid
fi

echo "✅ Server stopped"
