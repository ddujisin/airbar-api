from typing import Dict, List, Optional
from ..models.notification_preferences import (
    NotificationPreferences, NotificationChannel,
    NotificationType, QuietHours
)
from prisma import Prisma, Json
from fastapi import HTTPException
from datetime import datetime
import pytz
import json
import asyncio

class NotificationPreferencesManager:
    def __init__(self):
        self.db = Prisma()
        self._connected = False
        self._lock = asyncio.Lock()
        self._test_mode = False  # Add test mode flag

    async def _ensure_connection(self):
        """Ensure database connection is established with proper locking."""
        async with self._lock:
            try:
                if not self._connected:
                    if self._test_mode:
                        # Simulate connection failure in test mode
                        raise Exception("Test connection failure")
                    try:
                        await self.db.connect()
                    except Exception as e:
                        if "Already connected" not in str(e):
                            raise e
                    self._connected = True
            except Exception as e:
                self._connected = False
                raise HTTPException(
                    status_code=500,
                    detail=f"Database connection error: {str(e)}"
                )

    async def get_preferences(self, user_id: str) -> NotificationPreferences:
        """Get notification preferences for a user."""
        try:
            await self._ensure_connection()
            prefs = await self.db.notificationpreference.find_unique(
                where={"userId": user_id}
            )
            if not prefs:
                # Return default preferences
                return NotificationPreferences(
                    user_id=user_id,
                    channels={
                        "NEW_ORDER": ["websocket"],
                        "PAYMENT": ["websocket"],
                        "LOW_STOCK": ["websocket"],
                        "SYSTEM": ["websocket"],
                        "ALERT": ["websocket", "email"]
                    },
                    enabled=True,
                    priority_threshold=5
                )

            prefs_dict = prefs.model_dump()
            prefs_dict['user_id'] = prefs.userId
            return NotificationPreferences(**prefs_dict)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching notification preferences: {str(e)}"
            )

    async def update_preferences(
        self,
        user_id: str,
        preferences: NotificationPreferences
    ) -> NotificationPreferences:
        """Update notification preferences for a user."""
        try:
            await self._ensure_connection()

            # Convert channels to Prisma Json type
            channels_data = Json(preferences.channels)

            # Convert quiet_hours to Prisma Json type
            quiet_hours_data = Json(preferences.quiet_hours if preferences.quiet_hours else {})

            update_data = {
                "userId": user_id,
                "channels": channels_data,
                "quietHours": quiet_hours_data,
                "enabled": preferences.enabled,
                "mutedUntil": preferences.muted_until,
                "priorityThreshold": preferences.priority_threshold
            }

            updated_prefs = await self.db.notificationpreference.upsert(
                where={"userId": user_id},
                data={
                    "create": update_data,
                    "update": update_data
                }
            )

            prefs_dict = updated_prefs.model_dump()
            prefs_dict['user_id'] = updated_prefs.userId
            return NotificationPreferences(**prefs_dict)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error updating notification preferences: {str(e)}"
            )

    def should_send_notification(
        self,
        preferences: NotificationPreferences,
        notification_type: str,
        channel: str,
        priority: Optional[int] = None
    ) -> bool:
        """Check if notification should be sent based on preferences."""
        if not preferences.enabled:
            return False

        # Check if muted
        if preferences.muted_until:
            muted_until = datetime.fromisoformat(preferences.muted_until)
            if datetime.now(pytz.UTC) < muted_until:
                return False

        # Check priority threshold
        if priority is not None and preferences.priority_threshold:
            if priority < preferences.priority_threshold:
                return False

        # Check if notification type is enabled for the channel
        if notification_type not in preferences.channels:
            return True  # Default to sending if not specified
        if channel not in preferences.channels[notification_type]:
            return False

        # Check quiet hours if specified
        if preferences.quiet_hours:
            now = datetime.now(pytz.UTC)
            day = now.strftime("%A").lower()
            if day in preferences.quiet_hours:
                quiet_start = datetime.strptime(
                    preferences.quiet_hours[day]["start"],
                    "%H:%M"
                ).time()
                quiet_end = datetime.strptime(
                    preferences.quiet_hours[day]["end"],
                    "%H:%M"
                ).time()
                current_time = now.time()

                # Handle overnight quiet hours
                if quiet_start > quiet_end:
                    return not (current_time >= quiet_start or current_time < quiet_end)
                else:
                    return not (quiet_start <= current_time < quiet_end)

        return True

notification_preferences_manager = NotificationPreferencesManager()
