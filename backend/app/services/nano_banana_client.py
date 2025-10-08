import httpx
import asyncio
from typing import Optional, Dict
import logging
import uuid
from datetime import datetime

from app.core.config import settings
from app.models import JobMode

logger = logging.getLogger(__name__)


class NanoBananaClient:
    """Client for Nano Banana image generation API."""
    
    PROMPT_TEMPLATES = {
        JobMode.STUDIO_WHITE: (
            "Precisely isolate the product. Crisp edges. Shadow: subtle studio product shadow. "
            "Pure white (#FFFFFF) background. No background props. No text. Professional product photography."
        ),
        JobMode.MODEL_TRYON: (
            "Present the product on a realistic model. Maintain correct scale and placement. "
            "Clean studio lighting. Neutral backdrop. Focus on product clarity. "
            "Natural pose, professional model."
        ),
        JobMode.LIFESTYLE_SCENE: (
            "Place the product in a natural setting that fits the category. "
            "Balanced lighting, photorealistic materials, consistent shadows. "
            "Avoid brand logos and text. Create an authentic lifestyle environment."
        )
    }
    
    def __init__(self):
        self.api_key = settings.NANO_BANANA_API_KEY
        self.api_url = settings.NANO_BANANA_API_URL
        self.mode = settings.IMAGE_GENERATION_MODE
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        logger.info(f"NanoBananaClient initialized in {self.mode} mode")
    
    def get_prompt(self, mode: JobMode, custom_prompt: Optional[str] = None) -> str:
        """Get the prompt for a job mode."""
        base_prompt = self.PROMPT_TEMPLATES.get(mode, "")
        if custom_prompt:
            return f"{base_prompt}\n\nAdditional instructions: {custom_prompt}"
        return base_prompt
    
    async def create_job(
        self,
        input_image_url: str,
        mode: JobMode,
        custom_prompt: Optional[str] = None
    ) -> Dict:
        """Create a new image generation job."""
        prompt = self.get_prompt(mode, custom_prompt)
        
        # Mock mode - simulate job creation
        if self.mode == "mock":
            job_id = f"mock_{uuid.uuid4().hex[:12]}"
            logger.info(f"[MOCK] Created job {job_id} for mode {mode.value}")
            return {
                "job_id": job_id,
                "status": "queued",
                "created_at": datetime.utcnow().isoformat()
            }
        
        # Live mode - actual API call
        payload = {
            "input_image": input_image_url,
            "prompt": prompt,
            "mode": mode.value,
            "output_format": "png",
            "quality": "high"
        }
        
        try:
            response = await self.client.post(
                f"{self.api_url}/v1/generate",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to create Nano Banana job: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Dict:
        """Get the status of a generation job."""
        # Mock mode - simulate completed job
        if self.mode == "mock":
            logger.info(f"[MOCK] Checking status for job {job_id}")
            return {
                "job_id": job_id,
                "status": "completed",
                "output_url": f"https://mock-storage.example.com/results/{job_id}.png",
                "completed_at": datetime.utcnow().isoformat()
            }
        
        # Live mode - actual API call
        try:
            response = await self.client.get(
                f"{self.api_url}/v1/jobs/{job_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get job status: {e}")
            raise
    
    async def poll_until_complete(
        self,
        job_id: str,
        max_wait_seconds: int = 300,
        poll_interval: int = 5
    ) -> Dict:
        """Poll a job until it completes or times out."""
        elapsed = 0
        while elapsed < max_wait_seconds:
            status = await self.get_job_status(job_id)
            
            job_status = status.get("status")
            if job_status in ["completed", "succeeded", "success"]:
                return status
            elif job_status in ["failed", "error"]:
                raise Exception(f"Job failed: {status.get('error', 'Unknown error')}")
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Job {job_id} did not complete within {max_wait_seconds} seconds")
    
    async def download_result(self, result_url: str) -> bytes:
        """Download generated image."""
        # Mock mode - return a simple 1x1 PNG
        if self.mode == "mock":
            logger.info(f"[MOCK] Downloading result from {result_url}")
            # Minimal valid PNG (1x1 transparent pixel)
            return bytes.fromhex(
                '89504e470d0a1a0a0000000d494844520000000100000001'
                '08060000001f15c4890000000a49444154789c6300010000'
                '00050001d5a371fe0000000049454e44ae426082'
            )
        
        # Live mode - actual download
        try:
            response = await self.client.get(result_url)
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            logger.error(f"Failed to download result: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
nano_banana_client = NanoBananaClient()
