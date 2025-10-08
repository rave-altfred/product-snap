#!/bin/bash
set -e

# Docker Push Script
# Pushes built images to DigitalOcean Container Registry

# Load config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/config.env" ]; then
    source "$SCRIPT_DIR/config.env"
fi

# Configuration
REGISTRY="${DO_REGISTRY:-registry.digitalocean.com}"
REGISTRY_NAMESPACE="${DO_REGISTRY_NAMESPACE:-}"
TAG="${IMAGE_TAG:-latest}"
PUSH_CACHE="${PUSH_CACHE:-true}"
SERVICES="${SERVICES:-backend frontend worker}"

echo "Pushing Docker image to DigitalOcean Container Registry..."
echo "Push cache: $PUSH_CACHE"
echo ""

# Validate registry namespace
if [ -z "$REGISTRY_NAMESPACE" ]; then
    echo "Error: DO_REGISTRY_NAMESPACE is not set."
    echo "Please set it to your DigitalOcean Container Registry namespace."
    exit 1
fi

FULL_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:$TAG"
CACHE_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:buildcache"

# Check if image exists locally
if ! docker image inspect "$FULL_IMAGE_NAME" &> /dev/null; then
    echo "Error: Image $FULL_IMAGE_NAME not found locally."
    echo "Please run ./droplet/build.sh first."
    exit 1
fi

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "Error: doctl is not installed. Please install it first:"
    echo "brew install doctl"
    exit 1
fi

# Check if authenticated with DigitalOcean
if ! doctl account get &> /dev/null; then
    echo "Error: Not authenticated with DigitalOcean. Please run:"
    echo "doctl auth init"
    exit 1
fi

echo "Authenticating with DigitalOcean Container Registry..."
doctl registry login

echo ""
echo "Pushing image: $FULL_IMAGE_NAME"
docker push "$FULL_IMAGE_NAME"

# Push cache image if it exists and PUSH_CACHE is true
if [ "$PUSH_CACHE" = "true" ]; then
    if docker image inspect "$CACHE_IMAGE_NAME" &> /dev/null; then
        echo ""
        echo "Pushing cache image for faster subsequent builds..."
        echo "Cache image: $CACHE_IMAGE_NAME"
        docker push "$CACHE_IMAGE_NAME"
        echo "✓ Cache image pushed successfully!"
    else
        echo ""
        echo "Note: No cache image found. This is normal for the first build."
        echo "Subsequent builds will create and push cache images automatically."
    fi
fi

echo ""
echo "✓ Image pushed successfully!"
echo "Image: $FULL_IMAGE_NAME"
if [ "$PUSH_CACHE" = "true" ] && docker image inspect "$CACHE_IMAGE_NAME" &> /dev/null; then
    echo "Cache: $CACHE_IMAGE_NAME"
fi

echo ""
echo "Verifying image in registry..."
doctl registry repository list-tags "$REGISTRY_NAMESPACE/$IMAGE_NAME" || echo "Note: Use doctl registry repository list to see all images"

echo ""
echo "Build cache info:"
echo "  - Cache is stored in registry for distributed/team builds"
echo "  - Subsequent builds will be significantly faster"
echo "  - To skip cache push: PUSH_CACHE=false ./droplet/push.sh"

echo ""
echo "Next step:"
echo "Run ./droplet/deploy.sh to deploy this image to your droplet"
