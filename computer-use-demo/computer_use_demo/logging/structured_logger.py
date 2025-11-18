"""
Structured logging system for Proto AI Agent.

Provides AI-readable JSON logs for debugging, session replay, and analysis.
All events are logged in JSONL format (JSON Lines) for easy parsing.
"""

import json
import logging
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

# Event types for structured logging
EventType = Literal[
    # User actions
    "session_created",
    "session_loaded",
    "message_sent",
    "message_received",
    "conversation_stopped",
    "conversation_resumed",
    "session_switched",
    "page_loaded",
    # Agent behavior
    "thinking_started",
    "thinking_completed",
    "tool_selected",
    "tool_executed",
    "tool_failed",
    "api_request",
    "api_response",
    "api_error",
    # System events
    "server_started",
    "server_stopped",
    "session_persisted",
    "session_restored",
    "sse_connected",
    "sse_disconnected",
    "error_occurred",
    "debug_info",
]

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class StructuredLogger:
    """
    AI-readable structured logger that outputs JSON Lines format.

    Each log entry is a complete JSON object on a single line, making it
    easy for AI systems to parse and analyze.
    """

    def __init__(
        self,
        log_dir: str | None = None,
        log_level: LogLevel = "INFO",
        enable_console: bool = True,
        enable_sanitization: bool = True,
    ):
        """
        Initialize structured logger.

        Args:
            log_dir: Directory for log files (default: logs/ in project root)
            log_level: Minimum log level to record
            enable_console: Also print logs to console
            enable_sanitization: Redact sensitive data
        """
        # Determine log directory
        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            log_dir = str(project_root / "logs")

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.log_level = log_level
        self.enable_console = enable_console
        self.enable_sanitization = enable_sanitization

        # Create log files
        self.session_log = self.log_dir / "proto_sessions.jsonl"
        self.error_log = self.log_dir / "proto_errors.jsonl"
        self.tool_log = self.log_dir / "proto_tools.jsonl"
        self.system_log = self.log_dir / "proto_system.jsonl"

        # Ensure log files exist
        for log_file in [self.session_log, self.error_log, self.tool_log, self.system_log]:
            log_file.touch(exist_ok=True)

    def log_event(
        self,
        event_type: EventType,
        level: LogLevel = "INFO",
        session_id: str | None = None,
        data: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        error: Exception | None = None,
    ) -> None:
        """
        Log a structured event.

        Args:
            event_type: Type of event being logged
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            session_id: Session identifier
            data: Event-specific data
            context: Additional context information
            error: Exception object if this is an error event
        """
        # Build log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "event_type": event_type,
            "session_id": session_id,
            "data": data or {},
            "context": context or {},
        }

        # Add error information if present
        if error:
            log_entry["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "stack_trace": traceback.format_exc(),
            }

        # Sanitize sensitive data if enabled
        if self.enable_sanitization:
            log_entry = self._sanitize(log_entry)

        # Write to appropriate log file
        self._write_to_file(event_type, log_entry)

        # Also print to console if enabled
        if self.enable_console:
            self._print_to_console(log_entry)

    def _write_to_file(self, event_type: EventType, log_entry: dict[str, Any]) -> None:
        """Write log entry to appropriate file based on event type."""
        # Determine which file to write to
        if event_type.startswith("error_") or log_entry["level"] == "ERROR":
            log_file = self.error_log
        elif event_type.startswith("tool_"):
            log_file = self.tool_log
        elif event_type in ["server_started", "server_stopped", "sse_connected", "sse_disconnected"]:
            log_file = self.system_log
        else:
            log_file = self.session_log

        # Write as JSON line
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            # Fail silently - don't break the application
            print(f"Failed to write log: {e}")

    def _print_to_console(self, log_entry: dict[str, Any]) -> None:
        """Print log entry to console in readable format."""
        timestamp = log_entry["timestamp"]
        level = log_entry["level"]
        event_type = log_entry["event_type"]
        session_id = log_entry.get("session_id")
        session_id = session_id[:8] if session_id else "N/A"

        # Build console message
        msg = f"[{timestamp}] {level:8} {event_type:20} session={session_id}"

        # Add key data fields
        if log_entry.get("data"):
            msg += f" | {json.dumps(log_entry['data'])}"

        print(msg)

    def _sanitize(self, log_entry: dict[str, Any]) -> dict[str, Any]:
        """Remove sensitive data from log entry."""
        sensitive_keys = [
            "api_key",
            "password",
            "token",
            "secret",
            "authorization",
            "bearer",
        ]

        def sanitize_dict(d: dict[str, Any]) -> dict[str, Any]:
            sanitized = {}
            for key, value in d.items():
                # Check if key contains sensitive information
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = "[REDACTED]"
                elif isinstance(value, dict):
                    sanitized[key] = sanitize_dict(value)
                elif isinstance(value, list):
                    sanitized[key] = [
                        sanitize_dict(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    sanitized[key] = value
            return sanitized

        return sanitize_dict(log_entry)

    def log_user_message(
        self, session_id: str, message: str, message_id: str, context: dict[str, Any] | None = None
    ) -> None:
        """Convenience method for logging user messages."""
        self.log_event(
            event_type="message_sent",
            session_id=session_id,
            data={
                "message": message,
                "role": "user",
                "message_id": message_id,
                "message_length": len(message),
            },
            context=context,
        )

    def log_tool_execution(
        self,
        session_id: str,
        tool_name: str,
        tool_id: str,
        inputs: dict[str, Any],
        output: Any,
        duration_ms: float,
        success: bool,
        error: Exception | None = None,
    ) -> None:
        """Convenience method for logging tool executions."""
        self.log_event(
            event_type="tool_executed" if success else "tool_failed",
            level="INFO" if success else "ERROR",
            session_id=session_id,
            data={
                "tool_name": tool_name,
                "tool_id": tool_id,
                "inputs": inputs,
                "output_summary": str(output)[:200] if output else None,
                "duration_ms": duration_ms,
                "success": success,
            },
            error=error,
        )

    def log_error(
        self,
        session_id: str,
        error: Exception,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging errors."""
        self.log_event(
            event_type="error_occurred",
            level="ERROR",
            session_id=session_id,
            context=context,
            error=error,
        )


# Global logger instance
_logger: StructuredLogger | None = None


def get_logger() -> StructuredLogger:
    """Get or create global logger instance."""
    global _logger
    if _logger is None:
        # Read configuration from environment
        log_dir = os.getenv("PROTO_LOG_DIR")
        log_level = os.getenv("PROTO_LOG_LEVEL", "INFO")
        enable_console = os.getenv("PROTO_LOG_CONSOLE", "true").lower() == "true"
        enable_sanitization = os.getenv("PROTO_LOG_SANITIZE", "true").lower() == "true"

        _logger = StructuredLogger(
            log_dir=log_dir,
            log_level=log_level,  # type: ignore
            enable_console=enable_console,
            enable_sanitization=enable_sanitization,
        )
    return _logger
