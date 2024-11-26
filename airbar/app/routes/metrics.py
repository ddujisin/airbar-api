from fastapi import APIRouter, Depends
from ..websocket.connection_manager import connection_manager
from ..websocket.guest_handler import guest_handler
from ..middleware.auth import get_current_admin
from datetime import datetime

router = APIRouter()

@router.get("/ws/metrics", dependencies=[Depends(get_current_admin)])
async def get_websocket_metrics():
    """Get WebSocket connection and session metrics for monitoring."""
    metrics = {}

    # Aggregate connection metrics
    total_connections = len(connection_manager.active_connections)
    total_sessions = len(guest_handler.guest_sessions)

    # Calculate overall success rate and latency
    success_rates = []
    latencies = []

    for client_id, session_metrics in connection_manager.metrics.items():
        success_rates.append(session_metrics.get_success_rate())
        latencies.append(session_metrics.average_latency)

    avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    # Get message queue statistics
    queue_sizes = [len(queue) for queue in connection_manager.message_queues.values()]
    total_queued = sum(queue_sizes)
    max_queue_size = max(queue_sizes) if queue_sizes else 0

    metrics.update({
        "timestamp": datetime.now().isoformat(),
        "connections": {
            "active": total_connections,
            "sessions": total_sessions,
        },
        "performance": {
            "success_rate": round(avg_success_rate, 2),
            "average_latency_ms": round(avg_latency, 2),
            "message_queue": {
                "total": total_queued,
                "max_size": max_queue_size
            }
        },
        "sessions": {
            "active": [
                {
                    "session_id": session_id,
                    "created_at": session.created_at.isoformat(),
                    "last_active": session.last_active.isoformat(),
                    "metrics": connection_manager.get_metrics(session_id).dict() if connection_manager.get_metrics(session_id) else None
                }
                for session_id, session in guest_handler.guest_sessions.items()
            ]
        }
    })

    return metrics

