"""Test configuration and fixtures."""
import pytest
import asyncio
from fastapi import WebSocket
from unittest.mock import AsyncMock
from prisma import Prisma
from app.websocket.notification_handler import NotificationConnectionManager
from app.utils.notification_preferences import NotificationPreferencesManager

@pytest.fixture(scope="session")
def event_loop():
    """Create and configure event loop for tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def prisma_client():
    """Initialize Prisma client for tests."""
    client = Prisma()
    await client.connect()
    try:
        yield client
    finally:
        await client.disconnect()

@pytest.fixture(autouse=True)
async def setup_test_database(prisma_client):
    """Set up test database before each test."""
    # Clear existing data
    await prisma_client.notification_preference.delete_many()
    yield
    # Cleanup after test
    await prisma_client.notification_preference.delete_many()

@pytest.fixture
def test_user():
    """Create test user ID."""
    return "test_user_123"

@pytest.fixture
async def mock_websocket():
    """Create mock WebSocket instance."""
    mock = AsyncMock(spec=WebSocket)
    mock.send_json = AsyncMock()
    return mock

@pytest.fixture
async def preferences_manager(prisma_client):
    """Create NotificationPreferencesManager instance."""
    return NotificationPreferencesManager(prisma_client)

@pytest.fixture
async def connection_manager(preferences_manager):
    """Create NotificationConnectionManager instance."""
    return NotificationConnectionManager(preferences_manager)
