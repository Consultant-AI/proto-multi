"""
Unified log viewer - merges all log files into chronological order.

This makes it easy for AI to understand what happened by viewing a single timeline.
"""

import json
from pathlib import Path
from typing import Any


def merge_all_logs(log_dir: Path) -> list[dict[str, Any]]:
    """
    Merge all log files into a single chronological list.

    Args:
        log_dir: Directory containing log files

    Returns:
        List of all log entries sorted by timestamp
    """
    all_logs = []

    # Load all log files
    log_files = [
        "proto_sessions.jsonl",
        "proto_errors.jsonl",
        "proto_tools.jsonl",
        "proto_system.jsonl",
    ]

    for log_file in log_files:
        file_path = log_dir / log_file
        if not file_path.exists():
            continue

        with open(file_path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    all_logs.append(entry)
                except json.JSONDecodeError:
                    continue

    # Sort by timestamp
    all_logs.sort(key=lambda x: x.get("timestamp", ""))

    return all_logs


def create_unified_log(log_dir: Path, output_file: Path | None = None) -> None:
    """
    Create a single unified log file with all events in chronological order.

    This is the recommended format for AI analysis.

    Args:
        log_dir: Directory containing log files
        output_file: Output file path (default: log_dir/proto_unified.jsonl)
    """
    if output_file is None:
        output_file = log_dir / "proto_unified.jsonl"

    all_logs = merge_all_logs(log_dir)

    # Write unified log
    with open(output_file, "w") as f:
        for entry in all_logs:
            f.write(json.dumps(entry) + "\n")

    print(f"✅ Created unified log: {output_file}")
    print(f"   Total events: {len(all_logs)}")
    print(f"\nAI can now read this single file to see everything that happened in chronological order.")


def view_timeline(log_dir: Path, session_id: str | None = None, limit: int | None = None) -> None:
    """
    View complete timeline across all log sources.

    Args:
        log_dir: Directory containing log files
        session_id: Filter by session ID
        limit: Maximum number of entries to show
    """
    all_logs = merge_all_logs(log_dir)

    # Filter by session if requested
    if session_id:
        all_logs = [log for log in all_logs if log.get("session_id") == session_id]

    # Limit if requested
    if limit:
        all_logs = all_logs[:limit]

    # Display
    print(f"\n{'=' * 80}")
    print(f"Complete Timeline (all events in chronological order)")
    if session_id:
        print(f"Session: {session_id}")
    print(f"{'=' * 80}\n")

    for i, entry in enumerate(all_logs, 1):
        timestamp = entry.get("timestamp", "N/A")
        level = entry.get("level", "INFO")
        event_type = entry.get("event_type", "unknown")
        session = entry.get("session_id")
        session_str = session[:8] if session else "N/A"

        # Format with sequence number
        line = f"{i:4}. [{timestamp}] {level:8} {event_type:25} session={session_str}"

        # Add key data
        if entry.get("data"):
            data = entry["data"]
            # Show first 100 chars of data
            data_str = json.dumps(data)
            if len(data_str) > 100:
                data_str = data_str[:100] + "..."
            line += f" | {data_str}"

        print(line)

    print(f"\n{'=' * 80}")
    print(f"Total events: {len(all_logs)}")
    print(f"{'=' * 80}\n")


def main():
    """CLI entry point for unified log viewer."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified log viewer - see all events in chronological order"
    )
    parser.add_argument("--log-dir", default="logs", help="Log directory path")
    parser.add_argument("--session", help="Filter by session ID")
    parser.add_argument("--limit", "-n", type=int, help="Limit number of entries")
    parser.add_argument("--create-unified", action="store_true",
                       help="Create unified log file for AI analysis")
    parser.add_argument("--output", help="Output file for unified log")

    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        print(f"Log directory not found: {log_dir}")
        return 1

    if args.create_unified:
        output_file = Path(args.output) if args.output else None
        create_unified_log(log_dir, output_file)
    else:
        view_timeline(log_dir, session_id=args.session, limit=args.limit)

    return 0


if __name__ == "__main__":
    exit(main())
