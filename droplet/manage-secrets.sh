#!/bin/bash
set -e

# Docker Secrets Management Script
# Manages Docker Swarm secrets for ProductSnap deployment

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ENV_FILE:-$SCRIPT_DIR/.env.production}"
PROJECT_NAME="${PROJECT_NAME:-productsnap}"

# Secret definitions: env_var_name:secret_name
SECRETS=(
    "JWT_SECRET:jwt_secret"
    "PAYPAL_CLIENT_SECRET:paypal_client_secret"
    "NANO_BANANA_API_KEY:nano_banana_api_key"
    "S3_SECRET_KEY:s3_secret_key"
    "SMTP_PASSWORD:smtp_password"
    "GOOGLE_CLIENT_SECRET:google_client_secret"
)

# Optional secrets (won't fail if missing)
OPTIONAL_SECRETS=(
    "GOOGLE_CLIENT_SECRET"
)

show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  create      Create all secrets from .env.production"
    echo "  update      Update specific secret(s)"
    echo "  list        List all secrets"
    echo "  delete      Delete specific secret(s)"
    echo "  inspect     Inspect secret details (without showing value)"
    echo "  verify      Verify all required secrets exist"
    echo ""
    echo "Options:"
    echo "  -f FILE     Specify env file (default: .env.production)"
    echo "  -p PREFIX   Specify secret name prefix (default: productsnap)"
    echo "  -s SECRET   Specify secret name(s) for update/delete"
    echo ""
    echo "Examples:"
    echo "  $0 create"
    echo "  $0 update -s jwt_secret"
    echo "  $0 update -s jwt_secret -s s3_secret_key"
    echo "  $0 list"
    echo "  $0 verify"
    echo "  $0 delete -s old_secret"
}

# Parse secret value from env file
get_env_value() {
    local key="$1"
    local value=""
    
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}Error: $ENV_FILE not found${NC}" >&2
        return 1
    fi
    
    # Read value from env file
    while IFS='=' read -r env_key env_value; do
        # Skip comments and empty lines
        [[ "$env_key" =~ ^#.*$ || -z "$env_key" ]] && continue
        
        # Remove leading/trailing whitespace
        env_key=$(echo "$env_key" | xargs)
        env_value=$(echo "$env_value" | xargs)
        
        if [ "$env_key" = "$key" ]; then
            value="$env_value"
            break
        fi
    done < "$ENV_FILE"
    
    echo "$value"
}

# Check if secret is optional
is_optional() {
    local key="$1"
    for optional in "${OPTIONAL_SECRETS[@]}"; do
        if [ "$optional" = "$key" ]; then
            return 0
        fi
    done
    return 1
}

# Create a single secret
create_secret() {
    local env_var="$1"
    local secret_name="$2"
    local full_secret_name="${PROJECT_NAME}_${secret_name}"
    
    echo -n "  Creating $full_secret_name... "
    
    # Get value from env file
    value=$(get_env_value "$env_var")
    
    if [ -z "$value" ]; then
        if is_optional "$env_var"; then
            echo -e "${YELLOW}SKIPPED (optional)${NC}"
            return 0
        else
            echo -e "${RED}FAILED (no value in $ENV_FILE)${NC}"
            return 1
        fi
    fi
    
    # Check if secret already exists
    if docker secret inspect "$full_secret_name" &> /dev/null; then
        echo -e "${YELLOW}EXISTS (use update to change)${NC}"
        return 0
    fi
    
    # Create secret
    if echo "$value" | docker secret create "$full_secret_name" - &> /dev/null; then
        echo -e "${GREEN}✓ CREATED${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Update a secret (delete and recreate)
update_secret() {
    local env_var="$1"
    local secret_name="$2"
    local full_secret_name="${PROJECT_NAME}_${secret_name}"
    
    echo -n "  Updating $full_secret_name... "
    
    # Get value from env file
    value=$(get_env_value "$env_var")
    
    if [ -z "$value" ]; then
        echo -e "${RED}FAILED (no value in $ENV_FILE)${NC}"
        return 1
    fi
    
    # Remove existing secret if it exists
    if docker secret inspect "$full_secret_name" &> /dev/null; then
        docker secret rm "$full_secret_name" &> /dev/null || true
    fi
    
    # Create new secret
    if echo "$value" | docker secret create "$full_secret_name" - &> /dev/null; then
        echo -e "${GREEN}✓ UPDATED${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Delete a secret
delete_secret() {
    local secret_name="$1"
    local full_secret_name="${PROJECT_NAME}_${secret_name}"
    
    echo -n "  Deleting $full_secret_name... "
    
    if docker secret rm "$full_secret_name" &> /dev/null; then
        echo -e "${GREEN}✓ DELETED${NC}"
    else
        echo -e "${RED}✗ FAILED (may not exist)${NC}"
        return 1
    fi
}

# List all secrets
list_secrets() {
    echo -e "${BLUE}=== Docker Secrets ===${NC}"
    echo ""
    docker secret ls --filter "name=${PROJECT_NAME}_"
}

# Inspect secret
inspect_secret() {
    local secret_name="$1"
    local full_secret_name="${PROJECT_NAME}_${secret_name}"
    
    echo -e "${BLUE}=== Secret: $full_secret_name ===${NC}"
    docker secret inspect "$full_secret_name"
}

# Verify all secrets exist
verify_secrets() {
    echo -e "${BLUE}=== Verifying Secrets ===${NC}"
    echo ""
    
    local missing=0
    for secret_def in "${SECRETS[@]}"; do
        IFS=':' read -r env_var secret_name <<< "$secret_def"
        full_secret_name="${PROJECT_NAME}_${secret_name}"
        
        if docker secret inspect "$full_secret_name" &> /dev/null; then
            echo -e "  ${GREEN}✓${NC} $full_secret_name"
        else
            if is_optional "$env_var"; then
                echo -e "  ${YELLOW}○${NC} $full_secret_name (optional, not set)"
            else
                echo -e "  ${RED}✗${NC} $full_secret_name (MISSING)"
                missing=$((missing + 1))
            fi
        fi
    done
    
    echo ""
    if [ $missing -gt 0 ]; then
        echo -e "${RED}$missing required secret(s) missing${NC}"
        return 1
    else
        echo -e "${GREEN}All required secrets present${NC}"
        return 0
    fi
}

# Main command handling
COMMAND="${1:-}"
shift || true

# Parse options
SPECIFIC_SECRETS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            ENV_FILE="$2"
            shift 2
            ;;
        -p|--prefix)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -s|--secret)
            SPECIFIC_SECRETS+=("$2")
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

case "$COMMAND" in
    create)
        echo -e "${BLUE}=== Creating Secrets from $ENV_FILE ===${NC}"
        echo ""
        
        if [ ! -f "$ENV_FILE" ]; then
            echo -e "${RED}Error: $ENV_FILE not found${NC}"
            exit 1
        fi
        
        failed=0
        for secret_def in "${SECRETS[@]}"; do
            IFS=':' read -r env_var secret_name <<< "$secret_def"
            create_secret "$env_var" "$secret_name" || failed=$((failed + 1))
        done
        
        echo ""
        if [ $failed -gt 0 ]; then
            echo -e "${RED}Failed to create $failed secret(s)${NC}"
            exit 1
        else
            echo -e "${GREEN}All secrets created successfully${NC}"
        fi
        ;;
        
    update)
        echo -e "${BLUE}=== Updating Secrets ===${NC}"
        echo ""
        
        if [ ${#SPECIFIC_SECRETS[@]} -eq 0 ]; then
            echo -e "${RED}Error: Specify secret(s) to update with -s${NC}"
            echo "Example: $0 update -s jwt_secret -s s3_secret_key"
            exit 1
        fi
        
        for target_secret in "${SPECIFIC_SECRETS[@]}"; do
            found=0
            for secret_def in "${SECRETS[@]}"; do
                IFS=':' read -r env_var secret_name <<< "$secret_def"
                if [ "$secret_name" = "$target_secret" ]; then
                    update_secret "$env_var" "$secret_name"
                    found=1
                    break
                fi
            done
            
            if [ $found -eq 0 ]; then
                echo -e "  ${RED}Unknown secret: $target_secret${NC}"
            fi
        done
        ;;
        
    delete)
        if [ ${#SPECIFIC_SECRETS[@]} -eq 0 ]; then
            echo -e "${RED}Error: Specify secret(s) to delete with -s${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}WARNING: Deleting secrets${NC}"
        echo "This will delete the following secrets:"
        for secret in "${SPECIFIC_SECRETS[@]}"; do
            echo "  - ${PROJECT_NAME}_$secret"
        done
        read -p "Are you sure? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            echo "Aborted"
            exit 0
        fi
        
        echo ""
        for secret in "${SPECIFIC_SECRETS[@]}"; do
            delete_secret "$secret"
        done
        ;;
        
    list)
        list_secrets
        ;;
        
    inspect)
        if [ ${#SPECIFIC_SECRETS[@]} -eq 0 ]; then
            echo -e "${RED}Error: Specify secret to inspect with -s${NC}"
            exit 1
        fi
        
        for secret in "${SPECIFIC_SECRETS[@]}"; do
            inspect_secret "$secret"
            echo ""
        done
        ;;
        
    verify)
        verify_secrets
        ;;
        
    "")
        echo -e "${RED}Error: No command specified${NC}"
        echo ""
        show_usage
        exit 1
        ;;
        
    *)
        echo -e "${RED}Error: Unknown command: $COMMAND${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac
