"""
Comprehensive tests for controller-specific functionality.
Tests the new /my-team endpoint and controller access controls.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User, UserRole
from backend.app.crud import crud_user
from backend.app.schemas.user import UserCreate


class TestControllerAPI:
    """Test controller-specific API endpoints and functionality."""
    
    @pytest.mark.asyncio
    async def test_my_team_endpoint_success(self, client: AsyncClient, test_db: AsyncSession):
        """Test controller can access their assigned team via /my-team endpoint."""
        
        # Use a known controller ID from the mock mapping and database (ID 1 = controller1@demo.com)
        controller_id = 1
        
        # Create controller authentication headers using the real controller from database
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(controller_id),
            "email": "controller1@demo.com",
            "name": "Anna Controlling",
            "role": "controller"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test /my-team endpoint - this should return the employees actually assigned to controller ID 1
        response = await client.get("/api/v1/users/my-team", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure and that we get actual assigned employees
        assert isinstance(data, list)
        
        # Check the structure of returned employees (if any)
        for employee in data:
            assert "id" in employee
            assert "name" in employee
            assert "email" in employee
            assert "role" in employee
            assert "department" in employee
            assert "controller_id" in employee
            assert employee["role"] == "employee"
            assert employee["controller_id"] == controller_id
    
    @pytest.mark.asyncio
    async def test_my_team_endpoint_no_employees(self, client: AsyncClient, test_db: AsyncSession):
        """Test /my-team endpoint when controller has no assigned employees."""
        
        # Create a controller with no assigned employees
        controller_data = UserCreate(
            name="Lonely Controller",
            email="lonely.controller@example.com",
            role="controller",
            company="Test Company",
            department="Test Department",
            password_hash="hashed_password"
        )
        controller = await crud_user.create(test_db, obj_in=controller_data)
        
        # Create controller authentication headers
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(controller.id),
            "email": controller.email,
            "name": controller.name,
            "role": "controller"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test /my-team endpoint
        response = await client.get("/api/v1/users/my-team", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty list
        assert data == []
    
    @pytest.mark.asyncio
    async def test_my_team_endpoint_unauthorized(self, client: AsyncClient):
        """Test /my-team endpoint without authentication."""
        response = await client.get("/api/v1/users/my-team")
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_my_team_endpoint_forbidden_employee(self, client: AsyncClient, test_db: AsyncSession):
        """Test employee cannot access /my-team endpoint."""
        
        # Use a known employee ID from the mock mapping (ID 3 = employee)
        employee_id = 3
        
        # Create employee authentication headers using mock ID
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(employee_id),
            "email": "max.mustermann@demo.com",
            "name": "Max Mustermann",
            "role": "employee"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test /my-team endpoint should be forbidden for employees
        response = await client.get("/api/v1/users/my-team", headers=headers)
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Controller access required"
    
    @pytest.mark.asyncio
    async def test_my_team_endpoint_forbidden_admin(self, client: AsyncClient, test_db: AsyncSession):
        """Test admin cannot access /my-team endpoint (controller-specific)."""
        
        # Use a known admin ID from the mock mapping (ID 7 = admin)
        admin_id = 7
        
        # Create admin authentication headers using mock ID
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(admin_id),
            "email": "admin@demo.com",
            "name": "System Administrator",
            "role": "admin"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test /my-team endpoint should be forbidden for admins
        response = await client.get("/api/v1/users/my-team", headers=headers)
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Controller access required"
    
    @pytest.mark.asyncio
    async def test_multiple_controllers_separate_teams(self, client: AsyncClient, test_db: AsyncSession):
        """Test that different controllers only see their own assigned employees."""
        
        # Create two controllers
        controller1_data = UserCreate(
            name="Controller One",
            email="controller1@example.com",
            role="controller",
            company="Test Company",
            department="Finance",
            password_hash="hashed_password"
        )
        controller1 = await crud_user.create(test_db, obj_in=controller1_data)
        
        controller2_data = UserCreate(
            name="Controller Two",
            email="controller2@example.com",
            role="controller",
            company="Test Company",
            department="HR",
            password_hash="hashed_password"
        )
        controller2 = await crud_user.create(test_db, obj_in=controller2_data)
        
        # Create employees for controller1
        emp1_data = UserCreate(
            name="Employee for Controller 1",
            email="emp1@example.com",
            role="employee",
            company="Test Company",
            department="Sales",
            controller_id=controller1.id,
            password_hash="hashed_password"
        )
        emp1 = await crud_user.create(test_db, obj_in=emp1_data)
        
        # Create employees for controller2
        emp2_data = UserCreate(
            name="Employee for Controller 2",
            email="emp2@example.com",
            role="employee",
            company="Test Company",
            department="Marketing",
            controller_id=controller2.id,
            password_hash="hashed_password"
        )
        emp2 = await crud_user.create(test_db, obj_in=emp2_data)
        
        # Test controller1 sees only their employee
        from backend.app.core.auth import create_access_token
        token1 = create_access_token(data={
            "sub": str(controller1.id),
            "email": controller1.email,
            "name": controller1.name,
            "role": "controller"
        })
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        response1 = await client.get("/api/v1/users/my-team", headers=headers1)
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 1
        assert data1[0]["email"] == emp1.email
        assert data1[0]["controller_id"] == controller1.id
        
        # Test controller2 sees only their employee
        token2 = create_access_token(data={
            "sub": str(controller2.id),
            "email": controller2.email,
            "name": controller2.name,
            "role": "controller"
        })
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        response2 = await client.get("/api/v1/users/my-team", headers=headers2)
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 1
        assert data2[0]["email"] == emp2.email
        assert data2[0]["controller_id"] == controller2.id


class TestControllerRoleBasedAccess:
    """Test controller role-based access controls for various endpoints."""
    
    @pytest.mark.asyncio
    async def test_controller_cannot_access_admin_endpoints(self, client: AsyncClient, test_db: AsyncSession):
        """Test that controllers cannot access admin-only endpoints."""
        
        # Use a known controller ID from the mock mapping (ID 1 = controller)
        controller_id = 1
        
        # Create controller authentication headers using mock ID
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(controller_id),
            "email": "controller1@demo.com",
            "name": "Anna Controlling",
            "role": "controller"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test admin endpoints that should be forbidden
        admin_endpoints = [
            "/api/v1/admin/dashboard",
            "/api/v1/admin/controller-assignments",
            "/api/v1/admin/travels",
            "/api/v1/users/",  # Get all users (admin only)
            "/api/v1/users/controllers",  # Get all controllers (admin only)
        ]
        
        for endpoint in admin_endpoints:
            response = await client.get(endpoint, headers=headers)
            assert response.status_code == 403, f"Controller should not access {endpoint}, got {response.status_code}"
            data = response.json()
            assert "Admin access required" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_controller_can_access_own_data(self, client: AsyncClient, test_db: AsyncSession):
        """Test that controllers can access their own user data."""
        
        # Create a controller
        controller_data = UserCreate(
            name="Self Access Controller",
            email="selfaccess.controller@example.com",
            role="controller",
            company="Test Company", 
            department="Test Department",
            password_hash="hashed_password"
        )
        controller = await crud_user.create(test_db, obj_in=controller_data)
        
        # Create controller authentication headers
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(controller.id),
            "email": controller.email,
            "name": controller.name,
            "role": "controller"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test /me endpoint (should work)
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == controller.id
        assert data["email"] == controller.email
        assert data["role"] == "controller"
