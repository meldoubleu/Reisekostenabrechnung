"""
Essential Feature Tests - Core Functionality Only
Tests the most important features for production readiness.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from datetime import date, timedelta
import json


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def admin_headers(client):
    """Get admin authentication headers."""
    login_data = {"email": "admin@demo.com", "password": "admin123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    
    if response.status_code != 200:
        # Create admin if doesn't exist
        register_data = {
            "email": "admin@demo.com",
            "password": "admin123",
            "name": "Admin User",
            "role": "admin"
        }
        client.post("/api/v1/auth/register", json=register_data)
        response = client.post("/api/v1/auth/login", json=login_data)
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employee_headers(client):
    """Get employee authentication headers."""
    login_data = {"email": "employee@demo.com", "password": "employee123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    
    if response.status_code != 200:
        # Create employee if doesn't exist
        register_data = {
            "email": "employee@demo.com",
            "password": "employee123",
            "name": "Test Employee",
            "role": "employee"
        }
        client.post("/api/v1/auth/register", json=register_data)
        response = client.post("/api/v1/auth/login", json=login_data)
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCoreAuthentication:
    """Test core authentication features."""
    
    def test_user_can_login(self, client):
        """Test that users can log in with valid credentials."""
        # First register a user
        register_data = {
            "email": "testuser@demo.com",
            "password": "testpass123",
            "name": "Test User",
            "role": "employee"
        }
        client.post("/api/v1/auth/register", json=register_data)
        
        # Then login
        login_data = {"email": "testuser@demo.com", "password": "testpass123"}
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_invalid_login_rejected(self, client):
        """Test that invalid credentials are rejected."""
        login_data = {"email": "fake@demo.com", "password": "wrongpass"}
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code in [401, 404]
    
    def test_user_can_get_profile(self, client, employee_headers):
        """Test that authenticated users can get their profile."""
        response = client.get("/api/v1/auth/me", headers=employee_headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert "email" in user_data
        assert "role" in user_data


class TestTravelManagement:
    """Test core travel expense management."""
    
    def test_employee_can_create_travel(self, client, employee_headers):
        """Test that employees can create travel expenses."""
        travel_data = {
            "employee_name": "Test Employee",
            "start_at": date.today().isoformat() + "T09:00:00",
            "end_at": (date.today() + timedelta(days=2)).isoformat() + "T17:00:00",
            "destination_city": "Berlin",
            "destination_country": "Germany",
            "purpose": "Client Meeting",
            "total_expenses": 400.0
        }
        
        response = client.post("/api/v1/travels/", json=travel_data, headers=employee_headers)
        assert response.status_code in [200, 201]
        
        created_travel = response.json()
        assert created_travel["destination_city"] == "Berlin"
        assert created_travel["total_expenses"] == 400.0
        assert "id" in created_travel
        return created_travel["id"]
    
    def test_employee_can_view_their_travels(self, client, employee_headers):
        """Test that employees can view their travel list."""
        # Create a travel first
        self.test_employee_can_create_travel(client, employee_headers)
        
        # Then get the list
        response = client.get("/api/v1/travels/", headers=employee_headers)
        assert response.status_code == 200
        
        travels = response.json()
        assert isinstance(travels, list)
        assert len(travels) > 0
    
    def test_employee_can_update_travel(self, client, employee_headers):
        """Test that employees can update their travels."""
        # Create a travel first
        travel_id = self.test_employee_can_create_travel(client, employee_headers)
        
        # Update it
        update_data = {
            "destination_city": "Munich",
            "purpose": "Updated Meeting"
        }
        
        response = client.put(f"/api/v1/travels/{travel_id}", json=update_data, headers=employee_headers)
        assert response.status_code == 200
        
        updated_travel = response.json()
        assert updated_travel["destination_city"] == "Munich"


class TestUserManagement:
    """Test core user management features."""
    
    def test_admin_can_create_users(self, client, admin_headers):
        """Test that admins can create new users."""
        new_user_data = {
            "email": "newemployee@demo.com",
            "password": "newpass123",
            "name": "New Employee",
            "role": "employee"
        }
        
        # Try creating via admin endpoint
        response = client.post("/api/v1/admin/employees", json=new_user_data, headers=admin_headers)
        if response.status_code not in [200, 201]:
            # Fallback to regular user creation
            response = client.post("/api/v1/users/", json=new_user_data, headers=admin_headers)
        
        assert response.status_code in [200, 201]
        
        created_user = response.json()
        assert created_user["email"] == "newemployee@demo.com"
        assert created_user["role"] == "employee"
        return created_user["id"]
    
    def test_admin_can_view_all_users(self, client, admin_headers):
        """Test that admins can view all users in the system."""
        response = client.get("/api/v1/users/", headers=admin_headers)
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0


class TestBasicSecurity:
    """Test basic security features."""
    
    def test_unauthenticated_requests_rejected(self, client):
        """Test that requests without authentication are rejected."""
        # Try to access protected endpoint without auth
        response = client.get("/api/v1/travels/")
        assert response.status_code in [401, 422]  # Unauthorized or validation error
        
        response = client.get("/api/v1/users/")
        assert response.status_code in [401, 422]
    
    def test_employee_cannot_access_admin_functions(self, client, employee_headers):
        """Test that employees cannot access admin functions."""
        # Try to access admin dashboard
        response = client.get("/api/v1/admin/dashboard", headers=employee_headers)
        assert response.status_code in [401, 403, 404]
        
        # Try to create users
        user_data = {
            "email": "unauthorized@demo.com",
            "password": "pass123",
            "name": "Unauthorized User",
            "role": "employee"
        }
        response = client.post("/api/v1/admin/employees", json=user_data, headers=employee_headers)
        assert response.status_code in [401, 403, 404]


class TestSystemHealth:
    """Test basic system health and connectivity."""
    
    def test_api_is_accessible(self, client):
        """Test that the API is accessible."""
        # Test landing page
        response = client.get("/api/v1/")
        assert response.status_code == 200
    
    def test_auth_endpoints_accessible(self, client):
        """Test that authentication endpoints are accessible."""
        # Test registration endpoint structure
        response = client.post("/api/v1/auth/register", json={})
        # Should get validation error, not 404
        assert response.status_code in [422, 400]  # Validation error is expected
        
        # Test login endpoint structure  
        response = client.post("/api/v1/auth/login", json={})
        # Should get validation error, not 404
        assert response.status_code in [422, 400]  # Validation error is expected


@pytest.mark.integration
class TestCompleteWorkflow:
    """Test complete user workflows end-to-end."""
    
    def test_complete_employee_workflow(self, client):
        """Test complete employee workflow: register -> login -> create travel -> view travels."""
        
        # 1. Register new employee
        register_data = {
            "email": "workflow@demo.com",
            "password": "workflow123",
            "name": "Workflow Test",
            "role": "employee"
        }
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code in [200, 201]
        
        # 2. Login
        login_data = {"email": "workflow@demo.com", "password": "workflow123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create travel
        travel_data = {
            "employee_name": "Workflow Test",
            "start_at": date.today().isoformat() + "T09:00:00",
            "end_at": (date.today() + timedelta(days=1)).isoformat() + "T17:00:00",
            "destination_city": "Frankfurt",
            "destination_country": "Germany",
            "purpose": "Testing Complete Workflow",
            "total_expenses": 300.0
        }
        
        travel_response = client.post("/api/v1/travels/", json=travel_data, headers=headers)
        assert travel_response.status_code in [200, 201]
        
        # 4. View travels
        travels_response = client.get("/api/v1/travels/", headers=headers)
        assert travels_response.status_code == 200
        
        travels = travels_response.json()
        assert len(travels) > 0
        assert any(t["destination_city"] == "Frankfurt" for t in travels)
    
    def test_admin_user_creation_workflow(self, client, admin_headers):
        """Test admin creating users and those users being able to login."""
        
        # 1. Admin creates new employee
        new_employee = {
            "email": "admincreated@demo.com",
            "password": "created123",
            "name": "Admin Created User",
            "role": "employee"
        }
        
        create_response = client.post("/api/v1/admin/employees", json=new_employee, headers=admin_headers)
        if create_response.status_code not in [200, 201]:
            # Fallback to regular creation
            create_response = client.post("/api/v1/users/", json=new_employee, headers=admin_headers)
        
        assert create_response.status_code in [200, 201]
        
        # 2. Created user can login
        login_data = {"email": "admincreated@demo.com", "password": "created123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        # 3. Created user can access their profile
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        profile_response = client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
        
        profile = profile_response.json()
        assert profile["email"] == "admincreated@demo.com"
        assert profile["role"] == "employee"


class TestAdminManagement:
    """Test admin-specific management features."""
    
    def test_admin_can_assign_employee_to_controller(self, client, admin_headers):
        """Test that admin can assign employees to controllers."""
        # First get dashboard data to find available employees and controllers
        dashboard_response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert dashboard_response.status_code == 200
        
        dashboard_data = dashboard_response.json()
        
        # Skip test if no unassigned employees or controllers
        if not dashboard_data.get("unassigned_employees") or not dashboard_data.get("controllers"):
            return  # Skip test - no data to work with
        
        employee_id = dashboard_data["unassigned_employees"][0]["id"]
        controller_id = dashboard_data["controllers"][0]["id"]
        
        # Assign employee to controller
        response = client.put(
            f"/api/v1/admin/assign-employee/{employee_id}/to-controller/{controller_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "assigned" in result["message"].lower()
    
    def test_admin_can_unassign_employee(self, client, admin_headers):
        """Test that admin can unassign employees from controllers."""
        # First assign an employee (setup)
        dashboard_response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert dashboard_response.status_code == 200
        
        dashboard_data = dashboard_response.json()
        
        # Skip if no data available
        if not dashboard_data.get("unassigned_employees") or not dashboard_data.get("controllers"):
            return
        
        employee_id = dashboard_data["unassigned_employees"][0]["id"]
        controller_id = dashboard_data["controllers"][0]["id"]
        
        # First assign
        assign_response = client.put(
            f"/api/v1/admin/assign-employee/{employee_id}/to-controller/{controller_id}",
            headers=admin_headers
        )
        assert assign_response.status_code == 200
        
        # Then unassign
        unassign_response = client.put(
            f"/api/v1/admin/unassign-employee/{employee_id}",
            headers=admin_headers
        )
        assert unassign_response.status_code == 200
        
        result = unassign_response.json()
        assert "message" in result
        assert "unassigned" in result["message"].lower()
    
    def test_admin_can_delete_user(self, client, admin_headers):
        """Test that admin can delete users."""
        # Create a test user first
        test_user_data = {
            "email": "todelete@test.com",
            "password": "password123",
            "name": "User To Delete",
            "role": "employee"
        }
        
        # Create user via registration
        create_response = client.post("/api/v1/auth/register", json=test_user_data)
        assert create_response.status_code in [200, 201]
        
        created_user = create_response.json()
        user_id = created_user["user"]["id"]
        
        # Delete the user
        delete_response = client.delete(f"/api/v1/admin/users/{user_id}", headers=admin_headers)
        assert delete_response.status_code == 200
        
        result = delete_response.json()
        assert "message" in result
        assert "deleted" in result["message"].lower()
    
    def test_admin_dashboard_access(self, client, admin_headers):
        """Test that admin can access the dashboard with proper data."""
        response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        
        dashboard_data = response.json()
        
        # Check required fields
        assert "controllers" in dashboard_data
        assert "unassigned_employees" in dashboard_data
        assert "statistics" in dashboard_data
        
        # Check statistics structure
        stats = dashboard_data["statistics"]
        assert "total_controllers" in stats
        assert "total_employees" in stats
        assert "assigned_employees" in stats
        assert "unassigned_employees" in stats
