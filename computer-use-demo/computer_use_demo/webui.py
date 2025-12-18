"""
FastAPI-powered dark web UI for the Claude computer use demo.

Run with:
    python -m computer_use_demo.webui
Then open http://localhost:8000
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import pickle
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, cast
import platform
import subprocess
import threading
import time

import httpx
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from anthropic.types.beta import BetaContentBlockParam, BetaMessageParam

from .loop import APIProvider, sampling_loop
from .tools import ToolResult, ToolVersion
from .logging import get_logger
from .planning import ProjectManager
from .daemon import WorkQueue

DEFAULT_MODEL = os.getenv("COMPUTER_USE_MODEL", "claude-sonnet-4-5-20250929")
DEFAULT_TOOL_VERSION = cast(
    ToolVersion, os.getenv("COMPUTER_USE_TOOL_VERSION", "proto_coding_v1")
)


def _resolve_api_key(cli_value: str | None = None) -> str:
    candidates = [
        cli_value,
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("CLAUDE_API_KEY"),
    ]
    for path in (
        os.path.expanduser("~/.anthropic/api_key"),
        os.path.expanduser("~/.config/anthropic/api_key"),
    ):
        if os.path.exists(path):
            candidates.append(open(path, "r", encoding="utf-8").read().strip())
    for candidate in candidates:
        if candidate:
            return candidate.strip()
    raise RuntimeError(
        "No Anthropic API key found. Set ANTHROPIC_API_KEY or create ~/.anthropic/api_key."
    )


@dataclass
class DisplayMessage:
    id: str
    role: Literal["user", "assistant", "tool"]
    text: str
    label: str | None = None
    images: list[str] = field(default_factory=list)


class ChatSession:
    """In-memory conversation state shared by the FastAPI handlers."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = DEFAULT_MODEL,
        tool_version: ToolVersion = DEFAULT_TOOL_VERSION,  # type: ignore[assignment]
        system_prompt_suffix: str = "",
    ):
        self.api_key = api_key
        self.model = model
        self.tool_version = tool_version
        self.system_prompt_suffix = system_prompt_suffix
        self.messages: list[BetaMessageParam] = []
        self.display_messages: list[DisplayMessage] = []
        self._pending_assistant_chunks: list[str] = []
        self._lock = asyncio.Lock()
        self._busy = False
        self.only_n_images = 3
        self.max_tokens = 4096
        self.thinking_budget: int | None = None

        # Agent SDK features (optimized for Claude Code-like behavior)
        self.session_id = f"webui-{uuid.uuid4().hex[:8]}"
        self.enable_verification = False  # Disabled for faster, direct tool usage
        self.use_ceo_agent = os.getenv("PROTO_USE_CEO_AGENT", "true").lower() == "true"  # CEO agent with planning/delegation
        self.session_stats: dict[str, Any] = {}

        # SSE streaming for real-time updates
        self._sse_queues: list[asyncio.Queue] = []

        # WebSocket connections for real-time updates
        self._ws_connections: list[WebSocket] = []

        # Stop/resume functionality
        self._stop_requested = False
        self._current_task: asyncio.Task | None = None
        self._executor_future: Any = None  # Future from ThreadPoolExecutor

        # Session persistence
        self.created_at = datetime.now()
        self.last_active = datetime.now()

        # Logging
        self.logger = get_logger()
        self.logger.log_event(
            event_type="session_created",
            session_id=self.session_id,
            data={
                "model": self.model,
                "tool_version": self.tool_version,
            },
            context={
                "created_at": self.created_at.isoformat(),
            },
        )

    async def stop(self, reason: str = "user_initiated") -> None:
        """Request the agent to stop.

        Args:
            reason: Why the stop was triggered:
                - "user_initiated": User clicked stop button (default)
                - "error": An error/exception caused the stop
                - "system": System/timeout caused the stop
        """
        self._stop_requested = True
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

        self.logger.log_event(
            event_type="conversation_stopped",
            session_id=self.session_id,
            data={
                "task_cancelled": self._current_task is not None and not self._current_task.done(),
                "reason": reason,
            },
        )

    async def send(self, user_text: str) -> None:
        if not user_text.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        async with self._lock:
            if self._busy:
                raise HTTPException(status_code=409, detail="Agent is already running.")
            self._busy = True
            self._stop_requested = False

        try:
            self.last_active = datetime.now()

            # Clean up any incomplete tool_use blocks before adding new message
            # This handles cases where previous execution was interrupted
            self.messages = self._clean_messages(self.messages)

            # Append the user message for both the API payload and UI.
            message_id = str(uuid.uuid4())
            self.messages.append(
                {
                    "role": "user",
                    "content": [{"type": "text", "text": user_text}],
                }
            )
            self.display_messages.append(
                DisplayMessage(
                    id=message_id,
                    role="user",
                    text=user_text.strip(),
                    label="You",
                )
            )

            # Log user message
            self.logger.log_user_message(
                session_id=self.session_id,
                message=user_text,
                message_id=message_id,
                context={
                    "conversation_length": len(self.messages),
                    "tools_available": self.tool_version,
                },
            )

            def output_callback(block: BetaContentBlockParam):
                if isinstance(block, dict) and block.get("type") == "text":
                    self._pending_assistant_chunks.append(block.get("text", ""))
                    # Send real-time update via WebSocket/SSE
                    # Schedule on main event loop (thread-safe)
                    loop.call_soon_threadsafe(
                        lambda: asyncio.create_task(self._broadcast_sse_update())
                    )

            def tool_output_callback(result: ToolResult, tool_id: str, tool_name: str, tool_input: dict[str, Any]):
                # Format tool name nicely
                tool_display_name = tool_name.replace("_", " ").title()

                # Build concise tool description
                input_parts = []
                for key, value in tool_input.items():
                    # Format value concisely
                    if isinstance(value, str):
                        if len(value) > 50:
                            formatted_value = f'"{value[:50]}..."'
                        else:
                            formatted_value = f'"{value}"'
                    elif isinstance(value, list):
                        formatted_value = str(value)
                    else:
                        formatted_value = str(value)
                    input_parts.append(f"{key}={formatted_value}")

                # Create parameter description (no tool name - it's shown by the UI via label)
                text_parts = []

                if input_parts:
                    text_parts.append(', '.join(input_parts))

                # Add additional info if present (but skip generic "executed" messages)
                if result.system:
                    text_parts.append(f"[system] {result.system.strip()}")
                # Only include output if it's meaningful (not just "executed" confirmation)
                if result.output and not result.output.strip().endswith("executed"):
                    text_parts.append(result.output.strip())
                if result.error:
                    text_parts.append(f"⚠️ {result.error.strip()}")

                final_text = "\n".join(text_parts) if text_parts else "(no parameters)"

                images = (
                    [f"data:image/png;base64,{result.base64_image}"]
                    if result.base64_image
                    else []
                )

                self.display_messages.append(
                    DisplayMessage(
                        id=str(uuid.uuid4()),
                        role="tool",
                        label=tool_display_name,
                        text=final_text,
                        images=images,
                    )
                )

                # Log tool execution
                self.logger.log_event(
                    event_type="tool_executed" if not result.error else "tool_failed",
                    level="INFO" if not result.error else "ERROR",
                    session_id=self.session_id,
                    data={
                        "tool_id": tool_id,
                        "has_output": result.output is not None,
                        "has_error": result.error is not None,
                        "has_image": result.base64_image is not None,
                        "output_length": len(result.output) if result.output else 0,
                    },
                )

                # Send real-time update via WebSocket/SSE
                # Schedule on main event loop (thread-safe)
                loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self._broadcast_sse_update())
                )

            def api_response_callback(
                request: httpx.Request,
                response: httpx.Response | object | None,
                error: Exception | None,
            ):
                # Surface API failures to the UI as pseudo tool messages.
                if error:
                    self.display_messages.append(
                        DisplayMessage(
                            id=str(uuid.uuid4()),
                            role="assistant",
                            label="API Error",
                            text=str(error),
                        )
                    )
                    # Log API error
                    self.logger.log_error(
                        session_id=self.session_id,
                        error=error,
                        context={
                            "request_url": str(request.url) if request else None,
                            "request_method": request.method if request else None,
                        },
                    )

            # Run sampling_loop in thread pool to avoid blocking web server
            # This allows dashboard to stay responsive during agent execution
            loop = asyncio.get_event_loop()

            def run_sampling_loop_sync():
                """Run sampling_loop in a new event loop in thread."""
                return asyncio.run(sampling_loop(
                    model=self.model,
                    provider=APIProvider.ANTHROPIC,
                    system_prompt_suffix=self.system_prompt_suffix,
                    messages=self.messages,
                    output_callback=output_callback,
                    tool_output_callback=tool_output_callback,
                    api_response_callback=api_response_callback,
                    api_key=self.api_key,
                    only_n_most_recent_images=self.only_n_images,
                    max_tokens=self.max_tokens,
                    tool_version=self.tool_version,
                    thinking_budget=self.thinking_budget,
                    stop_flag=lambda: self._stop_requested,
                ))

            # Get thread pool executor from app state
            from fastapi import Request
            executor = app.state.agent_executor if hasattr(app.state, 'agent_executor') else None

            if executor:
                # Run in thread pool - dashboard stays responsive!
                # Note: Once started, executor tasks can't be cancelled mid-execution
                # but we can at least track it and prevent double-execution
                self._executor_future = loop.run_in_executor(executor, run_sampling_loop_sync)
                updated_messages = await self._executor_future
            else:
                # Fallback to direct await (old behavior)
                updated_messages = await sampling_loop(
                    model=self.model,
                    provider=APIProvider.ANTHROPIC,
                    system_prompt_suffix=self.system_prompt_suffix,
                    messages=self.messages,
                    output_callback=output_callback,
                    tool_output_callback=tool_output_callback,
                    api_response_callback=api_response_callback,
                    api_key=self.api_key,
                    only_n_most_recent_images=self.only_n_images,
                    max_tokens=self.max_tokens,
                    tool_version=self.tool_version,
                    thinking_budget=self.thinking_budget,
                    stop_flag=lambda: self._stop_requested,
                )

            self.messages = updated_messages

            assistant_text = "".join(self._pending_assistant_chunks).strip()
            self._pending_assistant_chunks.clear()
            if assistant_text:
                self.display_messages.append(
                    DisplayMessage(
                        id=str(uuid.uuid4()),
                        role="assistant",
                        label="Proto",
                        text=assistant_text,
                    )
                )

        finally:
            async with self._lock:
                self._busy = False
            # Final update when agent finishes - send multiple times to ensure delivery
            for _ in range(3):
                await self._broadcast_sse_update()
                await asyncio.sleep(0.1)

    async def _broadcast_sse_update(self):
        """Broadcast current state to all SSE and WebSocket connections."""
        data = self.serialize()

        # Broadcast to SSE
        for queue in self._sse_queues:
            try:
                await queue.put(data)
            except:
                pass  # Queue might be closed

        # Broadcast to WebSocket
        data_json = json.dumps(data)
        disconnected = []
        for ws in self._ws_connections:
            try:
                await ws.send_text(data_json)
            except:
                disconnected.append(ws)

        # Remove disconnected WebSockets
        for ws in disconnected:
            if ws in self._ws_connections:
                self._ws_connections.remove(ws)

    def save(self, sessions_dir: Path) -> None:
        """Save session to disk."""
        session_file = sessions_dir / f"{self.session_id}.pkl"
        with open(session_file, "wb") as f:
            pickle.dump({
                "session_id": self.session_id,
                "messages": self.messages,
                "display_messages": self.display_messages,
                "created_at": self.created_at,
                "last_active": self.last_active,
                "model": self.model,
                "tool_version": self.tool_version,
            }, f)

        # Also save as JSON for easy access by agents
        try:
            # Save to default Proto folder as requested
            # Use ProjectManager.PLANNING_ROOT (~/Proto)
            from .planning import ProjectManager
            proto_root = ProjectManager.PLANNING_ROOT
            log_dir = proto_root / "logs" / "conversations"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            json_file = log_dir / f"{self.session_id}.json"
            
            # Use serializer but we might need to be careful about strict JSON compliance
            # serialize() returns dict with datetimes as strings, which is good.
            data = self.serialize()
            
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            # Don't fail the main save if logging fails
            print(f"Failed to save JSON log: {e}")

    @classmethod
    def load(cls, session_id: str, sessions_dir: Path, api_key: str) -> "ChatSession":
        """Load session from disk."""
        session_file = sessions_dir / f"{session_id}.pkl"
        with open(session_file, "rb") as f:
            data = pickle.load(f)

        session = cls(api_key=api_key, model=data["model"], tool_version=data["tool_version"])
        session.session_id = data["session_id"]

        # Clean up messages to remove incomplete tool_use/tool_result pairs
        session.messages = cls._clean_messages(data["messages"])

        session.display_messages = data["display_messages"]
        session.created_at = data["created_at"]
        session.last_active = data["last_active"]
        return session

    @staticmethod
    def _clean_messages(messages: list[BetaMessageParam]) -> list[BetaMessageParam]:
        """Remove incomplete tool_use/tool_result pairs from messages.

        The official sampling loop requires that every tool_use block has a corresponding
        tool_result in the next user message. This cleans up any interrupted sessions.
        """
        if not messages:
            return messages

        # Check if the last message is an assistant message with tool_use blocks
        if messages and messages[-1]["role"] == "assistant":
            last_content = messages[-1]["content"]
            if isinstance(last_content, list):
                has_tool_use = any(
                    isinstance(block, dict) and block.get("type") == "tool_use"
                    for block in last_content
                )
                if has_tool_use:
                    # Remove the incomplete assistant message with tool_use
                    # This happens when the agent was stopped mid-execution
                    messages = messages[:-1]

        return messages

    def serialize(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "toolVersion": self.tool_version,
            "running": self._busy,
            "sessionId": self.session_id,
            "createdAt": self.created_at.isoformat(),
            "lastActive": self.last_active.isoformat(),
            "agentSdk": {
                "enabled": True,
                "verification": self.enable_verification,
                "ceoAgent": self.use_ceo_agent,
                "stats": self.session_stats,
            },
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "label": msg.label,
                    "text": msg.text,
                    "images": msg.images,
                }
                for msg in self.display_messages
            ],
        }


class SendRequest(BaseModel):
    message: str


app = FastAPI(title="Proto AI Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for React app - MUST be before other routes
static_path = Path(__file__).parent.parent / "static"
if static_path.exists() and (static_path / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(static_path / "assets")), name="static_assets")


# Middleware to ensure event loop responsiveness
@app.middleware("http")
async def ensure_responsive_middleware(request: Request, call_next):
    """
    Middleware to ensure dashboard stays responsive during agent execution.
    Yields control to event loop before processing dashboard requests.
    """
    # For dashboard API requests, ensure event loop processes other tasks first
    if request.url.path.startswith("/api/dashboard"):
        await asyncio.sleep(0)  # Yield to event loop

    response = await call_next(request)
    return response


SESSIONS_DIR = Path.home() / ".claude" / "webui_sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    # Create thread pool executor for agent work
    # This runs blocking agent operations in separate thread
    # so web server stays responsive
    import concurrent.futures
    app.state.agent_executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=4,  # Allow up to 4 concurrent agent sessions
        thread_name_prefix="agent_worker"
    )

    # Log server startup
    logger = get_logger()
    logger.log_event(
        event_type="server_started",
        data={
            "default_model": DEFAULT_MODEL,
            "default_tool_version": DEFAULT_TOOL_VERSION,
        },
    )

    api_key = _resolve_api_key()
    app.state.api_key = api_key
    app.state.sessions: dict[str, ChatSession] = {}
    app.state.current_session_id: str | None = None

    # Create a default session
    session = ChatSession(api_key=api_key)
    app.state.sessions[session.session_id] = session
    app.state.current_session_id = session.session_id


@app.get("/", response_class=HTMLResponse)
async def home_page():
    """Serve React app or fallback to old UI."""
    static_index = Path(__file__).parent.parent / "static" / "index.html"
    if static_index.exists():
        return FileResponse(static_index)
    # Fallback to old UI if React build doesn't exist
    return HTMLResponse(content=_html_shell(), status_code=200)


def _get_current_session() -> ChatSession:
    """Get the current active session."""
    session_id = app.state.current_session_id
    if not session_id or session_id not in app.state.sessions:
        raise HTTPException(status_code=404, detail="No active session")
    return app.state.sessions[session_id]


@app.get("/api/messages")
async def get_state():
    session = _get_current_session()
    return JSONResponse(session.serialize())


@app.post("/api/messages")
async def send_message(payload: SendRequest):
    session = _get_current_session()
    # Start processing in background - don't wait for completion
    task = asyncio.create_task(session.send(payload.message))
    session._current_task = task
    # Save session after sending message
    session.save(SESSIONS_DIR)
    # Return immediately with current state
    return JSONResponse(session.serialize())


@app.post("/api/stop")
async def stop_agent():
    """Stop the currently running agent."""
    session = _get_current_session()
    await session.stop(reason="user_initiated")
    session.save(SESSIONS_DIR)
    return JSONResponse({"status": "stopped"})


@app.get("/api/sessions")
async def list_sessions():
    """List all available sessions."""
    sessions = []
    for session_id, session in app.state.sessions.items():
        sessions.append({
            "id": session_id,
            "createdAt": session.created_at.isoformat(),
            "lastActive": session.last_active.isoformat(),
            "messageCount": len(session.display_messages),
            "isCurrent": session_id == app.state.current_session_id,
        })

    # Also check for saved sessions on disk
    for session_file in SESSIONS_DIR.glob("*.pkl"):
        session_id = session_file.stem
        if session_id not in app.state.sessions:
            try:
                with open(session_file, "rb") as f:
                    data = pickle.load(f)
                sessions.append({
                    "id": session_id,
                    "createdAt": data["created_at"].isoformat(),
                    "lastActive": data["last_active"].isoformat(),
                    "messageCount": len(data["display_messages"]),
                    "isCurrent": False,
                })
            except:
                pass

    # Sort by last active
    sessions.sort(key=lambda x: x["lastActive"], reverse=True)
    return JSONResponse(sessions)


@app.post("/api/sessions/new")
async def create_new_session():
    """Create a new session."""
    session = ChatSession(api_key=app.state.api_key)
    app.state.sessions[session.session_id] = session
    app.state.current_session_id = session.session_id
    session.save(SESSIONS_DIR)
    return JSONResponse(session.serialize())


@app.post("/api/sessions/{session_id}/switch")
async def switch_session(session_id: str):
    """Switch to a different session."""
    # Try to load from memory first
    if session_id in app.state.sessions:
        app.state.current_session_id = session_id
        return JSONResponse(app.state.sessions[session_id].serialize())

    # Try to load from disk
    try:
        session = ChatSession.load(session_id, SESSIONS_DIR, app.state.api_key)
        app.state.sessions[session_id] = session
        app.state.current_session_id = session_id
        return JSONResponse(session.serialize())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    # Remove from memory
    if session_id in app.state.sessions:
        del app.state.sessions[session_id]

    # Remove from disk
    session_file = SESSIONS_DIR / f"{session_id}.pkl"
    if session_file.exists():
        session_file.unlink()

    # If we deleted the current session, switch to another one
    if app.state.current_session_id == session_id:
        if app.state.sessions:
            app.state.current_session_id = next(iter(app.state.sessions.keys()))
        else:
            # Create a new session if none exist
            session = ChatSession(api_key=app.state.api_key)
            app.state.sessions[session.session_id] = session
            app.state.current_session_id = session.session_id

    return JSONResponse({"status": "deleted"})


@app.get("/api/stream")
async def stream_updates(request: Request):
    """Server-Sent Events endpoint for real-time updates."""
    session = _get_current_session()
    queue: asyncio.Queue = asyncio.Queue()
    session._sse_queues.append(queue)

    async def event_generator():
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                try:
                    # Wait for updates with timeout
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    # Send as JSON
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield ": keepalive\n\n"
        finally:
            # Clean up queue when client disconnects
            if queue in session._sse_queues:
                session._sse_queues.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    session = _get_current_session()
    session._ws_connections.append(websocket)

    try:
        # Send initial state
        initial_data = session.serialize()
        await websocket.send_text(json.dumps(initial_data))

        # Keep connection alive and listen for close
        while True:
            # Wait for messages (mostly just to detect disconnect)
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    except Exception:
        pass  # Connection closed
    finally:
        # Clean up
        if websocket in session._ws_connections:
            session._ws_connections.remove(websocket)


# Dashboard API Endpoints
@app.get("/api/dashboard/projects")
async def get_projects():
    """Get all projects with task counts."""
    try:
        # Run blocking file I/O operations in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()

        def _get_projects_sync():
            project_manager = ProjectManager()
            projects_list = project_manager.list_projects()  # Returns list of metadata dicts

            result = []
            for project_meta in projects_list:
                project_name = project_meta["project_name"]
                project_path = project_manager.get_project_path(project_name)
                task_manager = project_manager.get_task_manager(project_name)

                # Get task counts by status
                all_tasks = task_manager.get_all_tasks()
                status_counts = {
                    "pending": 0,
                    "in_progress": 0,
                    "completed": 0,
                    "blocked": 0,
                    "cancelled": 0,
                }
                for task in all_tasks:
                    status_counts[task.status.value] = status_counts.get(task.status.value, 0) + 1

                result.append({
                    "name": project_name,
                    "path": str(project_path),
                    "totalTasks": len(all_tasks),
                    "statusCounts": status_counts,
                    "createdAt": project_meta.get("created_at"),
                    "updatedAt": project_meta.get("updated_at"),
                })
            return result

        # Run in thread pool so file I/O doesn't block the event loop
        result = await loop.run_in_executor(None, _get_projects_sync)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/projects/{project_name}")
async def get_project_details(project_name: str):
    """Get detailed project information including tasks in tree structure."""
    try:
        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _get_project_details_sync():
            project_manager = ProjectManager()

            # Check if project exists
            if not project_manager.project_exists(project_name):
                raise HTTPException(status_code=404, detail="Project not found")

            task_manager = project_manager.get_task_manager(project_name)

            # Get task tree structure
            task_tree = task_manager.get_task_tree()

            return {
                "name": project_name,
                "taskTree": task_tree,
            }

        result = await loop.run_in_executor(None, _get_project_details_sync)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/projects/{project_name}/docs")
async def get_project_documents(project_name: str):
    """Get planning documents for a project."""
    try:
        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _get_project_documents_sync():
            project_manager = ProjectManager()

            if not project_manager.project_exists(project_name):
                raise HTTPException(status_code=404, detail="Project not found")

            project_path = project_manager.get_project_path(project_name)
            docs_path = project_path / "documents"

            documents = []
            if docs_path.exists():
                for doc_file in docs_path.glob("*.md"):
                    with open(doc_file, "r") as f:
                        content = f.read()

                    documents.append({
                        "name": doc_file.stem,
                        "filename": doc_file.name,
                        "content": content,
                    })
            return documents

        documents = await loop.run_in_executor(None, _get_project_documents_sync)
        return JSONResponse(documents)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/tasks")
async def get_all_tasks():
    """Get all tasks across all projects."""
    try:
        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _get_all_tasks_sync():
            project_manager = ProjectManager()
            projects = project_manager.list_projects()  # Returns list of metadata dicts

            all_tasks = []
            for project_meta in projects:
                project_name = project_meta["project_name"]
                task_manager = project_manager.get_task_manager(project_name)
                tasks = task_manager.get_all_tasks()

                for task in tasks:
                    all_tasks.append({
                        "id": task.id,
                        "project": project_name,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "assignedAgent": task.assigned_agent,
                        "createdAt": task.created_at,
                        "updatedAt": task.updated_at,
                    })
            return all_tasks

        all_tasks = await loop.run_in_executor(None, _get_all_tasks_sync)
        return JSONResponse(all_tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/queue/status")
async def get_queue_status():
    """Get work queue status."""
    try:
        work_queue = WorkQueue()
        summary = work_queue.get_queue_summary()

        return JSONResponse({
            "total": summary["total"],
            "byStatus": summary["by_status"],
            "byPriority": summary["by_priority"],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/agents/status")
async def get_agents_status():
    """Get current status of all agents."""
    try:
        # For now, return active agents from current session
        # In future, this could track daemon orchestrator agent status
        session = _get_current_session()

        # Extract agent activity from messages
        agent_activity = []

        # Check if we have any agent messages or tool usage
        for msg in session.display_messages:
            if msg.role == "assistant":
                agent_activity.append({
                    "agent": "current-session-agent",
                    "status": "active" if session._busy else "idle",
                    "lastActivity": session.last_active.isoformat(),
                })
                break

        return JSONResponse(agent_activity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/projects/{project_name}/data")
async def get_project_data(project_name: str):
    """Get the aggregated project_data.json for a root project."""
    try:
        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _get_project_data_sync():
            project_manager = ProjectManager()
            task_manager = project_manager.get_task_manager(project_name)

            # Check if it's a FolderTaskManager
            from computer_use_demo.planning import FolderTaskManager
            if not isinstance(task_manager, FolderTaskManager):
                raise HTTPException(status_code=400, detail="Project does not use folder-based task system")

            # Get all root tasks (tasks with no parent)
            root_tasks = task_manager.get_root_tasks()

            if not root_tasks:
                return {"error": "No root tasks found"}

            # Get project_data.json from first root task
            root_task = root_tasks[0]
            folder_path = task_manager.task_folders.get(root_task.id)

            if not folder_path:
                raise HTTPException(status_code=404, detail="Project folder not found")

            project_json = folder_path / "project_data.json"

            if not project_json.exists():
                raise HTTPException(status_code=404, detail="project_data.json not found")

            import json
            with open(project_json, "r") as f:
                data = json.load(f)

            return data

        data = await loop.run_in_executor(None, _get_project_data_sync)
        return JSONResponse(data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/tasks/{task_id}/files")
async def get_task_files(task_id: str, project_name: str):
    """List files in task's files/ directory."""
    try:
        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _get_task_files_sync():
            project_manager = ProjectManager()
            task_manager = project_manager.get_task_manager(project_name)

            # Check if it's a FolderTaskManager
            from computer_use_demo.planning import FolderTaskManager
            if not isinstance(task_manager, FolderTaskManager):
                raise HTTPException(status_code=400, detail="Project does not use folder-based task system")

            files = task_manager.get_task_files(task_id)

            file_list = []
            for file_path in files:
                if file_path.is_file():
                    file_list.append({
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime,
                    })
            return file_list

        file_list = await loop.run_in_executor(None, _get_task_files_sync)
        return JSONResponse(file_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/tasks/{task_id}/files/{filename}")
async def download_task_file(task_id: str, filename: str, project_name: str):
    """Download a specific file from task's files/ directory."""
    try:
        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _get_file_path_sync():
            project_manager = ProjectManager()
            task_manager = project_manager.get_task_manager(project_name)

            # Check if it's a FolderTaskManager
            from computer_use_demo.planning import FolderTaskManager
            if not isinstance(task_manager, FolderTaskManager):
                raise HTTPException(status_code=400, detail="Project does not use folder-based task system")

            folder_path = task_manager.task_folders.get(task_id)
            if not folder_path:
                raise HTTPException(status_code=404, detail="Task not found")

            file_path = folder_path / "files" / filename

            if not file_path.exists() or not file_path.is_file():
                raise HTTPException(status_code=404, detail="File not found")

            return file_path

        file_path = await loop.run_in_executor(None, _get_file_path_sync)

        from starlette.responses import FileResponse
        return FileResponse(file_path, filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dashboard/tasks/{task_id}/files")
async def upload_task_file(task_id: str, project_name: str, file: UploadFile = File(...)):
    """Upload file to task's files/ directory."""
    try:
        # Read file content
        content = await file.read()

        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _upload_file_sync():
            project_manager = ProjectManager()
            task_manager = project_manager.get_task_manager(project_name)

            # Check if it's a FolderTaskManager
            from computer_use_demo.planning import FolderTaskManager
            if not isinstance(task_manager, FolderTaskManager):
                raise HTTPException(status_code=400, detail="Project does not use folder-based task system")

            # Add file to task
            file_path = task_manager.add_task_file(task_id, file.filename, content)

            if not file_path:
                raise HTTPException(status_code=404, detail="Task not found")

            return file_path

        file_path = await loop.run_in_executor(None, _upload_file_sync)

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "size": len(content),
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/tasks/{task_id}/notes")
async def get_task_notes(task_id: str, project_name: str):
    """Get task notes content."""
    try:
        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _get_task_notes_sync():
            project_manager = ProjectManager()
            task_manager = project_manager.get_task_manager(project_name)

            # Check if it's a FolderTaskManager
            from computer_use_demo.planning import FolderTaskManager
            if not isinstance(task_manager, FolderTaskManager):
                raise HTTPException(status_code=400, detail="Project does not use folder-based task system")

            notes = task_manager.get_task_notes(task_id)

            if notes is None:
                raise HTTPException(status_code=404, detail="Task not found")

            return notes

        notes = await loop.run_in_executor(None, _get_task_notes_sync)
        return JSONResponse({"content": notes})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dashboard/tasks/{task_id}/notes")
async def update_task_notes(task_id: str, project_name: str, content: str = Body(...)):
    """Update task notes."""
    try:
        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _update_task_notes_sync():
            project_manager = ProjectManager()
            task_manager = project_manager.get_task_manager(project_name)

            # Check if it's a FolderTaskManager
            from computer_use_demo.planning import FolderTaskManager
            if not isinstance(task_manager, FolderTaskManager):
                raise HTTPException(status_code=400, detail="Project does not use folder-based task system")

            success = task_manager.update_task_notes(task_id, content)

            if not success:
                raise HTTPException(status_code=404, detail="Task not found")

            return success

        success = await loop.run_in_executor(None, _update_task_notes_sync)
        return JSONResponse({"success": True})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dashboard/projects")
async def create_project(project_name: str = Body(...), description: str = Body(default="")):
    """Create a new project with proper folder structure."""
    try:
        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _create_project_sync():
            from pathlib import Path

            # Create project directory in .proto/planning/
            project_manager = ProjectManager()

            # Use ProjectManager's slugify method for consistency
            sanitized_name = project_manager.slugify_project_name(project_name)

            # Use base_path to get the planning root directory
            project_path = project_manager.base_path / sanitized_name

            if project_path.exists():
                raise HTTPException(status_code=400, detail=f"Project '{sanitized_name}' already exists")

            # Create project structure
            project_path.mkdir(parents=True, exist_ok=True)

            # Create tasks directory
            tasks_dir = project_path / "tasks"
            tasks_dir.mkdir(exist_ok=True)

            # Create docs directory for planning documents
            docs_dir = project_path / "docs"
            docs_dir.mkdir(exist_ok=True)

            # Create files directory for project files
            files_dir = project_path / "files"
            files_dir.mkdir(exist_ok=True)

            # Create README.md with project description
            readme_path = project_path / "README.md"
            readme_content = f"# {project_name}\n\n{description}\n\n## Project Structure\n\n- `tasks/`: Project tasks and subtasks\n- `docs/`: Planning documents\n- `files/`: Project files and resources\n"
            with open(readme_path, 'w') as f:
                f.write(readme_content)

            return {
                "name": sanitized_name,
                "path": str(project_path),
                "created": True
            }

        result = await loop.run_in_executor(None, _create_project_sync)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/history")
async def get_session_history():
    """Get list of previous sessions from logs."""
    try:
        loop = asyncio.get_event_loop()

        def _get_sessions_sync():
            import json
            from pathlib import Path
            from collections import defaultdict

            sessions_file = Path("logs/proto_sessions.jsonl")
            if not sessions_file.exists():
                return []

            # Parse sessions log
            sessions_data = defaultdict(dict)

            with open(sessions_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        session_id = entry.get('session_id')
                        event_type = entry.get('event_type')
                        timestamp = entry.get('timestamp')

                        # Only track webui sessions (not agent sessions)
                        if not session_id or not session_id.startswith('webui-'):
                            continue

                        if event_type == 'session_created':
                            sessions_data[session_id]['created_at'] = timestamp
                            sessions_data[session_id]['id'] = session_id
                        elif event_type == 'message_sent':
                            # Store first user message as preview
                            data = entry.get('data', {})
                            if data.get('role') == 'user' and 'preview' not in sessions_data[session_id]:
                                message = data.get('message', '')
                                sessions_data[session_id]['preview'] = message[:100]
                    except:
                        continue

            # Convert to list and sort by timestamp
            # Only include sessions that have messages (have a preview)
            sessions_list = [
                {
                    'id': data.get('id', ''),
                    'timestamp': data.get('created_at', ''),
                    'preview': data.get('preview', '')
                }
                for data in sessions_data.values()
                if 'created_at' in data and 'preview' in data
            ]

            # Sort by timestamp descending (newest first)
            sessions_list.sort(key=lambda x: x['timestamp'], reverse=True)

            # Return last 50 sessions
            return sessions_list[:50]

        result = await loop.run_in_executor(None, _get_sessions_sync)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get all messages for a specific session."""
    try:
        loop = asyncio.get_event_loop()

        def _get_messages_sync():
            import json
            from pathlib import Path

            sessions_file = Path("logs/proto_sessions.jsonl")
            if not sessions_file.exists():
                return []

            messages = []

            with open(sessions_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get('session_id') != session_id:
                            continue

                        event_type = entry.get('event_type')
                        data = entry.get('data', {})
                        timestamp = entry.get('timestamp', '')

                        if event_type == 'message_sent':
                            role = data.get('role', 'user')
                            message = data.get('message', '')
                            if message:
                                messages.append({
                                    'role': role,
                                    'content': message,
                                    'timestamp': timestamp
                                })
                        elif event_type == 'assistant_response':
                            content = data.get('content', '') or data.get('response', '')
                            if content:
                                messages.append({
                                    'role': 'assistant',
                                    'content': content,
                                    'timestamp': timestamp
                                })
                        elif event_type == 'tool_use':
                            tool_name = data.get('tool_name', 'Tool')
                            tool_input = data.get('input', '')
                            messages.append({
                                'role': 'assistant',
                                'content': f"🔧 {tool_name}\n{str(tool_input)[:200]}",
                                'timestamp': timestamp
                            })
                    except:
                        continue

            return messages

        result = await loop.run_in_executor(None, _get_messages_sync)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/open-in-finder")
async def open_in_finder(request: Request):
    """Open a file or folder in Finder."""
    try:
        data = await request.json()
        path = data.get('path', '')

        if not path:
            raise HTTPException(status_code=400, detail="Path required")

        import subprocess
        from pathlib import Path

        base_path = Path(".proto/planning").resolve()

        # Handle both absolute and relative paths
        if path.startswith('/'):
            # Absolute path - allow any valid path on the system
            full_path = Path(path)
        else:
            full_path = base_path / path

        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        # Use macOS 'open' command to open in Finder
        subprocess.run(['open', str(full_path)], check=True)

        return JSONResponse({"success": True})
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to open: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/folder")
async def get_folder_contents(path: str):
    """Get contents of a folder (subfolders and files)."""
    try:
        # Run blocking file I/O operations in thread pool
        loop = asyncio.get_event_loop()

        def _get_folder_contents_sync():
            from pathlib import Path

            base_path = Path(".proto/planning").resolve()

            # Handle both absolute and relative paths
            if path.startswith('/'):
                folder_path = Path(path)
                # Ensure it's within the base path for security
                try:
                    folder_path.relative_to(base_path)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Path must be within .proto/planning")
            else:
                folder_path = base_path / path

            if not folder_path.exists() or not folder_path.is_dir():
                raise HTTPException(status_code=404, detail="Folder not found")

            # List subfolders and files
            folders = []
            files = []

            for item in sorted(folder_path.iterdir()):
                if item.is_dir():
                    # Count children
                    try:
                        child_count = len(list(item.iterdir()))
                    except:
                        child_count = 0

                    folders.append({
                        "name": item.name,
                        "path": str(item.relative_to(base_path)),
                        "type": "folder",
                        "children_count": child_count
                    })
                else:
                    # Get file info
                    stat = item.stat()
                    files.append({
                        "name": item.name,
                        "type": item.suffix[1:] if item.suffix else "file",
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })

            return {
                "path": path,
                "folders": folders,
                "files": files
            }

        result = await loop.run_in_executor(None, _get_folder_contents_sync)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/file")
async def get_file_contents(path: str):
    """Get contents of a file."""
    try:
        loop = asyncio.get_event_loop()

        def _get_file_contents_sync():
            from pathlib import Path

            base_path = Path(".proto/planning").resolve()

            # Handle both absolute and relative paths
            if path.startswith('/'):
                file_path = Path(path)
                # Ensure it's within the base path for security
                try:
                    file_path.relative_to(base_path)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Path must be within .proto/planning")
            else:
                file_path = base_path / path

            if not file_path.exists() or not file_path.is_file():
                raise HTTPException(status_code=404, detail="File not found")

            # Read file contents with size limit (1MB max)
            max_size = 1024 * 1024
            stat = file_path.stat()
            if stat.st_size > max_size:
                raise HTTPException(status_code=413, detail="File too large (max 1MB)")

            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                raise HTTPException(status_code=415, detail="File is not a text file")

            # Determine file type
            ext = file_path.suffix[1:].lower() if file_path.suffix else 'text'

            return {
                "path": str(file_path),
                "name": file_path.name,
                "type": ext,
                "content": content,
                "size": stat.st_size,
                "modified": stat.st_mtime
            }

        result = await loop.run_in_executor(None, _get_file_contents_sync)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/config")
async def get_dashboard_config():
    """Get dashboard configuration including default paths."""
    from .planning import ProjectManager
    return {
        "defaultProjectPath": str(ProjectManager.PLANNING_ROOT)
    }


@app.get("/api/browse/folder")
async def browse_folder(path: str):
    """Browse any folder on the filesystem."""
    try:
        loop = asyncio.get_event_loop()

        def _browse_folder_sync():
            from pathlib import Path

            folder_path = Path(path).resolve()

            if not folder_path.exists():
                raise HTTPException(status_code=404, detail="Folder not found")
            if not folder_path.is_dir():
                raise HTTPException(status_code=400, detail="Path is not a folder")

            folders = []
            files = []

            try:
                for item in sorted(folder_path.iterdir()):
                    # Skip hidden files
                    if item.name.startswith('.'):
                        continue
                    try:
                        if item.is_dir():
                            try:
                                child_count = len([x for x in item.iterdir() if not x.name.startswith('.')])
                            except:
                                child_count = 0

                            folders.append({
                                "name": item.name,
                                "path": str(item),
                                "type": "folder",
                                "children_count": child_count
                            })
                        else:
                            stat = item.stat()
                            files.append({
                                "name": item.name,
                                "type": item.suffix[1:] if item.suffix else "file",
                                "size": stat.st_size,
                                "modified": stat.st_mtime
                            })
                    except (PermissionError, OSError):
                        # Skip files we can't access
                        continue
            except PermissionError:
                raise HTTPException(status_code=403, detail="Permission denied")

            return {
                "path": str(folder_path),
                "folders": folders,
                "files": files
            }

        result = await loop.run_in_executor(None, _browse_folder_sync)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/browse/file")
async def browse_file(path: str):
    """Read any file from the filesystem."""
    try:
        loop = asyncio.get_event_loop()

        def _browse_file_sync():
            from pathlib import Path

            file_path = Path(path).resolve()

            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            if not file_path.is_file():
                raise HTTPException(status_code=400, detail="Path is not a file")

            # Read file contents with size limit (1MB max)
            max_size = 1024 * 1024
            stat = file_path.stat()
            if stat.st_size > max_size:
                raise HTTPException(status_code=413, detail="File too large (max 1MB)")

            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                raise HTTPException(status_code=415, detail="File is not a text file")
            except PermissionError:
                raise HTTPException(status_code=403, detail="Permission denied")

            ext = file_path.suffix[1:].lower() if file_path.suffix else 'text'

            return {
                "path": str(file_path),
                "name": file_path.name,
                "type": ext,
                "content": content,
                "size": stat.st_size,
                "modified": stat.st_mtime
            }

        result = await loop.run_in_executor(None, _browse_file_sync)
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/browse/pick-folder")
async def pick_folder():
    """Open native macOS file/folder picker dialog and return selected path."""
    import subprocess
    try:
        # Get default projects path
        default_path = str(Path.home() / "Proto")

        # Use Python/objc to open NSOpenPanel that allows both files and folders
        script = f'''
import objc
from Foundation import NSURL
from AppKit import NSOpenPanel, NSApp, NSApplication

# Initialize the app if needed
NSApplication.sharedApplication()

panel = NSOpenPanel.openPanel()
panel.setCanChooseFiles_(True)
panel.setCanChooseDirectories_(True)
panel.setAllowsMultipleSelection_(False)
panel.setPrompt_("Add")
panel.setMessage_("Select a file or folder to add to Explorer")

# Set default directory
default_url = NSURL.fileURLWithPath_("{default_path}")
panel.setDirectoryURL_(default_url)

# Run the panel
result = panel.runModal()

if result == 1:  # NSModalResponseOK
    url = panel.URLs()[0]
    print(url.path())
else:
    print("CANCELLED")
'''
        result = subprocess.run(
            ['python3', '-c', script],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout for user to select
        )

        output = result.stdout.strip()

        if result.returncode != 0 or output == "CANCELLED" or not output:
            return JSONResponse({"path": None, "cancelled": True})

        selected_path = output
        if selected_path.endswith('/'):
            selected_path = selected_path[:-1]  # Remove trailing slash

        # Determine if it's a file or folder
        import os
        is_dir = os.path.isdir(selected_path)
        path_type = "folder" if is_dir else "file"

        return JSONResponse({"path": selected_path, "cancelled": False, "type": path_type})
    except subprocess.TimeoutExpired:
        return JSONResponse({"path": None, "cancelled": True, "error": "Timeout"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/browse/pick-file")
async def pick_file():
    """Open native macOS file picker dialog and return selected path."""
    import subprocess
    try:
        # Use AppleScript to open native file picker
        script = '''
        tell application "System Events"
            activate
        end tell
        set selectedFile to choose file with prompt "Select a file to add to Explorer"
        return POSIX path of selectedFile
        '''
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout for user to select
        )

        if result.returncode != 0:
            # User cancelled or error
            return JSONResponse({"path": None, "cancelled": True})

        selected_path = result.stdout.strip()

        return JSONResponse({"path": selected_path, "cancelled": False})
    except subprocess.TimeoutExpired:
        return JSONResponse({"path": None, "cancelled": True, "error": "Timeout"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/tree")
async def get_agent_tree():
    """Get the complete organizational tree of all specialist agents."""
    from .agent_org_structure import COMPANY_ORG_STRUCTURE
    return JSONResponse({"departments": COMPANY_ORG_STRUCTURE})


@app.get("/api/agents/{agent_id}")
async def get_agent_info(agent_id: str):
    """Get detailed information about a specific agent."""
    from .agent_org_structure import get_agent_by_id, get_department_for_agent

    agent = get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    department = get_department_for_agent(agent_id)

    return JSONResponse({
        "agent": agent,
        "department": department
    })


@app.post("/api/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, payload: SendRequest):
    """Start a chat session with a specific specialist agent."""
    try:
        from .agent_org_structure import get_agent_by_id

        # Validate agent exists
        agent = get_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        # Use the ChatSession.send() approach for all agents
        session = _get_current_session()

        # Start processing in background - don't wait for completion
        task = asyncio.create_task(session.send(payload.message))
        session._current_task = task

        # Save session after sending message
        session.save(SESSIONS_DIR)

        # Return immediately with current state
        return JSONResponse(session.serialize())

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def _html_shell() -> str:
    """Single-page dark UI with vanilla JS for chat interactions."""
    css = """
    :root {
        --bg-main: #111b21;
        --bg-sidebar: #111b21;
        --bg-chat: #0b141a;
        --bg-panel-header: #202c33;
        --bg-message-in: #202c33;
        --bg-message-out: #005c4b;
        --bg-input: #2a3942;
        --text-primary: #e9edef;
        --text-secondary: #8696a0;
        --border: #2a3942;
        --accent: #00a884;
        --hover: #2a3942;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Helvetica Neue, Helvetica, Arial, sans-serif;
        background: var(--bg-main);
        color: var(--text-primary);
        overflow: hidden;
    }
    #app { display: flex; height: 100vh; }

    /* Sidebar Drawer */
    #sidebar {
        width: 400px;
        background: var(--bg-sidebar);
        border-right: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        position: fixed;
        left: -400px;
        top: 0;
        bottom: 0;
        transition: left 0.3s ease;
        z-index: 1000;
        box-shadow: 2px 0 10px rgba(0,0,0,0.3);
    }
    #sidebar.open {
        left: 0;
    }
    #sidebar-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 999;
    }
    #sidebar-overlay.show {
        display: block;
    }
    #sidebar-header {
        background: var(--bg-panel-header);
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 60px;
    }
    #sidebar-header h1 { font-size: 16px; font-weight: 500; color: var(--text-primary); }
    .header-icons { display: flex; gap: 20px; align-items: center; }
    .icon-btn {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 8px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
    }
    .icon-btn:hover { background: var(--hover); }
    .icon-btn.new-chat { color: var(--text-primary); }
    .icon-btn.new-chat-header {
        color: var(--text-primary);
        padding: 8px;
        border-radius: 50%;
    }
    .icon-btn.new-chat-header:hover {
        background: var(--hover);
    }
    .icon-btn.stop-btn { color: #ea4335; }

    /* Search */
    #search-container { padding: 8px 12px; background: var(--bg-sidebar); }
    #search-input {
        width: 100%;
        background: var(--bg-panel-header);
        border: none;
        border-radius: 8px;
        padding: 8px 12px 8px 52px;
        color: var(--text-primary);
        font-size: 14px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="%238696a0" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>');
        background-repeat: no-repeat;
        background-position: 12px center;
        background-size: 20px;
    }
    #search-input::placeholder { color: var(--text-secondary); }

    /* Sessions List */
    #sessions-list { flex: 1; overflow-y: auto; background: var(--bg-sidebar); }
    .session-item {
        padding: 12px 16px;
        border-bottom: 1px solid var(--border);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: background 0.2s;
    }
    .session-item:hover { background: var(--hover); }
    .session-item.active { background: var(--bg-panel-header); }
    .session-avatar {
        width: 49px;
        height: 49px;
        border-radius: 50%;
        background: var(--accent);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 20px;
        color: #fff;
    }
    .session-info { flex: 1; min-width: 0; }
    .session-header { display: flex; justify-content: space-between; margin-bottom: 3px; }
    .session-name { font-size: 16px; color: var(--text-primary); font-weight: 400; }
    .session-time { font-size: 12px; color: var(--text-secondary); }
    .session-preview {
        font-size: 14px;
        color: var(--text-secondary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Chat Area */
    #chat-area {
        flex: 1;
        display: flex;
        flex-direction: column;
        background: var(--bg-chat);
        position: relative;
    }

    /* Geometric Background */
    #chat-area::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            /* Circles */
            radial-gradient(circle at 15% 20%, rgba(0, 168, 132, 0.08) 0%, transparent 15%),
            radial-gradient(circle at 85% 80%, rgba(0, 168, 132, 0.08) 0%, transparent 15%),
            radial-gradient(circle at 70% 30%, rgba(0, 168, 132, 0.06) 0%, transparent 12%),
            radial-gradient(circle at 30% 70%, rgba(0, 168, 132, 0.06) 0%, transparent 12%),
            /* Diagonal lines */
            repeating-linear-gradient(45deg, transparent, transparent 60px, rgba(0, 168, 132, 0.04) 60px, rgba(0, 168, 132, 0.04) 62px),
            repeating-linear-gradient(-45deg, transparent, transparent 60px, rgba(0, 168, 132, 0.04) 60px, rgba(0, 168, 132, 0.04) 62px),
            /* Grid pattern */
            repeating-linear-gradient(0deg, transparent, transparent 100px, rgba(0, 168, 132, 0.02) 100px, rgba(0, 168, 132, 0.02) 101px),
            repeating-linear-gradient(90deg, transparent, transparent 100px, rgba(0, 168, 132, 0.02) 100px, rgba(0, 168, 132, 0.02) 101px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
        opacity: 1;
        pointer-events: none;
        z-index: 0;
    }
    #chat-header {
        background: var(--bg-panel-header);
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 60px;
        border-bottom: 1px solid var(--border);
        position: relative;
        z-index: 1;
    }
    .chat-title { display: flex; align-items: center; gap: 12px; }
    #menu-toggle {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 8px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
    }
    #menu-toggle:hover { background: var(--hover); }
    .chat-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--accent);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        color: #fff;
    }
    .chat-info h2 { font-size: 16px; font-weight: 400; color: var(--text-primary); }
    .chat-status { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }
    .header-actions {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .badge {
        font-size: 11px;
        padding: 4px 8px;
        border-radius: 4px;
        background: rgba(0, 168, 132, 0.2);
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stop-btn-header {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: rgba(234, 67, 53, 0.1);
        color: #ea4335;
        border: 1px solid rgba(234, 67, 53, 0.3);
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stop-btn-header:hover {
        background: rgba(234, 67, 53, 0.2);
        border-color: rgba(234, 67, 53, 0.5);
    }

    .stop-btn-header svg {
        width: 16px;
        height: 16px;
    }

    /* Messages */
    #messages {
        flex: 1;
        padding: 20px 8%;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 8px;
        position: relative;
        z-index: 1;
    }
    .bubble {
        max-width: 65%;
        padding: 6px 7px 8px 9px;
        border-radius: 7.5px;
        position: relative;
        word-wrap: break-word;
        box-shadow: 0 1px 0.5px rgba(0,0,0,.13);
    }
    .bubble.user {
        background: var(--bg-message-out);
        align-self: flex-end;
        margin-left: auto;
    }
    .bubble.assistant, .bubble.tool { background: var(--bg-message-in); align-self: flex-start; }
    .bubble .label {
        font-size: 12px;
        color: rgba(233, 237, 239, 0.6);
        margin-bottom: 4px;
        font-weight: 500;
    }
    .bubble .text {
        font-size: 14.2px;
        line-height: 19px;
        color: var(--text-primary);
        white-space: pre-wrap;
    }
    .bubble .time {
        font-size: 11px;
        color: rgba(233, 237, 239, 0.45);
        margin-top: 4px;
        text-align: right;
    }
    img.tool-screenshot { margin-top: 8px; border-radius: 6px; max-width: 100%; max-height: 400px; }

    /* Typing Indicator */
    .typing-indicator {
        display: none;
        max-width: 65%;
        padding: 12px 16px;
        border-radius: 7.5px;
        background: var(--bg-message-in);
        align-self: flex-start;
        box-shadow: 0 1px 0.5px rgba(0,0,0,.13);
    }
    .typing-indicator.active { display: block; }
    .typing-dots { display: flex; gap: 4px; align-items: center; }
    .typing-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--text-secondary);
        animation: typing-bounce 1.4s infinite ease-in-out;
    }
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    @keyframes typing-bounce {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* Composer */
    #composer {
        padding: 10px 16px 20px;
        background: var(--bg-panel-header);
        border-top: 1px solid var(--border);
        position: relative;
        z-index: 1;
    }
    .composer-wrapper {
        background: var(--bg-input);
        border-radius: 8px;
        display: flex;
        align-items: flex-end;
        padding: 5px 10px;
        gap: 8px;
    }
    #prompt {
        flex: 1;
        background: none;
        border: none;
        color: var(--text-primary);
        font-size: 15px;
        padding: 10px;
        resize: none;
        max-height: 100px;
        overflow-y: auto;
        font-family: inherit;
    }
    #prompt::placeholder { color: var(--text-secondary); }
    #sendBtn {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.2s;
    }
    #sendBtn:not(:disabled) { color: var(--accent); }
    #sendBtn:not(:disabled):hover { background: rgba(0, 168, 132, 0.1); }
    #sendBtn:disabled { opacity: 0.4; cursor: not-allowed; }

    .stop-btn-composer {
        background: none;
        border: none;
        color: #ea4335;
        cursor: pointer;
        padding: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.2s;
    }
    .stop-btn-composer:hover {
        background: rgba(234, 67, 53, 0.1);
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(134, 150, 160, 0.3); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(134, 150, 160, 0.5); }

    /* Dashboard Panel */
    .dashboard-panel {
        width: 400px;
        background: var(--bg-sidebar);
        border-left: 1px solid var(--border);
        display: none;
        flex-direction: column;
        overflow-y: auto;
    }
    .dashboard-panel.open {
        display: flex;
    }
    .dashboard-header {
        padding: 20px;
        border-bottom: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--bg-panel-header);
    }
    .dashboard-header h2 {
        font-size: 18px;
        margin: 0;
        color: var(--text-primary);
    }
    .dashboard-content {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
    }
    .dashboard-section {
        margin-bottom: 24px;
    }
    .dashboard-section h3 {
        font-size: 14px;
        font-weight: 600;
        margin: 0 0 12px 0;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .queue-status, .projects-list, .tasks-list {
        background: var(--bg-message-in);
        border-radius: 8px;
        padding: 12px;
    }
    .queue-status .stat-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid var(--border);
    }
    .queue-status .stat-item:last-child {
        border-bottom: none;
    }
    .queue-status .stat-label {
        color: var(--text-secondary);
        font-size: 13px;
    }
    .queue-status .stat-value {
        color: var(--text-primary);
        font-weight: 600;
    }
    .project-item, .task-item {
        padding: 12px;
        margin-bottom: 8px;
        background: var(--bg-chat);
        border-radius: 6px;
        border: 1px solid var(--border);
    }
    .project-item:hover, .task-item:hover {
        background: var(--hover);
    }
    .project-name, .task-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
        font-size: 14px;
    }
    .project-stats, .task-meta {
        font-size: 12px;
        color: var(--text-secondary);
        display: flex;
        gap: 12px;
    }
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .status-pending { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
    .status-in_progress { background: rgba(33, 150, 243, 0.2); color: #2196f3; }
    .status-completed { background: rgba(76, 175, 80, 0.2); color: #4caf50; }
    .status-blocked { background: rgba(244, 67, 54, 0.2); color: #f44336; }
    .loading {
        text-align: center;
        padding: 20px;
        color: var(--text-secondary);
        font-size: 13px;
    }
    .header-actions {
        display: flex;
        gap: 8px;
    }

    /* Project Detail View */
    .project-detail-view {
        display: none;
        flex-direction: column;
        padding: 20px;
        overflow-y: auto;
    }
    .project-detail-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .project-detail-header h2 {
        font-size: 20px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    .back-btn {
        background: var(--bg-message-in);
        border: 1px solid var(--border);
        color: var(--text-primary);
        cursor: pointer;
        padding: 8px 12px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        transition: background 0.2s;
    }
    .back-btn:hover {
        background: var(--hover);
    }
    .project-detail-stats {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 24px;
        background: var(--bg-message-in);
        padding: 16px;
        border-radius: 8px;
    }
    .project-detail-stats .stat-item {
        text-align: center;
    }
    .project-detail-stats .stat-label {
        display: block;
        font-size: 11px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .project-detail-stats .stat-value {
        display: block;
        font-size: 24px;
        font-weight: 700;
        color: var(--text-primary);
    }
    .project-detail-tasks h3 {
        font-size: 14px;
        font-weight: 600;
        margin: 0 0 12px 0;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .tasks-detail-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .task-detail-item {
        background: var(--bg-message-in);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 16px;
    }
    .task-detail-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 8px;
    }
    .task-detail-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        flex: 1;
    }
    .task-detail-badges {
        display: flex;
        gap: 6px;
        flex-shrink: 0;
    }
    .priority-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .priority-low { background: rgba(156, 156, 156, 0.2); color: #9c9c9c; }
    .priority-medium { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
    .priority-high { background: rgba(255, 152, 0, 0.2); color: #ff9800; }
    .priority-critical { background: rgba(244, 67, 54, 0.2); color: #f44336; }
    .status-in-progress { background: rgba(33, 150, 243, 0.2); color: #2196f3; }
    .task-detail-description {
        font-size: 13px;
        color: var(--text-secondary);
        margin-bottom: 12px;
        line-height: 1.5;
    }
    .task-detail-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        font-size: 12px;
        color: var(--text-secondary);
        padding-top: 8px;
        border-top: 1px solid var(--border);
    }
    .task-detail-meta strong {
        color: var(--text-primary);
    }
    .task-detail-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }
    .task-tag {
        background: var(--bg-panel-header);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
    }

    /* Tree View Styles */
    .tasks-tree-view {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .tree-node {
        border: 1px solid var(--border);
        border-radius: 6px;
        background: var(--bg-message-in);
        padding: 12px;
    }
    .tree-node-header {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .tree-toggle {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: all 0.2s;
    }
    .tree-toggle:hover {
        background: var(--bg-panel-header);
        color: var(--text-primary);
    }
    .tree-toggle svg {
        transition: transform 0.2s;
        transform: rotate(90deg);
    }
    .tree-spacer {
        width: 28px;
        display: inline-block;
    }
    .tree-node-content {
        flex: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .tree-node-title {
        font-weight: 500;
        color: var(--text-primary);
    }
    .tree-node-badges {
        display: flex;
        gap: 6px;
    }
    .tree-node-description {
        margin-top: 8px;
        margin-left: 36px;
        color: var(--text-secondary);
        font-size: 13px;
    }
    .tree-node-children {
        margin-top: 8px;
        margin-left: 16px;
        border-left: 2px solid var(--border);
        padding-left: 12px;
    }
    .tree-node-children.collapsed {
        display: none;
    }
    """


    js = """
    const messagesEl = document.getElementById('messages');
    const form = document.getElementById('chat-form');
    const promptEl = document.getElementById('prompt');
    const sendBtn = document.getElementById('sendBtn');
    const statusEl = document.getElementById('status');
    const stopBtn = document.getElementById('stopBtn');
    const stopBtnComposer = document.getElementById('stopBtnComposer');
    const newSessionBtn = document.getElementById('newSessionBtn');
    const newSessionBtnSidebar = document.getElementById('newSessionBtnSidebar');

    let eventSource = null;
    let currentSessionId = null;
    let typingIndicator = null;
    let pollingInterval = null;

    // Create typing indicator element
    function createTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'typing-indicator';
        div.id = 'typing-indicator';
        div.innerHTML = `
            <div class="label">Proto</div>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        return div;
    }

    // Format date for session display
    function formatDate(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return date.toLocaleDateString();
    }

    // Load sessions list
    async function loadSessions() {
        try {
            const res = await fetch('/api/sessions');
            const sessions = await res.json();

            const list = document.getElementById('sessions-list');
            list.innerHTML = '';

            sessions.forEach(session => {
                const div = document.createElement('div');
                div.className = 'session-item' + (session.isCurrent ? ' active' : '');
                div.dataset.sessionId = session.id;
                div.innerHTML = `
                    <div class="session-avatar">C</div>
                    <div class="session-info">
                        <div class="session-header">
                            <div class="session-name">Session ${session.id.slice(-4)}</div>
                            <div class="session-time">${formatDate(session.lastActive)}</div>
                        </div>
                        <div class="session-preview">${session.messageCount} messages</div>
                    </div>
                `;
                div.addEventListener('click', async () => {
                    if (session.id === currentSessionId) return;
                    try {
                        const res = await fetch(`/api/sessions/${session.id}/switch`, { method: 'POST' });
                        const data = await res.json();
                        renderMessages(data.messages, true);
                        updateStatus(data.running);
                        currentSessionId = session.id;
                        await loadSessions(); // Refresh to update active state
                    } catch (e) {
                        console.error('Failed to switch session:', e);
                        alert('Failed to switch session');
                    }
                });
                if (session.isCurrent) {
                    currentSessionId = session.id;
                }
                list.appendChild(div);
            });
        } catch (e) {
            console.error('Failed to load sessions:', e);
        }
    }

    // New session (header)
    newSessionBtn.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/sessions/new', { method: 'POST' });
            const data = await res.json();
            currentSessionId = data.sessionId;
            await loadSessions();
            renderMessages([], true);
        } catch (e) {
            console.error('Failed to create session:', e);
            alert('Failed to create new session');
        }
    });

    // New session (sidebar)
    newSessionBtnSidebar.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/sessions/new', { method: 'POST' });
            const data = await res.json();
            currentSessionId = data.sessionId;
            await loadSessions();
            renderMessages([], true);
            // Close sidebar after creating new session
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.remove('open');
            document.getElementById('sidebar-overlay').classList.remove('show');
        } catch (e) {
            console.error('Failed to create session:', e);
            alert('Failed to create new session');
        }
    });

    // Stop button (sidebar)
    stopBtn.addEventListener('click', async () => {
        try {
            await fetch('/api/stop', { method: 'POST' });
        } catch (e) {
            console.error('Failed to stop agent:', e);
        }
    });

    // Stop button (composer)
    stopBtnComposer.addEventListener('click', async () => {
        try {
            await fetch('/api/stop', { method: 'POST' });
        } catch (e) {
            console.error('Failed to stop agent:', e);
        }
    });

    function connectSSE() {
        if (eventSource) {
            eventSource.close();
        }

        eventSource = new EventSource('/api/stream');

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                renderMessages(data.messages, true);
                updateStatus(data.running);
            } catch (e) {
                console.error('SSE parse error:', e);
            }
        };

        eventSource.onerror = (error) => {
            console.error('SSE error, reconnecting in 3s...', error);
            eventSource.close();
            setTimeout(connectSSE, 3000);
        };
    }

    async function refreshState(scrollToBottom=true) {
        const res = await fetch('/api/messages');
        const data = await res.json();
        renderMessages(data.messages, scrollToBottom);
        updateStatus(data.running);
    }

    function renderMessages(messages, scrollToBottom=true) {
        messagesEl.innerHTML = '';
        let lastBubble = null;
        messages.forEach(msg => {
            const bubble = document.createElement('div');
            bubble.className = `bubble ${msg.role}`;

            if (msg.label) {
                const label = document.createElement('div');
                label.className = 'label';
                label.textContent = msg.label;
                bubble.appendChild(label);
            }

            const text = document.createElement('div');
            text.className = 'text';
            text.textContent = msg.text;
            bubble.appendChild(text);

            (msg.images || []).forEach(src => {
                const img = document.createElement('img');
                img.src = src;
                img.className = 'tool-screenshot';
                img.addEventListener('load', () => scrollMessagesToBottom(bubble));
                img.addEventListener('error', () => scrollMessagesToBottom(bubble));
                bubble.appendChild(img);
            });

            messagesEl.appendChild(bubble);
            lastBubble = bubble;
        });
        if (scrollToBottom && lastBubble) {
            scrollMessagesToBottom(lastBubble);
            setTimeout(() => scrollMessagesToBottom(lastBubble), 200);
        }
    }

    function scrollMessagesToBottom(target=null) {
        const el = target || messagesEl.lastElementChild;
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'end' });
        } else {
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }
    }

    function updateStatus(running) {
        statusEl.textContent = running ? 'Thinking...' : '';
        promptEl.disabled = running;

        // Toggle between send and stop button in composer
        sendBtn.style.display = running ? 'none' : 'flex';
        stopBtnComposer.style.display = running ? 'flex' : 'none';

        // Sidebar stop button (keep for convenience)
        stopBtn.style.display = running ? 'flex' : 'none';

        // Start/stop polling fallback
        if (running && !pollingInterval) {
            // Poll every 2 seconds while running as fallback if SSE fails
            pollingInterval = setInterval(refreshState, 2000);
        } else if (!running && pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }

        // Show/hide typing indicator
        if (!typingIndicator) {
            typingIndicator = createTypingIndicator();
        }

        const existingIndicator = document.getElementById('typing-indicator');
        if (running) {
            if (!existingIndicator) {
                messagesEl.appendChild(typingIndicator);
                typingIndicator.classList.add('active');
                scrollMessagesToBottom(typingIndicator);
            }
        } else {
            if (existingIndicator) {
                existingIndicator.remove();
            }
            promptEl.focus();
        }
    }

    form.addEventListener('submit', async (evt) => {
        evt.preventDefault();
        const message = promptEl.value.trim();
        if (!message) return;

        promptEl.value = '';
        updateStatus(true);

        const res = await fetch('/api/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        if (!res.ok) {
            const error = await res.json();
            alert(error.detail || 'Failed to send message.');
            updateStatus(false);
        }
        // SSE will handle updates automatically, no need to wait for response
    });

    // Initial state load
    refreshState(true);

    // Connect to SSE for real-time updates
    connectSSE();

    // Load sessions on page load
    loadSessions();

    // Refresh sessions list every 5 seconds
    setInterval(loadSessions, 5000);

    // Drawer toggle functionality
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    function toggleDrawer() {
        sidebar.classList.toggle('open');
        sidebarOverlay.classList.toggle('show');
    }

    menuToggle.addEventListener('click', toggleDrawer);
    sidebarOverlay.addEventListener('click', toggleDrawer);

    // Dashboard functionality
    const dashboardPanel = document.getElementById('dashboard-panel');
    const toggleDashboardBtn = document.getElementById('toggleDashboardBtn');
    const closeDashboardBtn = document.getElementById('closeDashboardBtn');

    function toggleDashboard() {
        dashboardPanel.classList.toggle('open');
        if (dashboardPanel.classList.contains('open')) {
            loadDashboardData();
        }
    }

    toggleDashboardBtn.addEventListener('click', toggleDashboard);
    closeDashboardBtn.addEventListener('click', toggleDashboard);

    // Load dashboard data
    async function loadDashboardData() {
        await Promise.all([
            loadQueueStatus(),
            loadProjects(),
            loadTasks()
        ]);
    }

    async function loadQueueStatus() {
        try {
            const res = await fetch('/api/dashboard/queue/status');
            const data = await res.json();
            const queueEl = document.getElementById('queue-status');

            let html = '';
            html += `<div class="stat-item"><span class="stat-label">Total Items</span><span class="stat-value">${data.total}</span></div>`;
            html += `<div class="stat-item"><span class="stat-label">Pending</span><span class="stat-value">${data.byStatus.pending || 0}</span></div>`;
            html += `<div class="stat-item"><span class="stat-label">In Progress</span><span class="stat-value">${data.byStatus.in_progress || 0}</span></div>`;
            html += `<div class="stat-item"><span class="stat-label">Completed</span><span class="stat-value">${data.byStatus.completed || 0}</span></div>`;

            queueEl.innerHTML = html;
        } catch (e) {
            document.getElementById('queue-status').innerHTML = '<div class="loading">Error loading queue data</div>';
        }
    }

    async function loadProjects() {
        try {
            const res = await fetch('/api/dashboard/projects');
            const projects = await res.json();
            const projectsEl = document.getElementById('projects-list');

            if (projects.length === 0) {
                projectsEl.innerHTML = '<div class="loading">No projects found</div>';
                return;
            }

            let html = '';
            projects.forEach(project => {
                const totalTasks = project.totalTasks || 0;
                const completedTasks = project.statusCounts.completed || 0;
                html += `<div class="project-item" onclick="showProjectDetails('${project.name}')" style="cursor: pointer;">
                    <div class="project-name">${project.name}</div>
                    <div class="project-stats">
                        <span>${totalTasks} tasks</span>
                        <span>${completedTasks} completed</span>
                    </div>
                </div>`;
            });

            projectsEl.innerHTML = html;
        } catch (e) {
            document.getElementById('projects-list').innerHTML = '<div class="loading">Error loading projects</div>';
        }
    }

    // Helper function to render task tree recursively
    function renderTaskTree(nodes, level = 0) {
        if (!nodes || nodes.length === 0) return '';

        let html = '';
        nodes.forEach(node => {
            const task = node.task;
            const statusClass = task.status.replace('_', '-');
            const statusText = task.status.replace('_', ' ');
            const priorityClass = task.priority || 'medium';
            const hasChildren = node.children && node.children.length > 0;
            const indent = level * 20;

            html += `
                <div class="tree-node" style="margin-left: ${indent}px;">
                    <div class="tree-node-header">
                        ${hasChildren ? `
                            <button class="tree-toggle" onclick="toggleTreeNode(event, this)">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="9 18 15 12 9 6"></polyline>
                                </svg>
                            </button>
                        ` : '<span class="tree-spacer"></span>'}
                        <div class="tree-node-content">
                            <div class="tree-node-title">${task.title}</div>
                            <div class="tree-node-badges">
                                <span class="status-badge status-${statusClass}">${statusText}</span>
                                <span class="priority-badge priority-${priorityClass}">${task.priority}</span>
                            </div>
                        </div>
                    </div>
                    ${task.description ? `<div class="tree-node-description">${task.description}</div>` : ''}
                    ${hasChildren ? `
                        <div class="tree-node-children">
                            ${renderTaskTree(node.children, level + 1)}
                        </div>
                    ` : ''}
                </div>
            `;
        });
        return html;
    }

    function toggleTreeNode(event, button) {
        event.stopPropagation();
        const node = button.closest('.tree-node');
        const children = node.querySelector('.tree-node-children');
        const svg = button.querySelector('svg');

        if (children) {
            children.classList.toggle('collapsed');
            svg.style.transform = children.classList.contains('collapsed') ? 'rotate(0deg)' : 'rotate(90deg)';
        }
    }

    async function showProjectDetails(projectSlug) {
        try {
            // Fetch project details
            const res = await fetch(`/api/dashboard/projects/${projectSlug}`);
            const project = await res.json();

            // Hide main dashboard sections
            document.querySelector('.dashboard-content').style.display = 'none';

            // Create and show project detail view
            let projectDetailEl = document.getElementById('project-detail-view');
            if (!projectDetailEl) {
                projectDetailEl = document.createElement('div');
                projectDetailEl.id = 'project-detail-view';
                projectDetailEl.className = 'project-detail-view';
                document.getElementById('dashboard-panel').querySelector('.dashboard-header').after(projectDetailEl);
            }

            // Build tree view HTML
            let tasksHtml = '';
            if (project.taskTree && project.taskTree.length > 0) {
                tasksHtml = renderTaskTree(project.taskTree);
            } else {
                tasksHtml = '<div class="loading">No tasks in this project</div>';
            }

            // Set the content
            projectDetailEl.innerHTML = `
                <div class="project-detail-header">
                    <button class="back-btn" onclick="hideProjectDetails()">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="19" y1="12" x2="5" y2="12"></line>
                            <polyline points="12 19 5 12 12 5"></polyline>
                        </svg>
                        Back
                    </button>
                    <h2>${project.name}</h2>
                </div>
                <div class="project-detail-tasks">
                    <h3>Task Hierarchy</h3>
                    <div class="tasks-tree-view">
                        ${tasksHtml}
                    </div>
                </div>
            `;

            projectDetailEl.style.display = 'block';
        } catch (e) {
            alert('Error loading project details: ' + e.message);
        }
    }

    function hideProjectDetails() {
        const projectDetailEl = document.getElementById('project-detail-view');
        if (projectDetailEl) {
            projectDetailEl.style.display = 'none';
        }
        document.querySelector('.dashboard-content').style.display = 'block';
    }

    async function loadTasks() {
        try {
            const res = await fetch('/api/dashboard/tasks');
            const tasks = await res.json();
            const tasksEl = document.getElementById('tasks-list');

            const activeTasks = tasks.filter(t => t.status === 'in_progress' || t.status === 'pending');

            if (activeTasks.length === 0) {
                tasksEl.innerHTML = '<div class="loading">No active tasks</div>';
                return;
            }

            let html = '';
            activeTasks.slice(0, 10).forEach(task => {
                html += `<div class="task-item">
                    <div class="task-title">${task.title}</div>
                    <div class="task-meta">
                        <span class="status-badge status-${task.status}">${task.status.replace('_', ' ')}</span>
                        <span>${task.project}</span>
                        ${task.assignedAgent ? `<span>${task.assignedAgent}</span>` : ''}
                    </div>
                </div>`;
            });

            tasksEl.innerHTML = html;
        } catch (e) {
            document.getElementById('tasks-list').innerHTML = '<div class="loading">Error loading tasks</div>';
        }
    }

    // Refresh dashboard every 10 seconds if open
    setInterval(() => {
        if (dashboardPanel.classList.contains('open')) {
            loadDashboardData();
        }
    }, 10000);
    """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Proto - AI Agent</title>
        <style>{css}</style>
    </head>
    <body>
        <div id="app">
            <!-- Overlay for drawer -->
            <div id="sidebar-overlay"></div>

            <!-- Sidebar Drawer -->
            <div id="sidebar">
                <div id="sidebar-header">
                    <h1>Conversations</h1>
                    <div class="header-icons">
                        <button id="newSessionBtnSidebar" class="icon-btn new-chat" title="New Conversation">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="12" y1="5" x2="12" y2="19"></line>
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                            </svg>
                        </button>
                        <button id="stopBtn" class="icon-btn stop-btn" title="Stop Agent" style="display:none">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                <rect x="6" y="6" width="12" height="12"></rect>
                            </svg>
                        </button>
                    </div>
                </div>
                <div id="search-container">
                    <input id="search-input" type="text" placeholder="Search conversations..." />
                </div>
                <div id="sessions-list"></div>
            </div>

            <!-- Chat Area -->
            <div id="chat-area">
                <div id="chat-header">
                    <div class="chat-title">
                        <button id="menu-toggle" title="Open Menu">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="3" y1="12" x2="21" y2="12"></line>
                                <line x1="3" y1="6" x2="21" y2="6"></line>
                                <line x1="3" y1="18" x2="21" y2="18"></line>
                            </svg>
                        </button>
                        <div class="chat-avatar">P</div>
                        <div class="chat-info">
                            <h2>Proto</h2>
                            <div class="chat-status" id="status"></div>
                        </div>
                    </div>
                    <div class="header-actions">
                        <button id="toggleDashboardBtn" class="icon-btn" title="Toggle Dashboard">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="7" height="7"></rect>
                                <rect x="14" y="3" width="7" height="7"></rect>
                                <rect x="3" y="14" width="7" height="7"></rect>
                                <rect x="14" y="14" width="7" height="7"></rect>
                            </svg>
                        </button>
                        <button id="newSessionBtn" class="icon-btn new-chat-header" title="New Conversation">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="12" y1="5" x2="12" y2="19"></line>
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                            </svg>
                        </button>
                    </div>
                </div>
                <div id="messages"></div>
                <div id="composer">
                    <form id="chat-form">
                        <div class="composer-wrapper">
                            <textarea id="prompt" placeholder="Message Proto" rows="1"></textarea>
                            <button id="sendBtn" type="submit" title="Send message">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                                </svg>
                            </button>
                            <button id="stopBtnComposer" type="button" class="stop-btn-composer" title="Stop" style="display:none">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                    <rect x="6" y="6" width="12" height="12" rx="2"></rect>
                                </svg>
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Dashboard Panel -->
            <div id="dashboard-panel" class="dashboard-panel">
                <div class="dashboard-header">
                    <h2>Project Dashboard</h2>
                    <button id="closeDashboardBtn" class="icon-btn" title="Close Dashboard">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                <div class="dashboard-content">
                    <div class="dashboard-section">
                        <h3>Work Queue</h3>
                        <div id="queue-status" class="queue-status">
                            <div class="loading">Loading...</div>
                        </div>
                    </div>
                    <div class="dashboard-section">
                        <h3>Projects</h3>
                        <div id="projects-list" class="projects-list">
                            <div class="loading">Loading...</div>
                        </div>
                    </div>
                    <div class="dashboard-section">
                        <h3>Active Tasks</h3>
                        <div id="tasks-list" class="tasks-list">
                            <div class="loading">Loading...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>{js}</script>
    </body>
    </html>
    """


def main():
    host = os.getenv("WEBUI_HOST", "127.0.0.1")
    port = int(os.getenv("WEBUI_PORT", "8000"))
    auto_open = os.getenv("WEBUI_AUTO_OPEN", "1") not in {"0", "false", "False"}
    if auto_open:
        threading.Thread(
            target=_maybe_launch_native_window, args=(host, port), daemon=True
        ).start()

    # Try to use uvloop for better async performance
    try:
        import uvloop
        loop = "uvloop"
    except ImportError:
        loop = "asyncio"

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=False,
        loop=loop,  # Use uvloop if available, else asyncio
        timeout_keep_alive=75,  # Keep connections alive longer
        limit_concurrency=1000,  # Allow many concurrent connections
        backlog=2048,  # Connection backlog
        limit_max_requests=10000,  # Restart worker after N requests
        timeout_graceful_shutdown=30,  # Graceful shutdown timeout
    )
    server = uvicorn.Server(config)
    server.run()


def _maybe_launch_native_window(host: str, port: int):
    """On macOS, open a chromeless Chrome window pointing at the UI."""
    if platform.system().lower() != "darwin":
        return
    url = f"http://{host}:{port}"
    time.sleep(1.5)
    chrome_path = "/Applications/Google Chrome.app"
    if not os.path.exists(chrome_path):
        return
    try:
        subprocess.Popen(
            [
                "open",
                "-na",
                "Google Chrome",
                "--args",
                f"--app={url}",
                "--new-window",
                "--user-data-dir=/tmp/claude-computer-use",
            ]
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
