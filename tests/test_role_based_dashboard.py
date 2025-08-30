"""
Test role-based dashboard functionality.
Ensures proper UI visibility and behavior for Employee vs Controller roles.
"""
import pytest
from httpx import AsyncClient
import json
from unittest.mock import patch


class TestRoleBasedDashboard:
    """Test role-based dashboard functionality for Employee and Controller roles."""
    
    @pytest.mark.asyncio
    async def test_landing_page_accessible(self, client: AsyncClient):
        """Test that the landing page is accessible."""
        response = await client.get("/api/v1/")
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        
        html_content = response.text
        assert "TravelExpense" in html_content
        assert "Anmelden" in html_content
        assert "Registrieren" in html_content
    
    @pytest.mark.asyncio
    async def test_dashboard_page_accessible(self, client: AsyncClient):
        """Test that the dashboard page is accessible."""
        response = await client.get("/api/v1/dashboard")
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        
        html_content = response.text
        assert "Dashboard - TravelExpense" in html_content
        assert "Dashboard" in html_content
    
    @pytest.mark.asyncio
    async def test_debug_page_accessible(self, client: AsyncClient):
        """Test that the debug page is accessible."""
        response = await client.get("/api/v1/debug")
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        
        html_content = response.text
        assert "TravelExpense Debug Page" in html_content
        assert "LocalStorage Content" in html_content
        assert "Login as Controller" in html_content
        assert "Login as Employee" in html_content

class TestLoginRoleDetection:
    """Test role detection logic in the login system."""
    
    @pytest.mark.asyncio
    async def test_landing_page_has_role_detection_logic(self, client: AsyncClient):
        """Test that the landing page contains the role detection JavaScript."""
        response = await client.get("/")
        html_content = response.text
        
        # Check for role detection in login form
        assert "email.includes('controller')" in html_content
        assert "'controller' :" in html_content
        assert "'employee'" in html_content
        
        # Check for role selection in registration
        assert 'data-role="employee"' in html_content
        assert 'data-role="controller"' in html_content
        assert "selectRole('employee')" in html_content
        assert "selectRole('controller')" in html_content

class TestDashboardElements:
    """Test that dashboard contains all necessary elements for role-based functionality."""
    
    @pytest.mark.asyncio
    async def test_dashboard_has_employee_elements(self, client: AsyncClient):
        """Test that dashboard contains employee-specific elements with proper IDs."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Employee navigation elements
        assert 'id="meine-reisen-nav"' in html_content
        assert 'id="belege-nav"' in html_content
        assert 'id="neue-reise-button"' in html_content
        
        # Employee sections
        assert 'id="employee-actions"' in html_content
        assert 'id="employee-travels"' in html_content
        assert 'id="personal-stats"' in html_content
        
        # Employee-specific content
        assert "Meine Reisen" in html_content
        assert "Neue Reise" in html_content
        assert "Belege" in html_content
    
    @pytest.mark.asyncio
    async def test_dashboard_has_controller_elements(self, client: AsyncClient):
        """Test that dashboard contains controller-specific elements with proper IDs."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Controller navigation elements
        assert 'id="controller-section"' in html_content
        assert 'style="display: none;"' in html_content  # Hidden by default
        
        # Controller sections
        assert 'id="controller-actions"' in html_content
        assert 'id="controller-overview"' in html_content
        
        # Controller-specific content
        assert "Team-Übersicht" in html_content
        assert "Genehmigungen" in html_content
        assert "Team-Berichte" in html_content
        assert "Controlling" in html_content  # Role text, not CONTROLLING
    
    @pytest.mark.asyncio
    async def test_dashboard_has_role_detection_javascript(self, client: AsyncClient):
        """Test that dashboard contains JavaScript for role-based UI switching."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for role detection function
        assert "function initUser()" in html_content
        assert "currentUser.role === 'controller'" in html_content
        
        # Check for element hiding/showing logic
        assert ".style.display = 'none'" in html_content
        assert ".style.display = 'block'" in html_content
        assert ".style.display = 'grid'" in html_content
        
        # Check for controller-specific functions
        assert "loadTeamOverview()" in html_content
        assert "displayTeamSummary" in html_content
        assert "displayTeamTable" in html_content

class TestTeamOverviewFunctionality:
    """Test the team overview functionality for controllers."""
    
    @pytest.mark.asyncio
    async def test_dashboard_has_team_overview_structure(self, client: AsyncClient):
        """Test that dashboard contains team overview HTML structure."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Team overview container
        assert 'id="controller-overview"' in html_content
        assert 'id="team-summary"' in html_content
        assert 'id="team-table"' in html_content
        assert 'id="team-table-body"' in html_content
        
        # Team table headers
        assert "Mitarbeiter" in html_content
        assert "Abteilung" in html_content
        assert "Aktive Reisen" in html_content
        assert "YTD Ausgaben" in html_content
        assert "Budget Status" in html_content
        assert "Zur Freigabe" in html_content
        assert "Aktionen" in html_content
        
        # Filters
        assert 'id="department-filter"' in html_content
        assert 'id="status-filter"' in html_content
    
    @pytest.mark.asyncio
    async def test_dashboard_has_team_overview_css(self, client: AsyncClient):
        """Test that dashboard contains CSS for team overview styling."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Team overview specific CSS classes
        assert ".team-summary" in html_content
        assert ".team-table" in html_content
        assert ".employee-info" in html_content
        assert ".employee-avatar" in html_content
        assert ".department-badge" in html_content
        assert ".budget-status" in html_content
        assert ".budget-ok" in html_content
        assert ".budget-warning" in html_content
        assert ".budget-over" in html_content

class TestRoleBasedJavaScriptFunctions:
    """Test JavaScript functions for role-based functionality."""
    
    @pytest.mark.asyncio
    async def test_dashboard_has_team_data_functions(self, client: AsyncClient):
        """Test that dashboard contains JavaScript functions for team data handling."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Team data functions
        assert "async function loadTeamOverview()" in html_content
        assert "function displayTeamSummary(" in html_content
        assert "function displayTeamTable(" in html_content
        assert "function getDepartmentName(" in html_content
        assert "function filterTeam()" in html_content
        assert "function viewMemberDetails(" in html_content
        assert "function reviewApprovals(" in html_content
    
    @pytest.mark.asyncio
    async def test_dashboard_contains_realistic_team_data(self, client: AsyncClient):
        """Test that dashboard contains realistic demo team data."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for demo team members
        assert "Max Mustermann" in html_content
        assert "Sarah Schmidt" in html_content
        assert "Michael Weber" in html_content
        assert "Lisa Müller" in html_content
        assert "Thomas Klein" in html_content
        assert "Anna Fischer" in html_content
        
        # Check for departments
        assert "'sales'" in html_content
        assert "'marketing'" in html_content
        assert "'development'" in html_content
        assert "'hr'" in html_content
        
        # Check for budget and expense data
        assert "ytdExpenses" in html_content
        assert "yearBudget" in html_content
        assert "pendingApprovals" in html_content

class TestAccessibility:
    """Test accessibility and proper HTML structure."""
    
    @pytest.mark.asyncio
    async def test_dashboard_has_proper_html_structure(self, client: AsyncClient):
        """Test that dashboard has proper HTML structure and accessibility."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for proper HTML structure
        assert "<!DOCTYPE html>" in html_content
        assert '<html lang="de">' in html_content
        assert "<head>" in html_content
        assert "<title>" in html_content
        assert "<body>" in html_content
        
        # Check for accessibility features
        assert '<button' in html_content  # Interactive elements should be present
        assert '<a href=' in html_content  # Navigation links
    
    @pytest.mark.asyncio
    async def test_landing_page_has_proper_form_structure(self, client: AsyncClient):
        """Test that landing page has proper form structure."""
        response = await client.get("/api/v1/")
        html_content = response.text
        
        # Check for form elements
        assert '<form id="login-form">' in html_content
        assert '<form id="register-form">' in html_content
        assert 'type="email"' in html_content
        assert 'type="password"' in html_content
        assert 'required' in html_content
        
        # Check for proper labels
        assert '<label for=' in html_content

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_dashboard_has_error_handling(self, client: AsyncClient):
        """Test that dashboard contains error handling logic."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for error handling in JavaScript
        assert "try {" in html_content
        assert "catch (error)" in html_content
        assert "console.error" in html_content
        assert "showTeamEmptyState" in html_content
    
    @pytest.mark.asyncio
    async def test_dashboard_has_empty_state_handling(self, client: AsyncClient):
        """Test that dashboard handles empty states properly."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for empty state messages
        assert "Keine Teamdaten verfügbar" in html_content
        assert "empty-state" in html_content

class TestDataValidation:
    """Test data validation and formatting."""
    
    @pytest.mark.asyncio
    async def test_dashboard_has_data_formatting_functions(self, client: AsyncClient):
        """Test that dashboard contains data formatting functions."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for formatting functions
        assert "toLocaleString()" in html_content
        assert "toFixed(" in html_content
        assert "formatDate" in html_content or "getStatusText" in html_content
    
    @pytest.mark.asyncio
    async def test_team_data_has_proper_structure(self, client: AsyncClient):
        """Test that team data has proper structure and validation."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for proper data structure in JavaScript
        assert "id:" in html_content
        assert "name:" in html_content
        assert "email:" in html_content
        assert "department:" in html_content
        assert "ytdExpenses:" in html_content
        assert "yearBudget:" in html_content

class TestUserExperience:
    """Test user experience features."""
    
    @pytest.mark.asyncio
    async def test_dashboard_has_interactive_elements(self, client: AsyncClient):
        """Test that dashboard contains interactive elements."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for interactive elements
        assert "onclick=" in html_content
        assert "onchange=" in html_content
        assert "addEventListener" in html_content
        
        # Check for buttons and links
        assert "btn" in html_content
        assert "class=\"btn" in html_content
    
    @pytest.mark.asyncio 
    async def test_responsive_design_elements(self, client: AsyncClient):
        """Test that dashboard contains responsive design elements."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for responsive CSS
        assert "grid-template-columns" in html_content
        assert "@media" in html_content or "flex" in html_content
        assert "responsive" in html_content or "auto-fit" in html_content

class TestSecurity:
    """Test security aspects of the role-based system."""
    
    @pytest.mark.asyncio
    async def test_no_sensitive_data_exposed(self, client: AsyncClient):
        """Test that no sensitive data is exposed in frontend code."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check that no actual passwords or tokens are hardcoded
        assert "password123" not in html_content.lower()
        assert "secret" not in html_content.lower()
        assert "token" not in html_content.lower()
        
        # Demo data should be clearly marked as demo
        assert "demo" in html_content.lower() or "Demo" in html_content
    
    @pytest.mark.asyncio
    async def test_role_validation_present(self, client: AsyncClient):
        """Test that role validation is present in the frontend."""
        response = await client.get("/api/v1/dashboard")
        html_content = response.text
        
        # Check for role validation
        assert "role ===" in html_content  # Strict comparison
        assert "localStorage.getItem('user')" in html_content
        assert "JSON.parse" in html_content
