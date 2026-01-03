"""
Human Pool Manager.

Manages a pool of humans for task delegation.
"""

import json
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import (
    EscalationRule,
    Human,
    HumanRequest,
    NotificationChannel,
    RequestPriority,
    RequestStatus,
)


def get_humans_dir() -> Path:
    """Get path to humans directory."""
    return Path.home() / ".proto" / "company" / "humans"


class HumanPoolManager:
    """
    Manages a pool of humans for task delegation.

    Features:
    - Register/unregister humans
    - Create and assign requests
    - Track request status
    - Auto-assign based on skills and workload
    """

    def __init__(self, data_dir: Path | None = None):
        self._data_dir = data_dir or get_humans_dir()
        self._humans: dict[str, Human] = {}
        self._requests: dict[str, HumanRequest] = {}
        self._escalation_rules: list[EscalationRule] = []
        self._lock = threading.Lock()

        # Ensure directories exist
        self._data_dir.mkdir(parents=True, exist_ok=True)
        (self._data_dir / "requests").mkdir(exist_ok=True)
        (self._data_dir / "completed").mkdir(exist_ok=True)

        # Load existing data
        self._load_humans()
        self._load_requests()

    def _load_humans(self) -> None:
        """Load humans from pool.json."""
        pool_file = self._data_dir / "pool.json"
        if pool_file.exists():
            try:
                with open(pool_file, "r") as f:
                    data = json.load(f)

                for human_data in data.get("humans", []):
                    human = Human(
                        id=human_data["id"],
                        name=human_data["name"],
                        email=human_data.get("email"),
                        phone=human_data.get("phone"),
                        slack_id=human_data.get("slack_id"),
                        skills=human_data.get("skills", []),
                        preferred_channel=NotificationChannel(
                            human_data.get("preferred_channel", "email")
                        ),
                        available=human_data.get("available", True),
                        max_workload=human_data.get("max_workload", 5),
                    )
                    self._humans[human.id] = human
            except Exception:
                pass

    def _save_humans(self) -> None:
        """Save humans to pool.json."""
        pool_file = self._data_dir / "pool.json"
        data = {
            "humans": [
                {
                    "id": h.id,
                    "name": h.name,
                    "email": h.email,
                    "phone": h.phone,
                    "slack_id": h.slack_id,
                    "skills": h.skills,
                    "preferred_channel": h.preferred_channel.value,
                    "available": h.available,
                    "max_workload": h.max_workload,
                }
                for h in self._humans.values()
            ]
        }

        with open(pool_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_requests(self) -> None:
        """Load pending requests."""
        requests_dir = self._data_dir / "requests"
        if requests_dir.exists():
            for req_file in requests_dir.glob("*.json"):
                try:
                    with open(req_file, "r") as f:
                        data = json.load(f)
                    request = self._request_from_dict(data)
                    self._requests[request.id] = request

                    # Update human workload
                    if request.assigned_to and request.status in [
                        RequestStatus.ASSIGNED,
                        RequestStatus.IN_PROGRESS,
                    ]:
                        human = self._humans.get(request.assigned_to)
                        if human:
                            human.workload += 1
                except Exception:
                    pass

    def _save_request(self, request: HumanRequest) -> None:
        """Save a request to disk."""
        if request.status in [RequestStatus.COMPLETED, RequestStatus.CANCELLED]:
            # Move to completed
            req_file = self._data_dir / "completed" / f"{request.id}.json"
            # Remove from requests dir
            pending_file = self._data_dir / "requests" / f"{request.id}.json"
            if pending_file.exists():
                pending_file.unlink()
        else:
            req_file = self._data_dir / "requests" / f"{request.id}.json"

        data = self._request_to_dict(request)
        with open(req_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _request_to_dict(self, request: HumanRequest) -> dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "id": request.id,
            "title": request.title,
            "description": request.description,
            "priority": request.priority.value,
            "status": request.status.value,
            "required_skills": request.required_skills,
            "assigned_to": request.assigned_to,
            "created_by": request.created_by,
            "project_name": request.project_name,
            "context": request.context,
            "deadline": request.deadline.isoformat() if request.deadline else None,
            "sla_hours": request.sla_hours,
            "created_at": request.created_at.isoformat(),
            "updated_at": request.updated_at.isoformat(),
            "assigned_at": request.assigned_at.isoformat() if request.assigned_at else None,
            "completed_at": request.completed_at.isoformat() if request.completed_at else None,
            "result": request.result,
            "attachments": request.attachments,
        }

    def _request_from_dict(self, data: dict[str, Any]) -> HumanRequest:
        """Convert dictionary to request."""
        return HumanRequest(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            priority=RequestPriority(data.get("priority", "medium")),
            status=RequestStatus(data.get("status", "pending")),
            required_skills=data.get("required_skills", []),
            assigned_to=data.get("assigned_to"),
            created_by=data.get("created_by"),
            project_name=data.get("project_name"),
            context=data.get("context", {}),
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            sla_hours=data.get("sla_hours"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            assigned_at=datetime.fromisoformat(data["assigned_at"]) if data.get("assigned_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            result=data.get("result"),
            attachments=data.get("attachments", []),
        )

    # Human management

    def register_human(self, human: Human) -> None:
        """Register a human in the pool."""
        with self._lock:
            self._humans[human.id] = human
            self._save_humans()

    def unregister_human(self, human_id: str) -> None:
        """Remove a human from the pool."""
        with self._lock:
            self._humans.pop(human_id, None)
            self._save_humans()

    def get_human(self, human_id: str) -> Human | None:
        """Get a human by ID."""
        return self._humans.get(human_id)

    def list_humans(self, available_only: bool = False) -> list[Human]:
        """List all humans."""
        humans = list(self._humans.values())
        if available_only:
            humans = [h for h in humans if h.available and h.workload < h.max_workload]
        return humans

    def find_humans_by_skill(self, skill: str) -> list[Human]:
        """Find humans with a specific skill."""
        return [h for h in self._humans.values() if skill in h.skills]

    # Request management

    def create_request(
        self,
        title: str,
        description: str,
        priority: RequestPriority = RequestPriority.MEDIUM,
        required_skills: list[str] | None = None,
        created_by: str | None = None,
        project_name: str | None = None,
        context: dict[str, Any] | None = None,
        deadline: datetime | None = None,
        sla_hours: float | None = None,
        auto_assign: bool = True,
    ) -> HumanRequest:
        """
        Create a new human request.

        Args:
            title: Request title
            description: Detailed description
            priority: Priority level
            required_skills: Skills needed
            created_by: Creating agent
            project_name: Project context
            context: Additional context
            deadline: Optional deadline
            sla_hours: SLA in hours
            auto_assign: Whether to auto-assign

        Returns:
            Created request
        """
        request = HumanRequest(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            priority=priority,
            required_skills=required_skills or [],
            created_by=created_by,
            project_name=project_name,
            context=context or {},
            deadline=deadline,
            sla_hours=sla_hours,
        )

        with self._lock:
            self._requests[request.id] = request
            self._save_request(request)

        # Auto-assign if requested
        if auto_assign:
            self.auto_assign_request(request.id)

        return request

    def get_request(self, request_id: str) -> HumanRequest | None:
        """Get a request by ID."""
        return self._requests.get(request_id)

    def list_requests(
        self,
        status: RequestStatus | None = None,
        assigned_to: str | None = None,
    ) -> list[HumanRequest]:
        """List requests with optional filters."""
        requests = list(self._requests.values())

        if status:
            requests = [r for r in requests if r.status == status]

        if assigned_to:
            requests = [r for r in requests if r.assigned_to == assigned_to]

        return sorted(requests, key=lambda r: (r.priority.value, r.created_at))

    def assign_request(self, request_id: str, human_id: str) -> bool:
        """Assign a request to a human."""
        with self._lock:
            request = self._requests.get(request_id)
            human = self._humans.get(human_id)

            if not request or not human:
                return False

            if human.workload >= human.max_workload:
                return False

            # Update request
            request.assigned_to = human_id
            request.status = RequestStatus.ASSIGNED
            request.assigned_at = datetime.utcnow()
            request.updated_at = datetime.utcnow()

            # Update human workload
            human.workload += 1

            self._save_request(request)
            return True

    def auto_assign_request(self, request_id: str) -> bool:
        """
        Auto-assign a request to the best available human.

        Selection criteria:
        1. Has required skills
        2. Is available
        3. Lowest workload
        """
        request = self._requests.get(request_id)
        if not request:
            return False

        # Find matching humans
        candidates = []
        for human in self._humans.values():
            if not human.available:
                continue
            if human.workload >= human.max_workload:
                continue

            # Check skills
            if request.required_skills:
                if not all(s in human.skills for s in request.required_skills):
                    continue

            candidates.append(human)

        if not candidates:
            return False

        # Sort by workload (lowest first)
        candidates.sort(key=lambda h: h.workload)

        # Assign to first candidate
        return self.assign_request(request_id, candidates[0].id)

    def complete_request(
        self,
        request_id: str,
        result: str,
    ) -> bool:
        """Mark a request as completed."""
        with self._lock:
            request = self._requests.get(request_id)
            if not request:
                return False

            # Update human workload
            if request.assigned_to:
                human = self._humans.get(request.assigned_to)
                if human and human.workload > 0:
                    human.workload -= 1

            # Update request
            request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.utcnow()
            request.updated_at = datetime.utcnow()
            request.result = result

            self._save_request(request)

            # Remove from active requests
            self._requests.pop(request_id, None)

            return True

    def cancel_request(self, request_id: str, reason: str = "") -> bool:
        """Cancel a request."""
        with self._lock:
            request = self._requests.get(request_id)
            if not request:
                return False

            # Update human workload
            if request.assigned_to:
                human = self._humans.get(request.assigned_to)
                if human and human.workload > 0:
                    human.workload -= 1

            # Update request
            request.status = RequestStatus.CANCELLED
            request.updated_at = datetime.utcnow()
            request.result = reason

            self._save_request(request)

            # Remove from active requests
            self._requests.pop(request_id, None)

            return True

    def check_escalations(self) -> list[HumanRequest]:
        """Check for requests that need escalation."""
        escalated = []

        for request in self._requests.values():
            if request.is_overdue() and request.status not in [
                RequestStatus.COMPLETED,
                RequestStatus.CANCELLED,
                RequestStatus.ESCALATED,
            ]:
                request.status = RequestStatus.ESCALATED
                request.updated_at = datetime.utcnow()
                self._save_request(request)
                escalated.append(request)

        return escalated


# Global manager instance
_global_manager: HumanPoolManager | None = None


def get_human_pool_manager() -> HumanPoolManager:
    """Get or create the global human pool manager."""
    global _global_manager

    if _global_manager is None:
        _global_manager = HumanPoolManager()

    return _global_manager
