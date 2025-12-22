"""
Log viewer and analysis utilities for Proto AI Agent.

Provides tools to view, filter, and analyze structured logs.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def load_logs(log_file: Path, session_id: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    """
    Load logs from JSONL file with optional filtering.

    Args:
        log_file: Path to log file
        session_id: Filter by session ID
        limit: Maximum number of entries to return

    Returns:
        List of log entries as dictionaries
    """
    if not log_file.exists():
        return []

    logs = []
    with open(log_file) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                # Filter by session if specified
                if session_id and entry.get("session_id") != session_id:
                    continue
                logs.append(entry)
                # Stop if we've reached limit
                if limit and len(logs) >= limit:
                    break
            except json.JSONDecodeError:
                continue

    return logs


def format_log_entry(entry: dict[str, Any], verbose: bool = False) -> str:
    """Format a log entry for human-readable display."""
    timestamp = entry.get("timestamp", "N/A")
    level = entry.get("level", "INFO")
    event_type = entry.get("event_type", "unknown")
    session_id = entry.get("session_id", "N/A")[:8] if entry.get("session_id") else "N/A"

    # Base format
    output = f"[{timestamp}] {level:8} {event_type:25} session={session_id}"

    # Add key data
    if entry.get("data"):
        data = entry["data"]
        # Show relevant fields based on event type
        if event_type == "message_sent":
            msg = data.get("message", "")[:50]
            output += f" | message=\"{msg}...\""
        elif event_type == "tool_executed":
            tool_name = data.get("tool_name")
            duration = data.get("duration_ms")
            success = data.get("success")
            output += f" | tool={tool_name} duration={duration}ms success={success}"
        elif event_type == "error_occurred":
            error_type = entry.get("error", {}).get("type", "Unknown")
            error_msg = entry.get("error", {}).get("message", "")[:50]
            output += f" | {error_type}: {error_msg}"
        elif verbose:
            output += f" | {json.dumps(data)}"

    return output


def view_session(log_dir: Path, session_id: str, verbose: bool = False) -> None:
    """View all logs for a specific session."""
    print(f"\n{'=' * 80}")
    print(f"Session: {session_id}")
    print(f"{'=' * 80}\n")

    # Load logs from all files
    all_logs = []
    for log_file in ["proto_sessions.jsonl", "proto_errors.jsonl", "proto_tools.jsonl", "proto_system.jsonl"]:
        file_path = log_dir / log_file
        if file_path.exists():
            logs = load_logs(file_path, session_id=session_id)
            all_logs.extend(logs)

    # Sort by timestamp
    all_logs.sort(key=lambda x: x.get("timestamp", ""))

    if not all_logs:
        print("No logs found for this session.")
        return

    # Display logs
    for entry in all_logs:
        print(format_log_entry(entry, verbose=verbose))

    print(f"\n{'=' * 80}")
    print(f"Total entries: {len(all_logs)}")
    print(f"{'=' * 80}\n")


def view_errors(log_dir: Path, last_n: int = 10) -> None:
    """View recent errors."""
    error_log = log_dir / "proto_errors.jsonl"
    if not error_log.exists():
        print("No error log found.")
        return

    print(f"\n{'=' * 80}")
    print(f"Recent Errors (last {last_n})")
    print(f"{'=' * 80}\n")

    errors = load_logs(error_log, limit=last_n)

    if not errors:
        print("No errors found.")
        return

    for entry in errors:
        print(format_log_entry(entry, verbose=True))
        # Show full error details
        if entry.get("error"):
            error = entry["error"]
            print(f"  Error Type: {error.get('type')}")
            print(f"  Message: {error.get('message')}")
            if error.get("stack_trace"):
                print(f"  Stack trace available")
        print()

    print(f"{'=' * 80}\n")


def view_tools(log_dir: Path, session_id: str | None = None, last_n: int = 20) -> None:
    """View tool execution logs."""
    tool_log = log_dir / "proto_tools.jsonl"
    if not tool_log.exists():
        print("No tool log found.")
        return

    print(f"\n{'=' * 80}")
    print(f"Tool Executions (last {last_n})")
    if session_id:
        print(f"Session: {session_id}")
    print(f"{'=' * 80}\n")

    tools = load_logs(tool_log, session_id=session_id, limit=last_n)

    if not tools:
        print("No tool executions found.")
        return

    for entry in tools:
        print(format_log_entry(entry, verbose=True))

    print(f"\n{'=' * 80}\n")


def generate_summary(log_dir: Path, session_id: str) -> None:
    """Generate AI-readable summary of a session."""
    print(f"\n{'=' * 80}")
    print(f"AI-Readable Session Summary: {session_id}")
    print(f"{'=' * 80}\n")

    # Load all logs for session
    all_logs = []
    for log_file in ["proto_sessions.jsonl", "proto_errors.jsonl", "proto_tools.jsonl"]:
        file_path = log_dir / log_file
        if file_path.exists():
            logs = load_logs(file_path, session_id=session_id)
            all_logs.extend(logs)

    all_logs.sort(key=lambda x: x.get("timestamp", ""))

    if not all_logs:
        print("No logs found for this session.")
        return

    # Extract key events
    user_messages = [log for log in all_logs if log.get("event_type") == "message_sent"]
    tools_executed = [log for log in all_logs if log.get("event_type") == "tool_executed"]
    tools_failed = [log for log in all_logs if log.get("event_type") == "tool_failed"]
    errors = [log for log in all_logs if log.get("event_type") == "error_occurred"]

    # Generate summary
    summary = {
        "session_id": session_id,
        "start_time": all_logs[0].get("timestamp") if all_logs else None,
        "end_time": all_logs[-1].get("timestamp") if all_logs else None,
        "total_events": len(all_logs),
        "user_messages": len(user_messages),
        "tools_executed": len(tools_executed),
        "tools_failed": len(tools_failed),
        "errors": len(errors),
        "user_messages_content": [msg.get("data", {}).get("message") for msg in user_messages],
        "tools_used": list(set(tool.get("data", {}).get("tool_name") for tool in tools_executed)),
        "error_types": list(set(err.get("error", {}).get("type") for err in errors)),
    }

    # Print formatted summary
    print(json.dumps(summary, indent=2))

    # Generate natural language summary
    print(f"\n{'=' * 80}")
    print("Natural Language Summary:")
    print(f"{'=' * 80}\n")

    print(f"Session had {len(user_messages)} user message(s).")
    if user_messages:
        print(f"First message: \"{user_messages[0].get('data', {}).get('message', 'N/A')}\"")

    print(f"\nAgent executed {len(tools_executed)} tool(s): {', '.join(summary['tools_used'])}")

    if tools_failed:
        print(f"\n{len(tools_failed)} tool(s) failed.")

    if errors:
        print(f"\n{len(errors)} error(s) occurred: {', '.join(summary['error_types'])}")

    print(f"\n{'=' * 80}\n")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Proto log viewer and analyzer")
    parser.add_argument("--log-dir", default="logs", help="Log directory path")
    parser.add_argument("--session", help="Session ID to view")
    parser.add_argument("--errors", action="store_true", help="View recent errors")
    parser.add_argument("--tools", action="store_true", help="View tool executions")
    parser.add_argument("--summary", action="store_true", help="Generate session summary")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Limit number of entries")

    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        print(f"Log directory not found: {log_dir}")
        sys.exit(1)

    if args.summary:
        if not args.session:
            print("--session required for --summary")
            sys.exit(1)
        generate_summary(log_dir, args.session)
    elif args.errors:
        view_errors(log_dir, last_n=args.limit)
    elif args.tools:
        view_tools(log_dir, session_id=args.session, last_n=args.limit)
    elif args.session:
        view_session(log_dir, args.session, verbose=args.verbose)
    else:
        print("Please specify --session, --errors, --tools, or --summary")
        sys.exit(1)


if __name__ == "__main__":
    main()
