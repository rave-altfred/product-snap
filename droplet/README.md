# Droplet Management Scripts

This directory contains scripts for managing DigitalOcean droplets for the Product Snap application.

## Prerequisites

1. **Install doctl** (DigitalOcean CLI)
   ```bash
   brew install doctl
   ```

2. **Authenticate with DigitalOcean**
   ```bash
   doctl auth init
   ```

3. **Set up a Container Registry**
   - Go to DigitalOcean Console → Container Registry
   - Create a registry if you don't have one
   - Note your registry namespace

4. **Set up a Secret Manager** (Recommended)
   - Use 1Password, Vault, or similar for secrets management
   - Never commit secrets to git

## Environment Variables

Create a `.env` file or export these in your shell:

```bash
# Required
export DO_REGISTRY_NAMESPACE="your-registry-namespace"

# Optional
export DROPLET_NAME="product-snap-app"
export DO_REGION="nyc3"
export DO_SIZE="s-1vcpu-1gb"  # Start minimal, resize later
export APP_DOMAIN="your-domain.com"
export LETSENCRYPT_EMAIL="your-email@example.com"
export DB_ID="your-database-id"  # For DigitalOcean managed databases
export APP_PORT="3000"

# Application Secrets (load from secret manager)
export DATABASE_URL=$(op read "op://vault/product-snap/DATABASE_URL")
export API_KEY=$(op read "op://vault/product-snap/API_KEY")
export JWT_SECRET=$(op read "op://vault/product-snap/JWT_SECRET")
export NEXTAUTH_SECRET=$(op read "op://vault/product-snap/NEXTAUTH_SECRET")
```

## Usage

### 1. Create Droplet

Creates a minimal DigitalOcean droplet. You can resize it later as needed.

```bash
./droplet/create-droplet.sh
```

This will:
- Create a droplet with minimal specs
- Save droplet info to `droplet/droplet-info.env`
- Output the droplet IP address

### 2. Prepare Droplet

Configures the droplet with security best practices, HTTPS, and Docker.

```bash
# Set required environment variables first
export APP_DOMAIN="your-domain.com"
export LETSENCRYPT_EMAIL="your-email@example.com"
export DB_ID="your-database-id"  # Optional

./droplet/prepare-droplet.sh
```

This will:
- Update system packages
- Install Docker, Nginx, Certbot, UFW, Fail2Ban
- Configure firewall (allow SSH, HTTP, HTTPS)
- Harden SSH configuration (disable password auth)
- Set up Nginx as reverse proxy
- Configure Let's Encrypt SSL certificates (if domain is set)
- Add droplet IP to database authorized sources (if DB_ID is set)

### 3. Build Docker Image

Builds your Docker image with proper secrets management.

```bash
# Load secrets from your secret manager
export DATABASE_URL=$(op read "op://vault/product-snap/DATABASE_URL")
export API_KEY=$(op read "op://vault/product-snap/API_KEY")
export JWT_SECRET=$(op read "op://vault/product-snap/JWT_SECRET")
export NEXTAUTH_SECRET=$(op read "op://vault/product-snap/NEXTAUTH_SECRET")

./droplet/build.sh
```

This will:
- Build Docker image using BuildKit
- Mount secrets securely (not in env or image layers)
- Tag image for DigitalOcean Container Registry
- Create `.dockerignore` if needed

**Note:** Your Dockerfile should use `--mount=type=secret` to access build secrets:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine

# Example: Reading a secret during build
RUN --mount=type=secret,id=DATABASE_URL \
    export DATABASE_URL=$(cat /run/secrets/DATABASE_URL) && \
    # Your build commands here
```

### 4. Push to Registry

Pushes the built image to DigitalOcean Container Registry.

```bash
./droplet/push.sh
```

This will:
- Authenticate with DigitalOcean Container Registry
- Push the Docker image
- Verify the upload

### 5. Deploy to Droplet

Deploys your application to the prepared droplet.

```bash
# Ensure secrets are loaded
export DATABASE_URL=$(op read "op://vault/product-snap/DATABASE_URL")
export API_KEY=$(op read "op://vault/product-snap/API_KEY")
export JWT_SECRET=$(op read "op://vault/product-snap/JWT_SECRET")
export NEXTAUTH_SECRET=$(op read "op://vault/product-snap/NEXTAUTH_SECRET")

./droplet/deploy.sh
```

This will:
- Upload docker-compose.yml to droplet
- Configure Docker registry authentication on droplet
- Securely transfer secrets to droplet
- Pull latest image
- Start application with docker-compose
- Show deployment logs

## Complete Workflow

```bash
# 1. Set up environment
export DO_REGISTRY_NAMESPACE="your-namespace"
export APP_DOMAIN="your-domain.com"
export LETSENCRYPT_EMAIL="your@email.com"

# 2. Create and prepare droplet
./droplet/create-droplet.sh
./droplet/prepare-droplet.sh

# 3. Load secrets and build
export DATABASE_URL=$(op read "op://vault/product-snap/DATABASE_URL")
export API_KEY=$(op read "op://vault/product-snap/API_KEY")
export JWT_SECRET=$(op read "op://vault/product-snap/JWT_SECRET")
export NEXTAUTH_SECRET=$(op read "op://vault/product-snap/NEXTAUTH_SECRET")

# 4. Build, push, and deploy
./droplet/build.sh
./droplet/push.sh
./droplet/deploy.sh
```

## Managing Your Droplet

### View Logs
```bash
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose logs -f'
```

### Restart Application
```bash
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose restart'
```

### Stop Application
```bash
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose down'
```

### Check Status
```bash
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose ps'
```

### Update Application
```bash
# Build and push new version
./droplet/build.sh
./droplet/push.sh

# Deploy update
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose pull && docker-compose up -d'
```

### Resize Droplet
```bash
# Get droplet ID
source droplet/droplet-info.env

# Resize (requires power off)
doctl compute droplet-action power-off $DROPLET_ID --wait
doctl compute droplet-action resize $DROPLET_ID --size s-2vcpu-4gb --wait
doctl compute droplet-action power-on $DROPLET_ID --wait
```

## Security Best Practices

1. **Never commit secrets** - Always use a secret manager
2. **Use SSH keys only** - Password authentication is disabled
3. **Keep packages updated** - Regularly run system updates
4. **Monitor logs** - Check application and system logs regularly
5. **Use HTTPS** - Always configure SSL certificates
6. **Firewall rules** - Only open necessary ports
7. **Backup database** - Regular automated backups
8. **Use private networking** - For database connections when possible

## Troubleshooting

### Can't connect to droplet
```bash
# Check droplet status
doctl compute droplet list

# Check firewall rules
ssh root@<DROPLET_IP> 'ufw status verbose'
```

### SSL certificate issues
```bash
# Check certificate status
ssh root@<DROPLET_IP> 'certbot certificates'

# Renew certificates
ssh root@<DROPLET_IP> 'certbot renew'
```

### Docker registry authentication issues
```bash
# Re-authenticate locally
doctl registry login

# Re-authenticate on droplet
doctl registry docker-config | ssh root@<DROPLET_IP> 'cat > /root/.docker/config.json'
```

### Application not starting
```bash
# Check logs
ssh root@<DROPLET_IP> 'cd /opt/product-snap && docker-compose logs'

# Check container status
ssh root@<DROPLET_IP> 'docker ps -a'

# Check secrets
ssh root@<DROPLET_IP> 'ls -la /opt/product-snap/secrets/'
```

## Files

- `create-droplet.sh` - Creates a new DigitalOcean droplet
- `prepare-droplet.sh` - Configures droplet with security and services
- `build.sh` - Builds Docker image with secrets
- `push.sh` - Pushes image to DigitalOcean Container Registry
- `deploy.sh` - Deploys application to droplet
- `droplet-info.env` - Generated file with droplet details (not committed)

## Notes

- Start with minimal droplet size and resize as needed
- All scripts include error checking and validation
- Scripts are idempotent where possible
- Secrets are never written to disk in plain text (except in secure locations on droplet)
- Docker secrets are mounted as files, not environment variables
