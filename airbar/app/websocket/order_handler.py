from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
from ..utils.websocket_manager import ConnectionManager

class OrderNotificationManager(ConnectionManager):
    def __init__(self):
        super().__init__()
        self.reservation_connections: Dict[str, Set[WebSocket]] = {}

    async def connect_reservation(self, websocket: WebSocket, reservation_id: str):
        await self.connect(websocket)
        if reservation_id not in self.reservation_connections:
            self.reservation_connections[reservation_id] = set()
        self.reservation_connections[reservation_id].add(websocket)

    async def disconnect_reservation(self, websocket: WebSocket, reservation_id: str):
        await self.disconnect(websocket)
        if reservation_id in self.reservation_connections:
            self.reservation_connections[reservation_id].discard(websocket)
            if not self.reservation_connections[reservation_id]:
                del self.reservation_connections[reservation_id]

    async def notify_reservation(self, reservation_id: str, message: dict):
        if reservation_id in self.reservation_connections:
            for connection in self.reservation_connections[reservation_id]:
                await self.send_json(connection, message)

    async def notify_order_update(self, order_id: str, reservation_id: str, status: str):
        message = {
            "type": "order_update",
            "order_id": order_id,
            "status": status
        }
        await self.notify_reservation(reservation_id, message)

    async def notify_payment_update(self, payment_id: str, reservation_id: str, status: str):
        message = {
            "type": "payment_update",
            "payment_id": payment_id,
            "status": status
        }
        await self.notify_reservation(reservation_id, message)

order_manager = OrderNotificationManager()
