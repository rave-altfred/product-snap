#!/bin/bash
#
# Build and Push Images to DigitalOcean Container Registry (DOCR)
# For App Platform deployment
#

set -e  # Exit on error

# Configuration
REGISTRY_NAME="${REGISTRY_NAME:-productsnap-registry}"
TAG="${TAG:-latest}"
BUILD_PLATFORM="${BUILD_PLATFORM:-linux/amd64}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with color
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    print_error "doctl CLI not found. Install with: brew install doctl"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker."
    exit 1
fi

# Get registry name from config if exists
if [ -f "$(dirname "$0")/../droplet/config.env" ]; then
    source "$(dirname "$0")/../droplet/config.env"
    if [ ! -z "$DO_REGISTRY_NAMESPACE" ]; then
        REGISTRY_NAME="$DO_REGISTRY_NAMESPACE"
    fi
fi

# Registry URLs
REGISTRY_URL="registry.digitalocean.com/${REGISTRY_NAME}"
BACKEND_IMAGE="${REGISTRY_URL}/lightclick-backend:${TAG}"
FRONTEND_IMAGE="${REGISTRY_URL}/lightclick-frontend:${TAG}"
WORKER_IMAGE="${REGISTRY_URL}/lightclick-worker:${TAG}"

print_info "Building and pushing images for App Platform"
print_info "Registry: ${REGISTRY_URL}"
print_info "Tag: ${TAG}"
print_info "Platform: ${BUILD_PLATFORM}"
echo ""

# Authenticate with registry
print_info "Authenticating with DOCR..."
if ! doctl registry login; then
    print_error "Failed to authenticate with registry"
    exit 1
fi

# Get project root
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

print_info "Project root: $PROJECT_ROOT"
echo ""

# Build backend image
print_info "Building backend image..."
docker build \
    --platform "$BUILD_PLATFORM" \
    --target production \
    -t "$BACKEND_IMAGE" \
    -f backend/Dockerfile \
    backend

if [ $? -ne 0 ]; then
    print_error "Backend build failed"
    exit 1
fi

# Build worker image (same as backend, different tag)
print_info "Tagging worker image..."
docker tag "$BACKEND_IMAGE" "$WORKER_IMAGE"

# Build frontend image
print_info "Building frontend image..."
docker build \
    --platform "$BUILD_PLATFORM" \
    --target production \
    -t "$FRONTEND_IMAGE" \
    --build-arg VITE_API_URL="/api" \
    -f frontend/Dockerfile \
    .

if [ $? -ne 0 ]; then
    print_error "Frontend build failed"
    exit 1
fi

echo ""
print_info "All images built successfully!"
echo ""

# Push images
print_info "Pushing backend image..."
docker push "$BACKEND_IMAGE"

print_info "Pushing worker image..."
docker push "$WORKER_IMAGE"

print_info "Pushing frontend image..."
docker push "$FRONTEND_IMAGE"

echo ""
print_info "✅ All images pushed successfully!"
echo ""
print_info "Images available at:"
echo "  - $BACKEND_IMAGE"
echo "  - $WORKER_IMAGE"
echo "  - $FRONTEND_IMAGE"
echo ""
print_info "Next steps:"
echo "  1. Update app-platform/.do/app.yaml with registry name: $REGISTRY_NAME"
echo "  2. Deploy app: doctl apps create --spec app-platform/.do/app.yaml"
echo "  3. Or update existing app: doctl apps update <app-id> --spec app-platform/.do/app.yaml"
echo ""
