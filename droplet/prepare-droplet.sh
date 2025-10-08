#!/bin/bash
set -e

# DigitalOcean Droplet Preparation Script
# Configures HTTPS, SSH, Let's Encrypt certificates, and database access

# Load droplet info
if [ ! -f "droplet/droplet-info.env" ]; then
    echo "Error: droplet-info.env not found. Please run create-droplet.sh first."
    exit 1
fi

source droplet/droplet-info.env

# Configuration
DOMAIN="${DOMAIN:-utils.studio}"
SUBDOMAIN="${SUBDOMAIN:-lightclick}"
FULL_DOMAIN="$SUBDOMAIN.$DOMAIN"
EMAIL="${LETSENCRYPT_EMAIL:-}"
DB_ID="${DB_ID:-}"

echo "Preparing droplet: $DROPLET_NAME (ID: $DROPLET_ID)"
echo ""

# Reserve and assign floating IP
FLOATING_IP=""
echo "=== Floating IP Setup ==="
echo "Reserving floating IP in $REGION..."
FLOATING_IP=$(doctl compute floating-ip create --region "$REGION" --format IP --no-header 2>&1)

if [ -n "$FLOATING_IP" ] && [[ ! "$FLOATING_IP" =~ "Error" ]]; then
    echo "✓ Floating IP reserved: $FLOATING_IP"
    
    echo "Assigning floating IP to droplet..."
    doctl compute floating-ip-action assign "$FLOATING_IP" "$DROPLET_ID" --wait
    echo "✓ Floating IP assigned to droplet"
    
    # Update droplet IP to floating IP
    DROPLET_IP="$FLOATING_IP"
    
    # Update droplet-info.env with floating IP
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cat > "$SCRIPT_DIR/droplet-info.env" << EOF
DROPLET_ID=$DROPLET_ID
DROPLET_NAME=$DROPLET_NAME
DROPLET_IP=$DROPLET_IP
FLOATING_IP=$FLOATING_IP
REGION=$REGION
DOMAIN=$DOMAIN
SUBDOMAIN=$SUBDOMAIN
FULL_DOMAIN=$FULL_DOMAIN
CREATED_AT=$(grep CREATED_AT "$SCRIPT_DIR/droplet-info.env" | cut -d= -f2)
EOF
    echo "✓ Droplet info updated with floating IP"
else
    echo "Warning: Failed to reserve floating IP. Using droplet IP: $DROPLET_IP"
fi

echo ""
echo "=== DNS Setup ==="
echo "Setting up DNS for $FULL_DOMAIN..."

# Check if DNS record already exists
EXISTING_RECORD=$(doctl compute domain records list "$DOMAIN" --format ID,Type,Name,Data --no-header 2>/dev/null | grep -E "^[0-9]+\s+A\s+$SUBDOMAIN\s+" | awk '{print $1}')

if [ -n "$EXISTING_RECORD" ]; then
    echo "Updating existing DNS record..."
    doctl compute domain records update "$DOMAIN" --record-id "$EXISTING_RECORD" --record-data "$DROPLET_IP"
    echo "✓ DNS record updated: $FULL_DOMAIN -> $DROPLET_IP"
else
    echo "Creating DNS record..."
    doctl compute domain records create "$DOMAIN" --record-type A --record-name "$SUBDOMAIN" --record-data "$DROPLET_IP" --record-ttl 3600
    echo "✓ DNS record created: $FULL_DOMAIN -> $DROPLET_IP"
fi

echo ""
echo "Domain: https://$FULL_DOMAIN"
echo "Note: DNS propagation may take a few minutes"
echo ""

# Use domain for connection
CONNECTION_HOST="$DROPLET_IP"

echo "=== Droplet Configuration ==="
echo "Connecting to: $CONNECTION_HOST"
echo ""

if [ -z "$DOMAIN" ]; then
    echo "Warning: APP_DOMAIN not set. SSL certificates will not be configured."
    echo "Set APP_DOMAIN environment variable to enable HTTPS."
fi

if [ -z "$EMAIL" ]; then
    echo "Warning: LETSENCRYPT_EMAIL not set. Required for Let's Encrypt."
fi

# Create preparation script to run on droplet
cat > /tmp/prepare-script.sh << 'SCRIPT_EOF'
#!/bin/bash
set -e

echo "=== System Update ==="
apt-get update
apt-get upgrade -y

echo "=== Installing Essential Packages ==="
apt-get install -y \
    curl \
    wget \
    git \
    ufw \
    fail2ban \
    nginx \
    certbot \
    python3-certbot-nginx \
    docker.io \
    docker-compose

# Enable and start Docker
systemctl enable docker
systemctl start docker

echo "=== Configuring Firewall (UFW) ==="
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw status

echo "=== Configuring Fail2Ban ==="
systemctl enable fail2ban
systemctl start fail2ban

echo "=== Hardening SSH ==="
# Backup original sshd_config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Update SSH configuration
sed -i 's/#PermitRootLogin yes/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Restart SSH
systemctl restart sshd

echo "=== Setting up Docker registry authentication ==="
mkdir -p /root/.docker

echo "=== Creating deployment directory ==="
mkdir -p /opt/product-snap
chown root:root /opt/product-snap
chmod 755 /opt/product-snap

echo "=== Basic Nginx configuration ==="
# Create default configuration
cat > /etc/nginx/sites-available/default << 'NGINX_EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
NGINX_EOF

# Test nginx configuration
nginx -t

# Reload nginx
systemctl reload nginx

echo "=== Droplet preparation complete ==="
SCRIPT_EOF

echo "Uploading and executing preparation script..."
scp -o StrictHostKeyChecking=no /tmp/prepare-script.sh root@$CONNECTION_HOST:/tmp/prepare-script.sh
ssh -o StrictHostKeyChecking=no root@$CONNECTION_HOST "chmod +x /tmp/prepare-script.sh && /tmp/prepare-script.sh"

# Configure Let's Encrypt if domain is set
if [ -n "$FULL_DOMAIN" ] && [ -n "$EMAIL" ]; then
    echo ""
    echo "=== Configuring Let's Encrypt SSL ==="
    echo "Domain: $FULL_DOMAIN"
    
    ssh root@$CONNECTION_HOST << EOF
certbot --nginx -d $FULL_DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect
EOF
    
    echo "✓ SSL certificates configured successfully"
else
    echo ""
    echo "Warning: LETSENCRYPT_EMAIL not set. SSL certificates not configured."
    echo "Set LETSENCRYPT_EMAIL and run certbot manually later."
fi

# Add droplet IP to database authorized sources if DB_ID is set
if [ -n "$DB_ID" ]; then
    echo ""
    echo "=== Adding droplet to database authorized sources ==="
    echo "Adding $DROPLET_IP to database firewall..."
    
    doctl databases firewalls append "$DB_ID" --rule "ip_addr:$DROPLET_IP"
    echo "✓ Added $DROPLET_IP to database trusted sources"
else
    echo ""
    echo "Note: DB_ID not set. If using DigitalOcean managed database, add droplet IP manually:"
    echo "doctl databases firewalls append <db-id> --rule \"ip_addr:$DROPLET_IP\""
fi

echo ""
echo "✓ Droplet preparation complete!"
echo ""
echo "Droplet is now configured with:"
echo "  - Updated system packages"
echo "  - Docker and Docker Compose"
echo "  - Nginx reverse proxy"
echo "  - UFW firewall (ports 22, 80, 443 open)"
echo "  - Fail2Ban for SSH protection"
echo "  - Hardened SSH configuration"
if [ -n "$DOMAIN" ]; then
    echo "  - Let's Encrypt SSL certificate for $DOMAIN"
fi
echo ""
echo "Next steps:"
echo "1. Configure Docker registry credentials on the droplet"
echo "2. Run ./droplet/build.sh to build your Docker images"
echo "3. Run ./droplet/push.sh to push to DigitalOcean Container Registry"
echo "4. Run ./droplet/deploy.sh to deploy your application"
