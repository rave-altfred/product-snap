# LightClick Studio - Quick Deployment Guide

## 🚀 First Time Setup

```bash
# 1. Install doctl
brew install doctl
doctl auth init

# 2. Navigate to app-platform directory
cd /Users/ravenir/dev/apps/product-snap/app-platform

# 3. Build and push images
./build-and-push.sh productsnap-registry latest

# 4. Validate configuration
./deploy.sh validate

# 5. Create app
./deploy.sh create

# 6. Monitor deployment
./deploy.sh logs
```

---

## 🔄 Regular Deployment (After Code Changes)

```bash
# 1. Build and push new images
./build-and-push.sh productsnap-registry latest

# 2. Deploy update
./deploy.sh update

# 3. Watch logs
./deploy.sh logs
```

---

## 📋 Common Commands

### Deployment Management

```bash
./deploy.sh create              # Create new app
./deploy.sh update              # Update existing app
./deploy.sh list                # List all apps
./deploy.sh info                # Get app details
./deploy.sh validate            # Validate app.yaml
```

### Log Viewing

```bash
./deploy.sh logs                # View deployment logs
./deploy.sh logs "" BUILD       # View build logs
./deploy.sh logs "" RUN         # View runtime logs
```

### Image Building

```bash
# Build with tag
./build-and-push.sh productsnap-registry latest
./build-and-push.sh productsnap-registry v1.0.0
./build-and-push.sh productsnap-registry staging
```

---

## 🐛 Quick Troubleshooting

### Deployment fails?
```bash
./deploy.sh logs "" BUILD
./deploy.sh validate
```

### Service won't start?
```bash
./deploy.sh logs "" RUN
./deploy.sh info
```

### Need to check database?
```bash
doctl databases list
doctl databases get <db-id>
```

---

## 📁 Important Files

- **`.do/app.yaml`** - App Platform configuration
- **`.do/app-id.txt`** - Saved app ID (auto-generated)
- **`build-and-push.sh`** - Build/push Docker images
- **`deploy.sh`** - Deployment management

---

## 🔗 Quick Links

- **App Console:** https://cloud.digitalocean.com/apps
- **Registry:** https://cloud.digitalocean.com/registry
- **Databases:** https://cloud.digitalocean.com/databases
- **Documentation:** https://docs.digitalocean.com/products/app-platform/

---

## ⚡ One-Liner Deployment

```bash
./build-and-push.sh productsnap-registry latest && ./deploy.sh update && ./deploy.sh logs
```

---

**Need more details?** See `README.md` for comprehensive guide.
