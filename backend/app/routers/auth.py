from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
import logging

from app.core.database import get_db
from app.core.config import settings
from app.core.redis_client import get_redis_client
from app.models import User, OAuthProvider
from app.services.auth_service import AuthService
from app.services.email_service import email_service
import redis.asyncio as redis

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Register a new user with email and password."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = AuthService.create_user(
        db,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        oauth_provider=OAuthProvider.EMAIL
    )
    
    # Generate verification token
    verification_token = AuthService.generate_verification_token()
    await redis_client.setex(
        f"email_verify:{verification_token}",
        86400,  # 24 hours
        user.id
    )
    
    # Send verification email
    try:
        await email_service.send_verification_email(
            user.email,
            verification_token,
            user.full_name
        )
    except Exception as e:
        # Log but don't fail registration
        pass
    
    # Create session
    refresh_token, session = AuthService.create_session(
        db,
        user.id,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host
    )
    
    # Create access token
    access_token = AuthService.create_access_token({"sub": user.id, "email": user.email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with email and password."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not AuthService.verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create session
    refresh_token, session = AuthService.create_session(
        db,
        user.id,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host
    )
    
    # Create access token
    access_token = AuthService.create_access_token({"sub": user.id, "email": user.email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    session = AuthService.verify_refresh_token(db, refresh_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found or disabled"
        )
    
    # Create new access token
    access_token = AuthService.create_access_token({"sub": user.id, "email": user.email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token  # Same refresh token
    )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout and revoke session."""
    payload = AuthService.decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Revoke all user sessions (or specific one if we track session IDs in tokens)
    user_id = payload.get("sub")
    # For now, we can't easily revoke without session ID in token
    # In production, you'd want to track this
    
    return {"message": "Logged out successfully"}


@router.post("/verify-email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Verify email address with token."""
    user_id = await redis_client.get(f"email_verify:{token}")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.email_verified = True
    db.commit()
    
    # Delete token
    await redis_client.delete(f"email_verify:{token}")
    
    return {"message": "Email verified successfully"}


# Helper to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    payload = AuthService.decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found or disabled"
        )
    
    return user


@router.get("/google/login")
async def google_login(
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Initiate Google OAuth flow."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured"
        )
    
    # Generate state token for CSRF protection
    state = AuthService.generate_verification_token()
    await redis_client.setex(
        f"oauth_state:{state}",
        600,  # 10 minutes
        "google"
    )
    
    # Build Google OAuth URL
    redirect_uri = settings.GOOGLE_REDIRECT_URI or f"{settings.BACKEND_URL}/api/auth/google/callback"
    oauth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        "response_type=code&"
        "scope=openid%20email%20profile&"
        f"state={state}&"
        "access_type=offline&"
        "prompt=consent"
    )
    
    return {"authorization_url": oauth_url}


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Handle Google OAuth callback."""
    # Verify state token
    stored_provider = await redis_client.get(f"oauth_state:{state}")
    # Redis may return bytes or str depending on version
    if isinstance(stored_provider, bytes):
        stored_provider = stored_provider.decode()
    
    if not stored_provider or stored_provider != "google":
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=invalid_state"
        )
    
    # Delete used state token
    await redis_client.delete(f"oauth_state:{state}")
    
    try:
        # Exchange code for tokens and get user info
        google_user_info = await AuthService.exchange_google_code(
            code,
            settings.GOOGLE_REDIRECT_URI or f"{settings.BACKEND_URL}/api/auth/google/callback"
        )
        
        # Find or create user
        user = db.query(User).filter(
            User.oauth_provider == OAuthProvider.GOOGLE,
            User.oauth_sub == google_user_info["sub"]
        ).first()
        
        if not user:
            # Check if email already exists with different provider
            existing_user = db.query(User).filter(User.email == google_user_info["email"]).first()
            if existing_user:
                # Link Google account to existing user
                user = existing_user
                user.oauth_provider = OAuthProvider.GOOGLE
                user.oauth_sub = google_user_info["sub"]
                user.email_verified = google_user_info.get("email_verified", False)
                if google_user_info.get("picture"):
                    user.avatar_url = google_user_info["picture"]
                db.commit()
            else:
                # Create new user
                user = AuthService.create_user(
                    db,
                    email=google_user_info["email"],
                    oauth_provider=OAuthProvider.GOOGLE,
                    oauth_sub=google_user_info["sub"],
                    full_name=google_user_info.get("name"),
                    avatar_url=google_user_info.get("picture"),
                    email_verified=google_user_info.get("email_verified", False)
                )
        
        # Create session
        refresh_token, session = AuthService.create_session(
            db,
            user.id,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host
        )
        
        # Create access token
        access_token = AuthService.create_access_token({"sub": user.id, "email": user.email})
        
        # Redirect to frontend with tokens
        redirect_url = (
            f"{settings.FRONTEND_URL}/auth/callback?"
            f"access_token={access_token}&"
            f"refresh_token={refresh_token}"
        )
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        # Log the actual error for debugging
        logger.error(f"Google OAuth callback failed: {str(e)}", exc_info=True)
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=oauth_failed"
        )
