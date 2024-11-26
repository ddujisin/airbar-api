"""Utility functions for managing notification preferences."""
from datetime import datetime, time, timedelta
from typing import Optional
from fastapi import HTTPException
from prisma.models import NotificationPreference
from ..models.notification_preferences import NotificationPreference as PreferenceModel

class NotificationPreferencesManager:
    """Manager for handling notification preferences."""

    def __init__(self, prisma_client=None):
        """Initialize the manager with a Prisma client."""
        if not prisma_client:
            raise ValueError("Prisma client is required")
        self.prisma = prisma_client

    async def get_preferences(self, user_id: str) -> PreferenceModel:
        """Get notification preferences for a user."""
        prefs = await self.prisma.notification_preference.find_unique(
            where={"user_id": user_id}
        )
        if not prefs:
            return PreferenceModel(user_id=user_id)
        return PreferenceModel.model_validate(prefs)

    async def update_preferences(self, user_id: str, preferences: PreferenceModel) -> PreferenceModel:
        """Update notification preferences for a user."""
        try:
            prefs = await self.prisma.notification_preference.upsert(
                where={"user_id": user_id},
                data={
                    "create": preferences.model_dump(),
                    "update": preferences.model_dump(exclude={"user_id"})
                }
            )
            return PreferenceModel.model_validate(prefs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

    @staticmethod
    def should_notify(preferences: PreferenceModel, channel: str, priority: int = 0) -> bool:
        """Check if notification should be sent based on preferences."""
        if not preferences:
            return True

        # Check if channel is enabled
        if channel not in preferences.enabled_channels:
            return False

        # Check priority threshold
        if priority < preferences.priority_threshold:
            return False

        # Check if currently muted
        if preferences.muted_until and preferences.muted_until > datetime.now():
            return False

        # Check quiet hours
        if preferences.quiet_hours_start is not None and preferences.quiet_hours_end is not None:
            current_hour = datetime.now().hour
            if preferences.quiet_hours_start <= preferences.quiet_hours_end:
                if preferences.quiet_hours_start <= current_hour < preferences.quiet_hours_end:
                    return False
            else:  # Handles cases where quiet hours span midnight
                if current_hour >= preferences.quiet_hours_start or current_hour < preferences.quiet_hours_end:
                    return False

        return True

    async def mute_notifications(self, user_id: str, duration_minutes: int) -> PreferenceModel:
        """Temporarily mute notifications for a user."""
        if duration_minutes < 0:
            raise HTTPException(status_code=400, detail="Duration must be positive")

        muted_until = datetime.now() + timedelta(minutes=duration_minutes)
        prefs = await self.get_preferences(user_id)
        prefs.muted_until = muted_until
        return await self.update_preferences(user_id, prefs)
