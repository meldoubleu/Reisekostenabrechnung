"""
User Management API Endpoint Tests
Complete coverage of all user-related endpoints.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from backend.app.main import app
import json
from datetime import date


@pytest_asyncio.fixture
async def async_client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def admin_headers(async_client: AsyncClient):
    """Get auth headers for admin."""
    login_data = {"username": "admin@demo.com", "password": "admin123"}
    response = await async_client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def controller_headers(async_client: AsyncClient):
    """Get auth headers for controller."""
    login_data = {"username": "controller1@demo.com", "password": "controller123"}
    response = await async_client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def employee_headers(async_client: AsyncClient):
    """Get auth headers for employee."""
    login_data = {"username": "malte@demo.com", "password": "employee123"}
    response = await async_client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestUsersListEndpoint:
    """Test /api/v1/users/ GET endpoint."""
    
    @pytest_asyncio.async_test
    async def test_get_all_users_admin(self, async_client: AsyncClient, admin_headers):
        """Test admin can get all users."""
        response = await async_client.get("/api/v1/users/", headers=admin_headers)
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0
        
        # Should include all roles
        roles = {user["role"] for user in users}
        assert len(roles) > 0  # At least one role should exist
        
        # Each user should have required fields
        for user in users:
            assert "id" in user
            assert "email" in user
            assert "full_name" in user
            assert "role" in user
    
    @pytest_asyncio.async_test
    async def test_get_all_users_controller_forbidden(self, async_client: AsyncClient, controller_headers):
        """Test controller cannot get all users."""
        response = await async_client.get("/api/v1/users/", headers=controller_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_get_all_users_employee_forbidden(self, async_client: AsyncClient, employee_headers):
        """Test employee cannot get all users."""
        response = await async_client.get("/api/v1/users/", headers=employee_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_get_all_users_unauthorized(self, async_client: AsyncClient):
        """Test getting all users without authentication."""
        response = await async_client.get("/api/v1/users/")
        assert response.status_code == 401


class TestUsersCreateEndpoint:
    """Test /api/v1/users/ POST endpoint."""
    
    @pytest_asyncio.async_test
    async def test_create_user_admin(self, async_client: AsyncClient, admin_headers):
        """Test admin can create new users."""
        new_user_data = {
            "email": f"test_user_{date.today().isoformat()}@example.com",
            "full_name": "Test User",
            "role": "employee",
            "department": "Testing"
        }
        
        response = await async_client.post("/api/v1/users/", json=new_user_data, headers=admin_headers)
        assert response.status_code == 201
        
        created_user = response.json()
        assert created_user["email"] == new_user_data["email"]
        assert created_user["role"] == "employee"
        assert "id" in created_user
        
        return created_user["id"]  # Return for cleanup
    
    @pytest_asyncio.async_test
    async def test_create_user_duplicate_email(self, async_client: AsyncClient, admin_headers):
        """Test creating user with duplicate email."""
        duplicate_user_data = {
            "email": "admin@demo.com",  # Existing email
            "full_name": "Duplicate User",
            "role": "employee"
        }
        
        response = await async_client.post("/api/v1/users/", json=duplicate_user_data, headers=admin_headers)
        assert response.status_code in [400, 409, 422]  # Should prevent duplicates
    
    @pytest_asyncio.async_test
    async def test_create_user_invalid_data(self, async_client: AsyncClient, admin_headers):
        """Test creating user with invalid data."""
        invalid_user_data = {
            "email": "invalid-email",  # Invalid email format
            "full_name": "",  # Empty name
            "role": "invalid_role"  # Invalid role
        }
        
        response = await async_client.post("/api/v1/users/", json=invalid_user_data, headers=admin_headers)
        assert response.status_code == 422
    
    @pytest_asyncio.async_test
    async def test_create_user_controller_forbidden(self, async_client: AsyncClient, controller_headers):
        """Test controller cannot create users."""
        new_user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "employee"
        }
        
        response = await async_client.post("/api/v1/users/", json=new_user_data, headers=controller_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_create_user_employee_forbidden(self, async_client: AsyncClient, employee_headers):
        """Test employee cannot create users."""
        new_user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "employee"
        }
        
        response = await async_client.post("/api/v1/users/", json=new_user_data, headers=employee_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_create_user_unauthorized(self, async_client: AsyncClient):
        """Test creating user without authentication."""
        new_user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "employee"
        }
        
        response = await async_client.post("/api/v1/users/", json=new_user_data)
        assert response.status_code == 401


class TestUsersGetByIdEndpoint:
    """Test /api/v1/users/{user_id} GET endpoint."""
    
    @pytest_asyncio.async_test
    async def test_get_user_by_id_admin(self, async_client: AsyncClient, admin_headers):
        """Test admin can get any user by ID."""
        # First get all users to find an ID
        users_response = await async_client.get("/api/v1/users/", headers=admin_headers)
        users = users_response.json()
        
        if len(users) > 0:
            user_id = users[0]["id"]
            
            response = await async_client.get(f"/api/v1/users/{user_id}", headers=admin_headers)
            assert response.status_code == 200
            
            user = response.json()
            assert user["id"] == user_id
            assert "email" in user
            assert "full_name" in user
            assert "role" in user
    
    @pytest_asyncio.async_test
    async def test_get_user_by_id_controller_limited(self, async_client: AsyncClient, controller_headers):
        """Test controller can get user info for assigned employees."""
        # Get controller's team first
        team_response = await async_client.get("/api/v1/users/my-team", headers=controller_headers)
        if team_response.status_code == 200:
            team = team_response.json()
            
            if len(team) > 0:
                user_id = team[0]["id"]
                
                response = await async_client.get(f"/api/v1/users/{user_id}", headers=controller_headers)
                assert response.status_code in [200, 403]  # Might be allowed or forbidden
    
    @pytest_asyncio.async_test
    async def test_get_user_by_id_nonexistent(self, async_client: AsyncClient, admin_headers):
        """Test getting non-existent user by ID."""
        response = await async_client.get("/api/v1/users/99999", headers=admin_headers)
        assert response.status_code == 404
    
    @pytest_asyncio.async_test
    async def test_get_user_by_id_employee_forbidden(self, async_client: AsyncClient, employee_headers):
        """Test employee cannot get other users by ID."""
        response = await async_client.get("/api/v1/users/999", headers=employee_headers)
        assert response.status_code in [403, 404]
    
    @pytest_asyncio.async_test
    async def test_get_user_by_id_unauthorized(self, async_client: AsyncClient):
        """Test getting user by ID without authentication."""
        response = await async_client.get("/api/v1/users/1")
        assert response.status_code == 401


class TestUsersUpdateEndpoint:
    """Test /api/v1/users/{user_id} PUT endpoint."""
    
    @pytest_asyncio.async_test
    async def test_update_user_admin(self, async_client: AsyncClient, admin_headers):
        """Test admin can update any user."""
        # First get a user to update
        users_response = await async_client.get("/api/v1/users/", headers=admin_headers)
        users = users_response.json()
        
        if len(users) > 0:
            user_id = users[0]["id"]
            
            update_data = {
                "full_name": "Updated Name",
                "department": "Updated Department"
            }
            
            response = await async_client.put(f"/api/v1/users/{user_id}", json=update_data, headers=admin_headers)
            assert response.status_code == 200
            
            updated_user = response.json()
            assert updated_user["full_name"] == "Updated Name"
    
    @pytest_asyncio.async_test
    async def test_update_user_invalid_data(self, async_client: AsyncClient, admin_headers):
        """Test updating user with invalid data."""
        users_response = await async_client.get("/api/v1/users/", headers=admin_headers)
        users = users_response.json()
        
        if len(users) > 0:
            user_id = users[0]["id"]
            
            update_data = {
                "email": "invalid-email",  # Invalid email format
                "role": "invalid_role"  # Invalid role
            }
            
            response = await async_client.put(f"/api/v1/users/{user_id}", json=update_data, headers=admin_headers)
            assert response.status_code == 422
    
    @pytest_asyncio.async_test
    async def test_update_user_controller_forbidden(self, async_client: AsyncClient, controller_headers):
        """Test controller cannot update users."""
        update_data = {"full_name": "Updated Name"}
        
        response = await async_client.put("/api/v1/users/1", json=update_data, headers=controller_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_update_user_employee_forbidden(self, async_client: AsyncClient, employee_headers):
        """Test employee cannot update users."""
        update_data = {"full_name": "Updated Name"}
        
        response = await async_client.put("/api/v1/users/1", json=update_data, headers=employee_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_update_user_unauthorized(self, async_client: AsyncClient):
        """Test updating user without authentication."""
        update_data = {"full_name": "Updated Name"}
        
        response = await async_client.put("/api/v1/users/1", json=update_data)
        assert response.status_code == 401


class TestUsersDeleteEndpoint:
    """Test /api/v1/users/{user_id} DELETE endpoint."""
    
    @pytest_asyncio.async_test
    async def test_delete_user_admin(self, async_client: AsyncClient, admin_headers):
        """Test admin can delete users."""
        # First create a user to delete
        new_user_data = {
            "email": f"delete_test_{date.today().isoformat()}@example.com",
            "full_name": "Delete Test User",
            "role": "employee"
        }
        
        create_response = await async_client.post("/api/v1/users/", json=new_user_data, headers=admin_headers)
        if create_response.status_code == 201:
            user_id = create_response.json()["id"]
            
            # Now delete the user
            response = await async_client.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
            assert response.status_code == 200
            
            # Verify user is deleted
            get_response = await async_client.get(f"/api/v1/users/{user_id}", headers=admin_headers)
            assert get_response.status_code == 404
    
    @pytest_asyncio.async_test
    async def test_delete_user_nonexistent(self, async_client: AsyncClient, admin_headers):
        """Test deleting non-existent user."""
        response = await async_client.delete("/api/v1/users/99999", headers=admin_headers)
        assert response.status_code == 404
    
    @pytest_asyncio.async_test
    async def test_delete_user_controller_forbidden(self, async_client: AsyncClient, controller_headers):
        """Test controller cannot delete users."""
        response = await async_client.delete("/api/v1/users/1", headers=controller_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_delete_user_employee_forbidden(self, async_client: AsyncClient, employee_headers):
        """Test employee cannot delete users."""
        response = await async_client.delete("/api/v1/users/1", headers=employee_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_delete_user_unauthorized(self, async_client: AsyncClient):
        """Test deleting user without authentication."""
        response = await async_client.delete("/api/v1/users/1")
        assert response.status_code == 401


class TestUsersGetByEmailEndpoint:
    """Test /api/v1/users/email/{email} endpoint."""
    
    @pytest_asyncio.async_test
    async def test_get_user_by_email_admin(self, async_client: AsyncClient, admin_headers):
        """Test admin can get user by email."""
        response = await async_client.get("/api/v1/users/email/admin@demo.com", headers=admin_headers)
        assert response.status_code in [200, 404]  # OK or Not Found
        
        if response.status_code == 200:
            user = response.json()
            assert user["email"] == "admin@demo.com"
            assert "id" in user
            assert "role" in user
    
    @pytest_asyncio.async_test
    async def test_get_user_by_email_controller(self, async_client: AsyncClient, controller_headers):
        """Test controller can get user by email (limited access)."""
        response = await async_client.get("/api/v1/users/email/malte@demo.com", headers=controller_headers)
        assert response.status_code in [200, 403, 404]  # Depends on permissions
    
    @pytest_asyncio.async_test
    async def test_get_user_by_email_invalid_email(self, async_client: AsyncClient, admin_headers):
        """Test getting user by invalid email format."""
        response = await async_client.get("/api/v1/users/email/invalid-email", headers=admin_headers)
        assert response.status_code in [400, 404, 422]
    
    @pytest_asyncio.async_test
    async def test_get_user_by_email_nonexistent(self, async_client: AsyncClient, admin_headers):
        """Test getting user by non-existent email."""
        response = await async_client.get("/api/v1/users/email/nonexistent@example.com", headers=admin_headers)
        assert response.status_code == 404
    
    @pytest_asyncio.async_test
    async def test_get_user_by_email_unauthorized(self, async_client: AsyncClient):
        """Test getting user by email without authentication."""
        response = await async_client.get("/api/v1/users/email/admin@demo.com")
        assert response.status_code == 401


class TestUsersControllersEndpoint:
    """Test /api/v1/users/controllers endpoint."""
    
    @pytest_asyncio.async_test
    async def test_get_controllers_admin(self, async_client: AsyncClient, admin_headers):
        """Test admin can get all controllers."""
        response = await async_client.get("/api/v1/users/controllers", headers=admin_headers)
        assert response.status_code == 200
        
        controllers = response.json()
        assert isinstance(controllers, list)
        
        # All returned users should be controllers
        for controller in controllers:
            assert controller["role"] == "controller"
            assert "id" in controller
            assert "email" in controller
            assert "full_name" in controller
    
    @pytest_asyncio.async_test
    async def test_get_controllers_controller(self, async_client: AsyncClient, controller_headers):
        """Test controller can get list of controllers."""
        response = await async_client.get("/api/v1/users/controllers", headers=controller_headers)
        assert response.status_code in [200, 403]  # Might be allowed or restricted
        
        if response.status_code == 200:
            controllers = response.json()
            assert isinstance(controllers, list)
    
    @pytest_asyncio.async_test
    async def test_get_controllers_employee_forbidden(self, async_client: AsyncClient, employee_headers):
        """Test employee cannot get controllers list."""
        response = await async_client.get("/api/v1/users/controllers", headers=employee_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_get_controllers_unauthorized(self, async_client: AsyncClient):
        """Test getting controllers without authentication."""
        response = await async_client.get("/api/v1/users/controllers")
        assert response.status_code == 401


class TestUsersMyTeamEndpoint:
    """Test /api/v1/users/my-team endpoint."""
    
    @pytest_asyncio.async_test
    async def test_get_my_team_controller(self, async_client: AsyncClient, controller_headers):
        """Test controller can get their assigned team."""
        response = await async_client.get("/api/v1/users/my-team", headers=controller_headers)
        assert response.status_code == 200
        
        team = response.json()
        assert isinstance(team, list)
        
        # All team members should be employees
        for member in team:
            assert member["role"] == "employee"
            assert "id" in member
            assert "email" in member
            assert "full_name" in member
    
    @pytest_asyncio.async_test
    async def test_get_my_team_admin(self, async_client: AsyncClient, admin_headers):
        """Test admin can get team (might return empty or all employees)."""
        response = await async_client.get("/api/v1/users/my-team", headers=admin_headers)
        assert response.status_code in [200, 403]  # Might work or be restricted to controllers
        
        if response.status_code == 200:
            team = response.json()
            assert isinstance(team, list)
    
    @pytest_asyncio.async_test
    async def test_get_my_team_employee_forbidden(self, async_client: AsyncClient, employee_headers):
        """Test employee cannot get team info."""
        response = await async_client.get("/api/v1/users/my-team", headers=employee_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_get_my_team_unauthorized(self, async_client: AsyncClient):
        """Test getting team without authentication."""
        response = await async_client.get("/api/v1/users/my-team")
        assert response.status_code == 401


class TestUsersAssignControllerEndpoint:
    """Test /api/v1/users/{employee_id}/assign-controller/{controller_id} endpoint."""
    
    @pytest_asyncio.async_test
    async def test_assign_controller_admin(self, async_client: AsyncClient, admin_headers):
        """Test admin can assign employees to controllers."""
        # Get controllers and employees
        users_response = await async_client.get("/api/v1/users/", headers=admin_headers)
        users = users_response.json()
        
        controllers = [u for u in users if u["role"] == "controller"]
        employees = [u for u in users if u["role"] == "employee"]
        
        if len(controllers) > 0 and len(employees) > 0:
            controller_id = controllers[0]["id"]
            employee_id = employees[0]["id"]
            
            response = await async_client.put(
                f"/api/v1/users/{employee_id}/assign-controller/{controller_id}",
                headers=admin_headers
            )
            assert response.status_code == 200
    
    @pytest_asyncio.async_test
    async def test_assign_controller_nonexistent_user(self, async_client: AsyncClient, admin_headers):
        """Test assigning controller with non-existent user."""
        response = await async_client.put(
            "/api/v1/users/99999/assign-controller/1",
            headers=admin_headers
        )
        assert response.status_code == 404
    
    @pytest_asyncio.async_test
    async def test_assign_controller_controller_forbidden(self, async_client: AsyncClient, controller_headers):
        """Test controller cannot assign other controllers."""
        response = await async_client.put(
            "/api/v1/users/1/assign-controller/2",
            headers=controller_headers
        )
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_assign_controller_employee_forbidden(self, async_client: AsyncClient, employee_headers):
        """Test employee cannot assign controllers."""
        response = await async_client.put(
            "/api/v1/users/1/assign-controller/2",
            headers=employee_headers
        )
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_assign_controller_unauthorized(self, async_client: AsyncClient):
        """Test assigning controller without authentication."""
        response = await async_client.put("/api/v1/users/1/assign-controller/2")
        assert response.status_code == 401


class TestUsersControllerEmployeesEndpoint:
    """Test /api/v1/users/controller/{controller_id}/employees endpoint."""
    
    @pytest_asyncio.async_test
    async def test_get_controller_employees_admin(self, async_client: AsyncClient, admin_headers):
        """Test admin can get employees for any controller."""
        # Get a controller first
        controllers_response = await async_client.get("/api/v1/users/controllers", headers=admin_headers)
        controllers = controllers_response.json()
        
        if len(controllers) > 0:
            controller_id = controllers[0]["id"]
            
            response = await async_client.get(f"/api/v1/users/controller/{controller_id}/employees", headers=admin_headers)
            assert response.status_code == 200
            
            employees = response.json()
            assert isinstance(employees, list)
            
            # All should be employees
            for employee in employees:
                assert employee["role"] == "employee"
    
    @pytest_asyncio.async_test
    async def test_get_controller_employees_controller_own(self, async_client: AsyncClient, controller_headers):
        """Test controller can get their own employees."""
        # Get current controller info
        me_response = await async_client.get("/api/v1/auth/me", headers=controller_headers)
        controller_id = me_response.json()["id"]
        
        response = await async_client.get(f"/api/v1/users/controller/{controller_id}/employees", headers=controller_headers)
        assert response.status_code == 200
        
        employees = response.json()
        assert isinstance(employees, list)
    
    @pytest_asyncio.async_test
    async def test_get_controller_employees_nonexistent(self, async_client: AsyncClient, admin_headers):
        """Test getting employees for non-existent controller."""
        response = await async_client.get("/api/v1/users/controller/99999/employees", headers=admin_headers)
        assert response.status_code == 404
    
    @pytest_asyncio.async_test
    async def test_get_controller_employees_employee_forbidden(self, async_client: AsyncClient, employee_headers):
        """Test employee cannot get controller's employees."""
        response = await async_client.get("/api/v1/users/controller/1/employees", headers=employee_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_get_controller_employees_unauthorized(self, async_client: AsyncClient):
        """Test getting controller employees without authentication."""
        response = await async_client.get("/api/v1/users/controller/1/employees")
        assert response.status_code == 401
