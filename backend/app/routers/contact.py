from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["contact"])
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current authenticated user, return None if not authenticated."""
    if not credentials:
        return None
    
    try:
        payload = AuthService.decode_access_token(credentials.credentials)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return None
        
        return user
    except:
        return None


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    category: str = "General"


@router.post("/support")
async def send_support_message(
    request: ContactRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Send a support message to the admin team."""
    try:
        # Use authenticated user's info if available, otherwise use provided info
        if current_user:
            user_name = current_user.full_name or request.name
            user_email = current_user.email
        else:
            user_name = request.name
            user_email = request.email
        
        await EmailService.send_support_message(
            user_email=user_email,
            user_name=user_name,
            subject=request.subject,
            message=request.message,
            category=request.category
        )
        
        logger.info(f"Support message sent from {user_email}")
        
        return {
            "message": "Support message sent successfully. We'll get back to you within 24-48 hours.",
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Failed to send support message: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send support message. Please try again later."
        )