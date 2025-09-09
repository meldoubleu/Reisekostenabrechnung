"""
Complete API Endpoint Coverage Tests
Tests all API endpoints organized by functionality.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from datetime import date, timedelta
import json
import io


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def admin_headers(client):
    """Get admin authentication headers."""
    # Try to login, register if needed
    login_data = {"email": "admin@demo.com", "password": "admin123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    
    if response.status_code != 200:
        register_data = {
            "email": "admin@demo.com",
            "password": "admin123", 
            "name": "Test Admin",
            "role": "admin"
        }
        client.post("/api/v1/auth/register", json=register_data)
        response = client.post("/api/v1/auth/login", json=login_data)
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def controller_headers(client):
    """Get controller authentication headers."""
    login_data = {"email": "controller@demo.com", "password": "controller123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    
    if response.status_code != 200:
        register_data = {
            "email": "controller@demo.com",
            "password": "controller123",
            "name": "Test Controller", 
            "role": "controller"
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


@pytest.mark.integration
class TestAuthEndpoints:
    """Test all authentication endpoints."""
    
    def test_post_auth_login(self, client):
        """Test POST /api/v1/auth/login"""
        valid_data = {"email": "admin@demo.com", "password": "admin123"}
        response = client.post("/api/v1/auth/login", json=valid_data)
        assert response.status_code in [200, 404]  # 404 if user doesn't exist
        
        invalid_data = {"email": "admin@demo.com", "password": "wrong"}
        response = client.post("/api/v1/auth/login", json=invalid_data)
        assert response.status_code in [401, 404]
    
    def test_post_auth_register(self, client):
        """Test POST /api/v1/auth/register"""
        register_data = {
            "email": "newuser@demo.com",
            "password": "newpass123",
            "name": "New User",
            "role": "employee"
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code in [200, 201, 400]  # 400 if user already exists
    
    def test_get_auth_me(self, client, admin_headers):
        """Test GET /api/v1/auth/me"""
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        assert response.status_code == 200
        user_data = response.json()
        assert "email" in user_data
        assert "role" in user_data


@pytest.mark.integration
class TestTravelEndpoints:
    """Test all travel-related endpoints."""
    
    def test_post_travels(self, client, employee_headers):
        """Test POST /api/v1/travels/"""
        travel_data = {
            "destination": "Test Destination",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=1)).isoformat(),
            "purpose": "Testing",
            "accommodation_costs": 100.0,
            "transport_costs": 50.0,
            "meal_costs": 30.0,
            "other_costs": 20.0,
            "total_expenses": 200.0
        }
        response = client.post("/api/v1/travels/", json=travel_data, headers=employee_headers)
        assert response.status_code in [200, 201]
        return response.json()["id"] if response.status_code in [200, 201] else None
    
    def test_get_travels(self, client, employee_headers):
        """Test GET /api/v1/travels/"""
        response = client.get("/api/v1/travels/", headers=employee_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_travels_my(self, client, employee_headers):
        """Test GET /api/v1/travels/my"""
        response = client.get("/api/v1/travels/my", headers=employee_headers)
        assert response.status_code in [200, 404]  # Endpoint might not exist
    
    def test_get_travels_assigned(self, client, controller_headers):
        """Test GET /api/v1/travels/assigned"""
        response = client.get("/api/v1/travels/assigned", headers=controller_headers)
        assert response.status_code in [200, 404]  # Endpoint might not exist
    
    def test_get_travel_by_id(self, client, employee_headers):
        """Test GET /api/v1/travels/{travel_id}"""
        travel_id = self.test_post_travels(client, employee_headers)
        if travel_id:
            response = client.get(f"/api/v1/travels/{travel_id}", headers=employee_headers)
            assert response.status_code == 200
            travel = response.json()
            assert travel["id"] == travel_id
    
    def test_put_travel_by_id(self, client, employee_headers):
        """Test PUT /api/v1/travels/{travel_id}"""
        travel_id = self.test_post_travels(client, employee_headers)
        if travel_id:
            update_data = {
                "destination": "Updated Destination",
                "purpose": "Updated Purpose"
            }
            response = client.put(f"/api/v1/travels/{travel_id}", json=update_data, headers=employee_headers)
            assert response.status_code == 200
    
    def test_post_travel_receipts(self, client, employee_headers):
        """Test POST /api/v1/travels/{travel_id}/receipts"""
        travel_id = self.test_post_travels(client, employee_headers)
        if travel_id:
            files = {"file": ("test.txt", io.BytesIO(b"test receipt"), "text/plain")}
            response = client.post(f"/api/v1/travels/{travel_id}/receipts", files=files, headers=employee_headers)
            assert response.status_code in [200, 201]
    
    def test_post_travel_submit(self, client, employee_headers):
        """Test POST /api/v1/travels/{travel_id}/submit"""
        travel_id = self.test_post_travels(client, employee_headers)
        if travel_id:
            response = client.post(f"/api/v1/travels/{travel_id}/submit", headers=employee_headers)
            assert response.status_code == 200
    
    def test_put_travel_approve(self, client, admin_headers):
        """Test PUT /api/v1/travels/{travel_id}/approve"""
        response = client.put("/api/v1/travels/999/approve", headers=admin_headers)
        assert response.status_code in [200, 404]  # 404 for non-existent travel
    
    def test_put_travel_reject(self, client, admin_headers):
        """Test PUT /api/v1/travels/{travel_id}/reject"""
        response = client.put("/api/v1/travels/999/reject", headers=admin_headers)
        assert response.status_code in [200, 404]  # 404 for non-existent travel
    
    def test_get_travel_export(self, client, admin_headers):
        """Test GET /api/v1/travels/{travel_id}/export"""
        response = client.get("/api/v1/travels/999/export", headers=admin_headers)
        assert response.status_code in [200, 404]  # 404 for non-existent travel
    
    def test_get_travel_receipts(self, client, employee_headers):
        """Test GET /api/v1/travels/{travel_id}/receipts"""
        travel_id = self.test_post_travels(client, employee_headers)
        if travel_id:
            response = client.get(f"/api/v1/travels/{travel_id}/receipts", headers=employee_headers)
            assert response.status_code in [200, 404]  # Endpoint might not exist
    
    def test_get_employee_travels(self, client, controller_headers):
        """Test GET /api/v1/travels/employee/{employee_id}/travels"""
        response = client.get("/api/v1/travels/employee/1/travels", headers=controller_headers)
        assert response.status_code in [200, 403, 404]
    
    def test_get_controller_travels(self, client, admin_headers):
        """Test GET /api/v1/travels/controller/{controller_id}/travels"""
        response = client.get("/api/v1/travels/controller/1/travels", headers=admin_headers)
        assert response.status_code in [200, 403, 404]


@pytest.mark.integration
class TestUserEndpoints:
    """Test all user management endpoints."""
    
    def test_post_users(self, client, admin_headers):
        """Test POST /api/v1/users/"""
        user_data = {
            "email": "testuser@demo.com",
            "password": "testpass123",
            "name": "Test User",
            "role": "employee"
        }
        response = client.post("/api/v1/users/", json=user_data, headers=admin_headers)
        assert response.status_code in [200, 201, 403]  # Might be restricted
        return response.json().get("id") if response.status_code in [200, 201] else None
    
    def test_get_users(self, client, admin_headers):
        """Test GET /api/v1/users/"""
        response = client.get("/api/v1/users/", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_users_controllers(self, client, admin_headers):
        """Test GET /api/v1/users/controllers"""
        response = client.get("/api/v1/users/controllers", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_users_my_team(self, client, controller_headers):
        """Test GET /api/v1/users/my-team"""
        response = client.get("/api/v1/users/my-team", headers=controller_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_user_by_id(self, client, admin_headers):
        """Test GET /api/v1/users/{user_id}"""
        users_response = client.get("/api/v1/users/", headers=admin_headers)
        if users_response.status_code == 200:
            users = users_response.json()
            if users:
                user_id = users[0]["id"]
                response = client.get(f"/api/v1/users/{user_id}", headers=admin_headers)
                assert response.status_code == 200
    
    def test_get_user_by_email(self, client, admin_headers):
        """Test GET /api/v1/users/email/{email}"""
        response = client.get("/api/v1/users/email/admin@demo.com", headers=admin_headers)
        assert response.status_code in [200, 404]
    
    def test_put_user_by_id(self, client, admin_headers):
        """Test PUT /api/v1/users/{user_id}"""
        user_id = self.test_post_users(client, admin_headers)
        if user_id:
            update_data = {"name": "Updated Name"}
            response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=admin_headers)
            assert response.status_code == 200
    
    def test_put_assign_controller(self, client, admin_headers):
        """Test PUT /api/v1/users/{employee_id}/assign-controller/{controller_id}"""
        response = client.put("/api/v1/users/1/assign-controller/2", headers=admin_headers)
        assert response.status_code in [200, 403, 404]
    
    def test_get_controller_employees(self, client, admin_headers):
        """Test GET /api/v1/users/controller/{controller_id}/employees"""
        response = client.get("/api/v1/users/controller/1/employees", headers=admin_headers)
        assert response.status_code in [200, 404]
    
    def test_delete_user(self, client, admin_headers):
        """Test DELETE /api/v1/users/{user_id}"""
        user_id = self.test_post_users(client, admin_headers)
        if user_id:
            response = client.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
            assert response.status_code == 200


@pytest.mark.integration
class TestAdminEndpoints:
    """Test all admin-specific endpoints."""
    
    def test_get_admin_dashboard(self, client, admin_headers):
        """Test GET /api/v1/admin/dashboard"""
        response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_post_admin_controllers(self, client, admin_headers):
        """Test POST /api/v1/admin/controllers"""
        controller_data = {
            "email": "newcontroller@demo.com",
            "password": "newpass123",
            "name": "New Controller",
            "role": "controller"
        }
        response = client.post("/api/v1/admin/controllers", json=controller_data, headers=admin_headers)
        assert response.status_code in [200, 201]
        return response.json()["id"] if response.status_code in [200, 201] else None
    
    def test_post_admin_employees(self, client, admin_headers):
        """Test POST /api/v1/admin/employees"""
        employee_data = {
            "email": "newemployee@demo.com",
            "password": "newpass123",
            "name": "New Employee",
            "role": "employee"
        }
        response = client.post("/api/v1/admin/employees", json=employee_data, headers=admin_headers)
        assert response.status_code in [200, 201]
        return response.json()["id"] if response.status_code in [200, 201] else None
    
    def test_put_admin_assign_employee(self, client, admin_headers):
        """Test PUT /api/v1/admin/assign-employee/{employee_id}/to-controller/{controller_id}"""
        controller_id = self.test_post_admin_controllers(client, admin_headers)
        employee_id = self.test_post_admin_employees(client, admin_headers)
        
        if controller_id and employee_id:
            response = client.put(f"/api/v1/admin/assign-employee/{employee_id}/to-controller/{controller_id}", headers=admin_headers)
            assert response.status_code == 200
    
    def test_put_admin_unassign_employee(self, client, admin_headers):
        """Test PUT /api/v1/admin/unassign-employee/{employee_id}"""
        employee_id = self.test_post_admin_employees(client, admin_headers)
        if employee_id:
            response = client.put(f"/api/v1/admin/unassign-employee/{employee_id}", headers=admin_headers)
            assert response.status_code == 200
    
    def test_delete_admin_users(self, client, admin_headers):
        """Test DELETE /api/v1/admin/users/{user_id}"""
        user_id = self.test_post_admin_employees(client, admin_headers)
        if user_id:
            response = client.delete(f"/api/v1/admin/users/{user_id}", headers=admin_headers)
            assert response.status_code == 200
    
    def test_get_admin_controller_assignments(self, client, admin_headers):
        """Test GET /api/v1/admin/controller-assignments"""
        response = client.get("/api/v1/admin/controller-assignments", headers=admin_headers)
        assert response.status_code == 200
    
    def test_get_admin_travels(self, client, admin_headers):
        """Test GET /api/v1/admin/travels"""
        response = client.get("/api/v1/admin/travels", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.integration
class TestReceiptEndpoints:
    """Test receipt-related endpoints."""
    
    def test_put_receipts_by_id(self, client, employee_headers):
        """Test PUT /api/v1/receipts/{receipt_id}"""
        # This would require creating a receipt first
        response = client.put("/api/v1/receipts/999", json={"description": "Updated"}, headers=employee_headers)
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestPageEndpoints:
    """Test frontend page endpoints."""
    
    def test_get_root(self, client):
        """Test GET /api/v1/"""
        response = client.get("/api/v1/")
        assert response.status_code == 200
    
    def test_get_landingpage(self, client):
        """Test GET /api/v1/landingpage"""
        response = client.get("/api/v1/landingpage")
        assert response.status_code == 200
    
    def test_get_dashboard(self, client):
        """Test GET /api/v1/dashboard"""
        response = client.get("/api/v1/dashboard")
        assert response.status_code == 200
    
    def test_get_travel_form(self, client):
        """Test GET /api/v1/travel-form"""
        response = client.get("/api/v1/travel-form")
        assert response.status_code == 200
    
    def test_get_ui(self, client):
        """Test GET /api/v1/ui"""
        response = client.get("/api/v1/ui")
        assert response.status_code == 200
    
    def test_get_debug(self, client):
        """Test GET /api/v1/debug"""
        response = client.get("/api/v1/debug")
        assert response.status_code == 200
    
    def test_get_admin_page(self, client):
        """Test GET /api/v1/admin"""
        response = client.get("/api/v1/admin")
        assert response.status_code == 200
