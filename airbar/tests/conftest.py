"""Test configuration and fixtures."""
import pytest
import asyncio
from prisma import Prisma
from app.websocket.notification_handler import notification_manager
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
    yield client
    await client.disconnect()

@pytest.fixture(autouse=True)
async def setup_test_database(prisma_client):
    """Set up test database before each test."""
    # Clear existing data
    await prisma_client.notification_preference.delete_many()
    yield
    # Cleanup after test
    await prisma_client.notification_preference.delete_many()
