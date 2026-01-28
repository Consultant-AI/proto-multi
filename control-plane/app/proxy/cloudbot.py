"""CloudBot WebSocket proxy"""
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.connection import get_db
from app.db.models import Instance, User
import asyncio
import websockets
import logging
import json

logger = logging.getLogger(__name__)


async def proxy_cloudbot(
    websocket: WebSocket,
    instance_id: str,
    current_user: User,
    db: AsyncSession
):
    """Proxy CloudBot WebSocket connection from browser to EC2 instance"""
    await websocket.accept()

    # Get instance
    result = await db.execute(
        select(Instance).where(
            Instance.id == instance_id,
            Instance.user_id == current_user.id
        )
    )
    instance = result.scalar_one_or_none()

    if not instance or not instance.public_ip:
        await websocket.close(code=1008, reason="Instance not found or not ready")
        return

    # Connect to CloudBot gateway on instance
    cloudbot_url = f"ws://{instance.public_ip}:{instance.cloudbot_port}"

    try:
        async with websockets.connect(cloudbot_url) as cloudbot_ws:
            logger.info(f"Connected to CloudBot at {cloudbot_url}")

            async def forward_to_cloudbot():
                """Forward WebSocket messages from browser to CloudBot"""
                try:
                    while True:
                        # Receive from browser
                        data = await websocket.receive_text()
                        # Forward to CloudBot
                        await cloudbot_ws.send(data)
                except WebSocketDisconnect:
                    logger.info("Browser WebSocket disconnected")
                except Exception as e:
                    logger.error(f"Error forwarding to CloudBot: {e}")

            async def forward_from_cloudbot():
                """Forward messages from CloudBot to browser"""
                try:
                    async for message in cloudbot_ws:
                        # Forward to browser
                        await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error forwarding from CloudBot: {e}")

            # Run both directions concurrently
            await asyncio.gather(
                forward_to_cloudbot(),
                forward_from_cloudbot(),
                return_exceptions=True
            )

    except (ConnectionRefusedError, OSError) as e:
        logger.error(f"Failed to connect to CloudBot at {cloudbot_url}: {e}")
        await websocket.close(code=1011, reason="CloudBot not available")
    except Exception as e:
        logger.error(f"CloudBot proxy error: {e}")
        await websocket.close(code=1011, reason="Proxy error")
    finally:
        try:
            await websocket.close()
        except:
            pass
