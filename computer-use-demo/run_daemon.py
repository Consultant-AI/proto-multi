#!/usr/bin/env python3
"""
Daemon Runner for Proto Multi-Agent System.

Starts and manages the continuous operation orchestrator.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from computer_use_demo.daemon import CompanyOrchestrator, WorkPriority
from computer_use_demo.logging import get_logger


async def run_daemon(
    check_interval: int = 10,
    max_concurrent: int = 5,
    add_initial_work: bool = False,
):
    """
    Run the daemon orchestrator.

    Args:
        check_interval: Seconds between queue checks
        max_concurrent: Maximum concurrent work items
        add_initial_work: Whether to add initial test work
    """
    logger = get_logger()

    logger.log_event(
        event_type="daemon_starting",
        session_id="daemon",
        data={
            "check_interval": check_interval,
            "max_concurrent": max_concurrent,
        },
    )

    # Create orchestrator
    orchestrator = CompanyOrchestrator(
        check_interval=check_interval,
        max_concurrent_work=max_concurrent,
    )

    # Add initial work if requested
    if add_initial_work:
        logger.log_event(
            event_type="adding_initial_work",
            session_id="daemon",
        )

        orchestrator.add_work(
            description="Review all existing projects and provide status update",
            priority=WorkPriority.HIGH,
        )

        orchestrator.add_work(
            description="Check for pending tasks across all projects and prioritize them",
            priority=WorkPriority.MEDIUM,
        )

    print("=" * 80)
    print("Proto Multi-Agent Daemon")
    print("=" * 80)
    print(f"Check interval: {check_interval}s")
    print(f"Max concurrent work: {max_concurrent}")
    print(f"State path: {orchestrator.state_path}")
    print(f"Queue path: {orchestrator.work_queue.queue_path}")
    print()
    print("Starting orchestrator... (Press Ctrl+C to stop)")
    print("=" * 80)
    print()

    # Start orchestrator (runs until stopped)
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal, shutting down gracefully...")
        orchestrator.stop()

        # Show final stats
        stats = orchestrator.get_stats()
        print("\nFinal Statistics:")
        print(f"  Total completed: {stats['total_completed']}")
        print(f"  Total failed: {stats['total_failed']}")
        print(f"  Active work: {stats['active_work_count']}")
        print(f"  Queue summary: {stats['work_queue']}")
        print("\nShutdown complete.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Proto Multi-Agent Daemon for continuous operation"
    )

    parser.add_argument(
        "--check-interval",
        type=int,
        default=10,
        help="Seconds between work queue checks (default: 10)",
    )

    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent work items (default: 5)",
    )

    parser.add_argument(
        "--add-work",
        action="store_true",
        help="Add initial test work to queue",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show daemon statistics and exit",
    )

    parser.add_argument(
        "--queue-status",
        action="store_true",
        help="Show work queue status and exit",
    )

    args = parser.parse_args()

    # Handle info commands
    if args.stats:
        from computer_use_demo.daemon import CompanyOrchestrator

        orchestrator = CompanyOrchestrator()
        stats = orchestrator.get_stats()

        print("Orchestrator Statistics:")
        print(f"  Running: {stats['running']}")
        print(f"  Started at: {stats['started_at']}")
        print(f"  Total completed: {stats['total_completed']}")
        print(f"  Total failed: {stats['total_failed']}")
        print(f"  Active work: {stats['active_work_count']}")
        print(f"  Last health check: {stats['last_health_check']}")
        return 0

    if args.queue_status:
        from computer_use_demo.daemon import WorkQueue

        queue = WorkQueue()
        summary = queue.get_queue_summary()

        print("Work Queue Status:")
        print(f"  Total items: {summary['total']}")
        print("\n  By Status:")
        for status, count in summary['by_status'].items():
            if count > 0:
                print(f"    {status}: {count}")
        print("\n  Pending by Priority:")
        for priority, count in summary['by_priority'].items():
            if count > 0:
                print(f"    {priority}: {count}")
        return 0

    # Run daemon
    try:
        asyncio.run(
            run_daemon(
                check_interval=args.check_interval,
                max_concurrent=args.max_concurrent,
                add_initial_work=args.add_work,
            )
        )
        return 0
    except Exception as e:
        print(f"Error running daemon: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
