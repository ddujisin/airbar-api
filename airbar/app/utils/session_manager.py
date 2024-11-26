from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException
from prisma import Prisma
import jwt
from ..config import settings

class SessionManager:
    def __init__(self):
        self.db = Prisma()
        self.SESSION_DURATION = timedelta(hours=24)

    async def create_guest_session(self, reservation_id: str, pin: str) -> Dict:
        """Create a new guest session after validating PIN."""
        try:
            # Verify reservation and PIN
            reservation = await self.db.reservation.find_first(
                where={
                    "id": reservation_id,
                    "pin": pin,
                    "status": {"not": "CHECKED_OUT"}
                }
            )

            if not reservation:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid reservation ID or PIN"
                )

            # Create session token
            session_data = {
                "reservation_id": reservation_id,
                "exp": datetime.utcnow() + self.SESSION_DURATION
            }

            session_token = jwt.encode(
                session_data,
                settings.JWT_SECRET,
                algorithm="HS256"
            )

            # Create or update session record
            session = await self.db.guestSession.upsert(
                where={
                    "reservationId": reservation_id
                },
                create={
                    "reservationId": reservation_id,
                    "token": session_token,
                    "expiresAt": session_data["exp"]
                },
                update={
                    "token": session_token,
                    "expiresAt": session_data["exp"]
                }
            )

            return {
                "session_id": session.id,
                "token": session_token,
                "expires_at": session.expiresAt
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating session: {str(e)}"
            )

    async def validate_session(self, token: str) -> Optional[Dict]:
        """Validate a session token and return session data."""
        try:
            # Decode token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"]
            )

            # Check if session exists and is valid
            session = await self.db.guestSession.find_first(
                where={
                    "token": token,
                    "expiresAt": {"gt": datetime.utcnow()}
                },
                include={
                    "reservation": True
                }
            )

            if not session:
                return None

            return {
                "session_id": session.id,
                "reservation_id": session.reservation.id,
                "guest_name": session.reservation.guestName,
                "room_number": session.reservation.roomNumber
            }

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error validating session: {str(e)}"
            )

    async def end_session(self, token: str) -> bool:
        """End a guest session."""
        try:
            # Delete session
            await self.db.guestSession.delete_many(
                where={
                    "token": token
                }
            )
            return True
        except Exception:
            return False

    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            await self.db.guestSession.delete_many(
                where={
                    "expiresAt": {"lt": datetime.utcnow()}
                }
            )
        except Exception as e:
            print(f"Error cleaning up sessions: {str(e)}")

session_manager = SessionManager()
