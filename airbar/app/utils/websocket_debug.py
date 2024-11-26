from typing import Optional, Dict, Any
from datetime import datetime
import logging
import json
from ..config import get_settings

settings = get_settings()

class WebSocketDebugger:
    def __init__(self):
        self.logger = logging.getLogger("websocket_debug")
        self._setup_logger()
        self.debug_level = settings.WS_DEBUG_LEVEL

    def _setup_logger(self):
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG if settings.DEBUG_MODE else logging.INFO)

    def log_connection(self, session_id: str, event_type: str):
        if self.debug_level == "none":
            return

        self.logger.info(f"WebSocket {event_type} - Session: {session_id}")

    def log_message(self, session_id: str, message: Dict[str, Any], direction: str):
        if self.debug_level == "none":
            return

        if self.debug_level == "verbose":
            self.logger.debug(
                f"WebSocket {direction} - Session: {session_id} - "
                f"Message: {json.dumps(message, indent=2)}"
            )
        else:
            self.logger.info(
                f"WebSocket {direction} - Session: {session_id} - "
                f"Type: {message.get('type')}"
            )

    def log_error(self, session_id: str, error: str, details: Optional[Dict] = None):
        self.logger.error(
            f"WebSocket Error - Session: {session_id} - Error: {error}"
            + (f" - Details: {json.dumps(details)}" if details else "")
        )

    def log_metrics(self, session_id: str, metrics: Dict[str, Any]):
        if self.debug_level in ["debug", "verbose"]:
            self.logger.debug(
                f"WebSocket Metrics - Session: {session_id} - "
                f"Metrics: {json.dumps(metrics, indent=2)}"
            )

    def log_queue_status(self, session_id: str, queue_size: int):
        if self.debug_level in ["debug", "verbose"]:
            self.logger.debug(
                f"Message Queue Status - Session: {session_id} - "
                f"Queue Size: {queue_size}"
            )

    def log_session_cleanup(self, session_id: str, reason: str):
        if self.debug_level != "none":
            self.logger.info(
                f"Session Cleanup - Session: {session_id} - Reason: {reason}"
            )

websocket_debugger = WebSocketDebugger()
