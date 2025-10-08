# Image Generation Mode Configuration

## Overview

ProductSnap supports two modes for image generation: **Live** and **Mock**. This allows you to test the complete job flow without consuming API credits or requiring a valid Gemini API key.

## Configuration

Set the `IMAGE_GENERATION_MODE` environment variable in your `.env` file:

```bash
# For testing - simulates image generation
IMAGE_GENERATION_MODE=mock

# For production - uses real Gemini 2.5 Flash API
IMAGE_GENERATION_MODE=live
```

## Mock Mode

### When to Use
- **Local development** - Test the complete job workflow without API calls
- **Testing** - Verify job queue, status updates, and storage without costs
- **CI/CD pipelines** - Run automated tests without external dependencies
- **Debugging** - Isolate issues in your code vs. API issues

### How It Works
When `IMAGE_GENERATION_MODE=mock`:

1. **Job Creation**: Returns a mock job ID (e.g., `mock_a1b2c3d4e5f6`)
2. **Status Polling**: Immediately returns "completed" status
3. **Image Download**: Returns a minimal valid 1x1 PNG image
4. **Logging**: All mock operations are logged with `[MOCK]` prefix

### Mock Behavior
```python
# Job creation response
{
    "job_id": "mock_a1b2c3d4e5f6",
    "status": "queued",
    "created_at": "2025-10-08T08:35:30.123456"
}

# Status check response
{
    "job_id": "mock_a1b2c3d4e5f6",
    "status": "completed",
    "output_url": "https://mock-storage.example.com/results/mock_a1b2c3d4e5f6.png",
    "completed_at": "2025-10-08T08:35:30.123456"
}
```

### What Gets Tested
✅ Job submission to Redis queue  
✅ Worker job processing loop  
✅ Job status transitions (QUEUED → PROCESSING → COMPLETED)  
✅ S3 upload/download operations  
✅ Thumbnail generation  
✅ Email notifications  
✅ Rate limiting and usage tracking  

### What Gets Skipped
❌ Actual Gemini API calls  
❌ Real image generation  
❌ API credit consumption  

## Live Mode

### When to Use
- **Production** - Real user jobs
- **Staging** - Integration testing with real API
- **Quality validation** - Verify actual image generation quality

### Requirements
1. Valid Google Cloud API key with Gemini API enabled
2. Set `NANO_BANANA_API_KEY` to your actual API key
3. Ensure API quota and billing are configured

### Configuration
```bash
# .env file
NANO_BANANA_API_KEY=AIzaSy...your_actual_key
NANO_BANANA_API_URL=https://generativelanguage.googleapis.com/v1beta
IMAGE_GENERATION_MODE=live
```

### API Endpoint
The Gemini 2.5 Flash API endpoint is:
```
https://generativelanguage.googleapis.com/v1beta
```

## Switching Modes

### During Development
You can switch modes anytime by updating the env var and restarting services:

```bash
# Switch to mock mode
echo "IMAGE_GENERATION_MODE=mock" >> backend/.env
docker-compose restart backend worker

# Switch to live mode
echo "IMAGE_GENERATION_MODE=live" >> backend/.env
docker-compose restart backend worker
```

### Environment-Specific
Use different values per environment:

- **Local Development**: `mock`
- **CI/CD**: `mock`
- **Staging**: `live` (with test API key)
- **Production**: `live` (with production API key)

## Monitoring

Check which mode is active by looking at startup logs:

```bash
docker-compose logs worker | grep "NanoBananaClient"
```

Expected output:
```
worker_1  | NanoBananaClient initialized in mock mode
```

All mock operations are logged with `[MOCK]` prefix:
```
worker_1  | [MOCK] Created job mock_a1b2c3d4e5f6 for mode studio_white
worker_1  | [MOCK] Checking status for job mock_a1b2c3d4e5f6
worker_1  | [MOCK] Downloading result from https://mock-storage.example.com/...
```

## Troubleshooting

### "NanoBananaClient initialized in live mode" but I set mock mode
- The env var might not be loaded. Check `docker-compose.yml` env_file paths
- Restart services: `docker-compose restart backend worker`

### Mock mode still making API calls
- Verify the env var name is exactly `IMAGE_GENERATION_MODE` (case-sensitive)
- Check there are no typos in the value (`mock` not `Mock` or `mocked`)

### Worker fails in live mode with authentication error
- Verify `NANO_BANANA_API_KEY` is valid
- Check Google Cloud Console for API quota/billing
- Ensure Gemini API is enabled for your project

## Best Practices

1. **Always use mock mode for local development** unless testing API integration
2. **Set mock mode in CI/CD** to avoid API costs during testing
3. **Use live mode in staging** with a separate API key and quota
4. **Never commit live mode** to `.env.example` - default to mock
5. **Log all mode switches** for debugging and audit trails

## Related Files

- `backend/app/core/config.py` - Configuration definition
- `backend/app/services/nano_banana_client.py` - Mock implementation
- `backend/app/worker.py` - Job processing with NanoBananaClient
- `.env.example` - Default configuration template
