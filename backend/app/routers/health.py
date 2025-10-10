from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.redis_client import get_redis_client
from app.core.config import settings
import redis.asyncio as redis
import subprocess
from datetime import datetime

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


@router.get("/version")
async def get_version():
    """Return application version information."""
    version_info = {
        "version": settings.APP_VERSION,
        "app_name": settings.APP_NAME,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Try to get git information
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        version_info["git_commit"] = git_commit
    except Exception:
        pass
    
    try:
        git_branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        version_info["git_branch"] = git_branch
    except Exception:
        pass
    
    return version_info
