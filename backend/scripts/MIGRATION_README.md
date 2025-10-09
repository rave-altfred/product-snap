# Digital Ocean Database Migration

## Overview
This migration fixes subscription enum values to use lowercase format, which is required for the updated PayPal subscription integration.

## What it does
1. Adds lowercase enum values to `subscriptionplan` type:
   - `free`, `personal`, `pro`
   - `basic_monthly`, `basic_yearly`
   - `pro_monthly`, `pro_yearly`

2. Adds lowercase enum values to `subscriptionstatus` type:
   - `active`, `cancelled`, `expired`, `pending`

3. Updates all existing subscription records to use lowercase values

## Prerequisites
- `psql` command-line tool installed (for bash script)
- OR Python 3 with `psycopg2` installed (for Python script)

## Option 1: Run with Bash Script

```bash
cd /Users/ravenir/dev/apps/product-snap/backend/scripts
./run_do_migration.sh
```

## Option 2: Run with Python Script

```bash
cd /Users/ravenir/dev/apps/product-snap/backend
python scripts/run_do_migration.py
```

## Option 3: Manual Execution

If you prefer to run manually:

```bash
psql \
  -h database-postgresql-do-user-25716918-0.d.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d defaultdb \
  -f scripts/migration_fix_subscription_enums.sql
```

You'll be prompted for the password: `REDACTED_PASSWORD`

## After Migration

1. **Restart your backend application** on Digital Ocean to ensure it picks up the new enum values
2. **Test the subscription flow** to verify everything works correctly
3. **Check logs** for any errors related to subscriptions

## Rollback

This migration is additive (only adds new enum values and updates existing records). It does NOT remove old uppercase values, so if you need to rollback your code, the old values will still work.

## Verification

After running the migration, you can verify the changes:

```sql
-- Check enum values
SELECT unnest(enum_range(NULL::subscriptionplan));
SELECT unnest(enum_range(NULL::subscriptionstatus));

-- Check existing subscription records
SELECT DISTINCT plan, status FROM subscriptions;
```

## Important Notes

⚠️ **This modifies the production database!** Make sure you understand what it does before running it.

✅ **Safe to run multiple times** - Uses `IF NOT EXISTS` checks, so running it again won't cause errors.

🔒 **Contains sensitive credentials** - Do not commit these scripts with credentials to a public repository. Consider using environment variables for production deployments.
