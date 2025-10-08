from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import Response
from PIL import Image
import io
import logging
import pillow_heif
from pillow_heif import register_heif_opener

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate")
async def generate_preview(file: UploadFile = File(...)):
    """Generate a JPEG preview from an uploaded image (including HEIC)."""
    # Register HEIF opener (safe to call multiple times)
    register_heif_opener()
    
    try:
        logger.info(f"Preview request - filename: {file.filename}, content_type: {file.content_type}")
        logger.info(f"Registered HEIC extensions: {[ext for ext in Image.registered_extensions() if 'heic' in ext.lower() or 'heif' in ext.lower()]}")
        
        # Read file content
        file_content = await file.read()
        logger.info(f"File read - size: {len(file_content)} bytes")
        
        # Check if it's a HEIC/HEIF file by extension
        is_heif = file.filename and (file.filename.lower().endswith('.heic') or file.filename.lower().endswith('.heif'))
        
        # Register HEIF support
        register_heif_opener()
        
        # Open image - PIL will handle HEIC after registration
        image_stream = io.BytesIO(file_content)
        
        if is_heif:
            logger.info("Opening HEIC file with pillow_heif.open_heif()...")
            try:
                # Try using pillow_heif.open_heif() which is more forgiving
                heif_file = pillow_heif.open_heif(file_content, convert_hdr_to_8bit=False, bgr_mode=False)
                logger.info(f"HEIC file opened - Size: {heif_file.size}, Mode: {heif_file.mode}")
                
                # Convert to PIL Image
                img = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    'raw'
                )
                logger.info(f"HEIC converted to PIL Image successfully")
            except Exception as e:
                logger.error(f"Failed to decode HEIC with open_heif: {e}")
                # Last resort: Try with PIL + registered opener
                try:
                    image_stream.seek(0)
                    img = Image.open(image_stream)
                    img.load()
                    logger.info(f"HEIC opened with PIL fallback - Format: {img.format}, Mode: {img.mode}")
                except Exception as e2:
                    logger.error(f"PIL fallback also failed: {e2}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot decode this HEIC file. It may be corrupted or use an unsupported format."
                    )
        else:
            # For other formats
            img = Image.open(image_stream)
        
        with img:
            # Convert to RGB if necessary (HEIC might be in different mode)
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Resize for preview (max 800px on longest side)
            max_size = 800
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to JPEG
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return Response(
                content=output.read(),
                media_type="image/jpeg"
            )
            
    except Exception as e:
        logger.error(f"Failed to generate preview: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate preview: {str(e)}"
        )
