#!/bin/bash
set -e

# Deployment Script
# Deploys multi-service application to DigitalOcean droplet using Docker Compose

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/config.env" ]; then
    source "$SCRIPT_DIR/config.env"
fi

# Load droplet info
if [ ! -f "$SCRIPT_DIR/droplet-info.env" ]; then
    echo -e "${RED}Error: droplet-info.env not found. Please run create-droplet.sh first.${NC}"
    exit 1
fi
source "$SCRIPT_DIR/droplet-info.env"

# Configuration
REGISTRY="${DO_REGISTRY:-registry.digitalocean.com}"
REGISTRY_NAMESPACE="${DO_REGISTRY_NAMESPACE:-}"
PROJECT_NAME="${PROJECT_NAME:-product-snap}"
TAG="${IMAGE_TAG:-latest}"
SERVICES="${SERVICES:-backend frontend worker}"
APP_DIR="/opt/$PROJECT_NAME"

echo "=========================================="
echo "ProductSnap Deployment"
echo "=========================================="
echo "Droplet: $DROPLET_NAME ($DROPLET_IP)"
echo "Services: $SERVICES"
echo "Tag: $TAG"
echo ""

# Validate registry namespace
if [ -z "$REGISTRY_NAMESPACE" ]; then
    echo -e "${RED}Error: DO_REGISTRY_NAMESPACE is not set.${NC}"
    echo "Please set it in droplet/config.env"
    exit 1
fi

# Check if production env file exists
if [ ! -f "$SCRIPT_DIR/.env.production" ]; then
    echo -e "${RED}Error: .env.production not found!${NC}"
    echo ""
    echo "Please create it from the template:"
    echo "  cp $SCRIPT_DIR/.env.production.template $SCRIPT_DIR/.env.production"
    echo ""
    echo "Then edit .env.production and fill in all the required values."
    exit 1
fi

# Validate .env.production has required variables
echo "Validating production environment configuration..."
REQUIRED_VARS=(
    "DATABASE_URL"
    "JWT_SECRET"
    "S3_ENDPOINT"
    "S3_BUCKET"
    "S3_ACCESS_KEY"
    "S3_SECRET_KEY"
)

MISSING_VARS=()
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    
    # Extract variable name
    VAR_NAME="${line%%=*}"
    VAR_VALUE="${line#*=}"
    
    # Check if it's in required vars and empty
    for req_var in "${REQUIRED_VARS[@]}"; do
        if [ "$VAR_NAME" = "$req_var" ] && [ -z "$VAR_VALUE" ]; then
            MISSING_VARS+=("$req_var")
        fi
    done
done < "$SCRIPT_DIR/.env.production"

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}Error: The following required variables are not set in .env.production:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Please edit $SCRIPT_DIR/.env.production and set these values."
    exit 1
fi

echo -e "${GREEN}✓ Configuration validated${NC}"
echo ""

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}Error: doctl is not installed. Please install it first:${NC}"
    echo "brew install doctl"
    exit 1
fi

# Check SSH connectivity
echo "Testing SSH connection to droplet..."
if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$DROPLET_IP "echo 'Connection successful'" &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to droplet via SSH${NC}"
    echo "Please ensure:"
    echo "  1. The droplet is running"
    echo "  2. Your SSH key is added to the droplet"
    echo "  3. The IP address is correct: $DROPLET_IP"
    exit 1
fi
echo -e "${GREEN}✓ SSH connection successful${NC}"
echo ""

echo "Authenticating with DigitalOcean Container Registry..."
doctl registry login

echo "Preparing deployment files..."

# Copy docker-compose template
cp "$SCRIPT_DIR/docker-compose.prod.yml" /tmp/docker-compose.yml

# Copy production env file
cp "$SCRIPT_DIR/.env.production" /tmp/.env.production

echo "Uploading files to droplet..."
ssh root@$DROPLET_IP "mkdir -p $APP_DIR/nginx/conf.d $APP_DIR/nginx/ssl"

# Upload docker-compose and env
scp -o StrictHostKeyChecking=no /tmp/docker-compose.yml root@$DROPLET_IP:$APP_DIR/docker-compose.yml
scp -o StrictHostKeyChecking=no /tmp/.env.production root@$DROPLET_IP:$APP_DIR/.env.production

# Set secure permissions on secrets file (readable only by root)
ssh root@$DROPLET_IP "chmod 600 $APP_DIR/.env.production"

# Upload system nginx config
if [ -f "$SCRIPT_DIR/../nginx/productsnap-system.conf" ]; then
    echo "Uploading system nginx configuration..."
    scp -o StrictHostKeyChecking=no "$SCRIPT_DIR/../nginx/productsnap-system.conf" root@$DROPLET_IP:/etc/nginx/sites-available/productsnap.conf
    
    # Enable site and test configuration
    ssh root@$DROPLET_IP "ln -sf /etc/nginx/sites-available/productsnap.conf /etc/nginx/sites-enabled/productsnap.conf && nginx -t && systemctl reload nginx || echo 'Nginx will be configured after SSL setup'"
fi

echo "Configuring registry authentication on droplet..."
# Get registry credentials and configure on droplet
REGISTRY_TOKEN=$(doctl registry docker-config --read-write)
ssh root@$DROPLET_IP "mkdir -p /root/.docker && echo '$REGISTRY_TOKEN' > /root/.docker/config.json"

echo ""
echo "=========================================="
echo "Deploying to droplet..."
echo "=========================================="

# Deploy on droplet
ssh root@$DROPLET_IP bash << EOF
set -e
cd $APP_DIR

echo "Pulling latest images..."
export \$(cat .env.production | grep -v '^#' | xargs)

# Pull all service images
for service in $SERVICES; do
    IMAGE_NAME="$PROJECT_NAME-\$service"
    FULL_IMAGE="$REGISTRY/$REGISTRY_NAMESPACE/\$IMAGE_NAME:$TAG"
    echo "Pulling \$FULL_IMAGE..."
    docker pull "\$FULL_IMAGE"
done

echo ""
echo "Stopping existing containers..."
docker-compose down || true

echo ""
echo "Starting services..."
docker-compose --env-file .env.production up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

echo ""
echo "Service status:"
docker-compose ps

echo ""
echo "Checking service health..."
docker-compose ps --format json | jq -r '.[] | "\(.Service): \(.State)"' 2>/dev/null || docker-compose ps

EOF

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo "=========================================="

# Get deployment status
echo ""
echo "Current status:"
ssh root@$DROPLET_IP "cd $APP_DIR && docker-compose ps"

echo ""
echo "Application URLs:"
if [ -n "$APP_DOMAIN" ]; then
    echo -e "  Frontend: ${GREEN}https://$APP_DOMAIN${NC}"
    echo -e "  Backend:  ${GREEN}https://$APP_DOMAIN/api${NC}"
    echo -e "  Health:   ${GREEN}https://$APP_DOMAIN/health${NC}"
else
    echo -e "  Frontend: ${GREEN}http://$DROPLET_IP${NC}"
    echo -e "  Backend:  ${GREEN}http://$DROPLET_IP/api${NC}"
    echo -e "  Health:   ${GREEN}http://$DROPLET_IP/health${NC}"
fi

echo ""
echo "Useful commands:"
echo "  View logs:    ssh root@$DROPLET_IP 'cd $APP_DIR && docker-compose logs -f'"
echo "  View service: ssh root@$DROPLET_IP 'cd $APP_DIR && docker-compose logs -f backend'"
echo "  Restart all:  ssh root@$DROPLET_IP 'cd $APP_DIR && docker-compose restart'"
echo "  Stop all:     ssh root@$DROPLET_IP 'cd $APP_DIR && docker-compose down'"
echo "  Status:       ssh root@$DROPLET_IP 'cd $APP_DIR && docker-compose ps'"
echo ""
echo "Deployment options:"
echo "  Deploy specific: SERVICES='backend' ./droplet/deploy.sh"
echo "  Different tag:   TAG=v1.0.0 ./droplet/deploy.sh"

# Cleanup temp files
rm -f /tmp/docker-compose.yml /tmp/.env.production
