import redis.asyncio as redis
from app.core.config import settings

redis_client: redis.Redis = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def close_redis_client():
    """Close Redis client."""
    global redis_client
    if redis_client:
        await redis_client.close()
