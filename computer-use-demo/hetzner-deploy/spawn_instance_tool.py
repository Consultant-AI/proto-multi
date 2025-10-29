"""
Tool definition for Claude to spawn new instances for subtasks
This can be integrated into the computer use demo
"""

from typing import ClassVar, Literal
from anthropic.types.beta import BetaToolUnionParam
import os
import requests


class SpawnInstanceTool:
    """
    A tool that allows Claude to spawn new Hetzner instances for subtasks.
    When Claude decides a subtask needs its own environment, it can create a new instance.
    """

    name: ClassVar[Literal["spawn_instance"]] = "spawn_instance"
    api_type: ClassVar[Literal["custom"]] = "custom"

    def __init__(self):
        self.spawner_api_url = os.environ.get(
            'INSTANCE_SPAWNER_API',
            'http://localhost:5000'
        )

    def to_params(self) -> BetaToolUnionParam:
        return {
            "type": "custom",
            "name": self.name,
            "description": (
                "Spawn a new Hetzner cloud instance for a subtask. "
                "Use this when you need to delegate a complex task to a separate environment. "
                "The new instance will have the same computer use capabilities and can work independently. "
                "You can optionally clone from a snapshot to preserve installed software/configurations."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "task_name": {
                        "type": "string",
                        "description": "Brief description of the subtask (e.g., 'web scraping', 'data analysis')"
                    },
                    "clone_from_current": {
                        "type": "boolean",
                        "description": "Whether to clone from current instance (preserves installed software). Default: false",
                        "default": False
                    },
                    "reason": {
                        "type": "string",
                        "description": "Why this subtask needs a separate instance"
                    }
                },
                "required": ["task_name", "reason"]
            }
        }

    def __call__(
        self,
        task_name: str,
        reason: str,
        clone_from_current: bool = False,
        **kwargs
    ):
        """
        Spawn a new instance for a subtask

        Args:
            task_name: Description of the subtask
            reason: Why a separate instance is needed
            clone_from_current: Whether to clone from current instance

        Returns:
            Information about the spawned instance
        """

        # Get current instance ID if cloning
        parent_instance_id = None
        if clone_from_current:
            parent_instance_id = os.environ.get('HETZNER_INSTANCE_ID')

        # Call spawner API
        try:
            response = requests.post(
                f"{self.spawner_api_url}/spawn",
                json={
                    "task_name": task_name,
                    "parent_instance_id": parent_instance_id if clone_from_current else None
                },
                timeout=300  # 5 minutes for instance creation
            )
            response.raise_for_status()
            result = response.json()

            return {
                "success": True,
                "instance_id": result['instance_id'],
                "instance_name": result['instance_name'],
                "chat_url": result['chat_url'],
                "desktop_url": result['desktop_url'],
                "message": (
                    f"✅ Spawned instance '{result['instance_name']}' for task: {task_name}\n"
                    f"   Chat interface: {result['chat_url']}\n"
                    f"   Desktop viewer: {result['desktop_url']}\n"
                    f"   Instance will be automatically stopped after inactivity to save costs."
                )
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Failed to spawn instance: {str(e)}"
            }


# Example integration into computer use demo tools
"""
To integrate this into computer_use_demo/tools/__init__.py:

1. Add to imports:
from .spawn_instance_tool import SpawnInstanceTool

2. Add to tool groups:
TOOL_GROUPS_BY_VERSION = {
    ToolVersion.V1: ToolGroup(
        tools=[
            BashTool,
            ComputerTool,
            EditTool,
            SpawnInstanceTool,  # Add this
        ],
        ...
    ),
}

3. Set environment variable in spawned instances:
INSTANCE_SPAWNER_API=http://your-main-server:5000
HETZNER_INSTANCE_ID=<current_instance_id>
"""
