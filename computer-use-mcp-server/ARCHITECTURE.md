# Computer Use MCP Server - Architecture

## Overview

This MCP (Model Context Protocol) server provides computer interaction capabilities to AI assistants like Claude Code. It exposes tools for taking screenshots, controlling the mouse, and simulating keyboard input.

## Directory Structure

```
computer-use-mcp-server/
├── src/
│   └── computer_use_mcp/
│       ├── __init__.py          # Package initialization
│       └── server.py            # Main MCP server implementation (all tools)
├── pyproject.toml               # Python package configuration
├── README.md                    # Comprehensive documentation
├── QUICK_START.md              # Quick setup guide
├── ARCHITECTURE.md             # This file
├── LICENSE                     # MIT License
└── .gitignore                  # Git ignore patterns
```

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│         Claude Code / MCP Client         │
│                                          │
│  - Sends tool requests via stdio        │
│  - Receives base64 images & responses   │
└──────────────────┬───────────────────────┘
                   │ JSON-RPC over stdio
                   │
┌──────────────────▼───────────────────────┐
│      Computer Use MCP Server             │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  FastMCP Framework                 │ │
│  │  - Tool registration               │ │
│  │  - Request/response handling       │ │
│  │  - Async execution                 │ │
│  └──────────────┬─────────────────────┘ │
│                 │                        │
│  ┌──────────────▼─────────────────────┐ │
│  │  Tool Implementations              │ │
│  │                                    │ │
│  │  Screenshot Tools:                 │ │
│  │    - screenshot()                  │ │
│  │                                    │ │
│  │  Mouse Control Tools:              │ │
│  │    - mouse_move(x, y)              │ │
│  │    - left_click()                  │ │
│  │    - right_click()                 │ │
│  │    - double_click()                │ │
│  │    - mouse_drag(...)               │ │
│  │    - scroll(direction, amount)     │ │
│  │    - get_cursor_position()         │ │
│  │                                    │ │
│  │  Keyboard Control Tools:           │ │
│  │    - type_text(text, delay_ms)     │ │
│  │    - press_key(key, modifiers)     │ │
│  └──────────────┬─────────────────────┘ │
│                 │                        │
└─────────────────┼────────────────────────┘
                  │
    ┌─────────────┴──────────────┐
    │                            │
┌───▼────────┐  ┌───────▼────────┐  ┌────▼─────────┐
│   macOS    │  │     Linux      │  │   Windows    │
│            │  │                │  │              │
│ cliclick   │  │ xdotool        │  │ PowerShell   │
│ screencap  │  │ gnome-ss/scrot │  │ Windows API  │
└────────────┘  └────────────────┘  └──────────────┘
     Platform-specific implementations
```

## Component Details

### 1. FastMCP Framework

The server uses the FastMCP framework, which provides:
- **Automatic tool registration**: Tools are defined using the `@mcp.tool()` decorator
- **JSON-RPC handling**: Manages the MCP protocol communication
- **Stdio transport**: Standard input/output for IPC with Claude Code
- **Async execution**: All tools run asynchronously using `asyncio`

### 2. Tool Implementation Pattern

Each tool follows this pattern:

```python
@mcp.tool()
async def tool_name(param1: type, param2: type = default) -> str:
    """Tool description shown to the AI.

    Args:
        param1: Description of parameter
        param2: Description with default value

    Returns:
        Success message or error description
    """
    try:
        # Platform-specific implementation
        if IS_MAC:
            # macOS implementation using cliclick/screencapture
            ...
        elif IS_LINUX:
            # Linux implementation using xdotool/gnome-screenshot
            ...
        elif IS_WINDOWS:
            # Windows implementation using PowerShell
            ...
        else:
            return f"Unsupported platform: {SYSTEM}"

        return "Success message"

    except Exception as e:
        return f"Error: {str(e)}"
```

### 3. Platform Detection

The server detects the operating system at startup:

```python
SYSTEM = platform.system().lower()
IS_MAC = SYSTEM == "darwin"
IS_LINUX = SYSTEM == "linux"
IS_WINDOWS = SYSTEM == "win32" or SYSTEM == "windows"
```

This enables platform-specific tool implementations while maintaining a consistent interface.

### 4. Screenshot Implementation

Screenshots are handled differently per platform:

**macOS**:
- Uses `screencapture -x` for silent capture
- Saves to temp file
- Encodes as base64
- Returns as data URI: `data:image/png;base64,{data}`

**Linux**:
- Tries `gnome-screenshot`, falls back to `scrot` or ImageMagick `import`
- Same encoding process as macOS

**Windows**:
- Uses PowerShell with System.Drawing APIs
- Captures primary screen
- Same encoding process

### 5. Mouse Control Implementation

Mouse operations use different tools per platform:

| Operation | macOS | Linux | Windows |
|-----------|-------|-------|---------|
| Move | `cliclick m:x,y` | `xdotool mousemove x y` | PowerShell Cursor.Position |
| Click | `cliclick c:.` | `xdotool click 1` | PowerShell mouse_event |
| Drag | `cliclick dd/du` | `xdotool mousedown/up` | PowerShell mouse events |
| Scroll | `cliclick w:amount` | `xdotool click 4/5` | PowerShell mouse_event wheel |

### 6. Keyboard Control Implementation

Keyboard operations:

| Operation | macOS | Linux | Windows |
|-----------|-------|-------|---------|
| Type | `cliclick t:"text"` | `xdotool type "text"` | PowerShell SendKeys |
| Key press | `cliclick kp:key` | `xdotool key key` | PowerShell SendKeys |
| Modifiers | `ctrl+key` | `ctrl+key` | `^key` (Ctrl), `+key` (Shift) |

### 7. Async Command Execution

All platform commands are executed asynchronously:

```python
async def run_command(cmd: str) -> tuple[str, str, int]:
    """Run shell command asynchronously."""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return (stdout.decode(), stderr.decode(), process.returncode or 0)
```

This ensures the MCP server remains responsive while executing system commands.

## MCP Protocol Communication

### Request Flow

1. **Client sends tool request** via stdin:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/call",
     "params": {
       "name": "screenshot",
       "arguments": {}
     }
   }
   ```

2. **Server executes tool**:
   - FastMCP routes to `screenshot()` function
   - Function executes platform-specific command
   - Returns result string

3. **Server sends response** via stdout:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "content": [
         {
           "type": "text",
           "text": "data:image/png;base64,iVBORw0KG..."
         }
       ]
     }
   }
   ```

### Tool Discovery

Claude Code discovers available tools at startup:

```json
{
  "method": "tools/list",
  "params": {}
}
```

The server responds with all registered tools and their schemas.

## Security Model

### Permissions Required

**macOS**:
- Accessibility permissions for terminal/Python
- Screen recording permission (for screenshots)
- Input monitoring permission (for keyboard/mouse)

**Linux**:
- X11 access (or Wayland with compatible tools)
- No special permissions typically needed

**Windows**:
- Script execution policy must allow PowerShell scripts
- User must have interactive desktop session

### Safety Considerations

1. **No network access**: Server only communicates via stdio
2. **Local execution only**: All commands run on the local machine
3. **No file system access**: Tools don't read/write files (except temp screenshots)
4. **User control**: User can monitor and interrupt operations
5. **No privilege escalation**: Runs with user's permissions

## Performance Considerations

### Screenshot Optimization

- **Temp files**: Screenshots use temp files that are auto-cleaned
- **Base64 encoding**: Efficient encoding for transport to Claude
- **Format**: PNG format balances quality and size

### Async Execution

- All operations are async to prevent blocking
- Multiple operations can be queued
- Server remains responsive during long operations

### Platform Tool Startup

- Tools are discovered once at server startup
- Commands are cached (e.g., `which cliclick`)
- No repeated platform checks during operation

## Extending the Server

### Adding New Tools

1. **Define the function** with `@mcp.tool()` decorator
2. **Add type hints** for parameters
3. **Write docstring** (shown to AI)
4. **Implement platform-specific logic**
5. **Return string result**

Example:

```python
@mcp.tool()
async def get_screen_size() -> str:
    """Get the screen resolution.

    Returns:
        Screen size as "width x height"
    """
    try:
        if IS_MAC:
            stdout, _, code = await run_command(
                "system_profiler SPDisplaysDataType | grep Resolution"
            )
            # Parse and return
            ...
        # ... other platforms

        return f"{width} x {height}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Platform-Specific Features

Some features may only work on certain platforms:

```python
@mcp.tool()
async def platform_specific_feature() -> str:
    """Feature description."""
    if not IS_MAC:
        return "This feature only works on macOS"

    # macOS-specific implementation
    ...
```

## Dependencies

### Python Packages
- `mcp[cli]>=1.21.0` - FastMCP framework and CLI tools
- `pillow>=10.0.0` - Image processing (future use)

### System Tools

**macOS**:
- `cliclick` (via Homebrew) - Mouse and keyboard control
- `screencapture` (built-in) - Screenshots

**Linux**:
- `xdotool` - Mouse and keyboard control
- `gnome-screenshot` or `scrot` - Screenshots
- X11 server (or Wayland with compatible tools)

**Windows**:
- PowerShell 5.0+ (built-in)
- .NET Framework (built-in)

## Troubleshooting

### Debug Mode

To see MCP protocol messages:

```bash
computer-use-mcp 2>&1 | tee mcp-debug.log
```

### Common Issues

1. **Tool not found**: Install platform-specific tools
2. **Permission denied**: Grant accessibility permissions (macOS)
3. **Blank screenshots**: Check screen recording permissions
4. **Keys not working**: Ensure target app has focus

### Testing Individual Tools

You can test the server manually by sending JSON-RPC messages:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | computer-use-mcp
```

## Related Documentation

- [README.md](README.md) - User-facing documentation
- [QUICK_START.md](QUICK_START.md) - Setup guide
- [Model Context Protocol Docs](https://modelcontextprotocol.io/) - MCP specification
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk) - Framework docs

## Version History

- **v0.1.0** (2025-01-11)
  - Initial release
  - Screenshot, mouse, and keyboard tools
  - macOS, Linux, Windows support
  - FastMCP-based implementation
