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
DOMAIN="${APP_DOMAIN:-}"
EMAIL="${LETSENCRYPT_EMAIL:-}"
DB_HOST="${DB_HOST:-}"

# Use domain if set, otherwise fall back to IP
CONNECTION_HOST="${DOMAIN:-$DROPLET_IP}"

echo "Preparing droplet: $DROPLET_NAME"
echo "Connection: $CONNECTION_HOST"
if [ -z "$DOMAIN" ]; then
    echo "⚠️  Warning: Using IP address. Set APP_DOMAIN for production."
fi
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
if [ -n "$DOMAIN" ] && [ -n "$EMAIL" ]; then
    echo ""
    echo "=== Configuring Let's Encrypt SSL ==="
    echo "Domain: $DOMAIN"
    
    ssh root@$CONNECTION_HOST << EOF
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect
EOF
    
    echo "✓ SSL certificates configured successfully"
fi

# Add droplet IP to database authorized sources if DB_HOST is set
if [ -n "$DB_HOST" ]; then
    echo ""
    echo "=== Adding droplet to database authorized sources ==="
    
    # Check if using DigitalOcean Managed Database
    if command -v doctl &> /dev/null; then
        echo "Attempting to add trusted source to DigitalOcean database..."
        
        # Get database info
        DB_ID="${DB_ID:-}"
        
        if [ -n "$DB_ID" ]; then
            doctl databases firewalls append "$DB_ID" --rule "ip_addr:$DROPLET_IP"
            echo "✓ Added $DROPLET_IP to database trusted sources"
        else
            echo "Warning: DB_ID not set. Please manually add $DROPLET_IP to your database firewall:"
            echo "doctl databases firewalls append <db-id> --rule \"ip_addr:$DROPLET_IP\""
        fi
    else
        echo "Note: Add $DROPLET_IP to your database authorized sources manually."
    fi
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
