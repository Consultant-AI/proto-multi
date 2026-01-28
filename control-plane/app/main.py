"""FastAPI application entry point"""
from fastapi import FastAPI, Request, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.config import settings, validate_production_config
from app.db.connection import get_db, init_db, close_db
from app.api import auth, instances, api_keys
from app.proxy.vnc import proxy_vnc
from app.proxy.cloudbot import proxy_cloudbot
from app.auth.middleware import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Validate production config
validate_production_config()

# Create FastAPI app
app = FastAPI(
    title="CloudBot Control Plane API",
    description="Control plane for CloudBot cloud platform",
    version="1.0.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment,
    }


# API info endpoint
@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "CloudBot Control Plane API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "instances": "/api/instances",
            "user": "/api/user",
            "websocket": {
                "vnc": "/api/instances/{id}/vnc",
                "cloudbot": "/api/instances/{id}/cloudbot",
            },
        },
        "docs": "/docs" if settings.environment != "production" else "disabled",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.environment == "development" else None,
        },
    )


# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(instances.router, prefix="/api/instances", tags=["instances"])
app.include_router(api_keys.router, prefix="/api/user/api-keys", tags=["api-keys"])


# WebSocket endpoints
@app.websocket("/api/instances/{instance_id}/vnc")
async def vnc_websocket(
    websocket: WebSocket,
    instance_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """VNC WebSocket proxy endpoint"""
    await proxy_vnc(websocket, instance_id, current_user, db)


@app.websocket("/api/instances/{instance_id}/cloudbot")
async def cloudbot_websocket(
    websocket: WebSocket,
    instance_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """CloudBot WebSocket proxy endpoint"""
    await proxy_cloudbot(websocket, instance_id, current_user, db)


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 CloudBot Control Plane starting...")
    logger.info(f"📝 Environment: {settings.environment}")
    logger.info(f"💾 Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'local'}")
    logger.info(f"🔴 Redis: {settings.redis_url}")
    if settings.local_dev_mode:
        logger.info("⚠️  Local dev mode enabled (no AWS)")
    logger.info(f"🌐 CORS origins: {settings.cors_origins_list}")

    # Initialize database
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 CloudBot Control Plane shutting down...")
    await close_db()
