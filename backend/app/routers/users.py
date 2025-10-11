from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import redis.asyncio as redis
from app.core.database import get_db
from app.core.redis_client import get_redis_client
from app.models import User, Job, Subscription, SubscriptionPlan, SubscriptionStatus
from app.services.rate_limit_service import RateLimitService
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
