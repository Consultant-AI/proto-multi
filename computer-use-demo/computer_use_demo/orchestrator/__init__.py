"""
Proto Global CEO Orchestrator Module.

Coordinates tasks across multiple computers in the network.

Usage:
    from computer_use_demo.orchestrator import (
        get_orchestrator,
        GlobalTask,
        TaskPriority,
    )

    # Get the orchestrator
    orchestrator = get_orchestrator()

    # Submit a task
    task = await orchestrator.submit_task(
        GlobalTask(
            name="Build project",
            description="Build and test the project",
            required_capabilities=[ComputerCapability.CODE_EXECUTION],
        )
    )

    # Wait for completion
    result = await orchestrator.wait_for_task(task.id)
"""

from .types import (
    GlobalTask,
    TaskPriority,
    TaskStatus,
    TaskResult,
    SubTask,
    TaskDependency,
)

from .orchestrator import (
    GlobalCEO,
    get_orchestrator,
    shutdown_orchestrator,
)

from .scheduler import (
    TaskScheduler,
    SchedulingStrategy,
)

from .decomposer import (
    TaskDecomposer,
)

__all__ = [
    # Types
    "GlobalTask",
    "TaskPriority",
    "TaskStatus",
    "TaskResult",
    "SubTask",
    "TaskDependency",
    # Orchestrator
    "GlobalCEO",
    "get_orchestrator",
    "shutdown_orchestrator",
    # Scheduler
    "TaskScheduler",
    "SchedulingStrategy",
    # Decomposer
    "TaskDecomposer",
]
