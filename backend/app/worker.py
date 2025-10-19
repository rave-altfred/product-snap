"""
Background worker for processing image generation jobs.
Run with: python -m app.worker
v2.1 - Testing cache
"""
import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional
from PIL import Image
import io
import uuid

# Register HEIF plugin for Pillow
from pillow_heif import register_heif_opener
register_heif_opener()

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.redis_client import get_redis_client
from app.models import Job, JobStatus, User
from app.services.storage_service import storage_service
from app.services.nano_banana_client import nano_banana_client
from app.services.rate_limit_service import RateLimitService
from app.services.analytics_service import analytics
from app.services.email_service import email_service

logger = setup_logging()
shutdown_flag = False


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    global shutdown_flag
    logger.info("Shutdown signal received")
    shutdown_flag = True


async def create_thumbnail(image_bytes: bytes) -> bytes:
    """Create a thumbnail from image bytes."""
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail((400, 400), Image.Resampling.LANCZOS)
    
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


async def process_job(job_id: str, db: Session, redis, rate_limiter: RateLimitService):
    """Process a single image generation job."""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        # Get user for plan limits
        user = db.query(User).filter(User.id == job.user_id).first()
        if not user:
            logger.error(f"User {job.user_id} not found")
            return
        
        logger.info(f"Processing job {job_id} for user {user.id}")
        
        # Update status to processing
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Increment concurrent counter
        await rate_limiter.increment_concurrent(user.id)
        
        try:
            # Pass S3 URL directly - the nano_banana_client will download from S3 internally
            input_url = job.input_url
            
            # Parse prompt metadata (sub-options)
            import json
            shadow_option = None
            subject_gender = None  # Renamed from model_gender
            scene_environment = None
            
            if job.prompt:
                try:
                    prompt_metadata = json.loads(job.prompt)
                    shadow_option = prompt_metadata.get('shadow_option')
                    subject_gender = prompt_metadata.get('subject_gender')  # New key
                    scene_environment = prompt_metadata.get('scene_environment')
                    logger.info(f"Job {job_id} sub-options: shadow={shadow_option}, gender={subject_gender}, environment={scene_environment}")
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse prompt metadata for job {job_id}")
            
            # Create Nano Banana job (Gemini generates synchronously)
            nb_response = await nano_banana_client.create_job(
                input_image_url=input_url,
                mode=job.mode,
                custom_prompt=job.prompt_override,
                shadow_option=shadow_option,
                subject_gender=subject_gender,
                scene_environment=scene_environment
            )
            
            job.nano_banana_job_id = nb_response.get("job_id")
            db.commit()
            
            # For Gemini, generation is synchronous - images are in the response
            generated_images = nb_response.get("generated_images", [])
            
            if not generated_images:
                # Fallback: try polling (for other APIs)
                result = await nano_banana_client.poll_until_complete(
                    job.nano_banana_job_id,
                    max_wait_seconds=300
                )
                generated_images = result.get("generated_images", [])
            
            # Store generated images to S3
            import base64
            result_urls = []
            for idx, image_base64 in enumerate(generated_images):
                try:
                    # Decode base64 image
                    image_bytes = base64.b64decode(image_base64)
                    logger.info(f"Decoded image {idx+1}/{len(generated_images)}, size: {len(image_bytes)} bytes")
                    
                    # Upload to storage
                    s3_url = storage_service.upload_bytes(
                        image_bytes,
                        f"result_{uuid.uuid4()}.png",
                        "image/png",
                        folder="results"
                    )
                    result_urls.append(s3_url)
                    logger.info(f"Uploaded generated image to {s3_url}")
                except Exception as e:
                    logger.error(f"Failed to process generated image {idx+1}: {e}")
            
            # Create thumbnail from first result
            if result_urls:
                first_result_bytes = storage_service.download_file(result_urls[0])
                if first_result_bytes:
                    thumbnail_bytes = await create_thumbnail(first_result_bytes)
                    thumbnail_url = storage_service.upload_bytes(
                        thumbnail_bytes,
                        f"thumb_{uuid.uuid4()}.png",
                        "image/png",
                        folder="thumbnails"
                    )
                    job.thumbnail_url = thumbnail_url
            
            # Update job with results
            job.status = JobStatus.COMPLETED
            job.result_urls = result_urls
            job.completed_at = datetime.utcnow()
            job.progress = 100
            
            if job.started_at:
                processing_time = (job.completed_at - job.started_at).total_seconds()
                job.processing_time_seconds = str(int(processing_time))
            
            db.commit()
            
            # Track successful job completion
            analytics.capture(
                user_id=str(user.id),
                event="job_completed",
                properties={
                    "job_id": str(job.id),
                    "mode": job.mode,
                    "processing_time_seconds": int(processing_time) if job.started_at else None,
                    "num_results": len(result_urls),
                }
            )
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
            
            # Track job failure
            analytics.capture(
                user_id=str(user.id),
                event="job_failed",
                properties={
                    "job_id": str(job.id),
                    "mode": job.mode,
                    "error": str(e),
                }
            )
        
        finally:
            # Decrement concurrent counter
            await rate_limiter.decrement_concurrent(user.id)
            # Flush PostHog events to ensure they're sent
            analytics.flush()
    
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}", exc_info=True)


async def worker_loop():
    """Main worker loop."""
    print("[WORKER] Starting worker loop...", flush=True)
    logger.info("Worker starting...")
    sys.stdout.flush()  # Force flush to ensure log appears
    print("[WORKER] After first log, about to connect to Redis", flush=True)
    
    # Log environment info for debugging
    import os
    redis_url_configured = "REDIS_URL" in os.environ
    redis_url_prefix = os.environ.get("REDIS_URL", "")[:20] if redis_url_configured else "NOT_SET"
    logger.info(f"Redis URL configured: {redis_url_configured}, prefix: {redis_url_prefix}")
    print(f"[WORKER] Redis URL configured: {redis_url_configured}", flush=True)
    sys.stdout.flush()
    
    logger.info("About to connect to Redis...")
    sys.stdout.flush()
    print("[WORKER] Logged Redis connection intent", flush=True)
    
    try:
        redis = await get_redis_client()
        logger.info("Redis connection established successfully")
        print("[WORKER] Redis connected!", flush=True)
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {type(e).__name__}: {e}", exc_info=True)
        print(f"[WORKER] Redis connection FAILED: {type(e).__name__}: {e}", flush=True)
        sys.stdout.flush()
        # Don't raise immediately - let's try to provide more context
        import traceback
        traceback.print_exc()
        sys.stderr.flush()
        raise
    
    rate_limiter = RateLimitService(redis)
    
    # Test database connection
    try:
        from sqlalchemy import text
        test_db = SessionLocal()
        test_db.execute(text("SELECT 1"))
        test_db.close()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}", exc_info=True)
        raise
    
    logger.info("Worker initialization complete, starting main loop")
    
    while not shutdown_flag:
        db = SessionLocal()
        try:
            # Get pending jobs from queue (Redis list)
            job_id = await redis.lpop("job_queue")
            
            if job_id:
                await process_job(job_id, db, redis, rate_limiter)
            else:
                # No jobs, sleep for a bit
                await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Worker loop error: {e}", exc_info=True)
            await asyncio.sleep(5)
        
        finally:
            db.close()
    
    logger.info("Worker shutting down...")


async def check_stale_jobs():
    """Periodically check for stale jobs and requeue them."""
    while not shutdown_flag:
        try:
            db = SessionLocal()
            
            # Find jobs that have been processing for more than 15 minutes
            stale_threshold = datetime.utcnow() - timedelta(minutes=15)
            stale_jobs = db.query(Job).filter(
                Job.status == JobStatus.PROCESSING,
                Job.started_at < stale_threshold
            ).all()
            
            redis = await get_redis_client()
            for job in stale_jobs:
                logger.warning(f"Requeuing stale job {job.id}")
                job.status = JobStatus.QUEUED
                db.commit()
                await redis.rpush("job_queue", job.id)
            
            db.close()
        
        except Exception as e:
            logger.error(f"Error checking stale jobs: {e}")
        
        await asyncio.sleep(60)  # Check every minute


async def main():
    """Main entry point."""
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run worker and stale job checker concurrently
        await asyncio.gather(
            worker_loop(),
            check_stale_jobs()
        )
    except Exception as e:
        logger.error(f"Worker failed to start: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error in worker: {e}", exc_info=True)
        sys.exit(1)
