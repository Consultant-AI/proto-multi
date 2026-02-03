"""Instance management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Union, Dict
from app.db.connection import get_db
from app.db.models import User, Instance, UserApiKey
from app.auth.middleware import get_current_user
from app.orchestrator.ec2 import orchestrator
from app.config import settings
from app.utils.encryption import decrypt_api_key
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory store for LOCAL_DEV_MODE
_demo_instances: dict[str, dict] = {}


def _get_user_id(current_user: Union[User, dict]) -> str:
    if isinstance(current_user, dict):
        return current_user["id"]
    return str(current_user.id)


async def _get_user_api_keys(user_id, db: AsyncSession) -> Dict[str, str]:
    """Fetch and decrypt user's API keys"""
    result = await db.execute(
        select(UserApiKey).where(UserApiKey.user_id == user_id)
    )
    api_keys = result.scalars().all()

    logger.info(f"Found {len(api_keys)} API keys in database for user {user_id}")

    decrypted_keys = {}
    for key in api_keys:
        try:
            decrypted_value = decrypt_api_key(key.encrypted_key)
            decrypted_keys[key.provider] = decrypted_value
            # Log success with partial key for debugging (first 10 chars)
            key_preview = decrypted_value[:10] + "..." if len(decrypted_value) > 10 else decrypted_value
            logger.info(f"Successfully decrypted API key for {key.provider}: {key_preview}")
        except Exception as e:
            logger.error(f"FAILED to decrypt API key for provider {key.provider}: {e}")
            logger.error(f"  Encrypted key length: {len(key.encrypted_key)}")

    logger.info(f"Total decrypted keys: {len(decrypted_keys)} providers: {list(decrypted_keys.keys())}")
    return decrypted_keys


# Request/Response models
class CreateInstanceRequest(BaseModel):
    name: Optional[str] = None
    instance_type: str = 't3.micro'  # t3.micro, t3.small, t3.medium, t3.large, t3.xlarge
    api_keys: Optional[Dict[str, str]] = None  # Provider -> API key mapping


class InstanceResponse(BaseModel):
    id: str
    name: Optional[str]
    status: str
    public_ip: Optional[str]
    ec2_instance_id: Optional[str]
    vnc_port: int
    cloudbot_port: int
    created_at: datetime


class InstanceListResponse(BaseModel):
    instances: List[InstanceResponse]


@router.post("", response_model=InstanceResponse, status_code=status.HTTP_201_CREATED)
async def create_instance(
    request: CreateInstanceRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new instance"""
    user_id = _get_user_id(current_user)

    if settings.local_dev_mode:
        # Create mock instance in memory
        user_instances = [i for i in _demo_instances.values() if i["user_id"] == user_id and i["status"] in ("launching", "running")]
        if len(user_instances) >= settings.max_instances_per_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.max_instances_per_user} active instances allowed"
            )

        instance_id = str(uuid.uuid4())
        mock_ec2_id = f"i-demo-{instance_id[:8]}"
        instance_data = {
            "id": instance_id,
            "user_id": user_id,
            "name": request.name or f"Instance {len(user_instances) + 1}",
            "status": "running",
            "public_ip": "127.0.0.1",
            "ec2_instance_id": mock_ec2_id,
            "vnc_port": 5900,
            "cloudbot_port": 18789,
            "created_at": datetime.utcnow(),
        }
        _demo_instances[instance_id] = instance_data

        return InstanceResponse(
            id=instance_data["id"],
            name=instance_data["name"],
            status=instance_data["status"],
            public_ip=instance_data["public_ip"],
            ec2_instance_id=instance_data["ec2_instance_id"],
            vnc_port=instance_data["vnc_port"],
            cloudbot_port=instance_data["cloudbot_port"],
            created_at=instance_data["created_at"],
        )

    # Production mode with real database
    result = await db.execute(
        select(Instance).where(
            Instance.user_id == current_user.id,
            Instance.status.in_(['launching', 'running'])
        )
    )
    active_instances = result.scalars().all()

    if len(active_instances) >= settings.max_instances_per_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.max_instances_per_user} active instances allowed"
        )

    instance = Instance(
        user_id=current_user.id,
        name=request.name or f"Instance {len(active_instances) + 1}",
        status="launching"
    )
    db.add(instance)
    await db.flush()

    try:
        # Use API keys from request if provided, otherwise fetch from database
        api_keys = request.api_keys
        if api_keys:
            logger.info(f"API keys provided in request: {list(api_keys.keys())}")
        else:
            logger.info(f"No API keys in request, fetching from database for user {current_user.id}")
            api_keys = await _get_user_api_keys(current_user.id, db)
        if not api_keys:
            logger.warning(f"No API keys found for user {current_user.id}")
        else:
            logger.info(f"Passing API keys to EC2: {list(api_keys.keys())}")

        ec2_result = await orchestrator.create_instance(
            user_id=str(current_user.id),
            instance_name=instance.name,
            instance_type=request.instance_type,
            api_keys=api_keys
        )
        instance.ec2_instance_id = ec2_result["instance_id"]
        instance.public_ip = ec2_result.get("public_ip")
        instance.status = ec2_result["status"]
        await db.commit()

    except Exception as e:
        instance.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to provision instance: {str(e)}"
        )

    return InstanceResponse(
        id=str(instance.id),
        name=instance.name,
        status=instance.status,
        public_ip=instance.public_ip,
        ec2_instance_id=instance.ec2_instance_id,
        vnc_port=instance.vnc_port,
        cloudbot_port=instance.cloudbot_port,
        created_at=instance.created_at
    )


@router.get("", response_model=InstanceListResponse)
async def list_instances(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all instances for current user"""
    user_id = _get_user_id(current_user)

    if settings.local_dev_mode:
        user_instances = [i for i in _demo_instances.values() if i["user_id"] == user_id]
        user_instances.sort(key=lambda x: x["created_at"], reverse=True)
        return InstanceListResponse(
            instances=[
                InstanceResponse(
                    id=inst["id"],
                    name=inst["name"],
                    status=inst["status"],
                    public_ip=inst["public_ip"],
                    ec2_instance_id=inst["ec2_instance_id"],
                    vnc_port=inst["vnc_port"],
                    cloudbot_port=inst["cloudbot_port"],
                    created_at=inst["created_at"],
                )
                for inst in user_instances
            ]
        )

    result = await db.execute(
        select(Instance).where(Instance.user_id == current_user.id).order_by(Instance.created_at.desc())
    )
    instances = result.scalars().all()

    # Sync status from EC2 for non-terminated instances
    for inst in instances:
        if inst.ec2_instance_id and inst.status not in ('terminated', 'failed'):
            try:
                ec2_status = await orchestrator.get_instance_status(inst.ec2_instance_id)
                if ec2_status.get("status"):
                    inst.status = ec2_status["status"]
                    if ec2_status.get("public_ip"):
                        inst.public_ip = ec2_status["public_ip"]
            except Exception:
                pass
    await db.commit()

    return InstanceListResponse(
        instances=[
            InstanceResponse(
                id=str(inst.id),
                name=inst.name,
                status=inst.status,
                public_ip=inst.public_ip,
                ec2_instance_id=inst.ec2_instance_id,
                vnc_port=inst.vnc_port,
                cloudbot_port=inst.cloudbot_port,
                created_at=inst.created_at
            )
            for inst in instances
        ]
    )


@router.get("/{instance_id}", response_model=InstanceResponse)
async def get_instance(
    instance_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get instance details"""
    user_id = _get_user_id(current_user)

    if settings.local_dev_mode:
        inst = _demo_instances.get(instance_id)
        if not inst or inst["user_id"] != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
        return InstanceResponse(
            id=inst["id"],
            name=inst["name"],
            status=inst["status"],
            public_ip=inst["public_ip"],
            ec2_instance_id=inst["ec2_instance_id"],
            vnc_port=inst["vnc_port"],
            cloudbot_port=inst["cloudbot_port"],
            created_at=inst["created_at"],
        )

    try:
        inst_uuid = uuid.UUID(instance_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid instance ID")

    result = await db.execute(
        select(Instance).where(Instance.id == inst_uuid, Instance.user_id == current_user.id)
    )
    instance = result.scalar_one_or_none()

    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")

    if instance.ec2_instance_id:
        ec2_status = await orchestrator.get_instance_status(instance.ec2_instance_id)
        if ec2_status.get("status"):
            instance.status = ec2_status["status"]
            if ec2_status.get("public_ip"):
                instance.public_ip = ec2_status["public_ip"]
            await db.commit()

    return InstanceResponse(
        id=str(instance.id),
        name=instance.name,
        status=instance.status,
        public_ip=instance.public_ip,
        ec2_instance_id=instance.ec2_instance_id,
        vnc_port=instance.vnc_port,
        cloudbot_port=instance.cloudbot_port,
        created_at=instance.created_at
    )


@router.post("/{instance_id}/stop")
async def stop_instance(
    instance_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop an instance"""
    user_id = _get_user_id(current_user)

    if settings.local_dev_mode:
        inst = _demo_instances.get(instance_id)
        if not inst or inst["user_id"] != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
        inst["status"] = "stopped"
        return {"message": "Instance stopped"}

    try:
        inst_uuid = uuid.UUID(instance_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid instance ID")

    result = await db.execute(
        select(Instance).where(Instance.id == inst_uuid, Instance.user_id == current_user.id)
    )
    instance = result.scalar_one_or_none()

    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")

    if instance.ec2_instance_id:
        success = await orchestrator.stop_instance(instance.ec2_instance_id)
        if success:
            instance.status = "stopping"
            instance.stopped_at = datetime.utcnow()
            await db.commit()

    return {"message": "Instance stop initiated"}


@router.post("/{instance_id}/start")
async def start_instance(
    instance_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a stopped instance"""
    user_id = _get_user_id(current_user)

    if settings.local_dev_mode:
        inst = _demo_instances.get(instance_id)
        if not inst or inst["user_id"] != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
        inst["status"] = "running"
        inst["public_ip"] = "127.0.0.1"
        return {"message": "Instance started"}

    try:
        inst_uuid = uuid.UUID(instance_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid instance ID")

    result = await db.execute(
        select(Instance).where(Instance.id == inst_uuid, Instance.user_id == current_user.id)
    )
    instance = result.scalar_one_or_none()

    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")

    if instance.ec2_instance_id:
        success = await orchestrator.start_instance(instance.ec2_instance_id)
        if success:
            instance.status = "launching"
            await db.commit()

    return {"message": "Instance start initiated"}


@router.delete("/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instance(
    instance_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Terminate and delete an instance"""
    user_id = _get_user_id(current_user)

    if settings.local_dev_mode:
        inst = _demo_instances.get(instance_id)
        if not inst or inst["user_id"] != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
        del _demo_instances[instance_id]
        return None

    try:
        inst_uuid = uuid.UUID(instance_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid instance ID")

    result = await db.execute(
        select(Instance).where(Instance.id == inst_uuid, Instance.user_id == current_user.id)
    )
    instance = result.scalar_one_or_none()

    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")

    if instance.ec2_instance_id:
        await orchestrator.terminate_instance(instance.ec2_instance_id)

    await db.delete(instance)
    await db.commit()

    return None
