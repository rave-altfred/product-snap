# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

ProductSnap is a full-stack AI product photography platform that transforms product photos into professional shots using Nano Banana AI. The application supports three generation modes (Studio White, Model Try-On, Lifestyle Scene) with tiered subscription plans (Free, Personal, Pro) and PayPal integration.

**Stack**: FastAPI (Python 3.11) backend, React 18 + TypeScript frontend, PostgreSQL, Redis, S3-compatible storage (DigitalOcean Spaces), Docker deployment.

## Development Commands

### Full Stack (Docker Compose)

```bash
# Start all services (backend, frontend, worker, postgres, redis, nginx)
docker-compose up -d

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose build
docker-compose up -d

# Restart specific service
docker-compose restart backend
docker-compose restart worker
```

### Backend Development

```bash
# Run migrations (create new migration)
docker-compose exec backend alembic revision --autogenerate -m "migration description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# View migration history
docker-compose exec backend alembic history

# Run tests
docker-compose exec backend pytest

# Run tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Access backend shell
docker-compose exec backend bash

# View backend logs with request IDs
docker-compose logs -f backend | grep "request_id"
```

### Frontend Development

```bash
# Install dependencies (if package.json changed)
docker-compose exec frontend npm install

# Run linter
docker-compose exec frontend npm run lint

# Build production bundle
docker-compose exec frontend npm run build

# Access frontend shell
docker-compose exec frontend sh
```

### Database Operations

```bash
# Backup database
docker-compose exec postgres pg_dump -U productsnap productsnap > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T postgres psql -U productsnap productsnap < backup.sql

# Access PostgreSQL shell
docker-compose exec postgres psql -U productsnap productsnap

# Check database connection
docker-compose exec postgres pg_isready -U productsnap
```

### Redis Operations

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Check queue length
docker-compose exec redis redis-cli LLEN job_queue

# View Redis memory usage
docker-compose exec redis redis-cli INFO memory

# Clear all Redis data (use with caution)
docker-compose exec redis redis-cli FLUSHALL
```

### Worker Monitoring

```bash
# Check worker status
docker-compose ps worker

# Restart worker (e.g., after code changes)
docker-compose restart worker

# View worker processing logs
docker-compose logs -f worker | grep "Processing job"

# Check for stale jobs
docker-compose logs worker | grep "stale job"
```

## Architecture

### Backend Structure

The FastAPI backend follows a layered architecture:

- **`app/main.py`**: Application entry point, middleware setup, router registration
- **`app/worker.py`**: Background job processor (separate process), polls Redis queue
- **`app/core/`**: Core configuration, database setup, logging, Redis client
- **`app/models/`**: SQLAlchemy ORM models (User, Job, Subscription, UsageCounter, AuditLog, Session)
- **`app/routers/`**: FastAPI route handlers (auth, jobs, users, subscriptions, admin, health)
- **`app/services/`**: Business logic layer
  - `auth_service.py`: JWT tokens, OAuth, password hashing (Argon2)
  - `storage_service.py`: S3/Spaces file operations
  - `nano_banana_client.py`: External AI API client
  - `paypal_service.py`: PayPal subscription management
  - `rate_limit_service.py`: Usage quotas and rate limiting (Redis-based)
  - `email_service.py`: SMTP email notifications
- **`app/schemas/`**: Pydantic request/response models (currently empty, inline in routers)
- **`alembic/`**: Database migrations

### Frontend Structure

React SPA with Vite build tool:

- **`src/main.tsx`**: Entry point, React Query provider setup
- **`src/App.tsx`**: Root component, routing configuration
- **`src/pages/`**: Page-level components (routes)
- **`src/components/`**: Reusable UI components
- **`src/lib/`**: API client (axios), utilities
- **`src/store/`**: Zustand state management stores (auth, UI state)
- **`src/types/`**: TypeScript type definitions

Path alias `@` resolves to `./src` (configured in `vite.config.ts`).

### Key Architectural Patterns

1. **Job Queue Pattern**: Jobs are submitted to Redis list (`job_queue`), worker process polls and executes
2. **Rate Limiting**: Redis-based counters track daily/monthly usage and concurrent jobs per user
3. **Authentication Flow**: 
   - JWT access tokens (30 min) + refresh tokens (30 days)
   - Session table tracks active sessions
   - Google OAuth support (optional)
4. **Storage Architecture**: 
   - Input images uploaded to S3 `uploads/` folder
   - Results stored in `results/` folder
   - Thumbnails in `thumbnails/` folder
   - Signed URLs generated for temporary access
5. **Middleware Chain** (backend):
   - Request ID injection (for log tracing)
   - Request/response logging
   - CORS (allows frontend origin)
   - Exception handling (validation errors, general errors)

## Database Models

Core entities and relationships:

- **User**: Email/password or OAuth, links to Subscription, Jobs, UsageCounter
- **Session**: Active JWT sessions with expiration
- **Subscription**: PayPal subscription tracking (FREE/PERSONAL/PRO, ACTIVE/CANCELLED/EXPIRED)
- **Job**: Image generation job (QUEUED/PROCESSING/COMPLETED/FAILED), tracks Nano Banana job ID
- **UsageCounter**: Daily/monthly job usage per user (reset logic in rate_limit_service)
- **AuditLog**: User action tracking for compliance/debugging

Use Alembic for all schema changes. Never modify database directly.

## Environment Configuration

All configuration via environment variables (`.env` file). Critical variables:

- **Required**: `JWT_SECRET`, `POSTGRES_PASSWORD`, `NANO_BANANA_API_KEY`, S3 credentials, PayPal credentials, SMTP credentials
- **Optional**: `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` (for OAuth), `PAYPAL_MODE` (sandbox/live)
- **URLs**: `FRONTEND_URL`, `BACKEND_URL`, `VITE_API_URL` (frontend env)

Copy `.env.example` to `.env` and configure before first run.

## Testing Strategy

Backend tests use pytest with async support:

```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py

# Run with verbose output
docker-compose exec backend pytest -v

# Run with coverage report
docker-compose exec backend pytest --cov=app --cov-report=term-missing
```

Test database should be separate from development database (configure via `TEST_DATABASE_URL` if needed).

## Common Development Tasks

### Adding a New API Endpoint

1. Create route handler in appropriate `app/routers/*.py` file
2. Define Pydantic schemas for request/response (inline or in `app/schemas/`)
3. Add business logic in `app/services/` if complex
4. Update route registration in `app/main.py` if new router
5. Test endpoint at `/api/docs` (Swagger UI)

### Adding a Database Field

1. Modify SQLAlchemy model in `app/models/`
2. Generate migration: `docker-compose exec backend alembic revision --autogenerate -m "add field X"`
3. Review generated migration in `alembic/versions/`
4. Apply: `docker-compose exec backend alembic upgrade head`
5. Update relevant Pydantic schemas and API endpoints

### Modifying Job Processing Logic

1. Edit `app/worker.py` (main processing loop or `process_job` function)
2. Update related services (`nano_banana_client.py`, `storage_service.py`)
3. Restart worker: `docker-compose restart worker`
4. Monitor: `docker-compose logs -f worker`

### Debugging Job Failures

1. Check worker logs: `docker-compose logs worker | grep ERROR`
2. Check job status in database: `docker-compose exec postgres psql -U productsnap -c "SELECT id, status, error_message FROM jobs ORDER BY created_at DESC LIMIT 10;"`
3. Verify Nano Banana API key: `docker-compose exec backend env | grep NANO_BANANA`
4. Check S3 connectivity: Verify credentials in `.env`
5. Inspect stale job requeuing: Look for "Requeuing stale job" in worker logs

## API Documentation

Interactive API docs available when backend is running:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI schema**: http://localhost:8000/api/openapi.json

All endpoints prefixed with `/api/` (except health check at `/health`).

## Deployment Commands

```bash
# Deploy to production
./app-platform/deploy.sh deploy prod

# Deploy to development
./app-platform/deploy.sh deploy dev
```

## Production Deployment Notes

- Use `docker-compose.prod.yml` overlay for production config
- NGINX handles SSL termination, proxies to backend/frontend
- Let's Encrypt certificates auto-renewed via certbot container
- Worker runs as separate container for horizontal scaling
- Structured JSON logs with request IDs for tracing
- Configure firewall: ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

## Troubleshooting

**Backend won't start**: Check `.env` variables, verify PostgreSQL health with `docker-compose ps postgres`

**Worker not processing jobs**: Verify Redis connection, check queue: `docker-compose exec redis redis-cli LLEN job_queue`

**Frontend can't reach API**: Check CORS settings in `app/main.py`, verify `VITE_API_URL` matches backend URL

**Migrations fail**: Ensure no manual database changes, check migration conflicts: `docker-compose exec backend alembic history`

**Job stuck in PROCESSING**: Worker checks for stale jobs (>15 min) and requeues automatically every minute

## Code Style

- **Backend**: PEP 8, async/await for I/O operations, type hints on service methods
- **Frontend**: ESLint config in `package.json`, React hooks for state/effects
- **Imports**: Absolute imports in backend (`from app.core.config import settings`), use `@/` alias in frontend
- **Logging**: Use structured logging with extra fields (`logger.info("message", extra={...})`)
- **Error Handling**: Raise FastAPI `HTTPException` in routers, catch and log in services

## Security Considerations

- JWT secrets must be 32+ characters (set `JWT_SECRET`)
- Passwords hashed with Argon2 (via passlib)
- All external secrets via environment variables (never commit)
- S3 signed URLs for temporary access (default 3600s expiration)
- Rate limiting enforced per subscription tier
- CORS restricted to `FRONTEND_URL` + localhost
