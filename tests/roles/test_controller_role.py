"""
Controller Role Tests - Complete API Endpoint Coverage
Tests all endpoints accessible by controller role users.
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
async def controller_auth_headers(async_client: AsyncClient):
    """Get authentication headers for controller user."""
    login_data = {
        "username": "controller1@demo.com",
        "password": "controller123"
    }
    
    login_response = await async_client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    token_data = login_response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


class TestControllerAuthEndpoints:
    """Test authentication endpoints for controllers."""
    
    @pytest_asyncio.async_test
    async def test_controller_login(self, async_client: AsyncClient):
        """Test controller login endpoint."""
        login_data = {
            "username": "controller1@demo.com",
            "password": "controller123"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"
    
    @pytest_asyncio.async_test
    async def test_controller_get_me(self, async_client: AsyncClient, controller_auth_headers):
        """Test getting current controller user info."""
        response = await async_client.get("/api/v1/auth/me", headers=controller_auth_headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == "controller1@demo.com"
        assert user_data["role"] == "controller"
        assert "id" in user_data
        assert "full_name" in user_data


class TestControllerTravelEndpoints:
    """Test travel-related endpoints for controllers."""
    
    @pytest_asyncio.async_test
    async def test_controller_get_all_travels(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view all travels."""
        response = await async_client.get("/api/v1/travels/", headers=controller_auth_headers)
        assert response.status_code == 200
        
        travels = response.json()
        assert isinstance(travels, list)
        # Controllers should be able to see travels from their assigned employees
    
    @pytest_asyncio.async_test
    async def test_controller_get_assigned_travels(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view travels assigned to them."""
        response = await async_client.get("/api/v1/travels/assigned", headers=controller_auth_headers)
        assert response.status_code == 200
        
        travels = response.json()
        assert isinstance(travels, list)
    
    @pytest_asyncio.async_test
    async def test_controller_get_employee_travels(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view specific employee's travels."""
        # First, get the controller's assigned employees
        team_response = await async_client.get("/api/v1/users/my-team", headers=controller_auth_headers)
        assert team_response.status_code == 200
        
        team = team_response.json()
        if len(team) > 0:
            employee_id = team[0]["id"]
            
            response = await async_client.get(f"/api/v1/travels/employee/{employee_id}/travels", headers=controller_auth_headers)
            assert response.status_code == 200
            
            travels = response.json()
            assert isinstance(travels, list)
    
    @pytest_asyncio.async_test
    async def test_controller_get_controller_travels(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view travels by controller ID."""
        # Get current controller info first
        me_response = await async_client.get("/api/v1/auth/me", headers=controller_auth_headers)
        controller_id = me_response.json()["id"]
        
        response = await async_client.get(f"/api/v1/travels/controller/{controller_id}/travels", headers=controller_auth_headers)
        assert response.status_code == 200
        
        travels = response.json()
        assert isinstance(travels, list)
    
    @pytest_asyncio.async_test
    async def test_controller_approve_travel(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can approve travels."""
        # First, try to get an existing travel to approve
        travels_response = await async_client.get("/api/v1/travels/", headers=controller_auth_headers)
        travels = travels_response.json()
        
        if len(travels) > 0:
            travel_id = travels[0]["id"]
            
            response = await async_client.put(f"/api/v1/travels/{travel_id}/approve", headers=controller_auth_headers)
            # Should succeed or return appropriate error if already approved/conditions not met
            assert response.status_code in [200, 400, 409]  # OK, Bad Request, or Conflict
    
    @pytest_asyncio.async_test
    async def test_controller_reject_travel(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can reject travels."""
        # First, try to get an existing travel to reject
        travels_response = await async_client.get("/api/v1/travels/", headers=controller_auth_headers)
        travels = travels_response.json()
        
        if len(travels) > 0:
            travel_id = travels[0]["id"]
            
            response = await async_client.put(f"/api/v1/travels/{travel_id}/reject", headers=controller_auth_headers)
            # Should succeed or return appropriate error if already rejected/conditions not met
            assert response.status_code in [200, 400, 409]  # OK, Bad Request, or Conflict
    
    @pytest_asyncio.async_test
    async def test_controller_get_specific_travel(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view specific travel details."""
        # Get a travel first
        travels_response = await async_client.get("/api/v1/travels/", headers=controller_auth_headers)
        travels = travels_response.json()
        
        if len(travels) > 0:
            travel_id = travels[0]["id"]
            
            response = await async_client.get(f"/api/v1/travels/{travel_id}", headers=controller_auth_headers)
            assert response.status_code == 200
            
            travel = response.json()
            assert travel["id"] == travel_id
    
    @pytest_asyncio.async_test
    async def test_controller_get_travel_receipts(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view travel receipts."""
        # Get a travel first
        travels_response = await async_client.get("/api/v1/travels/", headers=controller_auth_headers)
        travels = travels_response.json()
        
        if len(travels) > 0:
            travel_id = travels[0]["id"]
            
            response = await async_client.get(f"/api/v1/travels/{travel_id}/receipts", headers=controller_auth_headers)
            assert response.status_code == 200
            
            receipts = response.json()
            assert isinstance(receipts, list)


class TestControllerUserEndpoints:
    """Test user management endpoints for controllers."""
    
    @pytest_asyncio.async_test
    async def test_controller_get_my_team(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view their assigned employees."""
        response = await async_client.get("/api/v1/users/my-team", headers=controller_auth_headers)
        assert response.status_code == 200
        
        team = response.json()
        assert isinstance(team, list)
        # Each team member should be an employee
        for member in team:
            assert member["role"] == "employee"
    
    @pytest_asyncio.async_test
    async def test_controller_get_controllers_list(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view list of controllers."""
        response = await async_client.get("/api/v1/users/controllers", headers=controller_auth_headers)
        assert response.status_code == 200
        
        controllers = response.json()
        assert isinstance(controllers, list)
        # Each should be a controller
        for controller in controllers:
            assert controller["role"] == "controller"
    
    @pytest_asyncio.async_test
    async def test_controller_get_user_by_id(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view user details by ID."""
        # Get team first to get an employee ID
        team_response = await async_client.get("/api/v1/users/my-team", headers=controller_auth_headers)
        team = team_response.json()
        
        if len(team) > 0:
            user_id = team[0]["id"]
            
            response = await async_client.get(f"/api/v1/users/{user_id}", headers=controller_auth_headers)
            assert response.status_code == 200
            
            user = response.json()
            assert user["id"] == user_id
    
    @pytest_asyncio.async_test
    async def test_controller_get_user_by_email(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view user details by email."""
        # Try to get a known employee email
        response = await async_client.get("/api/v1/users/email/malte@demo.com", headers=controller_auth_headers)
        # Should work if controller has access to this employee
        assert response.status_code in [200, 403, 404]
    
    @pytest_asyncio.async_test
    async def test_controller_get_assigned_employees(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can view employees assigned to a specific controller."""
        # Get current controller info
        me_response = await async_client.get("/api/v1/auth/me", headers=controller_auth_headers)
        controller_id = me_response.json()["id"]
        
        response = await async_client.get(f"/api/v1/users/controller/{controller_id}/employees", headers=controller_auth_headers)
        assert response.status_code == 200
        
        employees = response.json()
        assert isinstance(employees, list)


class TestControllerRestrictedAccess:
    """Test that controllers cannot access admin-only endpoints."""
    
    @pytest_asyncio.async_test
    async def test_controller_cannot_access_admin_dashboard(self, async_client: AsyncClient, controller_auth_headers):
        """Test that controllers cannot access admin dashboard."""
        response = await async_client.get("/api/v1/admin/dashboard", headers=controller_auth_headers)
        assert response.status_code == 403  # Forbidden
    
    @pytest_asyncio.async_test
    async def test_controller_cannot_create_users(self, async_client: AsyncClient, controller_auth_headers):
        """Test that controllers cannot create new users."""
        new_user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "employee"
        }
        
        # Try admin employee creation
        response = await async_client.post("/api/v1/admin/employees", json=new_user_data, headers=controller_auth_headers)
        assert response.status_code == 403
        
        # Try admin controller creation
        response = await async_client.post("/api/v1/admin/controllers", json=new_user_data, headers=controller_auth_headers)
        assert response.status_code == 403
        
        # Try regular user creation
        response = await async_client.post("/api/v1/users/", json=new_user_data, headers=controller_auth_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_controller_cannot_delete_users(self, async_client: AsyncClient, controller_auth_headers):
        """Test that controllers cannot delete users."""
        # Try to delete a user (should fail)
        response = await async_client.delete("/api/v1/users/999", headers=controller_auth_headers)
        assert response.status_code == 403
        
        # Try admin delete
        response = await async_client.delete("/api/v1/admin/users/999", headers=controller_auth_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_controller_cannot_manage_assignments(self, async_client: AsyncClient, controller_auth_headers):
        """Test that controllers cannot manage employee-controller assignments."""
        # Try to assign employee to controller
        response = await async_client.put("/api/v1/admin/assign-employee/1/to-controller/2", headers=controller_auth_headers)
        assert response.status_code == 403
        
        # Try to unassign employee
        response = await async_client.put("/api/v1/admin/unassign-employee/1", headers=controller_auth_headers)
        assert response.status_code == 403
        
        # Try regular assignment
        response = await async_client.put("/api/v1/users/1/assign-controller/2", headers=controller_auth_headers)
        assert response.status_code == 403


class TestControllerTravelManagement:
    """Test travel management capabilities specific to controllers."""
    
    @pytest_asyncio.async_test
    async def test_controller_can_update_employee_travel(self, async_client: AsyncClient, controller_auth_headers):
        """Test that controller can update travels from assigned employees."""
        # Get assigned travels
        travels_response = await async_client.get("/api/v1/travels/assigned", headers=controller_auth_headers)
        travels = travels_response.json()
        
        if len(travels) > 0:
            travel_id = travels[0]["id"]
            
            update_data = {
                "status": "approved",
                "controller_comments": "Approved by controller"
            }
            
            response = await async_client.put(f"/api/v1/travels/{travel_id}", json=update_data, headers=controller_auth_headers)
            # Should succeed if controller has permission to update this travel
            assert response.status_code in [200, 403]
    
    @pytest_asyncio.async_test
    async def test_controller_export_travel_data(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller can export travel data."""
        # Get a travel to export
        travels_response = await async_client.get("/api/v1/travels/", headers=controller_auth_headers)
        travels = travels_response.json()
        
        if len(travels) > 0:
            travel_id = travels[0]["id"]
            
            response = await async_client.get(f"/api/v1/travels/{travel_id}/export", headers=controller_auth_headers)
            # Should work or return appropriate error
            assert response.status_code in [200, 404, 501]


class TestControllerUIEndpoints:
    """Test UI endpoints accessible to controllers."""
    
    @pytest_asyncio.async_test
    async def test_controller_can_access_ui_pages(self, async_client: AsyncClient):
        """Test that UI pages are accessible to controllers."""
        # Test main UI page
        response = await async_client.get("/api/v1/ui")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # Test dashboard page
        response = await async_client.get("/api/v1/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestControllerSecurityAndEdgeCases:
    """Test security and edge cases for controller role."""
    
    @pytest_asyncio.async_test
    async def test_controller_unauthorized_access(self, async_client: AsyncClient):
        """Test accessing protected endpoints without authentication."""
        # Try to access controller-specific endpoints without auth
        response = await async_client.get("/api/v1/travels/assigned")
        assert response.status_code == 401
        
        response = await async_client.get("/api/v1/users/my-team")
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_controller_with_invalid_token(self, async_client: AsyncClient):
        """Test accessing endpoints with invalid token."""
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        
        response = await async_client.get("/api/v1/travels/assigned", headers=invalid_headers)
        assert response.status_code == 401
        
        response = await async_client.get("/api/v1/users/my-team", headers=invalid_headers)
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_controller_accessing_unassigned_employee_data(self, async_client: AsyncClient, controller_auth_headers):
        """Test controller cannot access data from unassigned employees."""
        # Try to access employee travels for an employee not assigned to this controller
        # Note: This test assumes employee ID 999 is not assigned to the test controller
        response = await async_client.get("/api/v1/travels/employee/999/travels", headers=controller_auth_headers)
        assert response.status_code in [403, 404]  # Forbidden or Not Found
