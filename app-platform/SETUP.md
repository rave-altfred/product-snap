# App Platform Setup Guide

Quick guide for setting up dev and prod environments on DigitalOcean App Platform.

## File Structure

```
app-platform/.do/
├── app.yaml.example         ✅ In git - prod template
├── app-dev.yaml.example     ✅ In git - dev template
├── app.yaml                 ❌ Local only - actual prod config
├── app-dev.yaml             ❌ Local only - actual dev config
├── app-id.txt               ❌ Local only - prod app ID
└── app-id-dev.txt           ❌ Local only - dev app ID
```

## Initial Setup

### 1. Copy Templates

```bash
cd app-platform/.do

# Copy templates to actual config files
cp app.yaml.example app.yaml
cp app-dev.yaml.example app-dev.yaml
```

### 2. Fill in Production Config (`app.yaml`)

Your current `app.yaml` already has production values. Just verify:

```bash
# Check if app.yaml exists and has values
grep -i "TODO" app.yaml

# Should return nothing if all values are filled
```

If you see TODO values, replace them with actual production credentials.

### 3. Fill in Development Config (`app-dev.yaml`)

Open `app-dev.yaml` and replace all empty values:

**Required fields:**
- `DATABASE_URL` - Dev PostgreSQL connection string
- `REDIS_URL` - Dev Valkey/Redis connection string  
- `JWT_SECRET` - Generate with: `openssl rand -base64 32`
- `S3_BUCKET` - Dev bucket name (e.g., "productsnap-dev")
- `S3_ACCESS_KEY` - Spaces access key
- `S3_SECRET_KEY` - Spaces secret key
- `SMTP_USER` - Email user
- `SMTP_PASSWORD` - Email password
- `NANO_BANANA_API_KEY` - Gemini API key

**Optional PayPal fields** (if testing subscriptions):
- `PAYPAL_CLIENT_ID` - Sandbox client ID
- `PAYPAL_CLIENT_SECRET` - Sandbox client secret
- `PAYPAL_WEBHOOK_ID` - Sandbox webhook ID
- `PAYPAL_PLAN_ID_*` - Sandbox plan IDs

**Optional Google OAuth:**
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

### 4. Create Dev Resources

**Option A: Create new dev databases**

```bash
# PostgreSQL (1GB for dev)
doctl databases create productsnap-dev-db \
  --engine pg \
  --region fra1 \
  --size db-s-1vcpu-1gb \
  --num-nodes 1

# Get connection string
doctl databases connection <db-id> --format URI

# Valkey/Redis (1GB for dev)
doctl databases create productsnap-dev-valkey \
  --engine redis \
  --region fra1 \
  --size db-s-1vcpu-1gb \
  --num-nodes 1

# Get connection string
doctl databases connection <valkey-id> --format URI
```

**Option B: Reuse production databases** (not recommended, but cheaper)

Copy the same connection strings from `app.yaml` to `app-dev.yaml`.

**Create dev S3 bucket:**

```bash
# Via DigitalOcean console or:
doctl compute space create productsnap-dev --region fra1
```

Update `app-dev.yaml` with:
- `S3_BUCKET: productsnap-dev`

**S3 Access Keys:**

You can reuse the same S3 access keys from prod, or create new ones in the DigitalOcean console under Spaces → API Keys.

### 5. Validate Configs

```bash
cd app-platform

# Validate prod config (should pass - already deployed)
./deploy.sh validate

# Validate dev config (will use app-dev.yaml once scripts are updated)
# For now, temporarily rename to test:
mv .do/app.yaml .do/app.yaml.backup
mv .do/app-dev.yaml .do/app.yaml
./deploy.sh validate
mv .do/app.yaml .do/app-dev.yaml
mv .do/app.yaml.backup .do/app.yaml
```

## Next Steps

Once `app-dev.yaml` is filled and validated:

1. **Wait for script updates** - The `deploy.sh` and `build-and-push.sh` scripts need to be modified to support `dev|prod` parameters
2. **Create dev app** - Run `./deploy.sh create dev`
3. **Deploy to dev** - Run `./deploy.sh deploy dev`

## Quick Reference

### Generate Secrets

```bash
# JWT Secret
openssl rand -base64 32

# Random password
openssl rand -base64 24
```

### Get Database Connection Strings

```bash
# List databases
doctl databases list

# Get connection details
doctl databases connection <db-id>

# Get connection URI format
doctl databases connection <db-id> --format URI
```

### Check Current Prod App

```bash
# Get prod app ID
cat .do/app-id.txt

# View app details
doctl apps get $(cat .do/app-id.txt)
```

## Cost Estimate

**Development Environment:**
- Backend: $5/month
- Frontend: $5/month
- Worker: $5/month
- PostgreSQL (1GB): $15/month
- Valkey (1GB): $15/month
- **Total: ~$45/month**

**Production Environment:**
- Same as above: ~$48/month

**Combined: ~$93/month**

## Checklist

- [ ] Copy `app.yaml.example` to `app.yaml` (if not already done)
- [ ] Copy `app-dev.yaml.example` to `app-dev.yaml`
- [ ] Fill all TODO fields in `app-dev.yaml`
- [ ] Create dev databases (PostgreSQL + Valkey)
- [ ] Create dev S3 bucket
- [ ] Validate `app-dev.yaml` config
- [ ] Wait for script updates to support `dev|prod` parameter
- [ ] Create dev app: `./deploy.sh create dev`
- [ ] Deploy to dev: `./deploy.sh deploy dev`

## Troubleshooting

**Validation fails with empty values:**
- Make sure all required fields are filled (no empty strings "")
- Check for TODO placeholders

**Database connection string format:**
- PostgreSQL: `postgresql://user:pass@host:25060/db?sslmode=require`
- Valkey: `rediss://default:pass@host:25061/0?ssl_cert_reqs=required`

**Can't find app ID:**
- Prod: `cat .do/app-id.txt`
- Dev: `cat .do/app-id-dev.txt` (after creating dev app)
- Or list all: `doctl apps list`

---

See `ENVIRONMENTS.md` for complete workflow documentation.
