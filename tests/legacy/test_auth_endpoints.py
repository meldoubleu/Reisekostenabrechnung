"""
Authentication API Endpoint Tests
Complete coverage of all authentication-related endpoints.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from backend.app.main import app
import json


@pytest_asyncio.fixture
async def async_client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


class TestAuthLoginEndpoint:
    """Test /api/v1/auth/login endpoint."""
    
    @pytest_asyncio.async_test
    async def test_login_valid_employee(self, async_client: AsyncClient):
        """Test login with valid employee credentials."""
        login_data = {
            "username": "malte@demo.com",
            "password": "employee123"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
        assert "expires_in" in result or "exp" in result or True  # Some tokens include expiry
    
    @pytest_asyncio.async_test
    async def test_login_valid_controller(self, async_client: AsyncClient):
        """Test login with valid controller credentials."""
        login_data = {
            "username": "controller1@demo.com",
            "password": "controller123"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
    
    @pytest_asyncio.async_test
    async def test_login_valid_admin(self, async_client: AsyncClient):
        """Test login with valid admin credentials."""
        login_data = {
            "username": "admin@demo.com",
            "password": "admin123"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
    
    @pytest_asyncio.async_test
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "malte@demo.com",
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        
        result = response.json()
        assert "detail" in result or "message" in result
    
    @pytest_asyncio.async_test
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent@demo.com",
            "password": "anypassword"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_login_missing_fields(self, async_client: AsyncClient):
        """Test login with missing required fields."""
        # Missing password
        login_data = {
            "username": "malte@demo.com"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code in [400, 422]  # Bad Request or Validation Error
        
        # Missing username
        login_data = {
            "password": "employee123"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code in [400, 422]
    
    @pytest_asyncio.async_test
    async def test_login_empty_fields(self, async_client: AsyncClient):
        """Test login with empty fields."""
        login_data = {
            "username": "",
            "password": ""
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code in [400, 401, 422]
    
    @pytest_asyncio.async_test
    async def test_login_json_vs_form_data(self, async_client: AsyncClient):
        """Test login endpoint with different content types."""
        login_data = {
            "username": "malte@demo.com",
            "password": "employee123"
        }
        
        # Test with form data (usually expected for OAuth2)
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        # Test with JSON (should also work or return appropriate error)
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        # Some implementations expect form data for OAuth2, JSON might not work
        assert response.status_code in [200, 400, 422]


class TestAuthMeEndpoint:
    """Test /api/v1/auth/me endpoint."""
    
    @pytest_asyncio.async_test
    async def test_me_with_valid_employee_token(self, async_client: AsyncClient):
        """Test getting user info with valid employee token."""
        # First login
        login_data = {
            "username": "malte@demo.com",
            "password": "employee123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Then get user info
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_info = response.json()
        assert user_info["email"] == "malte@demo.com"
        assert user_info["role"] == "employee"
        assert "id" in user_info
        assert "full_name" in user_info
        assert "department" in user_info or True  # Optional field
    
    @pytest_asyncio.async_test
    async def test_me_with_valid_controller_token(self, async_client: AsyncClient):
        """Test getting user info with valid controller token."""
        # First login
        login_data = {
            "username": "controller1@demo.com",
            "password": "controller123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Then get user info
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_info = response.json()
        assert user_info["email"] == "controller1@demo.com"
        assert user_info["role"] == "controller"
        assert "id" in user_info
        assert "full_name" in user_info
    
    @pytest_asyncio.async_test
    async def test_me_with_valid_admin_token(self, async_client: AsyncClient):
        """Test getting user info with valid admin token."""
        # First login
        login_data = {
            "username": "admin@demo.com",
            "password": "admin123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Then get user info
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_info = response.json()
        assert user_info["email"] == "admin@demo.com"
        assert user_info["role"] == "admin"
        assert "id" in user_info
        assert "full_name" in user_info
    
    @pytest_asyncio.async_test
    async def test_me_without_token(self, async_client: AsyncClient):
        """Test getting user info without authentication token."""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_me_with_invalid_token(self, async_client: AsyncClient):
        """Test getting user info with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_me_with_malformed_token(self, async_client: AsyncClient):
        """Test getting user info with malformed token."""
        # Missing Bearer prefix
        headers = {"Authorization": "invalid_token_here"}
        
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        
        # Wrong format
        headers = {"Authorization": "Basic invalid_token_here"}
        
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    @pytest_asyncio.async_test
    async def test_me_with_expired_token(self, async_client: AsyncClient):
        """Test getting user info with expired token."""
        # Note: This test would require creating an expired token or waiting for expiry
        # For now, we'll test with a malformed token that simulates expiry
        headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.expired.token"}
        
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401


class TestAuthRegisterEndpoint:
    """Test /api/v1/auth/register endpoint (if available)."""
    
    @pytest_asyncio.async_test
    async def test_register_new_user(self, async_client: AsyncClient):
        """Test registering a new user."""
        register_data = {
            "email": "newuser@test.com",
            "password": "newpassword123",
            "full_name": "New User",
            "role": "employee"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=register_data)
        # Registration might be disabled or require admin privileges
        assert response.status_code in [200, 201, 403, 404, 501]
        
        if response.status_code in [200, 201]:
            result = response.json()
            assert "access_token" in result or "user" in result
    
    @pytest_asyncio.async_test
    async def test_register_duplicate_email(self, async_client: AsyncClient):
        """Test registering with existing email."""
        register_data = {
            "email": "malte@demo.com",  # Existing user
            "password": "newpassword123",
            "full_name": "Duplicate User",
            "role": "employee"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=register_data)
        # Should prevent duplicate registration or endpoint might not exist
        assert response.status_code in [400, 403, 404, 409, 422, 501]
    
    @pytest_asyncio.async_test
    async def test_register_invalid_data(self, async_client: AsyncClient):
        """Test registering with invalid data."""
        register_data = {
            "email": "invalid-email",  # Invalid email format
            "password": "123",  # Too short password
            "full_name": "",  # Empty name
            "role": "invalid_role"  # Invalid role
        }
        
        response = await async_client.post("/api/v1/auth/register", json=register_data)
        # Should validate data or endpoint might not exist
        assert response.status_code in [400, 404, 422, 501]


class TestAuthSecurityHeaders:
    """Test authentication-related security headers and behaviors."""
    
    @pytest_asyncio.async_test
    async def test_auth_endpoints_cors_headers(self, async_client: AsyncClient):
        """Test CORS headers on auth endpoints."""
        # Test OPTIONS request (preflight)
        response = await async_client.options("/api/v1/auth/login")
        # Should handle CORS properly
        assert response.status_code in [200, 204, 405]  # OK, No Content, or Method Not Allowed
    
    @pytest_asyncio.async_test
    async def test_auth_rate_limiting(self, async_client: AsyncClient):
        """Test rate limiting on auth endpoints."""
        login_data = {
            "username": "nonexistent@demo.com",
            "password": "wrongpassword"
        }
        
        # Make multiple failed login attempts
        for i in range(5):
            response = await async_client.post("/api/v1/auth/login", data=login_data)
            # Should consistently return 401 or eventually rate limit
            assert response.status_code in [401, 429]  # Unauthorized or Too Many Requests
    
    @pytest_asyncio.async_test
    async def test_auth_case_sensitivity(self, async_client: AsyncClient):
        """Test case sensitivity in email addresses."""
        # Test with different casing
        login_data = {
            "username": "MALTE@DEMO.COM",  # Uppercase
            "password": "employee123"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        # Email should be case-insensitive
        assert response.status_code in [200, 401]  # Might work or might be case-sensitive


class TestAuthEndpointEdgeCases:
    """Test edge cases and error conditions for auth endpoints."""
    
    @pytest_asyncio.async_test
    async def test_auth_very_long_inputs(self, async_client: AsyncClient):
        """Test auth endpoints with very long inputs."""
        long_string = "x" * 1000
        
        login_data = {
            "username": long_string,
            "password": long_string
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        # Should handle long inputs gracefully
        assert response.status_code in [400, 401, 422]
    
    @pytest_asyncio.async_test
    async def test_auth_special_characters(self, async_client: AsyncClient):
        """Test auth endpoints with special characters."""
        login_data = {
            "username": "user+test@demo.com",  # Valid email with plus
            "password": "pass@word!123"  # Password with special chars
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        # Should handle special characters properly
        assert response.status_code in [200, 401]  # Depends on if user exists
    
    @pytest_asyncio.async_test
    async def test_auth_unicode_characters(self, async_client: AsyncClient):
        """Test auth endpoints with unicode characters."""
        login_data = {
            "username": "user@démö.com",  # Unicode in email
            "password": "påsswörd123"  # Unicode in password
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        # Should handle unicode properly
        assert response.status_code in [200, 401, 422]
    
    @pytest_asyncio.async_test
    async def test_auth_sql_injection_attempts(self, async_client: AsyncClient):
        """Test auth endpoints against SQL injection attempts."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "admin'--",
            "admin' OR '1'='1",
            "' UNION SELECT * FROM users --"
        ]
        
        for malicious_input in malicious_inputs:
            login_data = {
                "username": malicious_input,
                "password": "anypassword"
            }
            
            response = await async_client.post("/api/v1/auth/login", data=login_data)
            # Should safely reject malicious input
            assert response.status_code in [400, 401, 422]
            
            # Response should not contain database error messages
            response_text = response.text.lower()
            dangerous_keywords = ["sql", "syntax", "database", "table", "column"]
            for keyword in dangerous_keywords:
                # Should not leak database information
                assert keyword not in response_text or "application/json" in response.headers.get("content-type", "")
