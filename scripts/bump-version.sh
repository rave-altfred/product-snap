#!/bin/bash

# Version management script for ProductSnap
# Usage: ./scripts/bump-version.sh [patch|minor|major]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_CONFIG="$ROOT_DIR/backend/app/core/config.py"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

function print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

function print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if bump type is provided
BUMP_TYPE=${1:-patch}

if [[ ! "$BUMP_TYPE" =~ ^(patch|minor|major)$ ]]; then
    print_error "Invalid bump type: $BUMP_TYPE"
    echo "Usage: $0 [patch|minor|major]"
    exit 1
fi

print_header "ProductSnap Version Bump: $BUMP_TYPE"

# Get current version from package.json
CURRENT_VERSION=$(node -p "require('$FRONTEND_DIR/package.json').version")
print_warning "Current version: $CURRENT_VERSION"

# Bump version in frontend package.json (without git operations)
cd "$FRONTEND_DIR"
npm version $BUMP_TYPE --no-git-tag-version

# Get new version
NEW_VERSION=$(node -p "require('$FRONTEND_DIR/package.json').version")
print_success "New version: $NEW_VERSION"

# Update backend config.py
print_header "Updating backend version"
cd "$ROOT_DIR"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/APP_VERSION: str = \".*\"/APP_VERSION: str = \"$NEW_VERSION\"/" "$BACKEND_CONFIG"
else
    # Linux
    sed -i "s/APP_VERSION: str = \".*\"/APP_VERSION: str = \"$NEW_VERSION\"/" "$BACKEND_CONFIG"
fi

print_success "Updated backend config to version $NEW_VERSION"

# Stage changes
print_header "Committing changes"
git add "$FRONTEND_DIR/package.json" "$FRONTEND_DIR/package-lock.json" "$BACKEND_CONFIG"
git commit -m "Bump version to $NEW_VERSION"

# Create git tag
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"

print_success "Created git tag: v$NEW_VERSION"

# Show summary
print_header "Version Bump Summary"
echo "Previous version: $CURRENT_VERSION"
echo "New version:      $NEW_VERSION"
echo "Git tag:          v$NEW_VERSION"
echo ""
print_warning "To push changes and tags, run:"
echo "  git push && git push --tags"
echo ""
print_success "Version bump complete!"
