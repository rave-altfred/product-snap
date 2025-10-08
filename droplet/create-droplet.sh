#!/bin/bash
set -e

# DigitalOcean Droplet Creation Script
# Creates a minimal droplet (can be resized later)

# Configuration
DROPLET_NAME="${DROPLET_NAME:-product-snap-app}"
REGION="${DO_REGION:-fra1}"
SIZE="${DO_SIZE:-s-1vcpu-1gb}"  # Minimal size
IMAGE="${DO_IMAGE:-ubuntu-22-04-x64}"
SSH_KEYS="${DO_SSH_KEYS:-}"  # Comma-separated list of SSH key IDs

echo "Creating DigitalOcean droplet..."
echo "Name: $DROPLET_NAME"
echo "Region: $REGION"
echo "Size: $SIZE"
echo "Image: $IMAGE"

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "Error: doctl is not installed. Please install it first:"
    echo "brew install doctl"
    exit 1
fi

# Check if authenticated
if ! doctl account get &> /dev/null; then
    echo "Error: Not authenticated with DigitalOcean. Please run:"
    echo "doctl auth init"
    exit 1
fi

# Get SSH keys if not specified
if [ -z "$SSH_KEYS" ]; then
    echo "Fetching SSH keys..."
    SSH_KEYS=$(doctl compute ssh-key list --format ID --no-header | tr '\n' ',' | sed 's/,$//')
fi

# Create the droplet
echo "Creating droplet..."
DROPLET_OUTPUT=$(doctl compute droplet create "$DROPLET_NAME" \
    --region "$REGION" \
    --size "$SIZE" \
    --image "$IMAGE" \
    --ssh-keys "$SSH_KEYS" \
    --enable-monitoring \
    --enable-ipv6 \
    --tag-names product-snap,app \
    --format ID,Name,PublicIPv4,Status \
    --no-header \
    --wait)

DROPLET_ID=$(echo "$DROPLET_OUTPUT" | awk '{print $1}')
DROPLET_IP=$(echo "$DROPLET_OUTPUT" | awk '{print $3}')

echo ""
echo "✓ Droplet created successfully!"
echo "Droplet ID: $DROPLET_ID"
echo "IP Address: $DROPLET_IP (temporary - use domain or reserved IP)"
echo ""
echo "Saving droplet info..."

# Save droplet info to file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat > "$SCRIPT_DIR/droplet-info.env" << EOF
DROPLET_ID=$DROPLET_ID
DROPLET_NAME=$DROPLET_NAME
DROPLET_IP=$DROPLET_IP
CREATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

echo "Droplet info saved to droplet/droplet-info.env"
echo ""
echo "⚠️  IMPORTANT: This IP is not fixed and may change if droplet is destroyed."
echo ""
echo "For production, you should:"
echo "1. Reserve a Floating IP: doctl compute floating-ip create --region fra1"
echo "2. Assign it to droplet: doctl compute floating-ip-action assign <floating-ip> $DROPLET_ID"
echo "3. Point your domain to the floating IP"
echo "4. Set APP_DOMAIN environment variable to your domain"
echo ""
echo "Next steps:"
echo "1. Wait a few moments for the droplet to fully initialize"
echo "2. (Optional) Reserve and assign a floating IP"
echo "3. Point your domain DNS to the IP"
echo "4. Run: APP_DOMAIN=yourdomain.com ./droplet/prepare-droplet.sh"
