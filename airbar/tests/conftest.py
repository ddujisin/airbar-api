import pytest
import asyncio
from prisma import Prisma
from app.utils.notification_manager import notification_manager
from app.utils.notification_preferences import notification_preferences_manager

@pytest.fixture(scope="session")
def event_loop_policy():
    """Create and configure event loop policy for tests."""
    return asyncio.get_event_loop_policy()

@pytest.fixture(scope="function")
async def prisma_client():
    """Provide a Prisma client for tests."""
    client = Prisma()
    await client.connect()
    yield client
    await client.disconnect()

@pytest.fixture(autouse=True)
async def setup_test_database(prisma_client):
    """Set up a clean test database before each test."""
    # Initialize database clients for managers
    notification_manager.db = prisma_client
    notification_preferences_manager.db = prisma_client
    notification_manager._connected = True
    notification_preferences_manager._connected = True

    # Clean up existing test data
    await prisma_client.notificationpreference.delete_many(
        where={"userId": {"contains": "test-"}}
    )
    await prisma_client.notification.delete_many(
        where={"targetUser": {"contains": "test-"}}
    )

    yield

    # Cleanup after tests
    await prisma_client.notificationpreference.delete_many(
        where={"userId": {"contains": "test-"}}
    )
    await prisma_client.notification.delete_many(
        where={"targetUser": {"contains": "test-"}}
    )

    # Reset connection state
    notification_manager._connected = False
    notification_preferences_manager._connected = False
    notification_manager.db = None
    notification_preferences_manager.db = None
