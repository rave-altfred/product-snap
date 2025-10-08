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
            logger.info("Opening HEIC file with registered PIL opener...")
            try:
                # Try opening with PIL Image directly
                img = Image.open(image_stream)
                # Force load to catch any issues early
                img.load()
                logger.info(f"HEIC opened successfully - Format: {img.format}, Mode: {img.mode}, Size: {img.size}")
            except Exception as e:
                logger.error(f"Failed to open HEIC with PIL: {e}")
                # Last resort: try to extract first frame using pillow_heif low-level API
                try:
                    import _pillow_heif
                    # Try to read with minimal validation
                    heif = _pillow_heif.HeifFile(file_content)
                    # Get first image
                    data = heif.to_bytes()
                    img = Image.frombytes(heif.mode, heif.size, data, 'raw')
                    logger.info("HEIC decoded using low-level _pillow_heif API")
                except Exception as e2:
                    logger.error(f"Low-level decode also failed: {e2}")
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
