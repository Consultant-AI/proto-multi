"""
Company Orchestrator for Continuous Multi-Agent Operation.

Coordinates autonomous operation of all agents with work distribution,
monitoring, and recovery capabilities.
"""

import asyncio
import signal
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..agents import create_agent_by_name
from ..proto_logging import get_logger
from ..planning import ProjectManager
from .work_queue import WorkItem, WorkPriority, WorkQueue, WorkStatus


class CompanyOrchestrator:
    """
    Orchestrator for continuous multi-agent operation.

    Manages the event loop that continuously:
    - Monitors work queue for pending tasks
    - Assigns work to appropriate agents
    - Handles failures and retries
    - Maintains system health
    - Persists state for recovery
    """

    def __init__(
        self,
        work_queue: Optional[WorkQueue] = None,
        project_manager: Optional[ProjectManager] = None,
        state_path: Optional[Path] = None,
        check_interval: int = 10,
        max_concurrent_work: int = 5,
    ):
        """
        Initialize orchestrator.

        Args:
            work_queue: Work queue to use (creates default if None)
            project_manager: Project manager (creates default if None)
            state_path: Path for state persistence
            check_interval: Seconds between queue checks
            max_concurrent_work: Maximum concurrent work items
        """
        self.logger = get_logger()

        self.work_queue = work_queue or WorkQueue()
        self.project_manager = project_manager or ProjectManager()

        if state_path is None:
            base_path = Path.home() / ".proto" / "daemon"
            base_path.mkdir(parents=True, exist_ok=True)
            state_path = base_path / "orchestrator_state.json"

        self.state_path = Path(state_path)
        self.check_interval = check_interval
        self.max_concurrent_work = max_concurrent_work

        # Runtime state
        self.running = False
        self.active_work: dict[str, WorkItem] = {}  # work_id -> WorkItem
        self.agent_status: dict[str, dict[str, Any]] = {}  # agent_name -> status
        self.stats = {
            "started_at": None,
            "total_work_completed": 0,
            "total_work_failed": 0,
            "last_health_check": None,
        }

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.log_event(
            event_type="orchestrator_shutdown_signal",
            session_id="orchestrator",
            data={"signal": signum},
        )
        self.stop()

    async def start(self):
        """Start the orchestrator event loop."""
        if self.running:
            self.logger.log_event(
                event_type="orchestrator_already_running",
                session_id="orchestrator",
            )
            return

        self.running = True
        self.stats["started_at"] = datetime.now().isoformat()

        self.logger.log_event(
            event_type="orchestrator_started",
            session_id="orchestrator",
            data={
                "check_interval": self.check_interval,
                "max_concurrent": self.max_concurrent_work,
            },
        )

        # Load any persisted state
        await self._load_state()

        # Start main event loop
        try:
            await self._run_event_loop()
        except Exception as e:
            self.logger.log_event(
                event_type="orchestrator_error",
                session_id="orchestrator",
                data={"error": str(e)},
            )
            raise
        finally:
            await self._cleanup()

    def stop(self):
        """Stop the orchestrator."""
        self.running = False
        self.logger.log_event(
            event_type="orchestrator_stopped",
            session_id="orchestrator",
            data=self.get_stats(),
        )

    async def _run_event_loop(self):
        """Main event loop for continuous operation."""
        loop_count = 0

        while self.running:
            try:
                # 1. Check work queue for pending work
                await self._process_work_queue()

                # 2. Monitor active work
                await self._monitor_active_work()

                # 3. Perform health checks
                await self._health_check()

                # 4. Background self-improvement (every 10 loops = ~100 seconds)
                loop_count += 1
                if loop_count % 10 == 0:
                    await self._background_self_improvement()

                # 5. Save state
                await self._save_state()

                # 6. Sleep before next iteration
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                self.logger.log_event(
                    event_type="orchestrator_loop_error",
                    session_id="orchestrator",
                    data={"error": str(e)},
                )
                # Continue running on errors
                await asyncio.sleep(self.check_interval)

    async def _process_work_queue(self):
        """Process pending work from queue."""
        # Check if we can take more work
        if len(self.active_work) >= self.max_concurrent_work:
            return

        # Get next work item
        work_item = self.work_queue.get_next_work()
        if not work_item:
            return

        # Determine which agent to assign
        agent_name = await self._select_agent_for_work(work_item)
        if not agent_name:
            self.logger.log_event(
                event_type="no_agent_available",
                session_id="orchestrator",
                data={"work_id": work_item.id},
            )
            return

        # Assign and start work
        self.work_queue.mark_assigned(work_item.id, agent_name)
        self.work_queue.mark_in_progress(work_item.id)
        self.active_work[work_item.id] = work_item

        # Execute work asynchronously
        asyncio.create_task(self._execute_work(work_item, agent_name))

        self.logger.log_event(
            event_type="work_dispatched",
            session_id="orchestrator",
            data={
                "work_id": work_item.id,
                "agent": agent_name,
                "priority": work_item.priority.value,
            },
        )

    async def _select_agent_for_work(self, work_item: WorkItem) -> Optional[str]:
        """
        Select appropriate agent for work item.

        Args:
            work_item: Work to assign

        Returns:
            Agent name, or None if no agent available
        """
        # If work has assigned agent, use that
        if work_item.assigned_agent:
            return work_item.assigned_agent

        # Otherwise, use CEO agent to delegate
        return "ceo-agent"

    async def _execute_work(self, work_item: WorkItem, agent_name: str):
        """
        Execute work item with specified agent.

        Args:
            work_item: Work to execute
            agent_name: Agent to execute with
        """
        try:
            self.logger.log_event(
                event_type="work_execution_started",
                session_id="orchestrator",
                data={"work_id": work_item.id, "agent": agent_name},
            )

            # Create agent instance
            agent = create_agent_by_name(agent_name)
            if not agent:
                raise ValueError(f"Could not create agent: {agent_name}")

            # Execute work
            # Note: This is a simplified version - actual execution would involve
            # running the agent loop with the work description as input
            result = await self._run_agent_on_work(agent, work_item)

            # Mark completed
            self.work_queue.mark_completed(work_item.id, result)
            self.stats["total_work_completed"] += 1

            self.logger.log_event(
                event_type="work_execution_completed",
                session_id="orchestrator",
                data={"work_id": work_item.id, "agent": agent_name},
            )

        except Exception as e:
            # Mark failed (with retry)
            error_msg = str(e)
            self.work_queue.mark_failed(work_item.id, error_msg, retry=True)
            self.stats["total_work_failed"] += 1

            self.logger.log_event(
                event_type="work_execution_failed",
                session_id="orchestrator",
                data={
                    "work_id": work_item.id,
                    "agent": agent_name,
                    "error": error_msg,
                },
            )

        finally:
            # Remove from active work
            if work_item.id in self.active_work:
                del self.active_work[work_item.id]

    async def _run_agent_on_work(self, agent: Any, work_item: WorkItem) -> str:
        """
        Run agent to complete work item.

        Args:
            agent: Agent instance
            work_item: Work to complete

        Returns:
            Result string
        """
        # This is a placeholder - actual implementation would:
        # 1. Load project context if work_item.project_name is set
        # 2. Provide work description and context to agent
        # 3. Run agent loop until completion
        # 4. Extract and return results

        # For now, return a placeholder
        return f"Work completed by {agent.name}: {work_item.description}"

    async def _monitor_active_work(self):
        """Monitor active work for stuck items."""
        from datetime import datetime, timedelta

        now = datetime.now()
        timeout = timedelta(hours=1)  # 1 hour timeout

        for work_id, work_item in list(self.active_work.items()):
            if not work_item.started_at:
                continue

            started = datetime.fromisoformat(work_item.started_at)
            elapsed = now - started

            if elapsed > timeout:
                # Work item is stuck - mark as failed
                self.work_queue.mark_failed(
                    work_id,
                    f"Work timed out after {elapsed.total_seconds():.0f}s",
                    retry=True,
                )

                if work_id in self.active_work:
                    del self.active_work[work_id]

                self.logger.log_event(
                    event_type="work_timeout",
                    session_id="orchestrator",
                    data={"work_id": work_id, "elapsed_seconds": elapsed.total_seconds()},
                )

    async def _health_check(self):
        """Perform health checks on system."""
        self.stats["last_health_check"] = datetime.now().isoformat()

        # Check work queue health
        queue_summary = self.work_queue.get_queue_summary()

        # Check if we have too many failed items
        failed_count = queue_summary["by_status"].get("failed", 0)
        if failed_count > 10:
            self.logger.log_event(
                event_type="health_check_warning",
                session_id="orchestrator",
                data={
                    "reason": "high_failure_count",
                    "failed_count": failed_count,
                },
            )

        # Log health status
        self.logger.log_event(
            event_type="health_check_completed",
            session_id="orchestrator",
            data={
                "active_work": len(self.active_work),
                "queue_summary": queue_summary,
                "stats": self.stats,
            },
        )

    async def _load_state(self):
        """Load persisted state."""
        if not self.state_path.exists():
            return

        try:
            import json

            with open(self.state_path, "r") as f:
                state = json.load(f)

            # Restore stats (but not started_at - that's new)
            if "stats" in state:
                self.stats["total_work_completed"] = state["stats"].get(
                    "total_work_completed", 0
                )
                self.stats["total_work_failed"] = state["stats"].get(
                    "total_work_failed", 0
                )

            self.logger.log_event(
                event_type="orchestrator_state_loaded",
                session_id="orchestrator",
                data={"stats": self.stats},
            )

        except Exception as e:
            self.logger.log_event(
                event_type="orchestrator_state_load_error",
                session_id="orchestrator",
                data={"error": str(e)},
            )

    async def _save_state(self):
        """Save current state to disk."""
        try:
            import json

            state = {
                "stats": self.stats,
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.state_path, "w") as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            self.logger.log_event(
                event_type="orchestrator_state_save_error",
                session_id="orchestrator",
                data={"error": str(e)},
            )

    async def _cleanup(self):
        """Cleanup on shutdown."""
        # Save final state
        await self._save_state()

        # Log final stats
        self.logger.log_event(
            event_type="orchestrator_cleanup",
            session_id="orchestrator",
            data={
                "active_work_count": len(self.active_work),
                "stats": self.stats,
            },
        )

    def add_work(
        self,
        description: str,
        priority: WorkPriority = WorkPriority.MEDIUM,
        project_name: Optional[str] = None,
        assigned_agent: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> WorkItem:
        """
        Add work to queue.

        Args:
            description: Description of work
            priority: Priority level
            project_name: Associated project
            assigned_agent: Specific agent to assign
            context: Additional context

        Returns:
            Created work item
        """
        return self.work_queue.add_work(
            description=description,
            priority=priority,
            project_name=project_name,
            assigned_agent=assigned_agent,
            context=context,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get orchestrator statistics."""
        queue_summary = self.work_queue.get_queue_summary()

        return {
            "running": self.running,
            "started_at": self.stats["started_at"],
            "active_work_count": len(self.active_work),
            "work_queue": queue_summary,
            "total_completed": self.stats["total_work_completed"],
            "total_failed": self.stats["total_work_failed"],
            "last_health_check": self.stats["last_health_check"],
        }

    def get_active_work(self) -> list[WorkItem]:
        """Get list of currently active work items."""
        return list(self.active_work.values())

    async def _background_self_improvement(self):
        """
        Run background self-improvement tasks during idle time.

        This method runs periodically to:
        - Mine knowledge from completed work logs
        - Identify optimization opportunities
        - Consolidate duplicate knowledge entries
        - Analyze error patterns
        - Queue low-priority improvement tasks
        """
        try:
            self.logger.log_event(
                event_type="self_improvement_started",
                session_id="orchestrator",
                data={"stats": self.stats},
            )

            # Only run if we have capacity (not at max concurrent work)
            if len(self.active_work) >= self.max_concurrent_work:
                return

            # Task 1: Mine knowledge from session logs
            await self._mine_knowledge_from_logs()

            # Task 2: Analyze error patterns
            await self._analyze_error_patterns()

            # Task 3: Queue optimization tasks (if idle enough)
            if len(self.active_work) == 0 and self.stats["total_work_completed"] >= 10:
                await self._queue_optimization_tasks()

            self.logger.log_event(
                event_type="self_improvement_completed",
                session_id="orchestrator",
                data={"actions_taken": "knowledge_mining_error_analysis"},
            )

        except Exception as e:
            self.logger.log_event(
                event_type="self_improvement_error",
                level="WARNING",
                session_id="orchestrator",
                data={"error": str(e)},
            )

    async def _mine_knowledge_from_logs(self):
        """
        Analyze session logs to extract learnings automatically.

        Scans recent session logs for patterns like:
        - Frequently occurring errors (→ lesson_learned)
        - Common tool sequences (→ pattern)
        - Successful task completions (→ best_practice)
        """
        try:
            import json
            from pathlib import Path
            from collections import Counter

            # Read recent session logs
            log_file = Path("logs/proto_sessions.jsonl")
            if not log_file.exists():
                return

            # Analyze last 100 lines
            recent_events = []
            with open(log_file, "r") as f:
                lines = f.readlines()
                for line in lines[-100:]:
                    try:
                        event = json.loads(line)
                        recent_events.append(event)
                    except:
                        continue

            # Extract tool usage patterns
            tool_sequences = []
            current_sequence = []

            for event in recent_events:
                if event.get("event_type") == "tool_selected":
                    tool_name = event.get("data", {}).get("tool_name")
                    if tool_name:
                        current_sequence.append(tool_name)
                elif event.get("event_type") == "message_sent" and current_sequence:
                    if len(current_sequence) >= 3:  # Meaningful sequence
                        tool_sequences.append(tuple(current_sequence))
                    current_sequence = []

            # Identify common sequences (potential patterns)
            if tool_sequences:
                sequence_counts = Counter(tool_sequences)
                common_sequences = sequence_counts.most_common(3)

                # If a sequence appears 3+ times, it's a pattern worth capturing
                for sequence, count in common_sequences:
                    if count >= 3:
                        # This would create a knowledge entry in the most recent project
                        # For now, just log it
                        self.logger.log_event(
                            event_type="pattern_discovered",
                            session_id="orchestrator",
                            data={
                                "tool_sequence": list(sequence),
                                "occurrence_count": count,
                                "recommendation": "Consider creating a compound tool for this sequence",
                            },
                        )

        except Exception as e:
            self.logger.log_event(
                event_type="knowledge_mining_error",
                level="WARNING",
                session_id="orchestrator",
                data={"error": str(e)},
            )

    async def _analyze_error_patterns(self):
        """
        Analyze error logs to identify recurring issues.

        Helps system learn which errors are common and how to prevent them.
        """
        try:
            import json
            from pathlib import Path
            from collections import Counter

            error_log = Path("logs/proto_errors.jsonl")
            if not error_log.exists():
                return

            # Read recent errors
            recent_errors = []
            with open(error_log, "r") as f:
                lines = f.readlines()
                for line in lines[-50:]:  # Last 50 errors
                    try:
                        event = json.loads(line)
                        recent_errors.append(event)
                    except:
                        continue

            if not recent_errors:
                return

            # Count error types
            error_types = Counter()
            for error in recent_errors:
                error_type = error.get("event_type", "unknown")
                error_msg = error.get("data", {}).get("error", "")

                # Extract error category (first word or exception type)
                category = error_msg.split(":")[0] if ":" in error_msg else error_type
                error_types[category] += 1

            # Log top recurring errors
            top_errors = error_types.most_common(5)
            if top_errors:
                self.logger.log_event(
                    event_type="error_analysis_completed",
                    session_id="orchestrator",
                    data={
                        "top_errors": [{"type": err, "count": count} for err, count in top_errors],
                        "recommendation": "Review error handlers for frequently occurring errors",
                    },
                )

        except Exception as e:
            self.logger.log_event(
                event_type="error_analysis_failed",
                level="WARNING",
                session_id="orchestrator",
                data={"error": str(e)},
            )

    async def _queue_optimization_tasks(self):
        """
        Queue project-aware optimization tasks based on accumulated knowledge.

        Analyzes each active project's knowledge base to find improvement opportunities.
        """
        try:
            from ..planning import ProjectManager

            # Only queue if we've completed at least 10 tasks and queue is mostly empty
            pending_work = self.work_queue.get_pending_work()
            pending_count = len(pending_work)

            if pending_count > 5:
                return  # Don't add more if queue has many pending items

            # Get all active projects
            project_manager = ProjectManager()
            all_projects = project_manager.list_projects()

            if not all_projects:
                return  # No projects to optimize

            tasks_queued = 0

            # Analyze each project for improvement opportunities
            for project in all_projects[:3]:  # Top 3 most recent projects
                project_name = project.get("slug", "")
                if not project_name:
                    continue

                # Get project's knowledge store
                knowledge_store = project_manager.get_knowledge_store(project_name)
                if not knowledge_store:
                    continue

                # Get all knowledge entries
                all_entries = knowledge_store.get_all_entries()
                if not all_entries:
                    continue

                # Count different knowledge types
                failures = [e for e in all_entries if e.type.value == "lesson_learned"]
                patterns = [e for e in all_entries if e.type.value == "pattern"]

                # OPTIMIZATION 1: If many failures, queue root cause analysis
                if len(failures) >= 5:
                    self.work_queue.add_work(
                        description=f"Analyze and fix root causes of {len(failures)} failures in {project['project_name']}",
                        priority=WorkPriority.MEDIUM,
                        project_name=project_name,
                        assigned_agent="senior-developer",
                        context={
                            "optimization_task": True,
                            "task_type": "root_cause_analysis",
                            "failure_count": len(failures),
                        },
                    )
                    tasks_queued += 1

                # OPTIMIZATION 2: If many patterns, consolidate and create reusable components
                if len(patterns) >= 5:
                    self.work_queue.add_work(
                        description=f"Create reusable tools/components from {len(patterns)} patterns in {project['project_name']}",
                        priority=WorkPriority.LOW,
                        project_name=project_name,
                        assigned_agent="senior-developer",
                        context={
                            "optimization_task": True,
                            "task_type": "pattern_consolidation",
                            "pattern_count": len(patterns),
                        },
                    )
                    tasks_queued += 1

            # GLOBAL OPTIMIZATION: Cross-project knowledge consolidation (only if idle)
            if pending_count == 0 and len(all_projects) > 1:
                self.work_queue.add_work(
                    description="Review knowledge across all projects and consolidate common learnings",
                    priority=WorkPriority.LOW,
                    assigned_agent="data-analyst",
                    context={
                        "optimization_task": True,
                        "task_type": "cross_project_knowledge",
                        "project_count": len(all_projects),
                    },
                )
                tasks_queued += 1

            if tasks_queued > 0:
                self.logger.log_event(
                    event_type="optimization_tasks_queued",
                    session_id="orchestrator",
                    data={
                        "tasks_added": tasks_queued,
                        "reason": "knowledge_based_optimization",
                        "projects_analyzed": len(all_projects[:3]),
                    },
                )

        except Exception as e:
            self.logger.log_event(
                event_type="optimization_queue_error",
                level="WARNING",
                session_id="orchestrator",
                data={"error": str(e)},
            )
