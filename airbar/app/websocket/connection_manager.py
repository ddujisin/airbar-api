from typing import Dict, Optional, List
from fastapi import WebSocket
from datetime import datetime
from collections import deque
from ..models.session import SessionMetrics
from ..config import get_settings
from ..utils.websocket_debug import websocket_debugger
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.message_queues: Dict[str, deque] = {}
        self.metrics: Dict[str, SessionMetrics] = {}
        self.settings = get_settings()
        self._background_tasks: List[asyncio.Task] = []

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.message_queues[client_id] = deque(maxlen=self.settings.WS_MESSAGE_QUEUE_SIZE)
        self.metrics[client_id] = SessionMetrics()
        websocket_debugger.log_connection(client_id, "connect")

        # Start heartbeat task
        task = asyncio.create_task(self._heartbeat(client_id))
        self._background_tasks.append(task)

    async def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].close()
            del self.active_connections[client_id]
            if client_id in self.metrics:
                self.metrics[client_id].record_connection_drop()
            websocket_debugger.log_connection(client_id, "disconnect")

        if client_id in self.message_queues:
            del self.message_queues[client_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id not in self.active_connections:
            return

        try:
            start_time = datetime.now()
            await self.active_connections[client_id].send_json(message)
            websocket_debugger.log_message(client_id, message, "outgoing")

            # Update metrics
            latency = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics[client_id].update_latency(latency)
            self.metrics[client_id].record_message_result(True)

        except Exception as e:
            websocket_debugger.log_error(client_id, str(e), {"message": message})
            self.metrics[client_id].record_message_result(False)
            if client_id in self.message_queues:
                self.message_queues[client_id].append(message)
            raise e

    async def broadcast(self, message: dict):
        for client_id in self.active_connections:
            try:
                await self.send_message(client_id, message)
            except Exception:
                continue

    async def _heartbeat(self, client_id: str):
        while client_id in self.active_connections:
            try:
                await self.send_message(client_id, {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                })
                if self.metrics.get(client_id):
                    websocket_debugger.log_metrics(client_id, self.metrics[client_id].dict())
                await asyncio.sleep(self.settings.WS_HEARTBEAT_INTERVAL)
            except Exception as e:
                websocket_debugger.log_error(client_id, f"Heartbeat failed: {str(e)}")
                await self.disconnect(client_id)
                break

    def get_metrics(self, client_id: str) -> Optional[SessionMetrics]:
        return self.metrics.get(client_id)

    async def process_message_queue(self, client_id: str):
        if client_id not in self.message_queues:
            return

        while self.message_queues[client_id]:
            message = self.message_queues[client_id].popleft()
            try:
                await self.send_message(client_id, message)
            except Exception:
                self.message_queues[client_id].appendleft(message)
                break

    async def cleanup(self):
        for task in self._background_tasks:
            task.cancel()

        for client_id in list(self.active_connections.keys()):
            await self.disconnect(client_id)

connection_manager = ConnectionManager()
