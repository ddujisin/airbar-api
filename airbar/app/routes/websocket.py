from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from ..websocket.guest_handler import guest_handler
from ..websocket.connection_manager import connection_manager
from ..middleware.auth import get_current_user
from ..middleware.session import validate_guest_session
from ..utils.session import create_session_id
from ..websocket.notification_handler import notification_ws_manager
import json
from fastapi.responses import JSONResponse
from ..websocket.order_handler import order_manager

router = APIRouter()

@router.websocket("/ws/guest")
async def guest_websocket(websocket: WebSocket):
    session_id = create_session_id()

    try:
        await guest_handler.connect(websocket, session_id)

        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get('type')
                message_data = data.get('data', {})

                if message_type == 'ping':
                    await connection_manager.send_message(session_id, {
                        'type': 'pong',
                        'data': {
                            'timestamp': message_data.get('timestamp')
                        }
                    })
                    continue

                if message_type == 'guest_session_start':
                    await guest_handler.handle_session_start(
                        session_id=session_id,
                        reservation_id=message_data.get('reservationId')
                    )

                elif message_type == 'qr_scan':
                    await guest_handler.handle_qr_scan(
                        session_id=session_id,
                        item_id=message_data.get('itemId')
                    )

            except json.JSONDecodeError:
                await guest_handler.send_error(session_id, "Invalid message format")
                continue

    except WebSocketDisconnect:
        await guest_handler.disconnect(session_id)

    except Exception as e:
        await guest_handler.send_error(session_id, str(e))
        await guest_handler.disconnect(session_id)

@router.websocket("/ws/orders/{reservation_id}")
async def order_websocket(websocket: WebSocket, reservation_id: str):
    try:
        await order_manager.connect_reservation(websocket, reservation_id)

        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get('type')

                if message_type == 'ping':
                    await websocket.send_json({
                        'type': 'pong',
                        'timestamp': data.get('timestamp')
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid message format"
                })

    except WebSocketDisconnect:
        await order_manager.disconnect_reservation(websocket, reservation_id)
    except Exception as e:
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1011, reason=str(e))

@router.websocket("/ws/notifications/{client_type}")
async def notification_websocket(
    websocket: WebSocket,
    client_type: str,
    user_id: str = None
):
    """WebSocket endpoint for real-time notifications."""
    if client_type not in ["admin", "guest"]:
        await websocket.close(code=4000, reason="Invalid client type")
        return

    try:
        await notification_ws_manager.connect(websocket, client_type, user_id)

        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get('type')

                if message_type == 'ping':
                    await websocket.send_json({
                        'type': 'pong',
                        'timestamp': data.get('timestamp')
                    })
                elif message_type == 'mark_read':
                    notification_id = data.get('notification_id')
                    if notification_id:
                        await notification_ws_manager.mark_notification_read(
                            client_type,
                            user_id,
                            notification_id
                        )
                elif message_type == 'subscribe':
                    topics = data.get('topics', [])
                    await notification_ws_manager.subscribe_to_topics(
                        client_type,
                        user_id,
                        topics
                    )

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid message format"
                })

    except WebSocketDisconnect:
        notification_ws_manager.disconnect(websocket, client_type, user_id)
    except Exception as e:
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1011, reason=str(e))

@router.on_event("startup")
async def startup_event():
    # Start the cleanup task
    from fastapi_utils.tasks import repeat_every

    @repeat_every(seconds=60)  # Run every minute
    async def cleanup_tasks():
        guest_handler.cleanup_expired_sessions()
        # Process any queued messages for all active connections
        for session_id in connection_manager.active_connections.keys():
            await connection_manager.process_message_queue(session_id)

@router.on_event("shutdown")
async def shutdown_event():
    await connection_manager.cleanup()
