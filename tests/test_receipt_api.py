"""
Test receipt management and OCR functionality.
"""
import pytest
from httpx import AsyncClient
import io
from PIL import Image
from .test_auth_utils import TestAuthHelper


class TestReceiptAPI:
    """Test receipt-related API endpoints."""
    
    @pytest.mark.asyncio
    async def test_upload_receipt_to_travel(self, client: AsyncClient, sample_travel_data, temp_upload_dir):
        """Test uploading a receipt to an existing travel."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client)
        
        # Create a travel first
        create_response = await client.post(
            "/api/v1/travels/",
            json=sample_travel_data,
            headers=headers
        )
        assert create_response.status_code == 200
        travel_id = create_response.json()["id"]

        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Upload the receipt
        files = {"file": ("test_receipt.png", img_buffer, "image/png")}
        response = await client.post(
            f"/api/v1/travels/{travel_id}/receipts",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["travel_id"] == travel_id
        assert "file_path" in data
        assert "test_receipt.png" in data["file_path"]
    
    @pytest.mark.asyncio
    async def test_upload_receipt_to_nonexistent_travel(self, client: AsyncClient):
        """Test uploading a receipt to a travel that doesn't exist."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client)
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        files = {"file": ("test_receipt.png", img_buffer, "image/png")}
        response = await client.post(
            "/api/v1/travels/999/receipts",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_travel_with_receipts_in_list(self, client: AsyncClient, sample_travel_data, temp_upload_dir):
        """Test that receipts are included when listing travels."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client)
        
        # Create a travel
        create_response = await client.post(
            "/api/v1/travels/",
            json=sample_travel_data,
            headers=headers
        )
        assert create_response.status_code == 200
        travel_id = create_response.json()["id"]

        # Upload a receipt
        receipt_path = temp_upload_dir / "receipt.jpg"
        img = Image.new('RGB', (100, 100), color='white')
        img.save(receipt_path, format='JPEG')
        
        with open(receipt_path, "rb") as img_file:
            files = {"file": ("receipt.jpg", img_file, "image/jpeg")}
            await client.post(
                f"/api/v1/travels/{travel_id}/receipts",
                files=files,
                headers=headers
            )
        
        # List travels and check receipts are included
        response = await client.get("/api/v1/travels/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert len(data[0]["receipts"]) == 1
        assert "receipt.jpg" in data[0]["receipts"][0]["file_path"]
