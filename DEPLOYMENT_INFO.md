# ProductSnap Deployment Information

## Server Details

**Created:** October 3, 2025  
**Provider:** DigitalOcean  
**Region:** Frankfurt (fra1)  
**Droplet ID:** 522319316

### Access Information

- **IPv4 Address:** `159.89.111.179`
- **IPv6 Address:** `2a03:b0c0:3:f0:0:1:62d9:f000`
- **Hostname:** `productsnap-app`

### SSH Access

```bash
# Root access
ssh root@159.89.111.179

# Application user access
ssh productsnap@159.89.111.179
```

## Server Specifications

- **OS:** Ubuntu 22.04.5 LTS
- **RAM:** 1GB
- **vCPUs:** 1
- **Disk:** 25GB SSD
- **Monthly Cost:** $6.00

## Installed Software

- **Docker:** 28.5.0
- **Docker Compose:** v2.39.4
- **Git:** 2.34.1
- **Certbot:** (ready for Let's Encrypt SSL)

## Firewall Configuration

**UFW Status:** Active

| Port | Protocol | Purpose | Status |
|------|----------|---------|--------|
| 22   | TCP      | SSH     | ✅ ALLOW |
| 80   | TCP      | HTTP    | ✅ ALLOW |
| 443  | TCP      | HTTPS   | ✅ ALLOW |

**Default Policies:**
- Incoming: DENY
- Outgoing: ALLOW

## Application Setup

- **Application User:** `productsnap` (uid: 1000)
- **Application Directory:** `/home/productsnap/app`
- **Docker Group:** User added to `docker` group
- **Permissions:** Full access to app directory

## Security Features

✅ System fully updated (187 packages upgraded)  
✅ Firewall enabled and configured  
✅ Automatic security updates enabled  
✅ SSH hardened (key-based authentication)  
✅ Non-root application user created  
✅ Docker daemon configured for production  

## System Optimizations Applied

```bash
# Network tuning
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
vm.swappiness = 10
```

## Docker Configuration

**Daemon Settings:**
- Log driver: json-file
- Max log size: 10m
- Max log files: 3
- Live restore: enabled

## Next Steps

### 1. Deploy Application

Copy application files to the server:
```bash
scp -r /Users/ravenir/dev/apps/product-snap/* productsnap@159.89.111.179:/home/productsnap/app/
```

### 2. Configure Environment

```bash
ssh productsnap@159.89.111.179
cd /home/productsnap/app
cp .env.example .env
nano .env  # Edit with production values
```

### 3. Set Up Domain (Optional)

Point your domain's DNS to:
- **A Record:** `159.89.111.179`
- **AAAA Record:** `2a03:b0c0:3:f0:0:1:62d9:f000`

### 4. Generate SSL Certificates

```bash
# Once domain is pointing to server
ssh root@159.89.111.179
certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com
```

### 5. Build and Deploy

```bash
ssh productsnap@159.89.111.179
cd /home/productsnap/app
# Will need to create docker-compose.yml first
docker compose up -d
```

## Monitoring Commands

```bash
# Check server resources
ssh root@159.89.111.179 'free -h && df -h'

# Check Docker status
ssh productsnap@159.89.111.179 'docker ps -a'

# View Docker logs
ssh productsnap@159.89.111.179 'docker compose logs -f'

# Check firewall status
ssh root@159.89.111.179 'ufw status verbose'
```

## Backup Strategy

### Database Backup
```bash
# Manual backup
ssh productsnap@159.89.111.179
docker compose exec postgres pg_dump -U productsnap productsnap > backup_$(date +%Y%m%d).sql
```

### Volume Backup
```bash
# Backup Docker volumes
ssh root@159.89.111.179 'tar -czf /root/volumes-backup-$(date +%Y%m%d).tar.gz /var/lib/docker/volumes/'
```

## Resize Droplet (If Needed)

If 1GB RAM is insufficient:

```bash
# Via doctl
doctl compute droplet-action resize 522319316 --size s-2vcpu-2gb --wait

# Or via DigitalOcean web console:
# Dashboard → Droplets → productsnap-app → Resize
```

Recommended sizes:
- **Light usage:** s-1vcpu-2gb ($12/month)
- **Production:** s-2vcpu-4gb ($24/month)
- **Heavy load:** s-4vcpu-8gb ($48/month)

## Destroy Droplet

**⚠️ Warning: This will permanently delete the server and all data!**

```bash
# Via doctl
doctl compute droplet delete 522319316

# Or via web console:
# Dashboard → Droplets → productsnap-app → Destroy
```

## Troubleshooting

### Can't SSH to server
```bash
# Check droplet status
doctl compute droplet get 522319316

# Check firewall rules
doctl compute firewall list
```

### Out of disk space
```bash
# Clean up Docker
ssh root@159.89.111.179 'docker system prune -af --volumes'
```

### Server unreachable
```bash
# Access via DigitalOcean console
# Dashboard → Droplets → productsnap-app → Console
```

## Support

- **DigitalOcean Status:** https://status.digitalocean.com/
- **Documentation:** https://docs.digitalocean.com/
- **Support:** https://cloud.digitalocean.com/support

---

**Last Updated:** October 3, 2025  
**Droplet Status:** ✅ Active and Ready
