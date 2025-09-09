"""
Test utilities for authentication and authorization testing.
"""
import asyncio
from typing import Dict, Optional
from httpx import AsyncClient


class TestAuthHelper:
    """Helper class for test authentication."""
    
    @staticmethod
    async def login_as_user(client: AsyncClient, email: str, password: str = "test123") -> Dict:
        """Login as a user and return the auth response."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")
        return response.json()
    
    @staticmethod
    async def get_auth_headers(client: AsyncClient, email: str, password: str = "test123") -> Dict[str, str]:
        """Get authentication headers for a user."""
        auth_data = await TestAuthHelper.login_as_user(client, email, password)
        return {"Authorization": f"Bearer {auth_data['access_token']}"}
    
    @staticmethod
    async def get_admin_headers(client: AsyncClient) -> Dict[str, str]:
        """Get admin authentication headers."""
        return await TestAuthHelper.get_auth_headers(client, "admin@demo.com", "admin123")
    
    @staticmethod
    async def get_controller_headers(client: AsyncClient) -> Dict[str, str]:
        """Get controller authentication headers."""
        return await TestAuthHelper.get_auth_headers(client, "controller1@demo.com", "controller123")
    
    @staticmethod
    async def get_employee_headers(client: AsyncClient) -> Dict[str, str]:
        """Get employee authentication headers."""
        return await TestAuthHelper.get_auth_headers(client, "max.mustermann@demo.com", "employee123")


def require_auth(role: Optional[str] = None):
    """Decorator to mark tests that require authentication."""
    def decorator(test_func):
        test_func._requires_auth = True
        test_func._required_role = role
        return test_func
    return decorator
