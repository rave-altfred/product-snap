#!/bin/bash

# Local Docker Deploy Script
# Restarts services with latest builds

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Product Snap Local Docker Deploy ===${NC}\n"

# Parse arguments
SERVICES="${@:-backend frontend worker nginx}"
RESTART_ONLY=false

# Function to print usage
usage() {
    echo "Usage: ./deploy.sh [OPTIONS] [SERVICES...]"
    echo ""
    echo "Options:"
    echo "  --restart-only Restart services without rebuilding"
    echo "  --help         Show this help message"
    echo ""
    echo "Services (default: backend frontend worker nginx):"
    echo "  backend        Deploy backend service"
    echo "  frontend       Deploy frontend service"
    echo "  worker         Deploy worker service"
    echo "  nginx          Deploy nginx service"
    echo "  all            Deploy all services"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh                        # Restart all main services"
    echo "  ./deploy.sh frontend               # Restart only frontend"
    echo "  ./deploy.sh --restart-only all     # Restart without build check"
    exit 0
}

# Parse options
PARSED_SERVICES=""
for arg in "$@"; do
    case $arg in
        --restart-only)
            RESTART_ONLY=true
            ;;
        --help|-h)
            usage
            ;;
        all)
            PARSED_SERVICES="backend frontend worker nginx"
            ;;
        backend|frontend|worker|nginx)
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

echo -e "${YELLOW}Deploying services: ${SERVICES}${NC}\n"

# Start/restart services (up will start if stopped, recreate if changed)
echo -e "${BLUE}>>> Starting/restarting services...${NC}"
docker-compose up -d $SERVICES

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Services deployed successfully${NC}\n"
else
    echo -e "${RED}✗ Failed to deploy services${NC}\n"
    exit 1
fi

# Show status
echo -e "${BLUE}>>> Service Status:${NC}"
docker-compose ps $SERVICES

echo -e "\n${GREEN}=== Deploy Complete ===${NC}"
echo -e "${YELLOW}Tip: Access your app at http://localhost${NC}"
