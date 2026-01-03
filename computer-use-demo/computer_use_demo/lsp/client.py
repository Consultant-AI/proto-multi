"""
LSP client implementation.

Communicates with Language Servers using JSON-RPC 2.0 over stdio.
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from .types import (
    CompletionItem,
    Diagnostic,
    DiagnosticSeverity,
    Hover,
    Location,
    LSPServerConfig,
    LSPServerStatus,
    Position,
    Range,
)


class LSPClient:
    """
    Client for communicating with a Language Server.

    Uses JSON-RPC 2.0 over stdio.
    """

    def __init__(self, config: LSPServerConfig, workspace_root: Path | None = None):
        self.config = config
        self.workspace_root = workspace_root or Path.cwd()
        self._process: subprocess.Popen | None = None
        self._request_id = 0
        self._pending_requests: dict[int, asyncio.Future] = {}
        self._reader_task: asyncio.Task | None = None
        self._status = LSPServerStatus.STOPPED
        self._capabilities: dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._diagnostics: dict[str, list[Diagnostic]] = {}  # uri -> diagnostics

    @property
    def status(self) -> LSPServerStatus:
        return self._status

    @property
    def is_running(self) -> bool:
        return self._status == LSPServerStatus.RUNNING

    @property
    def capabilities(self) -> dict[str, Any]:
        return self._capabilities

    async def start(self) -> bool:
        """Start the LSP server process."""
        async with self._lock:
            if self._status == LSPServerStatus.RUNNING:
                return True

            self._status = LSPServerStatus.STARTING

            try:
                # Build environment
                env = os.environ.copy()
                env.update(self.config.env)

                # Build command
                cmd = [self.config.command] + self.config.args

                # Start process
                self._process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True,
                    bufsize=1,
                )

                # Start reader task
                self._reader_task = asyncio.create_task(self._read_responses())

                # Initialize the server
                await self._initialize()

                self._status = LSPServerStatus.RUNNING
                return True

            except Exception as e:
                self._status = LSPServerStatus.ERROR
                await self.stop()
                raise RuntimeError(f"Failed to start LSP server '{self.config.name}': {e}")

    async def stop(self) -> None:
        """Stop the LSP server process."""
        async with self._lock:
            # Send shutdown request
            if self._status == LSPServerStatus.RUNNING:
                try:
                    await self.request("shutdown", timeout=5.0)
                    await self.notify("exit")
                except Exception:
                    pass

            # Cancel reader task
            if self._reader_task:
                self._reader_task.cancel()
                try:
                    await self._reader_task
                except asyncio.CancelledError:
                    pass
                self._reader_task = None

            # Terminate process
            if self._process:
                try:
                    self._process.terminate()
                    self._process.wait(timeout=5)
                except Exception:
                    try:
                        self._process.kill()
                    except Exception:
                        pass
                self._process = None

            # Cancel pending requests
            for future in self._pending_requests.values():
                future.cancel()
            self._pending_requests.clear()

            self._status = LSPServerStatus.STOPPED

    async def _initialize(self) -> None:
        """Initialize the LSP server connection."""
        response = await self.request(
            "initialize",
            {
                "processId": os.getpid(),
                "rootUri": self.workspace_root.as_uri(),
                "rootPath": str(self.workspace_root),
                "capabilities": {
                    "textDocument": {
                        "synchronization": {"didSave": True, "didOpen": True, "didClose": True},
                        "completion": {"completionItem": {"snippetSupport": True}},
                        "hover": {},
                        "definition": {},
                        "references": {},
                        "publishDiagnostics": {},
                    },
                    "workspace": {
                        "workspaceFolders": True,
                    },
                },
                "workspaceFolders": [
                    {
                        "uri": self.workspace_root.as_uri(),
                        "name": self.workspace_root.name,
                    }
                ],
                "initializationOptions": self.config.init_options,
            },
        )

        if response and "capabilities" in response:
            self._capabilities = response["capabilities"]

        # Send initialized notification
        await self.notify("initialized", {})

    async def request(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> Any:
        """Send a request and wait for response."""
        if not self.is_running and self._status != LSPServerStatus.STARTING:
            raise RuntimeError("LSP server is not running")

        self._request_id += 1
        request_id = self._request_id

        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
        }
        if params:
            request["params"] = params

        future: asyncio.Future[Any] = asyncio.get_event_loop().create_future()
        self._pending_requests[request_id] = future

        try:
            await self._send(request)
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            return None
        except Exception as e:
            self._pending_requests.pop(request_id, None)
            raise

    async def notify(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> None:
        """Send a notification (no response expected)."""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params:
            notification["params"] = params

        await self._send(notification)

    async def _send(self, message: dict[str, Any]) -> None:
        """Send a message to the server."""
        if not self._process or not self._process.stdin:
            raise RuntimeError("Process not running")

        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"

        try:
            self._process.stdin.write(header + content)
            self._process.stdin.flush()
        except Exception as e:
            raise RuntimeError(f"Failed to send message: {e}")

    async def _read_responses(self) -> None:
        """Background task to read responses from server."""
        if not self._process or not self._process.stdout:
            return

        buffer = ""

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, self._process.stdout.readline
                )

                if not line:
                    break

                buffer += line

                while "\r\n\r\n" in buffer:
                    header_end = buffer.index("\r\n\r\n")
                    header = buffer[:header_end]
                    buffer = buffer[header_end + 4:]

                    content_length = 0
                    for line in header.split("\r\n"):
                        if line.startswith("Content-Length:"):
                            content_length = int(line.split(":")[1].strip())
                            break

                    if content_length > 0:
                        while len(buffer) < content_length:
                            more = await asyncio.get_event_loop().run_in_executor(
                                None, lambda: self._process.stdout.read(content_length - len(buffer))
                            )
                            if not more:
                                break
                            buffer += more

                        content = buffer[:content_length]
                        buffer = buffer[content_length:]

                        try:
                            message = json.loads(content)
                            await self._handle_message(message)
                        except json.JSONDecodeError:
                            pass

            except asyncio.CancelledError:
                break
            except Exception:
                break

    async def _handle_message(self, message: dict[str, Any]) -> None:
        """Handle an incoming message."""
        if "id" in message and message["id"] is not None:
            request_id = message["id"]
            future = self._pending_requests.pop(request_id, None)

            if future and not future.done():
                if "error" in message:
                    future.set_exception(RuntimeError(str(message["error"])))
                else:
                    future.set_result(message.get("result"))

        elif "method" in message:
            # Handle server notifications
            method = message["method"]
            params = message.get("params", {})

            if method == "textDocument/publishDiagnostics":
                self._handle_diagnostics(params)

    def _handle_diagnostics(self, params: dict[str, Any]) -> None:
        """Handle diagnostics notification."""
        uri = params.get("uri", "")
        diagnostics = []

        for diag in params.get("diagnostics", []):
            range_data = diag.get("range", {})
            start = range_data.get("start", {})
            end = range_data.get("end", {})

            diagnostic = Diagnostic(
                range=Range(
                    start=Position(start.get("line", 0), start.get("character", 0)),
                    end=Position(end.get("line", 0), end.get("character", 0)),
                ),
                message=diag.get("message", ""),
                severity=DiagnosticSeverity(diag.get("severity", 1)),
                code=diag.get("code"),
                source=diag.get("source"),
            )
            diagnostics.append(diagnostic)

        self._diagnostics[uri] = diagnostics

    # High-level API methods

    async def open_document(self, path: Path, content: str | None = None) -> None:
        """Notify server that a document was opened."""
        if content is None:
            content = path.read_text()

        # Determine language ID
        language_id = self._get_language_id(path)

        await self.notify(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": path.as_uri(),
                    "languageId": language_id,
                    "version": 1,
                    "text": content,
                }
            },
        )

    async def close_document(self, path: Path) -> None:
        """Notify server that a document was closed."""
        await self.notify(
            "textDocument/didClose",
            {
                "textDocument": {
                    "uri": path.as_uri(),
                }
            },
        )

    async def save_document(self, path: Path, content: str | None = None) -> None:
        """Notify server that a document was saved."""
        params: dict[str, Any] = {
            "textDocument": {
                "uri": path.as_uri(),
            }
        }
        if content is not None:
            params["text"] = content

        await self.notify("textDocument/didSave", params)

    async def get_diagnostics(self, path: Path) -> list[Diagnostic]:
        """Get diagnostics for a file."""
        uri = path.as_uri()
        return self._diagnostics.get(uri, [])

    async def get_completions(
        self,
        path: Path,
        position: Position,
    ) -> list[CompletionItem]:
        """Get completion suggestions."""
        result = await self.request(
            "textDocument/completion",
            {
                "textDocument": {"uri": path.as_uri()},
                "position": position.to_lsp(),
            },
        )

        if not result:
            return []

        items = result if isinstance(result, list) else result.get("items", [])

        return [
            CompletionItem(
                label=item.get("label", ""),
                kind=item.get("kind"),
                detail=item.get("detail"),
                documentation=item.get("documentation"),
                insert_text=item.get("insertText"),
            )
            for item in items
        ]

    async def get_hover(
        self,
        path: Path,
        position: Position,
    ) -> Hover | None:
        """Get hover information."""
        result = await self.request(
            "textDocument/hover",
            {
                "textDocument": {"uri": path.as_uri()},
                "position": position.to_lsp(),
            },
        )

        if not result:
            return None

        contents = result.get("contents", "")
        if isinstance(contents, dict):
            contents = contents.get("value", "")
        elif isinstance(contents, list):
            contents = "\n".join(
                c.get("value", str(c)) if isinstance(c, dict) else str(c)
                for c in contents
            )

        return Hover(contents=contents)

    async def get_definition(
        self,
        path: Path,
        position: Position,
    ) -> list[Location]:
        """Get definition locations."""
        result = await self.request(
            "textDocument/definition",
            {
                "textDocument": {"uri": path.as_uri()},
                "position": position.to_lsp(),
            },
        )

        if not result:
            return []

        if not isinstance(result, list):
            result = [result]

        locations = []
        for loc in result:
            if "uri" in loc:
                range_data = loc.get("range", {})
                start = range_data.get("start", {})
                end = range_data.get("end", {})

                locations.append(
                    Location(
                        uri=loc["uri"],
                        range=Range(
                            start=Position(start.get("line", 0), start.get("character", 0)),
                            end=Position(end.get("line", 0), end.get("character", 0)),
                        ),
                    )
                )

        return locations

    def _get_language_id(self, path: Path) -> str:
        """Get language ID for a file."""
        ext = path.suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescriptreact",
            ".jsx": "javascriptreact",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".lua": "lua",
            ".sh": "shellscript",
            ".bash": "shellscript",
            ".zsh": "shellscript",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".sql": "sql",
            ".md": "markdown",
        }
        return language_map.get(ext, "plaintext")
