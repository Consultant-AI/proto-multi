"""
Task Decomposer for the Global CEO Orchestrator.

Breaks down complex tasks into sub-tasks for parallel execution.
"""

import uuid
from typing import Any

from .types import GlobalTask, SubTask, TaskStatus


class TaskDecomposer:
    """
    Decomposes complex tasks into sub-tasks.

    Strategies:
    - Sequential: Sub-tasks run one after another
    - Parallel: All sub-tasks run simultaneously
    - DAG: Sub-tasks form a directed acyclic graph
    """

    def __init__(self):
        self._decomposition_rules: dict[str, callable] = {}

    def register_rule(
        self,
        task_type: str,
        decomposer: callable,
    ) -> None:
        """
        Register a decomposition rule.

        Args:
            task_type: Type of task this rule applies to
            decomposer: Function that takes a task and returns sub-tasks
        """
        self._decomposition_rules[task_type] = decomposer

    def decompose(
        self,
        task: GlobalTask,
        strategy: str = "auto",
    ) -> list[SubTask]:
        """
        Decompose a task into sub-tasks.

        Args:
            task: Task to decompose
            strategy: "sequential", "parallel", "dag", or "auto"

        Returns:
            List of sub-tasks
        """
        # Check for registered rule
        task_type = task.metadata.get("type", "default")
        if task_type in self._decomposition_rules:
            return self._decomposition_rules[task_type](task)

        # Auto-detect based on task properties
        if strategy == "auto":
            strategy = self._detect_strategy(task)

        if strategy == "sequential":
            return self._decompose_sequential(task)
        elif strategy == "parallel":
            return self._decompose_parallel(task)
        elif strategy == "dag":
            return self._decompose_dag(task)
        else:
            # No decomposition - task runs as single unit
            return []

    def _detect_strategy(self, task: GlobalTask) -> str:
        """Auto-detect decomposition strategy."""
        # Check metadata hints
        if "decomposition" in task.metadata:
            return task.metadata["decomposition"]

        # Check for explicit steps in description
        description = task.description.lower()
        if "then" in description or "after" in description:
            return "sequential"
        elif "and" in description or "parallel" in description:
            return "parallel"

        # Default: no decomposition
        return "none"

    def _decompose_sequential(self, task: GlobalTask) -> list[SubTask]:
        """Decompose into sequential sub-tasks."""
        subtasks = []

        # Parse steps from description or metadata
        steps = task.metadata.get("steps", [])
        if not steps:
            # Try to parse from description
            steps = self._parse_steps(task.description)

        prev_id = None
        for i, step in enumerate(steps):
            subtask = SubTask(
                id=str(uuid.uuid4()),
                parent_id=task.id,
                name=step.get("name", f"Step {i + 1}"),
                description=step.get("description", ""),
                required_capabilities=step.get(
                    "capabilities",
                    task.required_capabilities,
                ),
                dependencies=[prev_id] if prev_id else [],
                order=i,
                timeout=step.get("timeout", task.timeout / max(len(steps), 1)),
            )
            subtasks.append(subtask)
            prev_id = subtask.id

        return subtasks

    def _decompose_parallel(self, task: GlobalTask) -> list[SubTask]:
        """Decompose into parallel sub-tasks."""
        subtasks = []

        # Parse parallel units from metadata
        units = task.metadata.get("parallel_units", [])
        if not units:
            units = task.metadata.get("steps", [])

        for i, unit in enumerate(units):
            subtask = SubTask(
                id=str(uuid.uuid4()),
                parent_id=task.id,
                name=unit.get("name", f"Unit {i + 1}"),
                description=unit.get("description", ""),
                required_capabilities=unit.get(
                    "capabilities",
                    task.required_capabilities,
                ),
                dependencies=[],  # No dependencies - all run in parallel
                order=i,
                timeout=unit.get("timeout", task.timeout),
            )
            subtasks.append(subtask)

        return subtasks

    def _decompose_dag(self, task: GlobalTask) -> list[SubTask]:
        """Decompose into a DAG of sub-tasks."""
        subtasks = []

        # Parse DAG from metadata
        dag = task.metadata.get("dag", {})
        nodes = dag.get("nodes", [])
        edges = dag.get("edges", [])

        # Create subtasks for nodes
        id_map = {}  # node_id -> subtask_id
        for node in nodes:
            subtask_id = str(uuid.uuid4())
            id_map[node["id"]] = subtask_id

            subtask = SubTask(
                id=subtask_id,
                parent_id=task.id,
                name=node.get("name", node["id"]),
                description=node.get("description", ""),
                required_capabilities=node.get(
                    "capabilities",
                    task.required_capabilities,
                ),
                dependencies=[],  # Will be filled in below
                timeout=node.get("timeout", task.timeout),
            )
            subtasks.append(subtask)

        # Add dependencies from edges
        for edge in edges:
            from_id = id_map.get(edge["from"])
            to_id = id_map.get(edge["to"])
            if from_id and to_id:
                for st in subtasks:
                    if st.id == to_id:
                        st.dependencies.append(from_id)

        return subtasks

    def _parse_steps(self, description: str) -> list[dict[str, Any]]:
        """Parse steps from a description string."""
        steps = []

        # Simple parsing: look for numbered items or bullet points
        lines = description.split("\n")
        current_step = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for numbered step
            if line[0].isdigit() and (". " in line[:5] or ") " in line[:5]):
                if current_step:
                    steps.append(current_step)
                # Extract step text
                for sep in [". ", ") "]:
                    if sep in line[:5]:
                        step_text = line.split(sep, 1)[1]
                        current_step = {"name": step_text[:50], "description": step_text}
                        break
            elif line.startswith("- ") or line.startswith("* "):
                if current_step:
                    steps.append(current_step)
                step_text = line[2:]
                current_step = {"name": step_text[:50], "description": step_text}
            elif current_step:
                current_step["description"] += " " + line

        if current_step:
            steps.append(current_step)

        return steps

    def merge_results(
        self,
        task: GlobalTask,
        subtasks: list[SubTask],
    ) -> Any:
        """
        Merge results from sub-tasks.

        Args:
            task: Parent task
            subtasks: Completed sub-tasks

        Returns:
            Merged result
        """
        # Check for custom merger
        merger = task.metadata.get("result_merger")
        if merger == "concat":
            return self._merge_concat(subtasks)
        elif merger == "dict":
            return self._merge_dict(subtasks)
        elif merger == "last":
            return self._merge_last(subtasks)
        else:
            return self._merge_default(subtasks)

    def _merge_default(self, subtasks: list[SubTask]) -> dict[str, Any]:
        """Default merge: collect all results."""
        return {
            "subtasks": [
                {
                    "id": st.id,
                    "name": st.name,
                    "success": st.result.success if st.result else False,
                    "data": st.result.data if st.result else None,
                    "error": st.result.error if st.result else None,
                }
                for st in subtasks
            ],
            "all_succeeded": all(
                st.result and st.result.success
                for st in subtasks
            ),
        }

    def _merge_concat(self, subtasks: list[SubTask]) -> list[Any]:
        """Concatenate results."""
        results = []
        for st in sorted(subtasks, key=lambda x: x.order):
            if st.result and st.result.data:
                if isinstance(st.result.data, list):
                    results.extend(st.result.data)
                else:
                    results.append(st.result.data)
        return results

    def _merge_dict(self, subtasks: list[SubTask]) -> dict[str, Any]:
        """Merge results as dictionary."""
        merged = {}
        for st in subtasks:
            if st.result and st.result.data:
                if isinstance(st.result.data, dict):
                    merged.update(st.result.data)
                else:
                    merged[st.name] = st.result.data
        return merged

    def _merge_last(self, subtasks: list[SubTask]) -> Any:
        """Return only the last result."""
        sorted_subtasks = sorted(subtasks, key=lambda x: x.order)
        if sorted_subtasks:
            last = sorted_subtasks[-1]
            return last.result.data if last.result else None
        return None
