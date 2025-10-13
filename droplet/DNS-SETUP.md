# DNS Setup Guide for lightclick.studio

## Overview

Your ProductSnap app is now configured to work with the **lightclick.studio** domain. The setup includes:

- **Root domain**: `lightclick.studio` (primary)
- **WWW subdomain**: `www.lightclick.studio` (redirects to root)
- **SSL certificates**: Automatic Let's Encrypt for both domains
- **Behavior**: All traffic (http/https, www/root) redirects to `https://lightclick.studio`

## Configuration Updated

The following files have been updated:

1. ✅ `droplet/config.env` - Domain set to `lightclick.studio`
2. ✅ `nginx/productsnap-system.conf` - Nginx configured for both domains
3. ✅ `droplet/prepare-droplet.sh` - Script updated to handle root domain + www
4. ✅ `droplet/.env.production.template` - Production URLs updated

## Step 1: Add Domain to DigitalOcean

If you haven't already added the domain to DigitalOcean:

```bash
# Add the domain to your DigitalOcean account
doctl compute domain create lightclick.studio
```

## Step 2: Update DNS Records

The `prepare-droplet.sh` script will automatically create DNS records, but you can verify or do it manually:

### Using the Script (Recommended)

The script will automatically:
- Create an A record for the root domain (`@`) pointing to your droplet IP
- Create an A record for `www` subdomain pointing to the same IP

### Manual Setup (via DigitalOcean UI)

Go to: **Networking** → **Domains** → **lightclick.studio** → **Add a record**

Create two A records:

1. **Root domain record**:
   - **Type**: A
   - **Hostname**: `@`
   - **Will direct to**: [Your Droplet IP]
   - **TTL**: 3600 seconds

2. **WWW subdomain record**:
   - **Type**: A
   - **Hostname**: `www`
   - **Will direct to**: [Your Droplet IP]
   - **TTL**: 3600 seconds

### Manual Setup (via doctl CLI)

```bash
# Get your droplet IP from droplet-info.env
source droplet/droplet-info.env

# Create root domain A record
doctl compute domain records create lightclick.studio \
  --record-type A \
  --record-name "@" \
  --record-data "$DROPLET_IP" \
  --record-ttl 3600

# Create www subdomain A record
doctl compute domain records create lightclick.studio \
  --record-type A \
  --record-name "www" \
  --record-data "$DROPLET_IP" \
  --record-ttl 3600
```

## Step 3: Run the Preparation Script

Now run the preparation script to set up the droplet with HTTPS:

```bash
./droplet/prepare-droplet.sh
```

This will:
1. ✅ Create/update DNS records for both `lightclick.studio` and `www.lightclick.studio`
2. ✅ Configure the droplet (firewall, nginx, docker, etc.)
3. ✅ Obtain Let's Encrypt SSL certificates for both domains
4. ✅ Configure nginx with the production configuration
5. ✅ Add droplet IP to database firewall (if DB_ID is set)

## Step 4: Verify DNS Propagation

DNS changes can take a few minutes to propagate. Check the status:

```bash
# Check if DNS has propagated
dig lightclick.studio +short
dig www.lightclick.studio +short

# Both should return your droplet IP
```

Or use online tools:
- https://www.whatsmydns.net/#A/lightclick.studio
- https://www.whatsmydns.net/#A/www.lightclick.studio

## Step 5: Deploy Your Application

Once DNS is set up and propagated:

```bash
# Build your Docker images
./droplet/build.sh

# Push to DigitalOcean registry
./droplet/push.sh

# Deploy to droplet
./droplet/deploy.sh
```

## Verification

After deployment, test all URLs:

1. **HTTP Root**: http://lightclick.studio → should redirect to https://lightclick.studio
2. **HTTP WWW**: http://www.lightclick.studio → should redirect to https://lightclick.studio
3. **HTTPS WWW**: https://www.lightclick.studio → should redirect to https://lightclick.studio
4. **HTTPS Root**: https://lightclick.studio → should load your app ✓

Check SSL certificate:

```bash
# Verify SSL certificate
echo | openssl s_client -servername lightclick.studio -connect lightclick.studio:443 2>/dev/null | openssl x509 -noout -dates

# Should show Let's Encrypt certificate with both domains
```

## Troubleshooting

### DNS Not Resolving

```bash
# Check DigitalOcean DNS records
doctl compute domain records list lightclick.studio

# You should see:
# ID       Type    Name    Data              TTL
# xxxxx    A       @       [your-ip]         3600
# xxxxx    A       www     [your-ip]         3600
```

### SSL Certificate Issues

```bash
# SSH into droplet and check certbot
ssh root@[droplet-ip]
certbot certificates

# Should show certificate for lightclick.studio with www.lightclick.studio as SAN
```

### Nginx Configuration Issues

```bash
# SSH into droplet and test nginx
ssh root@[droplet-ip]
nginx -t

# Check nginx logs
tail -f /var/log/nginx/productsnap_error.log
```

## Configuration Files Reference

### `droplet/config.env`
```bash
DOMAIN=lightclick.studio
SUBDOMAIN=@  # @ means root domain
LETSENCRYPT_EMAIL=rave@lightclick.studio
```

### Nginx Behavior
- All HTTP traffic → redirects to HTTPS
- www.lightclick.studio → redirects to lightclick.studio
- lightclick.studio → serves the app

## Notes

- DNS propagation typically takes 5-30 minutes but can take up to 48 hours
- Let's Encrypt certificates auto-renew every 90 days
- The setup supports both domains but canonicalizes to the root domain
- SSL certificates are obtained for both domains in a single certificate (SAN)
