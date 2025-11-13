"""
MCP Server providing computer use capabilities for Claude Code.

Provides tools for:
- Taking screenshots
- Moving and clicking the mouse
- Typing and pressing keyboard keys
- Scrolling and other interactions

Works on macOS, Linux, and Windows with platform-specific implementations.
"""

import asyncio
import base64
import hashlib
import os
import platform
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent, TextContent
from PIL import Image

# Initialize FastMCP server
mcp = FastMCP("computer-use")

# Platform detection
SYSTEM = platform.system().lower()
IS_MAC = SYSTEM == "darwin"
IS_LINUX = SYSTEM == "linux"
IS_WINDOWS = SYSTEM == "win32" or SYSTEM == "windows"

# Global variables for screen dimensions and scaling
_ACTUAL_WIDTH = None
_ACTUAL_HEIGHT = None
_DISPLAY_WIDTH = 1024
_DISPLAY_HEIGHT = 768


async def run_command(cmd: str) -> tuple[str, str, int]:
    """Run a shell command asynchronously and return stdout, stderr, returncode."""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", errors="ignore"),
        stderr.decode("utf-8", errors="ignore"),
        process.returncode or 0,
    )


async def get_screen_size() -> tuple[int, int]:
    """Get the actual screen dimensions.

    Returns:
        Tuple of (width, height) in pixels
    """
    global _ACTUAL_WIDTH, _ACTUAL_HEIGHT

    if _ACTUAL_WIDTH is not None and _ACTUAL_HEIGHT is not None:
        return _ACTUAL_WIDTH, _ACTUAL_HEIGHT

    try:
        if IS_MAC:
            # Use system_profiler to get display info
            cmd = "system_profiler SPDisplaysDataType | grep Resolution"
            stdout, stderr, code = await run_command(cmd)
            if code == 0 and stdout:
                # Parse output like "Resolution: 2560 x 1600"
                import re
                match = re.search(r'(\d+) x (\d+)', stdout)
                if match:
                    _ACTUAL_WIDTH = int(match.group(1))
                    _ACTUAL_HEIGHT = int(match.group(2))
                    return _ACTUAL_WIDTH, _ACTUAL_HEIGHT

        elif IS_LINUX:
            # Use xrandr to get screen info
            cmd = "xrandr | grep '*' | head -1"
            stdout, stderr, code = await run_command(cmd)
            if code == 0 and stdout:
                import re
                match = re.search(r'(\d+)x(\d+)', stdout)
                if match:
                    _ACTUAL_WIDTH = int(match.group(1))
                    _ACTUAL_HEIGHT = int(match.group(2))
                    return _ACTUAL_WIDTH, _ACTUAL_HEIGHT

        elif IS_WINDOWS:
            # Use PowerShell to get screen dimensions
            ps_script = """
            Add-Type -AssemblyName System.Windows.Forms
            $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            Write-Output "$($screen.Width)x$($screen.Height)"
            """
            cmd = f'powershell -Command "{ps_script}"'
            stdout, stderr, code = await run_command(cmd)
            if code == 0 and stdout:
                width, height = stdout.strip().split('x')
                _ACTUAL_WIDTH = int(width)
                _ACTUAL_HEIGHT = int(height)
                return _ACTUAL_WIDTH, _ACTUAL_HEIGHT
    except:
        pass

    # Fallback to common resolutions
    _ACTUAL_WIDTH = 1920
    _ACTUAL_HEIGHT = 1080
    return _ACTUAL_WIDTH, _ACTUAL_HEIGHT


async def scale_coordinates(x: int, y: int) -> tuple[int, int]:
    """Scale coordinates from display size to actual screen size.

    Args:
        x: X coordinate from the resized screenshot
        y: Y coordinate from the resized screenshot

    Returns:
        Tuple of (scaled_x, scaled_y) for actual screen
    """
    actual_width, actual_height = await get_screen_size()

    scaled_x = int(x * actual_width / _DISPLAY_WIDTH)
    scaled_y = int(y * actual_height / _DISPLAY_HEIGHT)

    return scaled_x, scaled_y


async def take_screenshot_hash() -> str:
    """Take a screenshot and return a hash for comparison purposes.

    This is a helper function used internally for detecting screen changes.
    Returns a hash of the screenshot for comparison.
    """
    # Create temporary file for screenshot
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    try:
        if IS_MAC:
            cmd = f"screencapture -x {temp_path}"
            await run_command(cmd)
        elif IS_LINUX:
            if subprocess.run(["which", "gnome-screenshot"], capture_output=True).returncode == 0:
                cmd = f"gnome-screenshot -f {temp_path}"
            elif subprocess.run(["which", "scrot"], capture_output=True).returncode == 0:
                cmd = f"scrot {temp_path}"
            elif subprocess.run(["which", "import"], capture_output=True).returncode == 0:
                cmd = f"import -window root {temp_path}"
            else:
                return ""
            await run_command(cmd)
        elif IS_WINDOWS:
            ps_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
            $bitmap.Save('{temp_path}', [System.Drawing.Imaging.ImageFormat]::Png)
            """
            cmd = f'powershell -Command "{ps_script}"'
            await run_command(cmd)

        if not os.path.exists(temp_path):
            return ""

        # Read file and compute hash for comparison
        with open(temp_path, "rb") as f:
            file_data = f.read()
            return hashlib.md5(file_data).hexdigest()
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def encode_image_to_base64(image_path: str, target_width: int = 1024, target_height: int = 768, quality: int = 35) -> str:
    """Read an image file, resize it, and encode it as base64 JPEG.

    Uses JPEG compression with lower quality to reduce token usage while maintaining coordinate mapping.
    At 1024x768 with quality=35, provides adequate detail for computer use with smaller file size.

    Args:
        image_path: Path to the image file
        target_width: Target width for resizing (default: 1024)
        target_height: Target height for resizing (default: 768)
        quality: JPEG quality 0-100 (default: 35)

    Returns:
        Base64-encoded JPEG image
    """
    # Open and resize image
    img = Image.open(image_path)
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Convert to RGB for JPEG (JPEG doesn't support transparency)
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Save as JPEG with specified quality
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


# Screenshot Tools

@mcp.tool()
async def screenshot() -> list[ImageContent | TextContent]:
    """Take a screenshot of the entire screen and return it as base64-encoded PNG.

    Returns:
        Base64-encoded PNG image of the screen
    """
    # Create temporary file for screenshot
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    try:
        if IS_MAC:
            # macOS: use screencapture
            cmd = f"screencapture -x {temp_path}"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return [TextContent(type="text", text=f"Error taking screenshot: {stderr}")]

        elif IS_LINUX:
            # Linux: try multiple tools
            if subprocess.run(["which", "gnome-screenshot"], capture_output=True).returncode == 0:
                cmd = f"gnome-screenshot -f {temp_path}"
            elif subprocess.run(["which", "scrot"], capture_output=True).returncode == 0:
                cmd = f"scrot {temp_path}"
            elif subprocess.run(["which", "import"], capture_output=True).returncode == 0:
                cmd = f"import -window root {temp_path}"
            else:
                return [TextContent(type="text", text="Error: No screenshot tool found. Install gnome-screenshot, scrot, or imagemagick.")]

            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return [TextContent(type="text", text=f"Error taking screenshot: {stderr}")]

        elif IS_WINDOWS:
            # Windows: use PowerShell
            ps_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
            $bitmap.Save('{temp_path}', [System.Drawing.Imaging.ImageFormat]::Png)
            """
            cmd = f'powershell -Command "{ps_script}"'
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return [TextContent(type="text", text=f"Error taking screenshot: {stderr}")]
        else:
            return [TextContent(type="text", text=f"Unsupported platform: {SYSTEM}")]

        # Check if file was created
        if not os.path.exists(temp_path):
            return [TextContent(type="text", text="Error: Screenshot file was not created")]

        # Get actual screen size before encoding
        await get_screen_size()

        # Read the image file and return as proper ImageContent
        base64_image = encode_image_to_base64(temp_path)
        return [
            ImageContent(
                type="image",
                data=base64_image,
                mimeType="image/jpeg"
            )
        ]

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


# Mouse Control Tools

@mcp.tool()
async def mouse_move(x: int, y: int) -> str:
    """Move the mouse cursor to the specified coordinates.

    Args:
        x: The x-coordinate to move to
        y: The y-coordinate to move to

    Returns:
        Success or error message
    """
    try:
        # Scale coordinates if needed
        x, y = await scale_coordinates(x, y)

        if IS_MAC:
            # macOS: use cliclick
            cmd = f"cliclick m:{x},{y}"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}. You may need to install cliclick: brew install cliclick"

        elif IS_LINUX:
            # Linux: use xdotool
            cmd = f"xdotool mousemove {x} {y}"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}. You may need to install xdotool: sudo apt-get install xdotool"

        elif IS_WINDOWS:
            # Windows: use PowerShell
            ps_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point({x}, {y})
            """
            cmd = f'powershell -Command "{ps_script}"'
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"
        else:
            return f"Unsupported platform: {SYSTEM}"

        return f"Mouse moved to ({x}, {y})"

    except Exception as e:
        return f"Error moving mouse: {str(e)}"


@mcp.tool()
async def left_click(x: int | None = None, y: int | None = None) -> str:
    """Perform a left mouse click at the current cursor position or specified coordinates.

    NOTE: For better reliability, consider using click_with_retry() which verifies the click succeeded.

    Args:
        x: Optional x-coordinate to click at
        y: Optional y-coordinate to click at

    Returns:
        Success or error message with screenshot
    """
    try:
        # Scale coordinates if needed
        if x is not None and y is not None:
            x, y = await scale_coordinates(x, y)

        if IS_MAC:
            if x is not None and y is not None:
                # Click at specific coordinates (combines move + click in one command)
                cmd = f"cliclick c:{x},{y}"
            else:
                # Click at current position
                cmd = "cliclick c:."
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}. You may need to install cliclick: brew install cliclick"

            # For macOS, ensure proper focus and interaction
            # Brief delay to let the click register
            await asyncio.sleep(0.1)

        elif IS_LINUX:
            if x is not None and y is not None:
                # Move mouse and click in single command (like reference implementation)
                cmd = f"xdotool mousemove --sync {x} {y} click 1"
            else:
                # Click at current position
                cmd = "xdotool click 1"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"

        elif IS_WINDOWS:
            if x is not None and y is not None:
                # Move to coordinates first
                await mouse_move(x, y)

            ps_script = """
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.Cursor]::Position | Out-Null
            $signature = @'
            [DllImport("user32.dll",CharSet=CharSet.Auto, CallingConvention=CallingConvention.StdCall)]
            public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);
'@
            $SendMouseClick = Add-Type -memberDefinition $signature -name "Win32MouseEventNew" -namespace Win32Functions -passThru
            $SendMouseClick::mouse_event(0x02, 0, 0, 0, 0)
            $SendMouseClick::mouse_event(0x04, 0, 0, 0, 0)
            """
            cmd = f'powershell -Command "{ps_script}"'
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"
        else:
            return f"Unsupported platform: {SYSTEM}"

        # Wait for UI to settle (like reference implementation)
        await asyncio.sleep(2.0)

        if x is not None and y is not None:
            return f"Left click performed at ({x}, {y})"
        else:
            return "Left click performed at current position"

    except Exception as e:
        return f"Error performing left click: {str(e)}"


@mcp.tool()
async def right_click() -> str:
    """Perform a right mouse click at the current cursor position.

    Returns:
        Success or error message
    """
    try:
        if IS_MAC:
            cmd = "cliclick rc:."
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}. You may need to install cliclick: brew install cliclick"

        elif IS_LINUX:
            cmd = "xdotool click 3"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"

        elif IS_WINDOWS:
            ps_script = """
            Add-Type -AssemblyName System.Windows.Forms
            $signature = @'
            [DllImport("user32.dll",CharSet=CharSet.Auto, CallingConvention=CallingConvention.StdCall)]
            public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);
'@
            $SendMouseClick = Add-Type -memberDefinition $signature -name "Win32MouseEventNew2" -namespace Win32Functions -passThru
            $SendMouseClick::mouse_event(0x08, 0, 0, 0, 0)
            $SendMouseClick::mouse_event(0x10, 0, 0, 0, 0)
            """
            cmd = f'powershell -Command "{ps_script}"'
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"
        else:
            return f"Unsupported platform: {SYSTEM}"

        return "Right click performed"

    except Exception as e:
        return f"Error performing right click: {str(e)}"


@mcp.tool()
async def double_click(x: int | None = None, y: int | None = None) -> str:
    """Perform a double left mouse click at the current cursor position or specified coordinates.

    Args:
        x: Optional x-coordinate to click at
        y: Optional y-coordinate to click at

    Returns:
        Success or error message with screenshot
    """
    try:
        # Scale coordinates if needed
        if x is not None and y is not None:
            x, y = await scale_coordinates(x, y)

        if IS_MAC:
            if x is not None and y is not None:
                # Double click at specific coordinates
                cmd = f"cliclick dc:{x},{y}"
            else:
                # Double click at current position
                cmd = "cliclick dc:."
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}. You may need to install cliclick: brew install cliclick"

        elif IS_LINUX:
            if x is not None and y is not None:
                # Move mouse and double click in single command
                cmd = f"xdotool mousemove --sync {x} {y} click --repeat 2 --delay 100 1"
            else:
                # Double click at current position
                cmd = "xdotool click --repeat 2 --delay 100 1"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"

        elif IS_WINDOWS:
            # Perform two clicks with small delay
            await left_click(x, y)
            await asyncio.sleep(0.1)
            await left_click()  # Second click at current position
        else:
            return f"Unsupported platform: {SYSTEM}"

        # Wait for UI to settle (like reference implementation)
        await asyncio.sleep(2.0)

        if x is not None and y is not None:
            return f"Double click performed at ({x}, {y})"
        else:
            return "Double click performed at current position"

    except Exception as e:
        return f"Error performing double click: {str(e)}"


@mcp.tool()
async def mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int) -> str:
    """Click and drag the mouse from start position to end position.

    Args:
        start_x: Starting x-coordinate
        start_y: Starting y-coordinate
        end_x: Ending x-coordinate
        end_y: Ending y-coordinate

    Returns:
        Success or error message
    """
    try:
        # Scale coordinates
        start_x, start_y = await scale_coordinates(start_x, start_y)
        end_x, end_y = await scale_coordinates(end_x, end_y)

        if IS_MAC:
            cmd = f"cliclick m:{start_x},{start_y} dd:{start_x},{start_y} m:{end_x},{end_y} du:{end_x},{end_y}"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}. You may need to install cliclick: brew install cliclick"

        elif IS_LINUX:
            cmd = f"xdotool mousemove {start_x} {start_y} mousedown 1 mousemove {end_x} {end_y} mouseup 1"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"

        elif IS_WINDOWS:
            # Move to start, press, move to end, release
            await mouse_move(start_x, start_y)
            ps_script = """
            Add-Type -AssemblyName System.Windows.Forms
            $signature = @'
            [DllImport("user32.dll",CharSet=CharSet.Auto, CallingConvention=CallingConvention.StdCall)]
            public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);
'@
            $SendMouseClick = Add-Type -memberDefinition $signature -name "Win32MouseEventNew3" -namespace Win32Functions -passThru
            $SendMouseClick::mouse_event(0x02, 0, 0, 0, 0)
            """
            await run_command(f'powershell -Command "{ps_script}"')
            await mouse_move(end_x, end_y)
            ps_script = """
            Add-Type -AssemblyName System.Windows.Forms
            $signature = @'
            [DllImport("user32.dll",CharSet=CharSet.Auto, CallingConvention=CallingConvention.StdCall)]
            public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);
'@
            $SendMouseClick = Add-Type -memberDefinition $signature -name "Win32MouseEventNew4" -namespace Win32Functions -passThru
            $SendMouseClick::mouse_event(0x04, 0, 0, 0, 0)
            """
            await run_command(f'powershell -Command "{ps_script}"')
        else:
            return f"Unsupported platform: {SYSTEM}"

        return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"

    except Exception as e:
        return f"Error performing drag: {str(e)}"


@mcp.tool()
async def scroll(direction: Literal["up", "down", "left", "right"], amount: int = 5) -> str:
    """Scroll the mouse wheel in the specified direction.

    Args:
        direction: Direction to scroll (up, down, left, right)
        amount: Number of scroll units (default: 5)

    Returns:
        Success or error message
    """
    try:
        if IS_MAC:
            # cliclick uses positive for down/right, negative for up/left
            if direction == "up":
                cmd = f"cliclick w:-{amount}"
            elif direction == "down":
                cmd = f"cliclick w:{amount}"
            elif direction == "left":
                cmd = f"cliclick h:-{amount}"
            elif direction == "right":
                cmd = f"cliclick h:{amount}"
            else:
                return f"Invalid direction: {direction}"

            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}. You may need to install cliclick: brew install cliclick"

        elif IS_LINUX:
            # xdotool: button 4 = up, 5 = down
            if direction == "up":
                cmd = f"xdotool click --repeat {amount} 4"
            elif direction == "down":
                cmd = f"xdotool click --repeat {amount} 5"
            elif direction == "left":
                cmd = f"xdotool click --repeat {amount} 6"
            elif direction == "right":
                cmd = f"xdotool click --repeat {amount} 7"
            else:
                return f"Invalid direction: {direction}"

            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"

        elif IS_WINDOWS:
            # Windows mouse wheel events
            if direction in ["up", "down"]:
                wheel_delta = 120 * amount if direction == "up" else -120 * amount
                ps_script = f"""
                Add-Type -AssemblyName System.Windows.Forms
                $signature = @'
                [DllImport("user32.dll",CharSet=CharSet.Auto, CallingConvention=CallingConvention.StdCall)]
                public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);
'@
                $SendMouseClick = Add-Type -memberDefinition $signature -name "Win32MouseEventNew5" -namespace Win32Functions -passThru
                $SendMouseClick::mouse_event(0x0800, 0, 0, {wheel_delta}, 0)
                """
                cmd = f'powershell -Command "{ps_script}"'
                stdout, stderr, code = await run_command(cmd)
                if code != 0:
                    return f"Error: {stderr}"
            else:
                return f"Horizontal scrolling not supported on Windows via this method"
        else:
            return f"Unsupported platform: {SYSTEM}"

        return f"Scrolled {direction} by {amount} units"

    except Exception as e:
        return f"Error scrolling: {str(e)}"


# Keyboard Control Tools

@mcp.tool()
async def type_text(text: str, delay_ms: int = 50) -> str:
    """Type the specified text using the keyboard.

    NOTE: For better reliability, consider using type_with_verification() which verifies the text appeared.

    Args:
        text: The text to type
        delay_ms: Delay between keystrokes in milliseconds (default: 50)

    Returns:
        Success or error message with screenshot
    """
    try:
        if IS_MAC:
            # Use AppleScript for more reliable text input in web browsers and apps
            # Escape special characters for AppleScript string literal
            escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')

            # Use keystroke command which works better with web applications
            applescript = f'''
            tell application "System Events"
                keystroke "{escaped_text}"
            end tell
            '''

            cmd = f"osascript -e '{applescript}'"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error typing text: {stderr}"

            # Add delay to allow UI to process the input
            # Web applications especially need time to handle keyboard events
            await asyncio.sleep(0.5)

        elif IS_LINUX:
            # xdotool type
            delay_sec = delay_ms
            escaped_text = text.replace("'", "'\\''")
            cmd = f"xdotool type --delay {delay_sec} '{escaped_text}'"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"

        elif IS_WINDOWS:
            # Windows SendKeys (escape special chars)
            escaped_text = text.replace('"', '""').replace('{', '{{').replace('}', '}}')
            ps_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("{escaped_text}")
            """
            cmd = f'powershell -Command "{ps_script}"'
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"
        else:
            return f"Unsupported platform: {SYSTEM}"

        # Wait for UI to settle (like reference implementation)
        await asyncio.sleep(2.0)

        return f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}"

    except Exception as e:
        return f"Error typing text: {str(e)}"


@mcp.tool()
async def press_key(key: str, modifiers: str = "") -> str:
    """Press a keyboard key or key combination.

    Args:
        key: The key to press (e.g., "Return", "Tab", "a", "F1")
        modifiers: Modifier keys separated by + (e.g., "ctrl", "shift", "alt", "cmd")

    Returns:
        Success or error message with screenshot

    Examples:
        press_key("Return")  # Press Enter
        press_key("c", "ctrl")  # Press Ctrl+C
        press_key("Tab", "shift")  # Press Shift+Tab
        press_key("s", "ctrl+shift")  # Press Ctrl+Shift+S
    """
    try:
        if IS_MAC:
            # Use AppleScript for more reliable key presses
            # Map key names to AppleScript key commands
            key_map = {
                "Return": "key code 36",  # Return key
                "Enter": "key code 36",   # Return key
                "Tab": "key code 48",     # Tab key
                "Space": "key code 49",   # Space key
                "Escape": "key code 53",  # Escape key
                "Backspace": "key code 51",  # Delete key
                "Delete": "key code 117", # Forward delete key
                "Up": "key code 126",     # Up arrow
                "Down": "key code 125",   # Down arrow
                "Left": "key code 123",   # Left arrow
                "Right": "key code 124",  # Right arrow
            }

            # For single character keys, use keystroke; for special keys, use key code
            if key in key_map:
                key_cmd = key_map[key]
            elif len(key) == 1:
                # Single character - use keystroke
                escaped_key = key.replace('\\', '\\\\').replace('"', '\\"')
                key_cmd = f'keystroke "{escaped_key}"'
            else:
                # Try as-is with keystroke
                escaped_key = key.replace('\\', '\\\\').replace('"', '\\"')
                key_cmd = f'keystroke "{escaped_key}"'

            # Build AppleScript with modifiers
            if modifiers:
                mod_map = {
                    "ctrl": "control down",
                    "shift": "shift down",
                    "alt": "option down",
                    "cmd": "command down",
                    "command": "command down"
                }
                mod_parts = [mod_map.get(m.strip().lower(), m.strip().lower()) for m in modifiers.split("+")]
                mod_str = ", ".join(mod_parts)
                applescript = f'''
                tell application "System Events"
                    {key_cmd} using {{{mod_str}}}
                end tell
                '''
            else:
                applescript = f'''
                tell application "System Events"
                    {key_cmd}
                end tell
                '''

            cmd = f"osascript -e '{applescript}'"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error pressing key: {stderr}"

        elif IS_LINUX:
            # xdotool key
            key_map = {
                "Return": "Return",
                "Enter": "Return",
                "Tab": "Tab",
                "Space": "space",
                "Escape": "Escape",
                "Backspace": "BackSpace",
                "Delete": "Delete",
            }
            linux_key = key_map.get(key, key)

            if modifiers:
                mod_map = {"ctrl": "ctrl", "shift": "shift", "alt": "alt", "cmd": "super", "command": "super"}
                mod_parts = [mod_map.get(m.strip().lower(), m.strip().lower()) for m in modifiers.split("+")]
                key_combo = "+".join(mod_parts + [linux_key])
                cmd = f"xdotool key {key_combo}"
            else:
                cmd = f"xdotool key {linux_key}"

            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"

        elif IS_WINDOWS:
            # Windows SendKeys format
            key_map = {
                "Return": "{ENTER}",
                "Enter": "{ENTER}",
                "Tab": "{TAB}",
                "Space": " ",
                "Escape": "{ESC}",
                "Backspace": "{BACKSPACE}",
                "Delete": "{DELETE}",
            }
            win_key = key_map.get(key, key)

            if modifiers:
                # SendKeys uses ^ for Ctrl, + for Shift, % for Alt
                mod_map = {"ctrl": "^", "shift": "+", "alt": "%", "cmd": "^", "command": "^"}
                mod_str = ""
                for m in modifiers.split("+"):
                    mod_str += mod_map.get(m.strip().lower(), "")
                full_key = f"{mod_str}{win_key}"
            else:
                full_key = win_key

            ps_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("{full_key}")
            """
            cmd = f'powershell -Command "{ps_script}"'
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"
        else:
            return f"Unsupported platform: {SYSTEM}"

        # Wait for UI to settle (like reference implementation)
        await asyncio.sleep(2.0)

        mod_text = f"{modifiers}+" if modifiers else ""
        return f"Pressed key: {mod_text}{key}"

    except Exception as e:
        return f"Error pressing key: {str(e)}"


@mcp.tool()
async def get_cursor_position() -> str:
    """Get the current mouse cursor position.

    Returns:
        Cursor position as "x,y" or error message
    """
    try:
        if IS_MAC:
            # Use cliclick to get position
            cmd = "cliclick p"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}. You may need to install cliclick: brew install cliclick"
            # Output format: "x,y"
            return stdout.strip()

        elif IS_LINUX:
            # Use xdotool
            cmd = "xdotool getmouselocation --shell"
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"
            # Parse output (X=123\nY=456\n...)
            lines = stdout.strip().split("\n")
            x = y = None
            for line in lines:
                if line.startswith("X="):
                    x = line.split("=")[1]
                elif line.startswith("Y="):
                    y = line.split("=")[1]
            if x and y:
                return f"{x},{y}"
            return "Error parsing cursor position"

        elif IS_WINDOWS:
            ps_script = """
            Add-Type -AssemblyName System.Windows.Forms
            $pos = [System.Windows.Forms.Cursor]::Position
            Write-Output "$($pos.X),$($pos.Y)"
            """
            cmd = f'powershell -Command "{ps_script}"'
            stdout, stderr, code = await run_command(cmd)
            if code != 0:
                return f"Error: {stderr}"
            return stdout.strip()
        else:
            return f"Unsupported platform: {SYSTEM}"

    except Exception as e:
        return f"Error getting cursor position: {str(e)}"


# High-level tools with verification and retry logic

@mcp.tool()
async def click_with_retry(x: int, y: int, max_retries: int = 3, verify_delay: float = 0.5) -> list[ImageContent | TextContent]:
    """Move mouse to coordinates and click with automatic verification.

    Takes a screenshot before and after the click. Retries if screen doesn't change.
    Returns the final screenshot for Claude to analyze what actually happened.

    Args:
        x: X-coordinate to click
        y: Y-coordinate to click
        max_retries: Maximum number of retry attempts (default: 3)
        verify_delay: Delay in seconds before taking verification screenshot (default: 0.5)

    Returns:
        Screenshot after clicking - Claude should analyze to verify the intended outcome
    """
    try:
        # Take before screenshot hash
        before_hash = await take_screenshot_hash()

        # Scale coordinates to actual screen resolution
        actual_x, actual_y = await scale_coordinates(x, y)

        for attempt in range(max_retries):
            # Click at coordinates (combines move + click in one command for better reliability)
            await left_click(x, y)  # Use original coordinates as left_click handles scaling

            # Wait for UI to update
            await asyncio.sleep(verify_delay)

            # Take after screenshot hash
            after_hash = await take_screenshot_hash()

            # Take final screenshot to return for analysis
            final_screenshot = await screenshot()

            # Check if screenshots are different (action had an effect)
            if before_hash != after_hash:
                return [
                    TextContent(
                        type="text",
                        text=f"Clicked at display coordinates ({x}, {y}) -> actual coordinates ({actual_x}, {actual_y}) on attempt {attempt + 1}. Screen changed successfully."
                    ),
                    *final_screenshot
                ]

            # If we're not on the last attempt, wait before retrying
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)

        # Return final screenshot even if no change detected
        final_screenshot = await screenshot()
        return [
            TextContent(
                type="text",
                text=f"Clicked at display coordinates ({x}, {y}) -> actual coordinates ({actual_x}, {actual_y}) {max_retries} times but screen did not change. Please analyze the screenshot to verify if the click target is correct."
            ),
            *final_screenshot
        ]

    except Exception as e:
        # Return error screenshot if possible
        try:
            error_screenshot = await screenshot()
            return [
                TextContent(type="text", text=f"Error in click_with_retry: {str(e)}"),
                *error_screenshot
            ]
        except:
            return [TextContent(type="text", text=f"Error in click_with_retry: {str(e)}")]


@mcp.tool()
async def type_with_verification(text: str, max_retries: int = 3, verify_delay: float = 1.0) -> list[ImageContent | TextContent]:
    """Type text with automatic verification.

    Takes screenshots before and after typing. Retries if screen doesn't change.
    Returns the final screenshot for Claude to analyze what actually happened.

    Args:
        text: The text to type
        max_retries: Maximum number of retry attempts (default: 3)
        verify_delay: Delay in seconds before taking verification screenshot (default: 1.0)

    Returns:
        Screenshot after typing - Claude should analyze to verify the text appeared correctly
    """
    try:
        # Take before screenshot hash
        before_hash = await take_screenshot_hash()

        for attempt in range(max_retries):
            # Type the text
            await type_text(text)

            # Wait for UI to process input
            await asyncio.sleep(verify_delay)

            # Take after screenshot hash
            after_hash = await take_screenshot_hash()

            # Take final screenshot to return for analysis
            final_screenshot = await screenshot()

            # Check if screenshots are different (text was typed)
            if before_hash != after_hash:
                return [
                    TextContent(
                        type="text",
                        text=f"Typed '{text[:50]}{'...' if len(text) > 50 else ''}' on attempt {attempt + 1}. Screen changed successfully."
                    ),
                    *final_screenshot
                ]

            # If we're not on the last attempt, wait before retrying
            if attempt < max_retries - 1:
                # Clear any partial input before retrying
                await press_key("a", "cmd" if IS_MAC else "ctrl")
                await press_key("Backspace")
                await asyncio.sleep(0.5)

        # Return final screenshot even if no change detected
        final_screenshot = await screenshot()
        return [
            TextContent(
                type="text",
                text=f"Typed '{text[:50]}{'...' if len(text) > 50 else ''}' {max_retries} times but screen did not change. Please analyze the screenshot to verify if typing succeeded."
            ),
            *final_screenshot
        ]

    except Exception as e:
        # Return error screenshot if possible
        try:
            error_screenshot = await screenshot()
            return [
                TextContent(type="text", text=f"Error in type_with_verification: {str(e)}"),
                *error_screenshot
            ]
        except:
            return [TextContent(type="text", text=f"Error in type_with_verification: {str(e)}")]


@mcp.tool()
async def press_key_with_verification(key: str, modifiers: str = "", max_retries: int = 3, verify_delay: float = 0.5) -> list[ImageContent | TextContent]:
    """Press a key with automatic verification.

    Takes screenshots before and after pressing the key. Retries if screen doesn't change.
    Returns the final screenshot for Claude to analyze what actually happened.

    Args:
        key: The key to press
        modifiers: Modifier keys separated by + (e.g., "ctrl", "shift")
        max_retries: Maximum number of retry attempts (default: 3)
        verify_delay: Delay in seconds before taking verification screenshot (default: 0.5)

    Returns:
        Screenshot after key press - Claude should analyze to verify the intended outcome
    """
    try:
        # Take before screenshot hash
        before_hash = await take_screenshot_hash()

        for attempt in range(max_retries):
            # Press the key
            await press_key(key, modifiers)

            # Wait for UI to update
            await asyncio.sleep(verify_delay)

            # Take after screenshot hash
            after_hash = await take_screenshot_hash()

            # Take final screenshot to return for analysis
            final_screenshot = await screenshot()

            # Check if screenshots are different (key press had an effect)
            if before_hash != after_hash:
                mod_text = f"{modifiers}+" if modifiers else ""
                return [
                    TextContent(
                        type="text",
                        text=f"Pressed {mod_text}{key} on attempt {attempt + 1}. Screen changed successfully."
                    ),
                    *final_screenshot
                ]

            # If we're not on the last attempt, wait before retrying
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)

        # Return final screenshot even if no change detected
        final_screenshot = await screenshot()
        mod_text = f"{modifiers}+" if modifiers else ""
        return [
            TextContent(
                type="text",
                text=f"Pressed {mod_text}{key} {max_retries} times but screen did not change. Please analyze the screenshot to verify if the key press had the intended effect."
            ),
            *final_screenshot
        ]

    except Exception as e:
        # Return error screenshot if possible
        try:
            error_screenshot = await screenshot()
            return [
                TextContent(type="text", text=f"Error in press_key_with_verification: {str(e)}"),
                *error_screenshot
            ]
        except:
            return [TextContent(type="text", text=f"Error in press_key_with_verification: {str(e)}")]


@mcp.tool()
async def execute_task_with_vision(task_description: str) -> list[ImageContent | TextContent]:
    """Execute a high-level task using a vision-action-verification loop.

    This is a meta-tool that helps with complex tasks by providing continuous
    visual feedback. It takes a screenshot to show the current state, which
    Claude can use to decide what actions to take next.

    The typical workflow is:
    1. Call this tool to see current state
    2. Claude analyzes the screenshot and decides on actions
    3. Claude calls specific action tools (click, type, etc.)
    4. Call this tool again to verify and see new state
    5. Repeat until task is complete

    Args:
        task_description: Description of what you're trying to accomplish

    Returns:
        Current screenshot with task context
    """
    try:
        # Take screenshot to show current state
        current_screenshot = await screenshot()

        return [
            TextContent(
                type="text",
                text=f"Current state for task: {task_description}\n\nUse the verification tools (click_with_retry, type_with_verification, press_key_with_verification) to ensure your actions succeed. Analyze this screenshot to plan your next action."
            ),
            *current_screenshot
        ]

    except Exception as e:
        return [TextContent(type="text", text=f"Error in execute_task_with_vision: {str(e)}")]


def main():
    """Initialize and run the MCP server."""
    # Run the server with stdio transport (standard for MCP)
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
