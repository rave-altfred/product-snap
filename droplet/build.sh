#!/bin/bash
set -e

# Docker Build Script with Secrets Management
# Builds Docker images using Docker secrets (no secrets in env files)

# Configuration
REGISTRY="${DO_REGISTRY:-registry.digitalocean.com}"
REGISTRY_NAMESPACE="${DO_REGISTRY_NAMESPACE:-}"
IMAGE_NAME="${IMAGE_NAME:-product-snap}"
TAG="${IMAGE_TAG:-latest}"

echo "Building Docker images..."
echo "Registry: $REGISTRY"
echo "Image: $IMAGE_NAME:$TAG"
echo ""

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "Error: Docker is not running. Please start Docker."
    exit 1
fi

# Validate registry namespace
if [ -z "$REGISTRY_NAMESPACE" ]; then
    echo "Error: DO_REGISTRY_NAMESPACE is not set."
    echo "Please set it to your DigitalOcean Container Registry namespace."
    exit 1
fi

FULL_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:$TAG"

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in current directory."
    exit 1
fi

# Create .dockerignore if it doesn't exist
if [ ! -f ".dockerignore" ]; then
    echo "Creating .dockerignore..."
    cat > .dockerignore << 'EOF'
node_modules
npm-debug.log
.env
.env.*
.git
.gitignore
README.md
.DS_Store
*.md
.vscode
.idea
coverage
.next
out
dist
build
droplet
EOF
fi

# Prepare build secrets
# Secrets should be stored in a secure location (e.g., 1Password, AWS Secrets Manager, etc.)
# and retrieved at build time
echo "Preparing build secrets..."

# Create temporary secrets directory
SECRETS_DIR=$(mktemp -d)
trap "rm -rf $SECRETS_DIR" EXIT

# Example: Load secrets from environment variables set in your shell
# These should be sourced from a secure secret manager
SECRET_VARS=(
    "DATABASE_URL"
    "API_KEY"
    "JWT_SECRET"
    "NEXTAUTH_SECRET"
)

# Export secrets to temporary files for Docker BuildKit
for var in "${SECRET_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        echo "Adding secret: $var"
        echo -n "${!var}" > "$SECRETS_DIR/$var"
    else
        echo "Warning: $var is not set, skipping..."
    fi
done

echo ""
echo "Building image with Docker BuildKit..."

# Enable BuildKit for better build performance and secrets support
export DOCKER_BUILDKIT=1

# Build with secrets
# Note: The Dockerfile should use --mount=type=secret to access these
BUILD_ARGS=""

# Add build-time arguments (non-sensitive data only)
BUILD_ARGS="$BUILD_ARGS --build-arg NODE_ENV=production"
BUILD_ARGS="$BUILD_ARGS --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
BUILD_ARGS="$BUILD_ARGS --build-arg VERSION=$TAG"

# Build command with secrets mounted
SECRET_MOUNTS=""
for var in "${SECRET_VARS[@]}"; do
    if [ -f "$SECRETS_DIR/$var" ]; then
        SECRET_MOUNTS="$SECRET_MOUNTS --secret id=$var,src=$SECRETS_DIR/$var"
    fi
done

docker build \
    $BUILD_ARGS \
    $SECRET_MOUNTS \
    -t "$FULL_IMAGE_NAME" \
    -f Dockerfile \
    .

echo ""
echo "✓ Build complete!"
echo "Image: $FULL_IMAGE_NAME"
echo ""
echo "Next steps:"
echo "1. Run ./droplet/push.sh to push the image to DigitalOcean Container Registry"
echo "2. Run ./droplet/deploy.sh to deploy to your droplet"
