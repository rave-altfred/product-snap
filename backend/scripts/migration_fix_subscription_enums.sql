-- Migration: Fix subscription enum values to lowercase
-- Date: 2025-10-09
-- Description: Adds lowercase enum values and updates existing records

-- Add lowercase enum values for subscriptionplan
ALTER TYPE subscriptionplan ADD VALUE IF NOT EXISTS 'free';
ALTER TYPE subscriptionplan ADD VALUE IF NOT EXISTS 'personal';
ALTER TYPE subscriptionplan ADD VALUE IF NOT EXISTS 'pro';
ALTER TYPE subscriptionplan ADD VALUE IF NOT EXISTS 'basic_monthly';
ALTER TYPE subscriptionplan ADD VALUE IF NOT EXISTS 'basic_yearly';
ALTER TYPE subscriptionplan ADD VALUE IF NOT EXISTS 'pro_monthly';
ALTER TYPE subscriptionplan ADD VALUE IF NOT EXISTS 'pro_yearly';

-- Add lowercase enum values for subscriptionstatus
ALTER TYPE subscriptionstatus ADD VALUE IF NOT EXISTS 'active';
ALTER TYPE subscriptionstatus ADD VALUE IF NOT EXISTS 'cancelled';
ALTER TYPE subscriptionstatus ADD VALUE IF NOT EXISTS 'expired';
ALTER TYPE subscriptionstatus ADD VALUE IF NOT EXISTS 'pending';

-- Update existing subscription records to use lowercase values
UPDATE subscriptions SET plan = 'free' WHERE plan = 'FREE';
UPDATE subscriptions SET plan = 'personal' WHERE plan = 'PERSONAL';
UPDATE subscriptions SET plan = 'pro' WHERE plan = 'PRO';

UPDATE subscriptions SET status = lower(status::text)::subscriptionstatus 
WHERE status IN ('ACTIVE', 'CANCELLED', 'EXPIRED', 'PENDING');

-- Verify the changes
SELECT 'Migration complete!' as message;
SELECT 'Current subscription plan values:' as info;
SELECT DISTINCT plan FROM subscriptions ORDER BY plan;
SELECT 'Current subscription status values:' as info;
SELECT DISTINCT status FROM subscriptions ORDER BY status;
