#!/usr/bin/env bash
# Test admin login and role verification

echo "Testing Admin Authentication Fix..."

# Test 1: Admin Login
echo "1. Testing admin login..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@demo.com", "password": "admin123"}')

echo "Login response: $RESPONSE"

# Extract token
TOKEN=$(echo "$RESPONSE" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    print(data.get('access_token', ''))
except:
    print('')
")

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed - no token received"
    exit 1
fi

echo "✅ Login successful - token received"

# Test 2: Check /auth/me endpoint
echo "2. Testing /auth/me endpoint..."
ME_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN")

echo "Auth/me response: $ME_RESPONSE"

# Check if role is admin
ROLE=$(echo "$ME_RESPONSE" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    print(data.get('role', ''))
except:
    print('')
")

echo "Detected role: $ROLE"

if [ "$ROLE" = "admin" ]; then
    echo "✅ Admin role correctly detected!"
else
    echo "❌ Admin role NOT detected. Got: $ROLE"
fi

echo ""
echo "Summary:"
echo "- Login: ✅"
echo "- Admin role: $([ "$ROLE" = "admin" ] && echo "✅" || echo "❌")"
