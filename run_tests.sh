#!/usr/bin/env bash
# Test runner for TravelExpense system

echo "🧪 TravelExpense Test Suite"
echo "=========================="

# Check if backend is running
if ! curl -s "http://localhost:8000/" > /dev/null; then
    echo "❌ Backend not running. Please start with ./run_local.sh start"
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Run system test
echo "🔄 Running system tests..."
python3 tests/integration/system_test.py
echo ""

# Run full integration test
echo "🔄 Running integration tests..."
python3 tests/integration/full_integration_test.py
echo ""

echo "✅ Test suite completed!"
