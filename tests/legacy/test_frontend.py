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
        response = await client.get("/api/v1/travel-form")
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        
        # Check that the form contains expected elements
        html_content = response.text
        assert "Neue Reise" in html_content
        assert 'id="travel-form"' in html_content
    
    @pytest.mark.asyncio
    async def test_ui_form_has_required_fields(self, client: AsyncClient):
        """Test that the UI form has all required fields."""
        response = await client.get("/api/v1/travel-form")
        html_content = response.text
        
        # Check for required input fields
        required_fields = [
            'id="trip-purpose"',
            'id="trip-destination"',
            'id="trip-start"',
            'id="trip-end"',
        ]
        
        for field in required_fields:
            assert field in html_content, f"Required field {field} not found in form"
        
        # Check for form submission elements
        assert 'type="submit"' in html_content
        assert "Reise einreichen" in html_content
    
    @pytest.mark.asyncio
    async def test_ui_form_has_receipt_upload(self, client: AsyncClient):
        """Test that the UI form includes receipt upload functionality."""
        response = await client.get("/api/v1/travel-form")
        html_content = response.text
        
        # Check for receipt upload functionality
        assert 'id="upload-area"' in html_content
        assert 'type="file"' in html_content
        
        # Check for receipt display table
        assert 'id="receipts-table"' in html_content
        assert "<th>Datei</th>" in html_content
        assert "<th>Größe</th>" in html_content
        assert "<th>Aktionen</th>" in html_content
        
        # Check for travel submission form
        assert 'type="submit"' in html_content
        assert 'id="travel-form"' in html_content
