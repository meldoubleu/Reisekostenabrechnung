#!/usr/bin/env python3
"""
Test frontend authentication flow to debug travel creation issue.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login_and_create_travel():
    # Step 1: Login
    print("Step 1: Logging in...")
    login_data = {
        "email": "max.mustermann@demo.com",
        "password": "employee123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    login_result = login_response.json()
    token = login_result["access_token"]
    user = login_result["user"]
    
    print(f"Login successful. User: {user['name']}, Role: {user['role']}")
    
    # Step 2: Create travel (simulating frontend data structure)
    print("\nStep 2: Creating travel...")
    
    travel_data = {
        "employee_name": user["name"],
        "purpose": "business",
        "start_at": "2025-09-07T00:00:00Z",
        "end_at": "2025-09-08T23:59:59Z",
        "departure_location": "Musterstraße 123, 80331 München, Deutschland",
        "destination_city": "Berlin",
        "destination_country": "Germany",
        "cost_center": user.get("cost_center")
        # No status field needed for submit endpoint
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Sending travel data: {json.dumps(travel_data, indent=2)}")
    print(f"Headers: {headers}")
    
    travel_response = requests.post(f"{BASE_URL}/travels/submit", json=travel_data, headers=headers)
    print(f"Travel creation status: {travel_response.status_code}")
    
    if travel_response.status_code == 201:  # Submit endpoint returns 201
        travel_result = travel_response.json()
        print(f"Travel created successfully: ID {travel_result['id']}")
    else:
        print(f"Travel creation failed: {travel_response.text}")
        # Try to parse error details
        try:
            error_details = travel_response.json()
            print(f"Error details: {json.dumps(error_details, indent=2)}")
        except:
            pass

if __name__ == "__main__":
    test_login_and_create_travel()
