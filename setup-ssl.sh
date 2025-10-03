#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP="${SERVER_IP:-159.89.111.179}"
DOMAIN="${DOMAIN}"
EMAIL="${EMAIL}"

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to check if domain is set
check_domain() {
    if [ -z "$DOMAIN" ]; then
        print_error "DOMAIN environment variable is not set!"
        print_info "Usage: DOMAIN=yourdomain.com EMAIL=you@email.com ./setup-ssl.sh"
        exit 1
    fi
    
    if [ -z "$EMAIL" ]; then
        print_error "EMAIL environment variable is not set!"
        print_info "Usage: DOMAIN=yourdomain.com EMAIL=you@email.com ./setup-ssl.sh"
        exit 1
    fi
    
    print_status "Domain: $DOMAIN"
    print_status "Email: $EMAIL"
}

# Function to verify DNS
check_dns() {
    print_info "Checking DNS configuration..."
    
    # Check A record
    DNS_IP=$(dig +short "$DOMAIN" A | head -n1)
    
    if [ -z "$DNS_IP" ]; then
        print_error "DNS A record not found for $DOMAIN"
        print_info "Please configure your DNS:"
        print_info "  A Record: $DOMAIN → $SERVER_IP"
        exit 1
    fi
    
    if [ "$DNS_IP" != "$SERVER_IP" ]; then
        print_warning "DNS points to $DNS_IP, but server is at $SERVER_IP"
        print_info "Please update your DNS to point to $SERVER_IP"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_status "DNS correctly configured"
    fi
}

# Function to generate SSL certificate
generate_certificate() {
    print_info "Generating SSL certificate with Let's Encrypt..."
    
    ssh root@${SERVER_IP} bash -s << ENDSSH
# Stop nginx if running
docker compose -f /home/productsnap/app/docker-compose.yml down nginx 2>/dev/null || true

# Get certificate using certbot
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email ${EMAIL} \
    -d ${DOMAIN} \
    --preferred-challenges http

# Check if certificate was generated
if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    echo "Certificate generation failed!"
    exit 1
fi

# Copy certificates to app directory
mkdir -p /home/productsnap/app/nginx/ssl
cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem /home/productsnap/app/nginx/ssl/
cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem /home/productsnap/app/nginx/ssl/
chown -R productsnap:productsnap /home/productsnap/app/nginx/ssl

echo "Certificate generated successfully!"
ENDSSH
    
    print_status "SSL certificate generated and installed"
}

# Function to update nginx configuration
update_nginx_config() {
    print_info "Updating NGINX configuration for HTTPS..."
    
    # Backup existing config
    ssh productsnap@${SERVER_IP} "cd /home/productsnap/app && cp nginx/conf.d/productsnap.conf nginx/conf.d/productsnap.conf.backup"
    
    # Create new HTTPS-enabled config
    cat << 'EOF' | ssh productsnap@${SERVER_IP} "cat > /home/productsnap/app/nginx/conf.d/productsnap.conf"
# Upstream servers
upstream backend_api {
    server backend:8000;
    keepalive 32;
}

upstream frontend_app {
    server frontend:80;
    keepalive 32;
}

# HTTP Server - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name DOMAIN_PLACEHOLDER;

    # Allow Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all other HTTP traffic to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name DOMAIN_PLACEHOLDER;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # API endpoints
    location /api {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 90s;
        proxy_connect_timeout 90s;
        proxy_send_timeout 90s;
    }

    # Frontend application
    location / {
        proxy_pass http://frontend_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Enable caching for static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            proxy_pass http://frontend_app;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF
    
    # Replace domain placeholder
    ssh productsnap@${SERVER_IP} "sed -i 's/DOMAIN_PLACEHOLDER/${DOMAIN}/g' /home/productsnap/app/nginx/conf.d/productsnap.conf"
    
    print_status "NGINX configuration updated"
}

# Function to restart nginx
restart_nginx() {
    print_info "Restarting NGINX..."
    
    ssh productsnap@${SERVER_IP} << 'ENDSSH'
cd /home/productsnap/app
docker compose restart nginx
sleep 3
docker compose ps nginx
ENDSSH
    
    print_status "NGINX restarted"
}

# Function to set up auto-renewal
setup_auto_renewal() {
    print_info "Setting up certificate auto-renewal..."
    
    ssh root@${SERVER_IP} bash -s << 'ENDSSH'
# Create renewal script
cat > /root/renew-cert.sh << 'SCRIPT'
#!/bin/bash
certbot renew --quiet
if [ -f "/etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem" ]; then
    cp /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/*.pem /home/productsnap/app/nginx/ssl/
    chown -R productsnap:productsnap /home/productsnap/app/nginx/ssl
    docker compose -f /home/productsnap/app/docker-compose.yml restart nginx
fi
SCRIPT

chmod +x /root/renew-cert.sh

# Add to crontab (run daily at 2am)
(crontab -l 2>/dev/null | grep -v "renew-cert.sh"; echo "0 2 * * * /root/renew-cert.sh >> /var/log/cert-renewal.log 2>&1") | crontab -

echo "Auto-renewal configured"
ENDSSH
    
    # Replace domain in renewal script
    ssh root@${SERVER_IP} "sed -i 's/DOMAIN_PLACEHOLDER/${DOMAIN}/g' /root/renew-cert.sh"
    
    print_status "Auto-renewal configured (daily check at 2am)"
}

# Main setup flow
main() {
    echo "=================================================="
    echo "ProductSnap SSL Setup Script"
    echo "=================================================="
    echo ""
    
    # Check domain and email
    check_domain
    
    # Check DNS
    echo ""
    check_dns
    
    # Confirm setup
    echo ""
    print_warning "This will:"
    print_info "  1. Generate Let's Encrypt SSL certificate for $DOMAIN"
    print_info "  2. Update NGINX to use HTTPS"
    print_info "  3. Redirect all HTTP traffic to HTTPS"
    print_info "  4. Set up automatic certificate renewal"
    echo ""
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "SSL setup cancelled"
        exit 0
    fi
    
    # Generate certificate
    echo ""
    generate_certificate
    
    # Update nginx config
    echo ""
    update_nginx_config
    
    # Restart nginx
    echo ""
    restart_nginx
    
    # Setup auto-renewal
    echo ""
    setup_auto_renewal
    
    # Test HTTPS
    echo ""
    print_info "Testing HTTPS connection..."
    sleep 3
    if curl -sf "https://${DOMAIN}/health" > /dev/null; then
        print_status "HTTPS is working!"
    else
        print_warning "HTTPS test failed. Check nginx logs."
    fi
    
    # Summary
    echo ""
    echo "=================================================="
    echo "SSL Setup Complete!"
    echo "=================================================="
    echo ""
    print_status "Your application is now accessible at:"
    print_status "  https://${DOMAIN}"
    print_status "  https://${DOMAIN}/api/docs"
    echo ""
    print_info "Certificate will auto-renew every 60 days"
    echo ""
}

# Run main function
main "$@"
