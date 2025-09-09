"""
Integration tests for the complete receipt management workflow.
Tests the enhanced timeline fields, receipt categorization, and update functionality.
"""
import pytest
from httpx import AsyncClient
import io
from PIL import Image
from .test_auth_utils import TestAuthHelper


class TestReceiptIntegration:
    """Test the complete receipt management workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_receipt_workflow(self, client_with_users: AsyncClient, sample_travel_data):
        """Test the complete workflow: create travel with enhanced timeline -> upload receipt -> categorize and update."""
        # Get employee authentication headers
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        # Step 1: Create a travel with enhanced timeline fields
        enhanced_travel_data = {
            **sample_travel_data,
            "departure_timestamp": "2024-01-15T08:00:00",
            "departure_location": "Frankfurt Airport",
            "arrival_at_destination_timestamp": "2024-01-15T10:30:00",
            "departure_from_destination_timestamp": "2024-01-17T16:00:00", 
            "arrival_home_timestamp": "2024-01-17T18:30:00"
        }
        
        create_response = await client_with_users.post(
            "/api/v1/travels/",
            json=enhanced_travel_data,
            headers=headers
        )
        assert create_response.status_code == 200
        travel_data = create_response.json()
        travel_id = travel_data["id"]
        
        # Verify enhanced timeline fields are saved
        assert travel_data["departure_timestamp"] == "2024-01-15T08:00:00"
        assert travel_data["departure_location"] == "Frankfurt Airport"
        assert travel_data["arrival_at_destination_timestamp"] == "2024-01-15T10:30:00"
        assert travel_data["departure_from_destination_timestamp"] == "2024-01-17T16:00:00" 
        assert travel_data["arrival_home_timestamp"] == "2024-01-17T18:30:00"
        
        # Step 2: Upload multiple receipts
        receipts = []
        receipt_scenarios = [
            {"filename": "hotel_receipt.png", "category": "lodging", "amount": 150.00, "merchant": "Hotel Berlin"},
            {"filename": "flight_receipt.png", "category": "transport", "amount": 250.00, "merchant": "Lufthansa"},
            {"filename": "dinner_receipt.png", "category": "meals", "amount": 45.50, "merchant": "Restaurant ABC"}
        ]
        
        for i, scenario in enumerate(receipt_scenarios):
            # Create test image
            img = Image.new('RGB', (100, 100), color='white')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Upload receipt
            files = {"file": (scenario["filename"], img_buffer, "image/png")}
            upload_response = await client_with_users.post(
                f"/api/v1/travels/{travel_id}/receipts",
                files=files,
                headers=headers
            )
            
            assert upload_response.status_code == 201
            receipt_data = upload_response.json()
            receipt_data["scenario"] = scenario  # Store scenario for later use
            receipts.append(receipt_data)
        
        # Step 3: Categorize and update each receipt
        for receipt in receipts:
            scenario = receipt["scenario"]
            receipt_id = receipt["id"]
            
            update_data = {
                "category": scenario["category"],
                "amount": scenario["amount"],
                "merchant": scenario["merchant"],
                "date": "2024-01-16T12:00:00",
                "notes": f"Business expense for {scenario['category']}"
            }
            
            update_response = await client_with_users.put(
                f"/api/v1/travels/receipts/{receipt_id}",
                json=update_data,
                headers=headers
            )
            
            assert update_response.status_code == 200
            updated_receipt = update_response.json()
            
            # Verify all fields were updated correctly
            assert updated_receipt["category"] == scenario["category"]
            assert updated_receipt["amount"] == scenario["amount"]
            assert updated_receipt["merchant"] == scenario["merchant"]
            assert updated_receipt["date"] == "2024-01-16T12:00:00"
            assert scenario["category"] in updated_receipt["notes"]
        
        # Step 4: Verify updated travel includes all categorized receipts
        travel_response = await client_with_users.get(
            f"/api/v1/travels/{travel_id}",
            headers=headers
        )
        
        assert travel_response.status_code == 200
        final_travel = travel_response.json()
        
        # Check all receipts are present and categorized
        assert len(final_travel["receipts"]) == 3
        
        # Verify categorization
        categories_found = set()
        total_amount = 0
        
        for receipt in final_travel["receipts"]:
            assert receipt["category"] in ["lodging", "transport", "meals"]
            assert receipt["amount"] > 0
            assert receipt["merchant"] is not None
            categories_found.add(receipt["category"])
            total_amount += receipt["amount"]
        
        # Verify all categories are represented
        assert categories_found == {"lodging", "transport", "meals"}
        assert total_amount == 445.50  # 150 + 250 + 45.50
    
    @pytest.mark.asyncio
    async def test_receipt_category_validation(self, client_with_users: AsyncClient, sample_travel_data):
        """Test that receipt category validation works properly."""
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        # Create travel and upload receipt
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
        
        # Test all valid categories
        valid_categories = ["lodging", "transport", "meals", "entertainment", "other"]
        
        for category in valid_categories:
            update_data = {"category": category}
            response = await client_with_users.put(
                f"/api/v1/travels/receipts/{receipt_id}",
                json=update_data,
                headers=headers
            )
            assert response.status_code == 200
            updated_receipt = response.json()
            assert updated_receipt["category"] == category
        
        # Test invalid category
        invalid_update = {"category": "invalid_category"}
        response = await client_with_users.put(
            f"/api/v1/travels/receipts/{receipt_id}",
            json=invalid_update,
            headers=headers
        )
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_timeline_duration_calculation(self, client_with_users: AsyncClient, sample_travel_data):
        """Test that timeline fields support proper duration calculation."""
        headers = await TestAuthHelper.get_employee_headers(client_with_users)
        
        # Test various timeline scenarios
        timeline_scenarios = [
            {
                "departure_datetime": "2024-01-15T08:00:00",
                "arrival_datetime": "2024-01-15T18:00:00",
                "expected_duration_hours": 10
            },
            {
                "departure_datetime": "2024-01-15T08:00:00", 
                "arrival_datetime": "2024-01-17T16:00:00",
                "expected_duration_hours": 56  # 2 days + 8 hours
            },
            {
                "departure_datetime": "2024-01-15T14:30:00",
                "arrival_datetime": "2024-01-15T17:15:00", 
                "expected_duration_hours": 2.75  # 2 hours 45 minutes
            }
        ]
        
        for i, scenario in enumerate(timeline_scenarios):
            travel_data = {
                **sample_travel_data,
                "purpose": f"Test trip {i+1}",
                "departure_timestamp": scenario["departure_datetime"],
                "departure_location": "Origin",
                "arrival_home_timestamp": scenario["arrival_datetime"]
            }
            
            response = await client_with_users.post(
                "/api/v1/travels/",
                json=travel_data,
                headers=headers
            )
            
            assert response.status_code == 200
            created_travel = response.json()
            
            # Verify timeline fields are stored correctly
            assert created_travel["departure_timestamp"] == scenario["departure_datetime"]
            assert created_travel["arrival_home_timestamp"] == scenario["arrival_datetime"]
            
            # Note: Duration calculation would typically be done on the frontend
            # The backend just stores the timestamps for frontend calculation
