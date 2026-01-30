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
import uuid as uuid_mod

logger = logging.getLogger(__name__)


async def send_status(websocket: WebSocket, status: str, message: str):
    """Send a status event to the browser"""
    try:
        await websocket.send_text(json.dumps({
            "type": "event",
            "event": "status",
            "payload": {"status": status, "message": message}
        }))
    except Exception:
        pass  # Ignore errors sending status


async def proxy_cloudbot(
    websocket: WebSocket,
    instance_id: str,
    current_user: User,
    db: AsyncSession
):
    """Proxy CloudBot WebSocket connection from browser to EC2 instance"""
    await websocket.accept()

    # Send initial status
    await send_status(websocket, "connecting", "Looking up instance...")

    # Get instance
    try:
        inst_uuid = uuid_mod.UUID(instance_id)
    except ValueError:
        await send_status(websocket, "error", "Invalid instance ID")
        await websocket.close(code=1008, reason="Invalid instance ID")
        return

    result = await db.execute(
        select(Instance).where(
            Instance.id == inst_uuid,
            Instance.user_id == current_user.id
        )
    )
    instance = result.scalar_one_or_none()

    if not instance or not instance.public_ip:
        await send_status(websocket, "error", "Instance not found or not ready")
        await websocket.close(code=1008, reason="Instance not found or not ready")
        return

    # Connect to CloudBot gateway on instance
    cloudbot_url = f"ws://{instance.public_ip}:{instance.cloudbot_port}"
    await send_status(websocket, "connecting", f"Connecting to CloudBot gateway...")

    try:
        async with websockets.connect(
            cloudbot_url,
            open_timeout=10,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=5
        ) as cloudbot_ws:
            logger.info(f"Connected to CloudBot at {cloudbot_url}")

            stop_event = asyncio.Event()

            async def forward_to_cloudbot():
                """Forward WebSocket messages from browser to CloudBot"""
                try:
                    while not stop_event.is_set():
                        # Receive from browser
                        data = await websocket.receive_text()
                        # Forward to CloudBot
                        await cloudbot_ws.send(data)
                except WebSocketDisconnect:
                    logger.info("Browser WebSocket disconnected")
                    stop_event.set()
                except Exception as e:
                    logger.error(f"Error forwarding to CloudBot: {e}")
                    stop_event.set()

            async def forward_from_cloudbot():
                """Forward messages from CloudBot to browser"""
                try:
                    async for message in cloudbot_ws:
                        if stop_event.is_set():
                            break
                        # Forward to browser
                        await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error forwarding from CloudBot: {e}")
                    stop_event.set()

            # Run both directions concurrently
            await asyncio.gather(
                forward_to_cloudbot(),
                forward_from_cloudbot(),
                return_exceptions=True
            )

    except asyncio.TimeoutError:
        error_msg = "CloudBot gateway connection timed out (service may still be starting)"
        logger.error(f"Timeout connecting to CloudBot at {cloudbot_url}")
        await send_status(websocket, "error", error_msg)
        await websocket.close(code=1011, reason="CloudBot timeout")
    except (ConnectionRefusedError, OSError) as e:
        error_msg = "CloudBot not available (service may not be running)"
        logger.error(f"Failed to connect to CloudBot at {cloudbot_url}: {e}")
        await send_status(websocket, "error", error_msg)
        await websocket.close(code=1011, reason="CloudBot not available")
    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        logger.error(f"CloudBot proxy error: {e}")
        await send_status(websocket, "error", error_msg)
        await websocket.close(code=1011, reason="Proxy error")
    finally:
        try:
            await websocket.close()
        except:
            pass
