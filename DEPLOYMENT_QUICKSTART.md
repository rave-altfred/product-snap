# 🚀 Deployment Quick Start

Get ProductSnap deployed to your DigitalOcean droplet in minutes.

## Prerequisites

✅ Docker installed locally  
✅ DigitalOcean droplet created (Ubuntu 22.04 recommended)  
✅ SSH access to droplet configured  
✅ Domain pointed to droplet IP (for SSL)  

## Step 1: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your production credentials
nano .env
```

**Required variables:**
- `JWT_SECRET` (generate with: `openssl rand -hex 32`)
- `POSTGRES_PASSWORD`
- `NANO_BANANA_API_KEY`
- S3 credentials (S3_ENDPOINT, S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY)
- PayPal credentials (PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
- SMTP credentials (SMTP_HOST, SMTP_USER, SMTP_PASSWORD)

## Step 2: Deploy

```bash
cd deployment

# Deploy to your droplet (replace with your droplet IP)
./build-and-deploy.sh --host 123.45.67.89
```

**That's it!** The script will:
1. ✅ Build optimized Docker images with caching
2. ✅ Transfer images to droplet
3. ✅ Run database migrations
4. ✅ Start all services
5. ✅ Perform health checks
6. ✅ Clean up old images

## Step 3: Configure SSL (Production)

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Install certbot
apt install certbot

# Get SSL certificate (replace with your domain)
certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Update nginx config with your domain
cd /opt/productsnap
nano nginx/conf.d/prod.conf

# Restart nginx
docker-compose restart nginx
```

## Step 4: Verify

```bash
# Check service status
ssh root@your-droplet-ip 'cd /opt/productsnap && docker-compose ps'

# Check logs
ssh root@your-droplet-ip 'cd /opt/productsnap && docker-compose logs -f'

# Test health endpoint
curl https://your-droplet-ip/health
```

## Quick Commands

```bash
# Rebuild and redeploy (with cache - FAST!)
./build-and-deploy.sh --host 123.45.67.89

# Force rebuild without cache
./build-and-deploy.sh --host 123.45.67.89 --no-cache

# Deploy existing images (skip build)
./build-and-deploy.sh --host 123.45.67.89 --skip-build

# Clean up old images
./cleanup-images.sh --both --host 123.45.67.89

# View what would happen (dry run)
./build-and-deploy.sh --host 123.45.67.89 --dry-run
```

## Subsequent Deployments

After initial setup, deploying updates is simple:

```bash
# 1. Make your code changes
# 2. Commit to git (optional but recommended)
# 3. Deploy

cd deployment
./build-and-deploy.sh --host 123.45.67.89
```

**Speed:** With layer caching, rebuilds take 10-30 seconds (was 5-8 minutes!)

## Troubleshooting

### Deployment fails at health check
```bash
ssh root@your-droplet-ip 'cd /opt/productsnap && docker-compose logs backend'
```

### Out of disk space
```bash
./cleanup-images.sh --remote --host 123.45.67.89
```

### Need to rollback
```bash
ssh root@your-droplet-ip
cd /opt/productsnap
docker images productsnap/*  # See available versions
# Edit docker-compose.prod.yml to use previous tag
docker-compose down && docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Performance Comparison

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| First build | 5-8 min | 5-8 min | - |
| Rebuild (no changes) | 5-8 min | 10-30 sec | **15x faster** ⚡ |
| Rebuild (code changes) | 5-8 min | 1-3 min | **3x faster** ⚡ |

## Security Checklist

- [ ] Changed default passwords in `.env`
- [ ] Generated strong JWT secret (32+ chars)
- [ ] SSL certificates configured
- [ ] Firewall enabled (ports 22, 80, 443)
- [ ] Regular backups scheduled
- [ ] .env file has correct production URLs

## Need Help?

- See [`deployment/README.md`](deployment/README.md) for detailed documentation
- Check [`MISSING_IMPLEMENTATIONS.md`](MISSING_IMPLEMENTATIONS.md) for feature status
- Review main [`README.md`](README.md) for project overview

---

**Next Steps:**
1. Set up automated backups: `crontab -e` → `0 2 * * * /opt/productsnap/deployment/backup.sh`
2. Configure monitoring (optional)
3. Set up CI/CD pipeline (optional)
