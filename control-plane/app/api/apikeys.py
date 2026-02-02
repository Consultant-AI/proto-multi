"""API Key management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from app.db.connection import get_db
from app.db.models import User, UserApiKey
from app.auth.middleware import get_current_user
from app.utils.encryption import encrypt_api_key, decrypt_api_key
from typing import List

router = APIRouter()


# Request/Response models
class ApiKeyRequest(BaseModel):
    provider: str  # 'anthropic', 'openai', 'google'
    api_key: str


class ApiKeyResponse(BaseModel):
    provider: str
    created_at: str


class ApiKeysListResponse(BaseModel):
    providers: List[str]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def store_api_key(
    request: ApiKeyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Store an encrypted API key"""
    # Validate provider
    valid_providers = ['anthropic', 'openai', 'google']
    if request.provider.lower() not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider must be one of: {', '.join(valid_providers)}"
        )

    # Encrypt API key
    encrypted = encrypt_api_key(request.api_key)

    # Check if key already exists for this provider
    result = await db.execute(
        select(UserApiKey).where(
            UserApiKey.user_id == current_user.id,
            UserApiKey.provider == request.provider.lower()
        )
    )
    existing_key = result.scalar_one_or_none()

    if existing_key:
        # Update existing key
        existing_key.encrypted_key = encrypted
    else:
        # Create new key
        api_key = UserApiKey(
            user_id=current_user.id,
            provider=request.provider.lower(),
            encrypted_key=encrypted
        )
        db.add(api_key)

    await db.commit()

    return {"message": f"{request.provider} API key stored successfully"}


@router.get("/", response_model=ApiKeysListResponse)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List configured API key providers (not the keys themselves)"""
    result = await db.execute(
        select(UserApiKey.provider).where(UserApiKey.user_id == current_user.id)
    )
    providers = [row[0] for row in result.all()]

    return ApiKeysListResponse(providers=providers)


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API key"""
    result = await db.execute(
        delete(UserApiKey).where(
            UserApiKey.user_id == current_user.id,
            UserApiKey.provider == provider.lower()
        )
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No API key found for provider: {provider}"
        )

    await db.commit()
    return None


async def get_user_api_key(user_id, provider: str, db: AsyncSession) -> str | None:
    """Helper function to get decrypted API key for a user"""
    result = await db.execute(
        select(UserApiKey).where(
            UserApiKey.user_id == user_id,
            UserApiKey.provider == provider.lower()
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        return None

    return decrypt_api_key(api_key.encrypted_key)
