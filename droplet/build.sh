#!/bin/bash
set -e

# Docker Build Script with Secrets Management
# Builds Docker images using Docker secrets (no secrets in env files)
# Includes multi-arch support, layer caching, and build optimization

# Configuration
REGISTRY="${DO_REGISTRY:-registry.digitalocean.com}"
REGISTRY_NAMESPACE="${DO_REGISTRY_NAMESPACE:-}"
IMAGE_NAME="${IMAGE_NAME:-product-snap}"
TAG="${IMAGE_TAG:-latest}"
PLATFORM="${BUILD_PLATFORM:-linux/amd64}"  # DigitalOcean droplets are typically amd64
USE_CACHE="${USE_CACHE:-true}"
CACHE_FROM_REGISTRY="${CACHE_FROM_REGISTRY:-true}"  # Use registry for distributed cache

echo "Building Docker images..."
echo "Registry: $REGISTRY"
echo "Image: $IMAGE_NAME:$TAG"
echo "Platform: $PLATFORM"
echo "Cache enabled: $USE_CACHE"
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
CACHE_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:buildcache"

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in current directory."
    exit 1
fi

# Verify target platform compatibility
echo "Verifying platform compatibility..."
if [[ "$PLATFORM" == *"arm"* ]] && [[ "$(uname -m)" != "arm64" ]]; then
    echo "Warning: Building for ARM on non-ARM host. This may be slower."
    echo "Consider using Docker buildx for cross-platform builds."
elif [[ "$PLATFORM" == *"amd64"* ]] && [[ "$(uname -m)" == "arm64" ]]; then
    echo "Note: Building for AMD64 on ARM (Apple Silicon). Using emulation."
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
echo "Configuring build cache strategy..."

# Enable BuildKit for better build performance and secrets support
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain  # Better build output

# Prepare cache strategy
CACHE_ARGS=""
if [ "$USE_CACHE" = "true" ]; then
    if [ "$CACHE_FROM_REGISTRY" = "true" ]; then
        echo "Using registry-based cache (recommended for CI/CD and team builds)"
        
        # Try to pull cache image from registry (don't fail if it doesn't exist)
        echo "Pulling cache from registry..."
        docker pull "$CACHE_IMAGE_NAME" 2>/dev/null || echo "No cache found in registry (first build)"
        docker pull "$FULL_IMAGE_NAME" 2>/dev/null || echo "No previous image found (first build)"
        
        # Use both buildcache and latest as cache sources
        CACHE_ARGS="$CACHE_ARGS --cache-from=$CACHE_IMAGE_NAME"
        CACHE_ARGS="$CACHE_ARGS --cache-from=$FULL_IMAGE_NAME"
    else
        echo "Using local cache (faster for solo development)"
        # BuildKit will use local cache automatically
    fi
else
    echo "Cache disabled (--no-cache build)"
    CACHE_ARGS="--no-cache"
fi

echo ""
echo "Building image with optimized layer caching..."
echo "Platform: $PLATFORM"

# Build with secrets
# Note: The Dockerfile should use --mount=type=secret to access these
BUILD_ARGS=""

# Add build-time arguments (non-sensitive data only)
BUILD_ARGS="$BUILD_ARGS --build-arg NODE_ENV=production"
BUILD_ARGS="$BUILD_ARGS --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
BUILD_ARGS="$BUILD_ARGS --build-arg VERSION=$TAG"
BUILD_ARGS="$BUILD_ARGS --build-arg BUILDKIT_INLINE_CACHE=1"  # Enable inline cache

# Build command with secrets mounted
SECRET_MOUNTS=""
for var in "${SECRET_VARS[@]}"; do
    if [ -f "$SECRETS_DIR/$var" ]; then
        SECRET_MOUNTS="$SECRET_MOUNTS --secret id=$var,src=$SECRETS_DIR/$var"
    fi
done

# Build the image
docker build \
    --platform "$PLATFORM" \
    $BUILD_ARGS \
    $CACHE_ARGS \
    $SECRET_MOUNTS \
    -t "$FULL_IMAGE_NAME" \
    -f Dockerfile \
    .

# Push cache to registry if using registry-based caching
if [ "$USE_CACHE" = "true" ] && [ "$CACHE_FROM_REGISTRY" = "true" ]; then
    echo ""
    echo "Tagging image for cache..."
    docker tag "$FULL_IMAGE_NAME" "$CACHE_IMAGE_NAME"
    
    echo "Cache image will be pushed with regular push (use ./droplet/push.sh)"
fi

echo ""
echo "Cleaning up old images..."
# Remove dangling images (intermediate layers not used by any image)
docker image prune -f > /dev/null 2>&1

# Remove old versions of THIS image (keep current tag and buildcache)
if docker images "$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME" --format "{{.ID}} {{.Tag}}" 2>/dev/null | grep -v "$TAG" | grep -v "buildcache" | awk '{print $1}' | grep -v "^$" > /dev/null 2>&1; then
    echo "Removing old versions of $IMAGE_NAME..."
    docker images "$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME" --format "{{.ID}} {{.Tag}}" | \
        grep -v "$TAG" | grep -v "buildcache" | awk '{print $1}' | \
        xargs docker rmi -f > /dev/null 2>&1 || true
fi

# Clean up build cache older than 7 days
docker builder prune -f --filter "until=168h" > /dev/null 2>&1 || true

echo "✓ Cleanup complete"

echo ""
echo "✓ Build complete!"
echo "Image: $FULL_IMAGE_NAME"
echo "Platform: $PLATFORM"

# Show image size
IMAGE_SIZE=$(docker image inspect "$FULL_IMAGE_NAME" --format='{{.Size}}' | awk '{print int($1/1024/1024)}')MB
echo "Image size: $IMAGE_SIZE"

# Show disk usage
echo ""
echo "Docker disk usage:"
docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}" 2>/dev/null || docker system df

echo ""
echo "Build optimization tips:"
echo "  - Dockerfile should follow multi-stage build pattern"
echo "  - Place frequently changing layers (code) after stable layers (dependencies)"
echo "  - Use .dockerignore to exclude unnecessary files"
echo "  - Cache is preserved in registry for faster subsequent builds"

echo ""
echo "Next steps:"
echo "1. Run ./droplet/push.sh to push the image to DigitalOcean Container Registry"
echo "2. Run ./droplet/deploy.sh to deploy to your droplet"

echo ""
echo "Advanced options:"
echo "  - Build for different platform: BUILD_PLATFORM=linux/arm64 ./droplet/build.sh"
echo "  - Disable cache: USE_CACHE=false ./droplet/build.sh"
echo "  - Use local cache only: CACHE_FROM_REGISTRY=false ./droplet/build.sh"
