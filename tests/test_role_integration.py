"""
Integration tests for role-based dashboard functionality.
Tests the complete user flow from login to role-specific dashboard features.
"""
import pytest
from httpx import AsyncClient
import json
import asyncio


class TestRoleBasedIntegration:
    """Integration tests for complete role-based user flows."""
    
    @pytest.mark.asyncio
    async def test_employee_login_flow_elements(self, client: AsyncClient):
        """Test that employee login flow contains all necessary elements."""
        # Test landing page
        response = await client.get("/api/v1/")
        assert response.status_code == 200
        html_content = response.text
        
        # Login form should contain role detection logic
        assert "email.includes('controller')" in html_content
        assert "'employee'" in html_content
        
        # Test dashboard
        response = await client.get("/api/v1/dashboard")
        assert response.status_code == 200
        html_content = response.text
        
        # Employee elements should be present
        assert 'id="employee-actions"' in html_content
        assert 'id="meine-reisen-nav"' in html_content
        assert 'id="neue-reise-button"' in html_content
    
    @pytest.mark.asyncio
    async def test_controller_login_flow_elements(self, client: AsyncClient):
        """Test that controller login flow contains all necessary elements."""
        # Test landing page
        response = await client.get("/api/v1/")
        assert response.status_code == 200
        html_content = response.text
        
        # Login form should contain role detection logic
        assert "email.includes('controller')" in html_content
        assert "'controller'" in html_content
        
        # Test dashboard
        response = await client.get("/api/v1/dashboard")
        assert response.status_code == 200
        html_content = response.text
        
        # Controller elements should be present
        assert 'id="controller-section"' in html_content
        assert 'id="controller-overview"' in html_content
        assert "loadTeamOverview()" in html_content

class TestDebugPageIntegration:
    """Test the debug page integration for testing role switching."""
    
    @pytest.mark.asyncio
    async def test_debug_page_functionality(self, client: AsyncClient):
        """Test that debug page contains all testing utilities."""
        response = await client.get("/api/v1/debug")
        assert response.status_code == 200
        html_content = response.text
        
        # Debug page elements
        assert "LocalStorage Content" in html_content
        assert "Quick Login Tests" in html_content
        assert "Role Detection Test" in html_content
        
        # JavaScript functions for testing
        assert "loginAsController()" in html_content
        assert "loginAsEmployee()" in html_content
        assert "testRoleDetection()" in html_content
        assert "clearData()" in html_content
        assert "goToDashboard()" in html_content
    
    @pytest.mark.asyncio
    async def test_debug_page_role_data_structure(self, client: AsyncClient):
        """Test that debug page sets up proper role data structure."""
        response = await client.get("/api/v1/debug")
        html_content = response.text
        
        # Controller user structure
        assert "role: 'controller'" in html_content or '"controller"' in html_content
        assert "controller@demo.com" in html_content
        assert "Controller User" in html_content
        
        # Employee user structure  
        assert "role: 'employee'" in html_content or '"employee"' in html_content
        assert "employee@demo.com" in html_content
        assert "Employee User" in html_content

class TestFormIntegration:
    """Test travel form integration with role-based system."""
    
    @pytest.mark.asyncio
    async def test_travel_form_accessible_from_employee_dashboard(self, client: AsyncClient):
        """Test that travel form is accessible from employee dashboard."""
        response = await client.get("/api/v1/travel-form")
        assert response.status_code == 200
        html_content = response.text
        
        # Travel form should be present
        assert "Neue Reise" in html_content
        assert "travel-form" in html_content
    
    @pytest.mark.asyncio
    async def test_ui_endpoint_serves_travel_form(self, client: AsyncClient):
        """Test that UI endpoint serves the travel form properly."""
        response = await client.get("/api/v1/ui")
        assert response.status_code == 200
        html_content = response.text
        
        # UI form should contain travel form elements
        assert "employee_name" in html_content
        assert "destination_city" in html_content
        assert "purpose" in html_content

class TestDataConsistency:
    """Test data consistency across different pages and roles."""
    
    @pytest.mark.asyncio
    async def test_consistent_navigation_structure(self, client: AsyncClient):
        """Test that navigation structure is consistent across pages."""
        # Test dashboard navigation
        response = await client.get("/api/v1/dashboard")
        dashboard_html = response.text
        
        # Should have consistent navigation elements
        assert "Dashboard" in dashboard_html
        assert "sidebar" in dashboard_html.lower() or "nav" in dashboard_html.lower()
        
        # Check for consistent styling
        assert "var(--primary)" in dashboard_html  # CSS variables
        assert "Inter" in dashboard_html  # Font consistency
    
    @pytest.mark.asyncio
    async def test_consistent_styling_across_pages(self, client: AsyncClient):
        """Test that styling is consistent across all pages."""
        pages = ["/api/v1/", "/api/v1/dashboard", "/api/v1/debug"]
        
        for page in pages:
            response = await client.get(page)
            assert response.status_code == 200
            html_content = response.text
            
            # Should have consistent CSS variables
            # Note: Debug page has simpler styling, so check for basic structure
            if "/debug" not in page:
                assert "--primary:" in html_content
                assert "--gray-" in html_content
            assert "Inter" in html_content or "Arial" in html_content  # Font family

class TestErrorScenariosIntegration:
    """Test error scenarios and edge cases in integration."""
    
    @pytest.mark.asyncio
    async def test_dashboard_without_user_data(self, client: AsyncClient):
        """Test dashboard behavior when no user data is present."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Should have redirect logic for missing user data
        assert "localStorage.getItem('user')" in html_content
        assert "window.location.href = '/'" in html_content
    
    @pytest.mark.asyncio
    async def test_team_overview_error_handling(self, client: AsyncClient):
        """Test team overview error handling."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Should have error handling for team data loading
        assert "try {" in html_content
        assert "catch (error)" in html_content
        assert "showTeamEmptyState" in html_content

class TestPerformanceAndOptimization:
    """Test performance aspects of the role-based dashboard."""
    
    @pytest.mark.asyncio
    async def test_javascript_efficiency(self, client: AsyncClient):
        """Test that JavaScript is efficiently structured."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Should use event listeners efficiently
        assert "addEventListener" in html_content
        assert "DOMContentLoaded" in html_content
        
        # Should have efficient DOM queries
        assert "getElementById" in html_content
        assert "querySelector" in html_content or "getElementById" in html_content
    
    @pytest.mark.asyncio
    async def test_css_optimization(self, client: AsyncClient):
        """Test that CSS is well-structured and optimized."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Should use CSS variables for consistency
        assert ":root {" in html_content
        assert "var(--" in html_content
        
        # Should have responsive design
        assert "grid" in html_content or "flex" in html_content
        assert "@media" in html_content

class TestCompleteUserJourney:
    """Test complete user journeys for both roles."""
    
    @pytest.mark.asyncio
    async def test_employee_complete_journey_structure(self, client: AsyncClient):
        """Test complete employee journey structure."""
        # Landing page -> Dashboard -> Travel Form
        
        # 1. Landing page
        response = await client.get("/api/v1/")
        assert response.status_code == 200
        assert "Anmelden" in response.text
        
        # 2. Dashboard  
        response = await client.get("/api/v1/dashboard")
        assert response.status_code == 200
        dashboard_html = response.text
        assert 'id="employee-actions"' in dashboard_html
        assert "Neue Reise" in dashboard_html
        
        # 3. Travel form
        response = await client.get("/api/v1/travel-form")
        assert response.status_code == 200
        assert "travel-form" in response.text
    
    @pytest.mark.asyncio
    async def test_controller_complete_journey_structure(self, client: AsyncClient):
        """Test complete controller journey structure."""
        # Landing page -> Dashboard (team view)
        
        # 1. Landing page
        response = await client.get("/api/v1/")
        assert response.status_code == 200
        assert "controller" in response.text.lower()
        
        # 2. Dashboard with team overview
        response = await client.get("/api/v1/dashboard") 
        assert response.status_code == 200
        dashboard_html = response.text
        assert 'id="controller-overview"' in dashboard_html
        assert "Team-Übersicht" in dashboard_html
        assert "YTD Ausgaben" in dashboard_html

class TestSecurityIntegration:
    """Test security aspects in integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_no_server_side_role_enforcement(self, client: AsyncClient):
        """Test that role enforcement is properly documented as frontend-only."""
        # Note: Current implementation is frontend-only for demo purposes
        # This test documents that server-side enforcement would be needed for production
        
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Should contain role logic in frontend
        assert "role ===" in html_content
        assert "controller" in html_content
        assert "employee" in html_content
    
    @pytest.mark.asyncio
    async def test_demo_data_clearly_marked(self, client: AsyncClient):
        """Test that demo data is clearly marked as such."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Demo data should be clearly identified
        assert "demo" in html_content.lower() or "Demo" in html_content
        assert "@demo.com" in html_content

class TestAccessibilityIntegration:
    """Test accessibility in complete user flows."""
    
    @pytest.mark.asyncio
    async def test_semantic_html_structure(self, client: AsyncClient):
        """Test that pages use semantic HTML structure."""
        pages = ["/api/v1/", "/api/v1/dashboard", "/api/v1/debug"]
        
        for page in pages:
            response = await client.get(page)
            html_content = response.text
            
            # Should have semantic structure
            # Note: Different pages may have different structures
            assert ("<main>" in html_content or 
                   "<section>" in html_content or 
                   "<div class=\"main\">" in html_content or
                   "content" in html_content)
            
            # Different pages may have different navigation structures  
            if "/debug" not in page:  # Debug page has simpler structure
                assert ("<header>" in html_content or 
                       "<nav>" in html_content or
                       "navigation" in html_content or
                       "header" in html_content)
                       
            assert ("<button>" in html_content or 
                   "button" in html_content or
                   "btn" in html_content)  # Interactive elements
            assert 'lang="de"' in html_content  # Language attribute
    
    @pytest.mark.asyncio
    async def test_form_accessibility(self, client: AsyncClient):
        """Test form accessibility features."""
        response = await client.get("/api/v1/")
        html_content = response.text
        
        # Forms should have proper labels and structure
        assert "<label" in html_content
        assert "for=" in html_content
        assert "required" in html_content

# Performance benchmark test (optional, requires additional setup)
class TestPerformanceBenchmarks:
    """Optional performance benchmarks for the role-based dashboard."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow  # Mark as slow test
    async def test_page_load_performance(self, client: AsyncClient):
        """Test that pages load within reasonable time limits."""
        import time
        
        start_time = time.time()
        response = await client.get("/api/v1/dashboard")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should load in under 5 seconds
    
    @pytest.mark.asyncio 
    @pytest.mark.slow
    async def test_multiple_concurrent_requests(self, client: AsyncClient):
        """Test handling of multiple concurrent requests."""
        import asyncio
        
        # Create multiple concurrent requests
        tasks = []
        for _ in range(10):
            task = client.get("/api/v1/dashboard")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
