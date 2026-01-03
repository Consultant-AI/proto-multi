"""
Task Scheduler for the Global CEO Orchestrator.

Handles task assignment and scheduling across computers.
"""

from enum import Enum
from typing import Any

from .types import GlobalTask, SubTask, TaskPriority


class SchedulingStrategy(str, Enum):
    """Strategies for scheduling tasks."""

    # Assign to least loaded computer
    LOAD_BALANCED = "load_balanced"

    # Assign to first available computer
    FIRST_AVAILABLE = "first_available"

    # Round-robin across computers
    ROUND_ROBIN = "round_robin"

    # Prioritize computers with best success rate
    BEST_PERFORMER = "best_performer"

    # Prioritize computers with lowest latency
    LOWEST_LATENCY = "lowest_latency"

    # Affinity-based (prefer same computer as related tasks)
    AFFINITY = "affinity"


class TaskScheduler:
    """
    Schedules tasks to computers based on various strategies.
    """

    def __init__(
        self,
        strategy: SchedulingStrategy = SchedulingStrategy.LOAD_BALANCED,
    ):
        self._strategy = strategy
        self._round_robin_index = 0
        self._affinity_map: dict[str, str] = {}  # task_id -> computer_id

    @property
    def strategy(self) -> SchedulingStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, value: SchedulingStrategy) -> None:
        self._strategy = value

    def schedule(
        self,
        task: GlobalTask | SubTask,
        available_computers: list[Any],  # list[Computer]
    ) -> Any | None:
        """
        Schedule a task to a computer.

        Args:
            task: Task to schedule
            available_computers: List of available computers

        Returns:
            Selected computer or None
        """
        if not available_computers:
            return None

        # Filter by required capabilities
        if hasattr(task, "required_capabilities") and task.required_capabilities:
            available_computers = [
                c for c in available_computers
                if all(
                    cap in [cap.value for cap in c.capabilities]
                    for cap in task.required_capabilities
                )
            ]

        if not available_computers:
            return None

        # Apply scheduling strategy
        if self._strategy == SchedulingStrategy.LOAD_BALANCED:
            return self._schedule_load_balanced(task, available_computers)
        elif self._strategy == SchedulingStrategy.FIRST_AVAILABLE:
            return self._schedule_first_available(available_computers)
        elif self._strategy == SchedulingStrategy.ROUND_ROBIN:
            return self._schedule_round_robin(available_computers)
        elif self._strategy == SchedulingStrategy.BEST_PERFORMER:
            return self._schedule_best_performer(available_computers)
        elif self._strategy == SchedulingStrategy.LOWEST_LATENCY:
            return self._schedule_lowest_latency(available_computers)
        elif self._strategy == SchedulingStrategy.AFFINITY:
            return self._schedule_affinity(task, available_computers)
        else:
            return self._schedule_load_balanced(task, available_computers)

    def _schedule_load_balanced(
        self,
        task: GlobalTask | SubTask,
        computers: list[Any],
    ) -> Any:
        """Select computer with lowest load."""
        return min(computers, key=lambda c: c.current_tasks / max(c.max_concurrent_tasks, 1))

    def _schedule_first_available(self, computers: list[Any]) -> Any:
        """Select first available computer."""
        return computers[0]

    def _schedule_round_robin(self, computers: list[Any]) -> Any:
        """Select computers in round-robin fashion."""
        computer = computers[self._round_robin_index % len(computers)]
        self._round_robin_index += 1
        return computer

    def _schedule_best_performer(self, computers: list[Any]) -> Any:
        """Select computer with best success rate."""
        return max(computers, key=lambda c: c.metrics.success_rate)

    def _schedule_lowest_latency(self, computers: list[Any]) -> Any:
        """Select computer with lowest latency."""
        return min(computers, key=lambda c: c.health.latency_ms)

    def _schedule_affinity(
        self,
        task: GlobalTask | SubTask,
        computers: list[Any],
    ) -> Any:
        """Select computer with affinity to related tasks."""
        # Check if parent task has affinity
        if isinstance(task, SubTask) and task.parent_id:
            preferred = self._affinity_map.get(task.parent_id)
            if preferred:
                for c in computers:
                    if c.id == preferred:
                        return c

        # Fall back to load balanced
        return self._schedule_load_balanced(task, computers)

    def record_affinity(self, task_id: str, computer_id: str) -> None:
        """Record task-computer affinity."""
        self._affinity_map[task_id] = computer_id

    def clear_affinity(self, task_id: str) -> None:
        """Clear affinity for a task."""
        self._affinity_map.pop(task_id, None)

    def prioritize_tasks(self, tasks: list[GlobalTask]) -> list[GlobalTask]:
        """
        Sort tasks by priority for scheduling.

        Order:
        1. Critical priority
        2. High priority
        3. Tasks with more dependencies satisfied
        4. Older tasks
        """
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }

        def sort_key(task: GlobalTask) -> tuple:
            return (
                priority_order.get(task.priority, 2),
                -len([d for d in task.dependencies]),  # More deps = later
                task.created_at,
            )

        return sorted(tasks, key=sort_key)

    def estimate_wait_time(
        self,
        task: GlobalTask,
        queue: list[GlobalTask],
        computers: list[Any],
    ) -> float:
        """
        Estimate wait time for a task.

        Returns:
            Estimated wait time in seconds
        """
        if not computers:
            return float("inf")

        # Count tasks ahead in queue
        tasks_ahead = 0
        for t in queue:
            if t.id == task.id:
                break
            tasks_ahead += 1

        # Calculate average task duration
        total_duration = sum(c.metrics.avg_task_duration for c in computers)
        avg_duration = total_duration / len(computers) if computers else 60.0

        # Calculate total capacity
        total_capacity = sum(c.max_concurrent_tasks for c in computers)
        current_load = sum(c.current_tasks for c in computers)
        available = max(total_capacity - current_load, 1)

        # Estimate wait
        return (tasks_ahead / available) * avg_duration

    def get_stats(self) -> dict[str, Any]:
        """Get scheduler statistics."""
        return {
            "strategy": self._strategy.value,
            "round_robin_index": self._round_robin_index,
            "affinity_count": len(self._affinity_map),
        }
