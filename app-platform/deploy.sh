#!/bin/bash
# DigitalOcean App Platform Deployment Script
# LightClick Studio
# 
# This script deploys the application to DigitalOcean App Platform
# Usage: 
#   ./deploy.sh create [dev|prod]       - Create new app
#   ./deploy.sh update [dev|prod]       - Update app spec only
#   ./deploy.sh deploy [dev|prod]       - Build, push, and deploy
#   ./deploy.sh list                    - List all apps
#   ./deploy.sh info [dev|prod]         - Get app information
#   ./deploy.sh logs [dev|prod] [type]  - View logs
#   ./deploy.sh validate [dev|prod]     - Validate app spec

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGION="fra"  # Frankfurt

# Function to detect and set environment-specific variables
set_environment() {
    local env="${1:-}"
    
    # Check if environment is provided
    if [ -z "$env" ]; then
        print_error "Environment parameter required"
        echo ""
        echo "Usage: ./deploy.sh <command> <dev|prod>"
        echo "Valid environments: dev, prod"
        exit 1
    fi
    
    # Validate environment value
    if [[ "$env" != "dev" && "$env" != "prod" ]]; then
        print_error "Invalid environment: $env"
        echo "Valid environments: dev, prod"
        exit 1
    fi
    
    ENVIRONMENT="$env"
    
    # Set environment-specific file paths
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        APP_SPEC_FILE="$SCRIPT_DIR/.do/app-dev.yaml"
        APP_ID_FILE="$SCRIPT_DIR/.do/app-id-dev.txt"
        ENV_LABEL="DEVELOPMENT"
    else
        APP_SPEC_FILE="$SCRIPT_DIR/.do/app.yaml"
        APP_ID_FILE="$SCRIPT_DIR/.do/app-id.txt"
        ENV_LABEL="PRODUCTION"
    fi
}

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if doctl is installed
check_doctl() {
    if ! command -v doctl &> /dev/null; then
        print_error "doctl CLI is not installed"
        echo ""
        echo "Install it with:"
        echo "  brew install doctl"
        echo ""
        echo "Then authenticate:"
        echo "  doctl auth init"
        exit 1
    fi
    
    print_success "doctl CLI is installed"
}

# Function to check if authenticated
check_auth() {
    if ! doctl account get &> /dev/null; then
        print_error "Not authenticated with DigitalOcean"
        echo ""
        echo "Run: doctl auth init"
        exit 1
    fi
    
    print_success "Authenticated with DigitalOcean"
}

# Function to check if app spec file exists
check_app_spec() {
    if [ ! -f "$APP_SPEC_FILE" ]; then
        print_error "App spec file not found: $APP_SPEC_FILE"
        exit 1
    fi
    
    print_success "App spec file found"
}

# Function to validate app spec
validate_app_spec() {
    print_info "Validating app spec..."
    
    if doctl apps spec validate "$APP_SPEC_FILE"; then
        print_success "App spec is valid"
    else
        print_error "App spec validation failed"
        exit 1
    fi
}

# Function to list existing apps
list_apps() {
    print_info "Existing apps:"
    doctl apps list --format ID,Spec.Name,DefaultIngress,Region,CreatedAt
}

# Function to create new app
create_app() {
    print_info "Creating new $ENV_LABEL app from spec..."
    print_info "Using spec: $APP_SPEC_FILE"
    
    # Create the app
    if doctl apps create --spec "$APP_SPEC_FILE" --format ID,Spec.Name,DefaultIngress --no-header > /tmp/app_create_output.txt; then
        print_success "App created successfully!"
        echo ""
        cat /tmp/app_create_output.txt
        echo ""
        
        # Extract app ID
        APP_ID=$(awk '{print $1}' /tmp/app_create_output.txt)
        
        print_info "App ID: $APP_ID"
        print_info "Environment: $ENVIRONMENT"
        
        # Save app ID to environment-specific file
        echo "$APP_ID" > "$APP_ID_FILE"
        print_success "App ID saved to $APP_ID_FILE"
        
        echo ""
        print_info "Monitor deployment:"
        echo "  ./deploy.sh logs $ENVIRONMENT BUILD"
        echo "  ./deploy.sh logs $ENVIRONMENT DEPLOY"
        echo "  ./deploy.sh info $ENVIRONMENT"
        
        rm /tmp/app_create_output.txt
    else
        print_error "Failed to create app"
        exit 1
    fi
}

# Function to update existing app
update_app() {
    local app_id=$1
    
    if [ -z "$app_id" ]; then
        # Try to read from saved file
        if [ -f "$APP_ID_FILE" ]; then
            app_id=$(cat "$APP_ID_FILE")
            print_info "Using saved $ENVIRONMENT App ID: $app_id"
        else
            print_error "App ID not provided and not found in $APP_ID_FILE"
            echo ""
            echo "Usage: ./deploy.sh update $ENVIRONMENT"
            echo "Or create app first: ./deploy.sh create $ENVIRONMENT"
            echo ""
            list_apps
            exit 1
        fi
    fi
    
    print_info "Updating $ENV_LABEL app: $app_id"
    print_info "Using spec: $APP_SPEC_FILE"
    
    # Update the app
    if doctl apps update "$app_id" --spec "$APP_SPEC_FILE"; then
        print_success "App updated successfully!"
        echo ""
        
        print_info "Monitor deployment:"
        echo "  ./deploy.sh logs $ENVIRONMENT DEPLOY"
        echo "  ./deploy.sh info $ENVIRONMENT"
        echo ""
        echo "View in browser:"
        echo "  https://cloud.digitalocean.com/apps/$app_id"
    else
        print_error "Failed to update app"
        exit 1
    fi
}

# Function to get app info
get_app_info() {
    local app_id=$1
    
    if [ -z "$app_id" ]; then
        if [ -f "$APP_ID_FILE" ]; then
            app_id=$(cat "$APP_ID_FILE")
        else
            print_error "App ID not provided and not found in $APP_ID_FILE"
            echo "Usage: ./deploy.sh info $ENVIRONMENT"
            exit 1
        fi
    fi
    
    print_info "$ENV_LABEL app information:"
    doctl apps get "$app_id"
}

# Function to view logs
view_logs() {
    local app_id=$1
    local log_type=${2:-DEPLOY}
    
    if [ -z "$app_id" ]; then
        if [ -f "$APP_ID_FILE" ]; then
            app_id=$(cat "$APP_ID_FILE")
        else
            print_error "App ID not provided and not found in $APP_ID_FILE"
            echo "Usage: ./deploy.sh logs $ENVIRONMENT [BUILD|DEPLOY|RUN]"
            exit 1
        fi
    fi
    
    print_info "Viewing $log_type logs for $ENV_LABEL app: $app_id"
    doctl apps logs "$app_id" --type="$log_type" --follow
}

# Function to update yaml tags
update_yaml_tags() {
    local tag=$1
    
    print_info "Updating $APP_SPEC_FILE with tag: $tag"
    
    # Update all image tags in app spec file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "/repository: lightclick-frontend/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
        sed -i '' "/repository: lightclick-backend/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
        sed -i '' "/repository: lightclick-worker/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
    else
        # Linux
        sed -i "/repository: lightclick-frontend/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
        sed -i "/repository: lightclick-backend/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
        sed -i "/repository: lightclick-worker/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
    fi
    
    print_success "Updated image tags to $tag"
}

# Function to build and deploy
build_and_deploy() {
    # Generate environment-prefixed tag
    local timestamp="$(date +%Y%m%d-%H%M%S)"
    local tag="${ENVIRONMENT}-v${timestamp}"
    
    print_info "Building and deploying $ENV_LABEL with tag: $tag"
    echo ""
    
    # Build and push images with environment-specific tag
    print_info "Step 1: Building and pushing Docker images..."
    TAG="$tag" "$SCRIPT_DIR/build-and-push.sh" "$ENVIRONMENT"
    
    echo ""
    print_info "Step 2: Updating app spec file..."
    update_yaml_tags "$tag"
    
    echo ""
    print_info "Step 3: Deploying to $ENV_LABEL App Platform..."
    
    # Get app ID
    local app_id
    if [ -f "$APP_ID_FILE" ]; then
        app_id=$(cat "$APP_ID_FILE")
    else
        print_error "App ID not found in $APP_ID_FILE"
        print_error "Create app first: ./deploy.sh create $ENVIRONMENT"
        exit 1
    fi
    
    # Deploy
    update_app "$app_id"
    
    echo ""
    print_success "$ENV_LABEL deployment complete! Tag: $tag"
    print_info "Database migrations will run automatically on backend startup"
}

# Function to show usage
show_usage() {
    echo "DigitalOcean App Platform Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh <command> <environment> [options]"
    echo ""
    echo "Environments (required for most commands):"
    echo "  dev                 Development environment"
    echo "  prod                Production environment"
    echo ""
    echo "Commands:"
    echo "  create <dev|prod>         Create a new app"
    echo "  update <dev|prod>         Update app spec only (no build)"
    echo "  deploy <dev|prod>         Build, push, and deploy all components"
    echo "  list                      List all apps"
    echo "  info <dev|prod>           Get app information"
    echo "  logs <dev|prod> [type]    View logs (BUILD|DEPLOY|RUN)"
    echo "  validate <dev|prod>       Validate app spec without deploying"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh create dev          # Create dev app"
    echo "  ./deploy.sh deploy dev          # Build and deploy to dev"
    echo "  ./deploy.sh deploy prod         # Build and deploy to prod"
    echo "  ./deploy.sh update prod         # Update prod app spec only"
    echo "  ./deploy.sh logs dev BUILD      # View dev build logs"
    echo "  ./deploy.sh validate dev        # Validate dev config"
    echo ""
    echo "Note: App IDs are automatically saved to:"
    echo "  - .do/app-id.txt (prod)"
    echo "  - .do/app-id-dev.txt (dev)"
}

# Main script
main() {
    local command=${1:-}
    
    if [ -z "$command" ]; then
        show_usage
        exit 1
    fi
    
    # Print header
    echo ""
    echo "═══════════════════════════════════════════════"
    echo "  DigitalOcean App Platform Deployment"
    echo "  LightClick Studio"
    echo "═══════════════════════════════════════════════"
    echo ""
    
    case "$command" in
        create)
            set_environment "${2:-}"
            check_doctl
            check_auth
            echo ""
            
            # Build images and update yaml before creating
            local timestamp="$(date +%Y%m%d-%H%M%S)"
            local tag="${ENVIRONMENT}-v${timestamp}"
            
            print_info "Step 1: Building and pushing Docker images..."
            TAG="$tag" "$SCRIPT_DIR/build-and-push.sh" "$ENVIRONMENT"
            
            echo ""
            print_info "Step 2: Updating app spec file..."
            update_yaml_tags "$tag"
            
            echo ""
            check_app_spec
            validate_app_spec
            echo ""
            create_app
            ;;
        update)
            set_environment "${2:-}"
            check_doctl
            check_auth
            check_app_spec
            validate_app_spec
            echo ""
            update_app ""
            ;;
        deploy)
            set_environment "${2:-}"
            check_doctl
            check_auth
            check_app_spec
            echo ""
            build_and_deploy
            ;;
        list)
            check_doctl
            check_auth
            echo ""
            list_apps
            ;;
        info)
            set_environment "${2:-}"
            check_doctl
            check_auth
            echo ""
            get_app_info ""
            ;;
        logs)
            set_environment "${2:-}"
            check_doctl
            check_auth
            echo ""
            view_logs "" "${3:-DEPLOY}"
            ;;
        validate)
            set_environment "${2:-}"
            check_doctl
            check_auth
            check_app_spec
            echo ""
            validate_app_spec
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
}

# Run main function
main "$@"
