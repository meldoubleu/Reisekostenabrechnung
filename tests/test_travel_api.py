"""
Test API endpoints for travel management.
"""
import pytest
from httpx import AsyncClient
from backend.app.models.travel import Travel, TravelStatus


class TestTravelAPI:
    """Test travel-related API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_travel(self, client: AsyncClient, sample_travel_data):
        """Test creating a new travel."""
        response = await client.post(
            "/api/v1/travels/",
            data=sample_travel_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["employee_name"] == sample_travel_data["employee_name"]
        assert data["destination_city"] == sample_travel_data["destination_city"]
        assert data["destination_country"] == sample_travel_data["destination_country"]
        assert data["purpose"] == sample_travel_data["purpose"]
        assert data["cost_center"] == sample_travel_data["cost_center"]
        assert data["status"] == "draft"
        assert "id" in data
        assert data["receipts"] == []
    
    @pytest.mark.asyncio
    async def test_list_travels_empty(self, client: AsyncClient):
        """Test listing travels when database is empty."""
        response = await client.get("/api/v1/travels/")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    @pytest.mark.asyncio
    async def test_list_travels_with_data(self, client: AsyncClient, sample_travel_data):
        """Test listing travels after creating some."""
        # Create a travel first
        create_response = await client.post(
            "/api/v1/travels/",
            data=sample_travel_data
        )
        assert create_response.status_code == 200
        
        # Now list travels
        response = await client.get("/api/v1/travels/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["employee_name"] == sample_travel_data["employee_name"]
    
    @pytest.mark.asyncio
    async def test_create_travel_missing_fields(self, client: AsyncClient):
        """Test creating travel with missing required fields."""
        incomplete_data = {
            "employee_name": "John Doe",
            # Missing other required fields
        }
        
        response = await client.post(
            "/api/v1/travels/",
            data=incomplete_data
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_submit_travel(self, client: AsyncClient, sample_travel_data):
        """Test submitting a travel for approval."""
        # Create a travel first
        create_response = await client.post(
            "/api/v1/travels/",
            data=sample_travel_data
        )
        travel_id = create_response.json()["id"]
        
        # Submit the travel
        response = await client.post(f"/api/v1/travels/{travel_id}/submit")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "submitted"
    
    @pytest.mark.asyncio
    async def test_submit_nonexistent_travel(self, client: AsyncClient):
        """Test submitting a travel that doesn't exist."""
        response = await client.post("/api/v1/travels/999/submit")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_export_travel_pdf(self, client: AsyncClient, sample_travel_data):
        """Test exporting travel as PDF."""
        # Create a travel first
        create_response = await client.post(
            "/api/v1/travels/",
            data=sample_travel_data
        )
        travel_id = create_response.json()["id"]
        
        # Export as PDF
        response = await client.get(f"/api/v1/travels/{travel_id}/export")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
    
    @pytest.mark.asyncio
    async def test_export_nonexistent_travel_pdf(self, client: AsyncClient):
        """Test exporting a travel that doesn't exist."""
        response = await client.get("/api/v1/travels/999/export")
        
        assert response.status_code == 404
