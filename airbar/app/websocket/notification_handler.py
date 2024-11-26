"""WebSocket handler for real-time notifications."""
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from ..models.notification_preferences import NotificationPreference
from ..utils.notification_preferences import NotificationPreferencesManager

class NotificationConnectionManager:
    """Manages WebSocket connections for notifications."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a new WebSocket client."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect a WebSocket client."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_notification(self, user_id: str, message: dict, priority: int = 0):
        """Send notification to a specific user."""
        if user_id not in self.active_connections:
            return

        # Get user preferences
        preferences = await NotificationPreferencesManager.get_preferences(user_id)

        # Check if we should send the notification
        if not NotificationPreferencesManager.should_notify(preferences, "websocket", priority):
            return

        # Send to all active connections for the user
        disconnected = set()
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, user_id)

    async def broadcast(self, message: dict, priority: int = 0):
        """Broadcast message to all connected clients."""
        for user_id in list(self.active_connections.keys()):
            await self.send_notification(user_id, message, priority)

notification_manager = NotificationConnectionManager()
