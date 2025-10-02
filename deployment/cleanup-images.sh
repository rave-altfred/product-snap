#!/bin/bash

################################################################################
# Docker Image Cleanup Script
# 
# Cleans up old Docker images on both local machine and remote droplet.
# Keeps only the latest tagged images and removes dangling/unused images.
#
# Usage:
#   ./cleanup-images.sh [options]
#
# Options:
#   --local              Clean local images only (default)
#   --remote             Clean remote droplet images only
#   --both               Clean both local and remote
#   -h, --host          Droplet IP (required for remote)
#   -u, --user          SSH user (default: root)
#   -k, --key           SSH key path (default: ~/.ssh/id_rsa)
#   --keep N            Keep N most recent images (default: 2)
#   --dry-run           Show what would be deleted
#   --help              Show this help
#
# Examples:
#   ./cleanup-images.sh --local
#   ./cleanup-images.sh --remote --host 123.45.67.89
#   ./cleanup-images.sh --both --host 123.45.67.89 --keep 3
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
CLEANUP_MODE="local"
SSH_USER="root"
SSH_KEY="$HOME/.ssh/id_rsa"
DROPLET_HOST=""
KEEP_COUNT=2
DRY_RUN="false"
PROJECT_REGISTRY="productsnap"

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗ ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

show_help() {
    grep '^#' "$0" | grep -v '#!/bin/bash' | sed 's/^# //; s/^#//'
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --local)
                CLEANUP_MODE="local"
                shift
                ;;
            --remote)
                CLEANUP_MODE="remote"
                shift
                ;;
            --both)
                CLEANUP_MODE="both"
                shift
                ;;
            -h|--host)
                DROPLET_HOST="$2"
                shift 2
                ;;
            -u|--user)
                SSH_USER="$2"
                shift 2
                ;;
            -k|--key)
                SSH_KEY="$2"
                shift 2
                ;;
            --keep)
                KEEP_COUNT="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --help)
                show_help
                ;;
            *)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Validate
    if [[ "$CLEANUP_MODE" =~ ^(remote|both)$ ]] && [[ -z "$DROPLET_HOST" ]]; then
        error "Droplet host required for remote cleanup. Use --host option."
        exit 1
    fi
}

# Cleanup local images
cleanup_local_images() {
    log "Cleaning up local Docker images..."

    if [[ "$DRY_RUN" == "true" ]]; then
        warning "DRY RUN MODE - No images will be deleted"
    fi

    # Get all productsnap images
    local images=$(docker images "${PROJECT_REGISTRY}/*" --format "{{.Repository}}:{{.Tag}} {{.ID}} {{.CreatedAt}}" 2>/dev/null || true)
    
    if [[ -z "$images" ]]; then
        log "No ProductSnap images found locally"
        return
    fi

    echo "$images" | head -n 10

    # Process each repository separately
    for repo in backend frontend; do
        local full_repo="${PROJECT_REGISTRY}/${repo}"
        
        log "Processing ${full_repo}..."
        
        # Get images for this repo, excluding 'latest' tag
        local repo_images=$(docker images "$full_repo" --format "{{.ID}} {{.Tag}}" | grep -v "latest" || true)
        
        if [[ -z "$repo_images" ]]; then
            log "  No tagged images to clean"
            continue
        fi

        # Count images
        local image_count=$(echo "$repo_images" | wc -l | tr -d ' ')
        log "  Found $image_count tagged images"

        # Skip if within keep limit
        if [[ $image_count -le $KEEP_COUNT ]]; then
            log "  Keeping all (within limit of $KEEP_COUNT)"
            continue
        fi

        # Get images to remove (all except the N most recent)
        local to_remove=$(echo "$repo_images" | tail -n +$((KEEP_COUNT + 1)) | awk '{print $1}')
        local remove_count=$(echo "$to_remove" | wc -l | tr -d ' ')

        if [[ -n "$to_remove" ]]; then
            log "  Removing $remove_count old images (keeping $KEEP_COUNT most recent)"
            
            if [[ "$DRY_RUN" == "true" ]]; then
                echo "$to_remove" | while read -r img_id; do
                    echo "    [DRY RUN] Would remove: $img_id"
                done
            else
                echo "$to_remove" | xargs -r docker rmi -f 2>/dev/null || {
                    warning "  Some images could not be removed (may be in use)"
                }
                success "  Removed old ${repo} images"
            fi
        fi
    done

    # Clean up dangling images
    log "Removing dangling images..."
    local dangling=$(docker images -f "dangling=true" -q)
    
    if [[ -n "$dangling" ]]; then
        local dangling_count=$(echo "$dangling" | wc -l | tr -d ' ')
        
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "  [DRY RUN] Would remove $dangling_count dangling images"
        else
            docker image prune -f > /dev/null 2>&1
            success "Removed $dangling_count dangling images"
        fi
    else
        log "  No dangling images found"
    fi

    # Show final status
    log "Local images after cleanup:"
    docker images "${PROJECT_REGISTRY}/*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null || true

    success "Local cleanup completed"
}

# Cleanup remote images
cleanup_remote_images() {
    log "Cleaning up remote Docker images on $DROPLET_HOST..."

    if [[ "$DRY_RUN" == "true" ]]; then
        warning "DRY RUN MODE - No images will be deleted"
    fi

    # Create cleanup script to run on remote
    local cleanup_script=$(cat <<REMOTE_SCRIPT
#!/bin/bash
set -e

KEEP_COUNT=$KEEP_COUNT
DRY_RUN=$DRY_RUN
PROJECT_REGISTRY="$PROJECT_REGISTRY"

echo "Starting remote cleanup..."
echo "Keep count: \$KEEP_COUNT"

# Cleanup function
for repo in backend frontend; do
    full_repo="\${PROJECT_REGISTRY}/\${repo}"
    echo "Processing \${full_repo}..."
    
    # Get non-latest images
    repo_images=\$(docker images "\$full_repo" --format "{{.ID}} {{.Tag}}" | grep -v "latest" || true)
    
    if [[ -z "\$repo_images" ]]; then
        echo "  No tagged images to clean"
        continue
    fi
    
    image_count=\$(echo "\$repo_images" | wc -l | tr -d ' ')
    echo "  Found \$image_count tagged images"
    
    if [[ \$image_count -le \$KEEP_COUNT ]]; then
        echo "  Keeping all (within limit)"
        continue
    fi
    
    # Remove old images
    to_remove=\$(echo "\$repo_images" | tail -n +\$((\$KEEP_COUNT + 1)) | awk '{print \$1}')
    
    if [[ -n "\$to_remove" ]]; then
        if [[ "\$DRY_RUN" == "true" ]]; then
            echo "  [DRY RUN] Would remove old images"
        else
            echo "\$to_remove" | xargs -r docker rmi -f 2>/dev/null || true
            echo "  ✓ Removed old \${repo} images"
        fi
    fi
done

# Clean dangling
echo "Removing dangling images..."
if [[ "\$DRY_RUN" == "true" ]]; then
    dangling_count=\$(docker images -f "dangling=true" -q | wc -l)
    echo "  [DRY RUN] Would remove \$dangling_count dangling images"
else
    docker image prune -f > /dev/null 2>&1
    echo "  ✓ Removed dangling images"
fi

# Show final status
echo "Remote images after cleanup:"
docker images "\${PROJECT_REGISTRY}/*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "No images found"

echo "Remote cleanup completed"
REMOTE_SCRIPT
)

    # Execute on remote
    if [[ "$DRY_RUN" == "true" ]]; then
        log "[DRY RUN] Would execute cleanup on remote host"
        echo "$cleanup_script" | head -n 20
        echo "..."
    else
        ssh -i "$SSH_KEY" "$SSH_USER@$DROPLET_HOST" "bash -s" <<< "$cleanup_script"
        success "Remote cleanup completed"
    fi
}

# Show disk space
show_disk_usage() {
    local location="$1"
    
    if [[ "$location" == "local" ]]; then
        log "Local Docker disk usage:"
        docker system df
    else
        log "Remote Docker disk usage:"
        ssh -i "$SSH_KEY" "$SSH_USER@$DROPLET_HOST" "docker system df" || true
    fi
}

main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║         Docker Image Cleanup Script                       ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    parse_args "$@"

    # Show initial disk usage
    if [[ "$CLEANUP_MODE" =~ ^(local|both)$ ]]; then
        show_disk_usage "local"
        echo ""
    fi

    # Perform cleanup
    case "$CLEANUP_MODE" in
        local)
            cleanup_local_images
            ;;
        remote)
            cleanup_remote_images
            ;;
        both)
            cleanup_local_images
            echo ""
            cleanup_remote_images
            ;;
    esac

    echo ""
    success "Cleanup completed! 🧹"
    echo ""
}

main "$@"
