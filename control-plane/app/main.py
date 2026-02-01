"""FastAPI application entry point"""
from fastapi import FastAPI, Request, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
import logging
import os

from app.config import settings, validate_production_config
from app.db.connection import get_db, init_db, close_db, AsyncSessionLocal
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


# Static assets endpoint for instance resources
@app.get("/assets/wallpaper.jpg")
async def get_wallpaper():
    """Serve the CloudBot wallpaper for instances"""
    wallpaper_path = os.path.join(os.path.dirname(__file__), "..", "cloudbot-wallpaper.jpg")
    if os.path.exists(wallpaper_path):
        return FileResponse(wallpaper_path, media_type="image/jpeg")
    return JSONResponse(status_code=404, content={"error": "Wallpaper not found"})


@app.get("/assets/openclaw.tgz")
async def get_openclaw_tarball():
    """Serve the OpenClaw tarball for EC2 instance installation"""
    tarball_path = os.path.join(os.path.dirname(__file__), "..", "openclaw.tgz")
    if os.path.exists(tarball_path):
        return FileResponse(tarball_path, media_type="application/gzip", filename="openclaw.tgz")
    return JSONResponse(status_code=404, content={"error": "OpenClaw tarball not found"})


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


# WebSocket endpoints - use query param auth since HTTPBearer doesn't work with WebSockets
@app.websocket("/api/instances/{instance_id}/vnc")
async def vnc_websocket(
    websocket: WebSocket,
    instance_id: str,
):
    """VNC WebSocket proxy endpoint"""
    from app.auth.jwt import verify_access_token
    from sqlalchemy import select
    from app.db.models import User, Instance
    import uuid as uuid_mod

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return

    payload = verify_access_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return

    user_id_str = payload.get("sub")
    if not user_id_str:
        await websocket.close(code=1008, reason="Invalid token payload")
        return

    async with AsyncSessionLocal() as db:
        try:
            user_id = uuid_mod.UUID(user_id_str)
            result = await db.execute(select(User).where(User.id == user_id))
            current_user = result.scalar_one_or_none()
            if not current_user:
                await websocket.close(code=1008, reason="User not found")
                return
            await proxy_vnc(websocket, instance_id, current_user, db)
        except Exception as e:
            logger.error(f"VNC WebSocket error: {e}")
            try:
                await websocket.close(code=1011, reason="Server error")
            except:
                pass


@app.websocket("/api/instances/{instance_id}/cloudbot")
async def cloudbot_websocket(
    websocket: WebSocket,
    instance_id: str,
):
    """CloudBot WebSocket proxy endpoint"""
    from app.auth.jwt import verify_access_token
    from sqlalchemy import select
    from app.db.models import User, Instance
    import uuid as uuid_mod

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return

    payload = verify_access_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return

    user_id_str = payload.get("sub")
    if not user_id_str:
        await websocket.close(code=1008, reason="Invalid token payload")
        return

    async with AsyncSessionLocal() as db:
        try:
            user_id = uuid_mod.UUID(user_id_str)
            result = await db.execute(select(User).where(User.id == user_id))
            current_user = result.scalar_one_or_none()
            if not current_user:
                await websocket.close(code=1008, reason="User not found")
                return
            await proxy_cloudbot(websocket, instance_id, current_user, db)
        except Exception as e:
            logger.error(f"CloudBot WebSocket error: {e}")
            try:
                await websocket.close(code=1011, reason="Server error")
            except:
                pass


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
