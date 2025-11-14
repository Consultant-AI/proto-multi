#!/usr/bin/env python3
"""
Direct test of the computer-use CLI to see what output it produces.
"""

import asyncio
import os
from pathlib import Path

async def test_cli_direct():
    """Test the CLI directly to see its output."""

    # Read API key
    api_key_path = Path.home() / ".anthropic" / "api_key"
    if api_key_path.exists():
        api_key = api_key_path.read_text().strip()
        os.environ["ANTHROPIC_API_KEY"] = api_key
    else:
        print("ERROR: API key not found at ~/.anthropic/api_key")
        print("Please create the file with your API key")
        return

    print("Starting computer-use CLI directly...")
    print("="*60)

    import shutil
    python_cmd = shutil.which("python3") or shutil.which("python")

    demo_dir = "/Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-demo"

    process = await asyncio.create_subprocess_exec(
        python_cmd,
        "-m",
        "computer_use_demo.cli",
        "--model",
        "claude-sonnet-4-5-20250929",
        "--tool-version",
        "computer_use_local",
        cwd=demo_dir,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env={**os.environ, "ANTHROPIC_API_KEY": api_key},
    )

    print("Process started, reading output...")

    # Read initial output
    for i in range(10):
        line = await process.stdout.readline()
        if line:
            print(f"[{i}] {line.decode().rstrip()}")
        else:
            break

    # Send a prompt
    print("\nSending prompt: 'Take a screenshot'")
    process.stdin.write(b"Take a screenshot\n")
    await process.stdin.drain()

    # Read response
    print("\nReading response...")
    for i in range(50):
        line = await process.stdout.readline()
        if line:
            decoded = line.decode().rstrip()
            print(f"[{i}] {decoded}")
            if "you>" in decoded:
                print("\nFound 'you>' prompt, stopping...")
                break
        await asyncio.sleep(0.1)

    # Cleanup
    process.stdin.write(b":quit\n")
    await process.stdin.drain()
    await process.wait()

    print("\n" + "="*60)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(test_cli_direct())
