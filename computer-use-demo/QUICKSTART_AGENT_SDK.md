# Quick Start - Agent SDK Edition

## Run the WebUI with Agent SDK

### Option 1: Using the startup script (Recommended)

```bash
cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-demo
./start-agent-sdk.sh
```

### Option 2: Direct Python command

```bash
cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-demo
python3 -m computer_use_demo.webui
```

Both commands will:
1. Start the web server on http://localhost:8000
2. Automatically open the UI in Chrome (on macOS)
3. Enable all Agent SDK features automatically

## What You'll See

The web interface will show:
- **"Agent SDK Enabled"** badge in the header
- Same familiar chat interface
- Behind the scenes: session persistence, verification loops, subagents

## First Test

Try this prompt to see Agent SDK in action:

```
Take a screenshot of the desktop, then create a file called test.txt
with "Hello from Agent SDK", and verify it was created correctly.
```

You'll notice:
- **Automatic verification**: The agent will verify the file was created
- **Hybrid tools**: Uses both GUI (screenshot) and direct file operations
- **Session persistence**: Session saved in `~/.claude/projects/webui-XXXXXXXX/`

## What's Different from Normal Mode?

| Feature | Normal Mode | Agent SDK Mode |
|---------|-------------|----------------|
| Session | Lost on refresh | Persists in ~/.claude/ |
| Verification | Manual | Automatic |
| Error handling | Fails immediately | Auto-retry |
| Context | Manual cleanup | Auto-compaction |

## View Session Data

After running tasks, check your session:

```bash
# List sessions
ls ~/.claude/projects/

# View your session transcript
cat ~/.claude/projects/webui-*/transcript.jsonl

# View learned conventions
cat ~/.claude/projects/webui-*/CLAUDE.md

# View statistics
cat ~/.claude/projects/webui-*/metadata.json
```

## Configuration

Edit `.claude/settings.json` to customize:

```json
{
  "agent_sdk": {
    "enabled": true,
    "session_persistence": true,
    "auto_verification": true,
    "subagents_enabled": true
  },
  "verification": {
    "visual_verification": true,
    "structural_verification": true,
    "auto_retry_on_failure": true,
    "max_retries": 3
  }
}
```

## Test Examples

### Example 1: Development Workflow
```
Create a Python script that prints "Hello World", save it as hello.py,
then run it and show me the output.
```

Agent will:
1. Create the file (file operations subagent)
2. Verify file exists (structural check)
3. Run the script (execution subagent)
4. Show output (verification)

### Example 2: Multi-Application
```
Open Firefox, navigate to anthropic.com, take a screenshot,
then create a file summary.txt with what you see.
```

Agent will:
1. Launch Firefox (GUI automation)
2. Verify browser opened (visual verification)
3. Navigate to URL
4. Capture screenshot
5. Analyze and create summary file
6. Verify file created (structural check)

### Example 3: Resumable Sessions

**First run:**
```
Start researching Python async/await patterns and create outline.md
```

**Later (same or different day):**
```
Continue working on the async/await research from before
```

Agent SDK will:
- Load previous session automatically
- Resume from where you left off
- Use learned conventions from CLAUDE.md

## Troubleshooting

### Session not found
If sessions aren't persisting, check:
```bash
ls -la ~/.claude/projects/
# Should show webui-* directories
```

### WebUI won't start
```bash
# Check Python dependencies
pip3 install -r computer_use_demo/requirements.txt

# Check API key
echo $ANTHROPIC_API_KEY
# or
cat ~/.anthropic/api_key
```

### Port already in use
```bash
# Use different port
WEBUI_PORT=8001 python3 -m computer_use_demo.webui
```

## Disable Agent SDK (revert to simple mode)

If you want to go back to the simple loop:

Edit `computer_use_demo/webui.py` line 32:
```python
# Change from:
from .agent_loop import sampling_loop

# Back to:
from .loop import sampling_loop
```

## Documentation

- [Full Agent SDK Integration Guide](AGENT_SDK_INTEGRATION.md)
- [User Guide](README_AGENT_SDK.md)
- [Implementation Details](IMPLEMENTATION_SUMMARY.md)
- [Architecture Diagrams](ARCHITECTURE_DIAGRAM.md)

## Support

For issues or questions:
- Check the documentation above
- Review session logs in `~/.claude/projects/`
- See [AGENT_SDK_INTEGRATION.md](AGENT_SDK_INTEGRATION.md) troubleshooting section

Enjoy the production-grade Agent SDK experience! 🚀
