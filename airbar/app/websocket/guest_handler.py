from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import WebSocket
from prisma import Prisma
from ..utils.session import create_session_token
from ..models.session import GuestSession
from ..config import get_settings
from .connection_manager import connection_manager
from ..utils.websocket_debug import websocket_debugger

class GuestWebSocketHandler:
    def __init__(self):
        self.guest_sessions: Dict[str, GuestSession] = {}
        self.settings = get_settings()
        self.db = Prisma()

    async def connect(self, websocket: WebSocket, session_id: str):
        await connection_manager.connect(websocket, session_id)
        websocket_debugger.log_connection(session_id, "guest_connect")

    async def disconnect(self, session_id: str):
        await connection_manager.disconnect(session_id)
        if session_id in self.guest_sessions:
            websocket_debugger.log_session_cleanup(session_id, "guest_disconnect")
            del self.guest_sessions[session_id]

    async def handle_session_start(self, session_id: str, reservation_id: str):
        try:
            await self.db.connect()
            reservation = await self.db.reservation.find_unique(
                where={'id': reservation_id}
            )

            if not reservation:
                await self.send_error(session_id, "Invalid reservation")
                return

            current_date = datetime.now().date()
            if not (reservation.start_date <= current_date <= reservation.end_date):
                await self.send_error(session_id, "Reservation not active for current date")
                return

            websocket_debugger.log_message(session_id, {
                "type": "session_start_attempt",
                "reservation_id": reservation_id
            }, "incoming")

            session_token = create_session_token()
            self.guest_sessions[session_id] = GuestSession(
                session_id=session_id,
                reservation_id=reservation_id,
                token=session_token,
                created_at=datetime.now(),
                last_active=datetime.now()
            )

            websocket_debugger.log_message(session_id, {
                "type": "session_started",
                "session_id": session_id,
                "reservation_id": reservation_id
            }, "outgoing")

            await connection_manager.send_message(session_id, {
                "type": "session_started",
                "data": {
                    "token": session_token,
                    "expires_in": self.settings.GUEST_SESSION_TIMEOUT
                }
            })

        except Exception as e:
            websocket_debugger.log_error(session_id, str(e))
            await self.send_error(session_id, str(e))
        finally:
            await self.db.disconnect()

    async def handle_qr_scan(self, session_id: str, item_id: str):
        session = self.guest_sessions.get(session_id)
        if not session:
            websocket_debugger.log_error(session_id, "Invalid session for QR scan")
            await self.send_error(session_id, "Invalid session")
            return

        try:
            await self.db.connect()
            item = await self.db.item.find_unique(
                where={'id': item_id}
            )

            if not item:
                await self.send_error(session_id, "Invalid item")
                return

            session.last_active = datetime.now()
            await connection_manager.send_message(session_id, {
                "type": "item_scanned",
                "data": {
                    "item": {
                        "id": item.id,
                        "name": item.name,
                        "price": float(item.price),
                        "description": item.description
                    }
                }
            })
            websocket_debugger.log_message(session_id, {
                "type": "qr_scan_success",
                "item_id": item_id
            }, "outgoing")

        except Exception as e:
            websocket_debugger.log_error(session_id, str(e))
            await self.send_error(session_id, str(e))
        finally:
            await self.db.disconnect()

    async def send_message(self, session_id: str, message: dict):
        await connection_manager.send_message(session_id, message)

    async def send_error(self, session_id: str, error: str):
        await self.send_message(session_id, {
            "type": "error",
            "data": {"message": error}
        })

    def cleanup_expired_sessions(self):
        now = datetime.now()
        timeout = timedelta(minutes=self.settings.guest_session_timeout)
        expired_sessions = [
            session_id for session_id, session in self.guest_sessions.items()
            if (now - session.last_active) > timeout
        ]

        for session_id in expired_sessions:
            del self.guest_sessions[session_id]

guest_handler = GuestWebSocketHandler()
