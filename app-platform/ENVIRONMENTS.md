# Environment Segregation Guide

**ProductSnap / LightClick Studio**  
**Last Updated:** 2025-10-16

---

## Overview

This document describes the development and production environment segregation strategy for ProductSnap deployments on DigitalOcean App Platform.

**Key Principle:** Code branches control **what** is deployed. Deployment scripts control **where** it's deployed.

---

## Architecture

### Two Independent App Platform Apps

```
┌─────────────────────────────────────────────────────────────┐
│                    DigitalOcean Account                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────┐  ┌─────────────────────────┐
│  │     DEV ENVIRONMENT         │  │    PROD ENVIRONMENT     │
│  ├─────────────────────────────┤  ├─────────────────────────┤
│  │ App: lightclick-dev         │  │ App: lightclick-studio  │
│  │ ID: abc-123-dev             │  │ ID: xyz-789-prod        │
│  ├─────────────────────────────┤  ├─────────────────────────┤
│  │ • PostgreSQL (dev)          │  │ • PostgreSQL (prod)     │
│  │ • Valkey/Redis (dev)        │  │ • Valkey/Redis (prod)   │
│  │ • S3 Bucket (dev)           │  │ • S3 Bucket (prod)      │
│  │ • PayPal Sandbox            │  │ • PayPal Live           │
│  ├─────────────────────────────┤  ├─────────────────────────┤
│  │ URL: *-dev.ondigitalocean   │  │ URL: lightclick.studio  │
│  └─────────────────────────────┘  └─────────────────────────┘
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Local Configuration Files

```
app-platform/.do/
├── app.yaml.example         # In git - template for prod
├── app-dev.yaml.example     # In git - template for dev
├── app.yaml                 # Local only - actual prod config
├── app-dev.yaml             # Local only - actual dev config
├── app-id.txt               # Local only - prod app ID
├── app-id-dev.txt           # Local only - dev app ID
└── .gitignore               # Excludes actual configs
```

**Git tracks:** Templates (`.example` files)  
**Git ignores:** Actual configs (contain secrets), App IDs

---

## Git Branching Strategy

```
main (stable, production-ready)
  │
  ├── hotfix/*           ← Urgent production fixes
  │
  └── develop            ← Integration branch
        │
        ├── feature/*    ← New features
        ├── bugfix/*     ← Non-urgent fixes
        └── experiment/* ← Experimental work
```

### Branch Purposes

| Branch Type | Purpose | Deploy To | Merge To |
|------------|---------|-----------|----------|
| `main` | Production-ready stable code | **prod** only | - |
| `hotfix/*` | Critical production fixes | **prod** (urgent) | `main`, then `develop` |
| `develop` | Integration of tested features | **dev** | `main` (when stable) |
| `feature/*` | New feature development | **dev** | `develop` |
| `bugfix/*` | Non-critical bug fixes | **dev** | `develop` |
| `experiment/*` | R&D, POCs | **dev** | `develop` (if successful) |

---

## Deployment Workflow

### Modified Scripts

The deployment scripts accept an environment parameter:

```bash
./deploy.sh <command> [dev|prod] [options]
./build-and-push.sh [dev|prod]
```

**Environment Parameter Logic:**

| Command | Reads | Deploys To |
|---------|-------|------------|
| `./deploy.sh deploy dev` | `app-dev.yaml` + `app-id-dev.txt` | Dev app |
| `./deploy.sh deploy prod` | `app.yaml` + `app-id.txt` | Prod app |

### Daily Development Cycle

```bash
# 1. Create feature branch
git checkout develop
git pull
git checkout -b feature/new-dashboard

# 2. Develop and test locally
docker-compose up -d
# ... make changes ...

# 3. Deploy to dev environment for testing
./app-platform/deploy.sh deploy dev

# 4. Verify on dev URL
curl https://lightclick-dev.ondigitalocean.app/health

# 5. Iterate as needed
# ... more changes ...
./app-platform/deploy.sh deploy dev

# 6. When feature is complete
git add .
git commit -m "Add new dashboard feature"
git push origin feature/new-dashboard

# 7. Merge to develop via PR
# ... create pull request ...
# ... code review ...
# ... merge to develop ...

# 8. Deploy develop branch to dev for integration testing
git checkout develop
git pull
./app-platform/deploy.sh deploy dev
```

### Production Deployment (Controlled)

```bash
# 1. Ensure develop is stable and tested
git checkout develop
./app-platform/deploy.sh deploy dev
# ... thorough testing in dev environment ...

# 2. Merge to main
git checkout main
git merge develop
git push origin main

# 3. Deploy to production
./app-platform/deploy.sh deploy prod

# 4. Monitor production
./app-platform/deploy.sh logs prod RUN

# 5. Tag release (optional)
git tag -a v1.2.0 -m "Release v1.2.0"
git push --tags
```

### Hotfix Workflow (Emergency)

```bash
# SCENARIO: Critical bug in production, but develop has unfinished features

# 1. Save current work
git status
git stash push -m "WIP: feature work"

# 2. Create hotfix from main
git checkout main
git pull
git checkout -b hotfix/critical-auth-bug

# 3. Fix the bug
vim backend/app/routers/auth.py
git add .
git commit -m "Fix critical auth vulnerability"

# 4. Deploy hotfix to production immediately
./app-platform/deploy.sh deploy prod

# 5. Verify fix in production
curl https://lightclick.studio/health
# ... test the fix ...

# 6. Merge hotfix back to main
git checkout main
git merge hotfix/critical-auth-bug
git push origin main
git tag -a v1.1.1 -m "Hotfix: auth vulnerability"
git push --tags

# 7. Merge hotfix to develop (so it's in future releases)
git checkout develop
git merge hotfix/critical-auth-bug
git push origin develop

# 8. Return to feature work
git checkout feature/new-dashboard
git rebase develop  # Include the hotfix
git stash pop       # Restore WIP
```

---

## Initial Setup

### One-Time Setup (New Developer or New Machine)

```bash
# 1. Clone repository
git clone <repo-url>
cd product-snap

# 2. Copy app spec templates
cd app-platform/.do
cp app.yaml.example app.yaml
cp app-dev.yaml.example app-dev.yaml

# 3. Edit configs with actual values
# Edit app.yaml (prod secrets)
# Edit app-dev.yaml (dev secrets)

# 4. Get app IDs from team or create new apps
# If apps already exist, get IDs from team and save:
echo "abc-123-dev" > app-id-dev.txt
echo "xyz-789-prod" > app-id.txt

# If creating new apps (first time):
./deploy.sh create dev
./deploy.sh create prod
```

### Creating Dev Environment (First Time)

```bash
# 1. Create dev databases
doctl databases create productsnap-dev-db \
  --engine pg \
  --region fra1 \
  --size db-s-1vcpu-1gb \
  --num-nodes 1

doctl databases create productsnap-dev-valkey \
  --engine redis \
  --region fra1 \
  --size db-s-1vcpu-1gb \
  --num-nodes 1

# 2. Create dev S3 bucket
doctl compute space create productsnap-dev --region nyc3

# 3. Update app-dev.yaml with connection strings

# 4. Create dev app
cd app-platform
./deploy.sh create dev

# 5. Configure PayPal sandbox credentials in app-dev.yaml

# 6. Deploy initial version
./deploy.sh deploy dev
```

---

## Environment Differences

### Development Environment

**Purpose:** Testing, experimentation, breaking things safely

**Characteristics:**
- Smaller databases (1GB vs 2GB+)
- PayPal sandbox mode
- Separate S3 bucket (`productsnap-dev`)
- Relaxed rate limits (optional)
- Debug logging enabled
- Auto-deploy from feature branches (optional)

**Environment Variables:**
```yaml
ENVIRONMENT: development
PAYPAL_MODE: sandbox
LOG_LEVEL: DEBUG
FRONTEND_URL: https://lightclick-dev.ondigitalocean.app
```

### Production Environment

**Purpose:** Live customer-facing application

**Characteristics:**
- Production-sized databases
- PayPal live mode
- Production S3 bucket
- Strict rate limits
- Standard logging (INFO/WARNING/ERROR)
- Deploy only from `main` branch

**Environment Variables:**
```yaml
ENVIRONMENT: production
PAYPAL_MODE: live
LOG_LEVEL: INFO
FRONTEND_URL: https://lightclick.studio
```

---

## Common Operations

### Deploy Current Branch to Dev

```bash
# From any branch
./app-platform/deploy.sh deploy dev
```

### Deploy Main to Production

```bash
git checkout main
git pull
./app-platform/deploy.sh deploy prod
```

### View Logs

```bash
# Dev logs
./app-platform/deploy.sh logs dev RUN

# Prod logs
./app-platform/deploy.sh logs prod RUN

# Specific service
doctl apps logs $(cat app-platform/.do/app-id-dev.txt) --type run backend
```

### Check App Status

```bash
# Dev status
./app-platform/deploy.sh info dev

# Prod status
./app-platform/deploy.sh info prod
```

### Rollback Production

```bash
# List deployments
doctl apps list-deployments $(cat app-platform/.do/app-id.txt)

# Rollback to previous
doctl apps create-deployment $(cat app-platform/.do/app-id.txt) \
  --deployment-id <previous-deployment-id>
```

### Run Database Migration

```bash
# Dev database
doctl apps exec $(cat app-platform/.do/app-id-dev.txt) backend -- alembic upgrade head

# Prod database (be careful!)
doctl apps exec $(cat app-platform/.do/app-id.txt) backend -- alembic upgrade head
```

---

## Safety Guidelines

### Before Deploying to Production

- [ ] Changes tested locally with `docker-compose`
- [ ] Changes deployed to dev and tested thoroughly
- [ ] Database migrations tested in dev
- [ ] No known bugs or regressions
- [ ] Code reviewed and approved
- [ ] On `main` branch with latest changes
- [ ] Team notified of deployment

### Production Deployment Checklist

```bash
# 1. Confirm you're on main
git branch --show-current  # Should output: main

# 2. Confirm main is up to date
git pull origin main

# 3. Check what will be deployed
git log --oneline -5

# 4. Run production deployment
./app-platform/deploy.sh deploy prod

# 5. Monitor deployment
./app-platform/deploy.sh logs prod DEPLOY

# 6. Verify health
curl https://lightclick.studio/health

# 7. Spot-check critical features
# - Login
# - Image generation
# - Subscription flow
```

---

## Troubleshooting

### Deployed Wrong Branch to Prod

```bash
# Immediately checkout correct branch and redeploy
git checkout main
./app-platform/deploy.sh deploy prod

# Or rollback (see "Rollback Production" above)
```

### Dev and Prod Configs Out of Sync

```bash
# Compare configs
diff app-platform/.do/app.yaml app-platform/.do/app-dev.yaml

# Update templates
cp app-platform/.do/app.yaml app-platform/.do/app.yaml.example
cp app-platform/.do/app-dev.yaml app-platform/.do/app-dev.yaml.example

# Strip secrets from examples before committing
vim app-platform/.do/app.yaml.example  # Replace secrets with placeholders
vim app-platform/.do/app-dev.yaml.example
```

### Lost App ID

```bash
# List all apps
doctl apps list

# Find your app and save ID
echo "<app-id>" > app-platform/.do/app-id.txt
# or
echo "<app-id>" > app-platform/.do/app-id-dev.txt
```

### Accidentally Deployed Dev Config to Prod

**DON'T PANIC.** The worst that happens is prod uses dev database (data goes to dev).

**Fix:**
1. Don't make more changes to either environment
2. Checkout main branch
3. Deploy correct prod config: `./deploy.sh deploy prod`
4. Verify: `curl https://lightclick.studio/health`
5. Check that prod database is being used (look at logs)

---

## Cost Optimization

**Current Setup:**
- Dev: ~$35/month (smaller databases)
- Prod: ~$48/month
- **Total: ~$83/month**

**Further Optimization:**
- Share databases between dev/prod (not recommended - data safety risk)
- Use smaller dev instances (basic-xxs)
- Pause dev environment when not actively developing

---

## Best Practices

1. **Never deploy directly to prod from feature branch**  
   Always go through `main` branch.

2. **Test in dev before prod**  
   Every change should be validated in dev first.

3. **Keep environments in sync**  
   Regularly deploy `main` to dev to keep them similar.

4. **Document environment variables**  
   Update `environment-mapping.md` when adding new vars.

5. **Use descriptive commit messages**  
   Makes deployment tracking easier.

6. **Tag production releases**  
   `git tag -a v1.2.0 -m "Release notes"`

7. **Monitor production after deployment**  
   Watch logs for 10-15 minutes after prod deploy.

8. **Backup before risky changes**  
   Database backups are automatic, but check before major migrations.

---

## Team Collaboration

### Sharing App IDs

App IDs should be shared securely with team members:

```bash
# Send via secure channel (1Password, encrypted message)
DEV_APP_ID=$(cat app-platform/.do/app-id-dev.txt)
PROD_APP_ID=$(cat app-platform/.do/app-id.txt)
echo "Dev: $DEV_APP_ID"
echo "Prod: $PROD_APP_ID"
```

### Shared Development Environment

If the team shares one dev environment:

- Coordinate deployments in team chat
- Use feature flags for WIP features
- Consider personal dev environments for major experiments

### Access Control

- All developers: Read access to prod, full access to dev
- Lead/DevOps only: Write access to prod
- Configure via DigitalOcean team permissions

---

## Future Improvements

- [ ] Add staging environment (between dev and prod)
- [ ] Automate prod deployments on `main` branch merge (CI/CD)
- [ ] Add deployment approval workflow
- [ ] Implement feature flags for gradual rollouts
- [ ] Add automated smoke tests post-deployment
- [ ] Set up monitoring/alerting (Sentry, etc.)

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy to dev | `./deploy.sh deploy dev` |
| Deploy to prod | `git checkout main && ./deploy.sh deploy prod` |
| View dev logs | `./deploy.sh logs dev RUN` |
| View prod logs | `./deploy.sh logs prod RUN` |
| Check dev status | `./deploy.sh info dev` |
| Check prod status | `./deploy.sh info prod` |
| List all apps | `./deploy.sh list` |
| Build images for dev | `./build-and-push.sh dev` |
| Build images for prod | `./build-and-push.sh prod` |

---

**Questions or issues?** Update this document or ask the team.
