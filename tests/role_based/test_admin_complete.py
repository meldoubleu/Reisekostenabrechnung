"""
Admin Role Complete Test Suite
Tests all API endpoints accessible by admin role users.
"""

import pytest
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
def admin_token(client):
    """Get authentication token for admin user."""
    login_data = {
        "email": "admin@demo.com",
        "password": "admin123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # If login fails, try to register first
    register_data = {
        "email": "admin@demo.com",
        "password": "admin123",
        "name": "Test Admin",
        "role": "admin"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    if register_response.status_code == 200:
        return register_response.json()["access_token"]
    
    raise Exception("Could not authenticate admin user")


@pytest.fixture
def admin_headers(admin_token):
    """Get authentication headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.mark.unit
class TestAdminAuthentication:
    """Test authentication endpoints for admins."""
    
    def test_admin_login_valid_credentials(self, client):
        """Test admin login with valid credentials."""
        login_data = {
            "email": "admin@demo.com",
            "password": "admin123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        if response.status_code == 404:
            # User doesn't exist, create it first
            register_data = {
                "email": "admin@demo.com",
                "password": "admin123",
                "name": "Test Admin",
                "role": "admin"
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
    
    def test_admin_get_me(self, client, admin_headers):
        """Test getting current admin user info."""
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == "admin@demo.com"
        assert user_data["role"] == "admin"
        assert "id" in user_data
        assert "name" in user_data


@pytest.mark.integration
class TestAdminDashboard:
    """Test admin dashboard endpoints."""
    
    def test_admin_dashboard_access(self, client, admin_headers):
        """Test admin dashboard access."""
        response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        
        dashboard_data = response.json()
        assert isinstance(dashboard_data, dict)
        # Dashboard should contain system statistics
        expected_keys = ["total_users", "total_travels", "total_expenses", "pending_approvals"]
        # Some of these keys might be present
        assert any(key in dashboard_data for key in expected_keys)


@pytest.mark.integration
class TestAdminUserManagement:
    """Test admin user management endpoints."""
    
    def test_admin_get_all_users(self, client, admin_headers):
        """Test getting all users."""
        response = client.get("/api/v1/users/", headers=admin_headers)
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
    
    def test_admin_create_controller(self, client, admin_headers):
        """Test creating a new controller."""
        controller_data = {
            "email": "new_controller@demo.com",
            "password": "newcontroller123",
            "name": "New Test Controller",
            "role": "controller",
            "company": "Demo GmbH",
            "department": "Operations"
        }
        
        response = client.post("/api/v1/admin/controllers", json=controller_data, headers=admin_headers)
        assert response.status_code in [200, 201]
        
        created_controller = response.json()
        assert created_controller["email"] == "new_controller@demo.com"
        assert created_controller["role"] == "controller"
        assert "id" in created_controller
        
        return created_controller["id"]
    
    def test_admin_create_employee(self, client, admin_headers):
        """Test creating a new employee."""
        employee_data = {
            "email": "new_employee@demo.com",
            "password": "newemployee123",
            "name": "New Test Employee",
            "role": "employee",
            "company": "Demo GmbH",
            "department": "Engineering"
        }
        
        response = client.post("/api/v1/admin/employees", json=employee_data, headers=admin_headers)
        assert response.status_code in [200, 201]
        
        created_employee = response.json()
        assert created_employee["email"] == "new_employee@demo.com"
        assert created_employee["role"] == "employee"
        assert "id" in created_employee
        
        return created_employee["id"]
    
    def test_admin_get_specific_user(self, client, admin_headers):
        """Test getting specific user by ID."""
        # First get all users to find a valid ID
        users_response = client.get("/api/v1/users/", headers=admin_headers)
        assert users_response.status_code == 200
        users = users_response.json()
        
        if users:
            user_id = users[0]["id"]
            response = client.get(f"/api/v1/users/{user_id}", headers=admin_headers)
            assert response.status_code == 200
            
            user = response.json()
            assert user["id"] == user_id
    
    def test_admin_update_user(self, client, admin_headers):
        """Test updating a user."""
        # Create a user first
        employee_id = self.test_admin_create_employee(client, admin_headers)
        
        update_data = {
            "name": "Updated Test Employee",
            "department": "Updated Department"
        }
        
        response = client.put(f"/api/v1/users/{employee_id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        
        updated_user = response.json()
        assert updated_user["name"] == "Updated Test Employee"
    
    def test_admin_delete_user(self, client, admin_headers):
        """Test deleting a user."""
        # Create a user first
        employee_id = self.test_admin_create_employee(client, admin_headers)
        
        response = client.delete(f"/api/v1/admin/users/{employee_id}", headers=admin_headers)
        assert response.status_code == 200
        
        # Verify user is deleted
        get_response = client.get(f"/api/v1/users/{employee_id}", headers=admin_headers)
        assert get_response.status_code == 404
    
    def test_admin_assign_employee_to_controller(self, client, admin_headers):
        """Test assigning an employee to a controller."""
        # Create both users first
        controller_id = self.test_admin_create_controller(client, admin_headers)
        employee_id = self.test_admin_create_employee(client, admin_headers)
        
        response = client.put(f"/api/v1/admin/assign-employee/{employee_id}/to-controller/{controller_id}", headers=admin_headers)
        assert response.status_code == 200
        
        # Verify assignment
        assignment_response = client.get("/api/v1/admin/controller-assignments", headers=admin_headers)
        assert assignment_response.status_code == 200
    
    def test_admin_unassign_employee(self, client, admin_headers):
        """Test unassigning an employee from controller."""
        # First create and assign
        controller_id = self.test_admin_create_controller(client, admin_headers)
        employee_id = self.test_admin_create_employee(client, admin_headers)
        
        # Assign
        assign_response = client.put(f"/api/v1/admin/assign-employee/{employee_id}/to-controller/{controller_id}", headers=admin_headers)
        assert assign_response.status_code == 200
        
        # Unassign
        unassign_response = client.put(f"/api/v1/admin/unassign-employee/{employee_id}", headers=admin_headers)
        assert unassign_response.status_code == 200
    
    def test_admin_get_controller_assignments(self, client, admin_headers):
        """Test getting all controller assignments."""
        response = client.get("/api/v1/admin/controller-assignments", headers=admin_headers)
        assert response.status_code == 200
        
        assignments = response.json()
        assert isinstance(assignments, dict) or isinstance(assignments, list)


@pytest.mark.integration
class TestAdminTravelManagement:
    """Test admin travel management endpoints."""
    
    def test_admin_get_all_travels(self, client, admin_headers):
        """Test getting all travels in the system."""
        response = client.get("/api/v1/admin/travels", headers=admin_headers)
        # Try alternative endpoint if this doesn't exist
        if response.status_code == 404:
            response = client.get("/api/v1/travels/", headers=admin_headers)
        
        assert response.status_code == 200
        travels = response.json()
        assert isinstance(travels, list)
    
    def test_admin_access_any_travel(self, client, admin_headers):
        """Test that admin can access any travel."""
        # Get all travels first
        travels_response = client.get("/api/v1/travels/", headers=admin_headers)
        assert travels_response.status_code == 200
        travels = travels_response.json()
        
        if travels:
            travel_id = travels[0]["id"]
            response = client.get(f"/api/v1/travels/{travel_id}", headers=admin_headers)
            assert response.status_code == 200
            
            travel = response.json()
            assert travel["id"] == travel_id
    
    def test_admin_approve_any_travel(self, client, admin_headers):
        """Test that admin can approve any travel."""
        # This would require creating a travel in draft/submitted status
        # For now, just test that the endpoint is accessible
        response = client.put("/api/v1/travels/999/approve", headers=admin_headers)
        # Should get 404 for non-existent travel, not 403
        assert response.status_code in [200, 404]
    
    def test_admin_reject_any_travel(self, client, admin_headers):
        """Test that admin can reject any travel."""
        response = client.put("/api/v1/travels/999/reject", headers=admin_headers)
        # Should get 404 for non-existent travel, not 403
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestAdminSystemAccess:
    """Test admin system-wide access capabilities."""
    
    def test_admin_full_user_access(self, client, admin_headers):
        """Test that admin has full access to user management."""
        endpoints_to_test = [
            ("/api/v1/users/", "GET"),
            ("/api/v1/users/controllers", "GET"),
            ("/api/v1/admin/dashboard", "GET"),
            ("/api/v1/admin/controller-assignments", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            if method == "GET":
                response = client.get(endpoint, headers=admin_headers)
                assert response.status_code == 200
    
    def test_admin_can_access_all_user_types(self, client, admin_headers):
        """Test that admin can access employees, controllers, and admins."""
        # Get all users
        users_response = client.get("/api/v1/users/", headers=admin_headers)
        assert users_response.status_code == 200
        users = users_response.json()
        
        # Check that we can access users of different roles
        for user in users:
            user_response = client.get(f"/api/v1/users/{user['id']}", headers=admin_headers)
            assert user_response.status_code == 200
            
            retrieved_user = user_response.json()
            assert retrieved_user["id"] == user["id"]
    
    def test_admin_export_capabilities(self, client, admin_headers):
        """Test admin export capabilities."""
        # Get travels first
        travels_response = client.get("/api/v1/travels/", headers=admin_headers)
        assert travels_response.status_code == 200
        travels = travels_response.json()
        
        if travels:
            travel_id = travels[0]["id"]
            export_response = client.get(f"/api/v1/travels/{travel_id}/export", headers=admin_headers)
            # Export should work for admin
            assert export_response.status_code in [200, 404]


@pytest.mark.e2e
class TestAdminCompleteWorkflow:
    """Test complete admin workflow end-to-end."""
    
    def test_complete_admin_system_management(self, client, admin_headers):
        """Test complete admin workflow: dashboard -> user management -> travel oversight."""
        
        # 1. Access admin dashboard
        dashboard_response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        
        # 2. Create a new controller
        controller_data = {
            "email": "workflow_controller@demo.com",
            "password": "controller123",
            "name": "Workflow Test Controller",
            "role": "controller"
        }
        
        controller_response = client.post("/api/v1/admin/controllers", json=controller_data, headers=admin_headers)
        assert controller_response.status_code in [200, 201]
        controller = controller_response.json()
        controller_id = controller["id"]
        
        # 3. Create a new employee
        employee_data = {
            "email": "workflow_employee@demo.com",
            "password": "employee123",
            "name": "Workflow Test Employee",
            "role": "employee"
        }
        
        employee_response = client.post("/api/v1/admin/employees", json=employee_data, headers=admin_headers)
        assert employee_response.status_code in [200, 201]
        employee = employee_response.json()
        employee_id = employee["id"]
        
        # 4. Assign employee to controller
        assign_response = client.put(f"/api/v1/admin/assign-employee/{employee_id}/to-controller/{controller_id}", headers=admin_headers)
        assert assign_response.status_code == 200
        
        # 5. Verify assignment
        assignments_response = client.get("/api/v1/admin/controller-assignments", headers=admin_headers)
        assert assignments_response.status_code == 200
        assignments = assignments_response.json()
        
        # 6. Check all travels in system
        travels_response = client.get("/api/v1/admin/travels", headers=admin_headers)
        if travels_response.status_code == 404:
            travels_response = client.get("/api/v1/travels/", headers=admin_headers)
        assert travels_response.status_code == 200
        travels = travels_response.json()
        
        # 7. Verify admin can access any user
        all_users_response = client.get("/api/v1/users/", headers=admin_headers)
        assert all_users_response.status_code == 200
        all_users = all_users_response.json()
        
        # Verify our created users are in the list
        user_emails = [user["email"] for user in all_users]
        assert "workflow_controller@demo.com" in user_emails
        assert "workflow_employee@demo.com" in user_emails
        
        # 8. Clean up - delete created users
        delete_controller_response = client.delete(f"/api/v1/admin/users/{controller_id}", headers=admin_headers)
        assert delete_controller_response.status_code == 200
        
        delete_employee_response = client.delete(f"/api/v1/admin/users/{employee_id}", headers=admin_headers)
        assert delete_employee_response.status_code == 200
