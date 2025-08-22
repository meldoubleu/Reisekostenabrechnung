"""
Integration tests for the complete travel expense workflow.
"""
import pytest
from httpx import AsyncClient
import io
from PIL import Image
from pathlib import Path


class TestTravelWorkflow:
    """Test the complete travel expense workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_travel_workflow(self, client: AsyncClient, sample_travel_data, temp_upload_dir):
        """Test the complete workflow: create travel -> upload receipts -> submit -> export."""
        
        # Step 1: Create a travel
        create_response = await client.post(
            "/api/v1/travels/",
            data=sample_travel_data
        )
        assert create_response.status_code == 200
        travel_data = create_response.json()
        travel_id = travel_data["id"]
        assert travel_data["status"] == "draft"
        assert travel_data["employee_name"] == sample_travel_data["employee_name"]
        
        # Step 2: Upload multiple receipts
        receipts = []
        for i in range(3):
            # Create test image with some text
            img = Image.new('RGB', (200, 100), color='white')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            files = {"file": (f"receipt_{i}.png", img_buffer, "image/png")}
            response = await client.post(
                f"/api/v1/travels/{travel_id}/receipts",
                files=files
            )
            assert response.status_code == 200
            receipt_data = response.json()
            assert receipt_data["travel_id"] == travel_id
            receipts.append(receipt_data)
        
        # Step 3: Verify travel has receipts
        get_response = await client.get("/api/v1/travels/")
        travels = get_response.json()
        our_travel = next(t for t in travels if t["id"] == travel_id)
        assert len(our_travel["receipts"]) == 3
        
        # Step 4: Submit the travel
        submit_response = await client.post(f"/api/v1/travels/{travel_id}/submit")
        assert submit_response.status_code == 200
        submitted_data = submit_response.json()
        assert submitted_data["status"] == "submitted"
        
        # Step 5: Export as PDF
        export_response = await client.get(f"/api/v1/travels/{travel_id}/export")
        assert export_response.status_code == 200
        assert export_response.headers["content-type"] == "application/pdf"
        assert len(export_response.content) > 0  # PDF should have content
    
    @pytest.mark.asyncio
    async def test_upload_different_file_types(self, client: AsyncClient, sample_travel_data, temp_upload_dir):
        """Test uploading different types of receipt files."""
        
        # Create a travel
        create_response = await client.post(
            "/api/v1/travels/",
            data=sample_travel_data
        )
        travel_id = create_response.json()["id"]
        
        # Test PNG upload
        png_img = Image.new('RGB', (100, 100), color='red')
        png_buffer = io.BytesIO()
        png_img.save(png_buffer, format='PNG')
        png_buffer.seek(0)
        
        png_response = await client.post(
            f"/api/v1/travels/{travel_id}/receipts",
            files={"file": ("receipt.png", png_buffer, "image/png")}
        )
        assert png_response.status_code == 200
        
        # Test JPEG upload
        jpg_img = Image.new('RGB', (100, 100), color='blue')
        jpg_buffer = io.BytesIO()
        jpg_img.save(jpg_buffer, format='JPEG')
        jpg_buffer.seek(0)
        
        jpg_response = await client.post(
            f"/api/v1/travels/{travel_id}/receipts",
            files={"file": ("receipt.jpg", jpg_buffer, "image/jpeg")}
        )
        assert jpg_response.status_code == 200
        
        # Verify both uploads
        get_response = await client.get("/api/v1/travels/")
        travels = get_response.json()
        our_travel = next(t for t in travels if t["id"] == travel_id)
        assert len(our_travel["receipts"]) == 2
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client: AsyncClient):
        """Test error handling for various edge cases."""
        
        # Test uploading receipt to non-existent travel
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        response = await client.post(
            "/api/v1/travels/99999/receipts",
            files={"file": ("test.png", img_buffer, "image/png")}
        )
        assert response.status_code == 404
        
        # Test submitting non-existent travel
        response = await client.post("/api/v1/travels/99999/submit")
        assert response.status_code == 404
        
        # Test exporting non-existent travel
        response = await client.get("/api/v1/travels/99999/export")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_travel_list_ordering(self, client: AsyncClient, sample_travel_data):
        """Test that travels are returned in the correct order (newest first)."""
        
        # Create multiple travels
        travel_ids = []
        for i in range(3):
            modified_data = sample_travel_data.copy()
            modified_data["employee_name"] = f"Employee {i}"
            
            response = await client.post(
                "/api/v1/travels/",
                data=modified_data
            )
            assert response.status_code == 200
            travel_ids.append(response.json()["id"])
        
        # Get list of travels
        response = await client.get("/api/v1/travels/")
        assert response.status_code == 200
        travels = response.json()
        
        # Should be ordered by ID descending (newest first)
        # Find our travels in the list
        our_travels = [t for t in travels if t["id"] in travel_ids]
        assert len(our_travels) == 3
        
        # They should be in descending order of ID
        our_travel_ids = [t["id"] for t in our_travels]
        assert our_travel_ids == sorted(travel_ids, reverse=True)
