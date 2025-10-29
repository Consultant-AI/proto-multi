#!/usr/bin/env python3
"""
Instance Spawner - API for chat to spawn new instances for subtasks
"""

import os
import sys
from typing import Optional, Dict
from hetzner_manager import HetznerManager, generate_cloud_init_script


class InstanceSpawner:
    """Manages spawning instances for subtasks from the chat interface"""

    def __init__(self, hetzner_api_token: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.hetzner = HetznerManager(hetzner_api_token)
        self.anthropic_api_key = anthropic_api_key or os.environ.get('ANTHROPIC_API_KEY')

    def spawn_subtask_instance(
        self,
        task_name: str,
        clone_from_snapshot: Optional[int] = None,
        parent_instance_id: Optional[int] = None
    ) -> Dict:
        """
        Spawn a new instance for a subtask

        Args:
            task_name: Name/description of the subtask
            clone_from_snapshot: Optional snapshot ID to clone from
            parent_instance_id: Optional parent instance ID (for creating snapshot first)

        Returns:
            Dict with instance details and access URLs
        """

        # Generate unique name
        import time
        timestamp = int(time.time())
        instance_name = f"subtask-{task_name.lower().replace(' ', '-')[:20]}-{timestamp}"

        # If parent instance specified and no snapshot, create snapshot first
        if parent_instance_id and not clone_from_snapshot:
            print(f"Creating snapshot of parent instance {parent_instance_id}...")
            snapshot = self.hetzner.create_snapshot(
                parent_instance_id,
                f"Auto-snapshot for subtask: {task_name}"
            )
            clone_from_snapshot = snapshot['id']

        # Create instance
        if clone_from_snapshot:
            print(f"Spawning subtask instance from snapshot {clone_from_snapshot}...")
            server = self.hetzner.clone_from_snapshot(
                snapshot_id=clone_from_snapshot,
                name=instance_name
            )
        else:
            print(f"Spawning fresh subtask instance...")
            user_data = generate_cloud_init_script(self.anthropic_api_key)
            server = self.hetzner.create_instance(
                name=instance_name,
                user_data=user_data,
                labels={
                    "app": "computer-use-demo",
                    "type": "subtask",
                    "task": task_name[:50]
                }
            )

        # Build response
        ip = server['public_net']['ipv4']['ip']
        return {
            "instance_id": server['id'],
            "instance_name": instance_name,
            "ip_address": ip,
            "chat_url": f"http://{ip}:8501",
            "desktop_url": f"http://{ip}:8080",
            "task_name": task_name,
            "status": "running"
        }

    def list_subtask_instances(self) -> list:
        """List all subtask instances"""
        return self.hetzner.list_instances(label_selector="type=subtask")

    def stop_subtask_instance(self, instance_id: int) -> None:
        """Stop a subtask instance (to save costs)"""
        self.hetzner.stop_instance(instance_id)

    def cleanup_subtask_instances(self, keep_last: int = 0) -> None:
        """
        Clean up old subtask instances

        Args:
            keep_last: Number of most recent subtask instances to keep
        """
        instances = self.list_subtask_instances()

        # Sort by creation time (newest first)
        instances.sort(key=lambda x: x['created'], reverse=True)

        # Delete old instances
        for instance in instances[keep_last:]:
            print(f"Deleting old subtask instance: {instance['name']}")
            self.hetzner.delete_instance(instance['id'])


# Flask API for chat integration
from flask import Flask, request, jsonify

app = Flask(__name__)
spawner = InstanceSpawner()


@app.route('/spawn', methods=['POST'])
def spawn_instance():
    """
    Spawn a new instance for a subtask

    POST /spawn
    {
        "task_name": "research web scraping",
        "clone_from_snapshot": 12345,  // optional
        "parent_instance_id": 67890     // optional
    }
    """
    data = request.json
    task_name = data.get('task_name', 'unnamed-task')
    clone_from_snapshot = data.get('clone_from_snapshot')
    parent_instance_id = data.get('parent_instance_id')

    try:
        result = spawner.spawn_subtask_instance(
            task_name=task_name,
            clone_from_snapshot=clone_from_snapshot,
            parent_instance_id=parent_instance_id
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/instances', methods=['GET'])
def list_instances():
    """List all subtask instances"""
    try:
        instances = spawner.list_subtask_instances()
        return jsonify({"instances": instances}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stop/<int:instance_id>', methods=['POST'])
def stop_instance(instance_id: int):
    """Stop a subtask instance"""
    try:
        spawner.stop_subtask_instance(instance_id)
        return jsonify({"status": "stopped", "instance_id": instance_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/cleanup', methods=['POST'])
def cleanup_instances():
    """Clean up old subtask instances"""
    keep_last = request.json.get('keep_last', 0) if request.json else 0
    try:
        spawner.cleanup_subtask_instances(keep_last=keep_last)
        return jsonify({"status": "cleaned"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # Run Flask API server
        print("Starting Instance Spawner API on port 5000...")
        app.run(host='0.0.0.0', port=5000)
    else:
        # CLI mode
        import argparse
        parser = argparse.ArgumentParser(description="Instance Spawner for Subtasks")
        parser.add_argument("task_name", help="Name of the subtask")
        parser.add_argument("--snapshot", type=int, help="Clone from snapshot ID")
        parser.add_argument("--parent", type=int, help="Parent instance ID")

        args = parser.parse_args()

        result = spawner.spawn_subtask_instance(
            task_name=args.task_name,
            clone_from_snapshot=args.snapshot,
            parent_instance_id=args.parent
        )

        print(f"\n✅ Subtask instance spawned!")
        print(f"   Instance ID: {result['instance_id']}")
        print(f"   Chat: {result['chat_url']}")
        print(f"   Desktop: {result['desktop_url']}")
