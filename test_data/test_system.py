#!/usr/bin/env python3
"""
System test script to verify all functionality is working correctly.
"""

import sqlite3
import subprocess
import sys
import time
import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode

def test_database():
    """Test database connection and user data."""
    print("🔍 Testing database...")
    
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Check users table
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    print(f"  Users in database: {user_count}")
    
    # Check each role
    cursor.execute('SELECT role, COUNT(*) FROM users GROUP BY role')
    roles = cursor.fetchall()
    for role, count in roles:
        print(f"  {role}: {count}")
    
    # Check admin user exists
    cursor.execute('SELECT id, email, name FROM users WHERE role = "admin"')
    admin = cursor.fetchone()
    if admin:
        print(f"  ✅ Admin user: {admin[1]} ({admin[2]})")
    else:
        print("  ❌ No admin user found!")
    
    conn.close()
    return user_count > 0

def test_backend_running():
    """Test if backend is running."""
    print("🚀 Testing backend...")
    
    try:
        req = Request('http://localhost:8000/')
        response = urlopen(req, timeout=5)
        if response.status == 200:
            print("  ✅ Backend is responding")
            return True
        else:
            print(f"  ❌ Backend returned status {response.status}")
            return False
    except Exception as e:
        print(f"  ❌ Backend not responding: {e}")
        return False

def test_authentication():
    """Test authentication for different user roles."""
    print("🔐 Testing authentication...")
    
    test_users = [
        ("admin@demo.com", "admin123", "admin"),
        ("controller1@demo.com", "controller123", "controller"),
        ("max.mustermann@demo.com", "employee123", "employee")
    ]
    
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
                else:
                    print(f"  ❌ {expected_role}: expected role {expected_role}, got {actual_role}")
            else:
                print(f"  ❌ {expected_role}: status {response.status}")
                
        except Exception as e:
            print(f"  ❌ {expected_role}: {e}")

def test_admin_endpoints():
    """Test admin dashboard endpoints."""
    print("📊 Testing admin endpoints...")
    
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
        
        # Test admin dashboard
        req = Request(
            'http://localhost:8000/api/v1/admin/dashboard',
            headers={'Authorization': f'Bearer {token}'}
        )
        response = urlopen(req, timeout=5)
        
        if response.status == 200:
            dashboard_data = json.loads(response.read().decode())
            print(f"  ✅ Admin dashboard: {len(dashboard_data.get('controllers', []))} controllers")
            print(f"    Unassigned employees: {len(dashboard_data.get('unassigned_employees', []))}")
        else:
            print(f"  ❌ Admin dashboard: status {response.status}")
            
    except Exception as e:
        print(f"  ❌ Admin endpoints: {e}")

def main():
    """Run all tests."""
    print("🧪 TravelExpense System Test")
    print("=" * 40)
    
    # Test database
    db_ok = test_database()
    print()
    
    # Test backend
    backend_ok = test_backend_running()
    print()
    
    if backend_ok:
        # Test authentication
        test_authentication()
        print()
        
        # Test admin endpoints
        test_admin_endpoints()
        print()
    
    print("=" * 40)
    if db_ok and backend_ok:
        print("✅ System appears to be working correctly!")
    else:
        print("❌ Some issues were found. Check the output above.")

if __name__ == "__main__":
    main()
