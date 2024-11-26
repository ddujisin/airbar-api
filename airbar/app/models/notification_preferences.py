"""Notification preferences model for the AirBar application."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class NotificationPreference(BaseModel):
    """User notification preferences."""
    user_id: str = Field(..., description="User ID")
    enabled_channels: List[str] = Field(default=["email", "websocket"], description="Enabled notification channels")
    quiet_hours_start: Optional[int] = Field(None, description="Start hour for quiet period (0-23)")
    quiet_hours_end: Optional[int] = Field(None, description="End hour for quiet period (0-23)")
    muted_until: Optional[datetime] = Field(None, description="Timestamp until notifications are muted")
    priority_threshold: int = Field(default=0, ge=0, le=10, description="Minimum priority level for notifications (0-10)")

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "enabled_channels": ["email", "websocket"],
                "quiet_hours_start": 22,
                "quiet_hours_end": 7,
                "muted_until": None,
                "priority_threshold": 3
            }
        }
