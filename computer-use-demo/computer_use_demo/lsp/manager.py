"""
LSP server manager.

Manages multiple language servers for different file types.
"""

import asyncio
import threading
from pathlib import Path
from typing import Any

from .client import LSPClient
from .types import (
    CompletionItem,
    Diagnostic,
    Hover,
    Location,
    LSPServerConfig,
    LSPServerInfo,
    LSPServerStatus,
    Position,
)


# Default LSP server configurations
DEFAULT_LSP_CONFIGS = {
    "pyright": LSPServerConfig(
        name="pyright",
        languages=["python"],
        command="pyright-langserver",
        args=["--stdio"],
        extensions=[".py"],
    ),
    "typescript": LSPServerConfig(
        name="typescript",
        languages=["typescript", "javascript", "typescriptreact", "javascriptreact"],
        command="typescript-language-server",
        args=["--stdio"],
        extensions=[".ts", ".tsx", ".js", ".jsx"],
    ),
    "rust-analyzer": LSPServerConfig(
        name="rust-analyzer",
        languages=["rust"],
        command="rust-analyzer",
        args=[],
        extensions=[".rs"],
    ),
    "gopls": LSPServerConfig(
        name="gopls",
        languages=["go"],
        command="gopls",
        args=["serve"],
        extensions=[".go"],
    ),
}


class LSPManager:
    """
    Manages multiple LSP servers.

    Automatically routes requests to the appropriate server based on file type.
    """

    def __init__(self, workspace_root: Path | None = None):
        self._workspace_root = workspace_root or Path.cwd()
        self._clients: dict[str, LSPClient] = {}
        self._configs: dict[str, LSPServerConfig] = {}
        self._extension_map: dict[str, str] = {}  # extension -> server name
        self._lock = threading.Lock()
        self._initialized = False

        # Load default configs
        for name, config in DEFAULT_LSP_CONFIGS.items():
            self._configs[name] = config
            for ext in config.extensions:
                self._extension_map[ext] = name

    def add_server_config(self, config: LSPServerConfig) -> None:
        """Add a server configuration."""
        with self._lock:
            self._configs[config.name] = config
            for ext in config.extensions:
                self._extension_map[ext] = config.name

    def remove_server_config(self, name: str) -> None:
        """Remove a server configuration."""
        with self._lock:
            config = self._configs.pop(name, None)
            if config:
                for ext in config.extensions:
                    if self._extension_map.get(ext) == name:
                        del self._extension_map[ext]

    async def start_server(self, name: str) -> LSPClient | None:
        """Start an LSP server."""
        with self._lock:
            if name in self._clients:
                client = self._clients[name]
                if client.is_running:
                    return client

            config = self._configs.get(name)
            if not config:
                return None

            client = LSPClient(config, self._workspace_root)

        try:
            await client.start()
            with self._lock:
                self._clients[name] = client
            return client
        except Exception as e:
            print(f"[LSP] Failed to start {name}: {e}")
            return None

    async def stop_server(self, name: str) -> None:
        """Stop an LSP server."""
        with self._lock:
            client = self._clients.pop(name, None)

        if client:
            await client.stop()

    async def stop_all(self) -> None:
        """Stop all servers."""
        with self._lock:
            servers = list(self._clients.keys())

        for name in servers:
            await self.stop_server(name)

    def get_client_for_file(self, path: Path) -> LSPClient | None:
        """Get the appropriate client for a file."""
        ext = path.suffix.lower()

        with self._lock:
            server_name = self._extension_map.get(ext)
            if not server_name:
                return None

            return self._clients.get(server_name)

    async def ensure_server_for_file(self, path: Path) -> LSPClient | None:
        """Ensure the appropriate server is running for a file."""
        ext = path.suffix.lower()

        with self._lock:
            server_name = self._extension_map.get(ext)
            if not server_name:
                return None

            client = self._clients.get(server_name)
            if client and client.is_running:
                return client

        return await self.start_server(server_name)

    def list_servers(self) -> list[LSPServerInfo]:
        """List all configured servers."""
        servers = []

        with self._lock:
            for name, config in self._configs.items():
                client = self._clients.get(name)
                info = LSPServerInfo(
                    name=name,
                    languages=config.languages,
                    status=client.status if client else LSPServerStatus.STOPPED,
                    pid=client._process.pid if client and client._process else None,
                    capabilities=client.capabilities if client else {},
                )
                servers.append(info)

        return servers

    # High-level API methods

    async def get_diagnostics(self, path: Path) -> list[Diagnostic]:
        """Get diagnostics for a file."""
        client = await self.ensure_server_for_file(path)
        if not client:
            return []

        return await client.get_diagnostics(path)

    async def get_completions(
        self,
        path: Path,
        line: int,
        character: int,
    ) -> list[CompletionItem]:
        """Get completions for a position."""
        client = await self.ensure_server_for_file(path)
        if not client:
            return []

        return await client.get_completions(path, Position(line, character))

    async def get_hover(
        self,
        path: Path,
        line: int,
        character: int,
    ) -> Hover | None:
        """Get hover information for a position."""
        client = await self.ensure_server_for_file(path)
        if not client:
            return None

        return await client.get_hover(path, Position(line, character))

    async def get_definition(
        self,
        path: Path,
        line: int,
        character: int,
    ) -> list[Location]:
        """Get definition locations for a position."""
        client = await self.ensure_server_for_file(path)
        if not client:
            return []

        return await client.get_definition(path, Position(line, character))

    async def open_file(self, path: Path, content: str | None = None) -> None:
        """Notify server that a file was opened."""
        client = await self.ensure_server_for_file(path)
        if client:
            await client.open_document(path, content)

    async def close_file(self, path: Path) -> None:
        """Notify server that a file was closed."""
        client = self.get_client_for_file(path)
        if client:
            await client.close_document(path)

    async def save_file(self, path: Path, content: str | None = None) -> None:
        """Notify server that a file was saved."""
        client = self.get_client_for_file(path)
        if client:
            await client.save_document(path, content)


# Global manager instance
_global_manager: LSPManager | None = None


def get_lsp_manager(workspace_root: Path | None = None) -> LSPManager:
    """Get or create the global LSP manager."""
    global _global_manager

    if _global_manager is None:
        _global_manager = LSPManager(workspace_root)

    return _global_manager


async def shutdown_lsp() -> None:
    """Shutdown all LSP servers."""
    global _global_manager

    if _global_manager:
        await _global_manager.stop_all()
        _global_manager = None
