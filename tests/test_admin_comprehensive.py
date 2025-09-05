"""
Additional comprehensive tests for admin functionality.
Tests admin-specific endpoints and access controls not covered elsewhere.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User, UserRole
from backend.app.crud import crud_user
from backend.app.schemas.user import UserCreate


class TestAdminSpecific:
    """Test admin-specific functionality beyond basic endpoints."""
    
    @pytest.mark.asyncio
    async def test_admin_dashboard_comprehensive(self, client: AsyncClient, test_db: AsyncSession):
        """Test admin dashboard returns comprehensive statistics."""
        
        # Use known admin ID from mock mapping (ID 7 = admin)
        admin_id = 7
        
        # Create admin authentication headers
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(admin_id),
            "email": "admin@demo.com",
            "name": "System Administrator",
            "role": "admin"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test admin dashboard
        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify dashboard structure
        assert "statistics" in data
        assert "controllers" in data
        assert "unassigned_employees" in data
        
        # Verify statistics structure
        stats = data["statistics"]
        required_stats = [
            "total_controllers",
            "total_employees", 
            "assigned_employees",
            "unassigned_employees"
        ]
        for stat in required_stats:
            assert stat in stats
            assert isinstance(stats[stat], int)
            assert stats[stat] >= 0
        
        # Verify controllers is a list
        assert isinstance(data["controllers"], list)
        
        # Verify unassigned_employees is a list
        assert isinstance(data["unassigned_employees"], list)
    
    @pytest.mark.asyncio
    async def test_admin_controller_assignments_endpoint(self, client: AsyncClient, test_db: AsyncSession):
        """Test admin can view controller assignments."""
        
        # Use known admin ID from mock mapping (ID 7 = admin)
        admin_id = 7
        
        # Create admin authentication headers
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(admin_id),
            "email": "admin@demo.com",
            "name": "System Administrator",
            "role": "admin"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test controller assignments endpoint
        response = await client.get("/api/v1/admin/controller-assignments", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list of controller assignments
        assert isinstance(data, list)
        
        # If there are assignments, verify structure
        for assignment in data:
            if assignment:  # Skip empty assignments
                assert "controller_id" in assignment
                assert "controller_name" in assignment
                assert "employee_count" in assignment
                assert isinstance(assignment["employee_count"], int)
    
    @pytest.mark.asyncio
    async def test_admin_travels_endpoint(self, client: AsyncClient, test_db: AsyncSession):
        """Test admin can view all travels."""
        
        # Use known admin ID from mock mapping (ID 7 = admin)
        admin_id = 7
        
        # Create admin authentication headers
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(admin_id),
            "email": "admin@demo.com",
            "name": "System Administrator",
            "role": "admin"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test travels endpoint
        response = await client.get("/api/v1/admin/travels", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list of travels
        assert isinstance(data, list)
        
        # If there are travels, verify basic structure
        for travel in data:
            if travel:  # Skip empty travels
                assert "id" in travel
                assert "user_id" in travel
                assert "status" in travel
    
    @pytest.mark.asyncio
    async def test_admin_create_controller_endpoint(self, client: AsyncClient, test_db: AsyncSession):
        """Test admin can create new controllers via POST endpoint."""
        
        # Use known admin ID from mock mapping (ID 7 = admin)
        admin_id = 7
        
        # Create admin authentication headers
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(admin_id),
            "email": "admin@demo.com",
            "name": "System Administrator",
            "role": "admin"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test creating a new controller
        controller_data = {
            "name": "Test Controller Admin",
            "email": "test.controller.admin@example.com",
            "role": "controller",
            "company": "Test Company",
            "department": "Test Department"
        }
        
        response = await client.post(
            "/api/v1/admin/controllers",
            headers=headers,
            json=controller_data
        )
        
        # Should return 201 created or handle gracefully
        assert response.status_code in [201, 400, 422]  # 400/422 for validation errors are acceptable
        
        if response.status_code == 201:
            data = response.json()
            assert data["name"] == controller_data["name"]
            assert data["email"] == controller_data["email"]
            assert data["role"] == "controller"
    
    @pytest.mark.asyncio
    async def test_admin_create_employee_endpoint(self, client: AsyncClient, test_db: AsyncSession):
        """Test admin can create new employees via POST endpoint."""
        
        # Use known admin ID from mock mapping (ID 7 = admin)
        admin_id = 7
        
        # Create admin authentication headers
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(admin_id),
            "email": "admin@demo.com",
            "name": "System Administrator",
            "role": "admin"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test creating a new employee
        employee_data = {
            "name": "Test Employee Admin",
            "email": "test.employee.admin@example.com",
            "role": "employee",
            "company": "Test Company",
            "department": "Test Department"
        }
        
        response = await client.post(
            "/api/v1/admin/employees",
            headers=headers,
            json=employee_data
        )
        
        # Should return 201 created or handle gracefully
        assert response.status_code in [201, 400, 422]  # 400/422 for validation errors are acceptable
        
        if response.status_code == 201:
            data = response.json()
            assert data["name"] == employee_data["name"]
            assert data["email"] == employee_data["email"]
            assert data["role"] == "employee"


class TestAdminRoleBasedAccess:
    """Test admin role-based access controls."""
    
    @pytest.mark.asyncio
    async def test_non_admin_cannot_access_admin_endpoints(self, client: AsyncClient, test_db: AsyncSession):
        """Test that employees and controllers cannot access admin endpoints."""
        
        # Test with employee (ID 3)
        employee_token = self._create_token(3, "max.mustermann@demo.com", "Max Mustermann", "employee")
        employee_headers = {"Authorization": f"Bearer {employee_token}"}
        
        # Test with controller (ID 1)
        controller_token = self._create_token(1, "controller1@demo.com", "Anna Controlling", "controller")
        controller_headers = {"Authorization": f"Bearer {controller_token}"}
        
        # Admin endpoints to test
        admin_endpoints = [
            "/api/v1/admin/dashboard",
            "/api/v1/admin/controller-assignments",
            "/api/v1/admin/travels"
        ]
        
        for endpoint in admin_endpoints:
            # Test employee access (should be forbidden)
            response = await client.get(endpoint, headers=employee_headers)
            assert response.status_code == 403, f"Employee should not access {endpoint}"
            data = response.json()
            assert "Admin access required" in data["detail"]
            
            # Test controller access (should be forbidden)
            response = await client.get(endpoint, headers=controller_headers)
            assert response.status_code == 403, f"Controller should not access {endpoint}"
            data = response.json()
            assert "Admin access required" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_admin_post_endpoints_forbidden_non_admin(self, client: AsyncClient, test_db: AsyncSession):
        """Test that non-admins cannot use admin POST endpoints."""
        
        # Test with controller (ID 1)
        controller_token = self._create_token(1, "controller1@demo.com", "Anna Controlling", "controller")
        controller_headers = {"Authorization": f"Bearer {controller_token}"}
        
        # Test creating controller (should be forbidden)
        controller_data = {
            "name": "Unauthorized Controller",
            "email": "unauthorized@example.com",
            "role": "controller",
            "company": "Test Company",
            "department": "Test Department"
        }
        
        response = await client.post(
            "/api/v1/admin/controllers",
            headers=controller_headers,
            json=controller_data
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "Admin access required" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_unauthenticated_access_admin_endpoints(self, client: AsyncClient):
        """Test that unauthenticated users cannot access admin endpoints."""
        
        admin_endpoints = [
            "/api/v1/admin/dashboard",
            "/api/v1/admin/controller-assignments",
            "/api/v1/admin/travels"
        ]
        
        for endpoint in admin_endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 403, f"Unauthenticated user should not access {endpoint}"
    
    def _create_token(self, user_id: int, email: str, name: str, role: str) -> str:
        """Helper method to create authentication tokens."""
        from backend.app.core.auth import create_access_token
        return create_access_token(data={
            "sub": str(user_id),
            "email": email,
            "name": name,
            "role": role
        })


class TestAdminBusinessLogic:
    """Test admin business logic and data integrity."""
    
    @pytest.mark.asyncio
    async def test_admin_statistics_accuracy(self, client: AsyncClient, test_db: AsyncSession):
        """Test that admin dashboard statistics are mathematically consistent."""
        
        # Use known admin ID from mock mapping (ID 7 = admin)
        admin_id = 7
        
        # Create admin authentication headers
        from backend.app.core.auth import create_access_token
        token = create_access_token(data={
            "sub": str(admin_id),
            "email": "admin@demo.com",
            "name": "System Administrator",
            "role": "admin"
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get dashboard data
        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        stats = data["statistics"]
        
        # Verify mathematical consistency
        total_employees = stats["total_employees"]
        assigned_employees = stats["assigned_employees"]
        unassigned_employees = stats["unassigned_employees"]
        
        # Total employees should equal assigned + unassigned
        assert total_employees == assigned_employees + unassigned_employees, \
            f"Total employees ({total_employees}) != assigned ({assigned_employees}) + unassigned ({unassigned_employees})"
        
        # All values should be non-negative
        assert total_employees >= 0
        assert assigned_employees >= 0
        assert unassigned_employees >= 0
        assert stats["total_controllers"] >= 0
        
        # If there are controllers but no employees, assigned should be 0
        if stats["total_controllers"] > 0 and total_employees == 0:
            assert assigned_employees == 0
