"""
Command-line interface for running the computer-use demo agent directly on the host.

This bypasses the Streamlit UI and Docker container so the agent can control the
local computer via the pyautogui-backed LocalComputerTool.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Any, cast, get_args

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Look for .env in the current directory and parent directories
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass  # dotenv not installed, will use system env vars only

from anthropic.types.beta import (
    BetaContentBlockParam,
    BetaMessageParam,
)

from .loop import APIProvider, sampling_loop
from .tools import ToolResult, ToolVersion


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="computer-use-cli",
        description="Interactive CLI for the Anthropic computer use demo that controls the host computer.",
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-5-20250929",
        help="Claude model to use (default: %(default)s)",
    )
    parser.add_argument(
        "--provider",
        choices=[provider.value for provider in APIProvider],
        default=APIProvider.ANTHROPIC.value,
        help="API provider backing the requests (default: %(default)s)",
    )
    parser.add_argument(
        "--tool-version",
        choices=get_args(ToolVersion),
        default="proto_coding_v1",
        help="Tool group to expose to the model (default: %(default)s)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        help="Max tokens per response (default: %(default)s)",
    )
    parser.add_argument(
        "--only-n-images",
        type=int,
        default=3,
        help="Keep only N most recent screenshots in the prompt (default: %(default)s)",
    )
    parser.add_argument(
        "--thinking-budget",
        type=int,
        default=0,
        help="Optional thinking token budget (default: disabled)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("~/.computer-use-cli").expanduser(),
        help="Directory to store transcripts and screenshots (default: %(default)s)",
    )
    parser.add_argument(
        "--system-prompt",
        default="",
        help="Optional suffix appended to the default system prompt.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Anthropic API key (falls back to ANTHROPIC_API_KEY env var).",
    )
    parser.add_argument(
        "--token-efficient-tools-beta",
        action="store_true",
        help="Enable the token efficient tools beta flag.",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with a predefined task (non-interactive).",
    )
    parser.add_argument(
        "--test-task",
        default=None,
        help="Task to run in test mode (required if --test-mode is set).",
    )
    return parser.parse_args()


class CLIRenderer:
    """Handles console output and artifact persistence."""

    def __init__(self, log_dir: Path):
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        self.run_dir = log_dir.expanduser() / f"session-{timestamp}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.image_dir = self.run_dir / "screens"
        self.image_dir.mkdir(exist_ok=True)
        self.image_index = 0

        self.transcript_path = self.run_dir / "transcript.txt"
        self.transcript_path.write_text(
            "Claude Computer Use CLI session\n"
            f"Started: {datetime.utcnow().isoformat()}Z\n\n"
        )

    def log(self, line: str):
        print(line, flush=True)
        with self.transcript_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def output_callback(self, block: BetaContentBlockParam):
        block_type = block.get("type") if isinstance(block, dict) else None
        if block_type == "text":
            text = cast(str, block.get("text", ""))
            if text:
                for line in text.splitlines():
                    self.log(f"assistant> {line}")
        elif block_type == "thinking":
            thinking = block.get("thinking", "")
            if thinking:
                self.log(f"[thinking] {thinking}")

    def tool_output_callback(self, result: ToolResult, tool_id: str):
        header = f"tool[{tool_id}]"
        if result.system:
            self.log(f"{header} SYSTEM: {result.system}")
        if result.output:
            for line in result.output.splitlines():
                self.log(f"{header} OUT: {line}")
        if result.error:
            for line in result.error.splitlines():
                self.log(f"{header} ERR: {line}")
        if result.base64_image:
            self.image_index += 1
            path = self.image_dir / f"{tool_id}-{self.image_index:03d}.png"
            path.write_bytes(base64.b64decode(result.base64_image))
            self.log(f"{header} image saved to {path}")

    def api_response_callback(
        self,
        request: Any,
        response: Any,
        error: Exception | None,
    ):
        if error:
            self.log(f"[api] error: {error}")


async def _chat_loop(args: argparse.Namespace, api_key: str):
    provider = APIProvider(args.provider)
    renderer = CLIRenderer(args.log_dir)

    # Test mode: run single task and exit
    if args.test_mode:
        if not args.test_task:
            renderer.log("ERROR: --test-task is required when using --test-mode")
            return

        renderer.log("=" * 80)
        renderer.log("Running in TEST MODE")
        renderer.log("=" * 80)
        renderer.log(f"Task: {args.test_task}")
        renderer.log("=" * 80)

        messages: list[BetaMessageParam] = [
            {"role": "user", "content": [{"type": "text", "text": args.test_task}]}
        ]

        try:
            messages = await sampling_loop(
                model=args.model,
                provider=provider,
                system_prompt_suffix=args.system_prompt,
                messages=messages,
                output_callback=renderer.output_callback,
                tool_output_callback=renderer.tool_output_callback,
                api_response_callback=renderer.api_response_callback,
                api_key=api_key,
                only_n_most_recent_images=args.only_n_images,
                max_tokens=args.max_tokens,
                tool_version=args.tool_version,
                thinking_budget=args.thinking_budget or None,
                token_efficient_tools_beta=args.token_efficient_tools_beta,
            )
            renderer.log("=" * 80)
            renderer.log(f"TEST COMPLETE - {len(messages)} messages exchanged")
            renderer.log("=" * 80)
        except Exception as e:
            renderer.log(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
        return

    # Interactive mode
    renderer.log(
        "Starting Claude computer use CLI. Type ':quit' to exit or ':help' for commands."
    )

    messages: list[BetaMessageParam] = []

    async def run_once(user_input: str):
        nonlocal messages
        messages.append({"role": "user", "content": [{"type": "text", "text": user_input}]})
        messages = await sampling_loop(
            model=args.model,
            provider=provider,
            system_prompt_suffix=args.system_prompt,
            messages=messages,
            output_callback=renderer.output_callback,
            tool_output_callback=renderer.tool_output_callback,
            api_response_callback=renderer.api_response_callback,
            api_key=api_key,
            only_n_most_recent_images=args.only_n_images,
            max_tokens=args.max_tokens,
            tool_version=args.tool_version,
            thinking_budget=args.thinking_budget or None,
            token_efficient_tools_beta=args.token_efficient_tools_beta,
        )

    while True:
        try:
            prompt = input("you> ").strip()
        except (KeyboardInterrupt, EOFError):
            renderer.log("Exiting…")
            break

        if not prompt:
            continue
        if prompt in (":quit", ":exit"):
            renderer.log("Goodbye!")
            break
        if prompt == ":help":
            renderer.log(
                "Commands:\n"
                "  :quit / :exit  Stop the session\n"
                "  :history       Show message count\n"
                "All other text is sent to Claude."
            )
            continue
        if prompt == ":history":
            renderer.log(f"Current messages: {len(messages)} (including tool turns)")
            continue

        renderer.log(f"you> {prompt}")
        await run_once(prompt)


def _resolve_api_key(cli_value: str | None) -> str:
    if cli_value:
        return cli_value
    env_key = os.getenv("ANTHROPIC_API_KEY")
    if env_key:
        return env_key
    for path in (
        Path("~/.anthropic/api_key").expanduser(),
        Path("~/.config/anthropic/api_key").expanduser(),
    ):
        if path.exists():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
    raise SystemExit(
        "No API key found. Set ANTHROPIC_API_KEY, pass --api-key, or create ~/.anthropic/api_key."
    )


def main():
    args = _parse_args()
    api_key = _resolve_api_key(args.api_key)
    try:
        asyncio.run(_chat_loop(args, api_key))
    except KeyboardInterrupt:
        print("\nInterrupted, exiting…")


if __name__ == "__main__":
    main()
