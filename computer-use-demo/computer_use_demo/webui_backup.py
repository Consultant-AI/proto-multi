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

from .loop import APIProvider
from .agent_loop import sampling_loop
from .tools import ToolResult, ToolVersion

DEFAULT_MODEL = os.getenv("COMPUTER_USE_MODEL", "claude-sonnet-4-5-20250929")
DEFAULT_TOOL_VERSION = cast(
    ToolVersion, os.getenv("COMPUTER_USE_TOOL_VERSION", "computer_use_local")
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
                # Agent SDK features
                session_id=self.session_id,
                enable_verification=self.enable_verification,
                enable_subagents=self.enable_subagents,
            )

            self.messages = updated_messages

            assistant_text = "".join(self._pending_assistant_chunks).strip()
            self._pending_assistant_chunks.clear()
            if assistant_text:
                self.display_messages.append(
                    DisplayMessage(
                        id=str(uuid.uuid4()),
                        role="assistant",
                        label="Claude",
                        text=assistant_text,
                    )
                )

        finally:
            async with self._lock:
                self._busy = False
            # Final update when agent finishes
            await self._broadcast_sse_update()

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
        session.messages = data["messages"]
        session.display_messages = data["display_messages"]
        session.created_at = data["created_at"]
        session.last_active = data["last_active"]
        return session

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


app = FastAPI(title="Claude Computer Use")
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
        --bg: #0d1117;
        --panel: #151b23;
        --border: #2a3140;
        --text: #f1f5f9;
        --muted: #9ba7be;
        --accent: #10a37f;
    }
    * { box-sizing: border-box; }
    body {
        margin: 0;
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        background: linear-gradient(180deg, #07090d, #0d1117);
        color: var(--text);
        min-height: 100vh;
        display: flex;
        justify-content: center;
        padding: 24px;
    }
    #app {
        width: min(960px, 100%);
        background: rgba(13, 17, 23, 0.85);
        border: 1px solid var(--border);
        border-radius: 24px;
        display: flex;
        flex-direction: column;
        box-shadow: 0 25px 65px rgba(0,0,0,0.35);
        overflow: hidden;
    }
    header {
        padding: 24px;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    header h1 {
        font-size: 20px;
        margin: 0;
    }
    .header-right {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 8px;
    }
    .controls-row {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    .session-select {
        background: #080b11;
        border: 1px solid var(--border);
        color: var(--text);
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 12px;
        cursor: pointer;
        min-width: 180px;
    }
    .session-select:hover {
        border-color: var(--accent);
    }
    .icon-btn {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        color: #667eea;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        padding: 0;
    }
    .icon-btn:hover {
        background: rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
    }
    .icon-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }
    .stop-btn {
        background: rgba(239, 68, 68, 0.1);
        border-color: rgba(239, 68, 68, 0.3);
        color: #ef4444;
    }
    .stop-btn:hover:not(:disabled) {
        background: rgba(239, 68, 68, 0.2);
    }
    #status {
        font-size: 14px;
        color: var(--muted);
    }
    .badge {
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 12px;
        background: rgba(16, 163, 127, 0.15);
        color: var(--accent);
        border: 1px solid rgba(16, 163, 127, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    #messages {
        flex: 1;
        padding: 24px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 16px;
        scroll-behavior: smooth;
        scroll-padding-bottom: 24px;
    }
    .bubble {
        border-radius: 18px;
        padding: 18px;
        background: var(--panel);
        border: 1px solid var(--border);
        line-height: 1.5;
        white-space: pre-wrap;
    }
    .bubble.user { background: #1d2633; border-color: #293345; }
    .bubble.assistant { background: #10151c; border-color: #1c2330; }
    .bubble.tool { background: #0f1a1b; border-color: #183230; }
    .label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--muted);
        margin-bottom: 6px;
    }
    #composer {
        padding: 20px 24px;
        border-top: 1px solid var(--border);
        background: rgba(11, 15, 21, 0.9);
    }
    #prompt {
        width: 100%;
        min-height: 90px;
        border-radius: 14px;
        border: 1px solid var(--border);
        background: #080b11;
        color: var(--text);
        padding: 14px;
        resize: vertical;
        font-size: 15px;
    }
    #sendBtn {
        margin-top: 12px;
        background: var(--accent);
        border: none;
        color: #fff;
        padding: 12px 24px;
        border-radius: 999px;
        font-size: 15px;
        cursor: pointer;
        box-shadow: 0 10px 20px rgba(16,163,127,0.35);
    }
    #sendBtn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        box-shadow: none;
    }
    img.tool-screenshot {
        margin-top: 12px;
        border-radius: 12px;
        max-width: 100%;
        border: 1px solid #1f2937;
    }
    .typing-indicator {
        display: none;
        border-radius: 18px;
        padding: 18px;
        background: #10151c;
        border: 1px solid #1c2330;
        line-height: 1.5;
    }
    .typing-indicator.active {
        display: block;
    }
    .typing-indicator .label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--muted);
        margin-bottom: 6px;
    }
    .typing-dots {
        display: flex;
        gap: 6px;
        align-items: center;
    }
    .typing-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent);
        animation: typing-bounce 1.4s infinite ease-in-out;
    }
    .typing-dots span:nth-child(1) {
        animation-delay: -0.32s;
    }
    .typing-dots span:nth-child(2) {
        animation-delay: -0.16s;
    }
    @keyframes typing-bounce {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1.2);
            opacity: 1;
        }
    }
    """

    js = """
    const messagesEl = document.getElementById('messages');
    const form = document.getElementById('chat-form');
    const promptEl = document.getElementById('prompt');
    const sendBtn = document.getElementById('sendBtn');
    const statusEl = document.getElementById('status');
    const stopBtn = document.getElementById('stopBtn');
    const sessionSelect = document.getElementById('sessionSelect');
    const newSessionBtn = document.getElementById('newSessionBtn');

    let eventSource = null;
    let currentSessionId = null;
    let typingIndicator = null;

    // Create typing indicator element
    function createTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'typing-indicator';
        div.id = 'typing-indicator';
        div.innerHTML = `
            <div class="label">Claude</div>
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

            sessionSelect.innerHTML = '';

            sessions.forEach(session => {
                const option = document.createElement('option');
                option.value = session.id;
                option.textContent = `${formatDate(session.lastActive)} (${session.messageCount} msgs)`;
                if (session.isCurrent) {
                    option.selected = true;
                    currentSessionId = session.id;
                }
                sessionSelect.appendChild(option);
            });
        } catch (e) {
            console.error('Failed to load sessions:', e);
        }
    }

    // Switch session
    sessionSelect.addEventListener('change', async (e) => {
        const sessionId = e.target.value;
        if (!sessionId || sessionId === currentSessionId) return;

        try {
            const res = await fetch(`/api/sessions/${sessionId}/switch`, { method: 'POST' });
            const data = await res.json();
            renderMessages(data.messages, true);
            updateStatus(data.running);
            currentSessionId = sessionId;
        } catch (e) {
            console.error('Failed to switch session:', e);
            alert('Failed to switch session');
        }
    });

    // New session
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

    // Stop button
    stopBtn.addEventListener('click', async () => {
        try {
            await fetch('/api/stop', { method: 'POST' });
            stopBtn.style.display = 'none';
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
        statusEl.textContent = running ? 'Claude is working…' : 'Idle';
        sendBtn.disabled = running;
        promptEl.disabled = running;

        // Show stop button when running, hide when idle
        stopBtn.style.display = running ? 'flex' : 'none';

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
    """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Claude Computer Use</title>
        <style>{css}</style>
    </head>
    <body>
        <div id="app">
            <header>
                <h1>Claude Computer Use</h1>
                <div class="header-right">
                    <div class="controls-row">
                        <!-- Session selector -->
                        <select id="sessionSelect" class="session-select">
                            <option value="">Loading sessions...</option>
                        </select>

                        <!-- New conversation button -->
                        <button id="newSessionBtn" class="icon-btn" title="New Conversation">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="12" y1="5" x2="12" y2="19"></line>
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                            </svg>
                        </button>

                        <!-- Stop button (hidden by default) -->
                        <button id="stopBtn" class="icon-btn stop-btn" title="Stop Agent" style="display:none">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <rect x="6" y="6" width="12" height="12"></rect>
                            </svg>
                        </button>
                    </div>
                    <div class="badge">Agent SDK Enabled</div>
                    <div id="status">Idle</div>
                </div>
            </header>
            <div id="messages"></div>
            <div id="composer">
                <form id="chat-form">
                    <textarea id="prompt" placeholder="Describe what Claude should do…"></textarea>
                    <button id="sendBtn" type="submit">Send</button>
                </form>
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
