# CloudBot Cloud Platform - MVP

Complete MVP implementation for a cloud-based platform where users can create on-demand Ubuntu desktop instances with integrated remote desktop viewing and AI-powered computer control via CloudBot.

## 🎯 MVP Features

- ✅ User authentication (signup, login, JWT tokens)
- ✅ API key management (Anthropic, OpenAI, Google)
- ✅ AWS EC2 instance provisioning (spot instances)
- ✅ Ubuntu 24.04 desktop with GNOME
- ✅ VNC remote desktop streaming (noVNC in browser)
- ✅ CloudBot AI agent integration
- ✅ WebSocket proxies for VNC and CloudBot
- ✅ Split-view UI (desktop + chat side-by-side)
- ✅ Instance management (create, list, stop, delete)
- ✅ Support for 10 concurrent users

## 📁 Project Structure

```
proto-multi/
├── control-plane/          # Python FastAPI backend
│   ├── app/
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── config.py      # Configuration management
│   │   ├── db/            # Database models and migrations
│   │   ├── auth/          # JWT authentication
│   │   ├── api/           # API endpoints (auth, instances, API keys)
│   │   ├── orchestrator/  # AWS EC2 orchestration
│   │   ├── proxy/         # WebSocket proxies (VNC, CloudBot)
│   │   ├── middleware/    # Auth middleware
│   │   └── utils/         # Encryption utilities
│   ├── requirements.txt
│   ├── alembic.ini
│   └── README.md
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx        # Main app with routing
│   │   ├── components/
│   │   │   ├── Auth/      # Login, Signup, ApiKeySetup
│   │   │   ├── Dashboard/ # InstanceList, CreateInstance
│   │   │   ├── Desktop/   # RemoteDesktop, SplitView
│   │   │   └── Chat/      # ChatInterface
│   │   ├── contexts/      # AuthContext, InstanceContext
│   │   ├── services/      # API client, VNC client
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── README.md
└── cloudbot/              # Forked from moltbot (AI agent)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 22+
- PostgreSQL 16+
- Redis 7+
- AWS account with EC2 permissions (or use LOCAL_DEV_MODE=true)

### 1. Backend Setup (Control Plane)

```bash
cd control-plane

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration:
# - DATABASE_URL (PostgreSQL)
# - REDIS_URL
# - JWT secrets (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - ENCRYPTION_KEY (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
# - AWS credentials (or set LOCAL_DEV_MODE=true)

# Run database migrations (if using PostgreSQL)
# Create database first: createdb cloudbot_platform
# Then apply schema:
psql -d cloudbot_platform -f app/db/migrations/001_initial.sql

# Start server
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

API documentation: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

### 3. Local Development Mode

For testing without AWS:

1. Set `LOCAL_DEV_MODE=true` in `control-plane/.env`
2. The system will create mock instances instead of real EC2 instances
3. VNC and CloudBot connections will fail (expected in local mode)

For full testing, you need:
- AWS credentials with EC2 permissions
- Configured VPC, security group, subnet
- Ubuntu 24.04 AMI ID for your region

## 🔧 Configuration

### Backend (.env)

```bash
# Server
ENVIRONMENT=development
PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cloudbot_platform
REDIS_URL=redis://localhost:6379

# JWT Secrets (generate secure values)
JWT_SECRET_KEY=your-secret-here
JWT_REFRESH_SECRET_KEY=your-refresh-secret-here

# Encryption Key (generate secure value)
ENCRYPTION_KEY=your-encryption-key-here

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
EC2_SECURITY_GROUP_ID=sg-xxx
EC2_SUBNET_ID=subnet-xxx
EC2_KEY_PAIR_NAME=cloudbot-key
UBUNTU_AMI_ID=ami-0c55b159cbfafe1f0

# Features
LOCAL_DEV_MODE=false
MAX_INSTANCES_PER_USER=2

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

## 📖 User Journey

1. **Sign Up**: User creates account at /signup
2. **Add API Keys**: Optional step to add Anthropic/OpenAI/Google API keys
3. **Dashboard**: View list of instances
4. **Create Instance**: Click "Create Instance" button
5. **Wait for Launch**: Instance provisions in 2-3 minutes
6. **Split View**: Once running, view desktop (left) + chat (right)
7. **Interact**: Control desktop manually or via CloudBot chat commands
8. **Manage**: Stop, start, or delete instances from dashboard

## 🎨 Features

### Authentication
- JWT-based authentication with access + refresh tokens
- Secure password hashing (bcrypt)
- Automatic token refresh

### Instance Management
- Create Ubuntu desktop instances on AWS EC2
- Spot instances for cost savings
- Per-user instance limits
- Real-time status updates

### Remote Desktop
- VNC streaming via WebSocket
- noVNC client in browser
- Full keyboard and mouse support
- Responsive canvas scaling

### CloudBot Integration
- AI agent with computer control tools
- Browser automation
- Shell command execution
- File operations
- Natural language interface

### Security
- Encrypted API key storage (AES-256)
- Instance ownership verification
- WebSocket authentication
- CORS configuration
- SQL injection prevention

## 🧪 Testing

### Manual Testing Checklist

#### Authentication
- [ ] Sign up with new email
- [ ] Login with existing account
- [ ] Token refresh works automatically
- [ ] Logout clears tokens

#### Instances
- [ ] Create new instance
- [ ] Instance appears in list with "launching" status
- [ ] Status updates to "running" after 2-3 minutes
- [ ] Can view instance details
- [ ] Can delete instance

#### Remote Desktop
- [ ] Desktop appears in browser
- [ ] Mouse clicks work
- [ ] Keyboard input works
- [ ] Can open Firefox
- [ ] Can open VS Code

#### CloudBot Chat
- [ ] Chat interface loads
- [ ] Can send messages
- [ ] Agent responds
- [ ] Agent can execute commands
- [ ] Commands affect desktop

#### Split View
- [ ] Desktop and chat appear side-by-side
- [ ] Both work simultaneously
- [ ] Can resize panels
- [ ] Reconnects after network interruption

### Multi-User Testing
- [ ] Create 3 accounts
- [ ] Each creates instances simultaneously
- [ ] All instances provision successfully
- [ ] No cross-user access
- [ ] All connections work independently

## 📊 MVP Metrics

### Performance Targets
- Instance provisioning: < 3 minutes
- VNC connection: < 5 seconds to first frame
- Chat response: < 2 seconds for simple commands
- Concurrent users: 10 with < 5% error rate

### Cost Estimates (AWS)
- EC2 t3.large spot: ~$0.03/hour
- Per user (4 hours/month): ~$5/month
- 10 users: ~$50/month (instances only)
- + Database, networking: ~$100/month total

## 🐛 Known Limitations

### MVP Scope
- Linux (Ubuntu) only - no Windows/Mac
- Single region deployment
- No persistent storage (ephemeral instances)
- No instance snapshots
- No billing system
- No usage quotas
- Basic monitoring only

### Local Dev Mode
- VNC connections fail (no real desktop)
- CloudBot connections fail (no real agent)
- Mock instances created for testing API only

### WebSocket Auth
- Token passed in query param (less secure than header)
- No reconnection backoff strategy
- Limited error handling

## 🔮 Post-MVP Roadmap

### Phase 2 (Months 2-3)
- Windows Server support (RDP)
- macOS support (if budget allows)
- Auto-stop idle instances
- Instance snapshots
- Persistent home directories
- Advanced monitoring
- Billing system (Stripe)

### Phase 3 (Months 4-6)
- Team accounts
- SSO integration
- Kubernetes deployment
- Multi-region support
- Instance templates
- Marketplace

### Phase 4 (Months 7-12)
- GPU instances
- Collaborative editing
- Instance sharing
- CI/CD integration
- Compliance certifications

## 📝 License

MIT

## 🙏 Credits

- CloudBot based on [moltbot](https://github.com/moltbot/moltbot) by Mario Zechner
- noVNC for browser-based VNC client
- FastAPI for backend framework
- React for frontend framework

---

## 🚨 Getting Started Now

1. **Start backend:**
```bash
cd control-plane
source venv/bin/activate
uvicorn app.main:app --reload
```

2. **Start frontend (new terminal):**
```bash
cd frontend
npm run dev
```

3. **Open browser:** http://localhost:5173

4. **Create account and start testing!**

For local testing without AWS, set `LOCAL_DEV_MODE=true` in control-plane/.env
