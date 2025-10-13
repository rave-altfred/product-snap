# Environment Files Documentation

This document explains all environment files in the ProductSnap project, their purpose, and which ones are actively used.

## Summary

**Total env files found: 11**

| File | Status | Purpose |
|------|--------|---------|
| `.env` | ✅ **ACTIVE** | Main config for local Docker Compose development |
| `.env.example` | ✅ **KEEP** | Template for creating `.env` files |
| `.env.bak` | ⚠️ **CAN REMOVE** | Backup/duplicate of `.env` (outdated) |
| `backend/.env` | ⚠️ **OPTIONAL** | Used by backend scripts (PayPal setup, etc.) |
| `backend/.env.example` | ✅ **KEEP** | Template for standalone backend development |
| `frontend/.env.test` | ✅ **ACTIVE** | Playwright E2E test credentials |
| `droplet/.env.production` | ✅ **ACTIVE** | Production deployment secrets (gitignored) |
| `droplet/.env.production.template` | ✅ **KEEP** | Template for production deployment |
| `droplet/config.env` | ✅ **ACTIVE** | Droplet configuration (non-secret values) |
| `droplet/droplet-info.env` | ✅ **ACTIVE** | Auto-generated droplet metadata (gitignored) |
| `backend/alembic/env.py` | ✅ **ACTIVE** | Alembic migrations script (not an env file) |

## Files You Can Safely Remove

### 1. `.env.bak` ⚠️ **REMOVE**
- **Location**: `/Users/ravenir/dev/apps/product-snap/.env.bak`
- **Why**: This is a backup copy of `.env` with nearly identical content to the root `.env`. It's not referenced anywhere in the codebase.
- **Action**: Delete this file

### 2. `backend/.env` ✅ **KEEP (If Using Scripts)**
- **Location**: `/Users/ravenir/dev/apps/product-snap/backend/.env`
- **Why it EXISTS**: Used by backend utility scripts in `backend/scripts/` directory:
  - `check_subscription.py` - Check PayPal subscription status
  - `list_paypal_plans.py` - List PayPal billing plans
  - `setup_paypal_plans.py` - Create PayPal billing plans
  - `setup_paypal_webhook.py` - Configure PayPal webhooks
  - `list_sandbox_accounts.py` - List PayPal sandbox accounts
  - All these scripts use `load_dotenv()` which loads `.env` from the backend directory
- **Why it's NOT used in Docker**:
  - The backend container reads environment variables from the root `.env` file via `docker-compose.yml`
  - `backend/app/core/config.py` tries to load `.env` but from `/app` inside the container
  - Environment variables are passed explicitly in `docker-compose.yml`
  - Production Dockerfile explicitly deletes `.env*` files (line 46)
- **Action**: 
  - **KEEP** if you run backend scripts (e.g., `cd backend && python scripts/setup_paypal_plans.py`)
  - **REMOVE** if you never run backend scripts directly (only use Docker)
  - Alternative: Copy root `.env` to `backend/.env` when needed, or run scripts from root with proper env vars

## Active Environment Files

### Root Directory

#### `.env` ✅ ACTIVE
- **Purpose**: Main configuration for local Docker Compose development
- **Used by**: `docker-compose.yml` (root directory)
- **Contains**: All secrets and configuration for local development (MinIO, PayPal sandbox, Gmail SMTP, etc.)
- **Notes**: 
  - This file should NOT be committed (it's in `.gitignore`)
  - Contains actual working credentials for local development

#### `.env.example` ✅ KEEP
- **Purpose**: Template for creating `.env` files
- **Used by**: Developers setting up the project
- **Contains**: All required variables with placeholder values
- **Notes**: 
  - This IS committed to git
  - Should be copied to `.env` and filled in by developers

### Backend Directory

#### `backend/.env` ⚠️ OPTIONAL (Currently Exists)
- **Purpose**: Configuration for backend utility scripts
- **Used by**: Backend scripts in `backend/scripts/` directory (all use `python-dotenv`)
- **Contains**: Same configuration as root `.env`, but used when running scripts from backend directory
- **Scripts that use this file**:
  - `setup_paypal_plans.py` - Creates PayPal subscription plans
  - `setup_paypal_webhook.py` - Configures PayPal webhooks
  - `list_paypal_plans.py` - Lists available PayPal plans
  - `check_subscription.py` - Checks PayPal subscription status
  - `list_sandbox_accounts.py` - Lists PayPal sandbox test accounts
- **Notes**: 
  - NOT used by Docker containers (they use root `.env` via docker-compose.yml)
  - Production build explicitly removes all `.env*` files from backend image
  - Can be removed if you never run backend scripts directly
  - Alternative: Copy root `.env` → `backend/.env` when needed

#### `backend/.env.example` ✅ KEEP
- **Purpose**: Template for standalone backend development (without Docker Compose)
- **Used by**: Developers running backend directly with `uvicorn` or `python`, or for backend scripts
- **Contains**: Backend-specific configuration template
- **Notes**: 
  - More detailed than root `.env.example`
  - Includes rate limit defaults and file upload limits
  - Useful if running backend outside Docker for debugging
  - Use as template for `backend/.env` when running scripts

### Frontend Directory

#### `frontend/.env.test` ✅ ACTIVE
- **Purpose**: Test user credentials for Playwright E2E tests
- **Used by**: `frontend/playwright.config.ts`, test files
- **Contains**: Test user emails/passwords, BASE_URL, USE_DOCKER flag
- **Notes**: 
  - Gitignored (`.gitignore` line 57)
  - Required for running E2E tests

### Droplet Directory

#### `droplet/.env.production` ✅ ACTIVE
- **Purpose**: Source file for Docker Swarm secrets in production
- **Used by**: `droplet/deploy.sh` (creates Docker secrets from this file)
- **Contains**: Real production credentials (database, S3, PayPal, etc.)
- **Notes**: 
  - Gitignored (`.gitignore` line 5)
  - Validated by `deploy.sh` before deployment
  - Values are converted to Docker Swarm secrets (not copied as plain files)
  - Secrets are mounted as files in containers at `/run/secrets/`

#### `droplet/.env.production.template` ✅ KEEP
- **Purpose**: Template for creating production environment
- **Used by**: Deployment setup process
- **Contains**: All required production variables with empty/placeholder values
- **Notes**: 
  - Committed to git as a template
  - Copy to `.env.production` and fill in before deploying

#### `droplet/config.env` ✅ ACTIVE
- **Purpose**: Droplet infrastructure configuration (non-secret)
- **Used by**: `droplet/deploy.sh`, `droplet/build.sh`, `droplet/create-droplet.sh`
- **Contains**: Registry namespace, region, domain, SSL email
- **Notes**: 
  - Committed to git (safe to share)
  - Manual configuration values

#### `droplet/droplet-info.env` ✅ ACTIVE
- **Purpose**: Auto-generated droplet metadata
- **Used by**: `droplet/deploy.sh`, deployment scripts
- **Contains**: Droplet ID, IP address, domain info
- **Notes**: 
  - Gitignored (`.gitignore` line 6)
  - Generated by `create-droplet.sh`
  - Read by deployment scripts to know where to deploy

## Environment File Hierarchy

### Local Development Flow
```
1. Copy .env.example → .env
2. Fill in local development values (or keep defaults)
3. Run: docker-compose up
4. Docker Compose injects variables from .env into containers
```

### Production Deployment Flow (Docker Secrets)
```
1. Copy droplet/.env.production.template → droplet/.env.production
2. Fill in production secrets
3. Run: droplet/deploy.sh
4. Script validates .env.production
5. Script initializes Docker Swarm (if needed)
6. Script creates Docker secrets from .env.production values
7. Stack deployed using docker-compose.prod.secrets.yml
8. Secrets mounted as files in containers at /run/secrets/
```

### Backend Scripts / Standalone Development
```
1. Copy backend/.env.example → backend/.env (or copy root .env to backend/.env)
2. Fill in configuration (PayPal, database, etc.)
3a. Run scripts: cd backend && python scripts/setup_paypal_plans.py
3b. Run backend: cd backend && uvicorn app.main:app --reload
4. Scripts load backend/.env via python-dotenv
5. Backend app loads backend/.env via Pydantic Settings (standalone mode only)
```

## How Environment Variables are Loaded

### Docker Compose (Development)
- **File**: `docker-compose.yml`
- **Method**: Reads `.env` from root directory, injects into container environment
- **Example**:
  ```yaml
  environment:
    DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
  ```

### Docker Compose (Production) - Docker Secrets
- **File**: `droplet/docker-compose.prod.secrets.yml`
- **Method**: Uses Docker Swarm secrets (mounted as files)
- **Example**:
  ```yaml
  backend:
    secrets:
      - jwt_secret
      - postgres_password
  ```
- **Notes**:
  - Backend config supports both direct env vars and `*_FILE` variants
  - Example: `JWT_SECRET_FILE=/run/secrets/jwt_secret`
  - Secrets automatically created/updated by `deploy.sh`

### Backend Application
- **File**: `backend/app/core/config.py`
- **Method**: Pydantic Settings with `env_file = ".env"` in Config class
- **Notes**: 
  - Looks for `.env` in working directory
  - In Docker, working dir is `/app` (no .env file there)
  - Falls back to environment variables (injected by Docker Compose)

### Frontend (Vite)
- **Method**: Vite automatically loads `.env` files in frontend directory
- **Pattern**: Variables prefixed with `VITE_` are exposed to browser
- **Example**: `VITE_API_URL` in root `.env` is accessible via `import.meta.env.VITE_API_URL`

## Recommended Actions

### Cleanup Commands

```bash
# Remove duplicate backup file
rm /Users/ravenir/dev/apps/product-snap/.env.bak

# OPTIONAL: Remove backend/.env if you don't run backend scripts
# (Check if you use scripts like setup_paypal_plans.py first)
rm /Users/ravenir/dev/apps/product-snap/backend/.env

# Verify no references exist
grep -r "\.env\.bak" . --exclude-dir=node_modules --exclude-dir=.git
```

### Keep These Files
- `.env` (active, gitignored)
- `.env.example` (template, committed)
- `backend/.env.example` (template, committed)
- `frontend/.env.test` (active, gitignored)
- `droplet/.env.production` (active, gitignored)
- `droplet/.env.production.template` (template, committed)
- `droplet/config.env` (active, committed)
- `droplet/droplet-info.env` (active, gitignored)

### Update .gitignore (Already Correct)
The `.gitignore` file already properly excludes sensitive files:
```
.env
.env.local
.env.production
droplet/.env.production
droplet/droplet-info.env
frontend/.env.test
```

## Docker Secrets in Production

Production deployments use Docker Swarm secrets for enhanced security:

### How It Works
1. **Deployment script** (`droplet/deploy.sh`) reads `droplet/.env.production`
2. **Creates secrets**: Each sensitive value becomes a Docker secret
3. **Mounts secrets**: Containers access secrets as files in `/run/secrets/`
4. **Backend reads**: Config supports `*_FILE` env vars (e.g., `JWT_SECRET_FILE`)

### Secrets Management
```bash
# Use the helper script to manage secrets
./droplet/manage-secrets.sh list          # List all secrets
./droplet/manage-secrets.sh inspect <name> # View secret metadata
./droplet/manage-secrets.sh update <name>  # Update a secret value
./droplet/manage-secrets.sh remove <name>  # Remove a secret
```

### Supported Secrets
All sensitive values from `.env.production` are converted to secrets:
- Database credentials (postgres_password, postgres_user, postgres_db)
- JWT signing key (jwt_secret)
- S3/Spaces credentials (s3_access_key, s3_secret_key)
- PayPal API credentials (paypal_client_id, paypal_client_secret)
- Email credentials (smtp_username, smtp_password)
- API keys (nano_banana_api_key)

### Benefits
- Secrets encrypted at rest and in transit
- No plain-text secrets in container images
- Secrets only accessible to authorized services
- Centralized secret rotation via `manage-secrets.sh`

## Environment Variable Best Practices

1. **Never commit secrets**: Use `.gitignore` for files with real credentials
2. **Use templates**: Provide `.example` files with placeholder values
3. **Validate before deployment**: `deploy.sh` checks required variables exist
4. **Use Docker Secrets in production**: Enabled by default for production deployments
5. **Separate concerns**: 
   - Root `.env` for Docker Compose (local dev)
   - `droplet/.env.production` for production secrets (converted to Docker secrets)
   - `backend/.env.example` for standalone development
6. **Document changes**: Update this file when adding new env files

## Troubleshooting

### "Environment variable not found"
- Check if the variable exists in the correct `.env` file
- For Docker: root `.env` file
- For production: `droplet/.env.production`
- Restart containers after changing `.env`: `docker-compose restart`

### "backend/.env not loaded"
- This is expected when using Docker Compose
- Environment variables are injected by `docker-compose.yml`
- The `backend/.env` file is only used for standalone backend development

### "Production deployment fails validation"
- Check `droplet/.env.production` has all required variables set
- Required: `DATABASE_URL`, `JWT_SECRET`, `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`
- See error output from `deploy.sh` for missing variables

## Related Documentation

- [WARP.md](../WARP.md) - Development workflow and commands
- [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md) - Production deployment instructions
- [STORAGE_CONFIGURATION.md](./STORAGE_CONFIGURATION.md) - S3/Spaces setup
- [PAYPAL_QUICKSTART.md](./PAYPAL_QUICKSTART.md) - PayPal configuration
