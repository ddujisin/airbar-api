# AirBar Notification System

A WebSocket-based notification system with advanced preference management for the AirBar application.

## Features

- Real-time notifications via WebSocket
- Configurable notification preferences per user
- Support for multiple notification channels
- Quiet hours and temporary muting
- Priority-based notification filtering
- Comprehensive test coverage

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Run database migrations:
```bash
prisma db push
```

3. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Notification Preferences

- `GET /notification-preferences/{user_id}` - Get user preferences
- `PUT /notification-preferences/{user_id}` - Update preferences
- `POST /notification-preferences/{user_id}/mute` - Temporarily mute notifications

### WebSocket

- `ws://localhost:8000/ws/notifications/{user_id}` - WebSocket connection for real-time notifications

## Testing

Run the test suite:
```bash
pytest
```

## Configuration

Notification preferences support:
- Multiple notification channels (email, websocket)
- Quiet hours (start/end time)
- Priority thresholds (0-10)
- Temporary muting with auto-expiration

## Development

The project uses:
- FastAPI for the web framework
- Prisma for database operations
- pytest for testing
- WebSockets for real-time communication

## License

MIT License
