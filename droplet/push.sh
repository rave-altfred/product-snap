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
PROJECT_NAME="${PROJECT_NAME:-product-snap}"
TAG="${IMAGE_TAG:-latest}"
PUSH_CACHE="${PUSH_CACHE:-true}"
SERVICES="${SERVICES:-backend frontend worker}"

echo "Pushing Docker images to DigitalOcean Container Registry..."
echo "Registry: $REGISTRY/$REGISTRY_NAMESPACE"
echo "Services: $SERVICES"
echo "Tag: $TAG"
echo "Push cache: $PUSH_CACHE"
echo ""

# Validate registry namespace
if [ -z "$REGISTRY_NAMESPACE" ]; then
    echo "Error: DO_REGISTRY_NAMESPACE is not set."
    echo "Please set it to your DigitalOcean Container Registry namespace."
    exit 1
fi

# Parse services into array
IFS=' ' read -ra SERVICE_ARRAY <<< "$SERVICES"

# Check if images exist locally
MISSING_IMAGES=()
for SERVICE in "${SERVICE_ARRAY[@]}"; do
    IMAGE_NAME="$PROJECT_NAME-$SERVICE"
    FULL_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:$TAG"
    if ! docker image inspect "$FULL_IMAGE_NAME" &> /dev/null; then
        MISSING_IMAGES+=("$FULL_IMAGE_NAME")
    fi
done

if [ ${#MISSING_IMAGES[@]} -gt 0 ]; then
    echo "Error: The following images not found locally:"
    for img in "${MISSING_IMAGES[@]}"; do
        echo "  - $img"
    done
    echo ""
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

# Push each service
PUSHED_IMAGES=()
for SERVICE in "${SERVICE_ARRAY[@]}"; do
    echo "=========================================="
    echo "Pushing service: $SERVICE"
    echo "=========================================="
    
    IMAGE_NAME="$PROJECT_NAME-$SERVICE"
    FULL_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:$TAG"
    CACHE_IMAGE_NAME="$REGISTRY/$REGISTRY_NAMESPACE/$IMAGE_NAME:buildcache"
    
    echo "Pushing image: $FULL_IMAGE_NAME"
    docker push "$FULL_IMAGE_NAME"
    
    # Push cache image if it exists and PUSH_CACHE is true
    if [ "$PUSH_CACHE" = "true" ]; then
        if docker image inspect "$CACHE_IMAGE_NAME" &> /dev/null; then
            echo "Pushing cache image: $CACHE_IMAGE_NAME"
            docker push "$CACHE_IMAGE_NAME"
        fi
    fi
    
    PUSHED_IMAGES+=("$FULL_IMAGE_NAME")
    echo "✓ $SERVICE pushed successfully"
    echo ""
done

echo "=========================================="
echo "Push Summary"
echo "=========================================="
echo "Pushed ${#PUSHED_IMAGES[@]} image(s):"
for img in "${PUSHED_IMAGES[@]}"; do
    echo "  - $img"
done

echo ""
echo "Next step:"
echo "Run ./droplet/deploy.sh to deploy these images to your droplet"
echo ""
echo "Push options:"
echo "  - Push specific service: SERVICES='backend' ./droplet/push.sh"
echo "  - Push multiple: SERVICES='backend frontend' ./droplet/push.sh"
echo "  - Skip cache: PUSH_CACHE=false ./droplet/push.sh"
