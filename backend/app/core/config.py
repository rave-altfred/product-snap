from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from pathlib import Path


def read_secret_file(file_path: str) -> Optional[str]:
    """Read a secret from a file (Docker Secrets convention)."""
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            return path.read_text().strip()
    except Exception as e:
        print(f"Warning: Failed to read secret file {file_path}: {e}")
    return None


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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override secrets from files if *_FILE env vars are set (Docker Secrets)
        self._load_secrets_from_files()


    def _load_secrets_from_files(self):
        """Load secrets from files if *_FILE environment variables are set.
        
        This follows Docker Secrets convention where sensitive values can be
        provided via files (typically mounted at /run/secrets/).
        
        For each secret field, if <FIELD_NAME>_FILE env var exists,
        read the secret from that file path.
        """
        secret_fields = [
            'DATABASE_URL',
            'JWT_SECRET',
            'GOOGLE_CLIENT_SECRET',
            'PAYPAL_CLIENT_SECRET',
            'NANO_BANANA_API_KEY',
            'S3_ACCESS_KEY',
            'S3_SECRET_KEY',
            'SMTP_PASSWORD',
        ]
        
        for field in secret_fields:
            file_env_var = f"{field}_FILE"
            file_path = os.getenv(file_env_var)
            
            if file_path:
                secret_value = read_secret_file(file_path)
                if secret_value:
                    setattr(self, field, secret_value)
                    print(f"✓ Loaded {field} from secret file")
                else:
                    print(f"⚠ Warning: {file_env_var} is set but file is empty or unreadable")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
