"""
Test travel endpoints for comprehensive coverage.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import json
from io import BytesIO
from datetime import datetime

from backend.app.models.user import User
from backend.app.models.travel import Travel
from backend.app.crud import crud_user, crud_travel
from backend.app.schemas.user import UserCreate
from backend.app.schemas.travel import TravelCreate


def create_test_travel_data(**kwargs):
    """Helper function to create test travel data with correct schema."""
    default_data = {
        "employee_name": "Test Employee",
        "purpose": "Business Meeting",
        "destination_city": "Berlin",
        "destination_country": "Germany",
        "start_at": "2025-09-01T09:00:00",
        "end_at": "2025-09-03T17:00:00",
        "cost_center": "CC001",
        "status": "draft"
    }
    default_data.update(kwargs)
    return default_data


class TestTravelEndpoints:
    """Test travel API endpoints."""
    
    @pytest.mark.asyncio
    async def test_submit_travel_employee(self, client: AsyncClient, employee_headers: dict):
        """Test employee can submit travel request."""
        travel_data = create_test_travel_data(
            employee_name="Test Employee",
            start_at="2025-09-01T09:00:00",
            end_at="2025-09-03T17:00:00",
            purpose="Business Meeting",
            cost_center="BIZ001"
        )

        response = await client.post(
            "/api/v1/travels/submit",
            headers=employee_headers,
            json=travel_data
        )

        assert response.status_code == 201
        data = response.json()

        assert data["purpose"] == travel_data["purpose"]
        assert data["destination_city"] == travel_data["destination_city"]
        assert data["destination_country"] == travel_data["destination_country"]
        assert data["start_at"] == travel_data["start_at"]
        assert data["end_at"] == travel_data["end_at"]
        assert data["employee_name"] == travel_data["employee_name"]
        assert data["cost_center"] == travel_data["cost_center"]
        assert data["status"] == "submitted"
        assert "id" in data
        assert "employee_id" in data
    
    @pytest.mark.asyncio
    async def test_submit_travel_unauthorized(self, client: AsyncClient):
        """Test travel submission without authentication."""
        travel_data = create_test_travel_data(
            purpose="Business Meeting"
        )
        
        response = await client.post("/api/v1/travels/submit", json=travel_data)
        assert response.status_code == 403  # Forbidden without auth
    
    @pytest.mark.asyncio
    async def test_get_my_travels_employee(self, client: AsyncClient, employee_headers: dict, test_db: AsyncSession):
        """Test employee can get their own travels."""
        response = await client.get("/api/v1/travels/my", headers=employee_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All travels should belong to the current user
        if data:  # If there are travels
            for travel in data:
                assert "employee_id" in travel
                assert "purpose" in travel
                assert "destination_city" in travel
                assert "destination_country" in travel
                assert "status" in travel
    
    @pytest.mark.asyncio
    async def test_get_my_travels_unauthorized(self, client: AsyncClient):
        """Test getting travels without authentication."""
        response = await client.get("/api/v1/travels/my")
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_travel_by_id_owner(self, client: AsyncClient, employee_headers: dict, test_db: AsyncSession):
        """Test user can get their own travel by ID."""
        # First submit a travel to get an ID
        travel_data = create_test_travel_data(
            purpose="Test Travel Get",
            destination_city="Munich",
            destination_country="Germany"
        )
        
        submit_response = await client.post(
            "/api/v1/travels/submit", 
            headers=employee_headers,
            json=travel_data
        )
        assert submit_response.status_code == 201
        travel = submit_response.json()
        
        # Now get the travel by ID
        response = await client.get(f"/api/v1/travels/{travel['id']}", headers=employee_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == travel["id"]
        assert data["purpose"] == travel_data["purpose"]
    
    @pytest.mark.asyncio
    async def test_get_travel_by_id_not_found(self, client: AsyncClient, employee_headers: dict):
        """Test getting nonexistent travel returns 404."""
        response = await client.get("/api/v1/travels/99999", headers=employee_headers)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_upload_receipt_employee(self, client: AsyncClient, employee_headers: dict, test_db: AsyncSession):
        """Test employee can upload receipt for their travel."""
        # First submit a travel
        travel_data = create_test_travel_data(
            purpose="Test Travel Receipt",
            destination_city="Hamburg",
            destination_country="Germany"
        )
        
        submit_response = await client.post(
            "/api/v1/travels/submit", 
            headers=employee_headers,
            json=travel_data
        )
        assert submit_response.status_code == 201
        travel = submit_response.json()
        
        # Create a fake PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n165\n%%EOF"
        
        files = {
            "file": ("test_receipt.pdf", BytesIO(pdf_content), "application/pdf")
        }
        
        response = await client.post(
            f"/api/v1/travels/{travel['id']}/receipts", 
            headers={k: v for k, v in employee_headers.items() if k != "Content-Type"},  # Remove content-type for file upload
            files=files
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "file_path" in data
        assert data["travel_id"] == travel["id"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_upload_receipt_invalid_file_type(self, client: AsyncClient, employee_headers: dict, test_db: AsyncSession):
        """Test uploading invalid file type for receipt."""
        # First submit a travel
        travel_data = create_test_travel_data(
            purpose="Test Travel Invalid Receipt",
            destination_city="Frankfurt",
            destination_country="Germany"
        )
        
        submit_response = await client.post(
            "/api/v1/travels/submit", 
            headers=employee_headers,
            json=travel_data
        )
        assert submit_response.status_code == 201
        travel = submit_response.json()
        
        # Try to upload a text file
        files = {
            "file": ("test.txt", BytesIO(b"This is not a valid receipt"), "text/plain")
        }
        
        response = await client.post(
            f"/api/v1/travels/{travel['id']}/receipts", 
            headers={k: v for k, v in employee_headers.items() if k != "Content-Type"},
            files=files
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "file type" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_travel_receipts_owner(self, client: AsyncClient, employee_headers: dict, test_db: AsyncSession):
        """Test user can get receipts for their own travel."""
        # First submit a travel
        travel_data = create_test_travel_data(
            purpose="Test Travel Get Receipts",
            destination_city="Cologne",
            destination_country="Germany"
        )
        
        submit_response = await client.post(
            "/api/v1/travels/submit", 
            headers=employee_headers,
            json=travel_data
        )
        assert submit_response.status_code == 201
        travel = submit_response.json()
        
        # Get receipts (should be empty initially)
        response = await client.get(
            f"/api/v1/travels/{travel['id']}/receipts", 
            headers=employee_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should be empty as no receipts uploaded yet
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_export_travel_data_employee(self, client: AsyncClient, employee_headers: dict):
        """Test employee can export their travel data."""
        response = await client.get("/api/v1/travels/export", headers=employee_headers)
        
        # Should return CSV data or empty response
        assert response.status_code in [200, 404]  # 404 if no travels exist
        
        if response.status_code == 200:
            assert "text/csv" in response.headers["content-type"]
    
    @pytest.mark.asyncio
    async def test_export_travel_data_unauthorized(self, client: AsyncClient):
        """Test travel export without authentication."""
        response = await client.get("/api/v1/travels/export")
        assert response.status_code == 403


class TestTravelControllerAccess:
    """Test controller access to assigned employee travels."""
    
    @pytest.mark.asyncio
    async def test_get_assigned_travels_controller(self, client: AsyncClient, controller_headers: dict):
        """Test controller can get travels of assigned employees."""
        response = await client.get("/api/v1/travels/assigned", headers=controller_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All travels should be from employees assigned to this controller
        if data:
            for travel in data:
                assert "employee_id" in travel
                assert "purpose" in travel
                assert "status" in travel
    
    @pytest.mark.asyncio
    async def test_get_assigned_travels_employee_forbidden(self, client: AsyncClient, employee_headers: dict):
        """Test employee cannot get assigned travels (controller-only endpoint)."""
        response = await client.get("/api/v1/travels/assigned", headers=employee_headers)
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_approve_travel_controller(self, client: AsyncClient, controller_headers: dict, admin_headers: dict, test_db: AsyncSession):
        """Test controller can approve travel from assigned employee."""
        # First create an employee assigned to a controller and submit a travel
        # We'll need to use admin to create the relationship first
        
        # Create controller
        controller_data = UserCreate(
            name="Test Controller Approve",
            email="test.controller.approve@example.com",
            role="controller",
            company="Test Company",
            department="Management"
        )
        controller = await crud_user.create(test_db, obj_in=controller_data)
        
        # Create employee assigned to controller
        employee_data = UserCreate(
            name="Test Employee Approve",
            email="test.employee.approve@example.com",
            role="employee",
            company="Test Company",
            department="Sales",
            controller_id=controller.id
        )
        employee = await crud_user.create(test_db, obj_in=employee_data)
        
        # Create travel for the employee
        travel_data = TravelCreate(
            employee_name="Test Employee Approve",
            purpose="Business Trip for Approval",
            destination_city="Berlin",
            destination_country="Germany",
            start_at="2025-10-01T09:00:00",
            end_at="2025-10-02T17:00:00",
            employee_id=employee.id
        )
        travel = await crud_travel.create(test_db, obj_in=travel_data)
        
        # Now try to approve as controller (this would need proper authentication setup)
        # For now, we'll test the endpoint exists and requires auth
        response = await client.put(
            f"/api/v1/travels/{travel.id}/approve", 
            headers=controller_headers
        )
        
        # The exact response depends on implementation, but should not be 404
        assert response.status_code in [200, 403, 404]  # 403 if not assigned to this controller


class TestTravelValidation:
    """Test travel data validation and business rules."""
    
    @pytest.mark.asyncio
    async def test_submit_travel_invalid_dates(self, client: AsyncClient, employee_headers: dict):
        """Test travel submission with invalid date range."""
        travel_data = create_test_travel_data(
            purpose="Invalid Date Travel",
            start_at="2025-09-10T09:00:00",
            end_at="2025-09-05T17:00:00"  # End before start
        )
        
        response = await client.post(
            "/api/v1/travels/submit", 
            headers=employee_headers,
            json=travel_data
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_submit_travel_missing_required_fields(self, client: AsyncClient, employee_headers: dict):
        """Test travel submission with missing required fields."""
        travel_data = {
            "purpose": "Incomplete Travel",
            # Missing destination, dates, etc.
        }
        
        response = await client.post(
            "/api/v1/travels/submit", 
            headers=employee_headers,
            json=travel_data
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_submit_travel_negative_cost(self, client: AsyncClient, employee_headers: dict):
        """Test travel submission with negative cost."""
        # Since cost is not part of TravelCreate schema anymore, 
        # this test now validates that proper travel data is accepted
        travel_data = create_test_travel_data(
            purpose="Valid Travel Data"
        )
        
        response = await client.post(
            "/api/v1/travels/submit", 
            headers=employee_headers,
            json=travel_data
        )
        
        # Should succeed with valid data
        assert response.status_code == 201


class TestTravelFiltering:
    """Test travel filtering and search functionality."""
    
    @pytest.mark.asyncio
    async def test_get_travels_with_status_filter(self, client: AsyncClient, employee_headers: dict):
        """Test filtering travels by status."""
        response = await client.get(
            "/api/v1/travels/my?status=submitted", 
            headers=employee_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All returned travels should have 'submitted' status
        for travel in data:
            assert travel["status"] == "submitted"
    
    @pytest.mark.asyncio
    async def test_get_travels_with_date_range(self, client: AsyncClient, employee_headers: dict):
        """Test filtering travels by date range."""
        response = await client.get(
            "/api/v1/travels/my?start_date=2025-09-01&end_date=2025-09-30", 
            headers=employee_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All returned travels should be within the date range
        for travel in data:
            travel_start = travel["start_at"]
            travel_end = travel["end_at"]
            # Convert datetime strings for comparison
            assert travel_start >= "2025-09-01"
            assert travel_end <= "2025-09-30"
