# CloudBot Platform - Setup Guide

Quick setup guide for the CloudBot cloud platform MVP.

## Prerequisites Installation

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Install Node.js 22
brew install node@22

# Install PostgreSQL (optional, can use LOCAL_DEV_MODE)
brew install postgresql@16
brew services start postgresql@16

# Install Redis (optional, can use LOCAL_DEV_MODE)
brew install redis
brew services start redis
```

### Ubuntu/Debian

```bash
# Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Install Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PostgreSQL (optional)
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Install Redis (optional)
sudo apt install redis-server
sudo systemctl start redis
```

## Quick Start (Local Dev Mode)

This mode doesn't require AWS or databases - perfect for testing the UI!

### 1. Backend Setup

```bash
cd control-plane

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment already configured for local dev
# (control-plane/.env is set with LOCAL_DEV_MODE=true)

# Start server
uvicorn app.main:app --reload --port 8000
```

Backend runs on http://localhost:8000
API docs: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Environment already configured
# (frontend/.env points to localhost:8000)

# Start dev server
npm run dev
```

Frontend runs on http://localhost:5173

### 3. Test the Application

1. Open http://localhost:5173
2. Click "Sign up"
3. Create account (email/password)
4. Skip API key setup (or add keys if you have them)
5. Click "Create Instance"
6. Instance will be created in mock mode
7. Note: VNC and CloudBot won't work in local dev mode (expected)

## Full Setup (With AWS)

For real EC2 instances, VNC, and CloudBot:

### 1. AWS Setup

1. Create AWS account
2. Create IAM user with EC2 permissions
3. Get access key ID and secret key
4. Create/configure:
   - VPC (or use default)
   - Security group (allow ports: 22, 5900, 18789)
   - Subnet
   - EC2 key pair
   - Find Ubuntu 24.04 AMI ID for your region

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb cloudbot_platform

# Apply schema
psql -d cloudbot_platform -f control-plane/app/db/migrations/001_initial.sql

# Start Redis (if not running)
redis-server
```

### 3. Backend Configuration

Edit `control-plane/.env`:

```bash
# Set to false for real AWS
LOCAL_DEV_MODE=false

# Add your AWS credentials
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
EC2_SECURITY_GROUP_ID=sg-xxxxx
EC2_SUBNET_ID=subnet-xxxxx
EC2_KEY_PAIR_NAME=your-keypair
UBUNTU_AMI_ID=ami-xxxxx  # Ubuntu 24.04 in your region

# Generate secure secrets
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_REFRESH_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Database URLs
DATABASE_URL=postgresql://localhost:5432/cloudbot_platform
REDIS_URL=redis://localhost:6379
```

### 4. Start Services

```bash
# Terminal 1: Backend
cd control-plane
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 5. Test Full Stack

1. Sign up and add API keys (Anthropic recommended)
2. Create instance - will provision real EC2
3. Wait 2-3 minutes for instance to launch
4. View desktop via VNC
5. Chat with CloudBot to control the desktop

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check if port 8000 is available
lsof -i :8000
```

### Frontend won't start

```bash
# Check Node version
node --version  # Should be 22+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 5173 is available
lsof -i :5173
```

### Database connection fails

```bash
# Check PostgreSQL is running
pg_isready

# Create database if missing
createdb cloudbot_platform

# Apply migrations
psql -d cloudbot_platform -f control-plane/app/db/migrations/001_initial.sql
```

### EC2 instances fail to provision

- Check AWS credentials are correct
- Verify security group allows required ports
- Ensure you have EC2 quota/limits
- Check AMI ID is valid for your region
- Review control-plane logs for AWS errors

### VNC doesn't connect

- Instance must be in "running" status
- Security group must allow port 5900
- Wait for user-data script to complete (~2-3 min)
- Check instance logs: `ssh -i key.pem ubuntu@<ip>`

### CloudBot doesn't respond

- Ensure API keys are configured
- Check CloudBot service is running on instance
- Security group must allow port 18789
- Review browser console for WebSocket errors

## Development Tips

### Backend

```bash
# Run with debug logging
uvicorn app.main:app --reload --log-level debug

# Check API docs
open http://localhost:8000/docs

# Test endpoints with curl
curl http://localhost:8000/health
```

### Frontend

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Check TypeScript errors
npx tsc --noEmit
```

### Database

```bash
# Connect to database
psql cloudbot_platform

# View tables
\dt

# Query users
SELECT * FROM users;

# Query instances
SELECT id, name, status, public_ip FROM instances;
```

## Next Steps

1. Review [MVP_README.md](MVP_README.md) for full documentation
2. Check [control-plane/README.md](control-plane/README.md) for backend details
3. Check [frontend/README.md](frontend/README.md) for frontend details
4. Review the implementation plan at `.claude/plans/glistening-wishing-milner.md`

## Support

For issues or questions:
1. Check logs: `control-plane` terminal and browser console
2. Review error messages carefully
3. Ensure all prerequisites are installed
4. Try LOCAL_DEV_MODE=true for initial testing

Happy coding! 🚀
