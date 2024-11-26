from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from ..utils.session_manager import session_manager
from ..config import settings
from typing import Optional
from datetime import datetime

async def session_middleware(request: Request, call_next):
    """Middleware to handle session validation and token refresh"""

    # Paths that don't require session validation
    public_paths = [
        "/api/session/start",
        "/api/auth/login",
        "/api/health",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]

    if request.url.path in public_paths:
        return await call_next(request)

    # Get session token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authorization header"}
            )
        return await call_next(request)

    token = auth_header.split(' ')[1]

    # Validate session
    try:
        session_data = await session_manager.validate_session(token)
        if not session_data:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired session"}
            )

        # Add session info to request state
        request.state.session = session_data
        return await call_next(request)

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(e)}
        )

async def get_current_session(request: Request) -> Optional[dict]:
    """Dependency to get current session data"""
    session = getattr(request.state, "session", None)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid session required"
        )
    return session
