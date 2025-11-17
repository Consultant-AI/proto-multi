"""
Structural Checker - Programmatic verification of system state.

Provides non-visual verification through:
- File system checks
- Process validation
- Command output verification
- Application state queries
"""

import asyncio
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class StructuralCheck:
    """Result of a structural verification check"""
    check_type: str
    success: bool
    details: dict[str, Any]
    error: str | None = None


class StructuralChecker:
    """
    Performs programmatic verification of system state.

    Complements visual verification with structural checks:
    - File existence and content
    - Process status
    - Network connectivity
    - Service availability
    """

    def __init__(self):
        """Initialize structural checker"""
        self.check_history: list[StructuralCheck] = []

    async def check_file_exists(
        self,
        file_path: str | Path,
        expected_content: str | None = None,
    ) -> StructuralCheck:
        """
        Check if a file exists and optionally validate content.

        Args:
            file_path: Path to file
            expected_content: Optional content to verify

        Returns:
            StructuralCheck result
        """
        path = Path(file_path)

        if not path.exists():
            check = StructuralCheck(
                check_type="file_exists",
                success=False,
                details={"path": str(path), "exists": False},
                error=f"File does not exist: {path}",
            )
        elif expected_content:
            try:
                actual_content = path.read_text()
                matches = expected_content in actual_content

                check = StructuralCheck(
                    check_type="file_content",
                    success=matches,
                    details={
                        "path": str(path),
                        "exists": True,
                        "content_matches": matches,
                    },
                    error=None if matches else "Content does not match expected",
                )
            except Exception as e:
                check = StructuralCheck(
                    check_type="file_content",
                    success=False,
                    details={"path": str(path), "exists": True},
                    error=f"Error reading file: {e}",
                )
        else:
            check = StructuralCheck(
                check_type="file_exists",
                success=True,
                details={"path": str(path), "exists": True},
            )

        self.check_history.append(check)
        return check

    async def check_process_running(
        self,
        process_name: str,
    ) -> StructuralCheck:
        """
        Check if a process is running.

        Args:
            process_name: Name of process to check

        Returns:
            StructuralCheck result
        """
        try:
            # Use ps to check for process
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            is_running = process_name in result.stdout

            check = StructuralCheck(
                check_type="process_running",
                success=is_running,
                details={
                    "process_name": process_name,
                    "running": is_running,
                },
                error=None if is_running else f"Process not found: {process_name}",
            )

        except Exception as e:
            check = StructuralCheck(
                check_type="process_running",
                success=False,
                details={"process_name": process_name},
                error=f"Error checking process: {e}",
            )

        self.check_history.append(check)
        return check

    async def check_command_output(
        self,
        command: str,
        expected_output: str | None = None,
        expected_exit_code: int = 0,
    ) -> StructuralCheck:
        """
        Run a command and verify its output/exit code.

        Args:
            command: Command to run
            expected_output: Expected substring in output
            expected_exit_code: Expected exit code

        Returns:
            StructuralCheck result
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )

            exit_code_matches = result.returncode == expected_exit_code
            output_matches = (
                expected_output in result.stdout
                if expected_output
                else True
            )

            success = exit_code_matches and output_matches

            check = StructuralCheck(
                check_type="command_output",
                success=success,
                details={
                    "command": command,
                    "exit_code": result.returncode,
                    "expected_exit_code": expected_exit_code,
                    "exit_code_matches": exit_code_matches,
                    "output_matches": output_matches,
                    "stdout": result.stdout[:500],  # First 500 chars
                    "stderr": result.stderr[:500],
                },
                error=None if success else "Command output/exit code mismatch",
            )

        except subprocess.TimeoutExpired:
            check = StructuralCheck(
                check_type="command_output",
                success=False,
                details={"command": command},
                error="Command timed out",
            )
        except Exception as e:
            check = StructuralCheck(
                check_type="command_output",
                success=False,
                details={"command": command},
                error=f"Error running command: {e}",
            )

        self.check_history.append(check)
        return check

    async def check_port_listening(
        self,
        port: int,
        host: str = "localhost",
    ) -> StructuralCheck:
        """
        Check if a port is listening.

        Args:
            port: Port number to check
            host: Host to check (default: localhost)

        Returns:
            StructuralCheck result
        """
        try:
            # Try to connect to port
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=5.0,
            )
            writer.close()
            await writer.wait_closed()

            check = StructuralCheck(
                check_type="port_listening",
                success=True,
                details={
                    "host": host,
                    "port": port,
                    "listening": True,
                },
            )

        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            check = StructuralCheck(
                check_type="port_listening",
                success=False,
                details={
                    "host": host,
                    "port": port,
                    "listening": False,
                },
                error=f"Port {port} is not listening on {host}",
            )
        except Exception as e:
            check = StructuralCheck(
                check_type="port_listening",
                success=False,
                details={"host": host, "port": port},
                error=f"Error checking port: {e}",
            )

        self.check_history.append(check)
        return check

    async def check_directory_contains(
        self,
        directory: str | Path,
        expected_files: list[str],
    ) -> StructuralCheck:
        """
        Check if directory contains expected files.

        Args:
            directory: Directory path to check
            expected_files: List of expected filenames

        Returns:
            StructuralCheck result
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            return StructuralCheck(
                check_type="directory_contents",
                success=False,
                details={"directory": str(dir_path)},
                error="Directory does not exist",
            )

        if not dir_path.is_dir():
            return StructuralCheck(
                check_type="directory_contents",
                success=False,
                details={"directory": str(dir_path)},
                error="Path is not a directory",
            )

        actual_files = [f.name for f in dir_path.iterdir()]
        missing_files = [f for f in expected_files if f not in actual_files]
        found_files = [f for f in expected_files if f in actual_files]

        success = len(missing_files) == 0

        check = StructuralCheck(
            check_type="directory_contents",
            success=success,
            details={
                "directory": str(dir_path),
                "expected_files": expected_files,
                "found_files": found_files,
                "missing_files": missing_files,
                "total_files": len(actual_files),
            },
            error=f"Missing files: {missing_files}" if missing_files else None,
        )

        self.check_history.append(check)
        return check

    def get_check_stats(self) -> dict[str, Any]:
        """
        Get statistics about checks performed.

        Returns:
            Dictionary with check statistics
        """
        total = len(self.check_history)
        successful = sum(1 for c in self.check_history if c.success)

        by_type = {}
        for check in self.check_history:
            check_type = check.check_type
            if check_type not in by_type:
                by_type[check_type] = {"total": 0, "successful": 0}
            by_type[check_type]["total"] += 1
            if check.success:
                by_type[check_type]["successful"] += 1

        return {
            "total_checks": total,
            "successful": successful,
            "failed": total - successful,
            "by_type": by_type,
        }
