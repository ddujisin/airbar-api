from datetime import datetime, timedelta
import jwt
from typing import Dict, Optional
from ..config import settings

class SessionManager:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.session_timeout = timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
        self.refresh_threshold = timedelta(minutes=settings.SESSION_REFRESH_THRESHOLD_MINUTES)

    def create_token(self, data: Dict) -> str:
        """Create a new session token with expiration"""
        expiration = datetime.utcnow() + self.session_timeout
        token_data = {
            **data,
            "exp": expiration.timestamp(),
            "iat": datetime.utcnow().timestamp()
        }
        return jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode a session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def is_token_expiring_soon(self, token: str, threshold_minutes: int = None) -> bool:
        """Check if token is expiring within the threshold"""
        threshold = timedelta(minutes=threshold_minutes or settings.SESSION_REFRESH_THRESHOLD_MINUTES)
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                return True

            expiration = datetime.fromtimestamp(exp_timestamp)
            threshold_time = datetime.utcnow() + threshold
            return expiration <= threshold_time
        except:
            return True

    def refresh_token(self, token: str) -> Optional[str]:
        """Create a new token with refreshed expiration time"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            # Remove existing expiration
            if "exp" in payload:
                del payload["exp"]
            # Create new token with fresh expiration
            return self.create_token(payload)
        except:
            return None

session_manager = SessionManager()
