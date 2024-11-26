from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class GuestSession(BaseModel):
    session_id: str
    reservation_id: str
    token: str
    created_at: datetime
    last_active: datetime
    pin_code: Optional[str] = None
    guest_id: Optional[str] = None

    def is_active(self, timeout_minutes: int = 15) -> bool:
        """Check if the session is still active based on timeout."""
        elapsed = (datetime.now() - self.last_active).total_seconds() / 60
        return elapsed <= timeout_minutes

    def update_activity(self) -> None:
        """Update the last active timestamp."""
        self.last_active = datetime.now()

    def to_dict(self) -> dict:
        """Convert session to dictionary for WebSocket transmission."""
        return {
            "session_id": self.session_id,
            "reservation_id": self.reservation_id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "guest_id": self.guest_id
        }

class SessionMetrics(BaseModel):
    """Model for tracking WebSocket session metrics."""
    total_messages: int = 0
    successful_messages: int = 0
    failed_messages: int = 0
    average_latency: float = 0.0
    last_ping_time: Optional[datetime] = None
    connection_drops: int = 0

    def update_latency(self, latency_ms: float) -> None:
        """Update average latency with new measurement."""
        if self.total_messages == 0:
            self.average_latency = latency_ms
        else:
            self.average_latency = (
                (self.average_latency * self.total_messages + latency_ms) /
                (self.total_messages + 1)
            )
        self.total_messages += 1

    def record_message_result(self, success: bool) -> None:
        """Record the result of a message transmission."""
        if success:
            self.successful_messages += 1
        else:
            self.failed_messages += 1

    def record_connection_drop(self) -> None:
        """Record a connection drop event."""
        self.connection_drops += 1

    def get_success_rate(self) -> float:
        """Calculate the message success rate."""
        total = self.successful_messages + self.failed_messages
        return (self.successful_messages / total * 100) if total > 0 else 0.0
