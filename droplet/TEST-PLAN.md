# Docker Secrets Deployment Test Plan

## ✅ Pre-Deployment Checklist

### 1. Verify Prerequisites
- [ ] `doctl` is installed and authenticated
- [ ] SSH access to droplet works: `ssh root@206.81.18.66`
- [ ] `.env.production` file exists and is complete
- [ ] Latest code committed to git

### 2. Build and Push Images
```bash
# Build images locally
./droplet/build.sh

# Check if images were built
docker images | grep product-snap

# Push to DO registry
./droplet/push.sh
```

### 3. Pre-Deployment Snapshot (Optional but Recommended)
```bash
# Check current services
ssh root@206.81.18.66 'docker ps'

# Check if docker-compose is running
ssh root@206.81.18.66 'docker-compose -f /opt/product-snap/docker-compose.yml ps'

# Take note of current state
```

---

## 🚀 Deployment Test

### Step 1: Deploy with Docker Secrets
```bash
./droplet/deploy-secrets.sh
```

**Watch for:**
- ✓ SSH connection successful
- ✓ Docker Swarm initialized
- ✓ Secrets created/updated
- ✓ Images pulled
- ✓ Stack deployed
- ✓ Services started

### Step 2: Verify Services Started
```bash
ssh root@206.81.18.66 'docker stack services product-snap'
```

**Expected output:**
```
ID             NAME                     MODE         REPLICAS   IMAGE
xxx            product-snap_backend     replicated   1/1        registry...
xxx            product-snap_frontend    replicated   1/1        registry...
xxx            product-snap_worker      replicated   1/1        registry...
xxx            product-snap_redis       replicated   1/1        redis:7-alpine
```

All should show `1/1` in REPLICAS column.

### Step 3: Check Backend Logs for Secret Loading
```bash
ssh root@206.81.18.66 'docker service logs product-snap_backend --tail 50 | grep -E "(Loaded|Warning|Error)"'
```

**Expected to see:**
```
✓ Loaded JWT_SECRET from secret file
✓ Loaded PAYPAL_CLIENT_SECRET from secret file
✓ Loaded NANO_BANANA_API_KEY from secret file
✓ Loaded S3_SECRET_KEY from secret file
✓ Loaded SMTP_PASSWORD from secret file
```

### Step 4: Verify Secrets Exist
```bash
ssh root@206.81.18.66 'docker secret ls'
```

**Expected secrets:**
- productsnap_jwt_secret
- productsnap_paypal_client_secret
- productsnap_nano_banana_api_key
- productsnap_s3_secret_key
- productsnap_smtp_password
- productsnap_google_client_secret (optional)

### Step 5: Test Application Health
```bash
# Check backend health endpoint
curl -f https://lightclick.utils.studio/health

# Should return: {"status": "ok"} or similar
```

---

## 🧪 Functional Tests

### Test 1: Login
```bash
# Try logging in to the application
open https://lightclick.utils.studio
```
- [ ] Login page loads
- [ ] Can log in with test credentials
- [ ] JWT token is issued (check browser dev tools)

### Test 2: Job Submission
- [ ] Can upload image
- [ ] Job is queued
- [ ] Worker processes job
- [ ] Results are returned

### Test 3: PayPal Integration
- [ ] Can view subscription plans
- [ ] PayPal checkout loads (if applicable)

### Test 4: Email Notifications
- [ ] Email sending works (check logs)

---

## 🔍 Monitoring (First 30 Minutes)

### Check Logs Continuously
```bash
# Backend
ssh root@206.81.18.66 'docker service logs -f product-snap_backend'

# Worker
ssh root@206.81.18.66 'docker service logs -f product-snap_worker'

# Frontend
ssh root@206.81.18.66 'docker service logs -f product-snap_frontend'
```

### Watch for Errors
Look for:
- ❌ "Failed to load secret"
- ❌ "Connection refused"
- ❌ "Authentication failed"
- ❌ Service restarts/crashes

### Check Service Status Every 5 Minutes
```bash
watch -n 5 "ssh root@206.81.18.66 'docker stack services product-snap'"
```

---

## ⚠️ Rollback Plan (If Needed)

If anything goes wrong:

### Quick Rollback
```bash
# Remove the stack
ssh root@206.81.18.66 'docker stack rm product-snap'

# Wait for services to stop
sleep 30

# Deploy with old method
./droplet/deploy.sh
```

### Verify Rollback
```bash
ssh root@206.81.18.66 'docker-compose -f /opt/product-snap/docker-compose.yml ps'
```

---

## ✅ Success Criteria

Mark as successful if ALL of these pass:

- [ ] All services show `1/1` replicas
- [ ] Backend logs show "✓ Loaded" messages for all secrets
- [ ] Application is accessible at https://lightclick.utils.studio
- [ ] User login works
- [ ] Job submission and processing works
- [ ] No errors in logs for 30 minutes
- [ ] Database connectivity confirmed
- [ ] S3 storage works (file upload/download)
- [ ] Email sending works

---

## 📊 Test Results

### Deployment Time
- Started: ___________
- Completed: ___________
- Duration: ___________

### Services Status
- Backend: ⬜ OK / ⬜ FAIL
- Worker: ⬜ OK / ⬜ FAIL
- Frontend: ⬜ OK / ⬜ FAIL
- Redis: ⬜ OK / ⬜ FAIL

### Secrets Loaded
- JWT_SECRET: ⬜ OK / ⬜ FAIL
- PAYPAL_CLIENT_SECRET: ⬜ OK / ⬜ FAIL
- NANO_BANANA_API_KEY: ⬜ OK / ⬜ FAIL
- S3_SECRET_KEY: ⬜ OK / ⬜ FAIL
- SMTP_PASSWORD: ⬜ OK / ⬜ FAIL

### Functional Tests
- Login: ⬜ OK / ⬜ FAIL
- Job Processing: ⬜ OK / ⬜ FAIL
- File Upload: ⬜ OK / ⬜ FAIL

### Overall Result
⬜ **PASS** - Ready to delete old files
⬜ **FAIL** - Need to rollback and debug

---

## 📝 Notes

Document any issues encountered:

```
<!-- Add notes here -->
```

---

## 🎯 Next Steps After Success

1. Monitor for 24-48 hours
2. If stable:
   - Delete `droplet/docker-compose.prod.yml`
   - Rename `docker-compose.prod.secrets.yml` to `docker-compose.prod.yml`
   - Update `deploy-secrets.sh` to use new name
   - Update main `deploy.sh` to use secrets (or retire it)
3. Update documentation
4. Celebrate! 🎉
