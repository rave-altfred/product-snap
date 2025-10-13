from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
from PIL import Image
import io

# Register HEIF support
import pillow_heif
from pillow_heif import register_heif_opener
register_heif_opener()

from app.core.database import get_db
from app.core.redis_client import get_redis_client
from app.core.config import settings
from app.models import Job, JobMode, JobStatus, User, Subscription, SubscriptionPlan, SubscriptionStatus
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
    shadow_option: Optional[str] = Form(None),
    model_gender: Optional[str] = Form(None),
    scene_environment: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Create a new image generation job."""
    # Register HEIF support (safe to call multiple times)
    register_heif_opener()
    
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
        # Check if it's a HEIC/HEIF file by extension
        is_heif = file.filename and (file.filename.lower().endswith('.heic') or file.filename.lower().endswith('.heif'))
        
        if is_heif:
            # Use pillow_heif.open_heif() which is more forgiving with metadata
            logger.info("Decoding HEIC file with pillow_heif.open_heif()...")
            heif_file = pillow_heif.open_heif(file_content, convert_hdr_to_8bit=False, bgr_mode=False)
            
            width, height = heif_file.size
            logger.info(f"HEIC decoded - Size: {width}x{height}, Mode: {heif_file.mode}")
            
            # Validate dimensions
            if width < settings.MIN_IMAGE_WIDTH or height < settings.MIN_IMAGE_HEIGHT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image dimensions too small. Minimum required: {settings.MIN_IMAGE_WIDTH}x{settings.MIN_IMAGE_HEIGHT}px, got: {width}x{height}px"
                )
            
            # Skip the rest of validation for HEIC since we've already decoded it
            img_format = 'HEIF'
        else:
            # Reset file position and validate image
            image_stream = io.BytesIO(file_content)
            with Image.open(image_stream) as img:
                # Verify it's actually an image
                img.verify()
                
                # Re-open for dimension checking (verify() makes image unusable)
                image_stream.seek(0)
                with Image.open(image_stream) as img:
                    width, height = img.size
                    img_format = img.format
                    logger.info(f"Image opened - Format: {img_format}, Mode: {img.mode}, Size: {width}x{height}")
                
                    if width < settings.MIN_IMAGE_WIDTH or height < settings.MIN_IMAGE_HEIGHT:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Image dimensions too small. Minimum required: {settings.MIN_IMAGE_WIDTH}x{settings.MIN_IMAGE_HEIGHT}px, got: {width}x{height}px"
                        )
        
        # Check image format matches MIME type
        format_mime_mapping = {
            'JPEG': 'image/jpeg',
            'MPO': 'image/jpeg',  # MPO is Multi-Picture Object (JPEG-based)
            'PNG': 'image/png',
            'WEBP': 'image/webp',
            'HEIF': ['image/heic', 'image/heif']
        }
        
        if img_format not in format_mime_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format: {img_format}"
            )
        
        expected_mime = format_mime_mapping[img_format]
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
        logger.error(f"Failed to validate image: {str(e)}", exc_info=True)
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
    
    # Check if subscription is active (pending subscriptions should use free limits)
    effective_plan = subscription.plan
    if subscription.status != SubscriptionStatus.ACTIVE:
        # If subscription is pending/cancelled/expired, treat as free
        effective_plan = SubscriptionPlan.FREE
    
    # Check rate limits
    rate_limiter = RateLimitService(redis_client)
    can_create, error_msg = await rate_limiter.check_job_limit(current_user.id, effective_plan)
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
    
    # Build prompt metadata from sub-options
    prompt_metadata = {}
    if shadow_option:
        prompt_metadata['shadow_option'] = shadow_option
    if model_gender:
        prompt_metadata['model_gender'] = model_gender
    if scene_environment:
        prompt_metadata['scene_environment'] = scene_environment
    
    # Store as JSON string in prompt field if we have metadata
    import json
    prompt_json = json.dumps(prompt_metadata) if prompt_metadata else None
    
    # Create job
    job = Job(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        mode=JobMode(mode),
        status=JobStatus.QUEUED,
        input_url=input_url,
        input_filename=file.filename,
        prompt=prompt_json,
        prompt_override=prompt_override
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Increment usage (use effective plan to track correctly)
    await rate_limiter.increment_usage(current_user.id, effective_plan)
    
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
            "thumbnail_url": storage_service.get_signed_url(job.thumbnail_url) if job.thumbnail_url else None,
            "result_urls": [storage_service.get_signed_url(url) for url in (job.result_urls or [])],
            "input_filename": job.input_filename,
            "error_message": job.error_message
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


@router.patch("/{job_id}")
async def update_job(
    job_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update job details (e.g., filename)."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Update allowed fields
    if "input_filename" in request:
        job.input_filename = request["input_filename"]
    
    db.commit()
    db.refresh(job)
    
    return {
        "id": job.id,
        "input_filename": job.input_filename,
        "message": "Job updated successfully"
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
