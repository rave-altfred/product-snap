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
            "Create a realistic product try-on photo showing a professional model wearing or using the product."
            "The product type is not specified — first analyze and infer what kind of product it is (for example: sunglasses, jewelry, hat, shoes, watch, handbag, etc.) and research how such products are usually presented in professional catalog or ecommerce photography."
            "Use appropriate lighting, composition, and model pose typical for that product category."
            "The model should appear natural, confident, and stylish, following poses and expressions seen in commercial fashion photography for that type of item."
            "Keep the background clean, minimal, and studio-like unless lifestyle context is commonly used for that product."
            "Ensure that the product is clearly visible, well-lit, and in focus."
            "Produce a high-quality, photorealistic image suitable for ecommerce or advertising use."
            "photorealistic professional product try-on, model wearing or using the product, AI should infer typical presentation for the product category, commercial fashion style, accurate lighting, natural confident pose, minimal studio background, high detail, soft shadows, ecommerce photography look"
        ),
        JobMode.LIFESTYLE_SCENE: (
            "Create a high-quality, photorealistic lifestyle scene image showing the product naturally placed "
            "in a real-world environment that fits its category. "
            "The product type is not specified — first analyze and infer what kind of product it is "
            "(for example: sunglasses, jewelry, hat, shoes, watch, handbag, etc.) and research how such products "
            "are usually presented in professional catalog or ecommerce lifestyle photography. "
            "Do not modify, replace, fill, or remove any part of the product. Preserve its original shape, proportions, "
            "surface texture, material, color, and any printed or engraved logos or markings exactly as shown. "
            "Do not add objects inside, on top of, or attached to the product. "
            "The scene should appear natural, stylish, and realistic, following lighting and composition principles "
            "seen in professional commercial photography for that product type. "
            "Use realistic materials, reflections, and balanced composition consistent with professional lifestyle imagery. "
            "Keep the focus on the product itself — it should be clearly visible, well-lit, and harmoniously integrated with the environment. "
            "Produce a photorealistic, high-detail, commercial-quality image suitable for ecommerce or social media promotion. "
            "photorealistic product lifestyle photo, natural setting matching product type, realistic materials, coherent shadows, authentic lighting, "
            "unaltered product geometry, preserve logos and textures, product as main subject, commercial photography style"
        )
    }
    
    def __init__(self):
        self.api_key = settings.NANO_BANANA_API_KEY
        self.api_url = settings.NANO_BANANA_API_URL
        self.project_id = settings.GOOGLE_CLOUD_PROJECT_ID
        self.use_vertex_ai = settings.USE_VERTEX_AI
        self.mode = settings.IMAGE_GENERATION_MODE
        
        # Initialize auth for Vertex AI if enabled
        if self.use_vertex_ai:
            try:
                import google.auth
                from google.auth.transport.requests import Request
                
                # Get default credentials (from ADC or environment)
                self.credentials, self.auth_project = google.auth.default(
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                logger.info(f"Using Vertex AI with project: {self.project_id}")
            except Exception as e:
                logger.error(f"Failed to initialize Vertex AI auth: {e}")
                logger.info("Falling back to API key mode")
                self.use_vertex_ai = False
        
        self.client = httpx.AsyncClient(
            timeout=60.0,  # Increased timeout for image generation
            headers={
                "Content-Type": "application/json"
            }
        )
        logger.info(f"NanoBananaClient initialized in {self.mode} mode (Vertex AI: {self.use_vertex_ai})")
    
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
        import base64
        from app.services.storage_service import storage_service
        
        if self.use_vertex_ai:
            # Vertex AI: Gemini 2.5 Flash Image (multimodal with image generation)
            model = "gemini-2.5-flash-image"
            endpoint = f"https://aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1/publishers/google/models/{model}:generateContent"
        else:
            # Generative Language API: Gemini 2.5 Flash Image
            model = "gemini-2.5-flash-image"
            endpoint = f"{self.api_url}/v1beta/models/{model}:generateContent"
        
        # Download the image from S3 and convert to base64
        try:
            # If input_image_url is an s3:// URL, download directly from S3
            # If it's a signed URL, parse it to get the S3 key and download from S3
            if input_image_url.startswith('s3://'):
                logger.info(f"Downloading image from S3: {input_image_url}")
                image_bytes = storage_service.download_file(input_image_url)
                if not image_bytes:
                    raise Exception("Failed to download image from S3")
            else:
                # Try to download from URL (signed URL)
                logger.info(f"Downloading image from URL: {input_image_url}")
                img_response = await self.client.get(input_image_url)
                img_response.raise_for_status()
                image_bytes = img_response.content
            
            image_data = base64.b64encode(image_bytes).decode('utf-8')
            
            # Detect content type (default to jpeg)
            content_type = 'image/jpeg'
            if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
                content_type = 'image/png'
            elif image_bytes[:2] == b'\xff\xd8':
                content_type = 'image/jpeg'
            elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
                content_type = 'image/webp'
            
            logger.info(f"Image downloaded, size: {len(image_bytes)} bytes, type: {content_type}")
        except Exception as e:
            logger.error(f"Failed to download input image: {e}")
            raise
        
        # Vertex AI expects the image as inline base64 data
        payload = {
            "contents": [{
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    },
                    {
                        "inline_data": {
                            "mime_type": content_type,
                            "data": image_data
                        }
                    }
                ]
            }],
            "generation_config": {
                "temperature": 0.4,
                "top_p": 1.0,
                "top_k": 32,
                "max_output_tokens": 2048,
            }
        }
        
        try:
            if self.use_vertex_ai:
                # Vertex AI: Use OAuth token
                from google.auth.transport.requests import Request
                
                # Refresh token if needed
                if not self.credentials.valid:
                    self.credentials.refresh(Request())
                
                access_token = self.credentials.token
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                logger.info(f"Calling Vertex AI Gemini 2.5 Flash + Imagen: {endpoint}")
                
                async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
                    response = await client.post(endpoint, json=payload)
                    response.raise_for_status()
                    result = response.json()
            else:
                # Generative Language API: Use API key
                endpoint_with_key = f"{endpoint}?key={self.api_key}"
                logger.info(f"Calling Generative Language API: {endpoint}")
                
                headers = {"Content-Type": "application/json"}
                async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
                    response = await client.post(endpoint_with_key, json=payload)
                    response.raise_for_status()
                    result = response.json()
            
            logger.info(f"Gemini API response received")
            
            # Extract the generated content from Gemini response
            # Response format: {"candidates": [{"content": {"parts": [{"text": "..." or "inlineData": {"data": "base64..."}}]}}]}
            # For Gemini 2.5 Flash Image, the response includes generated images as inlineData
            generated_images = []
            if "candidates" in result:
                for candidate in result["candidates"]:
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "inlineData" in part and "data" in part["inlineData"]:
                                # Store the base64 image data
                                generated_images.append(part["inlineData"]["data"])
                                logger.info(f"Found generated image in response (size: {len(part['inlineData']['data'])} chars)")
            
            return {
                "job_id": f"gemini_{uuid.uuid4().hex[:12]}",
                "status": "completed",
                "generated_images": generated_images,  # List of base64 encoded images
                "result": result
            }
        except httpx.HTTPError as e:
            logger.error(f"Failed to create Nano Banana job: {e}")
            if hasattr(e, 'response'):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            raise
    
    async def get_job_status(self, job_id: str) -> Dict:
        """Get the status of a generation job."""
        # Mock mode - simulate completed job with generated image
        if self.mode == "mock":
            logger.info(f"[MOCK] Checking status for job {job_id}")
            # Generate a mock image and return as base64
            mock_image_bytes = self._generate_mock_image(
                prompt="Mock generation",
                mode="mock",
                job_id=job_id
            )
            import base64
            mock_image_base64 = base64.b64encode(mock_image_bytes).decode('utf-8')
            
            return {
                "job_id": job_id,
                "status": "completed",
                "generated_images": [mock_image_base64],
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
        # Mock mode - simulate realistic generation time (20-30 seconds for testing auto-refresh)
        if self.mode == "mock":
            generation_time = random.uniform(20, 30)
            logger.info(f"[MOCK] Simulating generation for {generation_time:.1f} seconds")
            await asyncio.sleep(generation_time)
            return await self.get_job_status(job_id)
        
        # For Gemini, the job completes immediately (synchronous API)
        # The generated images are already in the response from create_job
        # Just return success status - the actual images are handled by create_job
        logger.info(f"Gemini job {job_id} completed (synchronous generation)")
        return {
            "job_id": job_id,
            "status": "completed"
        }
    
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
