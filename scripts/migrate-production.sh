#!/bin/bash
set -e

# Production Database Migration Script
# This script runs Alembic migrations against the production database

echo "=========================================="
echo "Production Database Migration"
echo "=========================================="
echo ""
echo "WARNING: This will run migrations on PRODUCTION database!"
echo "Database: database-postgresql-do-user-25716918-0.d.db.ondigitalocean.com"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Migration cancelled."
    exit 0
fi

echo ""
echo "Running migrations..."

# Set production database URL
export DATABASE_URL="postgresql://doadmin:REDACTED_PASSWORD@database-postgresql-do-user-25716918-0.d.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

# Run migrations in Docker container
docker run --rm \
  -v "$(pwd)/backend:/app" \
  -w /app \
  -e DATABASE_URL="$DATABASE_URL" \
  python:3.11-slim \
  bash -c "
    apt-get update -qq && apt-get install -y -qq postgresql-client > /dev/null 2>&1
    pip install -q alembic psycopg2-binary sqlalchemy
    alembic upgrade head
  "

echo ""
echo "=========================================="
echo "✓ Migration Complete!"
echo "=========================================="
