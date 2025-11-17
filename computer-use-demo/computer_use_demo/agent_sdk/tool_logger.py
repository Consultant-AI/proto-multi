"""
Tool execution logger for debugging and optimization.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("agent_sdk.tools")


class ToolLogger:
    """Logs tool executions for debugging and analysis"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.log_file = Path.home() / ".claude" / "projects" / f"computer-use-{session_id}" / "tool_log.jsonl"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.tool_counts = {
            "computer": 0,
            "bash": 0,
            "str_replace_editor": 0,
        }

    def log_tool_call(self, tool_name: str, tool_input: dict[str, Any]) -> None:
        """Log a tool execution"""
        self.tool_counts[tool_name] = self.tool_counts.get(tool_name, 0) + 1

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "input": self._sanitize_input(tool_input),
            "count": self.tool_counts.get(tool_name, 0)
        }

        # Write to file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Also log to console for debugging
        if tool_name == "computer":
            action = tool_input.get("action", "unknown")
            logger.warning(f"⚠️  Computer tool used: {action} (count: {self.tool_counts['computer']})")

            # Warn if too many computer calls
            if self.tool_counts['computer'] > 3:
                logger.error(
                    f"❌ TOO MANY COMPUTER TOOL CALLS ({self.tool_counts['computer']})! "
                    "Should use bash/edit tools instead!"
                )
        else:
            logger.info(f"✅ {tool_name} called (count: {self.tool_counts.get(tool_name, 0)})")

    def _sanitize_input(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Remove large data from logs"""
        sanitized = tool_input.copy()

        # Don't log full text content
        if "file_text" in sanitized and len(str(sanitized["file_text"])) > 200:
            sanitized["file_text"] = f"<{len(str(sanitized['file_text']))} chars>"

        if "text" in sanitized and len(str(sanitized["text"])) > 200:
            sanitized["text"] = f"<{len(str(sanitized['text']))} chars>"

        return sanitized

    def get_summary(self) -> dict[str, int]:
        """Get tool usage summary"""
        return self.tool_counts.copy()

    def print_summary(self) -> None:
        """Print tool usage summary"""
        print("\n" + "="*60)
        print("TOOL USAGE SUMMARY")
        print("="*60)

        total = sum(self.tool_counts.values())

        for tool, count in sorted(self.tool_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                pct = (count / total * 100) if total > 0 else 0

                # Color code
                if tool == "computer" and count > 3:
                    icon = "⚠️ "
                elif tool in ["bash", "str_replace_editor"]:
                    icon = "✅ "
                else:
                    icon = "   "

                print(f"{icon}{tool}: {count} calls ({pct:.1f}%)")

        print(f"\nTotal: {total} tool calls")
        print("="*60)

        # Analysis
        computer_count = self.tool_counts.get("computer", 0)
        direct_count = self.tool_counts.get("bash", 0) + self.tool_counts.get("str_replace_editor", 0)

        if computer_count > direct_count:
            print("⚠️  WARNING: More GUI calls than direct tool calls!")
            print("   Consider optimizing to use bash/edit tools more.")
        elif computer_count > 5:
            print("⚠️  WARNING: High number of computer tool calls")
            print("   This slows down execution and uses more context.")
        else:
            print("✅ Good tool usage - minimal GUI overhead")

        print("="*60 + "\n")
