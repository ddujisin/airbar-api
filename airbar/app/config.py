from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Session Settings
    SESSION_COOKIE_NAME: str = "session_token"
    SESSION_EXPIRE_MINUTES: int = 30
    SESSION_REFRESH_THRESHOLD_MINUTES: int = 5
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "strict"

    # WebSocket Settings
    WS_PING_INTERVAL: int = 30  # seconds
    WS_PING_TIMEOUT: int = 10  # seconds
    WS_MAX_RECONNECT_ATTEMPTS: int = 5
    WS_RECONNECT_INTERVAL: int = 5  # seconds
    WS_MESSAGE_QUEUE_SIZE: int = 100
    GUEST_SESSION_TIMEOUT: int = 15  # minutes
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds

    # Host Settings
    ALLOWED_HOSTS: str = "*"

    # CORS Settings
    CORS_ORIGINS: str = "*"
    CORS_HEADERS: str = "*"

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AirBar API"

    # Debug Settings
    DEBUG_MODE: bool = False
    WS_DEBUG_LEVEL: str = "info"  # none, info, debug, verbose

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
