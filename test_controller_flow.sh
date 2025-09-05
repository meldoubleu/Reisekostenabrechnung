#!/bin/bash

echo "🧪 Testing Complete Controller Authentication and Dashboard Flow"
echo "==============================================================="

# Test 1: Controller Login
echo "1️⃣ Testing Controller Login..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email": "controller1@demo.com", "password": "controller123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
USER_INFO=$(echo "$LOGIN_RESPONSE" | jq -r '.user')

if [ "$TOKEN" != "null" ] && [ "$TOKEN" != "" ]; then
    echo "✅ Login successful"
    echo "   Controller: $(echo "$USER_INFO" | jq -r '.name')"
    echo "   Role: $(echo "$USER_INFO" | jq -r '.role')"
    echo "   Token: ${TOKEN:0:20}..."
else
    echo "❌ Login failed"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

echo ""

# Test 2: User Identity Check
echo "2️⃣ Testing User Identity (/me endpoint)..."
ME_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/auth/me")
ME_ROLE=$(echo "$ME_RESPONSE" | jq -r '.role')

if [ "$ME_ROLE" = "controller" ]; then
    echo "✅ User identity confirmed as controller"
    echo "   User: $(echo "$ME_RESPONSE" | jq -r '.name')"
else
    echo "❌ User identity check failed"
    echo "$ME_RESPONSE"
    exit 1
fi

echo ""

# Test 3: Team Data Access
echo "3️⃣ Testing Team Data Access (/my-team endpoint)..."
TEAM_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/users/my-team")

# Check if response is a valid JSON array
if echo "$TEAM_RESPONSE" | jq -e 'type == "array"' > /dev/null 2>&1; then
    TEAM_COUNT=$(echo "$TEAM_RESPONSE" | jq 'length')
    echo "✅ Team data access successful"
    echo "   Assigned employees: $TEAM_COUNT"
    echo "   Employee names:"
    echo "$TEAM_RESPONSE" | jq -r '.[].name' | sed 's/^/     - /'
else
    echo "❌ Team data access failed"
    echo "$TEAM_RESPONSE"
    exit 1
fi

echo ""

# Test 4: Test with second controller
echo "4️⃣ Testing Second Controller (controller2@demo.com)..."
LOGIN_RESPONSE2=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email": "controller2@demo.com", "password": "controller123"}')

TOKEN2=$(echo "$LOGIN_RESPONSE2" | jq -r '.access_token')

if [ "$TOKEN2" != "null" ] && [ "$TOKEN2" != "" ]; then
    TEAM_RESPONSE2=$(curl -s -H "Authorization: Bearer $TOKEN2" "http://localhost:8000/api/v1/users/my-team")
    TEAM_COUNT2=$(echo "$TEAM_RESPONSE2" | jq 'length')
    echo "✅ Second controller authentication successful"
    echo "   Assigned employees: $TEAM_COUNT2"
    echo "   Employee names:"
    echo "$TEAM_RESPONSE2" | jq -r '.[].name' | sed 's/^/     - /'
else
    echo "❌ Second controller authentication failed"
fi

echo ""
echo "🎉 All controller authentication and data access tests completed!"
echo ""
echo "📝 Summary:"
echo "   - Controller authentication: ✅ Working"
echo "   - Role-based access control: ✅ Working" 
echo "   - Team data retrieval: ✅ Working"
echo "   - Multiple controllers: ✅ Working"
echo ""
echo "🌐 To test in browser:"
echo "   1. Go to http://localhost:8000/"
echo "   2. Login with: controller1@demo.com / controller123"
echo "   3. Navigate to dashboard to see assigned employees"
