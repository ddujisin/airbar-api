from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import Request, HTTPException
from jose import JWTError, jwt
from app.config import settings
import json

class SessionManager:
    SECRET_KEY = settings.JWT_SECRET_KEY
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=SessionManager.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SessionManager.SECRET_KEY, algorithm=SessionManager.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, SessionManager.SECRET_KEY, algorithms=[SessionManager.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

async def verify_session(request: Request):
    """Verify session and update session data"""
    if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
        return

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]
    try:
        payload = SessionManager.decode_token(token)
        # Check if session has expired
        exp = datetime.fromtimestamp(payload.get("exp"))
        if datetime.utcnow() >= exp:
            remove_session(token)  # Clean up expired session
            raise HTTPException(
                status_code=401,
                detail="Session has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update or create session data
        session_data = get_session_data(token) or {}
        session_data.update({
            "last_activity": datetime.utcnow().isoformat(),
            "user_id": payload.get("sub"),
            "user_type": payload.get("type")
        })
        update_session(token, session_data)

        request.state.session = payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Session storage
_session_store: Dict[str, dict] = {}

def get_session_data(token: str) -> Optional[dict]:
    """Get session data for a token"""
    return _session_store.get(token)

def update_session(token: str, data: dict) -> None:
    """Update or create session data for a token"""
    _session_store[token] = data

def remove_session(token: str) -> None:
    """Remove session data for a token"""
    _session_store.pop(token, None)

def get_current_session(request: Request) -> dict:
    """Get current session data from request"""
    token = request.headers.get("Authorization", "").split(" ")[1]
    return _session_store.get(token, {})

# Cleanup expired sessions periodically
def cleanup_expired_sessions():
    """Remove expired sessions from storage"""
    current_time = datetime.utcnow()
    expired_tokens = []

    for token, data in _session_store.items():
        try:
            payload = SessionManager.decode_token(token)
            exp = datetime.fromtimestamp(payload.get("exp"))
            if current_time >= exp:
                expired_tokens.append(token)
        except JWTError:
            expired_tokens.append(token)

    for token in expired_tokens:
        remove_session(token)
