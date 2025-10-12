from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ProductSnap"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    # PayPal
    PAYPAL_CLIENT_ID: str
    PAYPAL_CLIENT_SECRET: str
    PAYPAL_MODE: str = "sandbox"  # or 'live'
    PAYPAL_WEBHOOK_ID: Optional[str] = None
    
    # PayPal Plan IDs - Basic and Pro with monthly/yearly options
    PAYPAL_PLAN_ID_BASIC_MONTHLY: Optional[str] = None
    PAYPAL_PLAN_ID_BASIC_YEARLY: Optional[str] = None
    PAYPAL_PLAN_ID_PRO_MONTHLY: Optional[str] = None
    PAYPAL_PLAN_ID_PRO_YEARLY: Optional[str] = None
    
    # Nano Banana (Gemini 2.5 Flash + Imagen 3)
    NANO_BANANA_API_KEY: str  # For Generative Language API or OAuth token for Vertex AI
    NANO_BANANA_API_URL: str = "https://generativelanguage.googleapis.com"
    GOOGLE_CLOUD_PROJECT_ID: str = "gen-lang-client-0509931710"
    IMAGE_GENERATION_MODE: str = "live"  # 'live' or 'mock'
    USE_VERTEX_AI: bool = False  # Set to True to use Vertex AI instead of Generative Language API
    
    # S3/Spaces
    S3_ENDPOINT: str
    S3_PUBLIC_ENDPOINT: Optional[str] = None  # Public-facing endpoint for signed URLs (e.g., http://localhost:9000)
    S3_REGION: str = "us-east-1"
    S3_BUCKET: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    
    # SMTP
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str = "noreply@productsnap.com"
    SMTP_TLS: bool = True
    
    # URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Rate Limits (per plan)
    FREE_JOBS_PER_DAY: int = 5
    FREE_CONCURRENT_JOBS: int = 1
    PERSONAL_JOBS_PER_MONTH: int = 100
    PERSONAL_CONCURRENT_JOBS: int = 3
    PRO_JOBS_PER_MONTH: int = 500
    PRO_CONCURRENT_JOBS: int = 5
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"]
    MIN_IMAGE_WIDTH: int = 512
    MIN_IMAGE_HEIGHT: int = 512
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
