"""
Hook executor for running hooks.

Executes shell commands with proper timeout, error handling, and logging.
"""

import asyncio
import subprocess
import time
from typing import Any

from .registry import HookRegistry, get_hook_registry
from .template import extract_file_path_from_input, substitute_variables
from .types import HookConfig, HookContext, HookEvent, HookFailBehavior, HookResult


class HookExecutor:
    """
    Executes hooks for tool events.

    Handles:
    - Pre/post tool call hooks
    - Template variable substitution
    - Timeout management
    - Error handling and fail behavior
    """

    def __init__(self, registry: HookRegistry | None = None):
        self._registry = registry or get_hook_registry()
        self._enabled = True

    def enable(self) -> None:
        """Enable hook execution."""
        self._enabled = True

    def disable(self) -> None:
        """Disable hook execution."""
        self._enabled = False

    @property
    def enabled(self) -> bool:
        """Check if hooks are enabled."""
        return self._enabled

    async def run_pre_tool_hooks(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        session_id: str | None = None,
    ) -> tuple[bool, str | None]:
        """
        Run pre-tool-call hooks.

        Args:
            tool_name: Name of the tool being called
            tool_input: Tool input/arguments
            session_id: Current session ID

        Returns:
            Tuple of (should_continue, error_message)
            If should_continue is False, the tool execution should be aborted.
        """
        if not self._enabled:
            return True, None

        context = HookContext(
            event=HookEvent.PRE_TOOL_CALL,
            tool_name=tool_name,
            tool_input=tool_input,
            session_id=session_id,
            file_path=extract_file_path_from_input(tool_input),
        )

        hooks = self._registry.get_hooks_for_event(
            HookEvent.PRE_TOOL_CALL,
            tool_name=tool_name,
            tool_input=tool_input,
        )

        for hook in hooks:
            result = await self._execute_hook(hook, context)

            if result.should_abort:
                return False, result.error or f"Hook '{hook.description or hook.command}' blocked execution"

            if not result.success and hook.fail_behavior == HookFailBehavior.ABORT:
                return False, result.error or f"Hook '{hook.description or hook.command}' failed"

        return True, None

    async def run_post_tool_hooks(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        tool_result: Any,
        session_id: str | None = None,
    ) -> None:
        """
        Run post-tool-call hooks.

        Args:
            tool_name: Name of the tool that was called
            tool_input: Tool input/arguments
            tool_result: Result from the tool execution
            session_id: Current session ID
        """
        if not self._enabled:
            return

        context = HookContext(
            event=HookEvent.POST_TOOL_CALL,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_result=tool_result,
            session_id=session_id,
            file_path=extract_file_path_from_input(tool_input),
        )

        hooks = self._registry.get_hooks_for_event(
            HookEvent.POST_TOOL_CALL,
            tool_name=tool_name,
            tool_input=tool_input,
        )

        for hook in hooks:
            await self._execute_hook(hook, context)

    async def run_error_hooks(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        error: str,
        session_id: str | None = None,
    ) -> None:
        """
        Run error hooks when a tool fails.

        Args:
            tool_name: Name of the tool that failed
            tool_input: Tool input/arguments
            error: Error message
            session_id: Current session ID
        """
        if not self._enabled:
            return

        context = HookContext(
            event=HookEvent.ON_TOOL_ERROR,
            tool_name=tool_name,
            tool_input=tool_input,
            error=error,
            session_id=session_id,
            file_path=extract_file_path_from_input(tool_input),
        )

        hooks = self._registry.get_hooks_for_event(
            HookEvent.ON_TOOL_ERROR,
            tool_name=tool_name,
            tool_input=tool_input,
        )

        for hook in hooks:
            await self._execute_hook(hook, context)

    async def run_session_hooks(
        self,
        event: HookEvent,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Run session lifecycle hooks.

        Args:
            event: Either ON_SESSION_START or ON_SESSION_END
            session_id: Current session ID
            metadata: Additional metadata
        """
        if not self._enabled:
            return

        if event not in (HookEvent.ON_SESSION_START, HookEvent.ON_SESSION_END):
            return

        context = HookContext(
            event=event,
            session_id=session_id,
            metadata=metadata or {},
        )

        hooks = self._registry.get_hooks_for_event(event)

        for hook in hooks:
            await self._execute_hook(hook, context)

    async def _execute_hook(self, hook: HookConfig, context: HookContext) -> HookResult:
        """
        Execute a single hook.

        Args:
            hook: Hook configuration
            context: Execution context

        Returns:
            HookResult with execution details
        """
        start_time = time.time()

        try:
            # Substitute template variables
            command = substitute_variables(hook.command, context)

            # Execute the command
            if hook.blocking:
                result = await self._run_blocking(command, hook.timeout)
            else:
                result = await self._run_non_blocking(command)

            duration = time.time() - start_time
            result.duration = duration

            # Log result if needed
            if not result.success:
                self._log_hook_result(hook, result)

            return result

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            result = HookResult(
                success=False,
                error=f"Hook timed out after {hook.timeout} seconds",
                return_code=-1,
                duration=duration,
                should_abort=hook.fail_behavior == HookFailBehavior.ABORT,
            )
            self._log_hook_result(hook, result)
            return result

        except Exception as e:
            duration = time.time() - start_time
            result = HookResult(
                success=False,
                error=str(e),
                return_code=-1,
                duration=duration,
                should_abort=hook.fail_behavior == HookFailBehavior.ABORT,
            )
            self._log_hook_result(hook, result)
            return result

    async def _run_blocking(self, command: str, timeout: int) -> HookResult:
        """Run a command and wait for it to complete."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True,
            )

            if timeout > 0:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            else:
                stdout, stderr = await process.communicate()

            output = stdout.decode() if stdout else ""
            error_output = stderr.decode() if stderr else ""

            return HookResult(
                success=process.returncode == 0,
                output=output,
                error=error_output if error_output else None,
                return_code=process.returncode or 0,
                should_abort=False,
            )

        except asyncio.TimeoutError:
            raise

    async def _run_non_blocking(self, command: str) -> HookResult:
        """Start a command without waiting for it to complete."""
        try:
            # Start process in background
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                shell=True,
            )

            # Don't wait for completion
            return HookResult(
                success=True,
                output=f"Started background process (PID: {process.pid})",
                return_code=0,
                should_abort=False,
            )

        except Exception as e:
            return HookResult(
                success=False,
                error=str(e),
                return_code=-1,
                should_abort=False,
            )

    def _log_hook_result(self, hook: HookConfig, result: HookResult) -> None:
        """Log hook execution result."""
        if hook.fail_behavior == HookFailBehavior.IGNORE:
            return

        status = "succeeded" if result.success else "failed"
        desc = hook.description or hook.command[:50]

        if result.success:
            # Only log failures unless verbose
            return

        print(f"[Hook] {desc} {status}: {result.error or result.output}")


# Global executor instance
_global_executor: HookExecutor | None = None


def get_hook_executor() -> HookExecutor:
    """Get the global hook executor instance."""
    global _global_executor
    if _global_executor is None:
        _global_executor = HookExecutor()
    return _global_executor
