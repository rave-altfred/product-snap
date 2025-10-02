#!/bin/bash

# ProductSnap Deployment Script for DigitalOcean Droplet
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

set -e

ENV=${1:-production}
echo "🚀 Deploying ProductSnap to $ENV environment..."

# Load environment variables
if [ -f ".env.$ENV" ]; then
    source ".env.$ENV"
else
    echo "❌ Environment file .env.$ENV not found!"
    exit 1
fi

# Check required variables
required_vars=("JWT_SECRET" "POSTGRES_PASSWORD" "NANO_BANANA_API_KEY" "S3_BUCKET" "DOMAIN")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required variable $var is not set!"
        exit 1
    fi
done

echo "✅ Environment variables loaded"

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Build Docker images
echo "🏗️  Building Docker images..."
docker-compose build --no-cache

# Stop existing containers
echo "⏸️  Stopping existing containers..."
docker-compose down

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose run --rm backend alembic upgrade head

# Start services
echo "▶️  Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
echo "🏥 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed!"
    docker-compose logs backend
    exit 1
fi

# Show running containers
echo "📊 Running containers:"
docker-compose ps

# Show recent logs
echo "📝 Recent logs:"
docker-compose logs --tail=20

echo "✅ Deployment complete!"
echo "🌐 Application should be available at: https://$DOMAIN"
echo "📚 API docs: https://api.$DOMAIN/api/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To restart: docker-compose restart"
