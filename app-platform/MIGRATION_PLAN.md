# LightClick Studio - App Platform Migration Plan

## Overview

This document outlines the complete migration strategy from DigitalOcean Droplet deployment to App Platform deployment.

**Migration Date**: TBD  
**Current Status**: Planning Phase  
**Target Environment**: DigitalOcean App Platform

---

## 📊 Current Architecture (Droplet)

### Services Running on Droplet
1. **Backend** (FastAPI) - Port 8000, localhost only
2. **Frontend** (React/Vite) - Port 80, localhost only
3. **Worker** (Background job processor) - No exposed ports
4. **Redis** (Local container) - Port 6379, localhost only
5. **System NGINX** - Ports 80/443, handles SSL termination

### External Managed Services
- **PostgreSQL** - DigitalOcean Managed Database
- **Spaces** - S3-compatible object storage

### Current Limitations
- Single 1GB RAM droplet (resource constrained)
- Manual scaling (requires resizing droplet)
- Self-managed SSL certificates (Let's Encrypt)
- Manual deployment process via scripts
- System-level NGINX configuration
- Docker Swarm secrets management

---

## 🎯 Target Architecture (App Platform)

### App Platform Components
1. **Backend Service** (FastAPI)
   - Auto-scaled web service
   - HTTP routes handled by App Platform
   - Built-in SSL/TLS termination
   
2. **Frontend Service** (React/Vite)
   - Static site deployment
   - CDN-backed for global performance
   - Automatic build optimization
   
3. **Worker Service** (Background processor)
   - Long-running worker component
   - Auto-restart on failure
   - Shared environment with backend

### Managed Databases
- **PostgreSQL** - DigitalOcean Managed Database (existing or new)
- **Valkey** - DigitalOcean Managed Redis/Valkey
- **Spaces** - S3-compatible object storage (existing)

**Note:** Both databases are managed by DigitalOcean for high availability, automatic backups, and better performance.

### Benefits of App Platform
✅ **Automatic SSL** - Built-in SSL certificate management  
✅ **Auto-scaling** - Scales based on traffic  
✅ **Zero-downtime deployments** - Rolling updates  
✅ **Built-in monitoring** - Metrics and logs dashboard  
✅ **Simplified deployment** - Git-based or registry-based  
✅ **Environment management** - Built-in secrets management  
✅ **Health checks** - Automatic container health monitoring  
✅ **CDN integration** - Global static asset delivery  
✅ **Cost optimization** - Pay for what you use  

---

## 🚀 Deployment Strategy

### Using DigitalOcean Container Registry (DOCR)

We will use **DigitalOcean Container Registry** as the deployment method:

**Why DOCR over GitHub integration:**
- ✅ **Faster deployments** - Pre-built images, no build time on App Platform
- ✅ **Build control** - Build locally or on existing droplet with full control
- ✅ **Consistent images** - Same images used for testing and production
- ✅ **Leverages existing workflow** - Already using DOCR for droplet deployment
- ✅ **No GitHub coupling** - Can deploy from any source or CI/CD system

**Workflow:**
```
1. Build images locally/droplet → 
2. Tag with version → 
3. Push to DOCR → 
4. App Platform pulls from DOCR → 
5. Deploy
```

**Registry Format:**
```
registry.digitalocean.com/<your-registry-name>/lightclick-backend:latest
registry.digitalocean.com/<your-registry-name>/lightclick-frontend:latest
registry.digitalocean.com/<your-registry-name>/lightclick-worker:latest
```

---

## 🔄 Migration Strategy

### Phase 1: Planning & Preparation (Week 1)
**Goal**: Understand requirements and create migration artifacts

#### Tasks
- [x] Analyze current architecture
- [ ] Review App Platform pricing and resource needs
- [ ] Create App Platform specification file (`.do/app.yaml`)
- [ ] Document environment variable mapping
- [ ] Create migration scripts
- [ ] Setup Managed Valkey cluster
- [ ] Test Docker image compatibility
- [ ] **Setup DigitalOcean Container Registry (DOCR)**
- [ ] **Configure registry authentication**
- [ ] **Test image push to DOCR**

#### Deliverables
- `app-platform/.do/app.yaml` - App Platform spec
- `app-platform/README.md` - Deployment guide
- `app-platform/MIGRATION_PLAN.md` - This document
- `app-platform/environment-mapping.md` - Env var reference
- `app-platform/deploy.sh` - Deployment automation script

---

### Phase 2: Managed Database Setup (Week 1-2)
**Goal**: Setup or verify Managed PostgreSQL and create Managed Valkey

#### PostgreSQL Tasks
- [ ] Verify existing Managed PostgreSQL is ready
- [ ] OR create new Managed PostgreSQL (if not existing)
- [ ] Note connection string (host, port, database, user, password)
- [ ] Test connectivity from local machine
- [ ] Verify database size and plan (db-s-1vcpu-1gb recommended minimum)

### Valkey Tasks  
- [x] ~~Create Managed Valkey cluster~~ **Using existing shared instance**
- [x] Connection details obtained
- [x] Using database 1 for LightClick Studio (other service uses database 0)
- [x] Private connection configured for App Platform
- [x] TLS/SSL verified enabled

**Connection String (Private):**
```
rediss://default:<PASSWORD>@private-database-valkey-do-user-XXXXX-0.m.db.ondigitalocean.com:25061/1?ssl_cert_reqs=required
```

#### Cost Breakdown
- **Managed PostgreSQL (Basic, 1GB)**: $15/month (if new)
- **Managed Valkey (Basic, 1GB)**: $0/month (shared with other service)
- **Total for databases**: $15/month (PostgreSQL only)

**Cost Savings:** Sharing existing Valkey saves $15/month!

#### Testing Checklist
- [ ] PostgreSQL connection works
- [ ] Can run migrations successfully
- [ ] Valkey connection works (`redis-cli` test)
- [ ] Job queue operations work (LPUSH/RPOP)
- [ ] Rate limiting counters work (INCR/GET)
- [ ] Auth tokens work (SETEX/GET)
- [ ] Performance acceptable (latency < 5ms)

---

### Phase 3: App Platform Configuration (Week 2)
**Goal**: Create and test App Platform specification

#### App Platform Components

##### 1. Backend Service
```yaml
name: backend
type: service
dockerfile_path: backend/Dockerfile
http_port: 8000
instance_count: 1
instance_size_slug: basic-xs  # $5/month
routes:
  - path: /api
health_check:
  http_path: /health
  initial_delay_seconds: 30
```

##### 2. Frontend Service
```yaml
name: frontend
type: static-site
dockerfile_path: frontend/Dockerfile
routes:
  - path: /
output_dir: /usr/share/nginx/html
```

##### 3. Worker Service
```yaml
name: worker
type: worker
dockerfile_path: backend/Dockerfile
run_command: "python -m app.worker"
instance_count: 1
instance_size_slug: basic-xs  # $5/month
```

#### Environment Variables
All secrets managed via App Platform's encrypted environment variables:
- Database connection (PostgreSQL)
- Redis connection (Managed Redis)
- S3/Spaces credentials
- PayPal API keys
- Gemini API key
- SMTP credentials
- JWT secret
- OAuth credentials

#### Testing Strategy
- [ ] Create test App Platform app first
- [ ] Deploy with mock mode enabled
- [ ] Test all routes and functionality
- [ ] Verify worker processes jobs
- [ ] Load test with realistic traffic
- [ ] Test auto-scaling behavior

---

### Phase 4: Staging Deployment (Week 2-3)
**Goal**: Deploy to staging environment and validate

#### Steps
1. **Create Staging App**
   ```bash
   doctl apps create --spec app-platform/.do/app.yaml
   ```

2. **Configure Environment Variables**
   - Use App Platform console or `doctl` CLI
   - Set all required environment variables
   - Use staging database and Spaces bucket

3. **Deploy and Test**
   - Trigger initial build
   - Run database migrations
   - Test all features end-to-end
   - Monitor logs and metrics

4. **Performance Testing**
   - Load testing with realistic traffic
   - Monitor response times
   - Check memory usage and CPU
   - Verify auto-scaling triggers

#### Staging Validation Checklist
- [ ] All pages load correctly
- [ ] Authentication works (email/password + Google OAuth)
- [ ] Image upload and job creation works
- [ ] Worker processes jobs successfully
- [ ] Results stored in Spaces correctly
- [ ] Email notifications sent
- [ ] PayPal integration works (sandbox mode)
- [ ] Mobile responsive design intact
- [ ] Dark/light/auto theme switching works
- [ ] All API endpoints respond correctly

---

### Phase 5: Production Deployment (Week 3)
**Goal**: Deploy to production with zero downtime

#### Pre-Deployment Tasks
- [ ] Backup production database
- [ ] Export existing data from droplet
- [ ] Test rollback procedure
- [ ] Schedule maintenance window (if needed)
- [ ] Notify users of potential downtime
- [ ] Prepare rollback plan

#### Deployment Steps

##### Step 1: Create Production App Platform App
```bash
# Create app from spec
doctl apps create --spec app-platform/.do/app-production.yaml

# Note the app ID
export APP_ID=<app-id>
```

##### Step 2: Configure Production Environment Variables
```bash
# Use the setup script
./app-platform/configure-env.sh production
```

##### Step 3: Build and Push Images to DOCR
```bash
# Authenticate with DigitalOcean Container Registry
doctl registry login

# Build and push images (using existing droplet scripts)
./app-platform/build-and-push.sh

# Images will be pushed to:
# registry.digitalocean.com/<registry-name>/lightclick-backend:latest
# registry.digitalocean.com/<registry-name>/lightclick-frontend:latest
# registry.digitalocean.com/<registry-name>/lightclick-worker:latest
```

##### Step 4: Deploy from Registry
```bash
# App Platform will automatically pull from DOCR
doctl apps create-deployment $APP_ID

# Monitor deployment progress
doctl apps get-deployment $APP_ID <deployment-id>
```

##### Step 5: Run Database Migrations
```bash
# Via App Platform console or runtime
doctl apps exec $APP_ID backend -- alembic upgrade head
```

##### Step 6: DNS Cutover
```bash
# Update DNS to point to App Platform URL
# A record: your-app.ondigitalocean.app
# CNAME for custom domain: yourdomain.com
```

##### Step 7: Monitor & Validate
- Check all health endpoints
- Monitor error logs
- Verify job processing
- Test user flows
- Monitor performance metrics

#### Rollback Plan
If issues occur:
1. **DNS Rollback**: Point DNS back to droplet IP
2. **App Platform Rollback**: Revert to previous deployment
   ```bash
   doctl apps list-deployments $APP_ID
   doctl apps create-deployment $APP_ID --deployment-id <previous-id>
   ```
3. **Database Rollback**: Restore from backup if needed

---

### Phase 6: Post-Migration (Week 4)
**Goal**: Optimize and decommission old infrastructure

#### Optimization Tasks
- [ ] Review App Platform metrics
- [ ] Adjust instance sizes based on actual usage
- [ ] Configure auto-scaling rules
- [ ] Setup alerts and monitoring
- [ ] Optimize Docker images for faster builds
- [ ] Enable CDN caching for static assets
- [ ] Configure log retention and forwarding

#### Cleanup Tasks
- [ ] Keep droplet running for 1 week (safety)
- [ ] Verify no traffic to droplet
- [ ] Export logs from droplet
- [ ] Document learnings and issues
- [ ] Delete containerized Redis (if migrated to Managed)
- [ ] Destroy droplet
- [ ] Update documentation

#### Documentation Updates
- [ ] Update README.md with App Platform instructions
- [ ] Archive droplet deployment docs
- [ ] Create App Platform troubleshooting guide
- [ ] Document cost comparison
- [ ] Update WARP.md with new deployment commands

---

## 💰 Cost Comparison

### Current Droplet Setup
| Service | Cost | Notes |
|---------|------|-------|
| Droplet (1GB RAM) | $6/month | Resource constrained |
| Managed PostgreSQL | $15/month | Existing |
| Spaces (250GB) | $5/month | Existing |
| **Total** | **$26/month** | Limited scalability |

### App Platform Setup (Production-Grade)
| Service | Cost | Notes |
|---------|------|-------|
| Backend (basic-xs) | $5/month | Auto-scales to $10, $20 |
| Frontend (static site) | $3/month | CDN-backed |
| Worker (basic-xs) | $5/month | Auto-scales |
| **Managed Valkey (1GB)** | **$0/month** | **Shared with other service** |
| Managed PostgreSQL (1GB) | $15/month | Existing |
| Spaces (250GB) | $5/month | Existing |
| **Total** | **$33/month** | **+$7/month (+27%)** |

**Actual cost may vary based on:**
- Auto-scaling usage (additional instances)
- Bandwidth usage
- Build minutes (free tier: 400 minutes/month)

**Cost-Benefit Analysis:**
- ✅ **+85%** cost increase, BUT:
- ✅ Auto-scaling capability (handle traffic spikes)
- ✅ Zero-downtime deployments
- ✅ Built-in monitoring and logs
- ✅ No manual SSL management
- ✅ CDN for global performance
- ✅ Managed infrastructure (less ops work)
- ✅ **High availability databases** (PostgreSQL + Valkey)
- ✅ **Automatic backups** (daily snapshots)
- ✅ **Better performance** (sub-5ms latency for Valkey)

**Value Proposition:**
- Production-grade infrastructure from day 1
- No database management overhead
- Automatic failover and recovery
- Professional platform for serious business
- Peace of mind for critical job queue and rate limiting

---

## 🔧 Technical Considerations

### 1. Docker Image Compatibility
**Current**: Multi-stage builds with development and production targets  
**App Platform**: Supports Dockerfiles natively

**Action Items:**
- [ ] Test current Dockerfiles with App Platform
- [ ] Ensure health check endpoints work
- [ ] Verify PORT environment variable handling
- [ ] Test build times (optimize if needed)

### 2. Environment Variable Management
**Current**: Docker Swarm secrets (files in `/run/secrets/`)  
**App Platform**: Environment variables (encrypted)

**Migration Path:**
- Update `backend/app/core/config.py` to support both methods
- Provide fallback from `*_FILE` to direct env vars
- Already supported in current code!

### 3. Valkey Connection
**Current**: `redis://redis:6379/0` (container DNS)  
**App Platform**: Managed Valkey connection string with TLS

**Connection String Format:**
```
rediss://username:password@managed-valkey-host:25061/0?ssl_cert_reqs=required
```

**Action Items:**
- [ ] Update all references to use `REDIS_URL` env var
- [ ] Enable TLS/SSL connection (note the `rediss://` protocol)
- [ ] Test connection pooling with Managed Valkey
- [ ] Verify automatic backups are enabled
- [ ] Configure connection timeout and retry logic

### 4. Database Migrations
**Current**: Run via droplet SSH  
**App Platform**: Run via console or runtime exec

**Migration Commands:**
```bash
# App Platform method
doctl apps exec $APP_ID backend -- alembic upgrade head

# Or via App Platform console:
# Runtime → Select backend → Console → Run command
```

### 5. Worker Process
**Current**: Separate Docker service  
**App Platform**: Worker component type

**Considerations:**
- Worker runs independently of web service
- Shared environment variables with backend
- Auto-restart on failure
- Can scale independently

### 6. Static File Serving
**Current**: Nginx container serves React build  
**App Platform**: Static site component with CDN

**Benefits:**
- Global CDN distribution
- Better caching
- Faster load times worldwide
- Automatic compression

### 7. Custom Domain & SSL
**Current**: Let's Encrypt via certbot  
**App Platform**: Automatic SSL for custom domains

**Setup:**
1. Add custom domain in App Platform console
2. Update DNS records (provided by App Platform)
3. SSL certificate auto-provisioned
4. Auto-renewal handled by platform

---

## 🔍 Testing Strategy

### Pre-Migration Testing
1. **Load Testing**
   - Use staging environment
   - Simulate production traffic
   - Test auto-scaling behavior
   - Measure response times

2. **Feature Testing**
   - Complete E2E test suite (Playwright)
   - Test all API endpoints
   - Verify job processing
   - Test payment flows (PayPal sandbox)

3. **Integration Testing**
   - Database connectivity
   - Redis connectivity
   - S3/Spaces connectivity
   - Email sending (SMTP)
   - OAuth flows

### Post-Migration Testing
1. **Smoke Tests** (Immediately after deployment)
   - Health check endpoints
   - Homepage loads
   - Login/register works
   - Job creation works

2. **Full Regression** (Within 1 hour)
   - Run complete Playwright test suite
   - Manual testing of critical paths
   - Verify email notifications
   - Test payment flow

3. **Performance Monitoring** (First 24 hours)
   - Response times
   - Error rates
   - Job processing speed
   - Database query performance

---

## 📝 Migration Checklist

### Pre-Migration
- [ ] Review this migration plan
- [ ] Get stakeholder approval
- [ ] Create staging App Platform app
- [ ] Test staging deployment
- [ ] Setup Managed Redis (optional)
- [ ] Prepare rollback plan
- [ ] Schedule migration window
- [ ] Backup production database
- [ ] Notify users (if downtime expected)

### Migration Day
- [ ] Create production App Platform app
- [ ] Configure environment variables
- [ ] Deploy services
- [ ] Run database migrations
- [ ] Verify health checks pass
- [ ] Test critical functionality
- [ ] Update DNS records
- [ ] Monitor for errors
- [ ] Validate all features working
- [ ] Load test production

### Post-Migration
- [ ] Monitor for 24 hours
- [ ] Fix any issues discovered
- [ ] Optimize performance
- [ ] Configure alerts
- [ ] Update documentation
- [ ] Keep droplet for 1 week
- [ ] Decommission droplet
- [ ] Archive droplet configs

---

## 🚨 Risks & Mitigation

### Risk 1: Higher Costs Than Expected
**Mitigation:**
- Start with smallest instance sizes
- Monitor usage closely first month
- Set up billing alerts
- Use containerized Redis initially

### Risk 2: Performance Degradation
**Mitigation:**
- Thorough load testing before migration
- Keep droplet running for quick rollback
- Monitor response times closely
- Ready to scale up if needed

### Risk 3: Deployment Issues
**Mitigation:**
- Test thoroughly in staging first
- Deploy during low-traffic window
- Have rollback plan ready
- Keep droplet as backup

### Risk 4: Learning Curve
**Mitigation:**
- Read App Platform documentation
- Test in staging environment
- Document all procedures
- Practice rollback procedure

### Risk 5: Database Connection Issues
**Mitigation:**
- Test Managed Valkey connection thoroughly in staging
- Verify TLS/SSL certificates work correctly
- Configure proper connection pooling
- Have connection retry logic in place
- Monitor database connection metrics

---

## 📚 Resources & Documentation

### DigitalOcean Documentation
- [App Platform Overview](https://docs.digitalocean.com/products/app-platform/)
- [App Platform Spec Reference](https://docs.digitalocean.com/products/app-platform/reference/app-spec/)
- [Managed Redis](https://docs.digitalocean.com/products/databases/redis/)
- [App Platform Pricing](https://www.digitalocean.com/pricing/app-platform)

### Project Documentation
- `app-platform/README.md` - Deployment guide
- `app-platform/.do/app.yaml` - App Platform spec
- `app-platform/environment-mapping.md` - Environment variables
- `README.md` - Updated with App Platform info
- `WARP.md` - Updated deployment commands

### Tools Required
```bash
# DigitalOcean CLI
brew install doctl
doctl auth init

# Docker (for image building)
docker --version

# Git (for repository-based deployments)
git --version
```

---

## 🎯 Success Criteria

### Technical Success
✅ All services deployed and running  
✅ Health checks passing  
✅ Zero critical errors in logs  
✅ Response times within acceptable range  
✅ Job processing working correctly  
✅ Database migrations successful  
✅ SSL certificates active  
✅ Custom domain working  

### Business Success
✅ Zero downtime or < 5 minutes  
✅ No user complaints  
✅ All features functioning  
✅ Payment processing working  
✅ Email notifications sending  
✅ Cost within budget  

### Operational Success
✅ Deployment process documented  
✅ Monitoring and alerts configured  
✅ Team trained on App Platform  
✅ Rollback procedure tested  
✅ Old infrastructure decommissioned  

---

## 📞 Support & Escalation

### DigitalOcean Support
- **Ticket System**: https://cloud.digitalocean.com/support
- **Community**: https://www.digitalocean.com/community
- **Documentation**: https://docs.digitalocean.com

### Internal Team
- **Developer**: Rave
- **Migration Lead**: Rave
- **Rollback Authority**: Rave

### Emergency Contacts
- DigitalOcean Status: https://status.digitalocean.com
- Escalation: Open support ticket (if on paid support plan)

---

## 📅 Timeline Summary

| Phase | Duration | Key Activities |
|-------|----------|----------------|
| **Phase 1: Planning** | Week 1 | Create specs, scripts, test images |
| **Phase 2: Redis Setup** | Week 1-2 | Setup Managed Redis, test connectivity |
| **Phase 3: App Platform Config** | Week 2 | Create app spec, configure services |
| **Phase 4: Staging Deploy** | Week 2-3 | Deploy staging, test thoroughly |
| **Phase 5: Production Deploy** | Week 3 | Deploy production, DNS cutover |
| **Phase 6: Post-Migration** | Week 4 | Monitor, optimize, decommission |

**Total Estimated Time**: 3-4 weeks for complete migration

**Minimum Viable Migration**: 1 week (skip staging, accept higher risk)

---

## ✅ Next Steps

1. **Review this plan** - Get approval from stakeholders
2. **Create App Platform spec** - Build `.do/app.yaml`
3. **Setup Managed Redis** - Optional but recommended
4. **Test staging deployment** - Validate everything works
5. **Schedule production migration** - Pick low-traffic window
6. **Execute migration** - Follow this plan step-by-step
7. **Monitor and optimize** - Ensure success

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-13  
**Next Review**: Before Phase 1 starts
