#!/bin/bash
set -e

# Deployment Script with Docker Secrets Support
# Deploys multi-service application to DigitalOcean droplet using Docker Swarm

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
STACK_NAME="${PROJECT_NAME}"
USE_SECRETS="${USE_SECRETS:-true}"

echo "=========================================="
echo "ProductSnap Deployment (Docker Secrets)"
echo "=========================================="
echo "Droplet: $DROPLET_NAME ($DROPLET_IP)"
echo "Services: $SERVICES"
echo "Tag: $TAG"
echo "Secrets: $USE_SECRETS"
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

# Create non-secret env file (filter out secrets)
echo "Creating non-secret configuration file..."
grep -v -E "^(JWT_SECRET|PAYPAL_CLIENT_SECRET|NANO_BANANA_API_KEY|S3_SECRET_KEY|SMTP_PASSWORD|GOOGLE_CLIENT_SECRET)=" "$SCRIPT_DIR/.env.production" > /tmp/.env.nonsecrets

# Prepare docker-compose file
if [ "$USE_SECRETS" = "true" ]; then
    cp "$SCRIPT_DIR/docker-compose.prod.secrets.yml" /tmp/docker-compose.yml
else
    cp "$SCRIPT_DIR/docker-compose.prod.yml" /tmp/docker-compose.yml
fi

echo "Uploading files to droplet..."
ssh root@$DROPLET_IP "mkdir -p $APP_DIR/nginx/conf.d $APP_DIR/nginx/ssl"

# Upload docker-compose
scp -o StrictHostKeyChecking=no /tmp/docker-compose.yml root@$DROPLET_IP:$APP_DIR/docker-compose.yml

# Upload non-secret env file
scp -o StrictHostKeyChecking=no /tmp/.env.nonsecrets root@$DROPLET_IP:$APP_DIR/.env.production

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
echo "Deploying to droplet with Docker Secrets"
echo "=========================================="

# Deploy on droplet
ssh root@$DROPLET_IP bash << EOF
set -e
cd $APP_DIR

# Initialize Docker Swarm if not already initialized
if ! docker info | grep -q "Swarm: active"; then
    echo "Initializing Docker Swarm..."
    # Use the public IP address for advertising
    docker swarm init --advertise-addr $DROPLET_IP || true
    echo "✓ Docker Swarm initialized"
else
    echo "✓ Docker Swarm already active"
fi

# Check if stack exists and remove it to allow secret updates
if docker stack ls | grep -q "$STACK_NAME"; then
    echo ""
    echo "Removing existing stack to update secrets..."
    docker stack rm "$STACK_NAME"
    echo "Waiting for stack to be removed..."
    sleep 10
    echo "✓ Stack removed"
fi

echo ""
echo "Creating/updating Docker secrets..."

# Function to create or update secret
update_secret() {
    local secret_name="\$1"
    local secret_value="\$2"
    
    if [ -z "\$secret_value" ]; then
        echo "  ⚠ Skipping \$secret_name (empty value)"
        return 0
    fi
    
    # Check if secret exists
    if docker secret inspect "\$secret_name" &> /dev/null; then
        echo -n "  Updating \$secret_name... "
        # Remove old secret
        docker secret rm "\$secret_name" &> /dev/null || true
        sleep 1
    else
        echo -n "  Creating \$secret_name... "
    fi
    
    # Create secret
    if echo "\$secret_value" | docker secret create "\$secret_name" - &> /dev/null; then
        echo "✓"
    else
        echo "✗ FAILED"
        return 1
    fi
}

# Load secrets from .env.production file on droplet
export \$(cat .env.production | grep -v '^#' | xargs)

# Now we need to load the actual secret values
# Upload a temporary secrets file
EOF

# Create temporary secrets file with only secret values
echo "Extracting secrets..."
SECRET_VARS=("JWT_SECRET" "PAYPAL_CLIENT_SECRET" "NANO_BANANA_API_KEY" "S3_SECRET_KEY" "SMTP_PASSWORD" "GOOGLE_CLIENT_SECRET")
> /tmp/.secrets.env
for var in "${SECRET_VARS[@]}"; do
    value=$(grep "^${var}=" "$SCRIPT_DIR/.env.production" | cut -d'=' -f2-)
    if [ -n "$value" ]; then
        echo "${var}=${value}" >> /tmp/.secrets.env
    fi
done

# Upload secrets file
scp -o StrictHostKeyChecking=no /tmp/.secrets.env root@$DROPLET_IP:$APP_DIR/.secrets.env
ssh root@$DROPLET_IP "chmod 600 $APP_DIR/.secrets.env"

# Continue deployment on droplet
ssh root@$DROPLET_IP bash << EOF
set -e
cd $APP_DIR

# Function to create or update secret
update_secret() {
    local secret_name="\$1"
    local secret_value="\$2"
    
    if [ -z "\$secret_value" ]; then
        echo "  ⚠ Skipping \$secret_name (empty value)"
        return 0
    fi
    
    # Check if secret exists
    if docker secret inspect "\$secret_name" &> /dev/null; then
        echo -n "  Updating \$secret_name... "
        # Remove old secret
        docker secret rm "\$secret_name" &> /dev/null || true
        sleep 1
    else
        echo -n "  Creating \$secret_name... "
    fi
    
    # Create secret
    if echo "\$secret_value" | docker secret create "\$secret_name" - &> /dev/null; then
        echo "✓"
    else
        echo "✗ FAILED"
        return 1
    fi
}

# Load secrets
export \$(cat .secrets.env | grep -v '^#' | xargs)

# Create/update secrets
update_secret "${PROJECT_NAME}_jwt_secret" "\$JWT_SECRET"
update_secret "${PROJECT_NAME}_paypal_client_secret" "\$PAYPAL_CLIENT_SECRET"
update_secret "${PROJECT_NAME}_nano_banana_api_key" "\$NANO_BANANA_API_KEY"
update_secret "${PROJECT_NAME}_s3_secret_key" "\$S3_SECRET_KEY"
update_secret "${PROJECT_NAME}_smtp_password" "\$SMTP_PASSWORD"
update_secret "${PROJECT_NAME}_google_client_secret" "\$GOOGLE_CLIENT_SECRET"

# Remove secrets file immediately
rm -f .secrets.env

echo ""
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
echo "Deploying stack..."
# Deploy or update stack
docker stack deploy -c docker-compose.yml --with-registry-auth "$STACK_NAME"

echo ""
echo "Waiting for services to start..."
sleep 15

echo ""
echo "Service status:"
docker stack services "$STACK_NAME"

echo ""
echo "Checking service health..."
docker service ls --filter "name=${STACK_NAME}_"

EOF

# Clean up local temp files
rm -f /tmp/.secrets.env /tmp/.env.nonsecrets /tmp/docker-compose.yml

echo ""
echo "=========================================="
echo "Deployment Complete"
echo "=========================================="
echo ""
echo "Your application is now running with Docker Secrets!"
echo ""
echo "Useful commands:"
echo "  View services:  ssh root@$DROPLET_IP 'docker stack services $STACK_NAME'"
echo "  View logs:      ssh root@$DROPLET_IP 'docker service logs ${STACK_NAME}_backend'"
echo "  Scale service:  ssh root@$DROPLET_IP 'docker service scale ${STACK_NAME}_backend=2'"
echo "  Update stack:   Run this script again"
echo "  Remove stack:   ssh root@$DROPLET_IP 'docker stack rm $STACK_NAME'"
echo ""
echo "To manage secrets:"
echo "  ssh root@$DROPLET_IP"
echo "  docker secret ls"
echo "  docker secret inspect productsnap_jwt_secret"
echo ""
