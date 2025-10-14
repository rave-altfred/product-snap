# Scaling Strategy for DigitalOcean App Platform

## Overview

The application is configured to scale in two ways:
1. **Horizontal Scaling**: Add more container instances (autoscaling)
2. **Vertical Scaling**: Use larger instance sizes with more workers per container

## How It Works

### Worker Configuration via Environment Variable

The backend uses the `WEB_CONCURRENCY` environment variable to configure uvicorn workers:

```dockerfile
# backend/Dockerfile
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${WEB_CONCURRENCY:-1}
```

This means:
- **No rebuild needed** when scaling up/down
- Same Docker image works for all instance sizes
- Configuration happens at runtime via environment variable

### Recommended Worker Counts by Instance Size

| Instance Size | RAM | vCPU | WEB_CONCURRENCY | Cost/Month |
|--------------|-----|------|-----------------|------------|
| apps-s-1vcpu-0.5gb | 512MB | 0.5 | **1** | $5 |
| apps-s-1vcpu-1gb | 1GB | 1 | **2** | $12 |
| apps-s-1vcpu-2gb | 2GB | 1 | **4** | $24 |
| apps-d-1vcpu-2gb | 2GB | 1 | **4** | $35 (dedicated) |

**Rule of thumb**: 1 worker per 512MB RAM

## Scaling Scenarios

### Scenario 1: Start Small (Current Setup)

```yaml
# .do/app.yaml
services:
  - name: backend
    instance_count: 1
    instance_size_slug: apps-s-1vcpu-0.5gb  # 512MB
    envs:
      - key: WEB_CONCURRENCY
        value: "1"
```

**Total capacity**: 1 worker  
**Cost**: $5/month

### Scenario 2: Horizontal Autoscaling (Recommended for Traffic Spikes)

```yaml
services:
  - name: backend
    instance_size_slug: apps-s-1vcpu-0.5gb  # 512MB
    envs:
      - key: WEB_CONCURRENCY
        value: "1"
    
    autoscaling:
      min_instance_count: 1
      max_instance_count: 3
      metrics:
        cpu:
          percent: 80  # Scale up when CPU > 80%
```

**Capacity range**: 1-3 workers (scales based on CPU load)  
**Cost**: $5-$15/month (pay only for active instances)

### Scenario 3: Vertical Scaling (More Power Per Instance)

```yaml
services:
  - name: backend
    instance_count: 1
    instance_size_slug: apps-s-1vcpu-2gb  # 2GB
    envs:
      - key: WEB_CONCURRENCY
        value: "4"  # 4 workers in single container
```

**Total capacity**: 4 workers  
**Cost**: $24/month

### Scenario 4: Combined Scaling (High Traffic Production)

```yaml
services:
  - name: backend
    instance_size_slug: apps-s-1vcpu-1gb  # 1GB
    envs:
      - key: WEB_CONCURRENCY
        value: "2"  # 2 workers per container
    
    autoscaling:
      min_instance_count: 2
      max_instance_count: 5
      metrics:
        cpu:
          percent: 75
```

**Capacity range**: 4-10 workers (2 per container × 2-5 containers)  
**Cost**: $24-$60/month

## How to Scale

### Option 1: Edit `.do/app.yaml` and Redeploy

1. Edit `app-platform/.do/app.yaml`:
   ```yaml
   # Change instance size
   instance_size_slug: apps-s-1vcpu-1gb
   
   # Update worker count accordingly
   envs:
     - key: WEB_CONCURRENCY
       value: "2"
   
   # Enable autoscaling (optional)
   autoscaling:
     min_instance_count: 1
     max_instance_count: 3
     metrics:
       cpu:
         percent: 80
   ```

2. Apply changes:
   ```bash
   ./app-platform/deploy.sh deploy
   ```

### Option 2: Use `doctl` CLI Directly

```bash
# Get app ID
APP_ID=$(doctl apps list --format ID --no-header)

# Update instance size
doctl apps update $APP_ID --spec app-platform/.do/app.yaml
```

## Monitoring Scaling Decisions

### Check Current Instance Count

```bash
doctl apps list-components <app-id> --format Name,Type,InstanceCount,InstanceSize
```

### Monitor Resource Usage

```bash
# View metrics dashboard
doctl apps logs <app-id> --type run --follow | grep -E "(CPU|Memory|Request)"

# Or use DO dashboard
# https://cloud.digitalocean.com/apps/<app-id>/metrics
```

### Analyze Load Patterns

Key metrics to watch:
- **Response time**: Should stay under 500ms for API calls
- **CPU usage**: Scale up if consistently above 80%
- **Memory usage**: Each worker uses ~150-200MB RAM
- **Request queue**: Check Redis queue length for job backlog

## Worker vs Instance Scaling

### When to Increase Workers (Vertical)

✅ **Use more workers per instance when:**
- You have consistent, predictable traffic
- Most requests are I/O bound (database, S3, external API calls)
- You want to minimize cold start delays
- Cost predictability is important

### When to Use Autoscaling (Horizontal)

✅ **Use instance autoscaling when:**
- Traffic is spiky or unpredictable
- You need burst capacity
- You want to minimize costs during low-traffic periods
- You need high availability (multiple instances for redundancy)

## Background Worker Scaling

The worker service handles background jobs (image generation). Scale it independently:

```yaml
workers:
  - name: worker
    instance_count: 1  # Start with 1
    instance_size_slug: apps-s-1vcpu-1gb  # More RAM for image processing
    
    # Optional: Enable autoscaling based on Redis queue length
    # (Note: App Platform autoscaling is currently CPU-based only)
```

**Manual worker scaling based on queue length:**

```bash
# Check queue depth
doctl apps logs <app-id> --type run --component worker | grep "Queue length"

# If queue is consistently >10, add more workers
# Edit app.yaml: instance_count: 2
./app-platform/deploy.sh deploy
```

## Cost Optimization Tips

1. **Start small**: Begin with 1 instance @ 512MB ($5/month)
2. **Enable autoscaling early**: Let App Platform scale based on actual demand
3. **Set max instance limits**: Prevent runaway scaling costs
4. **Monitor usage**: Review metrics weekly to right-size instances
5. **Use shared instances for dev**: Only use dedicated instances for production

## Testing Scaling Configuration

### Load Test Before Production

```bash
# Install hey (HTTP load generator)
brew install hey  # macOS

# Test with 100 concurrent users for 30 seconds
hey -z 30s -c 100 https://your-app.ondigitalocean.app/api/health

# Monitor autoscaling behavior
doctl apps list-components <app-id> --format InstanceCount
```

### Simulate Different Loads

```python
# test_load.py - Simulate realistic traffic
import concurrent.futures
import requests
import time

API_URL = "https://your-app.ondigitalocean.app/api"
CONCURRENT_REQUESTS = 50
DURATION_SECONDS = 60

def make_request():
    try:
        r = requests.get(f"{API_URL}/health", timeout=10)
        return r.status_code, r.elapsed.total_seconds()
    except Exception as e:
        return None, str(e)

with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
    start = time.time()
    while time.time() - start < DURATION_SECONDS:
        futures = [executor.submit(make_request) for _ in range(CONCURRENT_REQUESTS)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        time.sleep(1)
```

## Summary

✅ **No rebuild needed** - Docker image is the same for all scales  
✅ **Configure via environment** - Change `WEB_CONCURRENCY` in app.yaml  
✅ **Autoscaling ready** - Enable when traffic warrants it  
✅ **Cost-effective** - Start small, scale as needed  

Current setup: **1 worker @ 512MB = $5/month** (perfect for MVP/testing)
