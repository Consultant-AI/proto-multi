"""Instance ownership verification middleware"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.connection import get_db
from app.db.models import Instance, User
from app.auth.middleware import get_current_user
import uuid


async def verify_instance_ownership(
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Instance:
    """Verify that the current user owns the specified instance"""
    try:
        inst_uuid = uuid.UUID(instance_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid instance ID format"
        )

    result = await db.execute(
        select(Instance).where(
            Instance.id == inst_uuid,
            Instance.user_id == current_user.id
        )
    )
    instance = result.scalar_one_or_none()

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found or access denied"
        )

    return instance
