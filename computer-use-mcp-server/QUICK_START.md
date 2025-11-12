# Quick Start Guide

## Prerequisites Installation

### macOS (what you're currently using)

Install cliclick for mouse and keyboard control:

```bash
brew install cliclick
```

If you don't have Homebrew installed, install it first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Linux

```bash
sudo apt-get update
sudo apt-get install xdotool gnome-screenshot
```

### Windows

No additional tools needed - uses built-in PowerShell.

## Installation Steps

1. **Install the MCP server** (already done!):
   ```bash
   cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-mcp-server
   pip3 install -e .
   ```

2. **Install cliclick on macOS**:
   ```bash
   brew install cliclick
   ```

3. **Grant Accessibility Permissions** (macOS only):
   - Go to: System Settings > Privacy & Security > Accessibility
   - Add and enable:
     - Your Terminal app (e.g., Terminal, iTerm2, VSCode Terminal)
     - Python
     - cliclick (if prompted)
   - Restart your terminal after granting permissions

4. **Register with Claude Code**:
   ```bash
   # Make sure you're in the server directory
   cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-mcp-server

   # Add to Claude Code (user scope - accessible from all projects)
   claude mcp add --scope user --transport stdio computer-use computer-use-mcp
   ```

   Or for local/project scope:
   ```bash
   # Local scope (project-specific, user-private)
   claude mcp add --scope local --transport stdio computer-use computer-use-mcp
   ```

5. **Restart Claude Code** to load the new MCP server

## Testing the Installation

After installation, you can test the MCP server by asking Claude Code:

1. **Test screenshot**:
   - "Take a screenshot"
   - "Show me what's on my screen"

2. **Test mouse**:
   - "Get the current cursor position"
   - "Move the mouse to coordinates (500, 500)"

3. **Test keyboard**:
   - "Type 'Hello World' in the current window"

## Usage Examples

### Screenshots
- "Take a screenshot and describe what you see"
- "Capture my screen and find the browser window"

### Mouse Control
- "Move mouse to (800, 600)"
- "Click at the current position"
- "Double-click at coordinates (300, 200)"
- "Right-click to open context menu"
- "Drag from (100, 100) to (500, 500)"
- "Scroll down 10 times"

### Keyboard Control
- "Type 'Hello, World!'"
- "Press Enter key"
- "Press Ctrl+C to copy"
- "Press Cmd+Tab to switch apps" (macOS)
- "Press Alt+Tab to switch apps" (Windows/Linux)

## Common Issues and Solutions

### Issue: "cliclick not found" error on macOS

**Solution**: Install cliclick:
```bash
brew install cliclick
```

### Issue: Permission denied or accessibility errors

**Solution**: Grant accessibility permissions:
1. System Settings > Privacy & Security > Accessibility
2. Add your terminal app and Python
3. Restart terminal

### Issue: MCP server not showing up in Claude Code

**Solution**:
1. Verify installation: `which computer-use-mcp`
2. Check if it's registered: `claude mcp list`
3. Try re-registering with full path:
   ```bash
   claude mcp add --transport stdio computer-use "$(which computer-use-mcp)"
   ```
4. Restart Claude Code

### Issue: Screenshots come back blank or black

**Solution** (Linux with Wayland):
- Switch to X11 session, or
- Install GNOME Screenshot: `sudo apt-get install gnome-screenshot`

### Issue: Keys don't work or type in wrong place

**Solution**: Make sure the target application window has focus before sending keyboard commands.

## Verifying Installation

Run these commands to verify everything is set up:

```bash
# 1. Check if the MCP server is installed
which computer-use-mcp

# 2. Check if cliclick is installed (macOS only)
which cliclick

# 3. Check if it's registered with Claude Code
claude mcp list

# 4. Test the server directly (should show JSON-RPC messages)
# Press Ctrl+C to exit after testing
computer-use-mcp
```

## Next Steps

Once installed and configured:

1. Open Claude Code
2. Start a conversation
3. Ask Claude to take a screenshot or control your computer
4. Claude will automatically use the MCP tools when needed

## Advanced Configuration

### Using .mcp.json for Team Projects

Create `.mcp.json` in your project root for team-shared configuration:

```json
{
  "mcpServers": {
    "computer-use": {
      "command": "computer-use-mcp",
      "transport": "stdio"
    }
  }
}
```

Commit this file to version control so your team can use it.

### Environment Variables

You can set environment variables for the MCP server:

```bash
# Example: Custom output directory
export COMPUTER_USE_OUTPUT_DIR="/tmp/screenshots"
```

## Security Notes

This MCP server has powerful capabilities:
- It can see your entire screen
- It can control your mouse and keyboard
- It can interact with any application

**Best Practices**:
- Only use with trusted projects
- Review Claude's actions before confirming sensitive operations
- Don't use in production environments without additional safeguards
- Consider using in a VM or isolated environment for sensitive work

## Troubleshooting

If you encounter issues:

1. Check the logs: Claude Code usually shows MCP server errors in the output
2. Test the server manually: Run `computer-use-mcp` directly to see if it starts
3. Verify permissions: Accessibility permissions are required on macOS
4. Check dependencies: Make sure cliclick (macOS) or xdotool (Linux) are installed

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review the [computer-use-demo](../computer-use-demo) for related examples
- File issues on GitHub if you encounter problems

## Summary of Commands

```bash
# macOS Setup
brew install cliclick
cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-mcp-server
pip3 install -e .
claude mcp add --scope user --transport stdio computer-use computer-use-mcp

# Linux Setup
sudo apt-get install xdotool gnome-screenshot
cd /path/to/computer-use-mcp-server
pip3 install -e .
claude mcp add --scope user --transport stdio computer-use computer-use-mcp

# Windows Setup (PowerShell)
cd \path\to\computer-use-mcp-server
pip install -e .
claude mcp add --scope user --transport stdio computer-use computer-use-mcp
```

That's it! You're ready to use computer control with Claude Code.
