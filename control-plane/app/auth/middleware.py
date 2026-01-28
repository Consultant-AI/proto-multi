"""Authentication middleware"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.connection import get_db
from app.db.models import User
from app.auth.jwt import verify_access_token
from app.config import settings
from typing import Optional, Union
from datetime import datetime
import uuid

security = HTTPBearer()

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Union[User, dict]:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials

    # Verify token
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In LOCAL_DEV_MODE, return a mock user dict
    if settings.local_dev_mode:
        return {
            "id": payload.get("sub", DEMO_USER_ID),
            "email": payload.get("email", "demo@cloudbot.dev"),
            "created_at": datetime.utcnow(),
        }

    # Extract user ID
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[Union[User, dict]]:
    """Get current user if authenticated, None otherwise"""
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
