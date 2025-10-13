#!/bin/bash
set -e

# DigitalOcean Droplet Preparation Script
# Configures HTTPS, SSH, Let's Encrypt certificates, and database access
# This script is idempotent and can be run multiple times safely

# Load config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/config.env" ]; then
    source "$SCRIPT_DIR/config.env"
fi

# Load droplet info
if [ ! -f "$SCRIPT_DIR/droplet-info.env" ]; then
    echo "Error: droplet-info.env not found. Please run create-droplet.sh first."
    exit 1
fi
source "$SCRIPT_DIR/droplet-info.env"

# Configuration (can be overridden by environment variables)
DOMAIN="${DOMAIN:-lightclick.studio}"
SUBDOMAIN="${SUBDOMAIN:-@}"

# Handle root domain vs subdomain
if [ "$SUBDOMAIN" = "@" ] || [ "$SUBDOMAIN" = "" ]; then
    FULL_DOMAIN="$DOMAIN"
else
    FULL_DOMAIN="$SUBDOMAIN.$DOMAIN"
fi
EMAIL="${LETSENCRYPT_EMAIL:-}"
DB_ID="${DB_ID:-}"

echo "Preparing droplet: $DROPLET_NAME (ID: $DROPLET_ID)"
echo ""

# Check if floating IP already exists
echo "=== Floating IP Setup ==="
if [ -n "$FLOATING_IP" ] && [ "$FLOATING_IP" != "$DROPLET_IP" ]; then
    echo "✓ Floating IP already configured: $FLOATING_IP"
    DROPLET_IP="$FLOATING_IP"
else
    echo "Checking for existing floating IP assignment..."
    # Check if droplet already has a floating IP
    EXISTING_FLOATING=$(doctl compute droplet get "$DROPLET_ID" --format "Public IPv4" --no-header 2>/dev/null || echo "")
    
    if [ -n "$EXISTING_FLOATING" ]; then
        echo "✓ Droplet already has IP: $EXISTING_FLOATING"
        FLOATING_IP="$EXISTING_FLOATING"
        DROPLET_IP="$EXISTING_FLOATING"
        
        # Update droplet-info.env
        sed -i.bak "s/^FLOATING_IP=.*/FLOATING_IP=$FLOATING_IP/" "$SCRIPT_DIR/droplet-info.env"
        sed -i.bak "s/^DROPLET_IP=.*/DROPLET_IP=$DROPLET_IP/" "$SCRIPT_DIR/droplet-info.env"
        rm -f "$SCRIPT_DIR/droplet-info.env.bak"
    else
        echo "No floating IP found. Using direct droplet IP: $DROPLET_IP"
        echo "Note: To add a floating IP later, reserve one manually and update droplet-info.env"
    fi
fi

echo ""
echo "=== DNS Setup ==="
echo "Setting up DNS for $FULL_DOMAIN..."

# Determine DNS record name for doctl
if [ "$SUBDOMAIN" = "@" ]; then
    DNS_RECORD_NAME="@"
    SEARCH_PATTERN="^[0-9]+\s+A\s+@\s+"
else
    DNS_RECORD_NAME="$SUBDOMAIN"
    SEARCH_PATTERN="^[0-9]+\s+A\s+$SUBDOMAIN\s+"
fi

# Check if DNS record already exists
EXISTING_RECORD=$(doctl compute domain records list "$DOMAIN" --format ID,Type,Name,Data --no-header 2>/dev/null | grep -E "$SEARCH_PATTERN" | awk '{print $1}')

if [ -n "$EXISTING_RECORD" ]; then
    echo "Updating existing DNS record..."
    doctl compute domain records update "$DOMAIN" --record-id "$EXISTING_RECORD" --record-data "$DROPLET_IP"
    echo "✓ DNS record updated: $FULL_DOMAIN -> $DROPLET_IP"
else
    echo "Creating DNS record..."
    doctl compute domain records create "$DOMAIN" --record-type A --record-name "$DNS_RECORD_NAME" --record-data "$DROPLET_IP" --record-ttl 3600
    echo "✓ DNS record created: $FULL_DOMAIN -> $DROPLET_IP"
fi

# Also create www subdomain if we're setting up root domain
if [ "$SUBDOMAIN" = "@" ]; then
    echo "Setting up www subdomain..."
    WWW_RECORD=$(doctl compute domain records list "$DOMAIN" --format ID,Type,Name,Data --no-header 2>/dev/null | grep -E "^[0-9]+\s+A\s+www\s+" | awk '{print $1}')
    
    if [ -n "$WWW_RECORD" ]; then
        echo "Updating existing www DNS record..."
        doctl compute domain records update "$DOMAIN" --record-id "$WWW_RECORD" --record-data "$DROPLET_IP"
        echo "✓ www DNS record updated: www.$DOMAIN -> $DROPLET_IP"
    else
        echo "Creating www DNS record..."
        doctl compute domain records create "$DOMAIN" --record-type A --record-name "www" --record-data "$DROPLET_IP" --record-ttl 3600
        echo "✓ www DNS record created: www.$DOMAIN -> $DROPLET_IP"
    fi
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
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"

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
echo "Configuring Docker..."
systemctl enable docker || true
if ! systemctl is-active --quiet docker; then
    systemctl start docker
    echo "✓ Docker started"
else
    echo "✓ Docker already running"
fi

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
# Create temporary HTTP-only configuration for certbot
cat > /etc/nginx/sites-available/default << 'NGINX_EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    # For Let's Encrypt challenges
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
NGINX_EOF

# Create certbot webroot
mkdir -p /var/www/certbot

# Test nginx configuration
nginx -t

# Enable and start nginx
systemctl enable nginx || true
if systemctl is-active --quiet nginx; then
    systemctl reload nginx
    echo "✓ Nginx reloaded"
else
    systemctl start nginx
    echo "✓ Nginx started"
fi

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
    echo "Email: $EMAIL"
    
    # Run certbot to get certificates for both root and www
    if [ "$SUBDOMAIN" = "@" ]; then
        echo "Obtaining certificates for both $FULL_DOMAIN and www.$DOMAIN..."
        ssh root@$CONNECTION_HOST "certbot --nginx -d $FULL_DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL"
    else
        echo "Obtaining certificate for $FULL_DOMAIN..."
        ssh root@$CONNECTION_HOST "certbot --nginx -d $FULL_DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect"
    fi
    
    if [ $? -eq 0 ]; then
        echo "✓ SSL certificates obtained"
        
        # Deploy production nginx configuration with SSL
        if [ -f "$SCRIPT_DIR/../nginx/productsnap-system.conf" ]; then
            echo "Deploying production nginx configuration..."
            scp -o StrictHostKeyChecking=no "$SCRIPT_DIR/../nginx/productsnap-system.conf" root@$CONNECTION_HOST:/etc/nginx/sites-available/productsnap.conf
            
            ssh root@$CONNECTION_HOST << 'NGINX_PROD_EOF'
# Enable production config
ln -sf /etc/nginx/sites-available/productsnap.conf /etc/nginx/sites-enabled/productsnap.conf

# Remove default
rm -f /etc/nginx/sites-enabled/default

# Test and reload
nginx -t && systemctl reload nginx
NGINX_PROD_EOF
            
            echo "✓ Production nginx configuration deployed"
        fi
        
        echo "✓ SSL setup complete - site available at https://$FULL_DOMAIN"
    else
        echo "Warning: SSL certificate setup failed. Site running on HTTP only."
    fi
else
    echo ""
    echo "Warning: LETSENCRYPT_EMAIL not set. SSL certificates not configured."
    echo "Set LETSENCRYPT_EMAIL in config.env and re-run this script."
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
