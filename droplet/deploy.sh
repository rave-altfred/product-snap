#!/bin/bash
set -e

# Deployment Script
# Deploys application to DigitalOcean droplet using Docker Compose

# Load droplet info
if [ ! -f "droplet/droplet-info.env" ]; then
    echo "Error: droplet-info.env not found. Please run create-droplet.sh first."
    exit 1
fi

source droplet/droplet-info.env

# Configuration
REGISTRY="${DO_REGISTRY:-registry.digitalocean.com}"
REGISTRY_NAMESPACE="${DO_REGISTRY_NAMESPACE:-}"
IMAGE_NAME="${IMAGE_NAME:-product-snap}"
TAG="${IMAGE_TAG:-latest}"
APP_PORT="${APP_PORT:-3000}"

echo "Deploying to droplet: $DROPLET_NAME ($DROPLET_IP)"
echo ""

# Validate registry namespace
if [ -z "$REGISTRY_NAMESPACE" ]; then
    echo "Error: DO_REGISTRY_NAMESPACE is not set."
    exit 1
fi

FULL_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:$TAG"

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "Error: doctl is not installed. Please install it first:"
    echo "brew install doctl"
    exit 1
fi

echo "Creating docker-compose.yml for deployment..."

# Create docker-compose configuration
cat > /tmp/docker-compose.yml << EOF
version: '3.8'

services:
  app:
    image: $FULL_IMAGE_NAME
    container_name: product-snap-app
    restart: unless-stopped
    ports:
      - "$APP_PORT:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
    secrets:
      - database_url
      - api_key
      - jwt_secret
      - nextauth_secret
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

secrets:
  database_url:
    file: /opt/product-snap/secrets/DATABASE_URL
  api_key:
    file: /opt/product-snap/secrets/API_KEY
  jwt_secret:
    file: /opt/product-snap/secrets/JWT_SECRET
  nextauth_secret:
    file: /opt/product-snap/secrets/NEXTAUTH_SECRET
EOF

echo "Preparing deployment secrets..."

# Create secrets deployment script
cat > /tmp/deploy-secrets.sh << 'SECRETS_SCRIPT'
#!/bin/bash
set -e

# Create secrets directory
mkdir -p /opt/product-snap/secrets
chmod 700 /opt/product-snap/secrets

# Note: Secrets should be provided via environment variables
# These can be set from a secure source like 1Password, Vault, etc.

SECRET_VARS=(
    "DATABASE_URL"
    "API_KEY"
    "JWT_SECRET"
    "NEXTAUTH_SECRET"
)

echo "Writing secrets to files..."
for var in "${SECRET_VARS[@]}"; do
    SECRET_VALUE="${!var}"
    if [ -n "$SECRET_VALUE" ]; then
        echo "Writing $var"
        echo -n "$SECRET_VALUE" > "/opt/product-snap/secrets/$var"
        chmod 600 "/opt/product-snap/secrets/$var"
    else
        echo "Warning: $var not provided"
    fi
done

echo "Secrets configured successfully"
SECRETS_SCRIPT

echo "Uploading deployment files to droplet..."
scp -o StrictHostKeyChecking=no /tmp/docker-compose.yml root@$DROPLET_IP:/opt/product-snap/docker-compose.yml
scp -o StrictHostKeyChecking=no /tmp/deploy-secrets.sh root@$DROPLET_IP:/opt/product-snap/deploy-secrets.sh

echo "Authenticating droplet with container registry..."
ssh root@$DROPLET_IP << 'EOF'
# Install doctl if not present
if ! command -v doctl &> /dev/null; then
    cd /tmp
    wget -q https://github.com/digitalocean/doctl/releases/download/v1.98.0/doctl-1.98.0-linux-amd64.tar.gz
    tar xf doctl-1.98.0-linux-amd64.tar.gz
    mv doctl /usr/local/bin/
    rm doctl-1.98.0-linux-amd64.tar.gz
fi
EOF

echo "Configuring registry authentication on droplet..."
# Get registry credentials and configure on droplet
REGISTRY_TOKEN=$(doctl registry docker-config --read-write)
ssh root@$DROPLET_IP "echo '$REGISTRY_TOKEN' > /root/.docker/config.json"

echo ""
echo "Deploying secrets (you'll need to provide them)..."
echo "Please ensure the following environment variables are set with your secrets:"
echo "  - DATABASE_URL"
echo "  - API_KEY"
echo "  - JWT_SECRET"
echo "  - NEXTAUTH_SECRET"
echo ""
read -p "Have you set these environment variables? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please set the required environment variables and run this script again."
    echo ""
    echo "Example:"
    echo "export DATABASE_URL=\$(op read 'op://vault/item/DATABASE_URL')  # Using 1Password"
    echo "export API_KEY=\$(op read 'op://vault/item/API_KEY')"
    echo "# ... set other secrets ..."
    echo ""
    echo "Then run: ./droplet/deploy.sh"
    exit 1
fi

# Deploy secrets to droplet
echo "Deploying secrets to droplet..."
ssh root@$DROPLET_IP "bash -s" < /tmp/deploy-secrets.sh << SECRETS_EOF
export DATABASE_URL="$DATABASE_URL"
export API_KEY="$API_KEY"
export JWT_SECRET="$JWT_SECRET"
export NEXTAUTH_SECRET="$NEXTAUTH_SECRET"
SECRETS_EOF

echo "Pulling latest image and deploying..."
ssh root@$DROPLET_IP << EOF
cd /opt/product-snap

# Pull the latest image
docker pull $FULL_IMAGE_NAME

# Stop and remove old containers
docker-compose down || true

# Start the application
docker-compose up -d

# Show logs
echo ""
echo "Deployment complete! Showing recent logs:"
docker-compose logs --tail=50
EOF

echo ""
echo "✓ Deployment successful!"
echo ""
echo "Application is running at:"
if [ -n "$APP_DOMAIN" ]; then
    echo "  https://$APP_DOMAIN"
else
    echo "  http://$DROPLET_IP:$APP_PORT"
fi
echo ""
echo "Useful commands:"
echo "  View logs: ssh root@$DROPLET_IP 'cd /opt/product-snap && docker-compose logs -f'"
echo "  Restart:   ssh root@$DROPLET_IP 'cd /opt/product-snap && docker-compose restart'"
echo "  Stop:      ssh root@$DROPLET_IP 'cd /opt/product-snap && docker-compose down'"
echo "  Status:    ssh root@$DROPLET_IP 'cd /opt/product-snap && docker-compose ps'"
