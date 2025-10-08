from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
from PIL import Image
import io

from app.core.database import get_db
from app.core.redis_client import get_redis_client
from app.core.config import settings
from app.models import Job, JobMode, JobStatus, User, Subscription
from app.services.storage_service import storage_service
from app.services.rate_limit_service import RateLimitService
from app.routers.auth import get_current_user
import redis.asyncio as redis

router = APIRouter()


class CreateJobRequest(BaseModel):
    mode: JobMode
    prompt_override: Optional[str] = None


@router.post("/create")
async def create_job(
    file: UploadFile = File(...),
    mode: str = Form(...),
    prompt_override: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Create a new image generation job."""
    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"File upload attempt - filename: {file.filename}, content_type: {file.content_type}")
    
    # Read file content for validation
    file_content = await file.read()
    logger.info(f"File size: {len(file_content)} bytes")
    
    # Validate file size
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB"
        )
    
    # Validate file type (check both MIME type and actual content)
    logger.info(f"Checking MIME type - Received: {file.content_type}, Allowed: {settings.ALLOWED_IMAGE_TYPES}")
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        logger.error(f"MIME type validation failed - Received: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Supported types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    
    # Validate image content and dimensions
    try:
        # Reset file position and validate image
        image_stream = io.BytesIO(file_content)
        with Image.open(image_stream) as img:
            # Verify it's actually an image
            img.verify()
            
            # Re-open for dimension checking (verify() makes image unusable)
            image_stream.seek(0)
            with Image.open(image_stream) as img:
                width, height = img.size
                logger.info(f"Image opened - Format: {img.format}, Mode: {img.mode}, Size: {width}x{height}")
                
                if width < settings.MIN_IMAGE_WIDTH or height < settings.MIN_IMAGE_HEIGHT:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Image dimensions too small. Minimum required: {settings.MIN_IMAGE_WIDTH}x{settings.MIN_IMAGE_HEIGHT}px, got: {width}x{height}px"
                    )
                
                # Check image format matches MIME type
                format_mime_mapping = {
                    'JPEG': 'image/jpeg',
                    'PNG': 'image/png',
                    'WEBP': 'image/webp',
                    'HEIF': ['image/heic', 'image/heif']
                }
                
                if img.format not in format_mime_mapping:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unsupported image format: {img.format}"
                    )
                
                expected_mime = format_mime_mapping[img.format]
                # Handle both single MIME type and list of MIME types (for HEIF)
                if isinstance(expected_mime, list):
                    if file.content_type not in expected_mime:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File content does not match declared MIME type. Expected one of: {', '.join(expected_mime)}, got: {file.content_type}"
                        )
                else:
                    if file.content_type != expected_mime:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File content does not match declared MIME type. Expected: {expected_mime}, got: {file.content_type}"
                        )
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}"
        )
    
    # Get user subscription
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active subscription"
        )
    
    # Check rate limits
    rate_limiter = RateLimitService(redis_client)
    can_create, error_msg = await rate_limiter.check_job_limit(current_user.id, subscription.plan)
    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_msg
        )
    
    # Upload input file (content already read during validation)
    input_url = storage_service.upload_bytes(
        file_content,
        file.filename or "upload.png",
        file.content_type,
        folder="uploads"
    )
    
    # Create job
    job = Job(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        mode=JobMode(mode),
        status=JobStatus.QUEUED,
        input_url=input_url,
        input_filename=file.filename,
        prompt_override=prompt_override
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Increment usage
    await rate_limiter.increment_usage(current_user.id, subscription.plan)
    
    # Add to queue
    await redis_client.rpush("job_queue", job.id)
    
    return {"job_id": job.id, "status": job.status.value}


@router.get("/list")
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """List user's jobs."""
    jobs = db.query(Job).filter(
        Job.user_id == current_user.id
    ).order_by(Job.created_at.desc()).limit(limit).offset(offset).all()
    
    # Add signed URLs for results
    job_list = []
    for job in jobs:
        job_dict = {
            "id": job.id,
            "mode": job.mode.value,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "progress": job.progress,
            "thumbnail_url": storage_service.get_signed_url(job.thumbnail_url) if job.thumbnail_url else None
        }
        job_list.append(job_dict)
    
    return {"jobs": job_list}


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job details with signed URLs."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return {
        "id": job.id,
        "mode": job.mode.value,
        "status": job.status.value,
        "input_url": storage_service.get_signed_url(job.input_url),
        "result_urls": [storage_service.get_signed_url(url) for url in (job.result_urls or [])],
        "thumbnail_url": storage_service.get_signed_url(job.thumbnail_url) if job.thumbnail_url else None,
        "progress": job.progress,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message
    }


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a job and its assets."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Delete assets from storage
    if job.input_url:
        storage_service.delete_file(job.input_url)
    if job.thumbnail_url:
        storage_service.delete_file(job.thumbnail_url)
    for url in (job.result_urls or []):
        storage_service.delete_file(url)
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}
