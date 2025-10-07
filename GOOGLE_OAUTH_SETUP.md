# Google OAuth Setup Guide

This guide explains how to set up and test Google OAuth authentication for ProductSnap.

## Overview

Google OAuth has been implemented with the following components:

### Backend (FastAPI)
- **Endpoints**:
  - `GET /api/auth/google/login` - Initiates OAuth flow
  - `GET /api/auth/google/callback` - Handles OAuth callback

- **Features**:
  - CSRF protection using state tokens stored in Redis
  - Automatic user creation for new Google users
  - Account linking for existing users with same email
  - Email verification from Google
  - Profile picture import from Google

### Frontend (React)
- **Pages**:
  - `Login.tsx` - "Sign in with Google" button
  - `Register.tsx` - "Sign up with Google" button
  - `OAuthCallback.tsx` - Handles OAuth redirect and token storage

- **Features**:
  - Beautiful Google button with official branding
  - Error handling for OAuth failures
  - Automatic redirect to dashboard on success

---

## Google Cloud Console Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "ProductSnap" (or your preferred name)
4. Click "Create"

### 2. Enable Google+ API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and press "Enable"

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type (for testing)
3. Fill in the required fields:
   - **App name**: ProductSnap
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Click "Save and Continue"
5. On "Scopes" page, click "Save and Continue" (default scopes are fine)
6. On "Test users" page, add your Google email for testing
7. Click "Save and Continue"

### 4. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Web application"
4. Configure:
   - **Name**: ProductSnap Web Client
   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (frontend)
     - `http://localhost:8000` (backend)
   - **Authorized redirect URIs**:
     - `http://localhost:8000/api/auth/google/callback`
     - For production: `https://api.yourdomain.com/api/auth/google/callback`
5. Click "Create"
6. **Save the Client ID and Client Secret** - you'll need these!

---

## Environment Configuration

### Development (.env)

Create or update your `.env` file:

```bash
# Copy from example if needed
cp .env.example .env
```

Update these values in `.env`:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# URLs (for local development)
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### Production

For production deployment, update:

```bash
GOOGLE_REDIRECT_URI=https://api.yourdomain.com/api/auth/google/callback
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com
```

And add the production redirect URI to Google Cloud Console credentials.

---

## Testing the Implementation

### 1. Start the Services

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 2. Test the OAuth Flow

#### From Login Page:

1. Open http://localhost:3000/login
2. Click "Sign in with Google"
3. You should be redirected to Google's consent screen
4. Select your Google account (must be added as test user)
5. Grant permissions
6. You should be redirected back to the app and logged in
7. Check the dashboard at http://localhost:3000/dashboard

#### From Register Page:

1. Open http://localhost:3000/register
2. Click "Sign up with Google"
3. Same flow as above
4. A new account will be created for you

### 3. Verify User in Database

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U productsnap productsnap

# Check users
SELECT id, email, oauth_provider, oauth_sub, email_verified, created_at FROM users;

# Check subscriptions
SELECT user_id, plan, status FROM subscriptions;

# Exit psql
\q
```

You should see:
- User with `oauth_provider = 'GOOGLE'`
- User with `email_verified = true`
- User with a `FREE` subscription

### 4. Test Account Linking

If you already have an account with email/password:

1. Logout from your current session
2. Click "Sign in with Google"
3. Use the same email address
4. Your Google account will be linked to the existing account
5. You can now log in with either method

---

## Troubleshooting

### "Google OAuth is not configured" Error

**Cause**: Environment variables not set or backend can't read them

**Solution**:
```bash
# Check if variables are set
docker-compose exec backend env | grep GOOGLE

# Restart backend after updating .env
docker-compose restart backend
```

### "redirect_uri_mismatch" Error

**Cause**: The redirect URI doesn't match what's configured in Google Console

**Solution**:
1. Check the exact error message URL
2. Go to Google Cloud Console → Credentials
3. Add the exact redirect URI to "Authorized redirect URIs"
4. Make sure there are no trailing slashes or typos

### OAuth Flow Starts but Fails at Callback

**Cause**: State token expired or Redis not working

**Solution**:
```bash
# Check Redis is running
docker-compose ps redis

# Check Redis connection
docker-compose exec redis redis-cli ping
# Should return "PONG"

# Check backend logs
docker-compose logs backend | grep -i oauth
```

### User Gets Redirected to Login with Error

Check the error parameter in the URL:
- `?error=invalid_state` - CSRF token validation failed
- `?error=oauth_failed` - Token exchange or user creation failed
- `?error=missing_tokens` - Callback didn't receive tokens

**Check backend logs** for detailed error messages:
```bash
docker-compose logs backend | tail -50
```

### Frontend Can't Connect to Backend

**Cause**: CORS or API URL misconfiguration

**Solution**:
1. Check `VITE_API_URL` in frontend container
2. Verify CORS settings in `backend/app/main.py`
3. Make sure backend is accessible at http://localhost:8000

### "Access Blocked: This app is not verified"

**Cause**: Google OAuth consent screen not published

**Solution**:
1. This is normal for development/testing
2. Click "Advanced" → "Go to ProductSnap (unsafe)"
3. This only shows for apps not verified by Google
4. For production, you'll need to submit for verification

---

## Security Considerations

### CSRF Protection
- State tokens are generated and stored in Redis
- Tokens expire after 10 minutes
- Validated in the callback endpoint

### Token Storage
- Access tokens and refresh tokens stored in localStorage
- In production, consider using httpOnly cookies for better security

### Account Linking
- Google accounts can be linked to existing email/password accounts
- Email addresses must match for automatic linking
- Email verification status is updated from Google

### OAuth Scopes
Current scopes requested:
- `openid` - OpenID Connect authentication
- `email` - Email address
- `profile` - Basic profile info (name, picture)

### Redis Security
- State tokens are automatically cleaned up after 10 minutes
- No sensitive data stored in state tokens

---

## API Endpoints Documentation

### GET /api/auth/google/login

**Description**: Initiates Google OAuth flow

**Response**:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=..."
}
```

**Frontend Usage**:
```typescript
const { data } = await axios.get(`${API_URL}/api/auth/google/login`)
window.location.href = data.authorization_url
```

### GET /api/auth/google/callback

**Description**: Handles OAuth callback from Google

**Query Parameters**:
- `code` (string, required) - Authorization code from Google
- `state` (string, required) - CSRF protection token

**Response**: Redirects to frontend with tokens
- Success: `{FRONTEND_URL}/auth/callback?access_token=xxx&refresh_token=yyy`
- Error: `{FRONTEND_URL}/login?error=oauth_failed`

**User Creation/Linking Logic**:
1. Exchange code for Google tokens
2. Get user info from Google
3. Check if user exists with Google OAuth:
   - If yes → login existing user
4. If no, check if email exists with different provider:
   - If yes → link Google account to existing user
5. If no existing user → create new user with:
   - Free subscription
   - Email verified from Google
   - Profile picture from Google

---

## Production Deployment Checklist

- [ ] Add production redirect URI to Google Console
- [ ] Update `GOOGLE_REDIRECT_URI` in production `.env`
- [ ] Update `FRONTEND_URL` and `BACKEND_URL` for production
- [ ] Verify OAuth consent screen is published (for verified app)
- [ ] Test OAuth flow on production domain
- [ ] Set up SSL/HTTPS (OAuth requires HTTPS in production)
- [ ] Consider rate limiting on OAuth endpoints
- [ ] Set up monitoring/alerts for OAuth failures
- [ ] Document OAuth flow for users (privacy policy, terms)

---

## Testing Checklist

- [x] Backend endpoints implemented
- [x] Frontend OAuth buttons added
- [x] OAuth callback page created
- [x] Environment variables documented
- [ ] Google Cloud Console configured
- [ ] Test new user registration via Google
- [ ] Test existing user login via Google
- [ ] Test account linking (email match)
- [ ] Test error handling (invalid state, expired token)
- [ ] Test email verification status
- [ ] Test profile picture import
- [ ] Verify database records created correctly
- [ ] Verify subscription created for new users

---

## Next Steps

1. **Setup Google Cloud Console** (see above)
2. **Configure environment variables** in `.env`
3. **Restart services**: `docker-compose restart`
4. **Test the flow** using the testing guide above
5. **Verify in database** that users are created correctly

## Need Help?

- Check backend logs: `docker-compose logs -f backend`
- Check frontend logs: `docker-compose logs -f frontend`
- Check Redis: `docker-compose exec redis redis-cli`
- Review MISSING_IMPLEMENTATIONS.md for context

---

## Code References

**Backend**:
- `backend/app/routers/auth.py` - OAuth endpoints (lines 246-361)
- `backend/app/services/auth_service.py` - Token exchange (lines 146-177)
- `backend/app/core/config.py` - Configuration (lines 26-28)

**Frontend**:
- `frontend/src/pages/Login.tsx` - Google login button
- `frontend/src/pages/Register.tsx` - Google signup button
- `frontend/src/pages/OAuthCallback.tsx` - Callback handler
- `frontend/src/App.tsx` - Route configuration

**Environment**:
- `.env.example` - Environment template with all required variables
