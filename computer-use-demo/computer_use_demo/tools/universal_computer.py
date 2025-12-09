"""
Universal computer tool that auto-detects the environment and uses the appropriate implementation.

Works on:
- Mac (uses LocalComputerTool via pyautogui)
- Ubuntu Desktop (uses LocalComputerTool via pyautogui)
- Containerized Ubuntu (uses ComputerTool20250124 via xdotool)
"""

from typing import Any
from .base import BaseAnthropicTool


class UniversalComputerTool(BaseAnthropicTool):
    """
    Auto-detecting computer tool that works across all platforms.

    Tries to use LocalComputerTool first (faster, works on Mac/desktop).
    Falls back to ComputerTool20250124 if pyautogui is unavailable (containers).
    """

    def __init__(self):
        super().__init__()

        # Try LocalComputerTool first (Mac/Ubuntu desktop)
        try:
            from .local_computer import LocalComputerTool
            self._impl = LocalComputerTool()
            self._using = "LocalComputerTool"
            print(f"✓ UniversalComputerTool: Using LocalComputerTool (pyautogui available)")
        except (RuntimeError, ImportError) as e:
            # Fall back to ComputerTool (containerized/VNC)
            try:
                from .computer import ComputerTool20250124
                self._impl = ComputerTool20250124()
                self._using = "ComputerTool20250124"
                print(f"✓ UniversalComputerTool: Using ComputerTool20250124 (container mode)")
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Could not initialize computer tool. "
                    f"LocalComputerTool failed: {e}, "
                    f"ComputerTool20250124 failed: {fallback_error}"
                ) from fallback_error

    # Delegate all properties and methods to the implementation

    @property
    def name(self):
        return self._impl.name

    @property
    def api_type(self):
        return self._impl.api_type

    @property
    def options(self):
        return self._impl.options

    def to_params(self):
        return self._impl.to_params()

    async def __call__(self, **kwargs) -> Any:
        return await self._impl(**kwargs)
