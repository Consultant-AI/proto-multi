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

## License

MIT
