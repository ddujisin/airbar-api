"""Main FastAPI application module."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma
from .routes import notification_preferences
from .websocket.notification_handler import notification_manager

app = FastAPI(title="AirBar API", version="0.1.0")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(notification_preferences.router)

@app.on_event("startup")
async def startup():
    """Initialize database connection on startup."""
    await Prisma().connect()

@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown."""
    await Prisma().disconnect()

@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications."""
    try:
        await notification_manager.connect(websocket, user_id)
        while True:
            try:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_json()
                # Echo received messages for testing
                await notification_manager.send_notification(user_id, {
                    "type": "echo",
                    "data": data
                })
            except WebSocketDisconnect:
                break
    finally:
        notification_manager.disconnect(websocket, user_id)

@app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {"status": "ok"}
