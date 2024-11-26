from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Set, Union
from ..utils.notification_manager import (
    notification_manager,
    NotificationType,
    NotificationPriority
)
from ..middleware.session_middleware import get_current_session
from pydantic import BaseModel
from ..websocket.notification_handler import notification_ws_manager

router = APIRouter()

class NotificationCreate(BaseModel):
    type: NotificationType
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    target_user: Optional[str] = None
    metadata: Optional[Dict] = None

class NotificationSubscription(BaseModel):
    topics: List[str]

class NotificationBulkOperation(BaseModel):
    notification_ids: List[str]

@router.post("")
async def create_notification(
    notification: NotificationCreate,
    session=Depends(get_current_session)
) -> Dict:
    """Create a new notification."""
    return await notification_manager.create_notification(
        type=notification.type,
        message=notification.message,
        priority=notification.priority,
        target_user=notification.target_user,
        metadata=notification.metadata
    )

@router.get("")
async def get_notifications(
    unread_only: bool = Query(default=False),
    notification_type: Optional[NotificationType] = None,
    limit: int = Query(default=50, ge=1, le=100),
    session=Depends(get_current_session)
) -> List[Dict]:
    """Get notifications for the current user."""
    return await notification_manager.get_notifications(
        user_id=session.get("user_id"),
        unread_only=unread_only,
        notification_type=notification_type,
        limit=limit
    )

@router.put("/read")
async def mark_notifications_read(
    operation: NotificationBulkOperation,
    session=Depends(get_current_session)
) -> Dict:
    """Mark multiple notifications as read."""
    return await notification_manager.mark_as_read(operation.notification_ids)

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    session=Depends(get_current_session)
) -> Dict:
    """Mark a single notification as read."""
    return await notification_manager.mark_as_read(notification_id)

@router.put("/read-all")
async def mark_all_notifications_read(
    session=Depends(get_current_session)
) -> Dict:
    """Mark all notifications as read for the current user."""
    return await notification_manager.mark_all_as_read(
        user_id=session.get("user_id")
    )

@router.delete("")
async def delete_notifications(
    operation: NotificationBulkOperation,
    session=Depends(get_current_session)
) -> Dict:
    """Delete multiple notifications."""
    return await notification_manager.delete_notifications(operation.notification_ids)

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    session=Depends(get_current_session)
) -> Dict:
    """Delete a single notification."""
    return await notification_manager.delete_notifications(notification_id)

@router.post("/subscribe")
async def subscribe_to_notifications(
    subscription: NotificationSubscription,
    session=Depends(get_current_session)
) -> Dict:
    """Subscribe to notification topics."""
    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    await notification_ws_manager.subscribe_to_topics(
        client_type="guest" if session.get("is_guest") else "admin",
        user_id=user_id,
        topics=subscription.topics
    )

    return {
        "status": "success",
        "subscribed_topics": subscription.topics
    }

@router.get("/subscriptions")
async def get_subscriptions(
    session=Depends(get_current_session)
) -> Dict:
    """Get current notification subscriptions."""
    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    subscriptions = notification_ws_manager.user_subscriptions.get(user_id, set())
    return {
        "subscribed_topics": list(subscriptions)
    }
