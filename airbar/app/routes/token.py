from fastapi import APIRouter, Depends, HTTPException
from ..middleware.auth import verify_token, create_token
from ..middleware.session import get_session_data, update_session
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/verify")
async def verify_session_token(token: str):
    """
    Verify a session token and return new token if close to expiration
    """
    try:
        # Verify the existing token
        payload = verify_token(token)

        # Get session data
        session_data = get_session_data(token)
        if not session_data:
            raise HTTPException(status_code=401, message="Invalid session")

        # Check if token needs refresh (less than 5 minutes remaining)
        exp_timestamp = payload.get('exp', 0)
        exp_time = datetime.fromtimestamp(exp_timestamp)
        time_remaining = exp_time - datetime.utcnow()

        if time_remaining < timedelta(minutes=5):
            # Create new token with extended expiration
            new_token = create_token(payload['sub'], payload.get('type'))
            # Update session with new token
            update_session(new_token, session_data)
            return {"valid": True, "new_token": new_token}

        return {"valid": True}

    except Exception as e:
        return {"valid": False, "error": str(e)}

@router.post("/refresh")
async def refresh_token(token: str):
    """
    Force refresh a valid token
    """
    try:
        payload = verify_token(token)
        session_data = get_session_data(token)

        if not session_data:
            raise HTTPException(status_code=401, message="Invalid session")

        new_token = create_token(payload['sub'], payload.get('type'))
        update_session(new_token, session_data)

        return {"token": new_token}

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
