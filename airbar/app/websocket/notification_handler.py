from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional, List
from ..utils.notification_manager import NotificationType, NotificationPriority
from ..utils.notification_preferences import notification_preferences_manager
from ..models.notification_preferences import NotificationChannel
import json
import logging
from prisma import Prisma
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NotificationWebsocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "admin": set(),
            "guest": set()
        }
        self.user_connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[str, Set[str]] = {}
        self.db = Prisma()

    async def connect(self, websocket: WebSocket, client_type: str, user_id: Optional[str] = None):
        """Connect a client to the notification websocket."""
        await websocket.accept()
        self.active_connections[client_type].add(websocket)
        if user_id:
            self.user_connections[user_id] = websocket

        try:
            while True:
                data = await websocket.receive_text()
                await self.handle_message(websocket, data, client_type, user_id)
        except WebSocketDisconnect:
            self.disconnect(websocket, client_type, user_id)
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            self.disconnect(websocket, client_type, user_id)

    def disconnect(self, websocket: WebSocket, client_type: str, user_id: Optional[str] = None):
        """Disconnect a client from the notification websocket."""
        self.active_connections[client_type].discard(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]

    async def should_send_notification(
        self,
        user_id: str,
        notification_type: str
    ) -> bool:
        """Check if user should receive notification based on preferences and subscriptions."""
        try:
            # Get user preferences
            preferences = await notification_preferences_manager.get_preferences(user_id)

            # Check preferences first
            if not notification_preferences_manager.should_send_notification(
                preferences,
                notification_type,
                NotificationChannel.WEBSOCKET
            ):
                return False

            # Then check subscriptions
            if user_id not in self.user_subscriptions:
                return True  # Default to sending if no subscriptions set

            subscriptions = self.user_subscriptions[user_id]
            return len(subscriptions) == 0 or notification_type in subscriptions
        except Exception as e:
            logger.error(f"Error checking notification preferences: {str(e)}")
            return True  # Default to sending on error

    async def broadcast_to_admins(self, message: Dict):
        """Broadcast a message to all connected admin clients."""
        for connection in self.active_connections["admin"]:
            try:
                websocket = connection
                user_id = next(
                    (uid for uid, conn in self.user_connections.items() if conn == websocket),
                    None
                )
                if user_id and await self.should_send_notification(user_id, message["type"]):
                    await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to admin: {str(e)}")

    async def broadcast_to_guests(self, message: Dict):
        """Broadcast a message to all connected guest clients."""
        for connection in self.active_connections["guest"]:
            try:
                websocket = connection
                user_id = next(
                    (uid for uid, conn in self.user_connections.items() if conn == websocket),
                    None
                )
                if user_id and await self.should_send_notification(user_id, message["type"]):
                    await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to guest: {str(e)}")

    async def send_to_user(self, user_id: str, message: Dict):
        """Send a message to a specific user."""
        if user_id in self.user_connections and await self.should_send_notification(user_id, message["type"]):
            try:
                await self.user_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {str(e)}")

    async def handle_message(
        self,
        websocket: WebSocket,
        message: str,
        client_type: str,
        user_id: Optional[str]
    ):
        """Handle incoming websocket messages."""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                })
            elif message_type == "mark_read":
                notification_id = data.get("notification_id")
                if notification_id and user_id:
                    await self.mark_notification_read(client_type, user_id, notification_id)
            elif message_type == "subscribe":
                topics = data.get("topics", [])
                if user_id:
                    await self.subscribe_to_topics(client_type, user_id, topics)
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")

    async def mark_notification_read(
        self,
        client_type: str,
        user_id: str,
        notification_id: str
    ):
        """Mark a notification as read."""
        try:
            await self.db.notification.update(
                where={
                    "id": notification_id,
                    "userId": user_id
                },
                data={
                    "read": True,
                    "readAt": datetime.now()
                }
            )
            await self.send_to_user(user_id, {
                "type": "notification_updated",
                "notification_id": notification_id,
                "read": True
            })
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")

    async def subscribe_to_topics(
        self,
        client_type: str,
        user_id: str,
        topics: List[str]
    ):
        """Subscribe a user to notification topics."""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()

        self.user_subscriptions[user_id].update(topics)
        await self.send_to_user(user_id, {
            "type": "subscription_updated",
            "topics": list(self.user_subscriptions[user_id])
        })

    async def notify_low_stock(self, item_name: str, current_stock: int):
        """Send low stock notification to admins."""
        message = {
            "type": NotificationType.LOW_STOCK,
            "priority": NotificationPriority.HIGH,
            "message": f"Low stock alert: {item_name} (Current stock: {current_stock})"
        }
        await self.broadcast_to_admins(message)

    async def notify_new_order(self, order_data: Dict):
        """Send new order notification to admins."""
        message = {
            "type": NotificationType.NEW_ORDER,
            "priority": NotificationPriority.MEDIUM,
            "message": f"New order received: #{order_data.get('order_id')}",
            "data": order_data
        }
        await self.broadcast_to_admins(message)

    async def notify_payment(self, payment_data: Dict):
        """Send payment notification to relevant users."""
        message = {
            "type": NotificationType.PAYMENT,
            "priority": NotificationPriority.MEDIUM,
            "message": f"Payment processed: ${payment_data.get('amount')}",
            "data": payment_data
        }
        if payment_data.get("user_id"):
            await self.send_to_user(payment_data["user_id"], message)
        await self.broadcast_to_admins(message)

    async def cleanup_expired_notifications(self):
        """Clean up expired notifications and disconnected users."""
        try:
            # Remove expired notifications (older than 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            await self.db.notification.delete_many(
                where={
                    "createdAt": {
                        "lt": thirty_days_ago
                    },
                    "read": True
                }
            )

            # Clean up disconnected user subscriptions
            disconnected_users = [
                user_id for user_id in self.user_subscriptions
                if user_id not in self.user_connections
            ]
            for user_id in disconnected_users:
                del self.user_subscriptions[user_id]

            logger.info("Completed notification system cleanup")
        except Exception as e:
            logger.error(f"Error during notification cleanup: {str(e)}")

notification_ws_manager = NotificationWebsocketManager()
