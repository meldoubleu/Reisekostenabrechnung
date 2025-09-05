import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
import tempfile
import os
from pathlib import Path

from backend.app.main import app
from backend.app.db.session import Base
from backend.app.models.travel import Travel, Receipt
from backend.app.models.user import User
from backend.app.api.deps import get_db


# Test database URL (in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_engine):
    """Create a test client with test database."""
    # Create a session maker for the test engine
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    
    # Recreate all tables to ensure clean state
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async def get_test_db():
        async with TestSessionLocal() as session:
            yield session
    
    # Override the dependency
    app.dependency_overrides[get_db] = get_test_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_db(test_engine):
    """Create a test database session for direct model testing."""
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    
    # Recreate all tables to ensure clean state
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads during tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Override the upload directory setting
        original_upload_dir = os.environ.get("UPLOAD_DIR", "./uploads")
        os.environ["UPLOAD_DIR"] = temp_dir
        yield Path(temp_dir)
        os.environ["UPLOAD_DIR"] = original_upload_dir


@pytest.fixture
def sample_travel_data():
    """Sample travel data for testing."""
    return {
        "employee_name": "John Doe",
        "start_at": "2025-08-25T09:00:00",
        "end_at": "2025-08-25T17:00:00",
        "destination_city": "Berlin",
        "destination_country": "Germany",
        "purpose": "Business Meeting",
        "cost_center": "IT001"
    }


@pytest.fixture
def sample_receipt_content():
    """Sample receipt content for OCR testing."""
    return b"Test receipt content - this would be an image file"


@pytest_asyncio.fixture
async def admin_headers(client_with_users: AsyncClient):
    """Create authentication headers for admin user."""
    login_data = {
        "email": "admin@demo.com",
        "password": "admin123"
    }
    
    response = await client_with_users.post("/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return {"Authorization": f"Bearer {token_data['access_token']}"}
    else:
        # Fallback if login endpoint doesn't exist or fails
        return {"Authorization": "Bearer admin_test_token"}


@pytest_asyncio.fixture
async def employee_headers(client_with_users: AsyncClient):
    """Create authentication headers for employee user."""
    login_data = {
        "email": "max.mustermann@demo.com",
        "password": "employee123"
    }
    
    response = await client_with_users.post("/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return {"Authorization": f"Bearer {token_data['access_token']}"}
    else:
        # Fallback if login endpoint doesn't exist or fails
        return {"Authorization": "Bearer employee_test_token"}


@pytest_asyncio.fixture
async def controller_headers(client_with_users: AsyncClient):
    """Create authentication headers for controller user."""
    login_data = {
        "email": "controller1@demo.com",
        "password": "controller123"
    }
    
    response = await client_with_users.post("/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return {"Authorization": f"Bearer {token_data['access_token']}"}
    else:
        # Fallback if login endpoint doesn't exist or fails
        return {"Authorization": "Bearer controller_test_token"}


@pytest_asyncio.fixture
async def demo_users(test_engine):
    """Create demo users in the test database."""
    from backend.app.core.auth import get_password_hash
    
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    
    async with TestSessionLocal() as session:
        # Create admin user
        admin_user = User(
            email="admin@demo.com",
            name="System Administrator",
            password_hash=get_password_hash("admin123"),
            role="admin",
            company="Demo GmbH",
            department="IT"
        )
        session.add(admin_user)
        
        # Create controller user
        controller_user = User(
            email="controller1@demo.com",
            name="Anna Controlling",
            password_hash=get_password_hash("controller123"),
            role="controller",
            company="Demo GmbH",
            department="Finance"
        )
        session.add(controller_user)
        
        # Create employee user
        employee_user = User(
            email="max.mustermann@demo.com",
            name="Max Mustermann",
            password_hash=get_password_hash("employee123"),
            role="employee",
            company="Demo GmbH",
            department="Sales",
            cost_center="SALES-001"
        )
        session.add(employee_user)
        
        await session.commit()
        return {
            "admin": admin_user,
            "controller": controller_user,
            "employee": employee_user
        }


@pytest_asyncio.fixture
async def client_with_users(test_engine, demo_users):
    """Create a test client with demo users already in the database."""
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    
    async def get_test_db():
        async with TestSessionLocal() as session:
            yield session
    
    # Override the dependency
    app.dependency_overrides[get_db] = get_test_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()
