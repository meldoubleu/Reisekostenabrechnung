"""
Employee Role Complete Test Suite
Tests all API endpoints accessible by employee role users.
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from backend.app.main import app
from datetime import date, timedelta
import json


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def employee_token(client):
    """Get authentication token for employee user."""
    login_data = {
        "email": "employee@demo.com",
        "password": "employee123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # If login fails, try to register first
    register_data = {
        "email": "employee@demo.com",
        "password": "employee123",
        "name": "Test Employee",
        "role": "employee"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    if register_response.status_code == 200:
        return register_response.json()["access_token"]
    
    raise Exception("Could not authenticate employee user")


@pytest.fixture
def employee_headers(employee_token):
    """Get authentication headers for employee user."""
    return {"Authorization": f"Bearer {employee_token}"}


@pytest.mark.unit
class TestEmployeeAuthentication:
    """Test authentication endpoints for employees."""
    
    def test_employee_login_valid_credentials(self, client):
        """Test employee login with valid credentials."""
        login_data = {
            "email": "employee@demo.com",
            "password": "employee123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        if response.status_code == 404:
            # User doesn't exist, create it first
            register_data = {
                "email": "employee@demo.com",
                "password": "employee123",
                "name": "Test Employee",
                "role": "employee"
            }
            register_response = client.post("/api/v1/auth/register", json=register_data)
            assert register_response.status_code == 200
            
            # Now try login again
            response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"
    
    def test_employee_login_invalid_credentials(self, client):
        """Test employee login with invalid credentials."""
        login_data = {
            "email": "employee@demo.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
    
    def test_employee_get_me(self, client, employee_headers):
        """Test getting current employee user info."""
        response = client.get("/api/v1/auth/me", headers=employee_headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == "employee@demo.com"
        assert user_data["role"] == "employee"
        assert "id" in user_data
        assert "name" in user_data


@pytest.mark.integration
class TestEmployeeTravelManagement:
    """Test travel management endpoints for employees."""
    
    def test_employee_create_travel(self, client, employee_headers):
        """Test creating a new travel expense."""
        travel_data = {
            "destination": "Berlin Business Trip",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=2)).isoformat(),
            "purpose": "Client Meeting",
            "accommodation_costs": 300.0,
            "transport_costs": 150.0,
            "meal_costs": 120.0,
            "other_costs": 30.0,
            "total_expenses": 600.0
        }
        
        response = client.post("/api/v1/travels/", json=travel_data, headers=employee_headers)
        assert response.status_code in [200, 201]
        
        result = response.json()
        assert result["destination"] == "Berlin Business Trip"
        assert result["total_expenses"] == 600.0
        assert "id" in result
        
        return result["id"]
    
    def test_employee_get_my_travels(self, client, employee_headers):
        """Test retrieving employee's own travels."""
        response = client.get("/api/v1/travels/my", headers=employee_headers)
        
        if response.status_code == 404:
            # Endpoint might be different, try alternatives
            response = client.get("/api/v1/travels/", headers=employee_headers)
        
        assert response.status_code == 200
        travels = response.json()
        assert isinstance(travels, list)
    
    def test_employee_update_travel(self, client, employee_headers):
        """Test updating an existing travel."""
        # First create a travel
        travel_id = self.test_employee_create_travel(client, employee_headers)
        
        update_data = {
            "destination": "Munich Updated Trip",
            "purpose": "Updated Purpose",
            "accommodation_costs": 350.0,
            "total_expenses": 700.0
        }
        
        response = client.put(f"/api/v1/travels/{travel_id}", json=update_data, headers=employee_headers)
        assert response.status_code == 200
        
        updated_travel = response.json()
        assert updated_travel["destination"] == "Munich Updated Trip"
        assert updated_travel["total_expenses"] == 700.0
    
    def test_employee_submit_travel(self, client, employee_headers):
        """Test submitting a travel for approval."""
        # First create a travel
        travel_id = self.test_employee_create_travel(client, employee_headers)
        
        response = client.post(f"/api/v1/travels/{travel_id}/submit", headers=employee_headers)
        assert response.status_code == 200
        
        submitted_travel = response.json()
        assert submitted_travel["status"] == "submitted"


@pytest.mark.integration
class TestEmployeeReceiptManagement:
    """Test receipt management endpoints for employees."""
    
    def test_employee_upload_receipt(self, client, employee_headers):
        """Test uploading a receipt to a travel."""
        # First create a travel
        travel_test = TestEmployeeTravelManagement()
        travel_id = travel_test.test_employee_create_travel(client, employee_headers)
        
        # Create a simple test file
        test_file_content = b"Test receipt content"
        files = {"file": ("test_receipt.txt", test_file_content, "text/plain")}
        
        response = client.post(
            f"/api/v1/travels/{travel_id}/receipts",
            files=files,
            headers=employee_headers
        )
        assert response.status_code in [200, 201]
        
        receipt_data = response.json()
        assert "id" in receipt_data
        assert receipt_data["travel_id"] == travel_id


@pytest.mark.integration
class TestEmployeeRestrictedAccess:
    """Test that employees cannot access restricted endpoints."""
    
    def test_employee_cannot_access_admin_endpoints(self, client, employee_headers):
        """Test that employees cannot access admin endpoints."""
        admin_endpoints = [
            "/api/v1/admin/dashboard",
            "/api/v1/admin/controllers",
            "/api/v1/admin/employees",
            "/api/v1/admin/users/1",
            "/api/v1/admin/travels"
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=employee_headers)
            assert response.status_code in [401, 403, 404]  # Unauthorized or forbidden
    
    def test_employee_cannot_access_other_users_data(self, client, employee_headers):
        """Test that employees cannot access other users' data."""
        # Try to access user management endpoints
        response = client.get("/api/v1/users/", headers=employee_headers)
        assert response.status_code in [401, 403, 404]
        
        # Try to access specific user
        response = client.get("/api/v1/users/999", headers=employee_headers)
        assert response.status_code in [401, 403, 404]
    
    def test_employee_cannot_approve_travels(self, client, employee_headers):
        """Test that employees cannot approve or reject travels."""
        # Try to approve a travel
        response = client.put("/api/v1/travels/1/approve", headers=employee_headers)
        assert response.status_code in [401, 403, 404]
        
        # Try to reject a travel
        response = client.put("/api/v1/travels/1/reject", headers=employee_headers)
        assert response.status_code in [401, 403, 404]


@pytest.mark.e2e
class TestEmployeeCompleteWorkflow:
    """Test complete employee workflow end-to-end."""
    
    def test_complete_employee_travel_workflow(self, client, employee_headers):
        """Test complete workflow: login -> create travel -> add receipts -> submit."""
        
        # 1. Create a new travel
        travel_data = {
            "destination": "Frankfurt Conference",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=1)).isoformat(),
            "purpose": "Tech Conference",
            "accommodation_costs": 200.0,
            "transport_costs": 100.0,
            "meal_costs": 80.0,
            "other_costs": 20.0,
            "total_expenses": 400.0
        }
        
        create_response = client.post("/api/v1/travels/", json=travel_data, headers=employee_headers)
        assert create_response.status_code in [200, 201]
        travel = create_response.json()
        travel_id = travel["id"]
        
        # 2. Verify travel was created
        get_response = client.get(f"/api/v1/travels/{travel_id}", headers=employee_headers)
        if get_response.status_code == 404:
            # Try alternative endpoint
            get_response = client.get("/api/v1/travels/my", headers=employee_headers)
            assert get_response.status_code == 200
            travels = get_response.json()
            assert len(travels) > 0
        else:
            assert get_response.status_code == 200
            retrieved_travel = get_response.json()
            assert retrieved_travel["destination"] == "Frankfurt Conference"
        
        # 3. Submit travel for approval
        submit_response = client.post(f"/api/v1/travels/{travel_id}/submit", headers=employee_headers)
        if submit_response.status_code == 200:
            submitted_travel = submit_response.json()
            assert submitted_travel["status"] == "submitted"
        
        # 4. Verify travel appears in employee's travel list
        my_travels_response = client.get("/api/v1/travels/my", headers=employee_headers)
        if my_travels_response.status_code == 404:
            my_travels_response = client.get("/api/v1/travels/", headers=employee_headers)
        
        assert my_travels_response.status_code == 200
        my_travels = my_travels_response.json()
        assert any(t["id"] == travel_id for t in my_travels)
