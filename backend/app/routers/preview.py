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
                # Use low-level _pillow_heif API to bypass strict metadata validation
                import _pillow_heif
                heif_ctx = _pillow_heif.load_file(file_content)
                logger.info(f"HEIC context loaded - images count: {heif_ctx.images_count}")
                
                # Get first image
                if heif_ctx.images_count > 0:
                    # Decode the first image
                    heif_ctx.decode_image(0)
                    img_data = heif_ctx.get_image_data(0)
                    
                    logger.info(f"HEIC decoded - Size: {img_data['width']}x{img_data['height']}, Mode: {img_data['mode']}")
                    
                    # Convert to PIL Image
                    img = Image.frombytes(
                        img_data['mode'],
                        (img_data['width'], img_data['height']),
                        img_data['data'],
                        'raw'
                    )
                    logger.info(f"HEIC converted to PIL Image successfully")
                else:
                    raise ValueError("No images found in HEIC file")
            except Exception as e:
                logger.error(f"Failed to decode HEIC with low-level API: {e}")
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
