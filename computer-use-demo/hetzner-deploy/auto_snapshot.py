#!/usr/bin/env python3
"""
Automatic snapshot system for Hetzner instances
Can run as a cron job to create daily/weekly snapshots
"""

import os
import sys
from datetime import datetime
from hetzner_manager import HetznerManager


def auto_snapshot(
    instance_id: int,
    keep_last: int = 7,  # Keep last 7 snapshots
    prefix: str = "auto"
):
    """
    Create automatic snapshot and clean up old ones

    Args:
        instance_id: The instance to snapshot
        keep_last: Number of snapshots to keep (default: 7 for weekly)
        prefix: Prefix for snapshot names (default: "auto")
    """

    manager = HetznerManager()

    # Create new snapshot with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    description = f"{prefix}-snapshot-{timestamp}"

    print(f"Creating automatic snapshot: {description}")
    snapshot = manager.create_snapshot(instance_id, description)

    print(f"✅ Snapshot created: {snapshot['id']}")

    # Get all auto snapshots
    all_snapshots = manager.list_snapshots(label_selector="created_by=computer-use-demo")
    auto_snapshots = [
        s for s in all_snapshots
        if s['description'].startswith(f"{prefix}-snapshot-")
    ]

    # Sort by creation date (newest first)
    auto_snapshots.sort(key=lambda x: x['created'], reverse=True)

    # Delete old snapshots (keep only last N)
    if len(auto_snapshots) > keep_last:
        print(f"\nCleaning up old snapshots (keeping last {keep_last})...")
        for old_snapshot in auto_snapshots[keep_last:]:
            print(f"  Deleting: {old_snapshot['description']} (ID: {old_snapshot['id']})")
            manager._request("DELETE", f"images/{old_snapshot['id']}")

        deleted_count = len(auto_snapshots) - keep_last
        print(f"✅ Deleted {deleted_count} old snapshot(s)")
    else:
        print(f"\nTotal snapshots: {len(auto_snapshots)} (under limit of {keep_last})")

    return snapshot


def get_instance_id_from_env():
    """Get instance ID from environment variable"""
    instance_id = os.environ.get('HETZNER_INSTANCE_ID')
    if not instance_id:
        raise ValueError(
            "HETZNER_INSTANCE_ID environment variable not set. "
            "Run this script inside the instance or set the variable manually."
        )
    return int(instance_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automatic snapshot creation")
    parser.add_argument(
        "--instance-id",
        type=int,
        help="Instance ID to snapshot (or set HETZNER_INSTANCE_ID env var)"
    )
    parser.add_argument(
        "--keep-last",
        type=int,
        default=7,
        help="Number of snapshots to keep (default: 7)"
    )
    parser.add_argument(
        "--prefix",
        default="auto",
        help="Snapshot name prefix (default: 'auto')"
    )

    args = parser.parse_args()

    # Get instance ID from args or environment
    try:
        instance_id = args.instance_id or get_instance_id_from_env()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Create snapshot
    try:
        auto_snapshot(instance_id, args.keep_last, args.prefix)
        print("\n✅ Automatic snapshot complete!")
    except Exception as e:
        print(f"\n❌ Error creating snapshot: {e}")
        sys.exit(1)
