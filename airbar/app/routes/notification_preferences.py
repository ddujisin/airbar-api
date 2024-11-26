"""Routes for managing notification preferences."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from ..models.notification_preferences import NotificationPreference
from ..utils.notification_preferences import NotificationPreferencesManager

router = APIRouter(prefix="/notification-preferences", tags=["notifications"])

@router.get("/{user_id}", response_model=NotificationPreference)
async def get_notification_preferences(user_id: str):
    """Get notification preferences for a user."""
    return await NotificationPreferencesManager.get_preferences(user_id)

@router.put("/{user_id}", response_model=NotificationPreference)
async def update_notification_preferences(
    user_id: str,
    preferences: NotificationPreference
):
    """Update notification preferences for a user."""
    if user_id != preferences.user_id:
        raise HTTPException(
            status_code=400,
            detail="User ID in path must match preference user ID"
        )
    return await NotificationPreferencesManager.update_preferences(user_id, preferences)

@router.post("/{user_id}/mute", response_model=NotificationPreference)
async def mute_notifications(user_id: str, duration_minutes: int):
    """Temporarily mute notifications for a user."""
    return await NotificationPreferencesManager.mute_notifications(user_id, duration_minutes)
