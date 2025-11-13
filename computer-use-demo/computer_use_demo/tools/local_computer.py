import asyncio
import base64
from io import BytesIO
from typing import Literal

try:
    import pyautogui
    from PIL import Image
except Exception as exc:  # pragma: no cover - import errors handled at runtime
    pyautogui = None  # type: ignore[assignment]
    _PY_AUTO_GUI_IMPORT_ERROR = exc
else:  # pragma: no cover - exercised in runtime usage
    _PY_AUTO_GUI_IMPORT_ERROR = None

from .base import BaseAnthropicTool, ToolError, ToolResult
from .computer import (
    Action_20250124,
    MAX_SCALING_TARGETS,
    ScalingSource,
    ScrollDirection,
)

CoordinateSource = Literal["api", "computer"]


def _normalize_key_name(key: str) -> str:
    """
    Normalize Anthropic key names to pyautogui friendly values.
    """
    normalized = key.strip()
    if not normalized:
        raise ToolError("Key cannot be empty")

    key_map = {
        "return": "enter",
        "enter": "enter",
        "space": "space",
        "tab": "tab",
        "escape": "esc",
        "backspace": "backspace",
        "delete": "delete",
        "left": "left",
        "right": "right",
        "up": "up",
        "down": "down",
        "cmd": "command",
        "command": "command",
        "super": "command",
        "win": "win",
        "control": "ctrl",
    }

    lowered = normalized.lower()
    if lowered in key_map:
        return key_map[lowered]

    if lowered.startswith("f") and lowered[1:].isdigit():
        return lowered

    return lowered


class LocalComputerTool(BaseAnthropicTool):
    """
    Computer tool implementation that drives the host machine via pyautogui.

    This avoids the Docker/X11 constraints of the reference implementation
    while matching the Anthropic computer tool contract.
    """

    name = "computer"
    api_type: Literal["computer_20250124"] = "computer_20250124"
    _screenshot_delay = 1.3

    def __init__(self):
        super().__init__()
        if pyautogui is None:
            raise RuntimeError(
                "pyautogui is not available. Install the optional dependency "
                "'pyautogui' (and grant accessibility permissions on macOS)."
            ) from _PY_AUTO_GUI_IMPORT_ERROR

        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0

        self._screen_width, self._screen_height = pyautogui.size()
        self.display_width, self.display_height = self._determine_display_size()
        self._scale_x = (
            self.display_width / self._screen_width if self._screen_width else 1.0
        )
        self._scale_y = (
            self.display_height / self._screen_height if self._screen_height else 1.0
        )

    # --- tool metadata -------------------------------------------------
    @property
    def options(self):
        return {
            "display_width_px": self.display_width,
            "display_height_px": self.display_height,
            "display_number": None,
        }

    def to_params(self):
        return {
            "name": self.name,
            "type": self.api_type,
            **self.options,
        }

    # --- helpers -------------------------------------------------------
    def _determine_display_size(self) -> tuple[int, int]:
        """
        Scale screenshots and coordinates down to a token-friendly resolution.
        """
        if self._screen_width <= 0 or self._screen_height <= 0:
            raise ToolError("Could not determine native screen dimensions")

        max_width = max(res["width"] for res in MAX_SCALING_TARGETS.values())
        max_height = max(res["height"] for res in MAX_SCALING_TARGETS.values())
        if (
            self._screen_width <= max_width
            and self._screen_height <= max_height
        ):
            return self._screen_width, self._screen_height

        # Preserve aspect ratio using the largest supported surface.
        scale_x = max_width / self._screen_width
        scale_y = max_height / self._screen_height
        scale = min(1.0, scale_x, scale_y)
        return (
            max(1, int(self._screen_width * scale)),
            max(1, int(self._screen_height * scale)),
        )

    def _scale_coordinates(self, source: ScalingSource, x: int, y: int) -> tuple[int, int]:
        if source == ScalingSource.API:
            actual_x = int(x / self._scale_x) if self._scale_x else x
            actual_y = int(y / self._scale_y) if self._scale_y else y
            return actual_x, actual_y

        if source == ScalingSource.COMPUTER:
            display_x = int(x * self._scale_x)
            display_y = int(y * self._scale_y)
            return display_x, display_y

        raise ToolError(f"Unknown scaling source: {source}")

    async def _run(self, func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def _capture_screenshot(self) -> str:
        try:
            screenshot = await self._run(pyautogui.screenshot)
        except Exception as exc:  # pragma: no cover - depends on OS
            raise ToolError(f"Failed to capture screenshot: {exc}") from exc

        if self.display_width != self._screen_width or self.display_height != self._screen_height:
            screenshot = screenshot.resize(
                (self.display_width, self.display_height),
                Image.Resampling.LANCZOS,
            )

        buffer = BytesIO()
        screenshot.save(buffer, format="PNG", optimize=True)
        return base64.b64encode(buffer.getvalue()).decode()

    async def _result(
        self,
        *,
        output: str | None = None,
        error: str | None = None,
        include_screenshot: bool = True,
    ) -> ToolResult:
        base64_image = None
        if include_screenshot:
            await asyncio.sleep(self._screenshot_delay)
            base64_image = await self._capture_screenshot()
        return ToolResult(output=output, error=error, base64_image=base64_image)

    def _validate_coordinate(self, coordinate: tuple[int, int] | None) -> tuple[int, int]:
        if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 2:
            raise ToolError(f"{coordinate} must be a tuple of length 2")
        x, y = coordinate
        if not isinstance(x, int) or not isinstance(y, int) or x < 0 or y < 0:
            raise ToolError(f"{coordinate} must contain non-negative integers")
        return self._scale_coordinates(ScalingSource.API, x, y)

    # --- core implementation ------------------------------------------
    async def screenshot(self) -> ToolResult:
        return ToolResult(base64_image=await self._capture_screenshot())

    async def _move_mouse(self, coordinate: tuple[int, int]) -> None:
        x, y = self._validate_coordinate(coordinate)
        await self._run(pyautogui.moveTo, x, y, 0)

    async def _click(
        self,
        *,
        coordinate: tuple[int, int] | None,
        button: Literal["left", "right", "middle"] = "left",
        clicks: int = 1,
        modifier: str | None = None,
    ):
        if coordinate is not None:
            await self._move_mouse(coordinate)
        held_keys: list[str] = []
        if modifier:
            held_keys = [_normalize_key_name(part) for part in modifier.split("+") if part]
            for key_name in held_keys:
                await self._run(pyautogui.keyDown, key_name)
        try:
            await self._run(pyautogui.click, clicks=clicks, interval=0.1, button=button)
        finally:
            for key_name in reversed(held_keys):
                await self._run(pyautogui.keyUp, key_name)

    async def _scroll(
        self,
        amount: int,
        direction: ScrollDirection,
        coordinate: tuple[int, int] | None,
        modifiers: list[str] | None,
    ):
        if coordinate is not None:
            await self._move_mouse(coordinate)

        if modifiers:
            for key_name in modifiers:
                await self._run(pyautogui.keyDown, key_name)
        try:
            if direction in ("up", "down"):
                await self._run(pyautogui.scroll, amount if direction == "up" else -amount)
            else:
                await self._run(
                    pyautogui.hscroll, amount if direction == "right" else -amount
                )
        finally:
            if modifiers:
                for key_name in reversed(modifiers):
                    await self._run(pyautogui.keyUp, key_name)

    # --- Anthropic tool interface -------------------------------------
    async def __call__(
        self,
        *,
        action: Action_20250124,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
        scroll_direction: ScrollDirection | None = None,
        scroll_amount: int | None = None,
        duration: int | float | None = None,
        key: str | None = None,
        **kwargs,
    ):
        if action == "screenshot":
            return await self.screenshot()

        if action == "cursor_position":
            x, y = pyautogui.position()
            display_x, display_y = self._scale_coordinates(
                ScalingSource.COMPUTER, x, y
            )
            return await self._result(
                output=f"X={display_x},Y={display_y}", include_screenshot=False
            )

        if action == "mouse_move":
            if coordinate is None:
                raise ToolError("coordinate is required for mouse_move")
            await self._move_mouse(coordinate)
            return await self._result(output=f"Moved mouse to {coordinate}")

        if action == "left_click_drag":
            if coordinate is None:
                raise ToolError("coordinate is required for left_click_drag")
            target_x, target_y = self._validate_coordinate(coordinate)
            await self._run(pyautogui.mouseDown, button="left")
            await self._run(pyautogui.moveTo, target_x, target_y, 0)
            await self._run(pyautogui.mouseUp, button="left")
            return await self._result(output=f"Dragged to {coordinate}")

        if action in ("left_click", "right_click", "middle_click", "double_click", "triple_click"):
            clicks = {"double_click": 2, "triple_click": 3}.get(action, 1)
            button = "left"
            if action == "right_click":
                button = "right"
            elif action == "middle_click":
                button = "middle"
            await self._click(
                coordinate=coordinate,
                button=button,
                clicks=clicks,
                modifier=key,
            )
            return await self._result(output=f"{action.replace('_', ' ').title()} executed")

        if action in ("left_mouse_down", "left_mouse_up"):
            if coordinate is not None:
                await self._move_mouse(coordinate)
            func = pyautogui.mouseDown if action == "left_mouse_down" else pyautogui.mouseUp
            await self._run(func, button="left")
            return await self._result(output=action.replace("_", " "))

        if action == "scroll":
            if scroll_direction is None:
                raise ToolError("scroll_direction is required for scroll")
            if scroll_amount is None or scroll_amount < 0:
                raise ToolError("scroll_amount must be a non-negative integer")
            modifier = None
            if text:
                modifier = [
                    _normalize_key_name(part) for part in text.split("+") if part
                ]
            await self._scroll(
                scroll_amount or 0, scroll_direction, coordinate, modifier
            )
            return await self._result(output=f"Scrolled {scroll_direction} by {scroll_amount}")

        if action in ("key", "hold_key"):
            if not text:
                raise ToolError("text argument is required for key events")
            keys = [_normalize_key_name(part) for part in text.split("+") if part]
            if not keys:
                raise ToolError("No valid keys provided")

            if action == "key":
                await self._run(pyautogui.hotkey, *keys)
                return await self._result(output=f"Pressed {'+'.join(keys)}")

            if duration is None or duration < 0:
                raise ToolError("duration must be provided for hold_key")
            for key_name in keys:
                await self._run(pyautogui.keyDown, key_name)
            try:
                await asyncio.sleep(duration)
            finally:
                for key_name in reversed(keys):
                    await self._run(pyautogui.keyUp, key_name)
            return await self._result(output=f"Held {'+'.join(keys)} for {duration}s")

        if action == "type":
            if text is None:
                raise ToolError("text is required for type")
            await self._run(pyautogui.write, text, interval=0.012)
            return await self._result(output=f"Typed {text[:40]}")

        if action == "wait":
            if duration is None or duration < 0:
                raise ToolError("duration must be provided for wait")
            await asyncio.sleep(duration)
            return await self._result(output=f"Waited for {duration}s")

        raise ToolError(f"Unsupported action: {action}")
