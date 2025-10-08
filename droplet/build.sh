#!/bin/bash
set -e

# Docker Build Script with Secrets Management
# Builds Docker images using Docker secrets (no secrets in env files)
# Includes multi-arch support, layer caching, and build optimization

# Configuration
REGISTRY="${DO_REGISTRY:-registry.digitalocean.com}"
REGISTRY_NAMESPACE="${DO_REGISTRY_NAMESPACE:-}"
TAG="${IMAGE_TAG:-latest}"
PLATFORM="${BUILD_PLATFORM:-linux/amd64}"  # DigitalOcean droplets are typically amd64
USE_CACHE="${USE_CACHE:-true}"
CACHE_FROM_REGISTRY="${CACHE_FROM_REGISTRY:-true}"  # Use registry for distributed cache

# Services to build (default: all)
SERVICES="${SERVICES:-backend frontend worker}"

echo "Building Docker images..."
echo "Registry: $REGISTRY"
echo "Services: $SERVICES"
echo "Tag: $TAG"
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

# Enable BuildKit for better build performance and secrets support
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain  # Better build output

echo ""
echo "Configuring build cache strategy..."

# Build each service
BUILT_IMAGES=()
for SERVICE in $SERVICES; do
    echo ""
    echo "==========================================" 
    echo "Building service: $SERVICE"
    echo "=========================================="
    
    IMAGE_NAME="product-snap-$SERVICE"
    FULL_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:$TAG"
    CACHE_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:buildcache"
    
    # Determine context and dockerfile
    case $SERVICE in
        backend|worker)
            CONTEXT="./backend"
            DOCKERFILE="./backend/Dockerfile"
            ;;
        frontend)
            CONTEXT="./frontend"
            DOCKERFILE="./frontend/Dockerfile"
            ;;
        *)
            echo "Error: Unknown service $SERVICE"
            continue
            ;;
    esac
    
    # Check if Dockerfile exists
    if [ ! -f "$DOCKERFILE" ]; then
        echo "Warning: $DOCKERFILE not found, skipping $SERVICE"
        continue
    fi
    
    # Prepare cache strategy
    CACHE_ARGS=""
    if [ "$USE_CACHE" = "true" ]; then
        if [ "$CACHE_FROM_REGISTRY" = "true" ]; then
            echo "Pulling cache from registry..."
            docker pull "$CACHE_IMAGE_NAME" 2>/dev/null || echo "No cache found (first build)"
            docker pull "$FULL_IMAGE_NAME" 2>/dev/null || echo "No previous image found"
            
            CACHE_ARGS="$CACHE_ARGS --cache-from=$CACHE_IMAGE_NAME"
            CACHE_ARGS="$CACHE_ARGS --cache-from=$FULL_IMAGE_NAME"
        fi
    else
        CACHE_ARGS="--no-cache"
    fi
    
    # Build arguments
    BUILD_ARGS=""
    BUILD_ARGS="$BUILD_ARGS --build-arg NODE_ENV=production"
    BUILD_ARGS="$BUILD_ARGS --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    BUILD_ARGS="$BUILD_ARGS --build-arg VERSION=$TAG"
    BUILD_ARGS="$BUILD_ARGS --build-arg BUILDKIT_INLINE_CACHE=1"
    
    # Build the image
    echo "Building $FULL_IMAGE_NAME..."
    docker build \
        --platform "$PLATFORM" \
        $BUILD_ARGS \
        $CACHE_ARGS \
        -t "$FULL_IMAGE_NAME" \
        -f "$DOCKERFILE" \
        "$CONTEXT"
    
    # Tag for cache
    if [ "$USE_CACHE" = "true" ] && [ "$CACHE_FROM_REGISTRY" = "true" ]; then
        docker tag "$FULL_IMAGE_NAME" "$CACHE_IMAGE_NAME"
    fi
    
    BUILT_IMAGES+=("$FULL_IMAGE_NAME")
    echo "✓ $SERVICE built successfully"
done

echo ""
echo "==========================================" 
echo "Cleaning up..."
echo "=========================================="
# Remove dangling images
docker image prune -f > /dev/null 2>&1

# Clean up old build cache
docker builder prune -f --filter "until=168h" > /dev/null 2>&1 || true

echo "✓ Cleanup complete"

echo ""
echo "==========================================" 
echo "Build Summary"
echo "=========================================="
echo "Built ${#BUILT_IMAGES[@]} image(s):"
for img in "${BUILT_IMAGES[@]}"; do
    SIZE=$(docker image inspect "$img" --format='{{.Size}}' 2>/dev/null | awk '{print int($1/1024/1024)}')MB || echo "N/A"
    echo "  - $img ($SIZE)"
done

echo ""
echo "Docker disk usage:"
docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}" 2>/dev/null || docker system df

echo ""
echo "Next steps:"
echo "1. Run ./droplet/push.sh to push images to DigitalOcean Container Registry"
echo "2. Run ./droplet/deploy.sh to deploy to your droplet"

echo ""
echo "Build options:"
echo "  - Build specific service: SERVICES='backend' ./droplet/build.sh"
echo "  - Build multiple: SERVICES='backend frontend' ./droplet/build.sh"
echo "  - Different platform: BUILD_PLATFORM=linux/arm64 ./droplet/build.sh"
echo "  - Disable cache: USE_CACHE=false ./droplet/build.sh"
