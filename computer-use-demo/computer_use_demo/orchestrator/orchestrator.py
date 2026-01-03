"""
Global CEO Orchestrator.

Central coordinator for task execution across multiple computers.
"""

import asyncio
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .types import (
    GlobalTask,
    SubTask,
    TaskPriority,
    TaskResult,
    TaskStatus,
)
from .scheduler import TaskScheduler, SchedulingStrategy
from .decomposer import TaskDecomposer


# Type for task callbacks
TaskCallback = Callable[[GlobalTask], None]


class GlobalCEO:
    """
    Global CEO - Central Orchestrator for multi-computer task execution.

    Responsibilities:
    - Accept and queue tasks
    - Decompose complex tasks into sub-tasks
    - Schedule tasks to computers
    - Monitor execution and handle failures
    - Aggregate results
    """

    def __init__(
        self,
        data_dir: Path | None = None,
        scheduling_strategy: SchedulingStrategy = SchedulingStrategy.LOAD_BALANCED,
    ):
        self._data_dir = data_dir or Path.home() / ".proto" / "orchestrator"
        self._data_dir.mkdir(parents=True, exist_ok=True)

        # Core components
        self._scheduler = TaskScheduler(strategy=scheduling_strategy)
        self._decomposer = TaskDecomposer()

        # Task management
        self._tasks: dict[str, GlobalTask] = {}
        self._task_queue: list[str] = []  # Task IDs in priority order
        self._lock = threading.Lock()

        # Event system
        self._task_events: dict[str, asyncio.Event] = {}

        # Callbacks
        self._on_task_complete: list[TaskCallback] = []
        self._on_task_failed: list[TaskCallback] = []

        # Background processing
        self._running = False
        self._processor_task: asyncio.Task | None = None

        # Registry and message bus will be injected
        self._registry = None
        self._message_bus = None

        # Load persisted tasks
        self._load_tasks()

    def _load_tasks(self) -> None:
        """Load persisted tasks."""
        tasks_file = self._data_dir / "tasks.json"
        if tasks_file.exists():
            try:
                with open(tasks_file, "r") as f:
                    data = json.load(f)

                for task_data in data.get("tasks", []):
                    task = self._task_from_dict(task_data)
                    if task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                        self._tasks[task.id] = task
                        self._task_queue.append(task.id)
            except Exception:
                pass

    def _save_tasks(self) -> None:
        """Save tasks to disk."""
        tasks_file = self._data_dir / "tasks.json"
        data = {
            "tasks": [self._task_to_dict(t) for t in self._tasks.values()],
            "updated_at": datetime.utcnow().isoformat(),
        }
        with open(tasks_file, "w") as f:
            json.dump(data, f, indent=2)

    def _task_to_dict(self, task: GlobalTask) -> dict[str, Any]:
        """Convert task to dictionary."""
        return task.to_dict()

    def _task_from_dict(self, data: dict[str, Any]) -> GlobalTask:
        """Create task from dictionary."""
        task = GlobalTask(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            priority=TaskPriority(data.get("priority", "medium")),
            status=TaskStatus(data.get("status", "pending")),
            required_capabilities=data.get("required_capabilities", []),
            preferred_tags=data.get("preferred_tags", []),
            assigned_to=data.get("assigned_to"),
            created_by=data.get("created_by"),
            timeout=data.get("timeout", 3600),
            max_retries=data.get("max_retries", 3),
            retry_count=data.get("retry_count", 0),
            metadata=data.get("metadata", {}),
        )

        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])

        return task

    def set_registry(self, registry: Any) -> None:
        """Set the computer registry."""
        self._registry = registry

    def set_message_bus(self, bus: Any) -> None:
        """Set the message bus."""
        self._message_bus = bus

    async def start(self) -> None:
        """Start the orchestrator."""
        self._running = True
        self._processor_task = asyncio.create_task(self._process_loop())
        print("[CEO] Orchestrator started")

    async def stop(self) -> None:
        """Stop the orchestrator."""
        self._running = False

        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

        self._save_tasks()
        print("[CEO] Orchestrator stopped")

    async def submit_task(
        self,
        task: GlobalTask,
        decompose: bool = True,
    ) -> GlobalTask:
        """
        Submit a task for execution.

        Args:
            task: Task to execute
            decompose: Whether to decompose into sub-tasks

        Returns:
            Submitted task with ID
        """
        with self._lock:
            # Store task
            self._tasks[task.id] = task
            self._task_events[task.id] = asyncio.Event()

            # Decompose if requested
            if decompose:
                subtasks = self._decomposer.decompose(task)
                if subtasks:
                    task.subtasks = subtasks
                    print(f"[CEO] Task {task.id} decomposed into {len(subtasks)} sub-tasks")

            # Add to queue
            self._task_queue.append(task.id)
            self._reorder_queue()

            self._save_tasks()

        print(f"[CEO] Task submitted: {task.name} ({task.id})")
        return task

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False

            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()

            # Cancel sub-tasks
            for st in task.subtasks:
                if st.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    st.status = TaskStatus.CANCELLED

            # Remove from queue
            if task_id in self._task_queue:
                self._task_queue.remove(task_id)

            # Signal completion
            if task_id in self._task_events:
                self._task_events[task_id].set()

            self._save_tasks()

        print(f"[CEO] Task cancelled: {task_id}")
        return True

    async def wait_for_task(
        self,
        task_id: str,
        timeout: float | None = None,
    ) -> TaskResult | None:
        """
        Wait for a task to complete.

        Args:
            task_id: Task to wait for
            timeout: Maximum wait time in seconds

        Returns:
            Task result or None if timeout/not found
        """
        event = self._task_events.get(task_id)
        if not event:
            task = self._tasks.get(task_id)
            if task and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return task.result
            return None

        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

        task = self._tasks.get(task_id)
        return task.result if task else None

    def get_task(self, task_id: str) -> GlobalTask | None:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(
        self,
        status: TaskStatus | None = None,
        limit: int = 100,
    ) -> list[GlobalTask]:
        """List tasks with optional filter."""
        tasks = list(self._tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        return tasks[:limit]

    def get_queue_position(self, task_id: str) -> int | None:
        """Get task's position in queue."""
        try:
            return self._task_queue.index(task_id)
        except ValueError:
            return None

    async def _process_loop(self) -> None:
        """Main processing loop."""
        while self._running:
            try:
                await self._process_next_task()
                await asyncio.sleep(0.1)  # Small delay to prevent busy-waiting
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[CEO] Processing error: {e}")
                await asyncio.sleep(1)

    async def _process_next_task(self) -> None:
        """Process the next task in queue."""
        if not self._task_queue:
            return

        if not self._registry:
            return

        with self._lock:
            # Get next task
            task_id = self._task_queue[0]
            task = self._tasks.get(task_id)

            if not task:
                self._task_queue.pop(0)
                return

            # Check dependencies
            if not self._are_dependencies_met(task):
                # Move to end of queue
                self._task_queue.pop(0)
                self._task_queue.append(task_id)
                return

        # Process task
        if task.is_decomposed():
            await self._process_decomposed_task(task)
        else:
            await self._process_simple_task(task)

    async def _process_simple_task(self, task: GlobalTask) -> None:
        """Process a simple (non-decomposed) task."""
        # Find available computer
        available = self._registry.list_available()
        computer = self._scheduler.schedule(task, available)

        if not computer:
            return  # No available computer, will retry

        # Assign and execute
        task.assigned_to = computer.id
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()

        await self._registry.update_task_count(computer.id, 1)

        try:
            # Send task to computer via message bus
            if self._message_bus:
                from ..messaging import Message, MessageType
                msg = Message(
                    type=MessageType.TASK_ASSIGN,
                    payload={
                        "task_id": task.id,
                        "name": task.name,
                        "description": task.description,
                        "input_data": task.input_data,
                        "timeout": task.timeout,
                    },
                    source="ceo",
                    target=computer.id,
                )
                await self._message_bus.publish(f"computer.{computer.id}", msg)

            # For now, mark as waiting for response
            # In real implementation, we'd wait for completion message
            print(f"[CEO] Task {task.id} assigned to {computer.name}")

        except Exception as e:
            await self._handle_task_failure(task, str(e))

    async def _process_decomposed_task(self, task: GlobalTask) -> None:
        """Process a decomposed task with sub-tasks."""
        # Get ready sub-tasks
        ready_subtasks = task.get_ready_subtasks()

        if not ready_subtasks and not task.is_complete():
            # Check for blocked tasks
            running = [st for st in task.subtasks if st.status == TaskStatus.RUNNING]
            if not running:
                # No progress possible - check for failures
                if task.has_failed_subtasks():
                    await self._handle_task_failure(
                        task,
                        "Sub-task(s) failed",
                    )
            return

        if task.is_complete():
            await self._complete_task(task)
            return

        # Schedule ready sub-tasks
        for subtask in ready_subtasks:
            available = self._registry.list_available()
            computer = self._scheduler.schedule(subtask, available)

            if not computer:
                continue  # No available computer

            subtask.assigned_to = computer.id
            subtask.status = TaskStatus.RUNNING

            await self._registry.update_task_count(computer.id, 1)

            # Send to computer
            if self._message_bus:
                from ..messaging import Message, MessageType
                msg = Message(
                    type=MessageType.TASK_ASSIGN,
                    payload={
                        "task_id": task.id,
                        "subtask_id": subtask.id,
                        "name": subtask.name,
                        "description": subtask.description,
                        "timeout": subtask.timeout,
                    },
                    source="ceo",
                    target=computer.id,
                )
                await self._message_bus.publish(f"computer.{computer.id}", msg)

            print(f"[CEO] Sub-task {subtask.name} assigned to {computer.name}")

    async def handle_task_complete(
        self,
        task_id: str,
        subtask_id: str | None,
        result: TaskResult,
    ) -> None:
        """
        Handle task completion message from a computer.

        Called when receiving a TASK_COMPLETE message.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return

            if subtask_id:
                # Sub-task completion
                for st in task.subtasks:
                    if st.id == subtask_id:
                        st.status = TaskStatus.COMPLETED
                        st.result = result
                        if st.assigned_to and self._registry:
                            asyncio.create_task(
                                self._registry.update_task_count(st.assigned_to, -1)
                            )
                        break

                # Check if all sub-tasks complete
                if task.is_complete():
                    asyncio.create_task(self._complete_task(task))
            else:
                # Simple task completion
                task.result = result
                await self._complete_task(task)

    async def handle_task_failure(
        self,
        task_id: str,
        subtask_id: str | None,
        error: str,
    ) -> None:
        """Handle task failure message from a computer."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return

            if subtask_id:
                for st in task.subtasks:
                    if st.id == subtask_id:
                        st.status = TaskStatus.FAILED
                        st.result = TaskResult(
                            success=False,
                            error=error,
                        )
                        if st.assigned_to and self._registry:
                            asyncio.create_task(
                                self._registry.update_task_count(st.assigned_to, -1)
                            )
                        break

            # Handle retry
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                print(f"[CEO] Retrying task {task_id} ({task.retry_count}/{task.max_retries})")
            else:
                await self._handle_task_failure(task, error)

    async def _complete_task(self, task: GlobalTask) -> None:
        """Mark task as complete."""
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()

        # Merge sub-task results if decomposed
        if task.is_decomposed():
            merged = self._decomposer.merge_results(task, task.subtasks)
            task.result = TaskResult(
                success=not task.has_failed_subtasks(),
                data=merged,
                duration=(task.completed_at - task.started_at).total_seconds()
                if task.started_at else 0,
            )

        # Update computer metrics
        if task.assigned_to and self._registry:
            duration = (
                (task.completed_at - task.started_at).total_seconds()
                if task.started_at else 0
            )
            await self._registry.record_task_result(
                task.assigned_to,
                success=True,
                duration=duration,
            )
            await self._registry.update_task_count(task.assigned_to, -1)

        # Remove from queue
        with self._lock:
            if task.id in self._task_queue:
                self._task_queue.remove(task.id)

        # Signal completion
        if task.id in self._task_events:
            self._task_events[task.id].set()

        # Callbacks
        for callback in self._on_task_complete:
            try:
                callback(task)
            except Exception:
                pass

        self._save_tasks()
        print(f"[CEO] Task completed: {task.name} ({task.id})")

    async def _handle_task_failure(self, task: GlobalTask, error: str) -> None:
        """Handle task failure."""
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.utcnow()
        task.result = TaskResult(
            success=False,
            error=error,
            duration=(task.completed_at - task.started_at).total_seconds()
            if task.started_at else 0,
        )

        # Update computer metrics
        if task.assigned_to and self._registry:
            duration = (
                (task.completed_at - task.started_at).total_seconds()
                if task.started_at else 0
            )
            await self._registry.record_task_result(
                task.assigned_to,
                success=False,
                duration=duration,
            )
            await self._registry.update_task_count(task.assigned_to, -1)

        # Remove from queue
        with self._lock:
            if task.id in self._task_queue:
                self._task_queue.remove(task.id)

        # Signal completion
        if task.id in self._task_events:
            self._task_events[task.id].set()

        # Callbacks
        for callback in self._on_task_failed:
            try:
                callback(task)
            except Exception:
                pass

        self._save_tasks()
        print(f"[CEO] Task failed: {task.name} - {error}")

    def _are_dependencies_met(self, task: GlobalTask) -> bool:
        """Check if task dependencies are met."""
        for dep in task.dependencies:
            dep_task = self._tasks.get(dep.task_id)
            if not dep_task:
                return False

            if dep.dependency_type == "completion":
                if dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                    return False
            elif dep.dependency_type == "success":
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
                if dep_task.result and not dep_task.result.success:
                    return False

        return True

    def _reorder_queue(self) -> None:
        """Reorder queue based on priority."""
        tasks = [self._tasks.get(tid) for tid in self._task_queue]
        tasks = [t for t in tasks if t is not None]
        prioritized = self._scheduler.prioritize_tasks(tasks)
        self._task_queue = [t.id for t in prioritized]

    def on_task_complete(self, callback: TaskCallback) -> None:
        """Register callback for task completion."""
        self._on_task_complete.append(callback)

    def on_task_failed(self, callback: TaskCallback) -> None:
        """Register callback for task failure."""
        self._on_task_failed.append(callback)

    def get_stats(self) -> dict[str, Any]:
        """Get orchestrator statistics."""
        tasks = list(self._tasks.values())
        return {
            "total_tasks": len(tasks),
            "queue_length": len(self._task_queue),
            "tasks_by_status": {
                status.value: len([t for t in tasks if t.status == status])
                for status in TaskStatus
            },
            "scheduler": self._scheduler.get_stats(),
        }


# Global orchestrator instance
_global_orchestrator: GlobalCEO | None = None


def get_orchestrator() -> GlobalCEO:
    """Get or create the global orchestrator."""
    global _global_orchestrator

    if _global_orchestrator is None:
        _global_orchestrator = GlobalCEO()

    return _global_orchestrator


async def shutdown_orchestrator() -> None:
    """Shutdown the global orchestrator."""
    global _global_orchestrator

    if _global_orchestrator:
        await _global_orchestrator.stop()
        _global_orchestrator = None
