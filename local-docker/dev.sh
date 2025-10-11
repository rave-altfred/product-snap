#!/bin/bash

# Local Docker Development Script
# Main script that builds and deploys services

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print usage
usage() {
    echo "Usage: ./dev.sh [OPTIONS] [SERVICES...]"
    echo ""
    echo "Options:"
    echo "  --build-only   Only build, don't deploy"
    echo "  --help         Show this help message"
    echo ""
    echo "Services (default: all):"
    echo "  backend        Build & deploy backend"
    echo "  frontend       Build & deploy frontend"
    echo "  worker         Build & deploy worker"
    echo "  all            Build & deploy all services"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh                      # Build & deploy all services"
    echo "  ./dev.sh frontend             # Build & deploy only frontend"
    echo "  ./dev.sh --build-only backend # Only build backend"
    echo ""
    echo "Note: Automatically cleans dangling images after each build"
    exit 0
}

# Parse arguments
BUILD_ONLY=false
SERVICES="all"

for arg in "$@"; do
    case $arg in
        --build-only)
            BUILD_ONLY=true
            ;;
        --help|-h)
            usage
            ;;
        backend|frontend|worker|all)
            SERVICES="$arg"
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            usage
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Product Snap Local Development      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# Build services (always cleans dangling images automatically)
"$SCRIPT_DIR/build.sh" $SERVICES

# Deploy unless build-only
if [ "$BUILD_ONLY" = false ]; then
    echo ""
    "$SCRIPT_DIR/deploy.sh" $SERVICES
fi

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Ready to develop! 🚀          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
