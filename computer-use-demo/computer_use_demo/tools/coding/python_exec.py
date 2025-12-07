"""
Python Code Execution Tool - Provides persistent Python environment for agents.

This tool allows agents to execute Python code with:
- Persistent variables across executions
- Pre-loaded data science libraries
- Rich output support (dataframes, plots)
- Clean error handling
"""

import asyncio
import os
import sys
import traceback
from typing import Any, Literal

from ..base import BaseAnthropicTool, CLIResult, ToolError, ToolResult


class _PythonSession:
    """A persistent Python interpreter session."""

    _started: bool
    _globals: dict[str, Any]
    _locals: dict[str, Any]
    _output_capture: list[str]

    def __init__(self):
        self._started = False
        self._globals = {}
        self._locals = {}
        self._output_capture = []
        self._setup_environment()

    def _setup_environment(self):
        """Set up the Python environment with common imports."""
        # Pre-load common data science libraries
        preload_code = """
import sys
import os
import json
import math
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

# Data science libraries (import only if available)
try:
    import pandas as pd
    import numpy as np
except ImportError:
    pass

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
except ImportError:
    pass

try:
    from scipy import stats
except ImportError:
    pass

# Helper function for printing dataframes
def display(obj):
    '''Display an object with nice formatting'''
    if 'pandas' in sys.modules:
        import pandas as pd
        if isinstance(obj, pd.DataFrame):
            print(obj.to_string())
            return
        if isinstance(obj, pd.Series):
            print(obj.to_string())
            return
    print(obj)
"""
        try:
            exec(preload_code, self._globals, self._locals)
            self._started = True
        except Exception as e:
            # If preload fails, still allow basic Python
            self._globals = {"__builtins__": __builtins__}
            self._locals = {}
            self._started = True

    def reset(self):
        """Reset the Python environment (clear all variables)."""
        self._globals.clear()
        self._locals.clear()
        self._output_capture.clear()
        self._setup_environment()

    async def execute(self, code: str) -> CLIResult:
        """Execute Python code and return the result."""
        if not self._started:
            raise ToolError("Session has not started.")

        # Capture stdout/stderr
        import io
        from contextlib import redirect_stdout, redirect_stderr

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        output = ""
        error = ""

        try:
            # Compile the code first to check for syntax errors
            compiled_code = compile(code, "<agent_code>", "exec")

            # Execute with output capture
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(compiled_code, self._globals, self._locals)

            # Get captured output
            output = stdout_capture.getvalue()
            error = stderr_capture.getvalue()

            # Strip trailing newlines from output
            if output:
                output = output.rstrip('\n')

            # If no output, try to get the last expression value
            if not output and not error:
                # Try to evaluate the last line as an expression
                lines = code.strip().split('\n')
                if lines:
                    last_line = lines[-1].strip()
                    if last_line and not last_line.startswith(('#', 'import', 'from', 'def', 'class', 'if', 'for', 'while', 'try', 'with')):
                        try:
                            result = eval(last_line, self._globals, self._locals)
                            if result is not None:
                                output = repr(result)
                        except:
                            pass  # Last line wasn't an expression, that's okay

        except SyntaxError as e:
            error = f"SyntaxError: {e.msg} (line {e.lineno})"
            if e.text:
                error += f"\n  {e.text.strip()}\n  {' ' * (e.offset - 1) if e.offset else ''}^"
        except Exception as e:
            error = f"{type(e).__name__}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

        return CLIResult(output=output if output else None, error=error if error else None)


class PythonExecutionTool(BaseAnthropicTool):
    """
    Execute Python code in a persistent environment.

    Features:
    - Persistent variables across executions
    - Pre-loaded data science libraries (pandas, numpy, matplotlib, scipy)
    - Rich output support
    - Clean error handling with traceback
    - Optional environment reset

    Pre-loaded libraries:
    - Standard: sys, os, json, math, statistics, datetime
    - Data Science: pandas (as pd), numpy (as np), matplotlib.pyplot (as plt), scipy.stats
    - Helper: display() function for pretty-printing dataframes

    Example usage:
    ```python
    # First execution - load data
    execute_python(code=\"\"\"
    import pandas as pd
    df = pd.DataFrame({'revenue': [100, 150, 200]})
    print(f"Loaded {len(df)} rows")
    \"\"\")

    # Second execution - analyze (using df from first execution)
    execute_python(code=\"\"\"
    avg_revenue = df['revenue'].mean()
    print(f"Average: ${avg_revenue:.2f}")
    \"\"\")

    # Reset environment if needed
    execute_python(code="print('Starting fresh')", reset=True)
    ```
    """

    _session: _PythonSession | None

    api_type: Literal["python_exec_v1"] = "python_exec_v1"
    name: Literal["execute_python"] = "execute_python"

    def __init__(self):
        self._session = None
        super().__init__()

    def to_params(self) -> Any:
        return {
            "type": "custom",
            "name": self.name,
            "description": (
                "Execute Python code in a persistent environment with data science libraries pre-loaded. "
                "Variables persist across executions. Use reset=true to clear the environment. "
                "Pre-loaded: pandas (pd), numpy (np), matplotlib.pyplot (plt), scipy.stats, datetime, json, math."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Can be multiple lines. Variables persist across calls."
                    },
                    "reset": {
                        "type": "boolean",
                        "description": "If true, reset the Python environment (clear all variables) before executing. Default: false."
                    }
                },
                "required": ["code"]
            }
        }

    async def __call__(
        self, code: str | None = None, reset: bool = False, **kwargs
    ):
        """Execute Python code with optional environment reset."""
        if reset or self._session is None:
            self._session = _PythonSession()
            if reset and code is None:
                return ToolResult(system="Python environment has been reset.")

        if code is not None:
            return await self._session.execute(code)

        raise ToolError("No code provided.")
