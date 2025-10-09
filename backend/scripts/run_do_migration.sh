#!/bin/bash
# Script to run migration on Digital Ocean database
# Usage: ./run_do_migration.sh

set -e

echo "🔧 Running subscription enum migration on Digital Ocean database..."
echo ""

# Digital Ocean connection details
DB_HOST="database-postgresql-do-user-25716918-0.d.db.ondigitalocean.com"
DB_PORT="25060"
DB_USER="doadmin"
DB_NAME="defaultdb"
DB_PASSWORD="REDACTED_PASSWORD"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MIGRATION_FILE="$SCRIPT_DIR/migration_fix_subscription_enums.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ Migration file not found: $MIGRATION_FILE"
    exit 1
fi

echo "📄 Migration file: $MIGRATION_FILE"
echo "🌐 Connecting to: $DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo "⚠️  WARNING: This will modify the production database!"
echo "   Press CTRL+C to cancel, or ENTER to continue..."
read

echo ""
echo "🚀 Running migration..."
echo ""

# Run the migration
PGPASSWORD="$DB_PASSWORD" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -f "$MIGRATION_FILE"

echo ""
echo "✅ Migration completed successfully!"
echo ""
echo "💡 Next steps:"
echo "   1. Restart your backend application on Digital Ocean"
echo "   2. Test the subscription flow"
echo ""
