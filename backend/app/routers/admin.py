from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User
from app.routers.auth import get_current_user

router = APIRouter()


async def require_admin(current_user: User = Depends(get_current_user)):
    """Ensure user is admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/stats")
async def get_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin statistics."""
    # Placeholder for admin stats
    return {"message": "Admin stats endpoint"}
