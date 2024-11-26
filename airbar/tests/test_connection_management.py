"""Tests for WebSocket connection management."""
import pytest
from fastapi import WebSocket, WebSocketDisconnect
from unittest.mock import AsyncMock, MagicMock
from app.websocket.notification_handler import NotificationConnectionManager

@pytest.fixture
def connection_manager():
    """Create a connection manager instance."""
    return NotificationConnectionManager()

@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection."""
    websocket = AsyncMock(spec=WebSocket)
    websocket.send_json = AsyncMock()
    return websocket

@pytest.mark.asyncio
async def test_connection_lifecycle(connection_manager, mock_websocket):
    """Test WebSocket connection lifecycle."""
    user_id = "test_user"

    # Test connection
    await connection_manager.connect(mock_websocket, user_id)
    assert user_id in connection_manager.active_connections
    assert mock_websocket in connection_manager.active_connections[user_id]

    # Test disconnection
    connection_manager.disconnect(mock_websocket, user_id)
    assert user_id not in connection_manager.active_connections

@pytest.mark.asyncio
async def test_notification_sending(connection_manager, mock_websocket):
    """Test sending notifications through WebSocket."""
    user_id = "test_user"
    test_message = {"type": "test", "content": "Hello"}

    # Connect user
    await connection_manager.connect(mock_websocket, user_id)

    # Send notification
    await connection_manager.send_notification(user_id, test_message)
    mock_websocket.send_json.assert_called_once_with(test_message)

@pytest.mark.asyncio
async def test_broadcast(connection_manager, mock_websocket):
    """Test broadcasting messages to all connections."""
    user_ids = ["user1", "user2"]
    test_message = {"type": "broadcast", "content": "Hello all"}

    # Connect multiple users
    for user_id in user_ids:
        websocket = AsyncMock(spec=WebSocket)
        websocket.send_json = AsyncMock()
        await connection_manager.connect(websocket, user_id)

    # Broadcast message
    await connection_manager.broadcast(test_message)

    # Verify all connections received the message
    for user_id in user_ids:
        for connection in connection_manager.active_connections[user_id]:
            connection.send_json.assert_called_once_with(test_message)

@pytest.mark.asyncio
async def test_handle_disconnection(connection_manager, mock_websocket):
    """Test handling WebSocket disconnection during send."""
    user_id = "test_user"
    test_message = {"type": "test", "content": "Hello"}

    # Setup mock to raise disconnect on send
    mock_websocket.send_json.side_effect = WebSocketDisconnect()

    # Connect and attempt to send
    await connection_manager.connect(mock_websocket, user_id)
    await connection_manager.send_notification(user_id, test_message)

    # Verify connection was removed
    assert user_id not in connection_manager.active_connections
