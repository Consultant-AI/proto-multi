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
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from anthropic.types.beta import BetaContentBlockParam, BetaMessageParam

from .loop import APIProvider, sampling_loop
from .tools import ToolResult, ToolVersion

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
        self.enable_subagents = False  # Disabled for simpler execution
        self.session_stats: dict[str, Any] = {}

        # SSE streaming for real-time updates
        self._sse_queues: list[asyncio.Queue] = []

        # Stop/resume functionality
        self._stop_requested = False
        self._current_task: asyncio.Task | None = None

        # Session persistence
        self.created_at = datetime.now()
        self.last_active = datetime.now()

    async def stop(self) -> None:
        """Request the agent to stop."""
        self._stop_requested = True
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

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
            self.messages.append(
                {
                    "role": "user",
                    "content": [{"type": "text", "text": user_text}],
                }
            )
            self.display_messages.append(
                DisplayMessage(
                    id=str(uuid.uuid4()),
                    role="user",
                    text=user_text.strip(),
                    label="You",
                )
            )

            def output_callback(block: BetaContentBlockParam):
                if isinstance(block, dict) and block.get("type") == "text":
                    self._pending_assistant_chunks.append(block.get("text", ""))
                    # Send real-time update via SSE
                    asyncio.create_task(self._broadcast_sse_update())

            def tool_output_callback(result: ToolResult, tool_id: str):
                text_parts: list[str] = []
                if result.system:
                    text_parts.append(f"[system] {result.system.strip()}")
                if result.output:
                    text_parts.append(result.output.strip())
                if result.error:
                    text_parts.append(f"⚠️ {result.error.strip()}")
                images = (
                    [f"data:image/png;base64,{result.base64_image}"]
                    if result.base64_image
                    else []
                )
                summary = text_parts or ["(tool executed)"]
                self.display_messages.append(
                    DisplayMessage(
                        id=str(uuid.uuid4()),
                        role="tool",
                        label=f"Tool {tool_id}",
                        text="\n".join(summary),
                        images=images,
                    )
                )
                # Send real-time update via SSE
                asyncio.create_task(self._broadcast_sse_update())

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
        """Broadcast current state to all SSE connections."""
        data = self.serialize()
        for queue in self._sse_queues:
            try:
                await queue.put(data)
            except:
                pass  # Queue might be closed

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
                "subagents": self.enable_subagents,
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


SESSIONS_DIR = Path.home() / ".claude" / "webui_sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup_event():
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
    await session.stop()
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
                    <button id="newSessionBtn" class="icon-btn new-chat-header" title="New Conversation">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                    </button>
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
    config = uvicorn.Config(app, host=host, port=port, reload=False)
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
