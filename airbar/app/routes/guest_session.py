from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from prisma import Prisma
from datetime import datetime
from pydantic import BaseModel
from ..middleware.auth import get_prisma
from ..utils.session_manager import session_manager
from ..config import settings

router = APIRouter()

class SessionCreate(BaseModel):
    reservation_id: str
    pin: str

@router.post("/start")
async def start_guest_session(session_data: SessionCreate):
    try:
        session = await session_manager.create_guest_session(
            session_data.reservation_id,
            session_data.pin
        )
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/validate")
async def validate_session(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = auth_header.split(' ')[1]
    session_data = await session_manager.validate_session(token)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    return session_data

@router.post("/end")
async def end_guest_session(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = auth_header.split(' ')[1]
    success = await session_manager.end_session(token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to end session"
        )

    return {"message": "Session ended successfully"}

async def get_current_guest_session(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = auth_header.split(' ')[1]
    session_data = await session_manager.validate_session(token)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    return session_data
