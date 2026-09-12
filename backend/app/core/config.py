"""Application configuration and settings"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Application
    APP_NAME: str = "TrustChain"
    APP_VERSION: str = "1.0.0"
    APP_ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://trustchain:trustchain@localhost:5432/trustchain"
    )
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_EXPIRY: int = 3600

    # JWT
    JWT_SECRET: str = Field(
        default="your-super-secret-jwt-key-change-in-production-minimum-32-characters"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 420
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Security
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 12
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    LOGIN_RATE_LIMIT_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_WINDOW: int = 900

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@trustchain-app.dev"
    SMTP_FROM_NAME: str = "TrustChain"

    # Blockchain
    POLYGON_RPC_URL: str = "https://rpc-mumbai.maticvigil.com"
    POLYGON_CHAIN_ID: int = 80001
    PRIVATE_KEY: str = ""
    SUPPLY_CHAIN_CONTRACT_ADDRESS: str = ""

    # AI/ML
    OPENAI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    YOLOV8_MODEL_PATH: str = "models/yolov8n.pt"
    WHISPER_MODEL_PATH: str = "models/ggml-base.bin"

    # Monitoring
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]

    # Mesh Network
    MESH_HEARTBEAT_INTERVAL: int = 30
    MESH_WEBSOCKET_TIMEOUT: int = 60
    MESH_MESSAGE_RETRY_ATTEMPTS: int = 3
    MESH_MESSAGE_RETRY_DELAY: int = 5

    # IPFS
    IPFS_API_URL: str = "http://localhost:5001"
    IPFS_GATEWAY_URL: str = "http://localhost:8080"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
