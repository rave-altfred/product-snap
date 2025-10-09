#!/usr/bin/env python3
"""
Script to run migration on Digital Ocean database
Usage: python scripts/run_do_migration.py
"""

import psycopg2
import sys
from pathlib import Path

# Digital Ocean connection details
DB_CONFIG = {
    "host": "database-postgresql-do-user-25716918-0.d.db.ondigitalocean.com",
    "port": 25060,
    "user": "doadmin",
    "password": "REDACTED_PASSWORD",
    "database": "defaultdb",
    "sslmode": "require"
}

def main():
    print("🔧 Running subscription enum migration on Digital Ocean database...")
    print()
    
    # Get migration file path
    script_dir = Path(__file__).parent
    migration_file = script_dir / "migration_fix_subscription_enums.sql"
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)
    
    print(f"📄 Migration file: {migration_file}")
    print(f"🌐 Connecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print()
    print("⚠️  WARNING: This will modify the production database!")
    
    response = input("   Press ENTER to continue or CTRL+C to cancel... ")
    
    print()
    print("🚀 Running migration...")
    print()
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()
        
        # Read and execute migration file
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Execute the migration
        cursor.execute(sql)
        
        # Commit the transaction
        conn.commit()
        
        print()
        print("✅ Migration completed successfully!")
        print()
        print("💡 Next steps:")
        print("   1. Restart your backend application on Digital Ocean")
        print("   2. Test the subscription flow")
        print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    main()
