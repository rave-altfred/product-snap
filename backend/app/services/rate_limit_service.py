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
                "jobs_total": settings.FREE_JOBS_PER_DAY,  # This is actually total, not per day
                "concurrent_jobs": settings.FREE_CONCURRENT_JOBS,
                "period": "total"
            }
        elif plan in [SubscriptionPlan.BASIC_MONTHLY, SubscriptionPlan.BASIC_YEARLY]:
            return {
                "jobs_per_month": settings.PERSONAL_JOBS_PER_MONTH,  # 100 jobs
                "concurrent_jobs": settings.PERSONAL_CONCURRENT_JOBS,  # 3 concurrent
                "period": "month"
            }
        elif plan in [SubscriptionPlan.PRO_MONTHLY, SubscriptionPlan.PRO_YEARLY]:
            return {
                "jobs_per_month": settings.PRO_JOBS_PER_MONTH,  # 1000 jobs
                "concurrent_jobs": settings.PRO_CONCURRENT_JOBS,  # 5 concurrent
                "period": "month"
            }
        # Fallback to free plan limits if unknown plan
        return {
            "jobs_total": settings.FREE_JOBS_PER_DAY,  # This is actually total, not per day
            "concurrent_jobs": settings.FREE_CONCURRENT_JOBS,
            "period": "total"
        }
    
    async def check_job_limit(self, user_id: str, plan: SubscriptionPlan) -> tuple[bool, str]:
        """Check if user can create a new job."""
        limits = self.get_plan_limits(plan)
        
        # Check usage limit
        if plan == SubscriptionPlan.FREE:
            # Use lifetime total for Free plan (no expiration)
            period_key = f"usage_total:{user_id}"
            max_jobs = limits["jobs_total"]
        else:
            period_key = f"usage:{user_id}:{datetime.utcnow().strftime('%Y-%m')}"
            max_jobs = limits.get("jobs_per_month", 0)
        
        current_usage = await self.redis.get(period_key)
        current_usage = int(current_usage) if current_usage else 0
        
        if current_usage >= max_jobs:
            period_text = "total" if limits['period'] == "total" else f"per {limits['period']}"
            return False, f"Usage limit exceeded ({max_jobs} jobs {period_text})"
        
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
            # Use lifetime total for Free plan (no expiration)
            period_key = f"usage_total:{user_id}"
            await self.redis.incr(period_key)
            # No TTL for Free plan - it's a lifetime total
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
            period_key = f"usage_total:{user_id}"
            max_jobs = limits["jobs_total"]
            period = "total"
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
    
    async def check_auth_rate_limit(self, ip_address: str, endpoint: str, max_attempts: int = 5, window_seconds: int = 300) -> tuple[bool, int]:
        """Check rate limit for auth endpoints (login, register, password reset).
        
        Args:
            ip_address: Client IP address
            endpoint: Endpoint name (e.g., 'login', 'register', 'forgot_password')
            max_attempts: Maximum attempts allowed in the time window
            window_seconds: Time window in seconds (default: 5 minutes)
        
        Returns:
            Tuple of (allowed, remaining_attempts)
        """
        key = f"auth_rate_limit:{endpoint}:{ip_address}"
        
        # Get current attempt count
        attempts = await self.redis.get(key)
        current_attempts = int(attempts) if attempts else 0
        
        if current_attempts >= max_attempts:
            # Check TTL to tell user when they can retry
            ttl = await self.redis.ttl(key)
            return False, 0
        
        return True, max_attempts - current_attempts
    
    async def increment_auth_attempts(self, ip_address: str, endpoint: str, window_seconds: int = 300):
        """Increment auth attempt counter for an IP address.
        
        Args:
            ip_address: Client IP address
            endpoint: Endpoint name
            window_seconds: Time window in seconds
        """
        key = f"auth_rate_limit:{endpoint}:{ip_address}"
        
        # Increment counter
        await self.redis.incr(key)
        
        # Set expiration if this is the first attempt
        ttl = await self.redis.ttl(key)
        if ttl == -1:  # Key exists but has no expiration
            await self.redis.expire(key, window_seconds)
    
    async def reset_auth_attempts(self, ip_address: str, endpoint: str):
        """Reset auth attempt counter (e.g., after successful login).
        
        Args:
            ip_address: Client IP address
            endpoint: Endpoint name
        """
        key = f"auth_rate_limit:{endpoint}:{ip_address}"
        await self.redis.delete(key)
