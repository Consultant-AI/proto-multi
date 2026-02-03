# CloudBot Control Plane (Python/FastAPI)

Control plane service for the CloudBot cloud platform. Manages user authentication, AWS EC2 instance provisioning, and WebSocket proxies for VNC and CloudBot connections.

## Features

- User authentication with JWT tokens
- AWS EC2 instance provisioning and management (boto3)
- WebSocket proxy for VNC desktop streaming
- WebSocket proxy for CloudBot agent communication
- Encrypted API key storage
- PostgreSQL database for state management
- Redis for session caching
- Automatic API documentation (OpenAPI/Swagger)

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **ASGI Server**: Uvicorn
- **Database**: PostgreSQL 16+ (asyncpg)
- **Cache**: Redis 7+
- **Cloud**: AWS boto3
- **Auth**: python-jose (JWT), passlib (bcrypt)

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 16+
- Redis 7+
- AWS account with EC2 permissions (for production)

## Development Setup

1. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Copy environment template**:
```bash
cp .env.example .env
```

4. **Update `.env` with your configuration**:
   - Database connection strings
   - JWT secrets (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
   - Encryption key (generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)
   - AWS credentials (if using AWS)
   - Set `LOCAL_DEV_MODE=true` for local development without AWS

5. **Run database migrations**:
```bash
alembic upgrade head
```

6. **Start development server**:
```bash
uvicorn app.main:app --reload --port 8000
```

The server will start on http://localhost:8000

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Scripts

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Run with custom log level
uvicorn app.main:app --reload --log-level debug

# Database migrations
alembic upgrade head       # Apply migrations
alembic downgrade -1       # Rollback last migration
alembic revision -m "msg"  # Create new migration

# Code formatting
black app/
ruff check app/

# Tests
pytest
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login and get JWT tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

### Instances
- `GET /api/instances` - List user's instances
- `POST /api/instances` - Create new instance
- `GET /api/instances/{id}` - Get instance details
- `DELETE /api/instances/{id}` - Terminate instance
- `POST /api/instances/{id}/stop` - Stop instance
- `POST /api/instances/{id}/start` - Start stopped instance

### API Keys
- `POST /api/user/api-keys` - Store encrypted API keys
- `GET /api/user/api-keys` - List configured providers
- `PUT /api/user/api-keys/{provider}` - Update API key
- `DELETE /api/user/api-keys/{provider}` - Remove API key

### WebSocket Endpoints
- `WS /api/instances/{id}/vnc` - VNC desktop streaming
- `WS /api/instances/{id}/cloudbot` - CloudBot agent communication

## Project Structure

```
control-plane/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration management
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py          # Database connection
│   │   └── migrations/            # Alembic migrations
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py                 # JWT utilities
│   │   └── middleware.py          # Auth middleware
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py                # Auth routes
│   │   ├── instances.py           # Instance routes
│   │   └── api_keys.py            # API key routes
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── ec2.py                 # AWS EC2 management
│   │   ├── user_data.sh           # EC2 bootstrap script
│   │   └── config_templates/      # CloudBot configs
│   ├── proxy/
│   │   ├── __init__.py
│   │   ├── vnc.py                 # VNC WebSocket proxy
│   │   └── cloudbot.py            # CloudBot WebSocket proxy
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── instance_ownership.py  # Instance access control
│   └── utils/
│       ├── __init__.py
│       └── encryption.py          # API key encryption
├── requirements.txt
├── pyproject.toml
├── alembic.ini                    # Alembic config
└── README.md
```

## Environment Variables

See `.env.example` for all available configuration options.

### Required in Production:
- `JWT_SECRET_KEY` - JWT signing secret
- `JWT_REFRESH_SECRET_KEY` - Refresh token secret
- `ENCRYPTION_KEY` - API key encryption key
- `DATABASE_URL` - PostgreSQL connection string
- `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY` - AWS credentials

## Security

- All passwords hashed with bcrypt
- API keys encrypted with Fernet (symmetric encryption)
- JWT tokens for authentication
- Rate limiting on auth endpoints (TODO)
- Instance ownership verification
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration

## Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t cloudbot-control-plane .
docker run -p 8000:8000 --env-file .env cloudbot-control-plane
```

## Deploying OpenClaw Updates

When you make changes to the `cloudbot/` code, new EC2 instances need the updated tarball.

### Quick Deploy

```bash
# From repo root - builds and uploads to S3
./control-plane/scripts/deploy-openclaw.sh
```

### Manual Deploy

```bash
# 1. Build the cloudbot package
cd cloudbot
npm run build
npm pack

# 2. Upload to S3
aws s3 cp openclaw-*.tgz s3://cloudbot-moltbot-assets/openclaw.tgz

# 3. Create a new instance from the dashboard to use the updated code
```

### How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    cloudbot/    │     │       S3        │     │  EC2 Instance   │
│                 │     │                 │     │                 │
│  npm run build  │────▶│  openclaw.tgz   │────▶│  user_data.sh   │
│  npm pack       │     │                 │     │  downloads &    │
│                 │     │                 │     │  installs       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

When an EC2 instance launches:
1. `user_data.sh` runs on boot
2. Downloads `openclaw.tgz` from `s3://cloudbot-moltbot-assets/`
3. Installs OpenClaw as a systemd service
4. API keys are set in `/etc/openclaw.env`

**Note:** Existing instances won't get updates. You must create new instances after deploying.

### Debugging Instance Issues

```bash
# SSH into the instance
ssh -i ~/.ssh/cloudbot.pem ubuntu@<instance-ip>

# Check OpenClaw service status
sudo systemctl status openclaw

# View OpenClaw logs
sudo journalctl -u openclaw -f

# Check API keys are set correctly
sudo cat /etc/openclaw.env
```

---

## DevOps & Deployment

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLOUDBOT PLATFORM                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────┐                     │
│  │    RAILWAY       │         │    AWS EC2       │                     │
│  │                  │         │                  │                     │
│  │  ┌────────────┐  │         │  ┌────────────┐  │                     │
│  │  │ Control    │  │ WebSocket│  │ CloudBot   │  │                     │
│  │  │ Plane      │◄─┼─Proxy───┼──┤ Instance   │  │                     │
│  │  │ (FastAPI)  │  │         │  │ (Ubuntu)   │  │                     │
│  │  └─────┬──────┘  │         │  └────────────┘  │                     │
│  │        │         │         │       │          │                     │
│  │  ┌─────┴──────┐  │         │  ┌────┴───────┐  │                     │
│  │  │ PostgreSQL │  │         │  │ OpenClaw   │  │                     │
│  │  │ (Railway)  │  │         │  │ Gateway    │  │                     │
│  │  └────────────┘  │         │  └────────────┘  │                     │
│  │                  │         │       │          │                     │
│  │  ┌────────────┐  │         │  ┌────┴───────┐  │                     │
│  │  │ Redis      │  │         │  │ VNC + XFCE │  │                     │
│  │  │ (Railway)  │  │         │  │ Desktop    │  │                     │
│  │  └────────────┘  │         │  └────────────┘  │                     │
│  └──────────────────┘         └──────────────────┘                     │
│           │                            ▲                                │
│           │                            │                                │
│  ┌────────┴─────────┐        ┌────────┴────────┐                       │
│  │    AWS S3        │        │  User Browser   │                       │
│  │                  │        │                 │                       │
│  │ • openclaw.tgz   │        │ • React Frontend│                       │
│  │ • wallpaper.jpg  │        │ • VNC Client    │                       │
│  │                  │        │ • Chat UI       │                       │
│  └──────────────────┘        └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Hosting Locations

| Component | Service | URL/Location |
|-----------|---------|--------------|
| Control Plane (API + Frontend) | Railway | https://cloudbot-ai.com |
| PostgreSQL Database | Railway (Plugin) | Auto-provisioned |
| Redis Cache | Railway (Plugin) | Auto-provisioned |
| EC2 Instances | AWS eu-central-1 | Dynamic IPs |
| OpenClaw Tarball | AWS S3 | s3://cloudbot-moltbot-assets/openclaw.tgz |
| Wallpaper Asset | Railway (static) | https://cloudbot-ai.com/assets/wallpaper.jpg |

### Railway Deployment

The control plane is deployed on Railway with automatic deployments from the main branch.

#### Initial Setup

1. **Create Railway Project**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Initialize project (from control-plane directory)
   cd control-plane
   railway init
   ```

2. **Add Services**:
   - Add PostgreSQL plugin
   - Add Redis plugin
   - Railway auto-provisions these

3. **Configure Environment Variables** in Railway dashboard:
   ```
   # Required
   ENVIRONMENT=production
   JWT_SECRET_KEY=<generate secure key>
   JWT_REFRESH_SECRET_KEY=<generate secure key>
   ENCRYPTION_KEY=<generate Fernet key>

   # AWS (for EC2 provisioning)
   AWS_ACCESS_KEY_ID=<your key>
   AWS_SECRET_ACCESS_KEY=<your secret>
   AWS_REGION=eu-central-1
   EC2_SECURITY_GROUP_ID=sg-xxxxx
   EC2_SUBNET_ID=subnet-xxxxx
   EC2_KEY_PAIR_NAME=cloudbot-key
   UBUNTU_AMI_ID=ami-xxxxx

   # Public URL for EC2 instances to download assets
   CONTROL_PLANE_URL=https://cloudbot-ai.com

   # CORS
   CORS_ORIGINS=https://cloudbot-ai.com

   # Stripe (optional)
   STRIPE_SECRET_KEY=sk_live_xxx
   STRIPE_PUBLISHABLE_KEY=pk_live_xxx
   ```

4. **Deploy**:
   ```bash
   # Push to main branch triggers auto-deploy
   git push origin main

   # Or manual deploy
   railway up
   ```

#### Updating the Control Plane

```bash
# 1. Make your changes
git add .
git commit -m "Your changes"

# 2. Push to main - Railway auto-deploys
git push origin main

# 3. Monitor deployment
railway logs
```

Railway automatically:
- Builds the Docker image (frontend + backend)
- Runs database migrations
- Zero-downtime deploys

### EC2 Instance Deployment

When a user creates a new instance from the dashboard:

1. **Control Plane** calls AWS EC2 API via boto3
2. **EC2 launches** with Ubuntu AMI
3. **user_data.sh** runs on first boot:
   - Installs XFCE desktop, VNC, Chrome, VS Code, LibreOffice
   - Downloads OpenClaw from `CONTROL_PLANE_URL/assets/openclaw.tgz`
   - Downloads wallpaper from `CONTROL_PLANE_URL/assets/wallpaper.jpg`
   - Configures OpenClaw with user's API keys
   - Starts all services (VNC, OpenClaw gateway)

#### Instance Bootstrap Flow

```
EC2 Launch
    │
    ▼
user_data.sh starts
    │
    ├── Install packages (XFCE, Chrome, VS Code, etc.)
    │
    ├── Download openclaw.tgz from $CONTROL_PLANE_URL/assets/
    │
    ├── npm install -g openclaw.tgz
    │
    ├── Create /etc/openclaw.env with API keys
    │
    ├── Create workspace at /root/cloudbot-workspace/
    │
    ├── Start services:
    │   ├── xvfb (virtual display :99)
    │   ├── x11vnc (VNC server on :5900)
    │   ├── xfce-session (desktop)
    │   └── openclaw (gateway on :18789)
    │
    └── Debug server on :8080
```

#### Key Environment Variables Injected

The control plane injects these into user_data.sh:
- `CONTROL_PLANE_URL` - For downloading assets
- `MOLTBOT_TARBALL_URL` - Fallback URL for OpenClaw
- `ANTHROPIC_API_KEY` - User's API key (encrypted in DB, decrypted at launch)
- Other API keys as configured by user

### Updating OpenClaw

When you make changes to the `cloudbot/` code:

```bash
# From repo root
./control-plane/scripts/deploy-openclaw.sh
```

This script:
1. Builds the cloudbot package (`npm run build`)
2. Creates tarball (`npm pack`)
3. Uploads to S3 (`aws s3 cp openclaw.tgz s3://cloudbot-moltbot-assets/`)

**Note**: Existing instances keep the old version. Only **new instances** get updates.

### Manual OpenClaw Deploy

```bash
cd cloudbot
npm run build
npm pack

# Upload to S3
aws s3 cp openclaw-*.tgz s3://cloudbot-moltbot-assets/openclaw.tgz

# The tarball is also served from Railway
# Copy to control-plane for Docker build
cp openclaw-*.tgz ../control-plane/openclaw.tgz
```

### Debugging EC2 Instances

Each instance runs a debug HTTP server on port 8080:

```bash
# Get instance IP from dashboard, then:

# View bootstrap log
curl http://<instance-ip>:8080/log

# Check OpenClaw status
curl http://<instance-ip>:8080/debug

# Test API key
curl http://<instance-ip>:8080/testapi

# Check npm installation
curl http://<instance-ip>:8080/check
```

#### SSH Access

```bash
ssh -i ~/.ssh/cloudbot.pem ubuntu@<instance-ip>

# Check services
sudo systemctl status openclaw
sudo systemctl status x11vnc
sudo systemctl status xfce-session

# View logs
sudo journalctl -u openclaw -f
cat /var/log/user-data.log

# Restart OpenClaw
sudo systemctl restart openclaw
```

### Asset Files

The control plane serves static assets that EC2 instances download:

| Asset | Path | Source |
|-------|------|--------|
| OpenClaw | `/assets/openclaw.tgz` | `control-plane/openclaw.tgz` |
| Wallpaper | `/assets/wallpaper.jpg` | `control-plane/cloudbot-wallpaper.jpg` |

These are copied into the Docker image and served by FastAPI.

### Environment Differences

| Setting | Local (.env) | Production (Railway) |
|---------|--------------|---------------------|
| `CONTROL_PLANE_URL` | `https://cloudbot-ai.com`* | `https://cloudbot-ai.com` |
| `DATABASE_URL` | localhost PostgreSQL | Railway PostgreSQL |
| `CORS_ORIGINS` | `localhost:5173,5174,3000` | `https://cloudbot-ai.com` |
| `ENVIRONMENT` | `development` | `production` |

*Set local to production URL so EC2 instances can download assets.

### Railway Configuration Files

- **railway.json** - Build and deploy settings
- **Dockerfile** - Multi-stage build (frontend + backend)
- **start.sh** - Runtime entrypoint

### Useful Railway Commands

```bash
# View logs
railway logs

# Open dashboard
railway open

# List services
railway status

# SSH into container (debugging)
railway shell

# Set environment variable
railway variables set KEY=value

# Run database migrations
railway run alembic upgrade head
```

### CI/CD Flow

```
Developer pushes to main
        │
        ▼
Railway detects push
        │
        ▼
Docker build (Dockerfile)
├── Stage 1: Build React frontend
└── Stage 2: Python backend + frontend dist
        │
        ▼
Health check (/health endpoint)
        │
        ▼
Traffic switched to new container
        │
        ▼
Old container terminated
```

### Monitoring

- **Railway Dashboard**: View logs, metrics, deployments
- **EC2 Debug Server**: `http://<ip>:8080/debug`
- **CloudWatch**: AWS metrics for EC2 instances

---

## License

MIT
