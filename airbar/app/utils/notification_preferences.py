"""Utility functions for managing notification preferences."""
from datetime import datetime, time, timedelta
from typing import Optional
from fastapi import HTTPException
from prisma.models import NotificationPreference
from ..models.notification_preferences import NotificationPreference as PreferenceModel

class NotificationPreferencesManager:
    """Manager for handling notification preferences."""

    @staticmethod
    async def get_preferences(user_id: str) -> PreferenceModel:
        """Get notification preferences for a user."""
        prefs = await NotificationPreference.prisma().find_unique(
            where={"user_id": user_id}
        )
        if not prefs:
            return PreferenceModel(user_id=user_id)
        return PreferenceModel.model_validate(prefs)

    @staticmethod
    async def update_preferences(user_id: str, preferences: PreferenceModel) -> PreferenceModel:
        """Update notification preferences for a user."""
        try:
            prefs = await NotificationPreference.prisma().upsert(
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

    @staticmethod
    async def mute_notifications(user_id: str, duration_minutes: int) -> PreferenceModel:
        """Temporarily mute notifications for a user."""
        if duration_minutes < 0:
            raise HTTPException(status_code=400, detail="Duration must be positive")

        muted_until = datetime.now() + timedelta(minutes=duration_minutes)
        prefs = await NotificationPreferencesManager.get_preferences(user_id)
        prefs.muted_until = muted_until
        return await NotificationPreferencesManager.update_preferences(user_id, prefs)
