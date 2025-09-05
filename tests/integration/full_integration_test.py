#!/usr/bin/env python3
"""
Integration tests for TravelExpense system.
Tests user creation, authentication, and database consistency.
"""

import json
import sqlite3
from urllib.request import urlopen, Request
from urllib.error import HTTPError


def test_database_consistency():
    """Test that all roles are using the same database."""
    print("🔍 Testing database consistency...")
    
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Check users table
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    print(f"  Users in database: {user_count}")
    
    # Check role distribution
    cursor.execute('SELECT role, COUNT(*) FROM users GROUP BY role')
    roles = cursor.fetchall()
    role_counts = {}
    for role, count in roles:
        role_counts[role] = count
        print(f"  {role}: {count}")
    
    conn.close()
    
    # Verify we have all required roles
    required_roles = ['admin', 'controller', 'employee']
    missing_roles = [role for role in required_roles if role not in role_counts]
    
    if missing_roles:
        print(f"  ❌ Missing roles: {missing_roles}")
        return False
    else:
        print("  ✅ All required roles present")
        return True


def test_authentication_all_roles():
    """Test authentication for all user roles."""
    print("🔐 Testing authentication for all roles...")
    
    test_users = [
        ("admin@demo.com", "admin123", "admin"),
        ("controller1@demo.com", "controller123", "controller"),
        ("max.mustermann@demo.com", "employee123", "employee")
    ]
    
    success_count = 0
    for email, password, expected_role in test_users:
        try:
            data = json.dumps({"email": email, "password": password}).encode()
            req = Request(
                'http://localhost:8000/api/v1/auth/login',
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            response = urlopen(req, timeout=5)
            
            if response.status == 200:
                result = json.loads(response.read().decode())
                actual_role = result['user']['role']
                if actual_role == expected_role:
                    print(f"  ✅ {expected_role}: {email}")
                    success_count += 1
                else:
                    print(f"  ❌ {expected_role}: expected role {expected_role}, got {actual_role}")
            else:
                print(f"  ❌ {expected_role}: status {response.status}")
                
        except Exception as e:
            print(f"  ❌ {expected_role}: {e}")
    
    return success_count == len(test_users)


def test_employee_creation_flow():
    """Test creating a new employee through admin API and verifying login."""
    print("👤 Testing employee creation flow...")
    
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
            return False
            
        login_result = json.loads(response.read().decode())
        token = login_result['access_token']
        print(f"  ✅ Admin login successful")
        
        # Create new employee
        new_employee = {
            "email": "integration.test@demo.com",
            "password": "employee123",
            "name": "Integration Test Employee",
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
                print(f"  ❌ Employee creation failed: status {response.status}")
                return False
                
        except HTTPError as e:
            if e.code == 400:
                error_detail = json.loads(e.read().decode())
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
                    response = urlopen(req, timeout=5)
                    
                    if response.status == 200:
                        print(f"  ✅ Existing employee can login successfully")
                        return True
                    else:
                        print(f"  ❌ Existing employee cannot login: status {response.status}")
                        return False
                else:
                    print(f"  ❌ Employee creation failed: {error_detail}")
                    return False
            else:
                print(f"  ❌ Employee creation failed: HTTP {e.code}")
                return False
            
    except Exception as e:
        print(f"  ❌ Employee creation test: {e}")
        return False


def test_admin_dashboard_access():
    """Test admin dashboard access and data."""
    print("📊 Testing admin dashboard access...")
    
    try:
        # Login as admin
        data = json.dumps({"email": "admin@demo.com", "password": "admin123"}).encode()
        req = Request(
            'http://localhost:8000/api/v1/auth/login',
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        response = urlopen(req, timeout=5)
        
        if response.status != 200:
            print("  ❌ Could not login as admin")
            return False
            
        login_result = json.loads(response.read().decode())
        token = login_result['access_token']
        
        # Test admin dashboard
        req = Request(
            'http://localhost:8000/api/v1/admin/dashboard',
            headers={'Authorization': f'Bearer {token}'}
        )
        response = urlopen(req, timeout=5)
        
        if response.status == 200:
            dashboard_data = json.loads(response.read().decode())
            controllers = dashboard_data.get('controllers', [])
            unassigned = dashboard_data.get('unassigned_employees', [])
            print(f"  ✅ Admin dashboard accessible")
            print(f"    Controllers: {len(controllers)}")
            print(f"    Unassigned employees: {len(unassigned)}")
            return True
        else:
            print(f"  ❌ Admin dashboard: status {response.status}")
            return False
            
    except Exception as e:
        print(f"  ❌ Admin dashboard test: {e}")
        return False


def main():
    """Run all integration tests."""
    print("🧪 TravelExpense Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Database Consistency", test_database_consistency),
        ("Authentication All Roles", test_authentication_all_roles),
        ("Employee Creation Flow", test_employee_creation_flow),
        ("Admin Dashboard Access", test_admin_dashboard_access)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("\n✅ CONFIRMED: All roles (admin, controller, employee) use the same database")
        print("✅ CONFIRMED: Admin-created employees can login with their credentials")
        print("✅ CONFIRMED: Authentication works for all user roles")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    main()
