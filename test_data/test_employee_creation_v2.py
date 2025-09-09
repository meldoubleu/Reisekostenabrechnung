#!/usr/bin/env python3
"""
Test employee creation through admin API.
"""

import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError

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
            "email": "test.employee.new@demo.com",
            "password": "employee123",
            "name": "Test Employee New",
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
        
        try:
            response = urlopen(req, timeout=5)
            
            if response.status == 201:
                created_user = json.loads(response.read().decode())
                print(f"  ✅ Employee created: {created_user['name']} ({created_user['email']})")
                
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
                    return True
                else:
                    print(f"  ❌ New employee cannot login: status {response.status}")
                    return False
            else:
                print(f"  ❌ Unexpected status: {response.status}")
                return False
                
        except HTTPError as e:
            if e.code == 400:
                try:
                    error_detail = json.loads(e.read().decode())
                    print(f"  ❌ Employee creation failed (400): {error_detail}")
                    if "Email already exists" in error_detail.get('detail', ''):
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
                        try:
                            response = urlopen(req, timeout=5)
                            if response.status == 200:
                                print(f"  ✅ Existing employee can login successfully")
                                return True
                            else:
                                print(f"  ❌ Existing employee cannot login: status {response.status}")
                                return False
                        except Exception as login_e:
                            print(f"  ❌ Login test failed: {login_e}")
                            return False
                except:
                    print(f"  ❌ Could not parse 400 error response")
                    return False
            else:
                print(f"  ❌ HTTP Error {e.code}: {e.reason}")
                return False
            
    except Exception as e:
        print(f"  ❌ Employee creation test: {e}")
        return False

if __name__ == "__main__":
    test_employee_creation()
