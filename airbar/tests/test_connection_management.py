import pytest
from fastapi import HTTPException
from app.utils.notification_manager import notification_manager
from app.utils.notification_preferences import notification_preferences_manager
import asyncio
from prisma import Prisma

@pytest.fixture(scope="function")
async def setup_managers():
    """Set up notification managers with database client."""
    client = Prisma()
    await client.connect()
    return client

@pytest.mark.asyncio
async def test_connection_management(setup_managers):
    """Test database connection management for notification managers."""
    client = await setup_managers
    notification_manager.db = client
    notification_manager._connected = False

    assert not notification_manager._connected
    await notification_manager._ensure_connection()
    assert notification_manager._connected

    assert not notification_preferences_manager._connected
    await notification_preferences_manager._ensure_connection()
    assert notification_preferences_manager._connected

@pytest.mark.asyncio
async def test_connection_error_handling():
    """Test error handling for database connection issues."""
    # Force disconnect state and enable test mode
    notification_manager._connected = False
    notification_manager._test_mode = True
    notification_preferences_manager._connected = False
    notification_preferences_manager._test_mode = True

    # Test error handling in notification manager
    with pytest.raises(HTTPException) as exc_info:
        await notification_manager.create_notification(
            type="SYSTEM",
            message="Test connection error",
            metadata={"test": True}
        )
    assert exc_info.value.status_code == 500
    assert "Error creating notification" in str(exc_info.value.detail)

    # Test error handling in preferences manager
    with pytest.raises(HTTPException) as exc_info:
        await notification_preferences_manager.get_preferences("test-user")
    assert exc_info.value.status_code == 500
    assert "Error fetching notification preferences" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_concurrent_connections(setup_managers):
    """Test concurrent database connections."""
    client = await setup_managers
    notification_manager.db = client
    notification_preferences_manager.db = client
    notification_manager._connected = False
    notification_manager._test_mode = False
    notification_preferences_manager._connected = False
    notification_preferences_manager._test_mode = False

    async def concurrent_operation(index: int):
        try:
            if index % 2 == 0:
                await notification_manager.create_notification(
                    type="SYSTEM",
                    message=f"Concurrent test {index}",
                    metadata={"test_id": index}
                )
            else:
                await notification_preferences_manager.get_preferences(f"test-user-{index}")
        except Exception as e:
            pytest.fail(f"Operation {index} failed: {str(e)}")

    try:
        # Run concurrent operations in smaller batches
        batch_size = 2
        for i in range(0, 6, batch_size):
            batch = range(i, min(i + batch_size, 6))
            await asyncio.gather(*[concurrent_operation(j) for j in batch])
    finally:
        await client.disconnect()
