from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from pydantic import BaseModel
import redis.asyncio as redis
import logging
from app.core.database import get_db
from app.core.redis_client import get_redis_client
from app.models import User, Job, Subscription, SubscriptionPlan, SubscriptionStatus
from app.services.rate_limit_service import RateLimitService
from app.services.paypal_service import PayPalService
from app.services.auth_service import AuthService
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


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
        "is_admin": current_user.is_admin,
        "oauth_provider": current_user.oauth_provider.value if current_user.oauth_provider else None
    }


@router.put("/me")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    try:
        if request.full_name is not None:
            current_user.full_name = request.full_name
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "message": "Profile updated successfully"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update profile for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user's password."""
    # Check if user is OAuth user (shouldn't have password)
    if not current_user.password_hash:
        raise HTTPException(
            status_code=400,
            detail="Cannot change password for OAuth users"
        )
    
    # Verify current password
    if not AuthService.verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 8 characters long"
        )
    
    try:
        # Update password
        current_user.password_hash = AuthService.hash_password(request.new_password)
        db.commit()
        
        logger.info(f"Password changed for user {current_user.id}")
        
        return {"message": "Password changed successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to change password for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")


@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Get current user's usage statistics."""
    # Get user's subscription to determine plan
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not subscription:
        plan = SubscriptionPlan.FREE
    else:
        # If subscription is not active, treat as free
        plan = subscription.plan if subscription.status == SubscriptionStatus.ACTIVE else SubscriptionPlan.FREE
    
    # Get usage stats from rate limiter service
    rate_limiter = RateLimitService(redis_client)
    usage_stats = await rate_limiter.get_usage_stats(current_user.id, plan)
    
    # Get total jobs count from database
    total_jobs = db.query(func.count(Job.id)).filter(Job.user_id == current_user.id).scalar() or 0
    
    # Get today's jobs count
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_jobs = db.query(func.count(Job.id)).filter(
        Job.user_id == current_user.id,
        Job.created_at >= today_start
    ).scalar() or 0
    
    # Format plan name
    plan_display_names = {
        SubscriptionPlan.FREE: "Free",
        SubscriptionPlan.BASIC_MONTHLY: "Basic",
        SubscriptionPlan.BASIC_YEARLY: "Basic",
        SubscriptionPlan.PRO_MONTHLY: "Pro",
        SubscriptionPlan.PRO_YEARLY: "Pro"
    }
    
    return {
        "today_usage": today_jobs,
        "today_limit": usage_stats["max_jobs"] if usage_stats["period"] == "day" else None,
        "current_period_usage": usage_stats["current_usage"],
        "current_period_limit": usage_stats["max_jobs"],
        "period": usage_stats["period"],
        "total_jobs": total_jobs,
        "plan": plan_display_names.get(plan, "Unknown"),
        "plan_raw": plan.value,
        "remaining_jobs": usage_stats["remaining"]
    }


@router.delete("/delete-account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and cancel active subscription."""
    try:
        # Check if user has active subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        # Cancel PayPal subscription if active
        if subscription and subscription.status == SubscriptionStatus.ACTIVE:
            if subscription.paypal_subscription_id:
                paypal_service = PayPalService()
                cancelled = paypal_service.cancel_subscription(
                    subscription.paypal_subscription_id,
                    reason="Account deletion"
                )
                if cancelled:
                    logger.info(f"Cancelled PayPal subscription {subscription.paypal_subscription_id} for user {current_user.id}")
                else:
                    logger.warning(f"Failed to cancel PayPal subscription {subscription.paypal_subscription_id} for user {current_user.id}")
        
        # Delete user (cascade will handle related records)
        db.delete(current_user)
        db.commit()
        
        logger.info(f"Deleted user account: {current_user.id} ({current_user.email})")
        
        return {"message": "Account deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete account for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete account")
