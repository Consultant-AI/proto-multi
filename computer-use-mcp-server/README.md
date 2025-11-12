# Computer Use MCP Server

A Model Context Protocol (MCP) server that provides computer use capabilities to Claude Code and other MCP clients. This allows AI assistants to interact with your computer through screenshots, mouse control, and keyboard input.

**✨ NEW: Vision-Action-Verification Loop** - This server now includes automatic verification and retry logic to ensure actions actually succeed. See [VERIFICATION_GUIDE.md](VERIFICATION_GUIDE.md) for details.

## Features

This MCP server provides the following tools:

### Screenshot
- `screenshot()` - Capture the entire screen as a compressed JPEG image (512x384, optimized for MCP's 25K token limit)

### High-Level Tools with Verification (NEW)
- `click_with_retry(x, y, max_retries, verify_delay)` - Click with automatic verification and retry
- `type_with_verification(text, max_retries, verify_delay)` - Type text with verification it appeared
- `press_key_with_verification(key, modifiers, max_retries, verify_delay)` - Press key with verification
- `execute_task_with_vision(task_description)` - Execute complex tasks with continuous visual feedback

**Why use these?** They take before/after screenshots, verify actions succeeded, and automatically retry on failure. Perfect for web applications and ensuring reliable automation.

### Mouse Control
- `mouse_move(x, y)` - Move the mouse cursor to specific coordinates
- `left_click()` - Perform a left mouse click
- `right_click()` - Perform a right mouse click
- `double_click()` - Perform a double click
- `mouse_drag(start_x, start_y, end_x, end_y)` - Click and drag from one point to another
- `scroll(direction, amount)` - Scroll in any direction (up/down/left/right)
- `get_cursor_position()` - Get the current mouse cursor position

### Keyboard Control
- `type_text(text, delay_ms)` - Type text with configurable delay between keystrokes (uses AppleScript on macOS for web app compatibility)
- `press_key(key, modifiers)` - Press keys or key combinations (e.g., Ctrl+C, Return, Tab)

## Quick Start

See the comprehensive guides for detailed information:
- **[VERIFICATION_GUIDE.md](VERIFICATION_GUIDE.md)** - How to use the verification and retry system
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Technical details of recent improvements

## Platform Support

This MCP server works across multiple platforms with platform-specific implementations:

- **macOS**: Uses `screencapture` for screenshots, AppleScript for keyboard (web app support), `cliclick` for mouse
- **Linux**: Uses `gnome-screenshot`/`scrot` and `xdotool`
- **Windows**: Uses PowerShell and Windows APIs

## Installation

### Prerequisites

#### macOS
```bash
brew install cliclick
```

#### Linux
```bash
sudo apt-get install xdotool gnome-screenshot
# or
sudo apt-get install xdotool scrot
```

#### Windows
No additional tools required (uses built-in PowerShell).

### Install the MCP Server

1. Navigate to the server directory:
```bash
cd computer-use-mcp-server
```

2. Install using pip:
```bash
pip install -e .
```

This will install the server and make it available as the `computer-use-mcp` command.

## Configuration for Claude Code

To use this MCP server with Claude Code, you need to register it. There are multiple ways to do this:

### Option 1: Using the Command Line (Recommended)

```bash
# Navigate to the server directory
cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-mcp-server

# Add the server to Claude Code
claude mcp add --transport stdio computer-use computer-use-mcp
```

### Option 2: Manual Configuration

Add the following to your Claude Code MCP configuration:

**For local/user scope:**
```bash
# Add to local scope (project-specific, user-private)
claude mcp add --scope local --transport stdio computer-use computer-use-mcp

# Add to user scope (cross-project)
claude mcp add --scope user --transport stdio computer-use computer-use-mcp
```

**For project scope (team-shared):**

Create or edit `.mcp.json` in your project root:
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

### Option 3: Direct Python Execution

If you prefer to run the Python module directly:
```bash
claude mcp add --transport stdio computer-use python -m computer_use_mcp.server
```

## Usage Examples

Once registered with Claude Code, you can ask Claude to interact with your computer:

### Screenshots
- "Take a screenshot of my desktop"
- "Show me what's on my screen"

### Mouse Control
- "Move the mouse to coordinates (500, 300)"
- "Click at the current position"
- "Double-click the icon at (200, 150)"
- "Drag from (100, 100) to (400, 400)"
- "Scroll down 10 units"

### Keyboard Control
- "Type 'Hello, World!'"
- "Press Enter"
- "Press Ctrl+C to copy"
- "Press Ctrl+Shift+S to save"

## Tool Reference

### screenshot()
Takes a screenshot of the entire screen.

**Returns:** Base64-encoded PNG image with data URI prefix

### mouse_move(x: int, y: int)
Moves the mouse cursor to specified coordinates.

**Parameters:**
- `x`: X-coordinate (pixels from left edge)
- `y`: Y-coordinate (pixels from top edge)

### left_click()
Performs a left mouse button click at the current cursor position.

### right_click()
Performs a right mouse button click at the current cursor position.

### double_click()
Performs a double-click at the current cursor position.

### mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int)
Clicks and drags from start position to end position.

**Parameters:**
- `start_x`, `start_y`: Starting coordinates
- `end_x`, `end_y`: Ending coordinates

### scroll(direction: str, amount: int = 5)
Scrolls the mouse wheel.

**Parameters:**
- `direction`: "up", "down", "left", or "right"
- `amount`: Number of scroll units (default: 5)

### type_text(text: str, delay_ms: int = 50)
Types the specified text using the keyboard.

**Parameters:**
- `text`: Text to type
- `delay_ms`: Delay between keystrokes in milliseconds (default: 50)

### press_key(key: str, modifiers: str = "")
Presses a keyboard key or key combination.

**Parameters:**
- `key`: Key name (e.g., "Return", "Tab", "a", "F1")
- `modifiers`: Modifier keys separated by + (e.g., "ctrl", "shift", "alt", "cmd")

**Examples:**
```python
press_key("Return")           # Press Enter
press_key("c", "ctrl")        # Press Ctrl+C
press_key("Tab", "shift")     # Press Shift+Tab
press_key("s", "ctrl+shift")  # Press Ctrl+Shift+S
```

### get_cursor_position()
Returns the current mouse cursor position.

**Returns:** String in format "x,y"

## Security and Permissions

This MCP server requires permissions to:
- Capture screenshots of your screen
- Control your mouse and keyboard
- Access system automation APIs

On macOS, you may need to grant accessibility permissions to:
- Your terminal application
- Python
- The specific tools (cliclick)

Go to System Settings > Privacy & Security > Accessibility to grant these permissions.

On Linux with Wayland, some features may require additional configuration or may work only under X11.

## Architecture

This server is built using:
- **FastMCP**: A Python framework for building MCP servers
- **Platform-specific automation tools**: Different tools for macOS, Linux, and Windows
- **Async/await**: All operations are asynchronous for better performance

The server communicates with MCP clients using the stdio transport protocol, which is the standard for MCP servers.

## Troubleshooting

### "command not found" errors

**macOS:**
```bash
brew install cliclick
```

**Linux:**
```bash
sudo apt-get install xdotool gnome-screenshot
```

### Permission denied errors

On macOS, grant accessibility permissions:
1. Go to System Settings > Privacy & Security > Accessibility
2. Add your terminal app or Python interpreter
3. Restart your terminal

### Screenshots return black images on Linux

If you're using Wayland, try:
1. Switch to X11 session, or
2. Install GNOME Screenshot which has better Wayland support:
   ```bash
   sudo apt-get install gnome-screenshot
   ```

### Key presses don't work

Make sure the target application has focus (click on it first) before sending key commands.

## Development

To modify or extend this server:

1. Edit the source code in `src/computer_use_mcp/server.py`
2. Add new tools by creating functions decorated with `@mcp.tool()`
3. Reinstall the package: `pip install -e .`
4. Restart Claude Code to pick up changes

## Related Projects

This MCP server is inspired by:
- [Anthropic's Computer Use Demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) - The original computer use implementation
- [Model Context Protocol](https://modelcontextprotocol.io/) - The open standard for AI-to-tool connections

## License

MIT License - see LICENSE file for details
