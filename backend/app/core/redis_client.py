import redis.asyncio as redis
from app.core.config import settings

redis_client: redis.Redis = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client instance.
    
    For DigitalOcean Managed Valkey with TLS (rediss://), redis-py 5.x
    handles SSL/TLS automatically. Just use the rediss:// URL as-is.
    """
    global redis_client
    if redis_client is None:
        import logging
        logger = logging.getLogger(__name__)
        
        # Validate REDIS_URL is set
        if not settings.REDIS_URL:
            error_msg = "REDIS_URL environment variable is not set"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Connecting to Redis/Valkey: {settings.REDIS_URL[:30]}...")
        
        # Clean up REDIS_URL - remove ssl_cert_reqs from query string if present
        # redis-py 5.x handles TLS automatically with rediss:// and doesn't need this parameter
        redis_url = settings.REDIS_URL
        if "?ssl_cert_reqs=" in redis_url or "&ssl_cert_reqs=" in redis_url:
            import re
            # Remove ssl_cert_reqs parameter
            redis_url = re.sub(r'[?&]ssl_cert_reqs=[^&]*', '', redis_url)
            # Clean up any trailing ? or &
            redis_url = re.sub(r'[?&]$', '', redis_url)
            logger.info(f"Cleaned URL (removed ssl_cert_reqs): {redis_url[:30]}...")
        
        # Simple connection parameters - let redis-py handle TLS automatically
        connection_kwargs = {
            "encoding": "utf-8",
            "decode_responses": True,
            "socket_connect_timeout": 10,
            "socket_timeout": 10,
        }
        
        try:
            # redis-py 5.x handles rediss:// URLs automatically with proper TLS
            redis_client = redis.from_url(
                redis_url,
                **connection_kwargs
            )
            logger.info("Redis client created, testing connection...")
            
            # Test the connection
            await redis_client.ping()
            logger.info("✓ Redis/Valkey connection successful!")
        except Exception as e:
            logger.error(f"Redis connection failed: {type(e).__name__}: {e}", exc_info=True)
            raise
    
    return redis_client


async def close_redis_client():
    """Close Redis client."""
    global redis_client
    if redis_client:
        await redis_client.close()
