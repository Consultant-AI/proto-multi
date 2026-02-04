# Multi-stage build for CloudBot Control Plane
# Build v2

# Stage 1: Build frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm install

# Build frontend
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY app/ ./app/
COPY alembic.ini ./
COPY cloudbot-wallpaper.jpg ./
COPY openclaw.tgz ./
COPY start.sh ./
RUN chmod +x start.sh

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create non-root user
RUN useradd -m -u 1000 cloudbot && chown -R cloudbot:cloudbot /app
USER cloudbot

# Expose port (Railway uses dynamic PORT)
EXPOSE 8000

# Note: Railway handles healthchecks via railway.json
# Removed Dockerfile HEALTHCHECK to avoid conflicts

# Run the application
CMD ["./start.sh"]
