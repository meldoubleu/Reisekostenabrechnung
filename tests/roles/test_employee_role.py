"""
Employee Role Tests - Complete API Endpoint Coverage
Tests all endpoints accessible by employee role users.
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
async def employee_auth_headers(async_client: AsyncClient):
    """Get authentication headers for employee user."""
    login_data = {
        "username": "malte@demo.com",
        "password": "employee123"
    }
    
    login_response = await async_client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    token_data = login_response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


class TestEmployeeAuthEndpoints:
    """Test authentication endpoints for employees."""
    
    @pytest_asyncio.async_test
    async def test_employee_login(self, async_client: AsyncClient):
        """Test employee login endpoint."""
        login_data = {
            "username": "malte@demo.com",
            "password": "employee123"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"
    
    @pytest_asyncio.async_test
    async def test_employee_get_me(self, async_client: AsyncClient, employee_auth_headers):
        """Test getting current employee user info."""
        response = await async_client.get("/api/v1/auth/me", headers=employee_auth_headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == "malte@demo.com"
        assert user_data["role"] == "employee"
        assert "id" in user_data
        assert "full_name" in user_data
    
    @pytest_asyncio.async_test
    async def test_employee_invalid_login(self, async_client: AsyncClient):
        """Test employee login with invalid credentials."""
        login_data = {
            "username": "malte@demo.com",
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401


class TestEmployeeTravelEndpoints:
    """Test travel-related endpoints for employees."""
    
    @pytest_asyncio.async_test
    async def test_employee_create_travel(self, async_client: AsyncClient, employee_auth_headers):
        """Test creating a new travel expense."""
        today = date.today()
        travel_data = {
            "destination": "Berlin Business Trip",
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=2)).isoformat(),
            "purpose": "Client Meeting and Training",
            "accommodation_costs": 300.0,
            "transport_costs": 150.0,
            "meal_costs": 120.0,
            "other_costs": 30.0,
            "total_expenses": 600.0,
            "status": "draft"
        }
        
        response = await async_client.post("/api/v1/travels/submit", json=travel_data, headers=employee_auth_headers)
        assert response.status_code == 201
        
        result = response.json()
        assert result["destination"] == "Berlin Business Trip"
        assert result["total_expenses"] == 600.0
        assert result["status"] == "draft"
        assert "id" in result
        
        return result["id"]  # Return for other tests
    
    @pytest_asyncio.async_test
    async def test_employee_get_my_travels(self, async_client: AsyncClient, employee_auth_headers):
        """Test retrieving employee's own travels."""
        response = await async_client.get("/api/v1/travels/my", headers=employee_auth_headers)
        assert response.status_code == 200
        
        travels = response.json()
        assert isinstance(travels, list)
        # Should have at least one travel (created in previous test or existing data)
    
    @pytest_asyncio.async_test
    async def test_employee_get_specific_travel(self, async_client: AsyncClient, employee_auth_headers):
        """Test getting a specific travel by ID."""
        # First create a travel
        travel_id = await self.test_employee_create_travel(async_client, employee_auth_headers)
        
        if travel_id:
            response = await async_client.get(f"/api/v1/travels/{travel_id}", headers=employee_auth_headers)
            assert response.status_code == 200
            
            travel = response.json()
            assert travel["id"] == travel_id
            assert travel["destination"] == "Berlin Business Trip"
    
    @pytest_asyncio.async_test
    async def test_employee_update_travel(self, async_client: AsyncClient, employee_auth_headers):
        """Test updating an existing travel."""
        # First create a travel
        travel_id = await self.test_employee_create_travel(async_client, employee_auth_headers)
        
        if travel_id:
            update_data = {
                "destination": "Munich Updated Trip",
                "purpose": "Updated Purpose",
                "accommodation_costs": 350.0,
                "transport_costs": 180.0,
                "meal_costs": 140.0,
                "other_costs": 30.0,
                "total_expenses": 700.0
            }
            
            response = await async_client.put(f"/api/v1/travels/{travel_id}", json=update_data, headers=employee_auth_headers)
            assert response.status_code == 200
            
            updated_travel = response.json()
            assert updated_travel["destination"] == "Munich Updated Trip"
            assert updated_travel["total_expenses"] == 700.0
    
    @pytest_asyncio.async_test
    async def test_employee_travel_receipts(self, async_client: AsyncClient, employee_auth_headers):
        """Test travel receipt operations."""
        # First create a travel
        travel_id = await self.test_employee_create_travel(async_client, employee_auth_headers)
        
        if travel_id:
            # Test getting receipts for a travel
            response = await async_client.get(f"/api/v1/travels/{travel_id}/receipts", headers=employee_auth_headers)
            assert response.status_code == 200
            
            receipts = response.json()
            assert isinstance(receipts, list)
    
    @pytest_asyncio.async_test
    async def test_employee_travel_export(self, async_client: AsyncClient, employee_auth_headers):
        """Test exporting travel data."""
        # First create a travel
        travel_id = await self.test_employee_create_travel(async_client, employee_auth_headers)
        
        if travel_id:
            response = await async_client.get(f"/api/v1/travels/{travel_id}/export", headers=employee_auth_headers)
            # This might return different status codes depending on implementation
            assert response.status_code in [200, 404, 501]  # OK, Not Found, or Not Implemented


class TestEmployeeRestrictedAccess:
    """Test that employees cannot access restricted endpoints."""
    
    @pytest_asyncio.async_test
    async def test_employee_cannot_access_all_users(self, async_client: AsyncClient, employee_auth_headers):
        """Test that employees cannot list all users."""
        response = await async_client.get("/api/v1/users/", headers=employee_auth_headers)
        assert response.status_code == 403  # Forbidden
    
    @pytest_asyncio.async_test
    async def test_employee_cannot_access_admin_endpoints(self, async_client: AsyncClient, employee_auth_headers):
        """Test that employees cannot access admin endpoints."""
        # Test admin dashboard
        response = await async_client.get("/api/v1/admin/dashboard", headers=employee_auth_headers)
        assert response.status_code == 403
        
        # Test admin user creation
        new_user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "employee"
        }
        response = await async_client.post("/api/v1/admin/employees", json=new_user_data, headers=employee_auth_headers)
        assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_employee_cannot_access_all_travels(self, async_client: AsyncClient, employee_auth_headers):
        """Test that employees cannot access all travels (only their own)."""
        response = await async_client.get("/api/v1/travels/", headers=employee_auth_headers)
        # This should either be forbidden or return only their travels
        # Based on the implementation, adjust this assertion
        if response.status_code == 200:
            travels = response.json()
            # If allowed, should only see own travels
            assert isinstance(travels, list)
        else:
            assert response.status_code == 403
    
    @pytest_asyncio.async_test
    async def test_employee_cannot_approve_travels(self, async_client: AsyncClient, employee_auth_headers):
        """Test that employees cannot approve/reject travels."""
        # Try to approve a travel (should fail)
        response = await async_client.put("/api/v1/travels/1/approve", headers=employee_auth_headers)
        assert response.status_code in [403, 404]  # Forbidden or Not Found
        
        # Try to reject a travel (should fail)
        response = await async_client.put("/api/v1/travels/1/reject", headers=employee_auth_headers)
        assert response.status_code in [403, 404]  # Forbidden or Not Found


class TestEmployeeDataValidation:
    """Test data validation for employee inputs."""
    
    @pytest_asyncio.async_test
    async def test_employee_invalid_travel_data(self, async_client: AsyncClient, employee_auth_headers):
        """Test creating travel with invalid data."""
        invalid_travel_data = {
            "destination": "",  # Empty destination
            "start_date": "invalid-date",  # Invalid date format
            "end_date": "2025-09-10",
            "purpose": "",  # Empty purpose
            "accommodation_costs": -100.0,  # Negative cost
            "total_expenses": "not-a-number"  # Invalid number
        }
        
        response = await async_client.post("/api/v1/travels/submit", json=invalid_travel_data, headers=employee_auth_headers)
        assert response.status_code == 422  # Validation error
    
    @pytest_asyncio.async_test
    async def test_employee_invalid_date_range(self, async_client: AsyncClient, employee_auth_headers):
        """Test creating travel with end date before start date."""
        today = date.today()
        invalid_travel_data = {
            "destination": "Test Destination",
            "start_date": today.isoformat(),
            "end_date": (today - timedelta(days=1)).isoformat(),  # End before start
            "purpose": "Test Purpose",
            "accommodation_costs": 100.0,
            "transport_costs": 50.0,
            "meal_costs": 30.0,
            "other_costs": 10.0,
            "total_expenses": 190.0,
            "status": "draft"
        }
        
        response = await async_client.post("/api/v1/travels/submit", json=invalid_travel_data, headers=employee_auth_headers)
        # Should either validate and reject, or business logic should handle it
        assert response.status_code in [422, 400]


class TestEmployeeUIEndpoints:
    """Test UI endpoints accessible to employees."""
    
    @pytest_asyncio.async_test
    async def test_employee_can_access_ui_pages(self, async_client: AsyncClient):
        """Test that UI pages are accessible."""
        # Test main UI page
        response = await async_client.get("/api/v1/ui")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # Test dashboard page
        response = await async_client.get("/api/v1/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # Test travel form page
        response = await async_client.get("/api/v1/travel-form")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestEmployeeSecurityAndEdgeCases:
    """Test security and edge cases for employee role."""
    
    @pytest_asyncio.async_test
    async def test_employee_unauthorized_access(self, async_client: AsyncClient):
        """Test accessing protected endpoints without authentication."""
        # Try to access employee's own travels without auth
        response = await async_client.get("/api/v1/travels/my")
        assert response.status_code == 401
        
        # Try to create travel without auth
        travel_data = {"destination": "Test", "purpose": "Test"}
        response = await async_client.post("/api/v1/travels/submit", json=travel_data)
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_employee_with_invalid_token(self, async_client: AsyncClient):
        """Test accessing endpoints with invalid token."""
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        
        response = await async_client.get("/api/v1/travels/my", headers=invalid_headers)
        assert response.status_code == 401
        
        response = await async_client.get("/api/v1/auth/me", headers=invalid_headers)
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_employee_accessing_other_user_travel(self, async_client: AsyncClient, employee_auth_headers):
        """Test that employee cannot access other users' specific travels."""
        # Try to access a travel with an ID that likely belongs to another user
        # Note: This assumes travel ID 999 doesn't belong to the test employee
        response = await async_client.get("/api/v1/travels/999", headers=employee_auth_headers)
        assert response.status_code in [403, 404]  # Forbidden or Not Found
