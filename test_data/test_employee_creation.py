#!/usr/bin/env python3
"""
Test employee creation through admin API.
"""

import json
from urllib.request import urlopen, Request

def test_employee_creation():
    """Test creating a new employee through admin API."""
    print("👤 Testing employee creation...")
    
    # First login as admin to get token
    try:
        data = json.dumps({"email": "admin@demo.com", "password": "admin123"}).encode()
        req = Request(
            'http://localhost:8000/api/v1/auth/login',
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        response = urlopen(req, timeout=5)
        
        if response.status != 200:
            print("  ❌ Could not login as admin")
            return
            
        login_result = json.loads(response.read().decode())
        token = login_result['access_token']
        print(f"  ✅ Admin login successful")
        
        # Create new employee
        new_employee = {
            "email": "test.employee@demo.com",
            "password": "employee123",
            "name": "Test Employee",
            "role": "employee",
            "company": "Demo GmbH",
            "department": "Testing",
            "cost_center": "TEST-001"
        }
        
        data = json.dumps(new_employee).encode()
        req = Request(
            'http://localhost:8000/api/v1/admin/employees',
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        response = urlopen(req, timeout=5)
        
        if response.status == 201:
            created_user = json.loads(response.read().decode())
            print(f"  ✅ Employee created: {created_user['name']} ({created_user['email']})")
            employee_id = created_user['id']
            
            # Test if the new employee can login
            login_data = json.dumps({
                "email": new_employee["email"], 
                "password": new_employee["password"]
            }).encode()
            req = Request(
                'http://localhost:8000/api/v1/auth/login',
                data=login_data,
                headers={'Content-Type': 'application/json'}
            )
            response = urlopen(req, timeout=5)
            
            if response.status == 200:
                login_result = json.loads(response.read().decode())
                print(f"  ✅ New employee can login successfully")
                print(f"    Role: {login_result['user']['role']}")
                return employee_id
            else:
                print(f"  ❌ New employee cannot login: status {response.status}")
                
        else:
            # Read response for any status code to see the error
            try:
                error_detail = json.loads(response.read().decode())
                print(f"  ❌ Employee creation failed ({response.status}): {error_detail}")
                if response.status == 400 and "Email already exists" in error_detail.get('detail', ''):
                    print("  ℹ️  Employee already exists, testing login...")
                    # Test login with existing user
                    login_data = json.dumps({
                        "email": new_employee["email"], 
                        "password": new_employee["password"]
                    }).encode()
                    req = Request(
                        'http://localhost:8000/api/v1/auth/login',
                        data=login_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    response = urlopen(req, timeout=5)
                    
                    if response.status == 200:
                        print(f"  ✅ Existing employee can login successfully")
                        return True
                    else:
                        print(f"  ❌ Existing employee cannot login: status {response.status}")
            except:
                response_text = response.read().decode()
                print(f"  ❌ Employee creation failed: status {response.status}")
                print(f"      Response: {response_text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Employee creation test: {e}")
        return False

if __name__ == "__main__":
    test_employee_creation()
