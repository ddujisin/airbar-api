from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routes import (
    admin, guest, auth, dashboard, guest_session, orders,
    payments, admin_qr, reservations, guest_profile, analytics,
    inventory, notifications, notification_preferences
)
from .middleware.session_middleware import session_middleware, get_current_session
from .config import settings
from .routes import websocket
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .routes import metrics

load_dotenv()
app = FastAPI(title=settings.PROJECT_NAME)

# Configure trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS.split(",")
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add session verification middleware
app.middleware("http")(session_middleware)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(
    admin.router,
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[get_current_session]
)
app.include_router(
    guest.router,
    prefix="/api/guest",
    tags=["guest"],
    dependencies=[get_current_session]
)
app.include_router(
    dashboard.router,
    prefix="/api/admin/dashboard",
    tags=["dashboard"],
    dependencies=[get_current_session]
)
app.include_router(guest_session.router, prefix="/api/session", tags=["session"])

# Metrics routes
app.include_router(
    metrics.router,
    prefix="/api/metrics",
    tags=["metrics"]
)

# WebSocket routes
app.include_router(websocket.router, tags=["websocket"])

# Order and Payment routes
app.include_router(
    orders.router,
    prefix="/api/orders",
    tags=["orders"],
    dependencies=[get_current_session]
)
app.include_router(
    payments.router,
    prefix="/api/payments",
    tags=["payments"],
    dependencies=[get_current_session]
)

# Guest profile routes
app.include_router(
    guest_profile.router,
    prefix="/api/guest/profile",
    tags=["guest-profile"],
    dependencies=[get_current_session]
)

# Admin QR routes
app.include_router(
    admin_qr.router,
    prefix="/api/admin/qr",
    tags=["admin-qr"],
    dependencies=[get_current_session]
)

# Reservation routes
app.include_router(
    reservations.router,
    prefix="/api/reservations",
    tags=["reservations"],
    dependencies=[get_current_session]
)

# Analytics routes
app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["analytics"],
    dependencies=[get_current_session]
)

# Inventory routes
app.include_router(
    inventory.router,
    prefix="/api/inventory",
    tags=["inventory"],
    dependencies=[get_current_session]
)

# Notification routes
app.include_router(
    notifications.router,
    prefix="/api/notifications",
    tags=["notifications"],
    dependencies=[get_current_session]
)

# Notification preferences routes
app.include_router(
    notification_preferences.router,
    prefix="/api/notifications/preferences",
    tags=["notification-preferences"],
    dependencies=[get_current_session]
)

# Configure WebSocket settings in CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
