"""
Comprehensive End-to-End Workflow Tests
Tests the complete user workflows for employees, controllers, and admins.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from backend.app.main import app
import json
import tempfile
import os

"""
Comprehensive End-to-End Workflow Tests
Tests the complete user workflows for employees, controllers, and admins.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from backend.app.main import app


@pytest_asyncio.fixture
async def async_client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


class TestEmployeeWorkflow:
    """Test complete employee workflow: login -> create travel -> view dashboard"""
    
    @pytest_asyncio.async_test
    async def test_employee_complete_workflow(self, async_client: AsyncClient):
        """Test complete employee workflow"""
        # Step 1: Employee Login
        login_data = {
            "username": "malte@demo.com",
            "password": "employee123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Step 2: Get user info
        user_response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert user_response.status_code == 200
        user_data = user_response.json()
        assert user_data["email"] == "malte@demo.com"
        assert user_data["role"] == "employee"
        
        # Step 3: Create a travel expense
        travel_data = {
            "destination": "Berlin",
            "start_date": "2025-09-10",
            "end_date": "2025-09-12",
            "purpose": "Client Meeting",
            "accommodation_costs": 300.0,
            "transport_costs": 150.0,
            "meal_costs": 120.0,
            "other_costs": 30.0,
            "total_expenses": 600.0,
            "status": "draft"
        }
        
        create_response = await async_client.post("/api/v1/travels/submit", json=travel_data, headers=headers)
        assert create_response.status_code == 200
        travel_result = create_response.json()
        assert travel_result["destination"] == "Berlin"
        assert travel_result["total_expenses"] == 600.0
        travel_id = travel_result["id"]
        
        # Step 4: Retrieve own travels
        my_travels_response = await async_client.get("/api/v1/travels/my", headers=headers)
        assert my_travels_response.status_code == 200
        travels = my_travels_response.json()
        assert len(travels) > 0
        
        # Verify the created travel is in the list
        created_travel = next((t for t in travels if t["id"] == travel_id), None)
        assert created_travel is not None
        assert created_travel["destination"] == "Berlin"
        assert created_travel["total_expenses"] == 600.0


class TestControllerWorkflow:
    """Test controller workflow: login -> view assigned employees -> manage travels"""
    
    @pytest_asyncio.async_test
    async def test_controller_complete_workflow(self, async_client: AsyncClient):
        """Test complete controller workflow"""
        # Step 1: Controller Login
        login_data = {
            "username": "controller1@demo.com",
            "password": "controller123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Step 2: Get controller info
        user_response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert user_response.status_code == 200
        user_data = user_response.json()
        assert user_data["role"] == "controller"
        
        # Step 3: View all travels (controller can see assigned employees' travels)
        travels_response = await async_client.get("/api/v1/travels/", headers=headers)
        assert travels_response.status_code == 200
        travels = travels_response.json()
        # Controllers should see some travels
        assert isinstance(travels, list)


class TestAdminWorkflow:
    """Test admin workflow: login -> manage users -> view all data"""
    
    @pytest_asyncio.async_test
    async def test_admin_complete_workflow(self, async_client: AsyncClient):
        """Test complete admin workflow"""
        # Step 1: Admin Login
        login_data = {
            "username": "admin@demo.com",
            "password": "admin123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Step 2: Get admin info
        user_response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert user_response.status_code == 200
        user_data = user_response.json()
        assert user_data["role"] == "admin"
        
        # Step 3: View all users
        users_response = await async_client.get("/api/v1/users/", headers=headers)
        assert users_response.status_code == 200
        users = users_response.json()
        assert len(users) > 0
        
        # Step 4: View all travels
        travels_response = await async_client.get("/api/v1/travels/", headers=headers)
        assert travels_response.status_code == 200
        travels = travels_response.json()
        assert isinstance(travels, list)


class TestTotalExpensesCalculation:
    """Test that total expenses are correctly calculated and stored"""
    
    @pytest_asyncio.async_test
    async def test_total_expenses_calculation(self, async_client: AsyncClient):
        """Test total expenses calculation in travel creation"""
        # Login as employee
        login_data = {
            "username": "malte@demo.com",
            "password": "employee123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Create travel with specific costs
        travel_data = {
            "destination": "Munich",
            "start_date": "2025-09-15",
            "end_date": "2025-09-16",
            "purpose": "Training",
            "accommodation_costs": 200.0,
            "transport_costs": 100.0,
            "meal_costs": 80.0,
            "other_costs": 20.0,
            "total_expenses": 400.0,  # Should match sum of individual costs
            "status": "draft"
        }
        
        create_response = await async_client.post("/api/v1/travels/submit", json=travel_data, headers=headers)
        assert create_response.status_code == 200
        travel_result = create_response.json()
        
        # Verify total expenses is correctly stored
        assert travel_result["total_expenses"] == 400.0
        assert travel_result["accommodation_costs"] == 200.0
        assert travel_result["transport_costs"] == 100.0
        assert travel_result["meal_costs"] == 80.0
        assert travel_result["other_costs"] == 20.0


class TestAuthenticationSecurity:
    """Test authentication and authorization security"""
    
    @pytest_asyncio.async_test
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test that unauthorized requests are properly rejected"""
        # Try to access protected endpoint without token
        response = await async_client.get("/api/v1/travels/my")
        assert response.status_code == 401
        
        # Try to access protected endpoint with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/api/v1/travels/my", headers=headers)
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_role_based_access(self, async_client: AsyncClient):
        """Test that role-based access control works correctly"""
        # Login as employee
        login_data = {
            "username": "malte@demo.com",
            "password": "employee123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        employee_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Employee should NOT be able to access admin endpoints
        response = await async_client.get("/api/v1/users/", headers=employee_headers)
        assert response.status_code == 403  # Forbidden


class TestDataValidation:
    """Test data validation for travel submissions"""
    
    @pytest_asyncio.async_test
    async def test_invalid_travel_data(self, async_client: AsyncClient):
        """Test that invalid travel data is rejected"""
        # Login first
        login_data = {
            "username": "malte@demo.com",
            "password": "employee123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Test missing required fields
        invalid_travel_data = {
            "destination": "",  # Empty destination
            "start_date": "invalid-date",  # Invalid date format
            "end_date": "2025-09-10",
            "purpose": "Test"
        }
        
        response = await async_client.post("/api/v1/travels/submit", json=invalid_travel_data, headers=headers)
        assert response.status_code == 422  # Validation error
    
    @pytest_asyncio.async_test
    async def test_date_validation(self, async_client: AsyncClient):
        """Test date validation logic"""
        # Login first
        login_data = {
            "username": "malte@demo.com",
            "password": "employee123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Test end date before start date
        invalid_travel_data = {
            "destination": "Test City",
            "start_date": "2025-09-15",
            "end_date": "2025-09-10",  # End before start
            "purpose": "Test",
            "accommodation_costs": 100.0,
            "transport_costs": 50.0,
            "meal_costs": 30.0,
            "other_costs": 10.0,
            "total_expenses": 190.0,
            "status": "draft"
        }
        
        response = await async_client.post("/api/v1/travels/submit", json=invalid_travel_data, headers=headers)
        # This should either be rejected or corrected by business logic
        # The exact response depends on how the backend handles this case
        assert response.status_code in [422, 400]  # Validation or business logic error
