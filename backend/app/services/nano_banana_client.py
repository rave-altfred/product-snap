import httpx
import asyncio
from typing import Optional, Dict
import logging
import uuid
import random
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

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
    
    def get_prompt(
        self, 
        mode: JobMode, 
        custom_prompt: Optional[str] = None,
        shadow_option: Optional[str] = None,
        model_gender: Optional[str] = None,
        scene_environment: Optional[str] = None
    ) -> str:
        """Get the prompt for a job mode with sub-options."""
        base_prompt = self.PROMPT_TEMPLATES.get(mode, "")
        
        # Add sub-option specific instructions
        modifications = []
        
        if mode == JobMode.STUDIO_WHITE and shadow_option:
            if shadow_option == 'no_shadow':
                modifications.append("No shadow. Completely flat, pure white isolation.")
            elif shadow_option == 'drop_shadow':
                modifications.append("Subtle drop shadow for depth.")
        
        if mode == JobMode.MODEL_TRYON and model_gender:
            if model_gender == 'male':
                modifications.append("Show on a male model with masculine features and styling.")
            elif model_gender == 'female':
                modifications.append("Show on a female model with feminine features and styling.")
        
        if mode == JobMode.LIFESTYLE_SCENE and scene_environment:
            if scene_environment == 'indoor':
                modifications.append("Indoor setting: kitchen counter, desk, living room, or bedroom environment.")
            elif scene_environment == 'outdoor':
                modifications.append("Outdoor setting: garden, park, cafe terrace, or street scene.")
        
        # Build final prompt
        final_prompt = base_prompt
        if modifications:
            final_prompt = f"{base_prompt} {' '.join(modifications)}"
        
        if custom_prompt:
            final_prompt = f"{final_prompt}\n\nAdditional instructions: {custom_prompt}"
        
        return final_prompt
    
    async def create_job(
        self,
        input_image_url: str,
        mode: JobMode,
        custom_prompt: Optional[str] = None,
        shadow_option: Optional[str] = None,
        model_gender: Optional[str] = None,
        scene_environment: Optional[str] = None
    ) -> Dict:
        """Create a new image generation job."""
        prompt = self.get_prompt(
            mode, 
            custom_prompt, 
            shadow_option, 
            model_gender, 
            scene_environment
        )
        
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
        # Mock mode - simulate realistic generation time (5-15 seconds)
        if self.mode == "mock":
            generation_time = random.uniform(5, 15)
            logger.info(f"[MOCK] Simulating generation for {generation_time:.1f} seconds")
            await asyncio.sleep(generation_time)
            return await self.get_job_status(job_id)
        
        # Live mode - actual polling
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
    
    def _generate_mock_image(self, prompt: str, mode: str, job_id: str) -> bytes:
        """Generate a mock result image with prompt text and info."""
        # Create image (1024x1024)
        width, height = 1024, 1024
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        # Try multiple common font paths for cross-platform compatibility
        title_font = None
        text_font = None
        small_font = None
        
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/Library/Fonts/Arial.ttf",  # macOS
            "C:\\Windows\\Fonts\\Arial.ttf",  # Windows
        ]
        
        for font_path in font_paths:
            try:
                title_font = ImageFont.truetype(font_path, 32)
                text_font = ImageFont.truetype(font_path, 20)
                small_font = ImageFont.truetype(font_path, 16)
                break
            except Exception:
                continue
        
        # If no system fonts found, use PIL's default
        if not title_font:
            logger.warning("No TrueType fonts found, using default font")
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw title
        title = "[MOCK GENERATION]"
        draw.text((50, 50), title, fill='red', font=title_font)
        
        # Draw mode
        mode_text = f"Mode: {mode.upper()}"
        draw.text((50, 120), mode_text, fill='black', font=text_font)
        
        # Draw job ID
        job_text = f"Job ID: {job_id}"
        draw.text((50, 160), job_text, fill='gray', font=small_font)
        
        # Draw timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        draw.text((50, 190), f"Generated: {timestamp}", fill='gray', font=small_font)
        
        # Draw prompt (wrapped)
        prompt_title = "Prompt:"
        draw.text((50, 240), prompt_title, fill='black', font=text_font)
        
        # Wrap prompt text
        y_offset = 280
        max_width = width - 100
        words = prompt.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Use textbbox if available (Pillow >= 8.0.0), otherwise use textsize
            try:
                bbox = draw.textbbox((0, 0), test_line, font=small_font)
                text_width = bbox[2] - bbox[0]
            except AttributeError:
                text_width = draw.textsize(test_line, font=small_font)[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw wrapped lines
        for line in lines[:30]:  # Max 30 lines
            draw.text((50, y_offset), line, fill='#333333', font=small_font)
            y_offset += 25
        
        # Draw footer
        footer = "This is a mock result for development. Enable live mode to generate real images."
        draw.text((50, height - 50), footer, fill='gray', font=small_font)
        
        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    async def download_result(self, result_url: str, prompt: str = "", mode: str = "", job_id: str = "") -> bytes:
        """Download generated image."""
        # Mock mode - generate image with prompt info
        if self.mode == "mock":
            logger.info(f"[MOCK] Generating mock result image")
            return self._generate_mock_image(prompt, mode, job_id)
        
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
