from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "email_verified": current_user.email_verified,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at.isoformat(),
        "is_admin": current_user.is_admin
    }
