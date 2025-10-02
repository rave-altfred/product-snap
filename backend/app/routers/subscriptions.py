from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User, Subscription
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/me")
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription."""
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not subscription:
        return {"plan": "free", "status": "active"}
    
    return {
        "plan": subscription.plan.value,
        "status": subscription.status.value,
        "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None
    }
