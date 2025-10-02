#!/bin/bash

# ProductSnap Backup Script
# Usage: ./backup.sh

set -e

BACKUP_DIR="/var/backups/productsnap"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

echo "🔄 Starting backup at $(date)"

# Backup PostgreSQL database
echo "📦 Backing up database..."
docker-compose exec -T postgres pg_dump -U productsnap productsnap | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"
echo "✅ Database backup saved to: $BACKUP_DIR/db_backup_$DATE.sql.gz"

# Backup .env file (contains configuration)
echo "📦 Backing up configuration..."
cp .env "$BACKUP_DIR/env_backup_$DATE"
echo "✅ Configuration backup saved"

# Optional: Backup Redis data (if persistence is enabled)
# echo "📦 Backing up Redis data..."
# docker-compose exec -T redis redis-cli SAVE
# docker cp $(docker-compose ps -q redis):/data/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb"

# Clean up old backups (keep last 7 days)
echo "🧹 Cleaning up old backups..."
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "env_backup_*" -mtime +7 -delete

echo "✅ Backup complete at $(date)"
echo "📁 Backups stored in: $BACKUP_DIR"

# List recent backups
echo ""
echo "Recent backups:"
ls -lht $BACKUP_DIR | head -10
