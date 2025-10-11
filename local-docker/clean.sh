#!/bin/bash

# Local Docker Cleanup Script
# Cleans up Docker images and resources

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Product Snap Docker Cleanup ===${NC}\n"

# Parse arguments
CLEAN_ALL=false
CLEAN_VOLUMES=false

# Function to print usage
usage() {
    echo "Usage: ./clean.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all          Clean all unused images (not just dangling)"
    echo "  --volumes      Also clean unused volumes (DANGEROUS - data loss!)"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./clean.sh                # Clean dangling images only"
    echo "  ./clean.sh --all          # Clean all unused images"
    echo "  ./clean.sh --all --volumes # Full cleanup including volumes"
    exit 0
}

# Parse options
for arg in "$@"; do
    case $arg in
        --all)
            CLEAN_ALL=true
            ;;
        --volumes)
            CLEAN_VOLUMES=true
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            usage
            ;;
    esac
done

# Show current disk usage
echo -e "${YELLOW}Current Docker disk usage:${NC}"
docker system df
echo ""

# Clean dangling images
if [ "$CLEAN_ALL" = true ]; then
    echo -e "${YELLOW}Cleaning all unused images...${NC}"
    docker image prune -a -f
else
    echo -e "${YELLOW}Cleaning dangling images...${NC}"
    docker image prune -f
fi

# Clean build cache
echo -e "\n${YELLOW}Cleaning build cache...${NC}"
docker builder prune -f

# Clean stopped containers
echo -e "\n${YELLOW}Cleaning stopped containers...${NC}"
docker container prune -f

# Clean networks
echo -e "\n${YELLOW}Cleaning unused networks...${NC}"
docker network prune -f

# Clean volumes if requested
if [ "$CLEAN_VOLUMES" = true ]; then
    echo -e "\n${RED}⚠️  WARNING: Cleaning volumes will delete database data!${NC}"
    read -p "Are you sure you want to clean volumes? (yes/no): " -r
    echo
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}Cleaning volumes...${NC}"
        docker volume prune -f
    else
        echo -e "${YELLOW}Skipping volume cleanup${NC}"
    fi
fi

echo -e "\n${GREEN}=== Cleanup Complete ===${NC}\n"

# Show new disk usage
echo -e "${YELLOW}Docker disk usage after cleanup:${NC}"
docker system df
