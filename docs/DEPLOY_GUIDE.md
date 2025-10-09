# ProductSnap Deployment Guide

## Quick Start - Deploy Without SSL (HTTP only)

If you want to deploy immediately without a domain/SSL:

```bash
# Deploy the application
./deploy.sh
```

That's it! The application will be available at:
- Frontend: http://159.89.111.179
- API Docs: http://159.89.111.179/api/docs
- Health Check: http://159.89.111.179/health

## Full Deployment with Domain & SSL

### Step 1: Configure DNS

Point your domain to the server:
```
A Record: yourdomain.com → 159.89.111.179
```

Wait for DNS propagation (can take 5-60 minutes). Verify with:
```bash
dig +short yourdomain.com
```

### Step 2: Deploy Application

```bash
./deploy.sh
```

### Step 3: Set Up SSL Certificate

```bash
DOMAIN=yourdomain.com EMAIL=you@email.com ./setup-ssl.sh
```

Your application will now be available at:
- https://yourdomain.com
- https://yourdomain.com/api/docs

## Environment Configuration

Before deploying, ensure your `.env` file is properly configured with:

**Required:**
- `JWT_SECRET` - Strong random string (32+ characters)
- `POSTGRES_PASSWORD` - Database password
- `NANO_BANANA_API_KEY` - Your Nano Banana API key
- `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` - S3/Spaces credentials
- `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET` - PayPal credentials
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` - Email configuration

**Optional:**
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` - For Google OAuth
- `PAYPAL_MODE` - Set to `sandbox` for testing or `live` for production

## Deployment Scripts

### `./deploy.sh`
- Deploys application code to the server
- Builds Docker images
- Starts all containers
- Runs database migrations
- Performs health checks

### `./setup-ssl.sh`
- Generates Let's Encrypt SSL certificate
- Updates NGINX to use HTTPS
- Sets up automatic certificate renewal
- **Prerequisites**: Domain DNS must be configured first

### `./setup-server.sh`
- Initial server setup (already completed)
- Installs Docker, configures firewall, creates app user

## Monitoring & Management

### View Logs
```bash
ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose logs -f'
```

### Check Status
```bash
ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose ps'
```

### Restart Application
```bash
ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose restart'
```

### Stop Application
```bash
ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose down'
```

### View Database Logs
```bash
ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose logs postgres'
```

### Run Database Migrations Manually
```bash
ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose exec backend alembic upgrade head'
```

### Generate New Migration
```bash
ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose exec backend alembic revision --autogenerate -m "description"'
```

## Troubleshooting

### Application won't start
1. Check logs: `ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose logs'`
2. Verify `.env` is configured: `ssh productsnap@159.89.111.179 'cd /home/productsnap/app && ls -la .env'`
3. Check container status: `ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose ps'`

### Database connection errors
1. Check PostgreSQL is running: `ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose ps postgres'`
2. Verify `DATABASE_URL` in `.env`
3. Check PostgreSQL logs: `ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose logs postgres'`

### SSL certificate fails to generate
1. Verify DNS is pointing to server: `dig +short yourdomain.com`
2. Ensure port 80 is accessible: `curl -I http://159.89.111.179`
3. Check certbot logs: `ssh root@159.89.111.179 'tail -100 /var/log/letsencrypt/letsencrypt.log'`

### Frontend shows 404 or blank page
1. Check frontend container: `ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose logs frontend'`
2. Verify build succeeded: `ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose exec frontend ls -la /usr/share/nginx/html'`
3. Check NGINX config: `ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose exec nginx nginx -t'`

### API returns 502 Bad Gateway
1. Check backend is running: `ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose ps backend'`
2. View backend logs: `ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose logs backend'`
3. Test health endpoint: `curl http://159.89.111.179/health`

## Server Resource Usage

### Check Memory Usage
```bash
ssh root@159.89.111.179 'free -h'
```

### Check Disk Usage
```bash
ssh root@159.89.111.179 'df -h'
```

### Check Docker Resource Usage
```bash
ssh productsnap@159.89.111.179 'docker stats --no-stream'
```

## Scaling Up

If the 1GB droplet is insufficient:

```bash
# Resize droplet to 2GB RAM
doctl compute droplet-action resize 522319316 --size s-1vcpu-2gb --wait

# Recommended sizes:
# - Light: s-1vcpu-2gb ($12/month) - 2GB RAM, 1 vCPU
# - Production: s-2vcpu-4gb ($24/month) - 4GB RAM, 2 vCPUs
# - Heavy: s-4vcpu-8gb ($48/month) - 8GB RAM, 4 vCPUs
```

## Backup & Restore

### Backup Database
```bash
ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose exec -T postgres pg_dump -U productsnap productsnap' > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
cat backup.sql | ssh productsnap@159.89.111.179 'cd /home/productsnap/app && docker compose exec -T postgres psql -U productsnap productsnap'
```

### Backup Volumes
```bash
ssh root@159.89.111.179 'tar czf /tmp/docker-volumes.tar.gz /var/lib/docker/volumes/'
scp root@159.89.111.179:/tmp/docker-volumes.tar.gz ./backup-volumes-$(date +%Y%m%d).tar.gz
```

## Update Application

```bash
# Pull latest code
git pull

# Redeploy
./deploy.sh
```

## Environment Variables

To update environment variables:

```bash
# SSH into server
ssh productsnap@159.89.111.179

# Edit .env
cd /home/productsnap/app
nano .env

# Restart services to apply changes
docker compose restart
```

## Security Best Practices

1. **Change default passwords** - Update `POSTGRES_PASSWORD` and `JWT_SECRET`
2. **Use strong secrets** - JWT_SECRET should be 32+ random characters
3. **Enable HTTPS** - Always use SSL in production
4. **Regular updates** - Keep server and Docker images updated
5. **Monitor logs** - Check for suspicious activity regularly
6. **Backup regularly** - Automate database backups

## Support

For more information:
- See `DEPLOYMENT_INFO.md` for server details
- See `README.md` for application documentation
- See `WARP.md` for development guidance
