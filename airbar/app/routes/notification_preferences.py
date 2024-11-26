from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional
from datetime import datetime, timedelta
from ..models.notification_preferences import NotificationPreferences, NotificationChannel, NotificationType
from ..utils.notification_preferences import notification_preferences_manager
from ..middleware.session_middleware import get_current_session

router = APIRouter()

@router.get("")
async def get_notification_preferences(
    session=Depends(get_current_session)
) -> NotificationPreferences:
    """Get notification preferences for the current user."""
    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return await notification_preferences_manager.get_preferences(user_id)

@router.put("")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    session=Depends(get_current_session)
) -> NotificationPreferences:
    """Update notification preferences for the current user."""
    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Ensure the user_id in preferences matches the authenticated user
    if preferences.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot modify preferences for another user"
        )

    return await notification_preferences_manager.update_preferences(
        user_id=user_id,
        preferences=preferences
    )

@router.post("/mute")
async def mute_notifications(
    duration_minutes: int,
    session=Depends(get_current_session)
) -> NotificationPreferences:
    """Mute notifications for a specified duration."""
    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    if duration_minutes < 0 or duration_minutes > 1440:  # Max 24 hours
        raise HTTPException(
            status_code=400,
            detail="Duration must be between 0 and 1440 minutes"
        )

    prefs = await notification_preferences_manager.get_preferences(user_id)
    muted_until = datetime.now() + timedelta(minutes=duration_minutes)
    prefs.muted_until = muted_until.isoformat()

    return await notification_preferences_manager.update_preferences(
        user_id=user_id,
        preferences=prefs
    )

@router.post("/unmute")
async def unmute_notifications(
    session=Depends(get_current_session)
) -> NotificationPreferences:
    """Unmute notifications."""
    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    prefs = await notification_preferences_manager.get_preferences(user_id)
    prefs.muted_until = None

    return await notification_preferences_manager.update_preferences(
        user_id=user_id,
        preferences=prefs
    )

@router.put("/priority-threshold")
async def update_priority_threshold(
    threshold: int,
    session=Depends(get_current_session)
) -> NotificationPreferences:
    """Update the priority threshold for notifications."""
    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    if threshold < 0 or threshold > 10:
        raise HTTPException(
            status_code=400,
            detail="Priority threshold must be between 0 and 10"
        )

    prefs = await notification_preferences_manager.get_preferences(user_id)
    prefs.priority_threshold = threshold

    return await notification_preferences_manager.update_preferences(
        user_id=user_id,
        preferences=prefs
    )
