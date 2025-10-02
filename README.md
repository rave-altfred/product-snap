# ProductSnap - AI Product Photography Platform

A production-ready full-stack web application that transforms product photos into professional shots using Nano Banana AI image generation.

## Features

### 🎨 Three Generation Modes
- **Studio White**: Precise product cutouts on pure white backgrounds
- **Model Try-On**: Products placed naturally on human models
- **Lifestyle Scene**: Products in realistic, photorealistic environments

### 🚀 Core Capabilities
- Camera capture and file upload support
- Email/password and Google OAuth authentication
- PayPal subscription management (Free, Personal, Pro tiers)
- Rate limiting and usage quotas per plan
- Real-time job progress tracking
- S3-compatible storage (DigitalOcean Spaces)
- Background job processing with Redis queue
- Email notifications
- Responsive design (desktop, tablet, mobile)

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Storage**: S3-compatible (DigitalOcean Spaces)
- **Auth**: JWT + Google OAuth + Argon2 password hashing
- **Payments**: PayPal Subscriptions
- **Email**: SMTP (SendGrid, etc.)
- **Image Processing**: Pillow, Nano Banana API

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **Data Fetching**: React Query (TanStack Query)
- **Routing**: React Router v6
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: NGINX
- **SSL**: Let's Encrypt (auto-renewal)
- **Database Migrations**: Alembic
- **Logging**: Structured JSON logs with request IDs

## Project Structure

```
product-snap/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, database, logging
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routers/        # FastAPI route handlers
│   │   ├── services/       # Business logic (auth, storage, etc.)
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── main.py         # FastAPI application
│   │   └── worker.py       # Background job processor
│   ├── alembic/            # Database migrations
│   ├── tests/              # Unit and integration tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable React components
│   │   ├── pages/          # Page components
│   │   ├── lib/            # API client, utilities
│   │   ├── store/          # Zustand stores
│   │   ├── types/          # TypeScript types
│   │   └── main.tsx        # Entry point
│   ├── Dockerfile
│   └── package.json
├── nginx/
│   ├── nginx.conf          # Main NGINX config
│   ├── conf.d/             # Server configurations
│   └── ssl/                # SSL certificates
├── deployment/             # Deployment scripts
├── docker-compose.yml
├── .env.example            # Environment variables template
└── README.md
```

## Local Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### 1. Clone and Configure

```bash
git clone <repository-url>
cd product-snap

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# REQUIRED: Set at minimum:
# - JWT_SECRET
# - POSTGRES_PASSWORD
# - NANO_BANANA_API_KEY
# - S3 credentials
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f worker
```

### 3. Run Migrations

```bash
# Create initial migration
docker-compose exec backend alembic revision --autogenerate -m "Initial schema"

# Apply migrations
docker-compose exec backend alembic upgrade head
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

## Environment Variables

See `.env.example` for all required variables. Key variables:

### Required
- `JWT_SECRET`: Secret key for JWT tokens (min 32 chars)
- `POSTGRES_PASSWORD`: Database password
- `NANO_BANANA_API_KEY`: Nano Banana API key
- `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`: S3 storage
- `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`: PayPal credentials
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`: Email configuration

### Optional
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: For Google OAuth
- `PAYPAL_MODE`: `sandbox` (dev) or `live` (production)
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`

## Production Deployment (DigitalOcean)

### 1. Create Droplet

```bash
# Create a Droplet with:
# - Ubuntu 22.04 LTS
# - 2GB+ RAM recommended
# - IPv6 enabled
# - SSH key configured
```

### 2. Initial Server Setup

```bash
# SSH into droplet
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Create app user
adduser productsnap
usermod -aG docker productsnap
```

### 3. Deploy Application

```bash
# Switch to app user
su - productsnap

# Clone repository
git clone <repository-url>
cd product-snap

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with production values

# Set production URLs
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com
```

### 4. SSL Certificate Setup

```bash
# Install certbot
apt install certbot

# Get certificate
certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Update nginx/conf.d/default.conf with your domain
# Update certificate paths in NGINX config
```

### 5. Start Production Services

```bash
# Build and start
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Check status
docker-compose ps
docker-compose logs
```

### 6. Configure Firewall

```bash
# Allow HTTP, HTTPS, SSH
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

## PayPal Configuration

1. Create PayPal App at https://developer.paypal.com/
2. Create subscription plans for Personal and Pro tiers
3. Add plan IDs to `.env`:
   ```
   PAYPAL_PLAN_ID_PERSONAL=P-xxx
   PAYPAL_PLAN_ID_PRO=P-yyy
   ```
4. Set up webhook endpoint: `https://api.yourdomain.com/api/webhooks/paypal`

## DigitalOcean Spaces Setup

1. Create a Space in DigitalOcean
2. Generate API keys (Spaces access keys)
3. Configure CORS if needed
4. Add to `.env`:
   ```
   S3_ENDPOINT=https://nyc3.digitaloceanspaces.com
   S3_BUCKET=productsnap-storage
   S3_ACCESS_KEY=your-key
   S3_SECRET_KEY=your-secret
   ```

## Monitoring and Maintenance

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f worker
```

### Database Backup
```bash
# Backup
docker-compose exec postgres pg_dump -U productsnap productsnap > backup.sql

# Restore
docker-compose exec -T postgres psql -U productsnap productsnap < backup.sql
```

### Update Application
```bash
git pull origin main
docker-compose build
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

## API Documentation

- Interactive API docs: `/api/docs` (Swagger UI)
- ReDoc documentation: `/api/redoc`
- OpenAPI schema: `/api/openapi.json`

## Testing

```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests (if implemented)
cd frontend
npm test
```

## Rate Limits

- **Free**: 5 jobs/day, 1 concurrent job, watermarked outputs
- **Personal**: 100 jobs/month, 3 concurrent jobs, no watermark
- **Pro**: 1000 jobs/month, 5 concurrent jobs, priority queue, custom prompts

## Troubleshooting

### Backend won't start
- Check `.env` configuration
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check logs: `docker-compose logs backend`

### Frontend can't reach API
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in backend
- Check NGINX proxy configuration

### Jobs not processing
- Check worker is running: `docker-compose ps worker`
- Check Redis connection: `docker-compose logs redis`
- View worker logs: `docker-compose logs worker`

### SSL certificate issues
- Verify domain DNS points to droplet IP
- Check certificate paths in NGINX config
- Renew manually: `certbot renew`

## Security Considerations

- Change all default passwords and secrets
- Use strong JWT secret (32+ characters)
- Enable firewall (ufw)
- Regular security updates: `apt update && apt upgrade`
- Keep Docker images updated
- Monitor logs for suspicious activity
- Set up automated backups
- Use environment variables for all secrets

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Email: support@yourdomain.com
