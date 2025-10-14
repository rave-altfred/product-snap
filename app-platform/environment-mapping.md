# Environment Variables - App Platform

Complete reference for all environment variables required by LightClick Studio on App Platform.

## 📋 Quick Reference

| Variable | Required | Secret | Default | Service |
|----------|----------|--------|---------|---------|
| `DATABASE_URL` | ✅ | ✅ | - | Backend, Worker |
| `REDIS_URL` | ✅ | ✅ | - | Backend, Worker |
| `JWT_SECRET` | ✅ | ✅ | - | Backend, Worker |
| `S3_ENDPOINT` | ✅ | ❌ | - | Backend, Worker |
| `S3_BUCKET` | ✅ | ❌ | - | Backend, Worker |
| `S3_ACCESS_KEY` | ✅ | ✅ | - | Backend, Worker |
| `S3_SECRET_KEY` | ✅ | ✅ | - | Backend, Worker |
| `PAYPAL_CLIENT_ID` | ✅ | ✅ | - | Backend, Worker |
| `PAYPAL_CLIENT_SECRET` | ✅ | ✅ | - | Backend, Worker |
| `NANO_BANANA_API_KEY` | ✅ | ✅ | - | Backend, Worker |
| `SMTP_HOST` | ✅ | ❌ | - | Backend, Worker |
| `SMTP_USER` | ✅ | ❌ | - | Backend, Worker |
| `SMTP_PASSWORD` | ✅ | ✅ | - | Backend, Worker |
| `SMTP_FROM_EMAIL` | ✅ | ❌ | - | Backend, Worker |

---

## 🗄️ Database Configuration

### `DATABASE_URL` ✅ REQUIRED | 🔒 SECRET
**Format:** `postgresql://user:password@host:port/database?sslmode=require`

PostgreSQL connection string for Managed Database.

**Example:**
```
postgresql://doadmin:AVNS_xxxxxxxxxxxx@productsnap-postgres-do-user-12345-0.b.db.ondigitalocean.com:25060/defaultdb?sslmode=require
```

**How to get:**
```bash
doctl databases connection <postgres-db-id> --format URI
```

**Used by:** Backend, Worker

---

### `REDIS_URL` ✅ REQUIRED | 🔒 SECRET
**Format:** `rediss://username:password@host:port/0?ssl_cert_reqs=required`

Valkey (Redis) connection string with TLS enabled.

**Example:**
```
rediss://default:AVNS_xxxxxxxxxxxx@productsnap-valkey-do-user-12345-0.b.db.ondigitalocean.com:25061/0?ssl_cert_reqs=required
```

**Important:** Must use `rediss://` (with double 's') for TLS connection.

**How to get:**
```bash
doctl databases connection <valkey-db-id> --format URI
```

**Used by:** Backend, Worker

---

## 🔐 Security Configuration

### `JWT_SECRET` ✅ REQUIRED | 🔒 SECRET
**Format:** String (32+ characters)

Secret key for JWT token signing.

**Generate:**
```bash
openssl rand -base64 32
```

**Example:**
```
K7vN9mP2qR8tU5wX3yZ6bC4dF1gH0jL9mN2pQ5rT8uV
```

**Used by:** Backend, Worker

---

### `JWT_ALGORITHM`
**Default:** `HS256`

JWT signing algorithm. Don't change unless you know what you're doing.

**Used by:** Backend, Worker

---

### `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
**Default:** `30`

Access token expiration time in minutes.

**Used by:** Backend, Worker

---

### `JWT_REFRESH_TOKEN_EXPIRE_DAYS`
**Default:** `30`

Refresh token expiration time in days.

**Used by:** Backend, Worker

---

## 📦 Storage Configuration (S3/Spaces)

### `S3_ENDPOINT` ✅ REQUIRED
**Format:** `https://<region>.digitaloceanspaces.com`

DigitalOcean Spaces endpoint URL.

**Examples:**
- `https://nyc3.digitaloceanspaces.com`
- `https://sfo3.digitaloceanspaces.com`
- `https://fra1.digitaloceanspaces.com`

**Used by:** Backend, Worker

---

### `S3_BUCKET` ✅ REQUIRED
**Format:** String

Your Spaces bucket name.

**Example:** `lightclick-storage`

**Used by:** Backend, Worker

---

### `S3_ACCESS_KEY` ✅ REQUIRED | 🔒 SECRET
**Format:** String (20 characters)

Spaces access key ID.

**How to get:** Spaces → Settings → API Keys

**Used by:** Backend, Worker

---

### `S3_SECRET_KEY` ✅ REQUIRED | 🔒 SECRET
**Format:** String (40 characters)

Spaces secret access key.

**How to get:** Spaces → Settings → API Keys

**Used by:** Backend, Worker

---

### `S3_PUBLIC_ENDPOINT`
**Format:** `https://<bucket>.<region>.digitaloceanspaces.com`

Public CDN endpoint for accessing files.

**Example:** `https://lightclick-storage.nyc3.digitaloceanspaces.com`

**Used by:** Backend, Worker

---

### `S3_REGION`
**Default:** `us-east-1`

S3-compatible region identifier.

**Used by:** Backend, Worker

---

## 💳 PayPal Configuration

### `PAYPAL_CLIENT_ID` ✅ REQUIRED | 🔒 SECRET
**Format:** String

PayPal REST API client ID.

**How to get:** PayPal Developer Dashboard → Apps & Credentials

**Used by:** Backend, Worker

---

### `PAYPAL_CLIENT_SECRET` ✅ REQUIRED | 🔒 SECRET
**Format:** String

PayPal REST API client secret.

**How to get:** PayPal Developer Dashboard → Apps & Credentials

**Used by:** Backend, Worker

---

### `PAYPAL_MODE`
**Default:** `sandbox`
**Options:** `sandbox`, `live`

PayPal API mode. Use `sandbox` for testing, `live` for production.

**Used by:** Backend, Worker

---

### `PAYPAL_WEBHOOK_ID`
**Format:** String

PayPal webhook ID for verifying webhook signatures.

**How to get:** PayPal Developer Dashboard → Webhooks

**Used by:** Backend

---

### `PAYPAL_PLAN_ID_BASIC_MONTHLY` ✅ REQUIRED
**Format:** `P-xxxxxxxxxxxxx`

PayPal subscription plan ID for Basic Monthly plan.

**How to get:** Create plan via PayPal API or dashboard

**Used by:** Backend, Worker

---

### `PAYPAL_PLAN_ID_BASIC_YEARLY` ✅ REQUIRED
**Format:** `P-xxxxxxxxxxxxx`

PayPal subscription plan ID for Basic Yearly plan.

**Used by:** Backend, Worker

---

### `PAYPAL_PLAN_ID_PRO_MONTHLY` ✅ REQUIRED
**Format:** `P-xxxxxxxxxxxxx`

PayPal subscription plan ID for Pro Monthly plan.

**Used by:** Backend, Worker

---

### `PAYPAL_PLAN_ID_PRO_YEARLY` ✅ REQUIRED
**Format:** `P-xxxxxxxxxxxxx`

PayPal subscription plan ID for Pro Yearly plan.

**Used by:** Backend, Worker

---

## 🤖 AI / Image Generation

### `NANO_BANANA_API_KEY` ✅ REQUIRED | 🔒 SECRET
**Format:** String

Google Gemini API key for AI image generation.

**How to get:** Google Cloud Console → APIs & Services → Credentials

**Used by:** Backend, Worker

---

### `NANO_BANANA_API_URL`
**Default:** `https://generativelanguage.googleapis.com`

Gemini API base URL.

**Used by:** Backend, Worker

---

### `IMAGE_GENERATION_MODE`
**Default:** `live`
**Options:** `mock`, `live`

Image generation mode. Use `mock` for testing without API calls.

**Used by:** Backend, Worker

---

### `USE_VERTEX_AI`
**Default:** `false`

Whether to use Vertex AI instead of Gemini directly.

**Used by:** Backend, Worker

---

### `GOOGLE_CLOUD_PROJECT_ID`
**Format:** String

Google Cloud project ID (if using Vertex AI).

**Used by:** Backend, Worker

---

## 📧 Email Configuration (SMTP)

### `SMTP_HOST` ✅ REQUIRED
**Format:** Hostname

SMTP server hostname.

**Examples:**
- Gmail: `smtp.gmail.com`
- SendGrid: `smtp.sendgrid.net`
- Mailgun: `smtp.mailgun.org`

**Used by:** Backend, Worker

---

### `SMTP_PORT`
**Default:** `587`

SMTP server port (TLS).

**Used by:** Backend, Worker

---

### `SMTP_USER` ✅ REQUIRED
**Format:** Email or username

SMTP authentication username.

**Example:** `your-email@gmail.com`

**Used by:** Backend, Worker

---

### `SMTP_PASSWORD` ✅ REQUIRED | 🔒 SECRET
**Format:** String

SMTP authentication password or app password.

**For Gmail:** Generate app password at https://myaccount.google.com/apppasswords

**Used by:** Backend, Worker

---

### `SMTP_FROM_EMAIL` ✅ REQUIRED
**Format:** Email

Email address to send from.

**Example:** `noreply@lightclick.studio`

**Used by:** Backend, Worker

---

### `SMTP_TLS`
**Default:** `True`

Whether to use TLS for SMTP connection.

**Used by:** Backend, Worker

---

## 🔗 OAuth Configuration (Optional)

### `GOOGLE_CLIENT_ID`
**Format:** String ending in `.apps.googleusercontent.com`

Google OAuth client ID.

**How to get:** Google Cloud Console → APIs & Services → Credentials

**Used by:** Backend

---

### `GOOGLE_CLIENT_SECRET` | 🔒 SECRET
**Format:** String

Google OAuth client secret.

**How to get:** Google Cloud Console → APIs & Services → Credentials

**Used by:** Backend

---

### `GOOGLE_REDIRECT_URI`
**Format:** URL

OAuth callback URL.

**Example:** `https://your-app.ondigitalocean.app/api/auth/google/callback`

**Used by:** Backend

---

## 🌐 Application URLs

### `FRONTEND_URL`
**Default:** `${APP_URL}` (auto-populated by App Platform)

Frontend application URL.

**Used by:** Backend, Worker

---

### `BACKEND_URL`
**Default:** `${APP_URL}/api` (auto-populated by App Platform)

Backend API URL.

**Used by:** Backend, Worker

---

### `APP_NAME`
**Default:** `LightClick Studio`

Application name for display purposes.

**Used by:** Backend

---

### `LOG_LEVEL`
**Default:** `INFO`
**Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`

Logging level for application.

**Used by:** Backend, Worker

---

## 🎨 Frontend Configuration

### `VITE_API_URL`
**Default:** `${APP_URL}/api` (auto-populated by App Platform)
**Scope:** BUILD_TIME

Backend API URL for frontend to connect to.

**Used by:** Frontend (build time)

---

## 📝 Setting Environment Variables

### Via doctl CLI

```bash
# Single variable
doctl apps update <app-id> --env="KEY=value"

# Multiple variables
doctl apps update <app-id> \
  --env="KEY1=value1" \
  --env="KEY2=value2" \
  --env="KEY3=value3"
```

### Via App Platform Console

1. Go to: https://cloud.digitalocean.com/apps
2. Select your app
3. Click "Settings" → "App-Level Environment Variables"
4. Click "Edit"
5. Add variables (check "Encrypt" for secrets)
6. Click "Save"

### In app.yaml Spec

```yaml
services:
  - name: backend
    envs:
      - key: LOG_LEVEL
        value: "INFO"
      
      - key: JWT_SECRET
        value: ""
        type: SECRET
        scope: RUN_TIME
```

---

## 🔒 Security Best Practices

1. **Always encrypt secrets**: Use `type: SECRET` in app.yaml or check "Encrypt" in console
2. **Never commit secrets**: Keep `.env.production` in `.gitignore`
3. **Use strong passwords**: Generate with `openssl rand -base64 32`
4. **Rotate regularly**: Change secrets every 90 days
5. **Limit access**: Only grant necessary permissions

---

## ✅ Environment Validation Checklist

Before deploying, ensure you have set:

**Required for Backend/Worker:**
- [ ] `DATABASE_URL`
- [ ] `REDIS_URL`
- [ ] `JWT_SECRET`
- [ ] `S3_ENDPOINT`
- [ ] `S3_BUCKET`
- [ ] `S3_ACCESS_KEY`
- [ ] `S3_SECRET_KEY`
- [ ] `PAYPAL_CLIENT_ID`
- [ ] `PAYPAL_CLIENT_SECRET`
- [ ] `PAYPAL_PLAN_ID_*` (all 4 plans)
- [ ] `NANO_BANANA_API_KEY`
- [ ] `SMTP_HOST`
- [ ] `SMTP_USER`
- [ ] `SMTP_PASSWORD`
- [ ] `SMTP_FROM_EMAIL`

**Optional:**
- [ ] `GOOGLE_CLIENT_ID` (if using OAuth)
- [ ] `GOOGLE_CLIENT_SECRET` (if using OAuth)
- [ ] `S3_PUBLIC_ENDPOINT` (for CDN)
- [ ] `PAYPAL_WEBHOOK_ID` (for webhooks)

---

**Last Updated:** 2025-10-13
