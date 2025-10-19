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
from app.services.rate_limit_service import RateLimitService
from app.services.analytics_service import analytics
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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


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
        # Don't increment rate limit for duplicate email (not abuse, just error)
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
    
    # Create access token with session ID
    access_token = AuthService.create_access_token(
        {"sub": user.id, "email": user.email},
        session_id=session.id
    )
    
    # Increment rate limit after successful registration
    await rate_limiter.increment_auth_attempts(client_ip, "register", window_seconds=900)
    
    # Track user registration
    analytics.identify(
        user_id=str(user.id),
        properties={
            "email": user.email,
            "name": user.full_name,
            "oauth_provider": "email",
        }
    )
    analytics.capture(
        user_id=str(user.id),
        event="user_registered",
        properties={"method": "email"}
    )
    analytics.flush()  # Ensure events are sent immediately
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Login with email and password."""
    # Check rate limit (5 attempts per 5 minutes per IP)
    rate_limiter = RateLimitService(redis_client)
    client_ip = request.client.host if request.client else "unknown"
    allowed, remaining = await rate_limiter.check_auth_rate_limit(client_ip, "login", max_attempts=5, window_seconds=300)
    
    if not allowed:
        logger.warning(f"Login rate limit exceeded for IP {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again in 5 minutes."
        )
    
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.password_hash:
        # Increment failed login attempts
        await rate_limiter.increment_auth_attempts(client_ip, "login", window_seconds=300)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not AuthService.verify_password(data.password, user.password_hash):
        # Increment failed login attempts
        await rate_limiter.increment_auth_attempts(client_ip, "login", window_seconds=300)
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
    
    # Create access token with session ID
    access_token = AuthService.create_access_token(
        {"sub": user.id, "email": user.email},
        session_id=session.id
    )
    
    # Reset rate limit on successful login
    await rate_limiter.reset_auth_attempts(client_ip, "login")
    
    # Track user login
    analytics.capture(
        user_id=str(user.id),
        event="user_logged_in",
        properties={"method": "email"}
    )
    analytics.flush()  # Ensure events are sent immediately
    
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
    
    # Create new access token with session ID
    access_token = AuthService.create_access_token(
        {"sub": user.id, "email": user.email},
        session_id=session.id
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token  # Same refresh token
    )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout and revoke current session."""
    payload = AuthService.decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get session ID from token
    session_id = payload.get("sid")
    user_id = payload.get("sub")
    
    if session_id:
        # Revoke the specific session
        revoked = AuthService.revoke_session(db, session_id)
        if revoked:
            logger.info(f"Session {session_id} revoked for user {user_id}")
        else:
            logger.warning(f"Session {session_id} not found for user {user_id}")
    else:
        # Fallback: session ID not in token (old tokens), revoke all user sessions
        logger.warning(f"No session ID in token, revoking all sessions for user {user_id}")
        count = AuthService.revoke_all_user_sessions(db, user_id)
        logger.info(f"Revoked {count} session(s) for user {user_id}")
    
    return {"message": "Logged out successfully"}


@router.post("/logout-all")
async def logout_all(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout from all devices by revoking all user sessions."""
    payload = AuthService.decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    
    # Revoke all sessions for this user
    count = AuthService.revoke_all_user_sessions(db, user_id)
    logger.info(f"Revoked all {count} session(s) for user {user_id}")
    
    return {"message": f"Logged out from all devices ({count} sessions revoked)"}


@router.get("/verify-email")
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
    
    # Decode user_id if it's bytes
    if isinstance(user_id, bytes):
        user_id = user_id.decode()
    
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


@router.post("/resend-verification")
async def resend_verification(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Resend email verification link."""
    # Get current user
    payload = AuthService.decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new verification token
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
        logger.error(f"Failed to send verification email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )
    
    return {"message": "Verification email sent"}


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Request password reset email."""
    # Check rate limit (3 attempts per 15 minutes per IP)
    rate_limiter = RateLimitService(redis_client)
    client_ip = request.client.host if request.client else "unknown"
    allowed, remaining = await rate_limiter.check_auth_rate_limit(client_ip, "forgot_password", max_attempts=3, window_seconds=900)
    
    if not allowed:
        logger.warning(f"Forgot password rate limit exceeded for IP {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset attempts. Please try again in 15 minutes."
        )
    
    # Find user by email
    user = db.query(User).filter(User.email == data.email).first()
    
    # Increment rate limit counter (always, even if user doesn't exist)
    await rate_limiter.increment_auth_attempts(client_ip, "forgot_password", window_seconds=900)
    
    # Always return success even if user doesn't exist (security best practice)
    # This prevents email enumeration attacks
    if not user:
        return {"message": "If that email exists, a password reset link has been sent"}
    
    # Only allow password reset for email/password users
    if user.oauth_provider != OAuthProvider.EMAIL:
        return {"message": "If that email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = AuthService.generate_verification_token()
    await redis_client.setex(
        f"password_reset:{reset_token}",
        3600,  # 1 hour
        user.id
    )
    
    # Send reset email
    try:
        await email_service.send_password_reset_email(
            user.email,
            reset_token,
            user.full_name
        )
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        # Don't expose error to user
    
    return {"message": "If that email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Reset password with token."""
    # Verify token
    user_id = await redis_client.get(f"password_reset:{data.token}")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Decode user_id if it's bytes
    if isinstance(user_id, bytes):
        user_id = user_id.decode()
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = AuthService.hash_password(data.new_password)
    db.commit()
    
    # Delete token
    await redis_client.delete(f"password_reset:{data.token}")
    
    logger.info(f"Password reset successful for user {user.email}")
    
    return {"message": "Password reset successfully"}


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
                # Track new user registration
                analytics.identify(
                    user_id=str(user.id),
                    properties={
                        "email": user.email,
                        "name": user.full_name,
                        "oauth_provider": "google",
                    }
                )
                analytics.capture(
                    user_id=str(user.id),
                    event="user_registered",
                    properties={"method": "google"}
                )
                analytics.flush()
        
        # Create session
        refresh_token, session = AuthService.create_session(
            db,
            user.id,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host
        )
        
        # Create access token with session ID
        access_token = AuthService.create_access_token(
            {"sub": user.id, "email": user.email},
            session_id=session.id
        )
        
        # Track user login (for existing users)
        analytics.capture(
            user_id=str(user.id),
            event="user_logged_in",
            properties={"method": "google"}
        )
        analytics.flush()
        
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
