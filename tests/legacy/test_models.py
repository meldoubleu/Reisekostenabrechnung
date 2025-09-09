"""
Test database models and relationships.
"""
import pytest
from datetime import datetime
from backend.app.models.travel import Travel, Receipt, TravelStatus
from sqlalchemy import select


class TestModels:
    """Test database models and their relationships."""
    
    @pytest.mark.asyncio
    async def test_create_travel_model(self, test_db):
        """Test creating a travel model instance."""
        travel = Travel(
            employee_name="John Doe",
            start_at=datetime(2025, 8, 25, 9, 0, 0),
            end_at=datetime(2025, 8, 25, 17, 0, 0),
            destination_city="Berlin",
            destination_country="Germany",
            purpose="Business Meeting",
            cost_center="IT001",
            status=TravelStatus.draft
        )
        
        test_db.add(travel)
        await test_db.commit()
        await test_db.refresh(travel)
        
        assert travel.id is not None
        assert travel.employee_name == "John Doe"
        assert travel.status == TravelStatus.draft
    
    @pytest.mark.asyncio
    async def test_travel_receipt_relationship(self, test_db):
        """Test the relationship between Travel and Receipt models."""
        # Create a travel
        travel = Travel(
            employee_name="Jane Doe",
            start_at=datetime(2025, 8, 25, 9, 0, 0),
            end_at=datetime(2025, 8, 25, 17, 0, 0),
            destination_city="Munich",
            destination_country="Germany",
            purpose="Conference",
            status=TravelStatus.draft
        )
        test_db.add(travel)
        await test_db.commit()
        await test_db.refresh(travel)
        
        # Create a receipt for the travel
        receipt = Receipt(
            travel_id=travel.id,
            file_path="/test/path/receipt.jpg",
            amount=25.50,
            currency="EUR",
            merchant="Test Restaurant"
        )
        test_db.add(receipt)
        await test_db.commit()
        
        # Test the relationship
        result = await test_db.execute(
            select(Travel).where(Travel.id == travel.id)
        )
        travel_with_receipts = result.scalar_one()
        
        # Load receipts (this would normally be done with selectinload in the API)
        await test_db.refresh(travel_with_receipts, ["receipts"])
        
        assert len(travel_with_receipts.receipts) == 1
        assert travel_with_receipts.receipts[0].amount == 25.50
        assert travel_with_receipts.receipts[0].merchant == "Test Restaurant"
    
    @pytest.mark.asyncio
    async def test_travel_status_enum(self, test_db):
        """Test travel status enumeration."""
        travel = Travel(
            employee_name="Test User",
            start_at=datetime(2025, 8, 25, 9, 0, 0),
            end_at=datetime(2025, 8, 25, 17, 0, 0),
            destination_city="Hamburg",
            destination_country="Germany",
            purpose="Meeting",
            status=TravelStatus.submitted
        )
        
        test_db.add(travel)
        await test_db.commit()
        await test_db.refresh(travel)
        
        assert travel.status == TravelStatus.submitted
        
        # Test status change
        travel.status = TravelStatus.approved
        await test_db.commit()
        await test_db.refresh(travel)
        
        assert travel.status == TravelStatus.approved
