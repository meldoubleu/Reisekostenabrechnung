"""
Test CRUD operations with comprehensive coverage.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crud import crud_user, crud_travel
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.schemas.travel import TravelCreate, TravelUpdate
from backend.app.models.user import UserRole


class TestUserCRUD:
    """Test user CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, test_db: AsyncSession):
        """Test creating a new user."""
        user_data = UserCreate(
            name="Test User CRUD",
            email="test.user.crud@example.com",
            role="employee",
            company="Test Company",
            department="Test Department",
            cost_center="TEST-001"
        )
        
        user = await crud_user.create(test_db, obj_in=user_data)
        
        assert user.name == user_data.name
        assert user.email == user_data.email
        assert user.role == UserRole.employee
        assert user.company == user_data.company
        assert user.department == user_data.department
        assert user.cost_center == user_data.cost_center
        assert user.id is not None
        assert user.is_active is True
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, test_db: AsyncSession):
        """Test getting user by ID."""
        user_data = UserCreate(
            name="Test User Get",
            email="test.user.get@example.com",
            role="controller",
            company="Test Company",
            department="Management"
        )
        
        created_user = await crud_user.create(test_db, obj_in=user_data)
        retrieved_user = await crud_user.get(test_db, id=created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, test_db: AsyncSession):
        """Test getting nonexistent user returns None."""
        user = await crud_user.get(test_db, id=99999)
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, test_db: AsyncSession):
        """Test getting user by email."""
        user_data = UserCreate(
            name="Test User Email",
            email="test.user.email@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        
        created_user = await crud_user.create(test_db, obj_in=user_data)
        retrieved_user = await crud_user.get_by_email(test_db, email=user_data.email)
        
        assert retrieved_user is not None
        assert retrieved_user.email == user_data.email
        assert retrieved_user.id == created_user.id
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, test_db: AsyncSession):
        """Test getting user by nonexistent email returns None."""
        user = await crud_user.get_by_email(test_db, email="nonexistent@example.com")
        assert user is None
    
    @pytest.mark.asyncio
    async def test_update_user(self, test_db: AsyncSession):
        """Test updating user."""
        user_data = UserCreate(
            name="Test User Update",
            email="test.user.update@example.com",
            role="employee",
            company="Test Company",
            department="Original Department"
        )
        
        created_user = await crud_user.create(test_db, obj_in=user_data)
        
        update_data = UserUpdate(
            name="Updated Name",
            department="Updated Department"
        )
        
        updated_user = await crud_user.update(test_db, db_obj=created_user, obj_in=update_data)
        
        assert updated_user.name == "Updated Name"
        assert updated_user.department == "Updated Department"
        assert updated_user.email == user_data.email  # Should remain unchanged
        assert updated_user.id == created_user.id
    
    @pytest.mark.asyncio
    async def test_delete_user(self, test_db: AsyncSession):
        """Test deleting user."""
        user_data = UserCreate(
            name="Test User Delete",
            email="test.user.delete@example.com",
            role="employee",
            company="Test Company",
            department="Test"
        )
        
        created_user = await crud_user.create(test_db, obj_in=user_data)
        deleted_user = await crud_user.remove(test_db, id=created_user.id)
        
        assert deleted_user is not None
        assert deleted_user.id == created_user.id
        
        # Verify user is actually deleted
        retrieved_user = await crud_user.get(test_db, id=created_user.id)
        assert retrieved_user is None
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, test_db: AsyncSession):
        """Test deleting nonexistent user returns None."""
        deleted_user = await crud_user.remove(test_db, id=99999)
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_get_multi_users(self, test_db: AsyncSession):
        """Test getting multiple users with pagination."""
        # Create several users
        for i in range(5):
            user_data = UserCreate(
                name=f"Test User Multi {i}",
                email=f"test.user.multi.{i}@example.com",
                role="employee",
                company="Test Company",
                department="Test"
            )
            await crud_user.create(test_db, obj_in=user_data)
        
        # Get users with pagination
        users = await crud_user.get_multi(test_db, skip=0, limit=3)
        
        assert len(users) >= 3  # Should have at least 3 users (might have more from other tests)
        assert all(hasattr(user, 'id') for user in users)
        assert all(hasattr(user, 'email') for user in users)
    
    @pytest.mark.asyncio
    async def test_get_controllers(self, test_db: AsyncSession):
        """Test getting all controllers."""
        # Create a controller
        controller_data = UserCreate(
            name="Test Controller",
            email="test.controller.crud@example.com",
            role="controller",
            company="Test Company",
            department="Management"
        )
        
        await crud_user.create(test_db, obj_in=controller_data)
        
        controllers = await crud_user.get_controllers(test_db)
        
        assert len(controllers) > 0
        for controller in controllers:
            assert controller.role == UserRole.controller
            assert hasattr(controller, 'employees')  # Should have employees relationship loaded
    
    @pytest.mark.asyncio
    async def test_assign_controller(self, test_db: AsyncSession):
        """Test assigning controller to employee."""
        # Create controller
        controller_data = UserCreate(
            name="Test Controller Assign",
            email="test.controller.assign.crud@example.com",
            role="controller",
            company="Test Company",
            department="Management"
        )
        controller = await crud_user.create(test_db, obj_in=controller_data)
        
        # Create employee
        employee_data = UserCreate(
            name="Test Employee Assign",
            email="test.employee.assign.crud@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        employee = await crud_user.create(test_db, obj_in=employee_data)
        
        # Assign controller
        updated_employee = await crud_user.assign_controller(
            test_db, 
            employee_id=employee.id, 
            controller_id=controller.id
        )
        
        assert updated_employee.controller_id == controller.id
        assert updated_employee.id == employee.id
    
    @pytest.mark.asyncio
    async def test_assign_controller_invalid_employee(self, test_db: AsyncSession):
        """Test assigning controller to nonexistent employee."""
        with pytest.raises(ValueError, match="Employee with id .* not found"):
            await crud_user.assign_controller(test_db, employee_id=99999, controller_id=1)
    
    @pytest.mark.asyncio
    async def test_assign_controller_invalid_controller(self, test_db: AsyncSession):
        """Test assigning nonexistent controller to employee."""
        # Create employee
        employee_data = UserCreate(
            name="Test Employee Invalid Controller",
            email="test.employee.invalid.controller@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        employee = await crud_user.create(test_db, obj_in=employee_data)
        
        with pytest.raises(ValueError, match="Controller with id .* not found"):
            await crud_user.assign_controller(test_db, employee_id=employee.id, controller_id=99999)
    
    @pytest.mark.asyncio
    async def test_get_employees_by_controller(self, test_db: AsyncSession):
        """Test getting employees assigned to a controller."""
        # Create controller
        controller_data = UserCreate(
            name="Test Controller Employees",
            email="test.controller.employees@example.com",
            role="controller",
            company="Test Company",
            department="Management"
        )
        controller = await crud_user.create(test_db, obj_in=controller_data)
        
        # Create employees assigned to controller
        for i in range(3):
            employee_data = UserCreate(
                name=f"Test Employee {i}",
                email=f"test.employee.{i}@example.com",
                role="employee",
                company="Test Company",
                department="Sales",
                controller_id=controller.id
            )
            employee = await crud_user.create(test_db, obj_in=employee_data)
            # Verify the employee was created with correct controller_id
            assert employee.controller_id == controller.id
        
        employees = await crud_user.get_employees_by_controller(
            test_db, 
            controller_id=controller.id
        )
        
        assert len(employees) == 3
        for employee in employees:
            assert employee.role == "employee"
            assert employee.controller_id == controller.id


class TestTravelCRUD:
    """Test travel CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_travel(self, test_db: AsyncSession):
        """Test creating a new travel."""
        # First create a user
        user_data = UserCreate(
            name="Test User Travel",
            email="test.user.travel@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        user = await crud_user.create(test_db, obj_in=user_data)
        
        travel_data = TravelCreate(
            employee_name="Test Employee",
            start_at="2025-09-01T09:00:00",
            end_at="2025-09-03T17:00:00",
            destination_city="Berlin",
            destination_country="Germany",
            purpose="Business Meeting CRUD",
            cost_center="IT001",
            employee_id=user.id
        )
        
        travel = await crud_travel.create(test_db, obj_in=travel_data)
        
        assert travel.purpose == travel_data.purpose
        assert travel.destination_city == travel_data.destination_city
        assert travel.destination_country == travel_data.destination_country
        assert travel.start_at == travel_data.start_at
        assert travel.end_at == travel_data.end_at
        assert travel.employee_name == travel_data.employee_name
        assert travel.cost_center == travel_data.cost_center
        assert travel.employee_id == user.id
        assert travel.id is not None
    
    @pytest.mark.asyncio
    async def test_get_travel_by_id(self, test_db: AsyncSession):
        """Test getting travel by ID."""
        # Create user and travel
        user_data = UserCreate(
            name="Test User Get Travel",
            email="test.user.get.travel@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        user = await crud_user.create(test_db, obj_in=user_data)
        
        travel_data = TravelCreate(
            employee_name="Get Travel Test Employee",
            start_at="2025-09-10T08:00:00",
            end_at="2025-09-11T18:00:00",
            destination_city="Munich",
            destination_country="Germany",
            purpose="Get Travel Test",
            cost_center="SALES001",
            employee_id=user.id
        )
        
        created_travel = await crud_travel.create(test_db, obj_in=travel_data)
        retrieved_travel = await crud_travel.get(test_db, id=created_travel.id)
        
        assert retrieved_travel is not None
        assert retrieved_travel.id == created_travel.id
        assert retrieved_travel.purpose == travel_data.purpose
    
    @pytest.mark.asyncio
    async def test_get_travel_by_id_not_found(self, test_db: AsyncSession):
        """Test getting nonexistent travel returns None."""
        travel = await crud_travel.get(test_db, id=99999)
        assert travel is None
    
    @pytest.mark.asyncio
    async def test_update_travel(self, test_db: AsyncSession):
        """Test updating travel."""
        # Create user and travel
        user_data = UserCreate(
            name="Test User Update Travel",
            email="test.user.update.travel@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        user = await crud_user.create(test_db, obj_in=user_data)
        
        travel_data = TravelCreate(
            employee_name="Update Travel Test Employee",
            start_at="2025-09-15T09:00:00",
            end_at="2025-09-16T17:00:00",
            destination_city="Original Destination",
            destination_country="Germany",
            purpose="Original Purpose",
            cost_center="SALES002",
            employee_id=user.id
        )
        
        created_travel = await crud_travel.create(test_db, obj_in=travel_data)
        
        update_data = TravelUpdate(
            employee_name="Updated Employee Name",
            start_at="2025-09-15T09:00:00",
            end_at="2025-09-16T17:00:00",
            destination_city="Updated Destination",
            destination_country="Germany",
            purpose="Updated Purpose",
            cost_center="SALES003"
        )
        
        updated_travel = await crud_travel.update(test_db, db_obj=created_travel, obj_in=update_data)
        
        assert updated_travel.purpose == "Updated Purpose"
        assert updated_travel.destination_city == "Updated Destination"
        assert updated_travel.employee_name == "Updated Employee Name"
        assert updated_travel.id == created_travel.id
    
    @pytest.mark.asyncio
    async def test_delete_travel(self, test_db: AsyncSession):
        """Test deleting travel."""
        # Create user and travel
        user_data = UserCreate(
            name="Test User Delete Travel",
            email="test.user.delete.travel@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        user = await crud_user.create(test_db, obj_in=user_data)
        
        travel_data = TravelCreate(
            employee_name="Delete Travel Test Employee",
            start_at="2025-09-20T10:00:00",
            end_at="2025-09-21T16:00:00",
            destination_city="Hamburg",
            destination_country="Germany",
            purpose="Travel to Delete",
            cost_center="SALES004",
            employee_id=user.id
        )
        
        created_travel = await crud_travel.create(test_db, obj_in=travel_data)
        deleted_travel = await crud_travel.remove(test_db, id=created_travel.id)
        
        assert deleted_travel is not None
        assert deleted_travel.id == created_travel.id
        
        # Verify travel is actually deleted
        retrieved_travel = await crud_travel.get(test_db, id=created_travel.id)
        assert retrieved_travel is None
    
    @pytest.mark.asyncio
    async def test_delete_travel_not_found(self, test_db: AsyncSession):
        """Test deleting nonexistent travel returns None."""
        deleted_travel = await crud_travel.remove(test_db, id=99999)
        assert deleted_travel is None
    
    @pytest.mark.asyncio
    async def test_get_multi_travels(self, test_db: AsyncSession):
        """Test getting multiple travels with pagination."""
        # Create user
        user_data = UserCreate(
            name="Test User Multi Travels",
            email="test.user.multi.travels@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        user = await crud_user.create(test_db, obj_in=user_data)
        
        # Create several travels
        for i in range(5):
            travel_data = TravelCreate(
                employee_name=f"Travel {i} Employee",
                start_at="2025-09-01T08:00:00",
                end_at="2025-09-02T18:00:00",
                destination_city=f"City {i}",
                destination_country="Germany",
                purpose=f"Travel {i}",
                cost_center=f"CC00{i}",
                employee_id=user.id
            )
            await crud_travel.create(test_db, obj_in=travel_data)
        
        # Get travels with pagination
        travels = await crud_travel.get_multi(test_db, skip=0, limit=3)
        
        assert len(travels) >= 3  # Should have at least 3 travels
        assert all(hasattr(travel, 'id') for travel in travels)
        assert all(hasattr(travel, 'purpose') for travel in travels)
    
    @pytest.mark.asyncio
    async def test_get_travels_by_user(self, test_db: AsyncSession):
        """Test getting travels by user ID."""
        # Create user
        user_data = UserCreate(
            name="Test User Travels By User",
            email="test.user.travels.by.user@example.com",
            role="employee",
            company="Test Company",
            department="Sales"
        )
        user = await crud_user.create(test_db, obj_in=user_data)
        
        # Create travels for this user
        for i in range(3):
            travel_data = TravelCreate(
                employee_name=f"User Travel {i} Employee",
                start_at="2025-09-01T09:00:00",
                end_at="2025-09-02T17:00:00",
                destination_city=f"User City {i}",
                destination_country="Germany",
                purpose=f"User Travel {i}",
                cost_center=f"UC00{i}",
                employee_id=user.id
            )
            await crud_travel.create(test_db, obj_in=travel_data)
        
        travels = await crud_travel.get_multi_by_employee_id(test_db, employee_id=user.id)
        
        assert len(travels) == 3
        for travel in travels:
            assert travel.employee_id == user.id
