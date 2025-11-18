#!/usr/bin/env python3
"""
Test script for CEO agent with medium-level task.
This simulates what happens when a user gives a medium complexity task.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from anthropic.types.beta import BetaMessageParam
from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.tools import ToolVersion


async def test_medium_task():
    """Test CEO agent with a medium-level task that should trigger planning."""

    # Medium task: Build a user authentication system
    task = """Create a simple user authentication system with the following:
1. A user registration module that validates email and password
2. A login function that checks credentials
3. Password hashing for security
4. Basic error handling
5. Unit tests for the key functions

Place all files in a new 'auth_system' directory."""

    print("=" * 80)
    print("Testing CEO Agent with Medium-Level Task")
    print("=" * 80)
    print(f"\nTask: {task}")
    print("\n" + "=" * 80)
    print("Starting execution...\n")

    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set")
        return

    # Create initial message
    messages: list[BetaMessageParam] = [
        {
            "role": "user",
            "content": [{"type": "text", "text": task}]
        }
    ]

    # Track outputs
    outputs = []
    tool_calls = []

    def output_callback(block):
        """Capture agent output."""
        if isinstance(block, dict):
            block_type = block.get("type")
            if block_type == "text":
                text = block.get("text", "")
                if text:
                    print(f"[AGENT] {text}")
                    outputs.append(text)
            elif block_type == "thinking":
                thinking = block.get("thinking", "")
                if thinking:
                    print(f"[THINKING] {thinking[:100]}...")

    def tool_output_callback(result, tool_id):
        """Capture tool execution."""
        tool_name = tool_id.split("_")[0] if "_" in tool_id else tool_id
        tool_calls.append(tool_name)

        if result.output:
            output_preview = result.output[:200].replace("\n", " ")
            print(f"[TOOL:{tool_name}] {output_preview}...")

        if result.error:
            print(f"[TOOL:{tool_name}] ERROR: {result.error}")

    def api_response_callback(request, response, error):
        """Capture API errors."""
        if error:
            print(f"[API ERROR] {error}")

    try:
        # Run the sampling loop
        result_messages = await sampling_loop(
            model="claude-sonnet-4-5-20250929",
            provider=APIProvider.ANTHROPIC,
            system_prompt_suffix="",
            messages=messages,
            output_callback=output_callback,
            tool_output_callback=tool_output_callback,
            api_response_callback=api_response_callback,
            api_key=api_key,
            only_n_most_recent_images=3,
            max_tokens=4096,
            tool_version="proto_coding_v1",
            thinking_budget=None,
            token_efficient_tools_beta=False,
        )

        print("\n" + "=" * 80)
        print("Execution Complete")
        print("=" * 80)
        print(f"\nTotal messages exchanged: {len(result_messages)}")
        print(f"Total tool calls: {len(tool_calls)}")
        print(f"\nTools used: {', '.join(set(tool_calls))}")

        # Check if planning tools were used
        planning_tools_used = [t for t in tool_calls if t in ['create_planning_docs', 'delegate_task', 'read_planning']]

        print("\n" + "=" * 80)
        print("Analysis")
        print("=" * 80)

        if planning_tools_used:
            print(f"✓ Planning tools were used: {', '.join(planning_tools_used)}")
            print("✓ CEO agent recognized this as a medium/complex task")
        else:
            print("⚠ No planning tools were used")
            print("  This suggests the CEO agent handled it directly")

        # Check if auth_system directory was created
        auth_dir = Path("auth_system")
        if auth_dir.exists():
            print(f"✓ Created auth_system directory")
            files = list(auth_dir.glob("**/*.py"))
            print(f"✓ Created {len(files)} Python files")
            for f in files:
                print(f"  - {f.name}")
        else:
            print("⚠ auth_system directory not found")

        # Check for planning documents
        planning_dir = Path(".proto/planning")
        if planning_dir.exists():
            projects = [d for d in planning_dir.iterdir() if d.is_dir()]
            if projects:
                print(f"✓ Created planning documents in {len(projects)} project(s)")
                for proj in projects:
                    docs = list(proj.glob("*.md"))
                    print(f"  - {proj.name}: {len(docs)} documents")
            else:
                print("⚠ No planning projects found")
        else:
            print("⚠ No .proto/planning directory")

        return True

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_medium_task())
    sys.exit(0 if success else 1)
