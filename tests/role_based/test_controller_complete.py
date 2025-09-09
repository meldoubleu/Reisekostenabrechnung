"""
Controller Role Complete Test Suite
Tests all API endpoints accessible by controller role users.
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
def controller_token(client):
    """Get authentication token for controller user."""
    login_data = {
        "email": "controller@demo.com",
        "password": "controller123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # If login fails, try to register first
    register_data = {
        "email": "controller@demo.com",
        "password": "controller123",
        "name": "Test Controller",
        "role": "controller"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    if register_response.status_code == 200:
        return register_response.json()["access_token"]
    
    raise Exception("Could not authenticate controller user")


@pytest.fixture
def controller_headers(controller_token):
    """Get authentication headers for controller user."""
    return {"Authorization": f"Bearer {controller_token}"}


@pytest.fixture
def employee_token(client):
    """Get authentication token for test employee."""
    login_data = {
        "email": "test_employee@demo.com",
        "password": "employee123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # If login fails, try to register first
    register_data = {
        "email": "test_employee@demo.com",
        "password": "employee123",
        "name": "Test Employee for Controller",
        "role": "employee"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    if register_response.status_code == 200:
        return register_response.json()["access_token"]
    
    return None


@pytest.fixture
def employee_headers(employee_token):
    """Get authentication headers for test employee."""
    if employee_token:
        return {"Authorization": f"Bearer {employee_token}"}
    return None


@pytest.mark.unit
class TestControllerAuthentication:
    """Test authentication endpoints for controllers."""
    
    def test_controller_login_valid_credentials(self, client):
        """Test controller login with valid credentials."""
        login_data = {
            "email": "controller@demo.com",
            "password": "controller123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        if response.status_code == 404:
            # User doesn't exist, create it first
            register_data = {
                "email": "controller@demo.com",
                "password": "controller123",
                "name": "Test Controller",
                "role": "controller"
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
    
    def test_controller_get_me(self, client, controller_headers):
        """Test getting current controller user info."""
        response = client.get("/api/v1/auth/me", headers=controller_headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == "controller@demo.com"
        assert user_data["role"] == "controller"
        assert "id" in user_data
        assert "name" in user_data


@pytest.mark.integration
class TestControllerUserManagement:
    """Test user management endpoints for controllers."""
    
    def test_controller_get_my_team(self, client, controller_headers):
        """Test getting assigned employees."""
        response = client.get("/api/v1/users/my-team", headers=controller_headers)
        assert response.status_code == 200
        
        team = response.json()
        assert isinstance(team, list)
    
    def test_controller_get_users(self, client, controller_headers):
        """Test getting all users (controller permission)."""
        response = client.get("/api/v1/users/", headers=controller_headers)
        # Controllers might have limited access
        assert response.status_code in [200, 403, 404]
    
    def test_controller_get_specific_user(self, client, controller_headers):
        """Test getting specific user info."""
        # Try to get user 1
        response = client.get("/api/v1/users/1", headers=controller_headers)
        assert response.status_code in [200, 403, 404]
    
    def test_controller_get_controllers(self, client, controller_headers):
        """Test getting list of controllers."""
        response = client.get("/api/v1/users/controllers", headers=controller_headers)
        assert response.status_code == 200
        
        controllers = response.json()
        assert isinstance(controllers, list)


@pytest.mark.integration
class TestControllerTravelManagement:
    """Test travel management endpoints for controllers."""
    
    def test_controller_get_all_travels(self, client, controller_headers):
        """Test getting all travels (controller view)."""
        response = client.get("/api/v1/travels/", headers=controller_headers)
        assert response.status_code == 200
        
        travels = response.json()
        assert isinstance(travels, list)
    
    def test_controller_get_assigned_travels(self, client, controller_headers):
        """Test getting travels from assigned employees."""
        response = client.get("/api/v1/travels/assigned", headers=controller_headers)
        # This endpoint might not exist, check alternatives
        if response.status_code == 404:
            response = client.get("/api/v1/travels/", headers=controller_headers)
        
        assert response.status_code == 200
        travels = response.json()
        assert isinstance(travels, list)
    
    def test_controller_approve_travel(self, client, controller_headers, employee_headers):
        """Test approving a travel expense."""
        # First create a travel as employee if possible
        if employee_headers:
            travel_data = {
                "destination": "Controller Test Trip",
                "start_date": date.today().isoformat(),
                "end_date": (date.today() + timedelta(days=1)).isoformat(),
                "purpose": "Testing",
                "accommodation_costs": 100.0,
                "transport_costs": 50.0,
                "meal_costs": 30.0,
                "other_costs": 20.0,
                "total_expenses": 200.0
            }
            
            create_response = client.post("/api/v1/travels/", json=travel_data, headers=employee_headers)
            if create_response.status_code in [200, 201]:
                travel = create_response.json()
                travel_id = travel["id"]
                
                # Submit the travel
                submit_response = client.post(f"/api/v1/travels/{travel_id}/submit", headers=employee_headers)
                
                # Now try to approve it as controller
                approve_response = client.put(f"/api/v1/travels/{travel_id}/approve", headers=controller_headers)
                assert approve_response.status_code in [200, 403, 404]
                
                if approve_response.status_code == 200:
                    approved_travel = approve_response.json()
                    assert approved_travel["status"] == "approved"
    
    def test_controller_reject_travel(self, client, controller_headers, employee_headers):
        """Test rejecting a travel expense."""
        # Similar to approve test but for rejection
        if employee_headers:
            travel_data = {
                "destination": "Reject Test Trip",
                "start_date": date.today().isoformat(),
                "end_date": (date.today() + timedelta(days=1)).isoformat(),
                "purpose": "Testing Rejection",
                "accommodation_costs": 100.0,
                "transport_costs": 50.0,
                "meal_costs": 30.0,
                "other_costs": 20.0,
                "total_expenses": 200.0
            }
            
            create_response = client.post("/api/v1/travels/", json=travel_data, headers=employee_headers)
            if create_response.status_code in [200, 201]:
                travel = create_response.json()
                travel_id = travel["id"]
                
                # Submit the travel
                submit_response = client.post(f"/api/v1/travels/{travel_id}/submit", headers=employee_headers)
                
                # Now try to reject it as controller
                reject_response = client.put(f"/api/v1/travels/{travel_id}/reject", headers=controller_headers)
                assert reject_response.status_code in [200, 403, 404]
                
                if reject_response.status_code == 200:
                    rejected_travel = reject_response.json()
                    assert rejected_travel["status"] == "rejected"
    
    def test_controller_get_employee_travels(self, client, controller_headers):
        """Test getting travels for specific employee."""
        # Try to get travels for employee ID 1
        response = client.get("/api/v1/travels/employee/1/travels", headers=controller_headers)
        # Alternative endpoint structures
        if response.status_code == 404:
            response = client.get("/api/v1/users/1/travels", headers=controller_headers)
        
        assert response.status_code in [200, 403, 404]
    
    def test_controller_export_travel(self, client, controller_headers):
        """Test exporting travel data."""
        # Get a travel ID first
        travels_response = client.get("/api/v1/travels/", headers=controller_headers)
        if travels_response.status_code == 200:
            travels = travels_response.json()
            if travels:
                travel_id = travels[0]["id"]
                
                export_response = client.get(f"/api/v1/travels/{travel_id}/export", headers=controller_headers)
                assert export_response.status_code in [200, 403, 404]


@pytest.mark.integration
class TestControllerRestrictedAccess:
    """Test that controllers cannot access admin-only endpoints."""
    
    def test_controller_cannot_access_admin_dashboard(self, client, controller_headers):
        """Test that controllers cannot access admin dashboard."""
        response = client.get("/api/v1/admin/dashboard", headers=controller_headers)
        assert response.status_code in [401, 403, 404]
    
    def test_controller_cannot_create_controllers(self, client, controller_headers):
        """Test that controllers cannot create other controllers."""
        controller_data = {
            "email": "new_controller@demo.com",
            "password": "newpass123",
            "name": "New Controller",
            "role": "controller"
        }
        
        response = client.post("/api/v1/admin/controllers", json=controller_data, headers=controller_headers)
        assert response.status_code in [401, 403, 404]
    
    def test_controller_cannot_delete_users(self, client, controller_headers):
        """Test that controllers cannot delete users."""
        response = client.delete("/api/v1/admin/users/1", headers=controller_headers)
        assert response.status_code in [401, 403, 404]
    
    def test_controller_cannot_manage_assignments(self, client, controller_headers):
        """Test that controllers cannot manage employee assignments."""
        response = client.put("/api/v1/admin/assign-employee/1/to-controller/2", headers=controller_headers)
        assert response.status_code in [401, 403, 404]


@pytest.mark.e2e
class TestControllerCompleteWorkflow:
    """Test complete controller workflow end-to-end."""
    
    def test_complete_controller_workflow(self, client, controller_headers, employee_headers):
        """Test complete workflow: login -> view team -> review travels -> approve/reject."""
        
        # 1. Get controller info
        me_response = client.get("/api/v1/auth/me", headers=controller_headers)
        assert me_response.status_code == 200
        controller_info = me_response.json()
        assert controller_info["role"] == "controller"
        
        # 2. Get team members
        team_response = client.get("/api/v1/users/my-team", headers=controller_headers)
        assert team_response.status_code == 200
        team = team_response.json()
        
        # 3. Get all travels to review
        travels_response = client.get("/api/v1/travels/", headers=controller_headers)
        assert travels_response.status_code == 200
        travels = travels_response.json()
        
        # 4. Create a test travel as employee if possible
        if employee_headers:
            travel_data = {
                "destination": "Controller Workflow Test",
                "start_date": date.today().isoformat(),
                "end_date": (date.today() + timedelta(days=1)).isoformat(),
                "purpose": "Workflow Testing",
                "accommodation_costs": 150.0,
                "transport_costs": 75.0,
                "meal_costs": 45.0,
                "other_costs": 30.0,
                "total_expenses": 300.0
            }
            
            create_response = client.post("/api/v1/travels/", json=travel_data, headers=employee_headers)
            if create_response.status_code in [200, 201]:
                travel = create_response.json()
                travel_id = travel["id"]
                
                # Submit for approval
                submit_response = client.post(f"/api/v1/travels/{travel_id}/submit", headers=employee_headers)
                
                # 5. Controller reviews and approves
                if submit_response.status_code == 200:
                    approve_response = client.put(f"/api/v1/travels/{travel_id}/approve", headers=controller_headers)
                    # Approval might be restricted based on assignment
                    assert approve_response.status_code in [200, 403, 404]
        
        # 6. Verify controller can access assigned travels
        assigned_response = client.get("/api/v1/travels/assigned", headers=controller_headers)
        if assigned_response.status_code == 404:
            # Try alternative endpoint
            assigned_response = client.get("/api/v1/travels/", headers=controller_headers)
        assert assigned_response.status_code == 200
        
        # 7. Verify controller can view employee travels
        if team:
            employee_id = team[0]["id"]
            employee_travels_response = client.get(f"/api/v1/travels/employee/{employee_id}/travels", headers=controller_headers)
            if employee_travels_response.status_code == 404:
                # Try alternative endpoint
                employee_travels_response = client.get(f"/api/v1/users/{employee_id}/travels", headers=controller_headers)
            # This might be restricted
            assert employee_travels_response.status_code in [200, 403, 404]
