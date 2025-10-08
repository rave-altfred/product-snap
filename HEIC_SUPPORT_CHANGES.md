# HEIC/HEIF Image Format Support

## Overview
Added support for HEIC/HEIF image formats uploaded from newer mobile devices (iPhone 7 and later).

## Changes Made

### 1. Backend Dependencies
- **File**: `backend/requirements.txt`
- **Change**: Added `pillow-heif==0.13.1` to enable HEIC/HEIF format decoding with Pillow

### 2. Configuration
- **File**: `backend/app/core/config.py`
- **Change**: Updated `ALLOWED_IMAGE_TYPES` to include `"image/heic"` and `"image/heif"`

### 3. Image Validation
- **File**: `backend/app/routers/jobs.py`
- **Changes**:
  - Updated `format_mime_mapping` dictionary to include HEIF format
  - Modified MIME type validation logic to handle both single MIME types and lists (for HEIF which can have multiple MIME types)

### 4. Application Initialization
- **File**: `backend/app/main.py`
- **Change**: Added import and registration of `pillow_heif.register_heif_opener()` at application startup

### 5. Worker Process
- **File**: `backend/app/worker.py`
- **Change**: Added import and registration of `pillow_heif.register_heif_opener()` for the background worker

### 6. Frontend UI
- **File**: `frontend/src/pages/NewShoot.tsx`
- **Change**: Updated file upload UI text to indicate support for HEIC/HEIF formats

## How It Works

1. **HEIF Plugin Registration**: The `pillow-heif` library is registered at startup in both the main API (`main.py`) and the worker process (`worker.py`), enabling Pillow to automatically decode HEIC/HEIF images.

2. **File Validation**: When a user uploads a HEIC/HEIF image:
   - The MIME type is validated against the allowed types list
   - Pillow opens and verifies the image format
   - The format is checked against the mapping to ensure it matches the declared MIME type

3. **Processing**: Once validated, HEIC/HEIF images are processed just like any other image format. Pillow can read them and convert them as needed for the AI processing pipeline.

## Deployment Notes

After deploying these changes, ensure:
1. The backend dependencies are reinstalled: `pip install -r backend/requirements.txt`
2. Both the API server and worker processes are restarted
3. The frontend is rebuilt and deployed

## Testing

To test HEIC/HEIF support:
1. Use an iPhone or iPad to take a photo (these devices save photos as HEIC by default)
2. Upload the photo through the web interface
3. Verify the upload succeeds and the job processes correctly

## Browser Compatibility

Note: While the backend now accepts HEIC/HEIF files, some older browsers may not be able to preview these images in the browser. The backend will still process them correctly and return results in standard formats (PNG/JPEG).
