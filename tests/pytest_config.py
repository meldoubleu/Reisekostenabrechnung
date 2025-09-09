"""
Test configuration for comprehensive test coverage
"""

import pytest
import pytest_asyncio
import asyncio


def pytest_configure(config):
    """Configure pytest markers and settings."""
    config.addinivalue_line(
        "markers", "unit: Unit tests that test individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that test component interactions"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests that test complete workflows"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add e2e marker to comprehensive workflow tests
        if "test_comprehensive_workflow" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        
        # Add integration marker to integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add unit marker to unit tests
        if any(unit_test in item.nodeid for unit_test in ["test_models", "test_auth_utils", "test_data_validation"]):
            item.add_marker(pytest.mark.unit)


# Configure asyncio for pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
