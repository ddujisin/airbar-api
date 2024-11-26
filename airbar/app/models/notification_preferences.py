from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

class NotificationChannel(str, Enum):
    WEBSOCKET = "websocket"
    EMAIL = "email"
    MOBILE = "mobile"
    SMS = "sms"
    PUSH = "push"

class NotificationType(str, Enum):
    NEW_ORDER = "NEW_ORDER"
    LOW_STOCK = "LOW_STOCK"
    PAYMENT = "PAYMENT"
    SYSTEM = "SYSTEM"
    ALERT = "ALERT"

class QuietHours(BaseModel):
    start: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    end: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")

class NotificationPreferences(BaseModel):
    user_id: str
    channels: Dict[str, List[str]]  # notification_type -> channels
    quiet_hours: Optional[Dict[str, Dict[str, str]]] = None  # day -> {start: "HH:MM", end: "HH:MM"}
    enabled: bool = True
    muted_until: Optional[datetime] = None
    priority_threshold: int = Field(default=0, ge=0, le=10)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "user123",
                "channels": {
                    "NEW_ORDER": ["websocket", "email"],
                    "LOW_STOCK": ["websocket", "mobile"],
                    "PAYMENT": ["websocket", "sms"]
                },
                "quiet_hours": {
                    "monday": {"start": "22:00", "end": "08:00"},
                    "sunday": {"start": "22:00", "end": "09:00"}
                },
                "enabled": True,
                "muted_until": None,
                "priority_threshold": 5
            }
        }
    )
