"""
FastAPI-powered dark web UI for the Claude computer use demo.

Run with:
    python -m computer_use_demo.webui
Then open http://localhost:8000
"""

from __future__ import annotations

import asyncio
import base64
import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal, cast
import platform
import subprocess
import threading
import time

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from anthropic.types.beta import BetaContentBlockParam, BetaMessageParam

from .loop import APIProvider, sampling_loop
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

    async def send(self, user_text: str) -> None:
        if not user_text.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        async with self._lock:
            if self._busy:
                raise HTTPException(status_code=409, detail="Agent is already running.")
            self._busy = True

        try:
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
                        label="Claude",
                        text=assistant_text,
                    )
                )

        finally:
            async with self._lock:
                self._busy = False

    def serialize(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "toolVersion": self.tool_version,
            "running": self._busy,
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


@app.on_event("startup")
async def startup_event():
    api_key = _resolve_api_key()
    app.state.session = ChatSession(api_key=api_key)


@app.get("/", response_class=HTMLResponse)
async def home_page():
    return HTMLResponse(content=_html_shell(), status_code=200)


@app.get("/api/messages")
async def get_state():
    session: ChatSession = app.state.session
    return JSONResponse(session.serialize())


@app.post("/api/messages")
async def send_message(payload: SendRequest):
    session: ChatSession = app.state.session
    await session.send(payload.message)
    return JSONResponse(session.serialize())


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
    #status {
        font-size: 14px;
        color: var(--muted);
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
    """

    js = """
    const messagesEl = document.getElementById('messages');
    const form = document.getElementById('chat-form');
    const promptEl = document.getElementById('prompt');
    const sendBtn = document.getElementById('sendBtn');
    const statusEl = document.getElementById('status');

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
        if (!running) {
            promptEl.focus();
        }
    }

    form.addEventListener('submit', async (evt) => {
        evt.preventDefault();
        const message = promptEl.value.trim();
        if (!message) return;

        updateStatus(true);
        const res = await fetch('/api/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        if (!res.ok) {
            const error = await res.json();
            alert(error.detail || 'Failed to send message.');
        } else {
            const data = await res.json();
            renderMessages(data.messages, true);
            updateStatus(false);
            promptEl.value = '';
        }
    });

    refreshState(true);
    setInterval(() => refreshState(true), 3000);
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
                <div id="status">Idle</div>
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
