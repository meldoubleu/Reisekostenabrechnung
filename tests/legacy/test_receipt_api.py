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
    async def test_upload_receipt_to_travel(self, client_with_users: AsyncClient, sample_travel_data, temp_upload_dir):
        """Test uploading a receipt to an existing travel."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        # Create a travel first
        create_response = await client_with_users.post(
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
        response = await client_with_users.post(
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
    async def test_upload_receipt_to_nonexistent_travel(self, client_with_users: AsyncClient):
        """Test uploading a receipt to a travel that doesn't exist."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        files = {"file": ("test_receipt.png", img_buffer, "image/png")}
        response = await client_with_users.post(
            "/api/v1/travels/999/receipts",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_travel_with_receipts_in_list(self, client_with_users: AsyncClient, sample_travel_data, temp_upload_dir):
        """Test that receipts are included when listing travels."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        # Create a travel
        create_response = await client_with_users.post(
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
            await client_with_users.post(
                f"/api/v1/travels/{travel_id}/receipts",
                files=files,
                headers=headers
            )
        
        # List travels and check receipts are included
        response = await client_with_users.get("/api/v1/travels/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert len(data[0]["receipts"]) == 1
        assert "receipt.jpg" in data[0]["receipts"][0]["file_path"]

    @pytest.mark.asyncio
    async def test_update_receipt_details(self, client_with_users: AsyncClient, sample_travel_data, temp_upload_dir):
        """Test updating receipt details via PUT endpoint."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        # Create a travel first
        create_response = await client_with_users.post(
            "/api/v1/travels/",
            json=sample_travel_data,
            headers=headers
        )
        assert create_response.status_code == 200
        travel_id = create_response.json()["id"]

        # Upload a receipt
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        files = {"file": ("test_receipt.png", img_buffer, "image/png")}
        upload_response = await client_with_users.post(
            f"/api/v1/travels/{travel_id}/receipts",
            files=files,
            headers=headers
        )
        
        assert upload_response.status_code == 201
        receipt_data = upload_response.json()
        receipt_id = receipt_data["id"]
        
        # Update receipt details
        update_data = {
            "amount": 45.50,
            "merchant": "Test Restaurant",
            "category": "meals",
            "notes": "Business lunch with client",
            "date": "2024-01-15T12:00:00"
        }
        
        update_response = await client_with_users.put(
            f"/api/v1/travels/receipts/{receipt_id}",
            json=update_data,
            headers=headers
        )
        
        assert update_response.status_code == 200
        updated_receipt = update_response.json()
        
        assert updated_receipt["id"] == receipt_id
        assert updated_receipt["amount"] == 45.50
        assert updated_receipt["merchant"] == "Test Restaurant"
        assert updated_receipt["category"] == "meals"
        assert updated_receipt["notes"] == "Business lunch with client"
        assert updated_receipt["date"] == "2024-01-15T12:00:00"

    @pytest.mark.asyncio
    async def test_update_receipt_partial_fields(self, client_with_users: AsyncClient, sample_travel_data):
        """Test updating only some receipt fields."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        # Create a travel and upload a receipt
        create_response = await client_with_users.post(
            "/api/v1/travels/",
            json=sample_travel_data,
            headers=headers
        )
        travel_id = create_response.json()["id"]

        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        files = {"file": ("test_receipt.png", img_buffer, "image/png")}
        upload_response = await client_with_users.post(
            f"/api/v1/travels/{travel_id}/receipts",
            files=files,
            headers=headers
        )
        receipt_id = upload_response.json()["id"]
        
        # Update only amount and category
        update_data = {
            "amount": 25.00,
            "category": "transport"
        }
        
        update_response = await client_with_users.put(
            f"/api/v1/travels/receipts/{receipt_id}",
            json=update_data,
            headers=headers
        )
        
        assert update_response.status_code == 200
        updated_receipt = update_response.json()
        
        assert updated_receipt["amount"] == 25.00
        assert updated_receipt["category"] == "transport"
        # Other fields should remain unchanged/null

    @pytest.mark.asyncio
    async def test_update_receipt_invalid_category(self, client_with_users: AsyncClient, sample_travel_data):
        """Test updating receipt with invalid category."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        # Create a travel and upload a receipt
        create_response = await client_with_users.post(
            "/api/v1/travels/",
            json=sample_travel_data,
            headers=headers
        )
        travel_id = create_response.json()["id"]

        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        files = {"file": ("test_receipt.png", img_buffer, "image/png")}
        upload_response = await client_with_users.post(
            f"/api/v1/travels/{travel_id}/receipts",
            files=files,
            headers=headers
        )
        receipt_id = upload_response.json()["id"]
        
        # Try to update with invalid category
        update_data = {
            "category": "invalid_category"
        }
        
        update_response = await client_with_users.put(
            f"/api/v1/travels/receipts/{receipt_id}",
            json=update_data,
            headers=headers
        )
        
        assert update_response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_update_nonexistent_receipt(self, client_with_users: AsyncClient):
        """Test updating a receipt that doesn't exist."""
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        update_data = {
            "amount": 25.00,
            "category": "transport"
        }
        
        update_response = await client_with_users.put(
            "/api/v1/travels/receipts/99999",
            json=update_data,
            headers=headers
        )
        
        assert update_response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_receipt_unauthorized(self, client_with_users: AsyncClient, sample_travel_data):
        """Test updating receipt without proper authorization."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        # Create a travel and upload a receipt
        create_response = await client_with_users.post(
            "/api/v1/travels/",
            json=sample_travel_data,
            headers=headers
        )
        travel_id = create_response.json()["id"]

        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        files = {"file": ("test_receipt.png", img_buffer, "image/png")}
        upload_response = await client_with_users.post(
            f"/api/v1/travels/{travel_id}/receipts",
            files=files,
            headers=headers
        )
        receipt_id = upload_response.json()["id"]
        
        # Try to update without authorization
        update_data = {
            "amount": 25.00,
            "category": "transport"
        }
        
        update_response = await client_with_users.put(
            f"/api/v1/travels/receipts/{receipt_id}",
            json=update_data
            # No headers = no authorization
        )
        
        assert update_response.status_code == 403
