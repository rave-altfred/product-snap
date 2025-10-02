from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import uuid
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User, Session as UserSession, Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.user import OAuthProvider


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using argon2."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token() -> str:
        """Create a random refresh token."""
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token for storage."""
        return pwd_context.hash(token)
    
    @staticmethod
    def verify_token(plain_token: str, hashed_token: str) -> bool:
        """Verify a token against its hash."""
        return pwd_context.verify(plain_token, hashed_token)
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decode and verify a JWT access token."""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            if payload.get("type") != "access":
                return None
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: Optional[str] = None,
        oauth_provider: Optional[OAuthProvider] = None,
        oauth_sub: Optional[str] = None,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        email_verified: bool = False
    ) -> User:
        """Create a new user."""
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=AuthService.hash_password(password) if password else None,
            oauth_provider=oauth_provider,
            oauth_sub=oauth_sub,
            full_name=full_name,
            avatar_url=avatar_url,
            email_verified=email_verified
        )
        db.add(user)
        
        # Create default free subscription
        subscription = Subscription(
            id=str(uuid.uuid4()),
            user_id=user.id,
            plan=SubscriptionPlan.FREE,
            status=SubscriptionStatus.ACTIVE
        )
        db.add(subscription)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def create_session(
        db: Session,
        user_id: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> tuple[str, UserSession]:
        """Create a new user session."""
        refresh_token = AuthService.create_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        session = UserSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            refresh_token_hash=AuthService.hash_token(refresh_token),
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return refresh_token, session
    
    @staticmethod
    def verify_refresh_token(db: Session, token: str) -> Optional[UserSession]:
        """Verify a refresh token and return the session."""
        # Note: In production, you'd want to index sessions by a hash or use Redis
        sessions = db.query(UserSession).filter(UserSession.expires_at > datetime.utcnow()).all()
        for session in sessions:
            if AuthService.verify_token(token, session.refresh_token_hash):
                return session
        return None
    
    @staticmethod
    def revoke_session(db: Session, session_id: str):
        """Revoke a user session."""
        db.query(UserSession).filter(UserSession.id == session_id).delete()
        db.commit()
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate an email verification token."""
        return secrets.token_urlsafe(32)
