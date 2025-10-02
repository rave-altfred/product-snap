from datetime import datetime, timedelta
from typing import Optional
import redis.asyncio as redis

from app.core.config import settings
from app.models import SubscriptionPlan


class RateLimitService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def get_plan_limits(self, plan: SubscriptionPlan) -> dict:
        """Get rate limits for a subscription plan."""
        if plan == SubscriptionPlan.FREE:
            return {
                "jobs_per_day": settings.FREE_JOBS_PER_DAY,
                "concurrent_jobs": settings.FREE_CONCURRENT_JOBS,
                "period": "day"
            }
        elif plan == SubscriptionPlan.PERSONAL:
            return {
                "jobs_per_month": settings.PERSONAL_JOBS_PER_MONTH,
                "concurrent_jobs": settings.PERSONAL_CONCURRENT_JOBS,
                "period": "month"
            }
        elif plan == SubscriptionPlan.PRO:
            return {
                "jobs_per_month": settings.PRO_JOBS_PER_MONTH,
                "concurrent_jobs": settings.PRO_CONCURRENT_JOBS,
                "period": "month"
            }
        return {}
    
    async def check_job_limit(self, user_id: str, plan: SubscriptionPlan) -> tuple[bool, str]:
        """Check if user can create a new job."""
        limits = self.get_plan_limits(plan)
        
        # Check usage limit
        if plan == SubscriptionPlan.FREE:
            period_key = f"usage:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
            max_jobs = limits["jobs_per_day"]
        else:
            period_key = f"usage:{user_id}:{datetime.utcnow().strftime('%Y-%m')}"
            max_jobs = limits.get("jobs_per_month", 0)
        
        current_usage = await self.redis.get(period_key)
        current_usage = int(current_usage) if current_usage else 0
        
        if current_usage >= max_jobs:
            return False, f"Usage limit exceeded ({max_jobs} jobs per {limits['period']})"
        
        # Check concurrent jobs
        concurrent_key = f"concurrent:{user_id}"
        concurrent_jobs = await self.redis.get(concurrent_key)
        concurrent_jobs = int(concurrent_jobs) if concurrent_jobs else 0
        
        if concurrent_jobs >= limits["concurrent_jobs"]:
            return False, f"Concurrent job limit exceeded ({limits['concurrent_jobs']} jobs)"
        
        return True, ""
    
    async def increment_usage(self, user_id: str, plan: SubscriptionPlan):
        """Increment user's job usage counter."""
        if plan == SubscriptionPlan.FREE:
            period_key = f"usage:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
            ttl = 86400  # 1 day
        else:
            period_key = f"usage:{user_id}:{datetime.utcnow().strftime('%Y-%m')}"
            ttl = 2592000  # 30 days
        
        await self.redis.incr(period_key)
        await self.redis.expire(period_key, ttl)
    
    async def increment_concurrent(self, user_id: str):
        """Increment concurrent job counter."""
        concurrent_key = f"concurrent:{user_id}"
        await self.redis.incr(concurrent_key)
    
    async def decrement_concurrent(self, user_id: str):
        """Decrement concurrent job counter."""
        concurrent_key = f"concurrent:{user_id}"
        count = await self.redis.decr(concurrent_key)
        # Ensure it doesn't go negative
        if count < 0:
            await self.redis.set(concurrent_key, 0)
    
    async def get_usage_stats(self, user_id: str, plan: SubscriptionPlan) -> dict:
        """Get user's current usage statistics."""
        limits = self.get_plan_limits(plan)
        
        if plan == SubscriptionPlan.FREE:
            period_key = f"usage:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
            max_jobs = limits["jobs_per_day"]
            period = "day"
        else:
            period_key = f"usage:{user_id}:{datetime.utcnow().strftime('%Y-%m')}"
            max_jobs = limits.get("jobs_per_month", 0)
            period = "month"
        
        current_usage = await self.redis.get(period_key)
        current_usage = int(current_usage) if current_usage else 0
        
        concurrent_key = f"concurrent:{user_id}"
        concurrent_jobs = await self.redis.get(concurrent_key)
        concurrent_jobs = int(concurrent_jobs) if concurrent_jobs else 0
        
        return {
            "current_usage": current_usage,
            "max_jobs": max_jobs,
            "period": period,
            "concurrent_jobs": concurrent_jobs,
            "max_concurrent": limits["concurrent_jobs"],
            "remaining": max(0, max_jobs - current_usage)
        }
