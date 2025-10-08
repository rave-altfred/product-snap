#!/bin/bash
set -e

# Docker Push Script
# Pushes built images to DigitalOcean Container Registry

# Configuration
REGISTRY="${DO_REGISTRY:-registry.digitalocean.com}"
REGISTRY_NAMESPACE="${DO_REGISTRY_NAMESPACE:-}"
IMAGE_NAME="${IMAGE_NAME:-product-snap}"
TAG="${IMAGE_TAG:-latest}"

echo "Pushing Docker image to DigitalOcean Container Registry..."
echo ""

# Validate registry namespace
if [ -z "$REGISTRY_NAMESPACE" ]; then
    echo "Error: DO_REGISTRY_NAMESPACE is not set."
    echo "Please set it to your DigitalOcean Container Registry namespace."
    exit 1
fi

FULL_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:$TAG"

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

echo ""
echo "✓ Image pushed successfully!"
echo "Image: $FULL_IMAGE_NAME"
echo ""
echo "Verifying image in registry..."
doctl registry repository list-tags "$REGISTRY_NAMESPACE/$IMAGE_NAME" || echo "Note: Use doctl registry repository list to see all images"

echo ""
echo "Next step:"
echo "Run ./droplet/deploy.sh to deploy this image to your droplet"
