# Deployment Scripts

This directory contains scripts for deploying ProductSnap to DigitalOcean droplets with optimized Docker builds and image management.

## 📁 Files

- **`build-and-deploy.sh`** - Main deployment script with BuildKit caching
- **`cleanup-images.sh`** - Docker image cleanup utility
- **`deploy.sh`** - Simple deployment script (existing)
- **`backup.sh`** - Database backup script (existing)

## 🚀 Quick Start

### Deploy to Droplet

```bash
# Full build and deploy
./build-and-deploy.sh --host your-droplet-ip

# With custom SSH user
./build-and-deploy.sh --host 123.45.67.89 --user productsnap --key ~/.ssh/mykey

# Skip build, deploy existing images
./build-and-deploy.sh --host 123.45.67.89 --skip-build

# Dry run (see what would happen)
./build-and-deploy.sh --host 123.45.67.89 --dry-run
```

### Clean Up Old Images

```bash
# Clean local images only
./cleanup-images.sh --local

# Clean remote droplet images
./cleanup-images.sh --remote --host 123.45.67.89

# Clean both local and remote
./cleanup-images.sh --both --host 123.45.67.89 --keep 3
```

## 📖 Detailed Usage

### build-and-deploy.sh

Complete build and deployment pipeline with the following features:

**Features:**
- ✅ BuildKit for faster builds with layer caching
- ✅ Multi-stage Docker builds for smaller production images
- ✅ Parallel image building where possible
- ✅ Automatic image tagging (timestamp + latest)
- ✅ Zero-downtime deployment
- ✅ Automatic database migrations
- ✅ Health checks after deployment
- ✅ Automatic cleanup of old images
- ✅ Rollback on failure

**Options:**
```
-h, --host      Droplet IP or hostname (required)
-u, --user      SSH user (default: root)
-p, --port      SSH port (default: 22)
-k, --key       SSH key path (default: ~/.ssh/id_rsa)
--no-cache      Build without Docker cache
--skip-build    Skip build phase, deploy existing images
--dry-run       Show commands without executing
--help          Show help message
```

**Example Workflows:**

```bash
# First deployment to new droplet
./build-and-deploy.sh --host 123.45.67.89 --user root

# Quick deploy after code changes (uses cache)
./build-and-deploy.sh --host 123.45.67.89

# Force rebuild without cache
./build-and-deploy.sh --host 123.45.67.89 --no-cache

# Deploy existing images (if already built)
./build-and-deploy.sh --host 123.45.67.89 --skip-build
```

**What It Does:**

1. **Prerequisites Check**
   - Verifies Docker and Docker Compose are installed
   - Checks Docker daemon is running
   - Enables BuildKit for faster builds

2. **SSH Connection Test**
   - Tests connection to droplet
   - Validates SSH key

3. **Build Phase** (unless --skip-build)
   - Builds backend image with production target
   - Builds frontend image with production target
   - Uses layer caching for faster subsequent builds
   - Tags images with timestamp and 'latest'
   - Compresses images to tar.gz for transfer

4. **Transfer Phase**
   - Creates deployment directory on droplet
   - Transfers image archives
   - Transfers docker-compose configuration
   - Transfers .env file (with warning)
   - Transfers nginx configuration

5. **Deploy Phase**
   - Loads images on droplet
   - Runs database migrations
   - Stops old containers gracefully
   - Starts new containers
   - Waits for services to be healthy
   - Performs health check

6. **Cleanup Phase**
   - Removes local tar.gz files
   - Removes old local Docker images
   - Keeps only 2 most recent versions
   - Removes dangling images

7. **Summary**
   - Shows deployment details
   - Provides helpful commands

### cleanup-images.sh

Standalone script for cleaning up Docker images on local machine and/or remote droplet.

**Features:**
- ✅ Clean local images
- ✅ Clean remote images via SSH
- ✅ Configurable retention (keep N most recent)
- ✅ Removes dangling images
- ✅ Dry-run mode to preview changes
- ✅ Shows disk space before/after

**Options:**
```
--local         Clean local images only (default)
--remote        Clean remote droplet images only
--both          Clean both local and remote
-h, --host      Droplet IP (required for remote)
-u, --user      SSH user (default: root)
-k, --key       SSH key path (default: ~/.ssh/id_rsa)
--keep N        Keep N most recent images (default: 2)
--dry-run       Show what would be deleted
--help          Show help
```

**Examples:**

```bash
# Clean local images (keep 2 most recent)
./cleanup-images.sh --local

# Clean local images (keep 5 most recent)
./cleanup-images.sh --local --keep 5

# Preview what would be deleted locally
./cleanup-images.sh --local --dry-run

# Clean remote droplet images
./cleanup-images.sh --remote --host 123.45.67.89

# Clean both local and remote
./cleanup-images.sh --both --host 123.45.67.89 --keep 3
```

**What It Cleans:**

- Old tagged images (keeps N most recent per repository)
- Dangling images (untagged, unused)
- Always keeps 'latest' tag

**What It Preserves:**

- The 'latest' tag for each repository
- The N most recent timestamped tags
- Images currently in use

## 🏗️ Docker Build Optimization

### Multi-Stage Builds

Both backend and frontend use multi-stage builds:

**Backend:**
```dockerfile
FROM python:3.11-slim as base
# Install system dependencies

FROM base as development
# Development dependencies and code

FROM base as production
# Production only, optimized
```

**Frontend:**
```dockerfile
FROM node:18-alpine as development
# Dev server

FROM node:18-alpine as build
# Build static assets

FROM nginx:alpine as production
# Serve static files
```

### Layer Caching Strategy

The build process uses several caching techniques:

1. **BuildKit**: Enabled by default for parallel layer processing
2. **Inline Cache**: `--build-arg BUILDKIT_INLINE_CACHE=1`
3. **Cache From**: `--cache-from productsnap/backend:latest`
4. **Dependency Layers**: Copy package files first, then source code

### Image Sizes

Typical production image sizes:
- Backend: ~150-250 MB (Python 3.11-slim based)
- Frontend: ~25-35 MB (nginx:alpine based)

## 📊 Performance Improvements

| Scenario | Without Optimization | With Optimization | Improvement |
|----------|---------------------|-------------------|-------------|
| First build | 5-8 minutes | 5-8 minutes | - |
| Rebuild (no changes) | 5-8 minutes | 10-30 seconds | **~15x faster** |
| Rebuild (code changes) | 5-8 minutes | 1-3 minutes | **~3x faster** |
| Rebuild (deps changes) | 5-8 minutes | 3-5 minutes | **~1.5x faster** |

## 🔐 Security Notes

1. **SSH Keys**: Scripts use SSH key authentication (no passwords)
2. **.env Transfer**: The script warns when transferring .env files
3. **Non-root User**: Backend runs as non-root user (appuser)
4. **Read-only Mounts**: Production uses read-only config mounts
5. **No Source Code**: Production images don't include .git, tests, etc.

## 🐛 Troubleshooting

### Build fails with "cannot connect to Docker daemon"

```bash
# Start Docker daemon
sudo systemctl start docker  # Linux
open -a Docker  # macOS

# Or check Docker Desktop is running
```

### SSH connection fails

```bash
# Test SSH manually
ssh -i ~/.ssh/id_rsa root@your-droplet-ip

# Check SSH key permissions
chmod 600 ~/.ssh/id_rsa
```

### "No space left on device" on droplet

```bash
# Clean up images remotely
./cleanup-images.sh --remote --host your-droplet-ip

# Or manually on droplet
ssh root@your-droplet-ip "docker system prune -af"
```

### Images too large

```bash
# Check image sizes
docker images productsnap/*

# Rebuild without cache
./build-and-deploy.sh --host your-droplet-ip --no-cache

# Verify multi-stage builds are working
docker history productsnap/backend:latest
```

### Deployment succeeds but health check fails

```bash
# Check logs on droplet
ssh root@your-droplet-ip "cd /opt/productsnap && docker-compose logs backend"

# Check if migrations ran
ssh root@your-droplet-ip "cd /opt/productsnap && docker-compose exec backend alembic current"

# Verify .env file has correct values
ssh root@your-droplet-ip "cat /opt/productsnap/.env"
```

## 🔄 Rollback

If deployment fails, the script attempts to rollback automatically. Manual rollback:

```bash
# SSH into droplet
ssh root@your-droplet-ip

# Go to deployment directory
cd /opt/productsnap

# Check available images
docker images productsnap/*

# Update docker-compose to use previous tag
# Edit docker-compose.prod.yml or use previous image

# Restart with old image
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📝 Environment Variables

Make sure your `.env` file is configured before deploying:

```bash
# Copy example
cp .env.example .env

# Edit with your values
vim .env

# Required variables:
# - JWT_SECRET (32+ chars)
# - POSTGRES_PASSWORD
# - NANO_BANANA_API_KEY
# - S3_* (all S3 credentials)
# - PAYPAL_* (PayPal credentials)
# - SMTP_* (Email credentials)
```

## 🎯 Best Practices

1. **Always test locally first**
   ```bash
   docker-compose up -d
   curl http://localhost:8000/health
   ```

2. **Use dry-run before production**
   ```bash
   ./build-and-deploy.sh --host your-droplet-ip --dry-run
   ```

3. **Keep images clean**
   ```bash
   # Run cleanup after each deploy
   ./cleanup-images.sh --both --host your-droplet-ip
   ```

4. **Monitor disk space**
   ```bash
   # Check local
   docker system df
   
   # Check remote
   ssh root@your-droplet-ip "docker system df"
   ```

5. **Tag important releases**
   ```bash
   # Before major deployment
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

## 📚 Additional Resources

- [Docker BuildKit Documentation](https://docs.docker.com/build/buildkit/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Layer Caching](https://docs.docker.com/build/cache/)
- [DigitalOcean Droplets](https://www.digitalocean.com/products/droplets)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs: `docker-compose logs`
3. Try with `--dry-run` to see what would happen
4. Check the main [README.md](../README.md) for general setup

---

*Last updated: October 2, 2025*
