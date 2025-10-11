#!/bin/bash

# Local Docker Build Script
# Builds services with proper caching and cleanup

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Product Snap Local Docker Build ===${NC}\n"

# Parse arguments
SERVICES="${@:-backend frontend worker}"

# Function to print usage
usage() {
    echo "Usage: ./build.sh [SERVICES...]"
    echo ""
    echo "Services (default: backend frontend worker):"
    echo "  backend        Build backend service"
    echo "  frontend       Build frontend service"
    echo "  worker         Build worker service"
    echo "  all            Build all services"
    echo ""
    echo "Examples:"
    echo "  ./build.sh                    # Build backend, frontend, and worker"
    echo "  ./build.sh frontend           # Build only frontend"
    echo "  ./build.sh all                # Build all services"
    echo ""
    echo "Note: Automatically cleans dangling images after build"
    exit 0
}

# Parse options
PARSED_SERVICES=""
for arg in "$@"; do
    case $arg in
        --help|-h)
            usage
            ;;
        all)
            PARSED_SERVICES="backend frontend worker"
            ;;
        backend|frontend|worker)
            PARSED_SERVICES="$PARSED_SERVICES $arg"
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            usage
            ;;
    esac
done

# Use parsed services if any, otherwise default
if [ -n "$PARSED_SERVICES" ]; then
    SERVICES="$PARSED_SERVICES"
fi

echo -e "${YELLOW}Building services: ${SERVICES}${NC}\n"

# Build each service
for SERVICE in $SERVICES; do
    echo -e "${BLUE}>>> Building $SERVICE...${NC}"
    docker-compose build $SERVICE
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $SERVICE built successfully${NC}\n"
    else
        echo -e "${RED}✗ Failed to build $SERVICE${NC}\n"
        exit 1
    fi
done

# Always clean up dangling images after build
echo -e "${YELLOW}Cleaning up dangling images...${NC}"
CLEANUP_OUTPUT=$(docker image prune -f 2>&1)

if echo "$CLEANUP_OUTPUT" | grep -q "Total reclaimed space: 0B"; then
    echo -e "${GREEN}✓ No dangling images to clean${NC}\n"
else
    RECLAIMED=$(echo "$CLEANUP_OUTPUT" | grep "Total reclaimed space" || echo "Cleaned up")
    echo -e "${GREEN}✓ $RECLAIMED${NC}\n"
fi

echo -e "${GREEN}=== Build Complete ===${NC}"
