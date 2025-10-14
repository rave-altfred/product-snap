#!/bin/bash
# DigitalOcean App Platform Deployment Script
# LightClick Studio
# 
# This script deploys the application to DigitalOcean App Platform
# Usage: 
#   ./deploy.sh create              - Create new app
#   ./deploy.sh update              - Update app spec only
#   ./deploy.sh deploy [component]  - Build, push, and deploy (default: all)
#                                     component: frontend, backend, worker, all

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_SPEC_FILE="$SCRIPT_DIR/.do/app.yaml"
REGION="fra"  # Frankfurt

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
    local app_name=${1:-}
    
    print_info "Creating new app from spec..."
    
    if [ -n "$app_name" ]; then
        print_info "App name: $app_name"
    fi
    
    # Create the app
    if doctl apps create --spec "$APP_SPEC_FILE" --format ID,Spec.Name,DefaultIngress --no-header > /tmp/app_create_output.txt; then
        print_success "App created successfully!"
        echo ""
        cat /tmp/app_create_output.txt
        echo ""
        
        # Extract app ID
        APP_ID=$(awk '{print $1}' /tmp/app_create_output.txt)
        
        print_info "App ID: $APP_ID"
        print_info "Save this ID for future updates!"
        
        # Save app ID to file
        echo "$APP_ID" > "$SCRIPT_DIR/.do/app-id.txt"
        print_success "App ID saved to .do/app-id.txt"
        
        echo ""
        print_info "Monitor deployment:"
        echo "  doctl apps list"
        echo "  doctl apps get $APP_ID"
        echo "  doctl apps logs $APP_ID --type=BUILD"
        echo "  doctl apps logs $APP_ID --type=DEPLOY"
        
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
        if [ -f "$SCRIPT_DIR/.do/app-id.txt" ]; then
            app_id=$(cat "$SCRIPT_DIR/.do/app-id.txt")
            print_info "Using saved App ID: $app_id"
        else
            print_error "App ID not provided and not found in .do/app-id.txt"
            echo ""
            echo "Usage: ./deploy.sh update <app-id>"
            echo ""
            list_apps
            exit 1
        fi
    fi
    
    print_info "Updating app: $app_id"
    
    # Update the app
    if doctl apps update "$app_id" --spec "$APP_SPEC_FILE"; then
        print_success "App updated successfully!"
        echo ""
        
        print_info "Monitor deployment:"
        echo "  doctl apps get $app_id"
        echo "  doctl apps logs $app_id --type=BUILD"
        echo "  doctl apps logs $app_id --type=DEPLOY"
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
        if [ -f "$SCRIPT_DIR/.do/app-id.txt" ]; then
            app_id=$(cat "$SCRIPT_DIR/.do/app-id.txt")
        else
            print_error "App ID not provided"
            echo "Usage: ./deploy.sh info <app-id>"
            exit 1
        fi
    fi
    
    print_info "App information:"
    doctl apps get "$app_id"
}

# Function to view logs
view_logs() {
    local app_id=$1
    local log_type=${2:-DEPLOY}
    
    if [ -z "$app_id" ]; then
        if [ -f "$SCRIPT_DIR/.do/app-id.txt" ]; then
            app_id=$(cat "$SCRIPT_DIR/.do/app-id.txt")
        else
            print_error "App ID not provided"
            echo "Usage: ./deploy.sh logs <app-id> [BUILD|DEPLOY|RUN]"
            exit 1
        fi
    fi
    
    print_info "Viewing $log_type logs for app: $app_id"
    doctl apps logs "$app_id" --type="$log_type" --follow
}

# Function to build and deploy
build_and_deploy() {
    local component=${1:-all}
    local tag="v$(date +%Y%m%d-%H%M%S)"
    
    print_info "Building and deploying: $component with tag: $tag"
    echo ""
    
    # Build and push images
    print_info "Step 1: Building and pushing Docker images..."
    TAG="$tag" "$SCRIPT_DIR/build-and-push.sh"
    
    # Update app.yaml with new tags
    print_info "Step 2: Updating app.yaml with new tags..."
    
    if [[ "$component" == "all" ]] || [[ "$component" == "frontend" ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "/repository: lightclick-frontend/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
        else
            sed -i "/repository: lightclick-frontend/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
        fi
        print_success "Updated frontend tag to $tag"
    fi
    
    if [[ "$component" == "all" ]] || [[ "$component" == "backend" ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "/repository: lightclick-backend/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
        else
            sed -i "/repository: lightclick-backend/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
        fi
        print_success "Updated backend tag to $tag"
    fi
    
    if [[ "$component" == "all" ]] || [[ "$component" == "worker" ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "/repository: lightclick-worker/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
        else
            sed -i "/repository: lightclick-worker/{n; s/tag: .*/tag: $tag/;}" "$APP_SPEC_FILE"
        fi
        print_success "Updated worker tag to $tag"
    fi
    
    echo ""
    print_info "Step 3: Deploying to App Platform..."
    
    # Get app ID
    local app_id
    if [ -f "$SCRIPT_DIR/.do/app-id.txt" ]; then
        app_id=$(cat "$SCRIPT_DIR/.do/app-id.txt")
    else
        print_error "App ID not found in .do/app-id.txt"
        exit 1
    fi
    
    # Deploy
    update_app "$app_id"
    
    echo ""
    print_success "Deployment complete! Tag: $tag"
}

# Function to show usage
show_usage() {
    echo "DigitalOcean App Platform Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  create              Create a new app from app.yaml"
    echo "  update [app-id]     Update app spec only (no build)"
    echo "  deploy [component]  Build, push, and deploy with versioned tags"
    echo "                      component: frontend, backend, worker, all (default)"
    echo "  list                List all apps"
    echo "  info [app-id]       Get app information"
    echo "  logs [app-id] [type] View logs (BUILD|DEPLOY|RUN)"
    echo "  validate            Validate app.yaml without deploying"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh create"
    echo "  ./deploy.sh deploy              # Build and deploy all components"
    echo "  ./deploy.sh deploy frontend     # Only frontend"
    echo "  ./deploy.sh update              # Update app spec only"
    echo "  ./deploy.sh logs abc123 BUILD"
    echo "  ./deploy.sh validate"
    echo ""
    echo "Note: App ID is automatically saved to .do/app-id.txt after creation"
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
            check_doctl
            check_auth
            check_app_spec
            validate_app_spec
            echo ""
            create_app "${2:-}"
            ;;
        update)
            check_doctl
            check_auth
            check_app_spec
            validate_app_spec
            echo ""
            update_app "${2:-}"
            ;;
        deploy)
            check_doctl
            check_auth
            check_app_spec
            echo ""
            build_and_deploy "${2:-all}"
            ;;
        list)
            check_doctl
            check_auth
            echo ""
            list_apps
            ;;
        info)
            check_doctl
            check_auth
            echo ""
            get_app_info "${2:-}"
            ;;
        logs)
            check_doctl
            check_auth
            echo ""
            view_logs "${2:-}" "${3:-DEPLOY}"
            ;;
        validate)
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
