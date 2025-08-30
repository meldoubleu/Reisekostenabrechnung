"""
Test user API endpoints with comprehensive coverage.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.crud import crud_user
from backend.app.schemas.user import UserCreate, UserUpdate


class TestUserEndpoints:
    """Test user API endpoints that require admin access."""
    
    @pytest.mark.asyncio
    async def test_get_all_users_admin(self, client: AsyncClient, admin_headers: dict, test_db: AsyncSession):
        """Test admin can get all users."""
        # Create some test users first
        user_data = UserCreate(
            name="Test User",
            email="test.user@example.com",
            role="employee",
            company="Test Company",
            department="Test Department"
        )
        await crud_user.create(test_db, obj_in=user_data)
        
        response = await client.get("/api/v1/users/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should have at least one user (the one we created, plus the admin user from auth fixture)
        assert len(data) >= 1
        
        # Check user structure
        user = data[0]
        assert "id" in user
        assert "email" in user
        assert "name" in user
        assert "role" in user
        assert "company" in user
        assert "department" in user
    
    @pytest.mark.asyncio
    async def test_get_all_users_forbidden_employee(self, client: AsyncClient, employee_headers: dict):
        """Test employee cannot get all users."""
        response = await client.get("/api/v1/users/", headers=employee_headers)
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Admin access required"
    
    @pytest.mark.asyncio
    async def test_get_all_users_forbidden_controller(self, client: AsyncClient, controller_headers: dict):
        """Test controller cannot get all users."""
        response = await client.get("/api/v1/users/", headers=controller_headers)
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Admin access required"
    
    @pytest.mark.asyncio
    async def test_get_all_users_unauthorized(self, client: AsyncClient):
        """Test unauthorized access to users endpoint."""
        response = await client.get("/api/v1/users/")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_create_user_admin(self, client: AsyncClient, admin_headers: dict):
        """Test admin can create users."""
        user_data = {
            "name": "Test User API",
            "email": "test.user.api@example.com",
            "role": "employee",
            "company": "Test Company",
            "department": "Test Department",
            "cost_center": "TEST-002"
        }
        
        response = await client.post(
            "/api/v1/users/", 
            headers=admin_headers,
            json=user_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == user_data["name"]
        assert data["email"] == user_data["email"]
        assert data["role"] == user_data["role"]
        assert data["company"] == user_data["company"]
        assert data["department"] == user_data["department"]
        assert data["cost_center"] == user_data["cost_center"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client: AsyncClient, admin_headers: dict):
        """Test creating user with duplicate email fails."""
        # First create a user
        user_data = {
            "name": "First User",
            "email": "duplicate.test@example.com",
            "role": "employee",
            "company": "Test Company",
            "department": "Test Department"
        }
        
        response1 = await client.post(
            "/api/v1/users/", 
            headers=admin_headers,
            json=user_data
        )
        assert response1.status_code == 201  # First creation should succeed
        
        # Now try to create another with the same email
        user_data2 = {
            "name": "Second User",
            "email": "duplicate.test@example.com",  # Same email
            "role": "controller",
            "company": "Test Company 2",
            "department": "Test Department 2"
        }
        
        response2 = await client.post(
            "/api/v1/users/", 
            headers=admin_headers,
            json=user_data2
        )
        
        assert response2.status_code == 400
        data = response2.json()
        assert "already exists" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_create_user_forbidden(self, client: AsyncClient, employee_headers: dict):
        """Test non-admin cannot create users."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "employee",
            "company": "Test Company",
            "department": "Test Department"
        }
        
        response = await client.post(
            "/api/v1/users/", 
            headers=employee_headers,
            json=user_data
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_controllers_admin(self, client: AsyncClient, admin_headers: dict):
        """Test admin can get all controllers."""
        response = await client.get("/api/v1/users/controllers", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that all returned users are controllers
        for user in data:
            assert user["role"] == "controller"
            assert "employees" in user
    
    @pytest.mark.asyncio
    async def test_get_controllers_forbidden(self, client: AsyncClient, employee_headers: dict):
        """Test non-admin cannot get controllers list."""
        response = await client.get("/api/v1/users/controllers", headers=employee_headers)
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_admin(self, client: AsyncClient, admin_headers: dict, test_db: AsyncSession):
        """Test admin can get user by ID."""
        # Create a test user
        user_data = UserCreate(
            name="Test User By ID",
            email="test.user.by.id@example.com",
            role="employee",
            company="Test Company",
            department="Test"
        )
        user = await crud_user.create(test_db, obj_in=user_data)
        
        response = await client.get(f"/api/v1/users/{user.id}", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
        assert data["name"] == user.name
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, client: AsyncClient, admin_headers: dict):
        """Test getting nonexistent user returns 404."""
        response = await client.get("/api/v1/users/99999", headers=admin_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not found"
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_forbidden(self, client: AsyncClient, employee_headers: dict):
        """Test non-admin cannot get user by ID."""
        response = await client.get("/api/v1/users/1", headers=employee_headers)
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_admin(self, client: AsyncClient, admin_headers: dict, test_db: AsyncSession):
        """Test admin can get user by email."""
        # First create a user
        user_data = UserCreate(
            name="Max Mustermann",
            email="max.mustermann@test.com",
            role="employee",
            company="Test Company",
            department="Test Department"
        )
        created_user = await crud_user.create(test_db, obj_in=user_data)
        
        response = await client.get(
            f"/api/v1/users/email/{created_user.email}", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == created_user.email
        assert data["role"] == "employee"
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, client: AsyncClient, admin_headers: dict):
        """Test getting user by nonexistent email returns 404."""
        response = await client.get(
            "/api/v1/users/email/nonexistent@example.com", 
            headers=admin_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_user_admin(self, client: AsyncClient, admin_headers: dict, test_db: AsyncSession):
        """Test admin can update users."""
        # Create a test user
        user_data = UserCreate(
            name="Test User Update",
            email="test.user.update@example.com",
            role="employee",
            company="Test Company",
            department="Test"
        )
        user = await crud_user.create(test_db, obj_in=user_data)
        
        update_data = {
            "name": "Updated Test User",
            "department": "Updated Department"
        }
        
        response = await client.put(
            f"/api/v1/users/{user.id}", 
            headers=admin_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Test User"
        assert data["department"] == "Updated Department"
        assert data["email"] == user.email  # Should remain unchanged
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client: AsyncClient, admin_headers: dict):
        """Test updating nonexistent user returns 404."""
        update_data = {"name": "Updated Name"}
        
        response = await client.put(
            "/api/v1/users/99999", 
            headers=admin_headers,
            json=update_data
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_user_forbidden(self, client: AsyncClient, employee_headers: dict):
        """Test non-admin cannot update users."""
        update_data = {"name": "Updated Name"}
        
        response = await client.put(
            "/api/v1/users/1", 
            headers=employee_headers,
            json=update_data
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_assign_controller_to_employee_admin(self, client: AsyncClient, admin_headers: dict, test_db: AsyncSession):
        """Test admin can assign controller to employee."""
        # Create controller and employee
        controller_data = UserCreate(
            name="Test Controller Assign",
            email="test.controller.assign2@example.com",
            role="controller",
            company="Test Company",
            department="Management"
        )
        controller = await crud_user.create(test_db, obj_in=controller_data)
        
        employee_data = UserCreate(
            name="Test Employee Assign",
            email="test.employee.assign2@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        employee = await crud_user.create(test_db, obj_in=employee_data)
        
        response = await client.put(
            f"/api/v1/users/{employee.id}/assign-controller/{controller.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # The response should be the updated employee
        assert data["id"] == employee.id
        assert data["controller_id"] == controller.id
    
    @pytest.mark.asyncio
    async def test_assign_controller_not_found(self, client: AsyncClient, admin_headers: dict):
        """Test assigning with nonexistent employee or controller."""
        response = await client.put(
            "/api/v1/users/99999/assign-controller/99998",
            headers=admin_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_employees_by_controller_admin(self, client: AsyncClient, admin_headers: dict):
        """Test admin can get employees by controller."""
        # Use existing controller from demo data
        response = await client.get(
            "/api/v1/users/controller/1/employees", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All returned users should be employees
        for user in data:
            assert user["role"] == "employee"
            assert user["controller_id"] == 1
    
    @pytest.mark.asyncio
    async def test_get_employees_by_controller_forbidden(self, client: AsyncClient, employee_headers: dict):
        """Test non-admin cannot get employees by controller."""
        response = await client.get(
            "/api/v1/users/controller/1/employees", 
            headers=employee_headers
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_delete_user_admin(self, client: AsyncClient, admin_headers: dict, test_db: AsyncSession):
        """Test admin can delete users."""
        # Create a test user
        user_data = UserCreate(
            name="Test User Delete",
            email="test.user.delete2@example.com",
            role="employee",
            company="Test Company",
            department="Test"
        )
        user = await crud_user.create(test_db, obj_in=user_data)
        
        response = await client.delete(f"/api/v1/users/{user.id}", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, client: AsyncClient, admin_headers: dict):
        """Test deleting nonexistent user returns 404."""
        response = await client.delete("/api/v1/users/99999", headers=admin_headers)
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_user_forbidden(self, client: AsyncClient, employee_headers: dict):
        """Test non-admin cannot delete users."""
        response = await client.delete("/api/v1/users/1", headers=employee_headers)
        
        assert response.status_code == 403


class TestUserEndpointsPagination:
    """Test pagination and filtering on user endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_users_with_pagination(self, client: AsyncClient, admin_headers: dict):
        """Test user list endpoint with pagination parameters."""
        response = await client.get(
            "/api/v1/users/?skip=0&limit=5", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    @pytest.mark.asyncio
    async def test_get_employees_by_controller_with_pagination(self, client: AsyncClient, admin_headers: dict):
        """Test employees by controller endpoint with pagination."""
        response = await client.get(
            "/api/v1/users/controller/1/employees?skip=0&limit=10", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
