# LightClick Studio - App Platform Deployment Guide

## Overview

This guide covers deploying LightClick Studio to DigitalOcean App Platform using pre-built Docker images from DigitalOcean Container Registry (DOCR).

**Architecture:**
- **Backend** (FastAPI) - $5/month
- **Frontend** (React/Vite static site) - $3/month
- **Worker** (Background job processor) - $5/month
- **Managed PostgreSQL** - $15/month
- **Managed Valkey (Redis)** - $15/month
- **Total: $48/month**

---

## Prerequisites

1. **DigitalOcean CLI (doctl)**
   ```bash
   brew install doctl
   doctl auth init
   ```

2. **Docker** for building images
   ```bash
   docker --version
   ```

3. **Managed Databases** (or create them):
   - PostgreSQL database
   - Valkey (Redis) database

4. **Container Registry**
   - Already configured: `productsnap-registry`

---

## Quick Start

### 1. Build and Push Images

```bash
# Navigate to app-platform directory
cd app-platform

# Build and push all images to DOCR
./build-and-push.sh productsnap-registry latest
```

This will build and push:
- `registry.digitalocean.com/productsnap-registry/lightclick-backend:latest`
- `registry.digitalocean.com/productsnap-registry/lightclick-worker:latest`
- `registry.digitalocean.com/productsnap-registry/lightclick-frontend:latest`

### 2. Create Managed Valkey Database

If you don't have Managed Valkey yet:

```bash
# Create Valkey cluster (Basic, 1GB)
doctl databases create lightclick-valkey \
  --engine redis \
  --region fra1 \
  --size db-s-1vcpu-1gb \
  --num-nodes 1

# Get connection details
doctl databases get <database-id>
doctl databases connection <database-id>
```

**Note the connection string** - you'll need it for environment variables.

Format: `rediss://username:password@host:25061/0?ssl_cert_reqs=required`

### 3. Get Database Connection Strings

**PostgreSQL:**
```bash
# If you have existing database
doctl databases get <postgres-db-id>
doctl databases connection <postgres-db-id>
```

**Valkey:**
```bash
doctl databases get <valkey-db-id>
doctl databases connection <valkey-db-id>
```

### 4. Create App Platform App

**Option A: Using deployment script (Recommended)**

```bash
# Validate and create app
./deploy.sh create

# App ID is automatically saved to .do/app-id.txt
```

**Option B: Using doctl directly**

```bash
# Create app from spec
doctl apps create --spec .do/app.yaml

# Note the App ID returned
export APP_ID=<your-app-id>
```

### 5. Configure Environment Variables

**Note:** The `app.yaml` already includes all environment variables with production values. If you need to change them:

**Method 1: Edit app.yaml (Recommended)**

Edit `.do/app.yaml` and update the `envs:` section at the app level, then:

```bash
./deploy.sh update
```

**Method 2: Via doctl CLI**

```bash
# Database connections (REQUIRED)
doctl apps update $APP_ID \
  --env="DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=require" \
  --env="REDIS_URL=rediss://default:pass@host:25061/0?ssl_cert_reqs=required"

# JWT Secret (REQUIRED)
doctl apps update $APP_ID \
  --env="JWT_SECRET=$(openssl rand -base64 32)"

# S3/Spaces (REQUIRED)
doctl apps update $APP_ID \
  --env="S3_ENDPOINT=https://nyc3.digitaloceanspaces.com" \
  --env="S3_BUCKET=your-bucket-name" \
  --env="S3_ACCESS_KEY=your-access-key" \
  --env="S3_SECRET_KEY=your-secret-key" \
  --env="S3_PUBLIC_ENDPOINT=https://your-bucket.nyc3.digitaloceanspaces.com"

# PayPal (REQUIRED)
doctl apps update $APP_ID \
  --env="PAYPAL_CLIENT_ID=your-client-id" \
  --env="PAYPAL_CLIENT_SECRET=your-client-secret" \
  --env="PAYPAL_PLAN_ID_BASIC_MONTHLY=P-xxx" \
  --env="PAYPAL_PLAN_ID_BASIC_YEARLY=P-xxx" \
  --env="PAYPAL_PLAN_ID_PRO_MONTHLY=P-xxx" \
  --env="PAYPAL_PLAN_ID_PRO_YEARLY=P-xxx"

# Gemini API (REQUIRED)
doctl apps update $APP_ID \
  --env="NANO_BANANA_API_KEY=your-gemini-api-key"

# SMTP (REQUIRED)
doctl apps update $APP_ID \
  --env="SMTP_HOST=smtp.gmail.com" \
  --env="SMTP_USER=your-email@gmail.com" \
  --env="SMTP_PASSWORD=your-app-password" \
  --env="SMTP_FROM_EMAIL=your-email@gmail.com"

# Google OAuth (OPTIONAL)
doctl apps update $APP_ID \
  --env="GOOGLE_CLIENT_ID=your-client-id" \
  --env="GOOGLE_CLIENT_SECRET=your-client-secret" \
  --env="GOOGLE_REDIRECT_URI=https://your-app.ondigitalocean.app/api/auth/google/callback"
```

**Method 2: Via App Platform Console**

1. Go to: https://cloud.digitalocean.com/apps
2. Click your app → Settings → App-Level Environment Variables
3. Add each variable (check "Encrypt" for secrets)

### 6. Deploy & Monitor

**Using deployment script:**

```bash
# View deployment logs (follows in real-time)
./deploy.sh logs

# View build logs
./deploy.sh logs "" BUILD

# Get app info
./deploy.sh info
```

**Using doctl directly:**

```bash
# Trigger deployment
doctl apps create-deployment $APP_ID

# Monitor deployment
doctl apps get-deployment $APP_ID <deployment-id>
```

### 7. Run Database Migrations

After first deployment:

```bash
# Run migrations
doctl apps logs $APP_ID --type run backend
doctl apps exec $APP_ID backend -- alembic upgrade head
```

### 8. Verify Deployment

```bash
# Get app URL
doctl apps get $APP_ID --format DefaultIngress

# Test health endpoint
curl https://your-app.ondigitalocean.app/health
```

---

## Environment Variables Reference

See `environment-mapping.md` for complete list with descriptions.

**Required Secrets:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Valkey connection string with TLS
- `JWT_SECRET` - Random 32+ character string
- `S3_ACCESS_KEY`, `S3_SECRET_KEY` - Spaces credentials
- `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET` - PayPal API keys
- `NANO_BANANA_API_KEY` - Gemini API key
- `SMTP_PASSWORD` - Email password

---

## Deployment Scripts

### Available Commands

**build-and-push.sh** - Build and push Docker images
```bash
./build-and-push.sh <registry-name> <tag>

# Example
./build-and-push.sh productsnap-registry v1.2.0
```

**deploy.sh** - Deploy and manage apps
```bash
./deploy.sh create              # Create new app
./deploy.sh update [app-id]     # Update app (auto-detects ID)
./deploy.sh list                # List all apps
./deploy.sh info [app-id]       # Get app info
./deploy.sh logs [app-id] [type] # View logs (BUILD|DEPLOY|RUN)
./deploy.sh validate            # Validate app.yaml
```

### Complete Deployment Workflow

```bash
# 1. Build and push new images
./build-and-push.sh productsnap-registry latest

# 2. Deploy update
./deploy.sh update

# 3. Monitor deployment
./deploy.sh logs
```

---

## Updating the App

### Update Code

```bash
# 1. Build new images
./build-and-push.sh productsnap-registry latest

# 2. Trigger new deployment (pulls latest images)
./deploy.sh update
```

### Update Configuration

**Using deployment script:**

```bash
# Edit .do/app.yaml, then:
./deploy.sh update
```

**Using doctl:**

```bash
# Update environment variable
doctl apps update $APP_ID --env="KEY=new-value"

# Update app spec
doctl apps update $APP_ID --spec .do/app.yaml
```

### Update Database Schema

```bash
# Run new migrations
doctl apps exec $APP_ID backend -- alembic upgrade head
```

---

## Monitoring

### View Logs

```bash
# All services
doctl apps logs $APP_ID --type build
doctl apps logs $APP_ID --type deploy
doctl apps logs $APP_ID --type run

# Specific service
doctl apps logs $APP_ID --type run backend
doctl apps logs $APP_ID --type run worker
doctl apps logs $APP_ID --type run frontend

# Follow logs
doctl apps logs $APP_ID --type run backend --follow
```

### Check Status

```bash
# App status
doctl apps get $APP_ID

# Deployment status
doctl apps list-deployments $APP_ID

# Service health
curl https://your-app.ondigitalocean.app/health
```

### Metrics

View in console: https://cloud.digitalocean.com/apps → Your App → Insights

---

## Troubleshooting

### Deployment Fails

```bash
# Check build logs
doctl apps logs $APP_ID --type build

# Check deployment logs
doctl apps logs $APP_ID --type deploy
```

**Common issues:**
- Missing environment variables
- Invalid database connection string
- Registry authentication failed

### Service Won't Start

```bash
# Check runtime logs
doctl apps logs $APP_ID --type run backend --tail 100

# Check health endpoint
curl https://your-app.ondigitalocean.app/health
```

**Common issues:**
- Database connection failed (check `DATABASE_URL`)
- Redis connection failed (check `REDIS_URL` has `rediss://` with TLS)
- Missing required environment variables

### Worker Not Processing Jobs

```bash
# Check worker logs
doctl apps logs $APP_ID --type run worker --follow

# Check if worker is running
doctl apps get $APP_ID
```

**Common issues:**
- Redis connection issues
- Database connection issues
- Job queue not accessible

### Frontend Not Loading

```bash
# Check if static site is deployed
doctl apps get $APP_ID

# Check frontend logs
doctl apps logs $APP_ID --type run frontend
```

**Common issues:**
- Build failed (wrong `VITE_API_URL`)
- Routing issues (check ingress rules)

---

## Rolling Back

### Rollback to Previous Deployment

```bash
# List deployments
doctl apps list-deployments $APP_ID

# Rollback to specific deployment
doctl apps create-deployment $APP_ID --deployment-id <previous-deployment-id>
```

---

## Custom Domain

### Add Custom Domain

```bash
# Add domain via console or spec
# Update app.yaml and add:
# domains:
#   - domain: lightclick.studio
#     type: PRIMARY

# Apply changes
doctl apps update $APP_ID --spec app-platform/.do/app.yaml
```

### Update DNS

App Platform will provide DNS records to configure:
- A record or CNAME pointing to App Platform
- SSL certificate will be auto-provisioned

---

## Scaling

### Manual Scaling

Edit `app-platform/.do/app.yaml`:

```yaml
services:
  - name: backend
    instance_count: 2  # Scale to 2 instances
    instance_size_slug: basic-s  # Upgrade to 1GB RAM
```

Apply:
```bash
doctl apps update $APP_ID --spec app-platform/.do/app.yaml
```

### Auto-Scaling

Uncomment auto-scaling in `app.yaml`:

```yaml
services:
  - name: backend
    autoscaling:
      min_instance_count: 1
      max_instance_count: 3
      metrics:
        cpu:
          percent: 80
```

---

## Cost Optimization

### Current Setup
- Backend: $5/month (basic-xs)
- Frontend: $3/month (static site)
- Worker: $5/month (basic-xs)
- Valkey: $15/month
- PostgreSQL: $15/month
- **Total: $48/month**

### Reduce Costs

1. **Use smaller instances** (if sufficient):
   - Backend/Worker: Keep at basic-xs ($5 each)
   
2. **Optimize build minutes**:
   - Use DOCR (pre-built images) ✅ Already doing this
   - Free tier: 400 build minutes/month

3. **Monitor usage**:
   - Check bandwidth usage
   - Optimize image sizes
   - Use CDN caching (automatic for static site)

---

## Security

### Secrets Management

- All secrets encrypted by App Platform
- Never commit secrets to git
- Rotate secrets regularly

### Database Security

- Managed databases use private networking
- TLS/SSL enforced for connections
- Automatic backups enabled

### Network Security

- App Platform provides DDoS protection
- Automatic SSL/TLS termination
- Can restrict database access to App Platform

---

## Backup & Recovery

### Database Backups

```bash
# PostgreSQL - automatic daily backups
doctl databases backups list <postgres-db-id>

# Restore from backup
doctl databases restore <postgres-db-id> <backup-id>

# Valkey - automatic backups
doctl databases backups list <valkey-db-id>
```

### Application State

```bash
# Export environment variables
doctl apps get $APP_ID --format Spec > app-backup.yaml

# Export database
doctl databases connection <postgres-db-id>
pg_dump -h host -U user -d database > backup.sql
```

---

## Support

### DigitalOcean Support
- Documentation: https://docs.digitalocean.com/products/app-platform/
- Community: https://www.digitalocean.com/community
- Support tickets: https://cloud.digitalocean.com/support

### App Platform Limits
- Max apps per account: 100
- Max services per app: 50
- Max static sites per app: 10
- Max env vars: 200

---

## Useful Commands

```bash
# List all apps
doctl apps list

# Get app details
doctl apps get $APP_ID

# List services
doctl apps get $APP_ID --format Spec

# Restart service
doctl apps create-deployment $APP_ID

# Delete app
doctl apps delete $APP_ID

# Exec into container
doctl apps exec $APP_ID backend -- bash
```

---

## Next Steps

1. ✅ Deploy to staging first
2. ✅ Test all features thoroughly
3. ✅ Monitor for 24-48 hours
4. ✅ Deploy to production
5. ✅ Update DNS to point to App Platform
6. ✅ Keep droplet running for 1 week as backup
7. ✅ Decommission droplet after successful migration

---

**Last Updated:** 2025-10-13  
**App Platform Spec Version:** 1.0
