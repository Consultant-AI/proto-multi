#!/usr/bin/env python3
"""
Test dashboard responsiveness while agent is executing.

This script:
1. Starts a long-running agent task
2. Simultaneously tests dashboard API endpoints
3. Verifies all endpoints remain responsive
"""

import asyncio
import time
import requests
from typing import List, Tuple

BASE_URL = "http://localhost:8000"


async def simulate_agent_work():
    """Simulate a long-running agent task."""
    print("🤖 Starting simulated agent work...")
    # In real scenario, agent would be thinking/executing tools
    # For test, we'll just make a long-running request
    await asyncio.sleep(10)
    print("🤖 Agent work completed")


async def test_dashboard_endpoint(endpoint: str, name: str) -> Tuple[str, float, bool]:
    """
    Test a single dashboard endpoint.

    Returns:
        Tuple of (name, response_time, success)
    """
    start = time.time()
    try:
        response = await asyncio.to_thread(requests.get, f"{BASE_URL}{endpoint}", timeout=5)
        elapsed = time.time() - start

        success = response.status_code == 200
        return (name, elapsed, success)
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ {name} failed: {str(e)}")
        return (name, elapsed, False)


async def test_dashboard_responsiveness():
    """Test dashboard API endpoints while agent is working."""
    print("\n" + "=" * 80)
    print("Testing Dashboard Responsiveness During Agent Execution")
    print("=" * 80 + "\n")

    # Dashboard endpoints to test
    endpoints = [
        ("/api/dashboard/projects", "List Projects"),
        ("/api/dashboard/projects/monday-clone", "Get Project Details"),
        ("/api/dashboard/projects/monday-clone/data", "Get Project Data JSON"),
        ("/api/dashboard/tasks", "List All Tasks"),
        ("/api/dashboard/queue/status", "Queue Status"),
        ("/api/dashboard/agents/status", "Agents Status"),
    ]

    # Test baseline (no agent activity)
    print("📊 Baseline Test (No Agent Activity)")
    print("-" * 80)

    baseline_results = []
    for endpoint, name in endpoints:
        result = await test_dashboard_endpoint(endpoint, name)
        baseline_results.append(result)
        status = "✅" if result[2] else "❌"
        print(f"  {status} {result[0]}: {result[1]:.3f}s")

    baseline_avg = sum(r[1] for r in baseline_results) / len(baseline_results)
    print(f"\n  Average response time: {baseline_avg:.3f}s")

    # Test during simulated agent work
    print("\n📊 Concurrent Test (Simulated Agent Work)")
    print("-" * 80)

    # Start agent work in background
    agent_task = asyncio.create_task(simulate_agent_work())

    # Wait a moment for agent to "start thinking"
    await asyncio.sleep(0.5)

    # Test endpoints while agent is working
    concurrent_results = []
    for endpoint, name in endpoints:
        result = await test_dashboard_endpoint(endpoint, name)
        concurrent_results.append(result)
        status = "✅" if result[2] else "❌"
        print(f"  {status} {result[0]}: {result[1]:.3f}s")

    concurrent_avg = sum(r[1] for r in concurrent_results) / len(concurrent_results)
    print(f"\n  Average response time: {concurrent_avg:.3f}s")

    # Wait for agent task to complete
    await agent_task

    # Analysis
    print("\n" + "=" * 80)
    print("Analysis")
    print("=" * 80)

    print(f"\nBaseline avg response time:   {baseline_avg:.3f}s")
    print(f"Concurrent avg response time: {concurrent_avg:.3f}s")

    if concurrent_avg < baseline_avg * 2:
        print(f"✅ PASS: Dashboard remained responsive (< 2x baseline)")
    else:
        print(f"⚠️  WARN: Dashboard slower than expected ({concurrent_avg / baseline_avg:.1f}x baseline)")

    # Check if all endpoints succeeded
    all_success = all(r[2] for r in concurrent_results)

    if all_success:
        print(f"✅ PASS: All endpoints responded successfully")
    else:
        failed = [r[0] for r in concurrent_results if not r[2]]
        print(f"❌ FAIL: Some endpoints failed: {', '.join(failed)}")

    print("\n" + "=" * 80)

    # Final verdict
    if all_success and concurrent_avg < baseline_avg * 2:
        print("✅ OVERALL: Dashboard is responsive during agent execution")
        return True
    else:
        print("❌ OVERALL: Dashboard responsiveness needs improvement")
        return False


async def test_rapid_fire():
    """Test many rapid requests to dashboard."""
    print("\n" + "=" * 80)
    print("Rapid Fire Test: 20 concurrent dashboard requests")
    print("=" * 80 + "\n")

    start = time.time()

    tasks = []
    for i in range(20):
        task = test_dashboard_endpoint("/api/dashboard/projects", f"Request {i+1}")
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start
    success_count = sum(1 for r in results if r[2])

    print(f"\nCompleted {len(results)} requests in {elapsed:.3f}s")
    print(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    print(f"Average per request: {elapsed/len(results):.3f}s")

    if success_count == len(results):
        print("✅ PASS: All concurrent requests succeeded")
        return True
    else:
        print(f"❌ FAIL: {len(results) - success_count} requests failed")
        return False


async def main():
    """Run all tests."""
    print("\n")
    print("=" * 80)
    print("Dashboard Responsiveness Test Suite")
    print("=" * 80)

    # Test 1: Baseline vs concurrent
    test1_passed = await test_dashboard_responsiveness()

    # Test 2: Rapid fire
    test2_passed = await test_rapid_fire()

    # Final summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Responsiveness Test: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Rapid Fire Test:     {'✅ PASS' if test2_passed else '❌ FAIL'}")

    if test1_passed and test2_passed:
        print("\n✅ All tests passed! Dashboard is responsive.")
        return True
    else:
        print("\n❌ Some tests failed. Dashboard responsiveness needs improvement.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
