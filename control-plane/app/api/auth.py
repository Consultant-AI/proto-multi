"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.db.connection import get_db
from app.db.models import User, Session as DBSession
from app.auth.jwt import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    hash_token,
)
from app.auth.middleware import get_current_user
from app.config import settings
import uuid

router = APIRouter()

# Demo user for LOCAL_DEV_MODE
DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"
DEMO_USER_EMAIL = "demo@cloudbot.dev"
DEMO_USER_PASSWORD = "demo1234"


# Request/Response models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: Optional[datetime] = None


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: AsyncSession = Depends(get_db)):
    """Create a new user account"""
    if settings.local_dev_mode:
        access_token = create_access_token({
            "sub": DEMO_USER_ID,
            "email": request.email
        })
        refresh_token = create_refresh_token({"sub": DEMO_USER_ID})
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    user = User(
        email=request.email,
        password_hash=hash_password(request.password)
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    session = DBSession(
        user_id=user.id,
        token_hash=hash_token(access_token),
        refresh_token_hash=hash_token(refresh_token),
        expires_at=datetime.utcnow()
    )
    db.add(session)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and get JWT tokens"""
    if settings.local_dev_mode:
        access_token = create_access_token({
            "sub": DEMO_USER_ID,
            "email": request.email
        })
        refresh_token = create_refresh_token({"sub": DEMO_USER_ID})
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    user.last_login = datetime.utcnow()

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    session = DBSession(
        user_id=user.id,
        token_hash=hash_token(access_token),
        refresh_token_hash=hash_token(refresh_token),
        expires_at=datetime.utcnow()
    )
    db.add(session)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token"""
    if settings.local_dev_mode:
        payload = verify_refresh_token(request.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        access_token = create_access_token({
            "sub": DEMO_USER_ID,
            "email": DEMO_USER_EMAIL
        })
        new_refresh_token = create_refresh_token({"sub": DEMO_USER_ID})
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )

    payload = verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user_id = uuid.UUID(payload["sub"])

    result = await db.execute(
        select(DBSession).where(
            DBSession.user_id == user_id,
            DBSession.refresh_token_hash == hash_token(request.refresh_token)
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or expired"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    session.token_hash = hash_token(access_token)
    session.refresh_token_hash = hash_token(new_refresh_token)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    """Get current user information"""
    if isinstance(current_user, dict):
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            created_at=current_user["created_at"]
        )

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        created_at=current_user.created_at
    )
