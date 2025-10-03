#!/bin/bash
set -e

# Make script fully non-interactive
export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_MODE=a
export NEEDRESTART_SUSPEND=1

echo "=================================================="
echo "ProductSnap Server Setup Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Update system
echo ""
echo "Step 1: Updating system packages..."
apt update && apt upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"
print_status "System updated"

# Install essential packages
echo ""
echo "Step 2: Installing essential packages..."
apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    ufw \
    git \
    vim \
    htop \
    unzip \
    certbot
print_status "Essential packages installed"

# Install Docker
echo ""
echo "Step 3: Installing Docker..."
if ! command -v docker &> /dev/null; then
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    print_status "Docker installed and started"
else
    print_warning "Docker already installed"
fi

# Verify Docker installation
docker --version
docker compose version

# Configure firewall
echo ""
echo "Step 4: Configuring UFW firewall..."
ufw --force disable
ufw --force reset

# Allow SSH (port 22)
ufw allow 22/tcp comment 'SSH'

# Allow HTTP and HTTPS
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Set default policies
ufw default deny incoming
ufw default allow outgoing

# Enable firewall
ufw --force enable
print_status "Firewall configured (SSH, HTTP, HTTPS allowed)"

# Show firewall status
ufw status numbered

# Create app user
echo ""
echo "Step 5: Creating application user..."
if ! id -u productsnap &> /dev/null; then
    useradd -m -s /bin/bash productsnap
    usermod -aG docker productsnap
    print_status "User 'productsnap' created and added to docker group"
else
    print_warning "User 'productsnap' already exists"
fi

# Create app directory
echo ""
echo "Step 6: Creating application directory..."
mkdir -p /home/productsnap/app
chown -R productsnap:productsnap /home/productsnap/app
print_status "Application directory created at /home/productsnap/app"

# Configure Docker daemon for production
echo ""
echo "Step 7: Configuring Docker for production..."
cat > /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true
}
EOF

systemctl restart docker
print_status "Docker configured for production"

# Set up automatic security updates
echo ""
echo "Step 8: Configuring automatic security updates..."
apt install -y unattended-upgrades
echo 'unattended-upgrades unattended-upgrades/enable_auto_updates boolean true' | debconf-set-selections
dpkg-reconfigure -f noninteractive unattended-upgrades
print_status "Automatic security updates enabled"

# Install certbot for Let's Encrypt
echo ""
echo "Step 9: Preparing for Let's Encrypt SSL..."
print_status "Certbot installed and ready"
print_warning "SSL certificates will be generated once domain is configured"

# System tuning for web applications
echo ""
echo "Step 10: System tuning..."
cat >> /etc/sysctl.conf <<EOF

# ProductSnap optimizations
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
vm.swappiness = 10
EOF

sysctl -p
print_status "System tuning applied"

# Set timezone to UTC
echo ""
echo "Step 11: Setting timezone to UTC..."
timedatectl set-timezone UTC
print_status "Timezone set to UTC"

# Enable and start cron
systemctl enable cron
systemctl start cron
print_status "Cron service enabled"

# Create SSL directory for certificates
mkdir -p /etc/letsencrypt
print_status "SSL directory prepared"

# Summary
echo ""
echo "=================================================="
echo "Server Setup Complete!"
echo "=================================================="
echo ""
echo "✓ System updated and essential packages installed"
echo "✓ Docker and Docker Compose installed"
echo "✓ Firewall configured (UFW active)"
echo "✓ Application user 'productsnap' created"
echo "✓ Application directory: /home/productsnap/app"
echo "✓ Automatic security updates enabled"
echo "✓ Certbot ready for SSL certificates"
echo "✓ System optimized for web applications"
echo ""
echo "Next steps:"
echo "1. Deploy your application to /home/productsnap/app"
echo "2. Point your domain DNS to this server: $(curl -s ifconfig.me)"
echo "3. Run: certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com"
echo "4. Configure NGINX with SSL certificates"
echo ""
echo "Server IP: $(curl -s ifconfig.me)"
echo "Access as app user: ssh productsnap@$(curl -s ifconfig.me)"
echo ""
