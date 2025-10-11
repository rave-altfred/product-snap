# Local Docker Development Scripts

This folder contains scripts to manage local Docker development for Product Snap.

## Scripts

### 🚀 dev.sh - Main Development Script
The main script that builds and deploys services in one command.

```bash
# Build and deploy all services
./dev.sh

# Build and deploy specific service
./dev.sh frontend

# Only build without deploying
./dev.sh --build-only backend
```

**Note:** Dangling images are automatically cleaned after each build.

### 🔨 build.sh - Build Services
Builds Docker images for services with proper caching.

```bash
# Build all services (backend, frontend, worker)
./build.sh

# Build specific service
./build.sh frontend

# Build all services
./build.sh all
```

**Note:** Dangling images are automatically cleaned after each build.

### 🚢 deploy.sh - Deploy Services
Restarts services with latest builds.

```bash
# Restart all main services
./deploy.sh

# Restart specific service
./deploy.sh frontend

# Restart with nginx
./deploy.sh backend frontend nginx
```

### 🧹 clean.sh - Cleanup Docker Resources
Cleans up Docker images and resources to free disk space.

```bash
# Clean dangling images only (safe)
./clean.sh

# Clean all unused images
./clean.sh --all

# Full cleanup including volumes (⚠️ data loss!)
./clean.sh --all --volumes
```

## Typical Workflows

### Starting Development
```bash
# First time or after major changes
docker-compose up -d

# After code changes
./dev.sh frontend  # or backend, or all
```

### Quick Frontend Update
```bash
./dev.sh frontend
```

### After Multiple Builds (Cleanup)
```bash
./clean.sh
```

### Full Rebuild
```bash
docker-compose down
./clean.sh --all
docker-compose up -d
```

## Tips

- **Cache is Good**: Docker caching speeds up builds significantly. Don't use `--no-cache` unless absolutely necessary.
- **Clean Regularly**: Run `./clean.sh` after several builds to free up disk space.
- **Service-Specific Builds**: Build only what changed (e.g., `./dev.sh frontend`) for faster iteration.
- **Check Status**: Use `docker-compose ps` to see running services.
- **View Logs**: Use `docker-compose logs -f [service]` to follow logs.

## Environment

These scripts work with the `docker-compose.yml` in the project root and assume:
- Docker and Docker Compose are installed
- You're running from the project root or the `local-docker` directory
- Services are defined: backend, frontend, worker, nginx, postgres, redis, minio
