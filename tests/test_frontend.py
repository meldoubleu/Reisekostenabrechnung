"""
Test frontend UI functionality.
"""
import pytest
from httpx import AsyncClient


class TestFrontendUI:
    """Test frontend user interface endpoints."""
    
    @pytest.mark.asyncio
    async def test_ui_form_accessible(self, client: AsyncClient):
        """Test that the UI form is accessible and returns HTML."""
        response = await client.get("/api/v1/ui")
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        
        # Check that the form contains expected elements
        html_content = response.text
        assert "Neue Reise" in html_content
        assert "travel-form" in html_content
        assert "employee_name" in html_content
        
        # Check for default values
        assert 'value="Max Mustermann"' in html_content
        assert 'value="München"' in html_content
        assert 'value="Germany"' in html_content
        assert 'value="SALES-001"' in html_content
        assert "Kundentermin und Projektabschluss bei ABC GmbH" in html_content
    
    @pytest.mark.asyncio
    async def test_ui_form_has_required_fields(self, client: AsyncClient):
        """Test that the UI form has all required fields."""
        response = await client.get("/api/v1/ui")
        html_content = response.text
        
        # Check for required input fields
        required_fields = [
            'name="employee_name"',
            'name="start_at"',
            'name="end_at"',
            'name="destination_city"',
            'name="destination_country"',
            'name="purpose"'
        ]
        
        for field in required_fields:
            assert field in html_content, f"Required field {field} not found in form"
        
        # Check for optional field
        assert 'name="cost_center"' in html_content
        
        # Check for form submission elements
        assert 'type="submit"' in html_content
        assert "Reise erstellen" in html_content  # Updated to match actual button text
    
    @pytest.mark.asyncio
    async def test_ui_form_has_receipt_upload(self, client: AsyncClient):
        """Test that the UI form includes receipt upload functionality."""
        response = await client.get("/api/v1/ui")
        html_content = response.text
        
        # Check for receipt upload form
        assert "receipt-form" in html_content
        assert 'type="file"' in html_content
        assert 'accept="image/*,application/pdf"' in html_content
        
        # Check for receipt display table
        assert "receipts" in html_content
        assert "<th>Datei</th>" in html_content
        assert "<th>Betrag</th>" in html_content
        assert "<th>Währung</th>" in html_content
        assert "<th>Datum</th>" in html_content
        assert "<th>Händler</th>" in html_content
        
        # Check for travel submission form
        assert 'type="submit"' in html_content
        assert "travel-form" in html_content
