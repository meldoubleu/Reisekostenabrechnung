"""
Test admin API endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.crud import crud_user
from backend.app.schemas.user import UserCreate


class TestAdminEndpoints:
    """Test admin-only API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_admin_dashboard_success(self, client: AsyncClient, admin_headers: dict):
        """Test successful admin dashboard access."""
        response = await client.get("/api/v1/admin/dashboard", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check dashboard structure
        assert "statistics" in data
        assert "controllers" in data
        assert "unassigned_employees" in data
        
        # Check statistics structure
        stats = data["statistics"]
        assert "total_controllers" in stats
        assert "total_employees" in stats
        assert "assigned_employees" in stats
        assert "unassigned_employees" in stats
        
        # Check that all values are integers
        assert isinstance(stats["total_controllers"], int)
        assert isinstance(stats["total_employees"], int)
        assert isinstance(stats["assigned_employees"], int)
        assert isinstance(stats["unassigned_employees"], int)
    
    @pytest.mark.asyncio
    async def test_get_admin_dashboard_unauthorized(self, client: AsyncClient):
        """Test admin dashboard access without authentication."""
        response = await client.get("/api/v1/admin/dashboard")
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_admin_dashboard_forbidden_employee(self, client: AsyncClient, employee_headers: dict):
        """Test admin dashboard access as employee (should be forbidden)."""
        response = await client.get("/api/v1/admin/dashboard", headers=employee_headers)
        assert response.status_code == 403
        
        data = response.json()
        assert data["detail"] == "Admin access required"
    
    @pytest.mark.asyncio
    async def test_get_admin_dashboard_forbidden_controller(self, client: AsyncClient, controller_headers: dict):
        """Test admin dashboard access as controller (should be forbidden)."""
        response = await client.get("/api/v1/admin/dashboard", headers=controller_headers)
        assert response.status_code == 403
        
        data = response.json()
        assert data["detail"] == "Admin access required"

    @pytest.mark.asyncio
    async def test_create_controller_success(self, client: AsyncClient, admin_headers: dict):
        """Test successful controller creation."""
        controller_data = {
            "name": "Test Controller Admin",
            "email": "test.controller.admin@example.com",
            "role": "controller",
            "company": "Test Company",
            "department": "Test Department"
        }
        
        response = await client.post(
            "/api/v1/admin/controllers", 
            headers=admin_headers,
            json=controller_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == controller_data["name"]
        assert data["email"] == controller_data["email"]
        assert data["role"] == "controller"
        assert data["company"] == controller_data["company"]
        assert data["department"] == controller_data["department"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_controller_duplicate_email(self, client: AsyncClient, admin_headers: dict):
        """Test controller creation with duplicate email."""
        # First create a controller
        controller_data = {
            "name": "First Controller",
            "email": "duplicate@test.com",
            "role": "controller",
            "company": "Test Company",
            "department": "Test Department"
        }
        
        response1 = await client.post(
            "/api/v1/admin/controllers", 
            headers=admin_headers,
            json=controller_data
        )
        assert response1.status_code == 201  # First creation should succeed
        
        # Now try to create another with the same email
        controller_data2 = {
            "name": "Second Controller",
            "email": "duplicate@test.com",  # Same email
            "role": "controller",
            "company": "Test Company 2",
            "department": "Test Department 2"
        }
        
        response2 = await client.post(
            "/api/v1/admin/controllers", 
            headers=admin_headers,
            json=controller_data2
        )
        
        assert response2.status_code == 400
        data = response2.json()
        assert "already exists" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_create_controller_unauthorized(self, client: AsyncClient):
        """Test controller creation without authentication."""
        controller_data = {
            "name": "Test Controller",
            "email": "test@example.com",
            "role": "controller",
            "company": "Test Company",
            "department": "Test Department"
        }
        
        response = await client.post("/api/v1/admin/controllers", json=controller_data)
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_create_employee_success(self, client: AsyncClient, admin_headers: dict):
        """Test successful employee creation."""
        employee_data = {
            "name": "Test Employee Admin",
            "email": "test.employee.admin@example.com",
            "role": "employee",
            "company": "Test Company",
            "department": "Test Department",
            "cost_center": "TEST-001"
        }
        
        response = await client.post(
            "/api/v1/admin/employees", 
            headers=admin_headers,
            json=employee_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == employee_data["name"]
        assert data["email"] == employee_data["email"]
        assert data["role"] == "employee"
        assert data["company"] == employee_data["company"]
        assert data["department"] == employee_data["department"]
        assert data["cost_center"] == employee_data["cost_center"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_employee_forbidden(self, client: AsyncClient, employee_headers: dict):
        """Test employee creation as non-admin (should be forbidden)."""
        employee_data = {
            "name": "Test Employee",
            "email": "test@example.com", 
            "role": "employee",
            "company": "Test Company",
            "department": "Test Department"
        }
        
        response = await client.post(
            "/api/v1/admin/employees", 
            headers=employee_headers,
            json=employee_data
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_assign_employee_to_controller_success(self, client: AsyncClient, admin_headers: dict, test_db: AsyncSession):
        """Test successful employee assignment to controller."""
        # Create a controller and employee for testing
        controller_data = UserCreate(
            name="Test Controller Assign",
            email="test.controller.assign@example.com",
            role="controller",
            company="Test Company",
            department="Management"
        )
        controller = await crud_user.create(test_db, obj_in=controller_data)
        
        employee_data = UserCreate(
            name="Test Employee Assign",
            email="test.employee.assign@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        employee = await crud_user.create(test_db, obj_in=employee_data)
        
        response = await client.put(
            f"/api/v1/admin/assign-employee/{employee.id}/to-controller/{controller.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "assigned" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_assign_employee_nonexistent(self, client: AsyncClient, admin_headers: dict):
        """Test assignment with nonexistent employee or controller."""
        response = await client.put(
            "/api/v1/admin/assign-employee/99999/to-controller/99998",
            headers=admin_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_unassign_employee_success(self, client: AsyncClient, admin_headers: dict, test_db: AsyncSession):
        """Test successful employee unassignment."""
        # Create and assign an employee to a controller
        controller_data = UserCreate(
            name="Test Controller Unassign",
            email="test.controller.unassign@example.com",
            role="controller",
            company="Test Company",
            department="Management"
        )
        controller = await crud_user.create(test_db, obj_in=controller_data)
        
        employee_data = UserCreate(
            name="Test Employee Unassign",
            email="test.employee.unassign@example.com",
            role="employee",
            company="Test Company",
            department="Sales",
            controller_id=controller.id
        )
        employee = await crud_user.create(test_db, obj_in=employee_data)
        
        response = await client.put(
            f"/api/v1/admin/unassign-employee/{employee.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "unassigned" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, client: AsyncClient, admin_headers: dict, test_db: AsyncSession):
        """Test successful user deletion."""
        # Create a user for deletion
        user_data = UserCreate(
            name="Test User Delete",
            email="test.user.delete@example.com",
            role="employee",
            company="Test Company",
            department="Test"
        )
        user = await crud_user.create(test_db, obj_in=user_data)
        
        response = await client.delete(
            f"/api/v1/admin/users/{user.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_delete_user_nonexistent(self, client: AsyncClient, admin_headers: dict):
        """Test deletion of nonexistent user."""
        response = await client.delete(
            "/api/v1/admin/users/99999",
            headers=admin_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_user_forbidden(self, client: AsyncClient, employee_headers: dict):
        """Test user deletion as non-admin."""
        response = await client.delete(
            "/api/v1/admin/users/1",
            headers=employee_headers
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_all_travels_admin(self, client: AsyncClient, admin_headers: dict):
        """Test admin access to all travel requests."""
        response = await client.get("/api/v1/admin/travels", headers=admin_headers)
        
        # Should work even if no travels exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_all_travels_forbidden(self, client: AsyncClient, employee_headers: dict):
        """Test non-admin access to all travels (should be forbidden)."""
        response = await client.get("/api/v1/admin/travels", headers=employee_headers)
        assert response.status_code == 403


class TestAdminDashboardDataIntegrity:
    """Test admin dashboard data integrity and consistency."""
    
    @pytest.mark.asyncio
    async def test_dashboard_statistics_consistency(self, client: AsyncClient, admin_headers: dict):
        """Test that dashboard statistics are mathematically consistent."""
        response = await client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        stats = data["statistics"]
        
        # Total employees should equal assigned + unassigned
        total_employees = stats["total_employees"]
        assigned_employees = stats["assigned_employees"]
        unassigned_employees = stats["unassigned_employees"]
        
        assert total_employees == assigned_employees + unassigned_employees
        
        # Check that actual data matches statistics
        controllers = data["controllers"]
        unassigned_list = data["unassigned_employees"]
        
        # Count employees from controllers
        actual_assigned = sum(len(controller["employees"]) for controller in controllers)
        assert actual_assigned == assigned_employees
        
        # Count unassigned employees
        actual_unassigned = len(unassigned_list)
        assert actual_unassigned == unassigned_employees
        
        # Count controllers
        actual_controllers = len(controllers)
        assert actual_controllers == stats["total_controllers"]
    
    @pytest.mark.asyncio
    async def test_controller_employee_relationships(self, client: AsyncClient, admin_headers: dict):
        """Test that controller-employee relationships are properly represented."""
        response = await client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        controllers = data["controllers"]
        
        for controller in controllers:
            # Each controller should have required fields
            assert "id" in controller
            assert "name" in controller
            assert "email" in controller
            assert "department" in controller
            assert "employees" in controller
            assert "employee_count" in controller
            
            # Employee count should match actual employees list
            assert controller["employee_count"] == len(controller["employees"])
            
            # Each employee should have required fields
            for employee in controller["employees"]:
                assert "id" in employee
                assert "name" in employee
                assert "email" in employee
                assert "department" in employee
                # cost_center can be None, so just check it exists
                assert "cost_center" in employee
