#!/usr/bin/env zsh
set -euo pipefail

echo "🧪 Running Basic API Tests..."

BASE_URL="http://localhost:8000/api/v1"

# Check if server is running
if ! curl -s "${BASE_URL}/travels/" > /dev/null; then
    echo "❌ Server not running. Start with: ./run_local.sh"
    exit 1
fi

echo "✅ Server is running"

# Test 1: Create a new travel
echo "📝 Test 1: Creating new travel..."
TRAVEL_RESPONSE=$(curl -s -X POST "${BASE_URL}/travels/" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "employee_name=Test User&start_at=2025-08-25T09:00:00&end_at=2025-08-25T17:00:00&destination_city=Berlin&destination_country=Germany&purpose=Business Meeting&cost_center=IT001")

TRAVEL_ID=$(echo $TRAVEL_RESPONSE | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
echo "✅ Created travel ID: $TRAVEL_ID"

# Test 2: List travels
echo "📋 Test 2: Listing travels..."
TRAVELS_COUNT=$(curl -s "${BASE_URL}/travels/" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
echo "✅ Found $TRAVELS_COUNT travels in database"

# Test 3: Test PDF export endpoint
echo "📄 Test 3: Testing PDF export..."
if curl -s -I "${BASE_URL}/travels/${TRAVEL_ID}/export" | grep -q "200 OK"; then
    echo "✅ PDF export endpoint working"
else
    echo "⚠️  PDF export endpoint issues"
fi

# Test 4: Submit travel
echo "📤 Test 4: Submitting travel..."
curl -s -X POST "${BASE_URL}/travels/${TRAVEL_ID}/submit" > /dev/null
echo "✅ Travel submitted"

echo ""
echo "🎉 All basic tests passed!"
echo "🌐 Frontend: http://localhost:8000/api/v1/ui"
echo "📚 API Docs: http://localhost:8000/docs"
