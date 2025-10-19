# PostHog Analytics Integration

PostHog has been integrated into both the frontend (React) and backend (FastAPI) to track user behavior and key events.

## Configuration

### Environment Variables

The PostHog API key is already configured in:
- `app-platform/.do/app.yaml` (production)
- `app-platform/.do/app-dev.yaml` (development)
- `backend/.env.example` (local backend)
- `frontend/.env` (local frontend)

**API Key**: `phc_OmHOpQohQb8bYKAnp5X1dCuTH7jENHCdibEjIOEU8ji`  
**Host**: `https://us.i.posthog.com`

## Frontend Tracking

### Auto-tracked Events
- **Page views**: Automatically tracked on every route change
- **Page leave**: Tracked when users leave pages

### User Identification
Users are automatically identified when they:
- **Register** - Email, name, and OAuth provider tracked
- **Login** - Session starts with user context
- **Logout** - PostHog session reset

**Location**: `frontend/src/store/authStore.ts`

### Manual Event Tracking
To track custom events in the frontend:

```typescript
import posthog from 'posthog-js'

// Track an event
posthog.capture('button_clicked', {
  button_name: 'generate',
  mode: 'studio_white'
})

// Identify user properties
posthog.identify(userId, {
  subscription_tier: 'pro',
  jobs_completed: 42
})
```

## Backend Tracking

### Tracked Events

1. **User Registration** (`user_registered`)
   - Properties: `method` (email/google)
   - Location: `backend/app/routers/auth.py`

2. **User Login** (`user_logged_in`)
   - Properties: `method` (email/google)
   - Location: `backend/app/routers/auth.py`

3. **Job Completed** (`job_completed`)
   - Properties: `job_id`, `mode`, `processing_time_seconds`, `num_results`
   - Location: `backend/app/worker.py`

4. **Job Failed** (`job_failed`)
   - Properties: `job_id`, `mode`, `error`
   - Location: `backend/app/worker.py`

### Analytics Service

**File**: `backend/app/services/analytics_service.py`

```python
from app.services.analytics_service import analytics

# Track an event
analytics.capture(
    user_id=str(user.id),
    event="subscription_upgraded",
    properties={
        "from_tier": "free",
        "to_tier": "pro",
        "plan_type": "monthly"
    }
)

# Identify user
analytics.identify(
    user_id=str(user.id),
    properties={
        "email": user.email,
        "subscription_tier": "pro",
        "is_admin": user.is_admin
    }
)
```

## Deployment

### Build-time Configuration

The frontend Dockerfile now accepts PostHog env vars as build arguments:

```bash
docker build \
  --build-arg VITE_API_URL=https://lightclick.studio/api \
  --build-arg VITE_POSTHOG_API_KEY=phc_OmHOpQohQb8bYKAnp5X1dCuTH7jENHCdibEjIOEU8ji \
  --build-arg VITE_POSTHOG_HOST=https://us.i.posthog.com \
  -f frontend/Dockerfile .
```

These are automatically provided by DigitalOcean App Platform via the `scope: RUN_AND_BUILD_TIME` configuration.

### Runtime Configuration

Backend PostHog is configured at runtime via environment variables (already set in app.yaml files).

## Viewing Analytics

1. Go to https://app.posthog.com/
2. Log in with your account
3. View dashboards, insights, and session recordings

### Recommended Dashboards

Create these insights in PostHog:

1. **User Funnel**: Registration → First Job → Job Completed → Subscription Upgrade
2. **Job Metrics**: 
   - Job completion rate (completed vs failed)
   - Average processing time
   - Jobs by mode (Studio White, Model Try-On, Lifestyle Scene)
3. **Retention**: Day 1, Day 7, Day 30 retention cohorts
4. **Subscription Conversions**: Free → Personal → Pro upgrades

## Privacy Considerations

- PostHog is configured with `person_profiles: 'identified_only'` to only track authenticated users
- No PII is sent to PostHog beyond email addresses (which are hashed by PostHog)
- Analytics can be disabled by removing the `POSTHOG_API_KEY` environment variable

## Free Tier Limits

- **1 million events/month** - Should be sufficient for early stage
- **Unlimited users**
- **Full feature access** (session replay, feature flags, analytics)

If you exceed 1M events/month, consider self-hosting PostHog or upgrading to a paid plan.
