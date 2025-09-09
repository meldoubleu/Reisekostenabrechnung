#!/usr/bin/env bash
# Core Features Test - Essential Tests Only

set -e

echo "🎯 Core Features Test"
echo "===================="

# Activate venv if available
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check if backend is running
if ! curl -s http://localhost:8000/api/v1/ > /dev/null 2>&1; then
    echo "⚠️  Backend not running, starting it..."
    ./run_local.sh start &
    BACKEND_PID=$!
    CLEANUP_BACKEND=true
    echo "⏳ Waiting for backend to start..."
    sleep 8
else
    echo "✅ Backend is running"
fi

echo ""
echo "🧪 Running Core Feature Tests"
echo "-----------------------------"

# Run only the core tests
pytest -c pytest-essential.ini tests/test_core_features.py -v --tb=short

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 All core features are working!"
else
    echo ""
    echo "❌ Some core features need attention"
fi

# Cleanup if needed
if [[ "$CLEANUP_BACKEND" == "true" ]]; then
    echo ""
    echo "🧹 Stopping test backend..."
    kill $BACKEND_PID 2>/dev/null || true
    sleep 2
fi

echo ""
echo "✅ Core Features Testing Complete"
echo ""
echo "Features Tested:"
echo "• User Registration & Login"
echo "• User Profile Access"
echo "• Travel Creation & Viewing"
echo "• Basic Security"
echo "• System Health"
echo "• Complete User Journey"
