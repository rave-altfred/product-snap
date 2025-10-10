# Storage Configuration Guide

## Overview

ProductSnap uses S3-compatible object storage for storing uploaded images, generated results, and thumbnails. The application supports two storage backends:

1. **MinIO** (for local development)
2. **Digital Ocean Spaces** (for production)

Both use the same S3 API, making the code environment-agnostic.

---

## Local Development (MinIO)

### What is MinIO?
MinIO is a high-performance, S3-compatible object storage server that runs in a Docker container. It's perfect for local development because:
- ✅ Free and open-source
- ✅ No cloud costs
- ✅ Identical S3 API to production
- ✅ Easy to reset and test

### Configuration

**docker-compose.yml** includes MinIO service:
```yaml
minio:
  image: minio/minio:latest
  ports:
    - "9000:9000"  # API
    - "9001:9001"  # Console
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin
```

**Local .env:**
```bash
# MinIO runs inside Docker network
S3_ENDPOINT=http://minio:9000

# Browser needs localhost to access signed URLs
S3_PUBLIC_ENDPOINT=http://localhost:9000

S3_BUCKET=productsnap
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_REGION=us-east-1
```

### Access MinIO Console

Visit: **http://localhost:9001**
- Username: `minioadmin`
- Password: `minioadmin`

Here you can:
- Browse uploaded files
- View bucket contents
- Manage access policies
- Monitor storage usage

---

## Production (Digital Ocean Spaces)

### What is Digital Ocean Spaces?
Digital Ocean Spaces is a scalable, S3-compatible object storage service. Benefits:
- ✅ Scalable and reliable
- ✅ CDN integration available
- ✅ Predictable pricing ($5/month for 250GB)
- ✅ S3-compatible API

### Setup

1. **Create a Space** in Digital Ocean:
   - Go to Spaces in DO dashboard
   - Click "Create Space"
   - Choose region (e.g., `fra1`, `nyc3`)
   - Name it (e.g., `productsnap-storage`)
   - Set to **Private** (files accessed via signed URLs)

2. **Generate API Keys**:
   - Go to API → Spaces Keys
   - Click "Generate New Key"
   - Save the Access Key and Secret Key

3. **Configure Environment**:

**Production .env:**
```bash
# Both internal and public use the same HTTPS endpoint
S3_ENDPOINT=https://fra1.digitaloceanspaces.com
S3_PUBLIC_ENDPOINT=https://fra1.digitaloceanspaces.com

S3_BUCKET=productsnap-storage
S3_ACCESS_KEY=YOUR_SPACES_ACCESS_KEY
S3_SECRET_KEY=YOUR_SPACES_SECRET_KEY
S3_REGION=fra1  # or your region: nyc3, sfo3, etc.
```

### Regional Endpoints

| Region | Endpoint |
|--------|----------|
| Frankfurt | `https://fra1.digitaloceanspaces.com` |
| New York | `https://nyc3.digitaloceanspaces.com` |
| San Francisco | `https://sfo3.digitaloceanspaces.com` |
| Singapore | `https://sgp1.digitaloceanspaces.com` |
| Amsterdam | `https://ams3.digitaloceanspaces.com` |

Choose the region closest to your users for best performance.

---

## How It Works

### Storage Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Application Code (Same for Both Environments)          │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Uses S3 API
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼───────┐  ┌──────▼──────────┐
│  Local Dev    │  │   Production    │
│               │  │                 │
│  MinIO        │  │  DO Spaces      │
│  localhost    │  │  Cloud          │
│  :9000        │  │  Storage        │
└───────────────┘  └─────────────────┘
```

### Signed URLs

Files are stored **privately** for security. When the frontend needs to display an image:

1. Frontend requests job details from API
2. Backend generates **signed URLs** (temporary, expiring links)
3. Frontend uses signed URL to load image
4. URL expires after 1 hour (configurable)

**Why Two Endpoints?**

- `S3_ENDPOINT`: Used by backend to **upload** files (internal Docker network)
- `S3_PUBLIC_ENDPOINT`: Used to **generate signed URLs** (accessible from browser)

For local development:
- Backend uses `http://minio:9000` (Docker network)
- Browser uses `http://localhost:9000` (host machine)

For production:
- Both use same HTTPS endpoint
- `S3_PUBLIC_ENDPOINT` defaults to `S3_ENDPOINT` if not set

---

## Storage Structure

```
productsnap/
├── uploads/
│   └── {uuid}/
│       └── original_filename.jpg
├── results/
│   └── {uuid}/
│       └── result_{uuid}.png
└── thumbnails/
    └── {uuid}/
        └── thumb_{uuid}.png
```

Files are organized by:
- **Folder**: Type of file (uploads, results, thumbnails)
- **UUID Subfolder**: Prevents naming conflicts
- **Filename**: Descriptive name with UUID

---

## Configuration Reference

### Environment Variables

| Variable | Description | Local | Production |
|----------|-------------|-------|------------|
| `S3_ENDPOINT` | Internal S3 endpoint | `http://minio:9000` | `https://fra1.digitaloceanspaces.com` |
| `S3_PUBLIC_ENDPOINT` | Public endpoint for signed URLs | `http://localhost:9000` | Same as S3_ENDPOINT |
| `S3_BUCKET` | Bucket/Space name | `productsnap` | `productsnap-storage` |
| `S3_ACCESS_KEY` | Access key | `minioadmin` | Your Spaces key |
| `S3_SECRET_KEY` | Secret key | `minioadmin` | Your Spaces secret |
| `S3_REGION` | Region code | `us-east-1` | `fra1`, `nyc3`, etc. |

### Code Configuration

**storage_service.py** handles both environments:

```python
class StorageService:
    def __init__(self):
        # Internal client for uploads (uses S3_ENDPOINT)
        self.s3_client = boto3.client('s3', 
            endpoint_url=settings.S3_ENDPOINT,
            ...
        )
        
        # Public client for signed URLs (uses S3_PUBLIC_ENDPOINT)
        if settings.S3_PUBLIC_ENDPOINT:
            self.public_s3_client = boto3.client('s3',
                endpoint_url=settings.S3_PUBLIC_ENDPOINT,
                ...
            )
        else:
            # Fallback to same client
            self.public_s3_client = self.s3_client
```

---

## Troubleshooting

### Images Not Displaying Locally

**Symptom**: Job completes but no image shows

**Solution**: Check `S3_PUBLIC_ENDPOINT` is set to `http://localhost:9000`

```bash
# Verify environment variable
docker exec productsnap-backend env | grep S3_PUBLIC_ENDPOINT

# Should output:
# S3_PUBLIC_ENDPOINT=http://localhost:9000
```

### 403 Forbidden on Signed URLs

**Symptom**: Signed URL returns 403 error

**Solution**: Check credentials and bucket permissions

```bash
# For MinIO: Check bucket exists
docker exec productsnap-backend python -c "
from app.services.storage_service import storage_service
print(storage_service.s3_client.list_buckets())
"

# For Spaces: Verify API keys are correct
```

### Connection Refused to MinIO

**Symptom**: `Connection refused to minio:9000`

**Solution**: MinIO service not running

```bash
# Start MinIO
docker compose up -d minio

# Check health
docker compose ps minio
```

### Slow Image Loading in Production

**Symptom**: Images take long to load

**Solution**: Enable CDN on Digital Ocean Spaces

1. Go to your Space settings
2. Enable CDN
3. Update `S3_PUBLIC_ENDPOINT` to CDN URL:
   ```bash
   S3_PUBLIC_ENDPOINT=https://your-space-name.fra1.cdn.digitaloceanspaces.com
   ```

---

## Migration Guide

### Moving from Local to Production

1. **Export test data** (optional):
   ```bash
   # Backup MinIO data
   docker exec productsnap-minio mc mirror /data/productsnap ./backup
   ```

2. **Set up Digital Ocean Space**:
   - Create Space
   - Generate API keys

3. **Update production .env**:
   ```bash
   S3_ENDPOINT=https://fra1.digitaloceanspaces.com
   S3_PUBLIC_ENDPOINT=https://fra1.digitaloceanspaces.com
   S3_BUCKET=productsnap-storage
   S3_ACCESS_KEY=your_key
   S3_SECRET_KEY=your_secret
   S3_REGION=fra1
   ```

4. **Deploy**:
   ```bash
   # Rebuild with new config
   docker compose -f droplet/docker-compose.prod.yml up -d --build
   ```

### Import Data to Spaces (if needed)

```bash
# Install AWS CLI or mc (MinIO Client)
pip install awscli

# Configure for Spaces
aws configure set aws_access_key_id YOUR_KEY
aws configure set aws_secret_access_key YOUR_SECRET

# Upload
aws s3 sync ./backup s3://productsnap-storage \
  --endpoint-url https://fra1.digitaloceanspaces.com
```

---

## Cost Comparison

### Local Development (MinIO)
- **Cost**: $0
- **Storage**: Limited by disk space
- **Performance**: Local (very fast)
- **Use case**: Development and testing

### Production (DO Spaces)
- **Cost**: $5/month for 250GB storage + 1TB transfer
- **Storage**: Scalable
- **Performance**: CDN-enabled (fast globally)
- **Use case**: Production workloads

### Pricing Calculator

| Users/Month | Images/User | Storage Needed | Monthly Cost |
|-------------|-------------|----------------|--------------|
| 100 | 10 | ~10GB | $5 |
| 500 | 10 | ~50GB | $5 |
| 1000 | 10 | ~100GB | $5 |
| 5000 | 10 | ~500GB | $10 |

---

## Best Practices

### Security

1. ✅ **Private Buckets**: Always keep buckets/spaces private
2. ✅ **Signed URLs**: Use expiring signed URLs (default: 1 hour)
3. ✅ **Rotate Keys**: Periodically rotate API keys
4. ✅ **CORS**: Configure CORS only for your domain in production

### Performance

1. ✅ **Thumbnails**: Always generate and use thumbnails for listings
2. ✅ **CDN**: Enable CDN in production for faster loading
3. ✅ **Cleanup**: Implement cleanup for old/unused files
4. ✅ **Compression**: Store images in optimized formats (WebP, PNG)

### Monitoring

1. 📊 **Track Storage**: Monitor bucket size growth
2. 📊 **Track Bandwidth**: Monitor transfer usage
3. 📊 **Track Costs**: Set up billing alerts
4. 📊 **Track Errors**: Log failed uploads/downloads

---

## Summary

| Feature | Local (MinIO) | Production (Spaces) |
|---------|---------------|---------------------|
| **Cost** | Free | $5+/month |
| **Setup** | Docker Compose | DO Dashboard |
| **API** | S3-compatible | S3-compatible |
| **Access** | localhost:9000 | HTTPS endpoint |
| **Performance** | Local disk | CDN-enabled |
| **Scalability** | Limited | Unlimited |
| **Best For** | Development | Production |

Both use the **same application code** - just change environment variables! 🎉
