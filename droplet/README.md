# ProductSnap Deployment Guide

This directory contains scripts and configuration for deploying ProductSnap to a DigitalOcean droplet.

## Architecture Overview

**Services on Droplet:**
- `backend` - FastAPI backend service
- `frontend` - React frontend (Vite build served by Nginx)
- `worker` - Background job processor
- `redis` - Local Redis instance for caching/queues
- `nginx` - Reverse proxy and SSL termination

**External Services (DigitalOcean Managed):**
- PostgreSQL Database (Managed Database)
- Spaces (S3-compatible object storage)

## Prerequisites

1. **DigitalOcean CLI (`doctl`)**
   ```bash
   brew install doctl
   doctl auth init
   ```

2. **Docker** - For building images locally

3. **SSH Key** - Added to your DigitalOcean account

4. **External Services Setup:**
   - Create a DigitalOcean Managed PostgreSQL database
   - Create a Spaces bucket for file storage
   - Note down connection details

## Initial Setup

### 1. Configure Settings

Edit `droplet/config.env`:
```bash
# Set your DigitalOcean registry namespace
DO_REGISTRY_NAMESPACE=your-registry-name

# Set your domain
DOMAIN=yourdomain.com
SUBDOMAIN=app

# Other settings as needed
```

### 2. Create Production Environment File

```bash
# Copy template
cp droplet/.env.production.template droplet/.env.production

# Edit with your values
nano droplet/.env.production
```

**Required Variables:**
- `DATABASE_URL` - PostgreSQL connection string from DO Managed Database
- `JWT_SECRET` - Generate with: `openssl rand -base64 32`
- `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` - From DO Spaces
- `PAYPAL_*` - PayPal API credentials
- `SMTP_*` - Email service credentials

### 3. Create Droplet (Optional - if not already created)

```bash
./droplet/create-droplet.sh
```

This will:
- Create a new droplet
- Install Docker and Docker Compose
- Configure firewall
- Save droplet info to `droplet-info.env`

## Deployment Workflow

### Complete Deployment (All Services)

```bash
# 1. Build all images
./droplet/build.sh

# 2. Push to registry
./droplet/push.sh

# 3. Deploy to droplet
./droplet/deploy.sh
```

### Selective Service Deployment

Deploy only specific services:

```bash
# Build only backend
SERVICES='backend' ./droplet/build.sh

# Push only backend
SERVICES='backend' ./droplet/push.sh

# Deploy only backend (will restart only this service)
SERVICES='backend' ./droplet/deploy.sh
```

### Quick Update Workflow

For quick code changes without rebuilding everything:

```bash
# Build and deploy just the backend
SERVICES='backend' ./droplet/build.sh && \
SERVICES='backend' ./droplet/push.sh && \
SERVICES='backend' ./droplet/deploy.sh
```

## Script Details

### `build.sh`
Builds Docker images for services.

**Options:**
- `SERVICES='backend frontend'` - Build specific services
- `BUILD_PLATFORM=linux/amd64` - Target platform
- `USE_CACHE=false` - Disable Docker cache
- `TAG=v1.0.0` - Custom image tag

**Examples:**
```bash
# Build all with custom tag
TAG=v1.0.0 ./droplet/build.sh

# Build only frontend without cache
SERVICES='frontend' USE_CACHE=false ./droplet/build.sh
```

### `push.sh`
Pushes built images to DigitalOcean Container Registry.

**Options:**
- `SERVICES='backend'` - Push specific services
- `PUSH_CACHE=false` - Skip pushing cache images
- `TAG=v1.0.0` - Push specific tag

**Examples:**
```bash
# Push specific version
TAG=v1.0.0 ./droplet/push.sh

# Push without cache
PUSH_CACHE=false ./droplet/push.sh
```

### `deploy.sh`
Deploys services to the droplet using docker-compose.

**Options:**
- `SERVICES='backend frontend'` - Deploy specific services
- `TAG=v1.0.0` - Deploy specific version

**Examples:**
```bash
# Deploy specific version
TAG=v1.0.0 ./droplet/deploy.sh

# Deploy only worker
SERVICES='worker' ./droplet/deploy.sh
```

## Managing the Droplet

### View Logs

```bash
# All services
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose logs -f'

# Specific service
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose logs -f backend'

# Last 100 lines
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose logs --tail=100'
```

### Service Management

```bash
# Check status
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose ps'

# Restart service
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose restart backend'

# Restart all
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose restart'

# Stop all
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose down'

# Start all
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose up -d'
```

### Database Migrations

```bash
# Run migrations
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose exec backend alembic upgrade head'

# Create migration
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose exec backend alembic revision --autogenerate -m "description"'
```

### Shell Access

```bash
# Backend shell
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose exec backend bash'

# Redis CLI
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose exec redis redis-cli'

# View environment
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose exec backend env'
```

## Troubleshooting

### Check Service Health

```bash
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose ps'
```

### View Recent Errors

```bash
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose logs --tail=50 backend | grep ERROR'
```

### Restart Everything

```bash
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose down && docker-compose up -d'
```

### Clean Up Docker

```bash
# Remove unused images
ssh root@<DROPLET_IP> 'docker image prune -f'

# Remove unused volumes (careful!)
ssh root@<DROPLET_IP> 'docker volume prune -f'

# Full cleanup
ssh root@<DROPLET_IP> 'docker system prune -af'
```

### Registry Authentication Issues

```bash
# Re-authenticate with registry
doctl registry login

# Update droplet registry credentials
REGISTRY_TOKEN=$(doctl registry docker-config --read-write)
ssh root@<DROPLET_IP> "echo '$REGISTRY_TOKEN' > /root/.docker/config.json"
```

## Files Overview

```
droplet/
├── config.env                    # Manual configuration
├── droplet-info.env             # Auto-generated (gitignored)
├── .env.production              # Production secrets (gitignored)
├── .env.production.template     # Template for production env
├── docker-compose.prod.yml      # Production compose file
├── build.sh                     # Build images
├── push.sh                      # Push to registry
├── deploy.sh                    # Deploy to droplet
├── create-droplet.sh            # Create new droplet
├── prepare-droplet.sh           # Setup existing droplet
└── README.md                    # This file
```

## Security Best Practices

1. **Never commit** `.env.production` or `droplet-info.env`
2. **Rotate secrets** regularly (JWT_SECRET, API keys)
3. **Use strong passwords** for database and services
4. **Enable SSL** in production (configure nginx)
5. **Restrict database access** to droplet IP only
6. **Keep droplet updated**: `ssh root@<IP> 'apt update && apt upgrade -y'`
7. **Monitor logs** for suspicious activity
8. **Backup database** regularly (DigitalOcean automated backups)

## Environment Variables Reference

See `.env.production.template` for all available environment variables and their descriptions.

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Verify service health: `docker-compose ps`
3. Check this README for common solutions
4. Review DigitalOcean documentation
