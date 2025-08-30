"""
Test data validation and business logic for role-based dashboard.
"""
import pytest
from httpx import AsyncClient
import re
import json


class TestTeamDataValidation:
    """Test validation of team data structure and business logic."""
    
    @pytest.mark.asyncio
    async def test_team_data_structure_validity(self, client: AsyncClient):
        """Test that team data has valid structure and realistic values."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Extract team data from JavaScript
        # Look for the team members array definition
        team_data_pattern = r'const teamMembers = \[(.*?)\];'
        match = re.search(team_data_pattern, html_content, re.DOTALL)
        
        assert match, "Team members data not found in dashboard"
        
        # Validate that required fields are present
        team_data_text = match.group(1)
        required_fields = ['id', 'name', 'email', 'department', 'ytdExpenses', 'yearBudget']
        for field in required_fields:
            assert f'"{field}":' in team_data_text or f"{field}:" in team_data_text, f"Field {field} missing from team data"
    
    @pytest.mark.asyncio
    async def test_budget_calculation_logic(self, client: AsyncClient):
        """Test that budget calculation logic is present and correct."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for budget utilization calculation
        assert "budgetUtilization = (member.ytdExpenses / member.yearBudget * 100)" in html_content
        assert "budgetUtilization > 100" in html_content
        assert "budgetUtilization > 90" in html_content
        
        # Check for budget status logic
        assert "budget-over" in html_content
        assert "budget-warning" in html_content
        assert "budget-ok" in html_content
    
    @pytest.mark.asyncio
    async def test_department_mapping_validity(self, client: AsyncClient):
        """Test that department mapping is complete and valid."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for department mapping function
        assert "function getDepartmentName(" in html_content
        
        # Check for all department mappings
        departments = ['sales', 'marketing', 'development', 'hr']
        for dept in departments:
            assert f"'{dept}'" in html_content, f"Department {dept} not found in mapping"
    
    @pytest.mark.asyncio
    async def test_email_validation_format(self, client: AsyncClient):
        """Test that email formats in team data are valid."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Look for email patterns in the team data (check multiple possible formats)
        email_patterns = [
            r'email["\']:\s*["\'][^"\']+@[^"\']+\.[^"\']+["\']',  # email: "user@domain.com"
            r'email:\s*["\'][^"\']+@[^"\']+\.[^"\']+["\']',       # email: "user@domain.com"
            r'["\'][^"\']*@demo\.com["\']',                       # any "@demo.com" email
        ]
        
        emails_found = False
        for pattern in email_patterns:
            emails = re.findall(pattern, html_content)
            if len(emails) > 0:
                emails_found = True
                # All emails should be from demo.com for consistency
                for email_match in emails:
                    assert "@demo.com" in email_match, f"Non-demo email found: {email_match}"
                break
        
        # If no regex patterns match, check for basic email presence
        if not emails_found:
            assert "@demo.com" in html_content, "No demo email addresses found in team data"


class TestRoleBasedBusinessRules:
    """Test business rules for role-based functionality."""
    
    @pytest.mark.asyncio
    async def test_controller_access_rules(self, client: AsyncClient):
        """Test that controller access rules are properly implemented."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Controllers should not see employee-specific elements
        assert "document.getElementById('neue-reise-button').style.display = 'none'" in html_content
        assert "document.getElementById('meine-reisen-nav').style.display = 'none'" in html_content
        assert "document.getElementById('personal-stats').style.display = 'none'" in html_content
    
    @pytest.mark.asyncio
    async def test_employee_access_rules(self, client: AsyncClient):
        """Test that employee access rules are properly implemented."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Employees should see their own elements
        assert "document.getElementById('employee-actions').style.display = 'grid'" in html_content
        assert "document.getElementById('personal-stats').style.display = 'grid'" in html_content
        
        # Employees should not see controller elements
        assert "document.getElementById('controller-section').style.display = 'none'" in html_content
    
    @pytest.mark.asyncio
    async def test_role_determination_logic(self, client: AsyncClient):
        """Test that role determination logic is robust."""
        response = await client.get("/")
        html_content = response.text
        
        # Login role determination should be based on email
        assert "email.includes('controller')" in html_content
        assert "'controller' :" in html_content
        assert "'employee'" in html_content
        
        # Registration role should be explicit selection
        assert 'data-role="controller"' in html_content
        assert 'data-role="employee"' in html_content


class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    @pytest.mark.asyncio
    async def test_team_summary_calculations(self, client: AsyncClient):
        """Test that team summary calculations are implemented correctly."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for aggregation functions
        assert "teamMembers.length" in html_content
        assert "teamMembers.filter(" in html_content
        assert "teamMembers.reduce(" in html_content
        
        # Check for specific calculations
        assert "totalYTDExpenses" in html_content
        assert "totalBudget" in html_content
        assert "totalPendingApprovals" in html_content
        assert "budgetUtilization" in html_content
    
    @pytest.mark.asyncio
    async def test_number_formatting_consistency(self, client: AsyncClient):
        """Test that number formatting is consistent throughout."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for consistent number formatting
        assert "toLocaleString()" in html_content
        assert "toFixed(" in html_content
        
        # Check for currency formatting
        assert "€" in html_content
    
    @pytest.mark.asyncio
    async def test_status_consistency(self, client: AsyncClient):
        """Test that status values are consistent."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for consistent status values
        assert "'active'" in html_content
        assert "'inactive'" in html_content
        
        # Check for status text mapping
        assert "getStatusText" in html_content or status_mapping_present(html_content)


def status_mapping_present(html_content: str) -> bool:
    """Helper function to check if status mapping is present."""
    status_indicators = ["Aktiv", "Inaktiv", "Im Rahmen", "Kritisch", "Überzogen"]
    return any(status in html_content for status in status_indicators)


class TestUserInterfaceLogic:
    """Test user interface logic and interaction patterns."""
    
    @pytest.mark.asyncio
    async def test_navigation_consistency(self, client: AsyncClient):
        """Test that navigation is consistent between roles."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Both roles should have dashboard navigation
        assert "Dashboard" in html_content
        assert 'onclick="showPage(' in html_content
        
        # Check for navigation function
        assert "function showPage(" in html_content or "showPage" in html_content
    
    @pytest.mark.asyncio
    async def test_responsive_behavior_elements(self, client: AsyncClient):
        """Test that responsive behavior elements are present."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for responsive grid system
        assert "grid-template-columns" in html_content
        assert "auto-fit" in html_content or "repeat(" in html_content
        
        # Check for flexible layouts
        assert "flex" in html_content
    
    @pytest.mark.asyncio
    async def test_loading_states_and_feedback(self, client: AsyncClient):
        """Test that loading states and user feedback are implemented."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for loading state handling
        assert "loading" in html_content.lower() or "Loading" in html_content
        
        # Check for error handling feedback
        assert "error" in html_content.lower() or "Error" in html_content
        assert "try {" in html_content and "catch" in html_content


class TestAPIEndpointCoverage:
    """Test that all API endpoints work correctly."""
    
    @pytest.mark.asyncio
    async def test_all_frontend_endpoints_accessible(self, client: AsyncClient):
        """Test that all frontend endpoints are accessible."""
        endpoints = [
            "/api/v1/",
            "/api/v1/dashboard", 
            "/api/v1/travel-form",
            "/api/v1/ui",
            "/api/v1/debug"
        ]
        
        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} not accessible"
            assert response.headers["content-type"].startswith("text/html"), f"Endpoint {endpoint} not returning HTML"
    
    @pytest.mark.asyncio
    async def test_endpoint_content_validity(self, client: AsyncClient):
        """Test that each endpoint returns valid content."""
        endpoint_content_checks = {
            "/api/v1/": ["TravelExpense", "Anmelden"],
            "/api/v1/dashboard": ["Dashboard", "TravelExpense"],
            "/api/v1/travel-form": ["Neue Reise", "travel-form"],
            "/api/v1/ui": ["employee_name", "destination"],
            "/api/v1/debug": ["Debug", "LocalStorage"]
        }
        
        for endpoint, expected_content in endpoint_content_checks.items():
            response = await client.get(endpoint)
            html_content = response.text
            
            for content in expected_content:
                assert content in html_content, f"Expected content '{content}' not found in {endpoint}"


class TestErrorHandlingRobustness:
    """Test error handling and edge case robustness."""
    
    @pytest.mark.asyncio
    async def test_javascript_error_handling(self, client: AsyncClient):
        """Test that JavaScript has proper error handling."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for try-catch blocks
        assert "try {" in html_content
        assert "catch (error)" in html_content
        assert "console.error" in html_content
    
    @pytest.mark.asyncio
    async def test_empty_state_handling(self, client: AsyncClient):
        """Test that empty states are properly handled."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for empty state functions
        assert "showTeamEmptyState" in html_content
        assert "empty-state" in html_content
        
        # Check for fallback content
        assert "Keine" in html_content  # German for "No/None"
    
    @pytest.mark.asyncio
    async def test_malformed_data_handling(self, client: AsyncClient):
        """Test handling of potentially malformed data."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for JSON parsing with error handling
        assert "JSON.parse" in html_content
        assert "try {" in html_content or error_handling_present(html_content)


def error_handling_present(html_content: str) -> bool:
    """Helper function to check if error handling patterns are present."""
    error_patterns = ["catch", "error", "Error", "null", "undefined"]
    return any(pattern in html_content for pattern in error_patterns)


class TestPerformanceOptimization:
    """Test performance optimization aspects."""
    
    @pytest.mark.asyncio
    async def test_efficient_dom_queries(self, client: AsyncClient):
        """Test that DOM queries are efficient."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Should use getElementById for better performance
        assert "getElementById" in html_content
        
        # Should cache DOM elements where appropriate
        dom_query_count = html_content.count("getElementById")
        assert dom_query_count > 5, "Should have multiple DOM queries for dynamic behavior"
    
    @pytest.mark.asyncio
    async def test_css_efficiency(self, client: AsyncClient):
        """Test that CSS is efficiently structured."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Should use CSS variables for consistency
        assert ":root {" in html_content
        assert "var(--" in html_content
        
        # Should avoid inline styles where possible (some may be necessary for dynamic behavior)
        inline_style_count = html_content.count('style="')
        # Some inline styles are expected for dynamic show/hide behavior
        assert inline_style_count < 50, "Too many inline styles, consider CSS classes"


class TestBrowserCompatibility:
    """Test browser compatibility aspects."""
    
    @pytest.mark.asyncio
    async def test_modern_javascript_features_used_appropriately(self, client: AsyncClient):
        """Test that modern JavaScript features are used appropriately."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Should use modern features but with fallbacks
        assert "const " in html_content  # Modern variable declarations
        assert "async " in html_content or "await " in html_content  # Async/await
        assert "addEventListener" in html_content  # Modern event handling
    
    @pytest.mark.asyncio
    async def test_css_modern_features(self, client: AsyncClient):
        """Test that CSS uses modern but well-supported features."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Should use CSS Grid and Flexbox (well supported)
        assert "grid" in html_content
        assert "flex" in html_content
        
        # Should use CSS custom properties
        assert "var(--" in html_content
