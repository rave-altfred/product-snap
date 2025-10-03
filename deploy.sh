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
SERVER_USER="${SERVER_USER:-productsnap}"
APP_DIR="/home/productsnap/app"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# Function to check if .env exists
check_env_file() {
    if [ ! -f "$LOCAL_DIR/.env" ]; then
        print_error ".env file not found!"
        print_info "Please create .env from .env.example and configure it"
        print_info "Run: cp .env.example .env && nano .env"
        exit 1
    fi
    print_status ".env file found"
}

# Function to deploy files
deploy_files() {
    print_info "Deploying application files to server..."
    
    # Create temporary exclude file
    cat > /tmp/rsync-exclude << 'EOF'
.git
.gitignore
__pycache__
*.pyc
.pytest_cache
node_modules
.env.example
build
*.log
.DS_Store
setup-server.sh
DEPLOYMENT_INFO.md
WARP.md
MISSING_IMPLEMENTATIONS.md
EOF

    # Rsync files to server
    rsync -avz --delete \
        --exclude-from=/tmp/rsync-exclude \
        "$LOCAL_DIR/" \
        "${SERVER_USER}@${SERVER_IP}:${APP_DIR}/"
    
    rm -f /tmp/rsync-exclude
    print_status "Files deployed successfully"
}

# Function to run migrations
run_migrations() {
    print_info "Running database migrations..."
    
    ssh "${SERVER_USER}@${SERVER_IP}" << 'ENDSSH'
cd /home/productsnap/app
# Check if backend container is running
if docker ps | grep -q productsnap-backend; then
    echo "Running migrations..."
    docker compose exec -T backend alembic upgrade head
else
    echo "Backend container not running, migrations will run on first start"
fi
ENDSSH
    
    print_status "Database migrations completed"
}

# Function to build and start containers
start_containers() {
    print_info "Building and starting Docker containers..."
    
    ssh "${SERVER_USER}@${SERVER_IP}" << 'ENDSSH'
cd /home/productsnap/app

# Pull latest images
docker compose pull postgres redis

# Build application images
echo "Building application images..."
docker compose build --no-cache backend frontend

# Start services
echo "Starting services..."
docker compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 10

# Check service status
docker compose ps

# Show logs
echo -e "\n=== Recent logs ==="
docker compose logs --tail=50
ENDSSH
    
    print_status "Containers started successfully"
}

# Function to check service health
check_health() {
    print_info "Checking service health..."
    
    # Check HTTP endpoint
    if curl -sf "http://${SERVER_IP}/health" > /dev/null; then
        print_status "Health check passed!"
    else
        print_warning "Health check failed. Check logs with: ssh ${SERVER_USER}@${SERVER_IP} 'cd ${APP_DIR} && docker compose logs'"
    fi
}

# Main deployment flow
main() {
    echo "=================================================="
    echo "ProductSnap Deployment Script"
    echo "=================================================="
    echo ""
    
    print_info "Target server: ${SERVER_USER}@${SERVER_IP}"
    print_info "App directory: ${APP_DIR}"
    echo ""
    
    # Confirm deployment
    read -p "Continue with deployment? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deployment cancelled"
        exit 0
    fi
    
    # Step 1: Check environment file
    echo ""
    echo "Step 1: Checking environment configuration..."
    check_env_file
    
    # Step 2: Deploy files
    echo ""
    echo "Step 2: Deploying application files..."
    deploy_files
    
    # Step 3: Build and start containers
    echo ""
    echo "Step 3: Building and starting containers..."
    start_containers
    
    # Step 4: Run migrations
    echo ""
    echo "Step 4: Running database migrations..."
    run_migrations
    
    # Step 5: Health check
    echo ""
    echo "Step 5: Performing health check..."
    sleep 5
    check_health
    
    # Summary
    echo ""
    echo "=================================================="
    echo "Deployment Complete!"
    echo "=================================================="
    echo ""
    print_status "Application URL: http://${SERVER_IP}"
    print_status "API Documentation: http://${SERVER_IP}/api/docs"
    print_status "Health Check: http://${SERVER_IP}/health"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    ssh ${SERVER_USER}@${SERVER_IP} 'cd ${APP_DIR} && docker compose logs -f'"
    echo "  Restart:      ssh ${SERVER_USER}@${SERVER_IP} 'cd ${APP_DIR} && docker compose restart'"
    echo "  Stop:         ssh ${SERVER_USER}@${SERVER_IP} 'cd ${APP_DIR} && docker compose down'"
    echo "  Status:       ssh ${SERVER_USER}@${SERVER_IP} 'cd ${APP_DIR} && docker compose ps'"
    echo ""
}

# Run main function
main "$@"
