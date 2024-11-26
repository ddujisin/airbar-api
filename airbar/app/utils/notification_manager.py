from typing import Dict, List, Optional, Union
from prisma import Prisma
from fastapi import HTTPException
from datetime import datetime
import asyncio
import json
from enum import Enum
from .notification_preferences import notification_preferences_manager, NotificationChannel

class NotificationType(str, Enum):
    LOW_STOCK = "LOW_STOCK"
    NEW_ORDER = "NEW_ORDER"
    PAYMENT = "PAYMENT"
    SYSTEM = "SYSTEM"
    RESERVATION = "RESERVATION"

class NotificationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class NotificationManager:
    def __init__(self):
        self.db = Prisma()  # Initialize Prisma instance
        self._connected = False
        self._lock = asyncio.Lock()
        self._test_mode = False

    async def _ensure_connection(self):
        """Ensure database connection is established."""
        async with self._lock:
            try:
                if not self._connected:
                    await self.db.connect()
                    self._connected = True
            except Exception as e:
                if "Already connected" not in str(e):
                    raise HTTPException(
                        status_code=500,
                        detail=f"Database connection error: {str(e)}"
                    )

    async def create_notification(
        self,
        type: str,
        message: str,
        priority: str = NotificationPriority.MEDIUM.value,
        target_user: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a new notification and check user preferences."""
        try:
            await self._ensure_connection()

            # Check user preferences if target user is specified
            if target_user:
                preferences = await notification_preferences_manager.get_preferences(target_user)
                if not notification_preferences_manager.should_send_notification(
                    preferences,
                    type,
                    "websocket"
                ):
                    return None

            # Convert metadata to proper JSON format
            notification_data = {
                "type": type,
                "message": message,
                "priority": priority,
                "targetUser": target_user,
                "read": False,
            }

            # Handle metadata as proper JSON
            if metadata is not None:
                notification_data["metadata"] = json.dumps(metadata)

            notification = await self.db.notification.create(data=notification_data)
            return {
                "id": notification.id,
                "type": notification.type,
                "message": notification.message,
                "priority": notification.priority,
                "created_at": notification.createdAt,
                "read": notification.read
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating notification: {str(e)}"
            )

    async def get_notifications(
        self,
        user_id: Optional[str] = None,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get notifications for a user based on their preferences."""
        try:
            await self._ensure_connection()
            where_clause = {}
            if user_id:
                where_clause["targetUser"] = user_id
                # Check user preferences
                preferences = await notification_preferences_manager.get_preferences(user_id)
                if not preferences.enabled:
                    return []
            if unread_only:
                where_clause["read"] = False
            if notification_type:
                where_clause["type"] = notification_type

            notifications = await self.db.notification.find_many(
                where=where_clause,
                order={
                    "priority": "desc",
                    "createdAt": "desc"
                },
                take=limit
            )
            return [
                {
                    "id": notif.id,
                    "type": notif.type,
                    "message": notif.message,
                    "priority": notif.priority,
                    "created_at": notif.createdAt,
                    "read": notif.read,
                    "metadata": notif.metadata
                }
                for notif in notifications
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching notifications: {str(e)}"
            )

    async def mark_as_read(
        self,
        notification_id: Union[str, List[str]]
    ) -> Dict:
        """Mark one or multiple notifications as read."""
        try:
            await self._ensure_connection()
            if isinstance(notification_id, list):
                await self.db.notification.update_many(
                    where={"id": {"in": notification_id}},
                    data={
                        "read": True,
                        "readAt": datetime.now()
                    }
                )
                return {"success": True, "count": len(notification_id)}
            else:
                notification = await self.db.notification.update(
                    where={"id": notification_id},
                    data={
                        "read": True,
                        "readAt": datetime.now()
                    }
                )
                return {
                    "id": notification.id,
                    "read": notification.read,
                    "read_at": notification.readAt
                }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error marking notification(s) as read: {str(e)}"
            )

    async def mark_all_as_read(self, user_id: Optional[str] = None) -> Dict:
        """Mark all notifications as read for a user."""
        try:
            await self._ensure_connection()
            where_clause = {"read": False}
            if user_id:
                where_clause["targetUser"] = user_id

            await self.db.notification.update_many(
                where=where_clause,
                data={"read": True}
            )
            return {"success": True}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error marking notifications as read: {str(e)}"
            )

    async def delete_notifications(
        self,
        notification_ids: Union[str, List[str]]
    ) -> Dict:
        """Delete one or multiple notifications."""
        try:
            await self._ensure_connection()
            if isinstance(notification_ids, list):
                await self.db.notification.delete_many(
                    where={"id": {"in": notification_ids}}
                )
                return {"success": True, "count": len(notification_ids)}
            else:
                await self.db.notification.delete(
                    where={"id": notification_ids}
                )
                return {"success": True}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting notification(s): {str(e)}"
            )

notification_manager = NotificationManager()
