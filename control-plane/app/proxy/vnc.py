"""VNC WebSocket proxy"""
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.connection import get_db
from app.db.models import Instance, User
from app.auth.middleware import get_current_user
import asyncio
import socket
import logging

logger = logging.getLogger(__name__)


async def proxy_vnc(
    websocket: WebSocket,
    instance_id: str,
    current_user: User,
    db: AsyncSession
):
    """Proxy VNC connection from browser to EC2 instance"""
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

    # Connect to VNC server on instance
    vnc_host = instance.public_ip
    vnc_port = instance.vnc_port

    try:
        # Create TCP connection to VNC server
        reader, writer = await asyncio.open_connection(vnc_host, vnc_port)
        logger.info(f"Connected to VNC server at {vnc_host}:{vnc_port}")

        async def forward_to_vnc():
            """Forward WebSocket messages to VNC"""
            try:
                while True:
                    data = await websocket.receive_bytes()
                    writer.write(data)
                    await writer.drain()
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
            except Exception as e:
                logger.error(f"Error forwarding to VNC: {e}")
            finally:
                writer.close()
                await writer.wait_closed()

        async def forward_from_vnc():
            """Forward VNC responses to WebSocket"""
            try:
                while True:
                    data = await reader.read(8192)
                    if not data:
                        break
                    await websocket.send_bytes(data)
            except Exception as e:
                logger.error(f"Error forwarding from VNC: {e}")
            finally:
                await websocket.close()

        # Run both directions concurrently
        await asyncio.gather(
            forward_to_vnc(),
            forward_from_vnc(),
            return_exceptions=True
        )

    except ConnectionRefusedError:
        logger.error(f"Failed to connect to VNC server at {vnc_host}:{vnc_port}")
        await websocket.close(code=1011, reason="VNC server not available")
    except Exception as e:
        logger.error(f"VNC proxy error: {e}")
        await websocket.close(code=1011, reason="Proxy error")
