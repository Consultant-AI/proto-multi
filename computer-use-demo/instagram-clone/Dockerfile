# Multi-stage Dockerfile for Instagram Clone

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/client
COPY client/package*.json ./
RUN npm ci
COPY client/ ./
RUN npm run build

# Stage 2: Backend
FROM node:18-alpine
WORKDIR /app

# Install dependencies
COPY server/package*.json ./
RUN npm ci --only=production

# Copy server code
COPY server/ ./

# Copy built frontend
COPY --from=frontend-build /app/client/build ./public

# Create uploads directory
RUN mkdir -p uploads/posts uploads/avatars uploads/stories

# Expose port
EXPOSE 5000

# Start server
CMD ["npm", "start"]
