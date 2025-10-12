# Nano Banana (Gemini 2.5 Flash + Imagen 3) Deployment Guide

## Overview

Nano Banana uses Google's **Gemini 2.5 Flash + Imagen 3** via **Vertex AI** for AI-powered product photography generation.

## Local Development Setup ✅ COMPLETE

You've already completed local setup with Application Default Credentials (ADC).

**Current Configuration:**
- API: Vertex AI
- Model: `gemini-2.5-flash-image`
- Project: `gen-lang-client-0509931710`
- Auth: Application Default Credentials (ADC) mounted from `~/.config/gcloud`

## Production Deployment (Droplet)

For production on your DigitalOcean droplet, you have two options:

### Option 1: Use ADC on Droplet (Recommended)

Run these commands **on your droplet** after deployment:

```bash
# SSH into droplet
ssh root@YOUR_DROPLET_IP

# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate
gcloud auth login
gcloud config set project gen-lang-client-0509931710
gcloud auth application-default login

# This creates: ~/.config/gcloud/application_default_credentials.json
```

### Option 2: Copy Credentials from Local (Quick Setup)

Copy your local credentials to the droplet:

```bash
# From your local machine
scp -r ~/.config/gcloud root@YOUR_DROPLET_IP:/root/.config/

# Then SSH into droplet and set permissions
ssh root@YOUR_DROPLET_IP
chmod -R 755 /root/.config/gcloud
chmod 600 /root/.config/gcloud/application_default_credentials.json
```

## Production Environment Variables

Add these to `droplet/.env.production`:

```bash
# Nano Banana (Gemini 2.5 Flash + Imagen 3)
NANO_BANANA_API_KEY=AIzaSyAYXtSBwW3MBh_Kjax8H73q79WOhtK5-yo
NANO_BANANA_API_URL=https://generativelanguage.googleapis.com
GOOGLE_CLOUD_PROJECT_ID=gen-lang-client-0509931710
USE_VERTEX_AI=true
IMAGE_GENERATION_MODE=live
```

## Production Docker Compose

Update `droplet/docker-compose.prod.yml` worker service to mount credentials:

```yaml
  worker:
    image: ${REGISTRY}/${REGISTRY_NAMESPACE}/${PROJECT_NAME}-worker:${TAG}
    restart: unless-stopped
    command: python -m app.worker
    volumes:
      - /root/.config/gcloud:/home/appuser/.config/gcloud:ro  # Mount gcloud credentials
    environment:
      GOOGLE_APPLICATION_CREDENTIALS: /home/appuser/.config/gcloud/application_default_credentials.json
      # ... other environment variables
```

## Deploy to Production

```bash
# 1. Update production environment file
nano droplet/.env.production  # Add the variables above

# 2. Update docker-compose.prod.yml (add volumes section to worker)
nano droplet/docker-compose.prod.yml

# 3. Build and deploy
./droplet/build.sh
./droplet/push.sh
./droplet/deploy.sh

# 4. Setup auth on droplet (Option 1 or 2 above)

# 5. Restart worker to pick up credentials
ssh root@YOUR_DROPLET_IP 'cd /opt/product-snap && docker compose restart worker'
```

## Verify Production Setup

```bash
# Check worker logs for Vertex AI initialization
ssh root@YOUR_DROPLET_IP 'cd /opt/product-snap && docker compose logs worker | grep "Vertex AI"'

# Expected output:
# "Using Vertex AI with project: gen-lang-client-0509931710"
# "NanoBananaClient initialized in live mode (Vertex AI: True)"

# Test a generation through the web interface
# Monitor worker logs:
ssh root@YOUR_DROPLET_IP 'cd /opt/product-snap && docker compose logs -f worker'
```

## Troubleshooting

### "File application_default_credentials.json was not found"

**Solution:** Mount path is incorrect or credentials not set up on droplet.

```bash
# Check if file exists on droplet
ssh root@YOUR_DROPLET_IP 'ls -la /root/.config/gcloud/application_default_credentials.json'

# If not found, run Option 1 or 2 setup above
```

### "Failed to initialize Vertex AI auth"

**Solution:** Credentials might be expired or have wrong permissions.

```bash
# Re-authenticate on droplet
ssh root@YOUR_DROPLET_IP
gcloud auth application-default login
docker compose restart worker
```

### "401 Unauthorized" from Vertex AI

**Solution:** Token expired or wrong project.

```bash
# Refresh credentials
ssh root@YOUR_DROPLET_IP
gcloud auth application-default login
gcloud config set project gen-lang-client-0509931710
docker compose restart worker
```

### "Worker falls back to API key mode"

**Solution:** Vertex AI auth failed, check logs for details.

```bash
ssh root@YOUR_DROPLET_IP 'cd /opt/product-snap && docker compose logs worker | grep -A 5 "Failed to initialize"'
```

## Switching Between Modes

### Use Vertex AI (Production - Image Generation)
```bash
USE_VERTEX_AI=true
IMAGE_GENERATION_MODE=live
```

### Use Generative Language API (Fallback - Text/Vision Only)
```bash
USE_VERTEX_AI=false
IMAGE_GENERATION_MODE=live
```

### Use Mock Mode (Development)
```bash
IMAGE_GENERATION_MODE=mock
```

## Cost Considerations

**Vertex AI Pricing (Gemini 2.5 Flash + Imagen 3):**
- Text input: ~$0.075 per 1M tokens
- Image input: ~$0.30 per 1M tokens
- Image output: ~$0.05 per image (1024x1024)

**Estimate:** ~$0.10-0.20 per product photo generation

## Security Notes

1. **Never commit** `application_default_credentials.json` to git
2. **Credentials auto-refresh** - tokens are valid for 1 hour but refresh automatically
3. **Least privilege** - The authenticated user should only have Vertex AI User role
4. **Monitor usage** - Check Google Cloud Console for API usage and costs

## Support

- **Google Cloud Console:** https://console.cloud.google.com/
- **Vertex AI Documentation:** https://cloud.google.com/vertex-ai/docs
- **Project ID:** gen-lang-client-0509931710
- **Model:** gemini-2.5-flash-image

## Next Steps

1. ✅ Local development is working
2. ⏳ Deploy to production droplet
3. ⏳ Set up auth on droplet  
4. ⏳ Test image generation
5. ⏳ Monitor costs and performance
