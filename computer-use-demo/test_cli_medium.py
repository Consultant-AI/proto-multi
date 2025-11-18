#!/usr/bin/env python3
"""
Test CEO agent with medium-level task through CLI.
This script runs the agent and monitors its behavior.
"""

import asyncio
import os
import sys
from pathlib import Path

# Load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass

# Check API key is available
if not os.getenv("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not set")
    print("Please create a .env file with: ANTHROPIC_API_KEY=your-key-here")
    sys.exit(1)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from anthropic.types.beta import BetaMessageParam
from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.tools import ToolVersion


async def main():
    """Run medium-level task test."""

    # Medium-level task that should trigger planning
    task = """Create a simple user authentication system with the following:
1. A user registration module that validates email and password
2. A login function that checks credentials
3. Password hashing for security using bcrypt
4. Basic error handling
5. Unit tests for the key functions

Place all files in a new 'auth_system' directory."""

    print("=" * 80)
    print("TESTING CEO AGENT WITH MEDIUM-LEVEL TASK")
    print("=" * 80)
    print(f"\nTask:\n{task}\n")
    print("=" * 80)
    print("\nExpected behavior:")
    print("  - CEO agent should recognize this as a medium/complex task")
    print("  - May create planning documents in .proto/planning/")
    print("  - Should organize implementation systematically")
    print("  - Should create auth_system/ directory with files")
    print("\n" + "=" * 80)
    print("\nStarting execution...\n")

    messages: list[BetaMessageParam] = [
        {"role": "user", "content": [{"type": "text", "text": task}]}
    ]

    tool_usage = []
    planning_tools_used = []

    def output_callback(block):
        """Track agent output."""
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text", "")
            if text:
                # Print agent's response
                for line in text.splitlines():
                    print(f"[AGENT] {line}")

    def tool_output_callback(result, tool_id):
        """Track tool usage."""
        # Extract tool name from tool_id (format: toolu_01XYZ...)
        tool_name = "unknown"
        if result.output and "Tool:" in result.output[:100]:
            # Try to extract from output
            for line in result.output.split("\n")[:5]:
                if "create_planning_docs" in line:
                    tool_name = "create_planning_docs"
                    break
                elif "delegate_task" in line:
                    tool_name = "delegate_task"
                    break
                elif "read_planning" in line:
                    tool_name = "read_planning"
                    break

        # Check result for tool indicators
        if not tool_name or tool_name == "unknown":
            if result.base64_image:
                tool_name = "computer"
            elif result.output:
                output_lower = result.output.lower()
                if "created" in output_lower or "mkdir" in output_lower:
                    tool_name = "bash"
                elif "editing" in output_lower or "file" in output_lower:
                    tool_name = "edit"

        tool_usage.append(tool_name)

        if tool_name in ["create_planning_docs", "delegate_task", "read_planning"]:
            planning_tools_used.append(tool_name)
            print(f"\n🎯 PLANNING TOOL USED: {tool_name}")
            if result.output:
                print(f"   Output: {result.output[:200]}...")
        else:
            print(f"[TOOL] {tool_name}: ", end="")
            if result.output:
                preview = result.output[:100].replace("\n", " ")
                print(preview + ("..." if len(result.output) > 100 else ""))
            elif result.error:
                print(f"ERROR - {result.error[:100]}")
            else:
                print("(no output)")

    def api_response_callback(request, response, error):
        """Track API errors."""
        if error:
            print(f"[API ERROR] {error}")

    try:
        result_messages = await sampling_loop(
            model="claude-sonnet-4-5-20250929",
            provider=APIProvider.ANTHROPIC,
            system_prompt_suffix="",
            messages=messages,
            output_callback=output_callback,
            tool_output_callback=tool_output_callback,
            api_response_callback=api_response_callback,
            api_key=os.environ["ANTHROPIC_API_KEY"],
            only_n_most_recent_images=3,
            max_tokens=4096,
            tool_version="proto_coding_v1",
            thinking_budget=None,
            token_efficient_tools_beta=False,
        )

        # Analyze results
        print("\n" + "=" * 80)
        print("EXECUTION COMPLETE - ANALYSIS")
        print("=" * 80)

        print(f"\nTotal messages: {len(result_messages)}")
        print(f"Total tool calls: {len(tool_usage)}")
        print(f"Tools used: {', '.join(set(tool_usage))}")

        if planning_tools_used:
            print(f"\n✓ Planning tools were used: {', '.join(set(planning_tools_used))}")
            print("✓ CEO agent engaged planning capabilities")
        else:
            print("\n⚠ No planning tools detected")
            print("  Agent may have handled task directly")

        # Check for created artifacts
        auth_dir = Path("auth_system")
        if auth_dir.exists():
            print(f"\n✓ Created auth_system directory")
            py_files = list(auth_dir.glob("**/*.py"))
            print(f"✓ Created {len(py_files)} Python files:")
            for f in py_files:
                print(f"  - {f.relative_to(auth_dir)}")
        else:
            print("\n⚠ auth_system directory not found")

        # Check for planning documents
        planning_dir = Path(".proto/planning")
        if planning_dir.exists():
            projects = [d for d in planning_dir.iterdir() if d.is_dir()]
            if projects:
                print(f"\n✓ Created planning documents:")
                for proj in projects:
                    docs = list(proj.glob("*.md"))
                    print(f"  - {proj.name}: {len(docs)} documents")
            else:
                print("\n⚠ No planning projects found")
        else:
            print("\n⚠ No .proto/planning directory")

        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
