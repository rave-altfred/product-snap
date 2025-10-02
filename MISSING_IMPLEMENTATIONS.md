# Missing Implementations & TODO List

This document tracks features that are **declared/configured but not yet implemented** in the ProductSnap codebase.

Generated: October 2, 2025

---

## 🔴 Critical - Core Functionality

### 1. Google OAuth Authentication
**Status**: Config exists, but no implementation

**What exists:**
- Environment variables: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- Config settings in `backend/app/core/config.py` (lines 26-28)
- OAuthProvider enum includes `GOOGLE` in `backend/app/models/user.py`
- Docker compose passes these variables to backend

**What's missing:**
- No `/api/auth/google/login` endpoint
- No `/api/auth/google/callback` endpoint
- No OAuth flow implementation in `auth_service.py`
- Frontend has no "Sign in with Google" button

**Priority**: HIGH - This is a major feature mentioned in docs

**Files to create/modify:**
```
backend/app/routers/auth.py          # Add Google OAuth endpoints
backend/app/services/auth_service.py  # Add OAuth flow logic
frontend/src/pages/Login.tsx         # Add Google login button
frontend/src/pages/Register.tsx      # Add Google signup button
```

**Implementation steps:**
1. Install google-auth library: `pip install google-auth google-auth-oauthlib google-auth-httplib2`
2. Add OAuth flow endpoints in auth router
3. Implement OAuth callback handler
4. Add "Continue with Google" button in frontend
5. Handle OAuth user creation/linking in auth service

---

### 2. PayPal Webhook Handler
**Status**: Service method exists, but no webhook endpoint

**What exists:**
- `paypal_service.verify_webhook_signature()` method implemented
- PayPal subscription creation/cancellation works
- README mentions webhook endpoint: `/api/webhooks/paypal`

**What's missing:**
- No `/api/webhooks/paypal` endpoint in any router
- No webhook event handling logic
- No subscription status updates from PayPal events
- No webhook verification implementation

**Priority**: HIGH - Required for subscription lifecycle management

**Files to create:**
```
backend/app/routers/webhooks.py  # New file for webhook endpoints
```

**Implementation steps:**
1. Create webhooks router
2. Add POST `/api/webhooks/paypal` endpoint
3. Verify PayPal webhook signature
4. Handle events:
   - `BILLING.SUBSCRIPTION.ACTIVATED`
   - `BILLING.SUBSCRIPTION.CANCELLED`
   - `BILLING.SUBSCRIPTION.SUSPENDED`
   - `BILLING.SUBSCRIPTION.EXPIRED`
   - `PAYMENT.SALE.COMPLETED`
5. Update subscription status in database
6. Register router in `main.py`
7. Configure webhook URL in PayPal dashboard

**PayPal Events to handle:**
```python
SUBSCRIPTION_ACTIVATED     → Set status to ACTIVE
SUBSCRIPTION_CANCELLED     → Set status to CANCELLED
SUBSCRIPTION_SUSPENDED     → Set status to CANCELLED
SUBSCRIPTION_EXPIRED       → Set status to EXPIRED
PAYMENT_SALE_COMPLETED     → Update billing info
```

---

### 3. PayPal Subscription Management Endpoints
**Status**: Service exists, but minimal API endpoints

**What exists:**
- `GET /api/subscriptions/me` - Get current subscription
- PayPal service with create/cancel/get methods

**What's missing:**
- `POST /api/subscriptions/create` - Initiate subscription upgrade
- `POST /api/subscriptions/cancel` - Cancel subscription
- `GET /api/subscriptions/plans` - List available plans with pricing
- `POST /api/subscriptions/resume` - Resume cancelled subscription

**Priority**: HIGH - Users can't actually subscribe!

**Files to modify:**
```
backend/app/routers/subscriptions.py  # Add missing endpoints
frontend/src/pages/Billing.tsx        # Implement subscription UI
```

---

### 4. Database Migrations
**Status**: Alembic configured but no migrations exist

**What exists:**
- Alembic setup in `backend/alembic/`
- `alembic.ini` configuration
- SQLAlchemy models fully defined

**What's missing:**
- No migration files in `alembic/versions/`
- Database schema not created
- Application won't work without migrations

**Priority**: CRITICAL - Must be done before first run

**Command to run:**
```bash
docker-compose exec backend alembic revision --autogenerate -m "Initial schema"
docker-compose exec backend alembic upgrade head
```

---

## 🟡 Important - User Experience

### 5. Session Revocation on Logout
**Status**: Logout endpoint exists but doesn't revoke sessions

**What exists:**
- `POST /api/auth/logout` endpoint
- Session model tracks active sessions
- TODO comment in code: "For now, we can't easily revoke without session ID in token"

**What's missing:**
- Session ID not included in JWT payload
- No actual session revocation in database
- Users remain logged in even after logout

**Priority**: MEDIUM-HIGH - Security issue

**Files to modify:**
```
backend/app/services/auth_service.py  # Include session_id in JWT
backend/app/routers/auth.py          # Revoke session on logout
```

**Implementation:**
1. Add `session_id` to JWT payload when creating access token
2. Modify logout endpoint to delete session from database
3. Optionally: Check session validity on each request (performance tradeoff)

---

### 6. Email Verification Flow
**Status**: Partially implemented

**What exists:**
- Email verification token generated on registration
- `POST /api/auth/verify-email` endpoint
- Email service with send_verification_email method
- Token stored in Redis with 24h expiration

**What's missing:**
- Frontend verification page/component
- Email click-through link handling
- Resend verification email endpoint
- Enforcement of email verification (users can use app without verifying)

**Priority**: MEDIUM

**Files to create/modify:**
```
frontend/src/pages/VerifyEmail.tsx     # New verification page
backend/app/routers/auth.py            # Add resend endpoint
frontend/src/App.tsx                   # Add route
```

---

### 7. Password Reset Flow
**Status**: Not implemented at all

**What exists:**
- Email service can send emails
- User model has password_hash field

**What's missing:**
- `POST /api/auth/forgot-password` endpoint
- `POST /api/auth/reset-password` endpoint
- Password reset token generation/validation
- Frontend forgot password page
- Password reset email template

**Priority**: MEDIUM - Common user need

**Files to create:**
```
backend/app/routers/auth.py              # Add password reset endpoints
backend/app/services/email_service.py    # Add reset email template
frontend/src/pages/ForgotPassword.tsx    # New page
frontend/src/pages/ResetPassword.tsx     # New page
```

---

### 8. Job Result Watermarking (Free Tier)
**Status**: Mentioned in docs but not implemented

**What exists:**
- Rate limits check subscription tier
- Worker processes all jobs the same way

**What's missing:**
- Image watermarking logic for FREE tier users
- Watermark image asset
- Conditional watermarking based on subscription

**Priority**: MEDIUM - Business model requirement

**Files to modify:**
```
backend/app/worker.py                    # Add watermark logic
backend/assets/watermark.png             # Watermark image
```

**Implementation:**
1. Add Pillow watermarking function
2. Check user subscription tier in worker
3. Apply watermark to FREE tier results
4. Skip watermark for PERSONAL/PRO tiers

---

### 9. Custom Prompts (Pro Tier)
**Status**: Backend supports it, frontend doesn't

**What exists:**
- `custom_prompt` parameter in job creation
- `NanoBananaClient` appends custom prompts
- PRO tier mentioned to support custom prompts

**What's missing:**
- Frontend UI for custom prompt input
- Tier checking before accepting custom prompts
- Error message if non-PRO user tries custom prompts

**Priority**: MEDIUM

**Files to modify:**
```
frontend/src/pages/NewShoot.tsx          # Add custom prompt field
backend/app/routers/jobs.py              # Verify PRO tier for custom prompts
```

---

## 🟢 Nice to Have - Enhancement

### 10. Frontend Tests
**Status**: No tests exist

**What's missing:**
- No test files at all
- No test configuration
- No CI setup

**Priority**: LOW-MEDIUM

**Setup needed:**
```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
```

---

### 11. Backend Unit Tests
**Status**: Test directory exists but empty

**What exists:**
- `backend/tests/` directory created
- pytest in requirements.txt

**What's missing:**
- No test files
- No fixtures
- No test database setup
- Coverage near 0%

**Priority**: MEDIUM

**Key tests needed:**
```
tests/test_auth_service.py          # Password hashing, JWT, OAuth
tests/test_rate_limit_service.py    # Quota enforcement
tests/test_nano_banana_client.py    # API mocking
tests/test_storage_service.py       # S3 operations
tests/test_paypal_service.py        # Subscription logic
tests/test_routers/test_auth.py     # Auth endpoints
tests/test_routers/test_jobs.py     # Job endpoints
```

---

### 12. Admin Dashboard Features
**Status**: Router exists, minimal implementation

**What exists:**
- `backend/app/routers/admin.py` file
- Basic structure
- No actual admin endpoints

**What's missing:**
- User management endpoints (list, disable, delete)
- Job monitoring/management
- System statistics
- Subscription overview
- Admin authentication check

**Priority**: MEDIUM

**Endpoints to add:**
```
GET  /api/admin/users              # List all users
GET  /api/admin/users/{id}         # User details
PUT  /api/admin/users/{id}/disable # Disable user
GET  /api/admin/jobs               # List all jobs
GET  /api/admin/stats              # System statistics
GET  /api/admin/subscriptions      # Subscription overview
```

---

### 13. Job Priority Queue (Pro Tier)
**Status**: Mentioned in docs but not implemented

**What exists:**
- Redis job queue (`LPUSH`/`RPOP`)
- Worker processes jobs sequentially

**What's missing:**
- Separate priority queues for different tiers
- PRO jobs processed before FREE jobs
- Queue priority logic

**Priority**: LOW-MEDIUM

**Implementation:**
```
job_queue_pro      → Process first (PRO tier)
job_queue_personal → Process second (PERSONAL tier)
job_queue_free     → Process last (FREE tier)
```

---

### 14. Real-time Job Progress Updates
**Status**: Mentioned in README, not implemented

**What exists:**
- Job status in database (QUEUED, PROCESSING, COMPLETED, FAILED)
- Polling available via `GET /api/jobs/{id}`

**What's missing:**
- WebSocket connection for real-time updates
- Progress percentage tracking
- Frontend real-time UI updates

**Priority**: LOW

**Files to create:**
```
backend/app/routers/websockets.py    # WebSocket endpoint
frontend/src/lib/websocket.ts        # WS client
```

---

### 15. File Upload Validation
**Status**: Partially implemented

**What exists:**
- Config defines limits: `MAX_UPLOAD_SIZE`, `ALLOWED_IMAGE_TYPES`, `MIN_IMAGE_WIDTH`, `MIN_IMAGE_HEIGHT`
- Job creation accepts file uploads

**What's missing:**
- Actual enforcement of file size limit
- Image dimension validation
- File type verification (not just extension)
- Proper error messages

**Priority**: MEDIUM - Security & UX

**Files to modify:**
```
backend/app/routers/jobs.py    # Add validation before S3 upload
```

---

### 16. Thumbnail Generation
**Status**: Mentioned in storage architecture, not implemented

**What exists:**
- S3 folder structure includes `thumbnails/`
- Storage service can upload files

**What's missing:**
- Thumbnail generation logic
- Automatic thumbnail creation on upload/completion
- Thumbnail size configuration
- Frontend displaying thumbnails in library

**Priority**: LOW-MEDIUM - Performance optimization

---

### 17. Audit Logging
**Status**: Model exists, not used

**What exists:**
- `AuditLog` model defined
- Fields for action, user, IP, user agent

**What's missing:**
- No audit log records created anywhere
- No audit log viewing endpoint
- No admin audit trail

**Priority**: LOW - Compliance feature

**Actions to log:**
```
- User registration
- Login/logout
- Password changes
- Subscription changes
- Job creation
- Admin actions
```

---

### 18. Environment Configuration
**Status**: `.env.example` exists, no `.env`

**What's missing:**
- Actual `.env` file (must be created by developer)
- Validation that required env vars are set
- Startup checks for missing config

**Priority**: CRITICAL (for first run)

**Command to run:**
```bash
cp .env.example .env
# Then edit .env with actual credentials
```

---

### 19. NGINX SSL Configuration
**Status**: Config exists but placeholders

**What exists:**
- NGINX config files
- SSL directory structure
- Certbot container for Let's Encrypt

**What's missing:**
- Actual SSL certificates (need domain)
- Domain-specific NGINX config
- Certificate renewal testing

**Priority**: CRITICAL (for production)

**Steps:**
1. Point domain DNS to server IP
2. Run certbot to get certificates
3. Update NGINX config with domain name
4. Test certificate renewal

---

### 20. Database Backup Automation
**Status**: Script exists, not automated

**What exists:**
- `deployment/backup.sh` script
- Manual backup capability

**What's missing:**
- Cron job for automated backups
- Backup to remote storage (S3)
- Backup monitoring/alerts
- Restoration testing

**Priority**: HIGH (for production)

**Setup:**
```bash
# Add to crontab
0 2 * * * /path/to/backup.sh  # Daily at 2 AM
```

---

## Summary Statistics

| Priority | Count | Category |
|----------|-------|----------|
| 🔴 CRITICAL | 4 | Must implement before launch |
| 🟡 HIGH | 5 | Core features missing |
| 🟢 MEDIUM | 8 | UX & security improvements |
| ⚪ LOW | 3 | Nice-to-have enhancements |
| **TOTAL** | **20** | **Missing features** |

---

## Recommended Implementation Order

### Phase 1: MVP (Minimum Viable Product)
1. ✅ Database Migrations (CRITICAL)
2. ✅ Environment Configuration (CRITICAL)
3. ✅ PayPal Subscription Endpoints (HIGH)
4. ✅ PayPal Webhook Handler (HIGH)
5. ✅ File Upload Validation (MEDIUM)

### Phase 2: User Experience
6. ✅ Password Reset Flow (MEDIUM)
7. ✅ Email Verification Frontend (MEDIUM)
8. ✅ Session Revocation (HIGH)
9. ✅ Google OAuth (HIGH)

### Phase 3: Business Logic
10. ✅ Watermarking for Free Tier (MEDIUM)
11. ✅ Custom Prompts UI (MEDIUM)
12. ✅ Thumbnail Generation (MEDIUM)

### Phase 4: Production Readiness
13. ✅ NGINX SSL (CRITICAL for production)
14. ✅ Database Backup Automation (HIGH)
15. ✅ Admin Dashboard (MEDIUM)
16. ✅ Backend Tests (MEDIUM)

### Phase 5: Polish
17. ✅ Audit Logging (LOW)
18. ✅ Job Priority Queue (LOW)
19. ✅ Real-time Updates (LOW)
20. ✅ Frontend Tests (LOW)

---

## Next Immediate Actions

**To get the app running locally:**
```bash
# 1. Create environment file
cp .env.example .env
# Edit .env with real credentials

# 2. Run database migrations
docker-compose up -d postgres redis
docker-compose exec backend alembic revision --autogenerate -m "Initial schema"
docker-compose exec backend alembic upgrade head

# 3. Start all services
docker-compose up -d

# 4. Verify health
curl http://localhost:8000/health
```

**To implement PayPal subscriptions (HIGH priority):**
1. Create `backend/app/routers/webhooks.py`
2. Add subscription management endpoints to `subscriptions.py`
3. Update frontend billing page
4. Test subscription flow in PayPal sandbox

**To add Google OAuth (HIGH priority):**
1. Install google-auth library
2. Add OAuth endpoints to `auth.py`
3. Add "Sign in with Google" button to frontend
4. Test OAuth flow with Google developer console

---

*This document should be updated as features are implemented.*
