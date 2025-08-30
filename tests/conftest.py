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
from backend.app.api.v1.travels import get_db


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
    
    # Clear the database before each test
    async with test_engine.begin() as conn:
        # Delete all data from tables (in correct order due to foreign keys)
        await conn.execute(text("DELETE FROM receipts"))
        await conn.execute(text("DELETE FROM travels"))
    
    async def get_test_db():
        async with TestSessionLocal() as session:
            yield session
    
    # Override the dependency
    app.dependency_overrides[get_db] = get_test_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


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
