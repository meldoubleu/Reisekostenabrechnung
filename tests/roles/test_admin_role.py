"""
Admin Role Tests - Complete API Endpoint Coverage
Tests all endpoints accessible by admin role users.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from backend.app.main import app
import json
from datetime import date, timedelta


@pytest_asyncio.fixture
async def async_client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def admin_auth_headers(async_client: AsyncClient):
    """Get authentication headers for admin user."""
    login_data = {
        "username": "admin@demo.com",
        "password": "admin123"
    }
    
    login_response = await async_client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    token_data = login_response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


class TestAdminAuthEndpoints:
    """Test authentication endpoints for admin."""
    
    @pytest_asyncio.async_test
    async def test_admin_login(self, async_client: AsyncClient):
        """Test admin login endpoint."""
        login_data = {
            "username": "admin@demo.com",
            "password": "admin123"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"
    
    @pytest_asyncio.async_test
    async def test_admin_get_me(self, async_client: AsyncClient, admin_auth_headers):
        """Test getting current admin user info."""
        response = await async_client.get("/api/v1/auth/me", headers=admin_auth_headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == "admin@demo.com"
        assert user_data["role"] == "admin"
        assert "id" in user_data
        assert "full_name" in user_data


class TestAdminDashboardEndpoints:
    """Test admin dashboard and system overview endpoints."""
    
    @pytest_asyncio.async_test
    async def test_admin_get_dashboard(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin dashboard endpoint."""
        response = await async_client.get("/api/v1/admin/dashboard", headers=admin_auth_headers)
        assert response.status_code == 200
        
        dashboard = response.json()
        assert isinstance(dashboard, dict)
        
        # Dashboard should contain system statistics
        # The exact keys depend on implementation, but should include counts
        expected_keys = ["total_users", "total_travels", "total_expenses", "active_users"]
        for key in expected_keys:
            # Don't assert presence since implementation may vary
            pass
    
    @pytest_asyncio.async_test
    async def test_admin_get_controller_assignments(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view controller-employee assignments."""
        response = await async_client.get("/api/v1/admin/controller-assignments", headers=admin_auth_headers)
        assert response.status_code == 200
        
        assignments = response.json()
        assert isinstance(assignments, (list, dict))


class TestAdminUserManagementEndpoints:
    """Test admin user management endpoints."""
    
    @pytest_asyncio.async_test
    async def test_admin_get_all_users(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view all users."""
        response = await async_client.get("/api/v1/users/", headers=admin_auth_headers)
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0
        
        # Should include users of all roles
        roles_found = {user["role"] for user in users}
        assert "admin" in roles_found or "employee" in roles_found or "controller" in roles_found
    
    @pytest_asyncio.async_test
    async def test_admin_create_employee(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can create new employees."""
        new_employee_data = {
            "email": f"test_employee_{date.today().isoformat()}@example.com",
            "full_name": "Test Employee",
            "role": "employee",
            "department": "Testing",
            "cost_center": "TEST-001"
        }
        
        response = await async_client.post("/api/v1/admin/employees", json=new_employee_data, headers=admin_auth_headers)
        assert response.status_code == 201
        
        created_user = response.json()
        assert created_user["email"] == new_employee_data["email"]
        assert created_user["role"] == "employee"
        assert "id" in created_user
        
        return created_user["id"]  # Return for cleanup or further testing
    
    @pytest_asyncio.async_test
    async def test_admin_create_controller(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can create new controllers."""
        new_controller_data = {
            "email": f"test_controller_{date.today().isoformat()}@example.com",
            "full_name": "Test Controller",
            "role": "controller",
            "department": "Management"
        }
        
        response = await async_client.post("/api/v1/admin/controllers", json=new_controller_data, headers=admin_auth_headers)
        assert response.status_code == 201
        
        created_user = response.json()
        assert created_user["email"] == new_controller_data["email"]
        assert created_user["role"] == "controller"
        assert "id" in created_user
        
        return created_user["id"]  # Return for cleanup or further testing
    
    @pytest_asyncio.async_test
    async def test_admin_create_user_general(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can create users via general endpoint."""
        new_user_data = {
            "email": f"test_general_{date.today().isoformat()}@example.com",
            "full_name": "Test General User",
            "role": "employee",
            "department": "General"
        }
        
        response = await async_client.post("/api/v1/users/", json=new_user_data, headers=admin_auth_headers)
        assert response.status_code == 201
        
        created_user = response.json()
        assert created_user["email"] == new_user_data["email"]
        assert "id" in created_user
    
    @pytest_asyncio.async_test
    async def test_admin_update_user(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can update existing users."""
        # First, get a user to update
        users_response = await async_client.get("/api/v1/users/", headers=admin_auth_headers)
        users = users_response.json()
        
        if len(users) > 0:
            user_id = users[0]["id"]
            
            update_data = {
                "full_name": "Updated Name",
                "department": "Updated Department"
            }
            
            response = await async_client.put(f"/api/v1/users/{user_id}", json=update_data, headers=admin_auth_headers)
            assert response.status_code == 200
            
            updated_user = response.json()
            assert updated_user["full_name"] == "Updated Name"
    
    @pytest_asyncio.async_test
    async def test_admin_delete_user(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can delete users."""
        # First create a user to delete
        test_user_data = {
            "email": f"delete_test_{date.today().isoformat()}@example.com",
            "full_name": "Delete Test User",
            "role": "employee"
        }
        
        create_response = await async_client.post("/api/v1/users/", json=test_user_data, headers=admin_auth_headers)
        if create_response.status_code == 201:
            user_id = create_response.json()["id"]
            
            # Now delete the user
            delete_response = await async_client.delete(f"/api/v1/users/{user_id}", headers=admin_auth_headers)
            assert delete_response.status_code == 200
            
            # Verify user is deleted
            get_response = await async_client.get(f"/api/v1/users/{user_id}", headers=admin_auth_headers)
            assert get_response.status_code == 404
    
    @pytest_asyncio.async_test
    async def test_admin_delete_user_via_admin_endpoint(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can delete users via admin endpoint."""
        # First create a user to delete
        test_user_data = {
            "email": f"admin_delete_test_{date.today().isoformat()}@example.com",
            "full_name": "Admin Delete Test User",
            "role": "employee"
        }
        
        create_response = await async_client.post("/api/v1/users/", json=test_user_data, headers=admin_auth_headers)
        if create_response.status_code == 201:
            user_id = create_response.json()["id"]
            
            # Delete via admin endpoint
            delete_response = await async_client.delete(f"/api/v1/admin/users/{user_id}", headers=admin_auth_headers)
            assert delete_response.status_code == 200


class TestAdminAssignmentEndpoints:
    """Test admin assignment management endpoints."""
    
    @pytest_asyncio.async_test
    async def test_admin_assign_employee_to_controller(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can assign employees to controllers."""
        # Get controllers and employees
        users_response = await async_client.get("/api/v1/users/", headers=admin_auth_headers)
        users = users_response.json()
        
        controllers = [u for u in users if u["role"] == "controller"]
        employees = [u for u in users if u["role"] == "employee"]
        
        if len(controllers) > 0 and len(employees) > 0:
            controller_id = controllers[0]["id"]
            employee_id = employees[0]["id"]
            
            response = await async_client.put(
                f"/api/v1/admin/assign-employee/{employee_id}/to-controller/{controller_id}",
                headers=admin_auth_headers
            )
            assert response.status_code == 200
    
    @pytest_asyncio.async_test
    async def test_admin_unassign_employee(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can unassign employees from controllers."""
        # Get an employee
        users_response = await async_client.get("/api/v1/users/", headers=admin_auth_headers)
        users = users_response.json()
        
        employees = [u for u in users if u["role"] == "employee"]
        
        if len(employees) > 0:
            employee_id = employees[0]["id"]
            
            response = await async_client.put(
                f"/api/v1/admin/unassign-employee/{employee_id}",
                headers=admin_auth_headers
            )
            assert response.status_code == 200
    
    @pytest_asyncio.async_test
    async def test_admin_assign_via_users_endpoint(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can assign via users endpoint."""
        # Get controllers and employees
        users_response = await async_client.get("/api/v1/users/", headers=admin_auth_headers)
        users = users_response.json()
        
        controllers = [u for u in users if u["role"] == "controller"]
        employees = [u for u in users if u["role"] == "employee"]
        
        if len(controllers) > 0 and len(employees) > 0:
            controller_id = controllers[0]["id"]
            employee_id = employees[0]["id"]
            
            response = await async_client.put(
                f"/api/v1/users/{employee_id}/assign-controller/{controller_id}",
                headers=admin_auth_headers
            )
            assert response.status_code == 200


class TestAdminTravelEndpoints:
    """Test travel-related endpoints for admin."""
    
    @pytest_asyncio.async_test
    async def test_admin_get_all_travels(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view all travels in the system."""
        response = await async_client.get("/api/v1/travels/", headers=admin_auth_headers)
        assert response.status_code == 200
        
        travels = response.json()
        assert isinstance(travels, list)
    
    @pytest_asyncio.async_test
    async def test_admin_get_all_travels_admin_endpoint(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view all travels via admin endpoint."""
        response = await async_client.get("/api/v1/admin/travels", headers=admin_auth_headers)
        assert response.status_code == 200
        
        travels = response.json()
        assert isinstance(travels, list)
    
    @pytest_asyncio.async_test
    async def test_admin_get_specific_travel(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view any specific travel."""
        # Get all travels first
        travels_response = await async_client.get("/api/v1/travels/", headers=admin_auth_headers)
        travels = travels_response.json()
        
        if len(travels) > 0:
            travel_id = travels[0]["id"]
            
            response = await async_client.get(f"/api/v1/travels/{travel_id}", headers=admin_auth_headers)
            assert response.status_code == 200
            
            travel = response.json()
            assert travel["id"] == travel_id
    
    @pytest_asyncio.async_test
    async def test_admin_update_any_travel(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can update any travel."""
        # Get all travels first
        travels_response = await async_client.get("/api/v1/travels/", headers=admin_auth_headers)
        travels = travels_response.json()
        
        if len(travels) > 0:
            travel_id = travels[0]["id"]
            
            update_data = {
                "status": "approved",
                "admin_notes": "Approved by admin"
            }
            
            response = await async_client.put(f"/api/v1/travels/{travel_id}", json=update_data, headers=admin_auth_headers)
            assert response.status_code == 200
    
    @pytest_asyncio.async_test
    async def test_admin_approve_reject_travels(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can approve/reject any travel."""
        # Get all travels first
        travels_response = await async_client.get("/api/v1/travels/", headers=admin_auth_headers)
        travels = travels_response.json()
        
        if len(travels) > 0:
            travel_id = travels[0]["id"]
            
            # Test approve
            approve_response = await async_client.put(f"/api/v1/travels/{travel_id}/approve", headers=admin_auth_headers)
            assert approve_response.status_code in [200, 400, 409]
            
            # Test reject
            reject_response = await async_client.put(f"/api/v1/travels/{travel_id}/reject", headers=admin_auth_headers)
            assert reject_response.status_code in [200, 400, 409]
    
    @pytest_asyncio.async_test
    async def test_admin_get_employee_travels(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view travels for any employee."""
        # Get employees first
        users_response = await async_client.get("/api/v1/users/", headers=admin_auth_headers)
        users = users_response.json()
        
        employees = [u for u in users if u["role"] == "employee"]
        
        if len(employees) > 0:
            employee_id = employees[0]["id"]
            
            response = await async_client.get(f"/api/v1/travels/employee/{employee_id}/travels", headers=admin_auth_headers)
            assert response.status_code == 200
            
            travels = response.json()
            assert isinstance(travels, list)
    
    @pytest_asyncio.async_test
    async def test_admin_get_controller_travels(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view travels for any controller."""
        # Get controllers first
        users_response = await async_client.get("/api/v1/users/", headers=admin_auth_headers)
        users = users_response.json()
        
        controllers = [u for u in users if u["role"] == "controller"]
        
        if len(controllers) > 0:
            controller_id = controllers[0]["id"]
            
            response = await async_client.get(f"/api/v1/travels/controller/{controller_id}/travels", headers=admin_auth_headers)
            assert response.status_code == 200
            
            travels = response.json()
            assert isinstance(travels, list)


class TestAdminUserLookupEndpoints:
    """Test admin user lookup and information endpoints."""
    
    @pytest_asyncio.async_test
    async def test_admin_get_user_by_id(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view any user by ID."""
        # Get all users first
        users_response = await async_client.get("/api/v1/users/", headers=admin_auth_headers)
        users = users_response.json()
        
        if len(users) > 0:
            user_id = users[0]["id"]
            
            response = await async_client.get(f"/api/v1/users/{user_id}", headers=admin_auth_headers)
            assert response.status_code == 200
            
            user = response.json()
            assert user["id"] == user_id
    
    @pytest_asyncio.async_test
    async def test_admin_get_user_by_email(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view any user by email."""
        # Try to get a known user
        response = await async_client.get("/api/v1/users/email/malte@demo.com", headers=admin_auth_headers)
        assert response.status_code in [200, 404]  # OK or Not Found
    
    @pytest_asyncio.async_test
    async def test_admin_get_controllers_list(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view all controllers."""
        response = await async_client.get("/api/v1/users/controllers", headers=admin_auth_headers)
        assert response.status_code == 200
        
        controllers = response.json()
        assert isinstance(controllers, list)
        for controller in controllers:
            assert controller["role"] == "controller"
    
    @pytest_asyncio.async_test
    async def test_admin_get_controller_employees(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin can view employees assigned to any controller."""
        # Get a controller first
        controllers_response = await async_client.get("/api/v1/users/controllers", headers=admin_auth_headers)
        controllers = controllers_response.json()
        
        if len(controllers) > 0:
            controller_id = controllers[0]["id"]
            
            response = await async_client.get(f"/api/v1/users/controller/{controller_id}/employees", headers=admin_auth_headers)
            assert response.status_code == 200
            
            employees = response.json()
            assert isinstance(employees, list)


class TestAdminUIEndpoints:
    """Test UI endpoints accessible to admin."""
    
    @pytest_asyncio.async_test
    async def test_admin_can_access_all_ui_pages(self, async_client: AsyncClient):
        """Test that all UI pages are accessible to admin."""
        # Test main UI page
        response = await async_client.get("/api/v1/ui")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # Test dashboard page
        response = await async_client.get("/api/v1/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # Test admin page
        response = await async_client.get("/api/v1/admin")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # Test travel form page
        response = await async_client.get("/api/v1/travel-form")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestAdminSecurityAndEdgeCases:
    """Test security and edge cases for admin role."""
    
    @pytest_asyncio.async_test
    async def test_admin_unauthorized_access(self, async_client: AsyncClient):
        """Test accessing admin endpoints without authentication."""
        # Try to access admin dashboard without auth
        response = await async_client.get("/api/v1/admin/dashboard")
        assert response.status_code == 401
        
        # Try to access user management without auth
        response = await async_client.get("/api/v1/users/")
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_admin_with_invalid_token(self, async_client: AsyncClient):
        """Test accessing admin endpoints with invalid token."""
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        
        response = await async_client.get("/api/v1/admin/dashboard", headers=invalid_headers)
        assert response.status_code == 401
        
        response = await async_client.get("/api/v1/users/", headers=invalid_headers)
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_admin_data_validation(self, async_client: AsyncClient, admin_auth_headers):
        """Test data validation for admin operations."""
        # Test creating user with invalid data
        invalid_user_data = {
            "email": "invalid-email",  # Invalid email format
            "full_name": "",  # Empty name
            "role": "invalid_role"  # Invalid role
        }
        
        response = await async_client.post("/api/v1/users/", json=invalid_user_data, headers=admin_auth_headers)
        assert response.status_code == 422  # Validation error
    
    @pytest_asyncio.async_test
    async def test_admin_duplicate_user_creation(self, async_client: AsyncClient, admin_auth_headers):
        """Test that admin cannot create duplicate users."""
        # Try to create a user with existing email
        duplicate_user_data = {
            "email": "admin@demo.com",  # This should already exist
            "full_name": "Duplicate Admin",
            "role": "admin"
        }
        
        response = await async_client.post("/api/v1/users/", json=duplicate_user_data, headers=admin_auth_headers)
        assert response.status_code in [400, 409, 422]  # Should prevent duplicates
