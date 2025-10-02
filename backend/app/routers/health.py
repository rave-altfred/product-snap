from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.redis_client import get_redis_client
import redis.asyncio as redis

router = APIRouter()


@router.get("/health")
async def health_check(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Health check endpoint."""
    # Check database
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        await redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    healthy = db_status == "healthy" and redis_status == "healthy"
    
    return {
        "status": "healthy" if healthy else "degraded",
        "services": {
            "database": db_status,
            "redis": redis_status
        }
    }
