# Docker Secrets Deployment Guide

This guide explains how to deploy ProductSnap using Docker Secrets for enhanced security.

## 🔐 What Changed

### Before (Old Method)
- Secrets stored in `.env.production` file on droplet
- File readable by root user (chmod 600)
- Passed to containers via `env_file` directive
- Visible in `docker inspect` output

### After (New Method)
- Secrets stored in Docker Swarm encrypted storage
- Never written to disk as plain text
- Mounted at `/run/secrets/` inside containers
- Not visible in `docker inspect` output
- Automatic rotation support

## 🚀 Deployment Workflow

### 1. Build Images (No Change)
```bash
./droplet/build.sh
```

### 2. Push to Registry (No Change)
```bash
./droplet/push.sh
```

### 3. Deploy with Secrets (NEW)
```bash
./droplet/deploy-secrets.sh
```

This script will:
- ✅ Initialize Docker Swarm (if not already)
- ✅ Create/update Docker Secrets from `.env.production`
- ✅ Deploy services using `docker stack deploy`
- ✅ Remove temporary secrets file from droplet
- ✅ Verify services are running

## 📋 Secrets Management

### List Secrets
```bash
ssh root@<droplet-ip>
docker secret ls
```

### Inspect Secret (metadata only, not value)
```bash
docker secret inspect productsnap_jwt_secret
```

### Update a Secret
```bash
# On droplet
./manage-secrets.sh update -s jwt_secret

# Or via deploy-secrets.sh (updates all secrets)
./deploy-secrets.sh
```

### Verify All Secrets Exist
```bash
# On droplet
cd /opt/product-snap
./manage-secrets.sh verify
```

## 🔍 Monitoring

### View Services
```bash
ssh root@<droplet-ip> 'docker stack services product-snap'
```

### View Logs
```bash
ssh root@<droplet-ip> 'docker service logs product-snap_backend'
ssh root@<droplet-ip> 'docker service logs product-snap_worker'
ssh root@<droplet-ip> 'docker service logs product-snap_frontend'
```

### Service Status
```bash
ssh root@<droplet-ip> 'docker service ls'
```

### Inspect Service
```bash
ssh root@<droplet-ip> 'docker service inspect product-snap_backend'
```

## 🛠️ Troubleshooting

### Services Not Starting
```bash
# Check service events
ssh root@<droplet-ip> 'docker service ps product-snap_backend --no-trunc'

# Check if secrets exist
ssh root@<droplet-ip> 'docker secret ls'
```

### Secret Not Loading
```bash
# Check backend logs for secret loading messages
ssh root@<droplet-ip> 'docker service logs product-snap_backend | grep "Loaded"'

# Should see:
# ✓ Loaded JWT_SECRET from secret file
# ✓ Loaded PAYPAL_CLIENT_SECRET from secret file
# etc.
```

### Rollback to Old Method
If Docker Secrets cause issues:
```bash
# Remove the stack
ssh root@<droplet-ip> 'docker stack rm product-snap'

# Use old deployment script
./droplet/deploy.sh
```

## 📊 Comparison

| Aspect | Old Method | New Method (Secrets) |
|--------|-----------|----------------------|
| Security | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Complexity | Simple | Moderate |
| Secrets on Disk | Yes (.env.production) | No (encrypted in Swarm) |
| Rotation | Manual | Automated support |
| Audit Trail | Limited | Full Swarm audit |
| Visibility | `docker inspect` | Hidden |
| Container Access | Environment vars | File mount |

## 🎯 Migration Checklist

- [ ] Test deployment with `deploy-secrets.sh`
- [ ] Verify all services start correctly
- [ ] Check backend logs for secret loading
- [ ] Test application functionality
- [ ] Monitor for 24-48 hours
- [ ] If stable, delete old `docker-compose.prod.yml`
- [ ] Update `deploy.sh` or retire it

## 🔗 Related Files

- `docker-compose.prod.secrets.yml` - Production compose with secrets
- `deploy-secrets.sh` - New deployment script
- `manage-secrets.sh` - Secret management utility (on droplet)
- `backend/app/core/config.py` - Updated to read from secret files

## ⚠️ Important Notes

1. **Swarm Mode Required**: Docker Secrets require Docker Swarm
2. **Secrets are Immutable**: To update, must delete and recreate
3. **Service Restart**: Updating secrets requires service restart
4. **Backup `.env.production`**: Still needed as source of truth
5. **Not for Local Dev**: Local development still uses regular `.env`
