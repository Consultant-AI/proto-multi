#!/usr/bin/env python3
"""
Test script for Proto Planning and Multi-Agent System.

This script demonstrates the complete workflow:
1. Task complexity analysis
2. Planning document generation
3. Project structure creation
4. Reading planning documents
"""

import asyncio

from computer_use_demo.planning import ProjectManager, TaskComplexityAnalyzer


async def test_complexity_analysis():
    """Test the task complexity analyzer."""
    print("=" * 60)
    print("TEST 1: Task Complexity Analysis")
    print("=" * 60)

    analyzer = TaskComplexityAnalyzer()

    # Test different complexity levels
    test_tasks = [
        "Fix typo in README.md",
        "Add user authentication with JWT tokens",
        "Build a complete e-commerce platform with payments and admin dashboard",
    ]

    for task in test_tasks:
        print(f"\nTask: {task}")
        analysis = analyzer.analyze(task)
        print(f"  Complexity: {analysis.complexity}")
        print(f"  Planning required: {analysis.planning_required}")
        print(f"  Estimated steps: {analysis.estimated_steps}")
        print(f"  Required specialists: {', '.join(analysis.required_specialists) or 'None'}")
        print(f"  Reasoning: {analysis.reasoning}")


async def test_project_structure():
    """Test project structure creation."""
    print("\n" + "=" * 60)
    print("TEST 2: Project Structure Management")
    print("=" * 60)

    pm = ProjectManager()

    # Create a test project
    project_name = "test-ecommerce-platform"
    print(f"\nCreating project: {project_name}")

    if pm.project_exists(project_name):
        print(f"  Project already exists at: {pm.get_project_path(project_name)}")
    else:
        project_path = pm.create_project(project_name)
        print(f"  Project created at: {project_path}")
        print(f"  Structure:")
        print(f"    - {project_path}/")
        print(f"    - {project_path}/agents/")
        print(f"    - {project_path}/.project_metadata.json")

    # List all projects
    print("\nAll projects:")
    projects = pm.list_projects()
    for project in projects:
        print(f"  - {project['project_name']} (slug: {project['slug']})")
        print(f"    Status: {project.get('status', 'unknown')}")
        print(f"    Created: {project.get('created_at', 'unknown')}")


async def test_document_templates():
    """Test planning document templates."""
    print("\n" + "=" * 60)
    print("TEST 3: Planning Document Templates")
    print("=" * 60)

    from computer_use_demo.planning import PlanningDocuments

    print("\nAvailable document templates:")
    templates = PlanningDocuments.get_all_templates()

    for doc_type, template in templates.items():
        print(f"\n  {template.title} ({template.filename})")
        print(f"    Type: {template.doc_type}")
        # Show first 100 chars of generation prompt
        prompt_preview = template.generation_prompt[:100].replace("\n", " ")
        print(f"    Prompt: {prompt_preview}...")


async def test_tool_availability():
    """Test that planning tools are available."""
    print("\n" + "=" * 60)
    print("TEST 4: Planning Tools Availability")
    print("=" * 60)

    from computer_use_demo.tools.planning import (
        DelegateTaskTool,
        PlanningTool,
        ReadPlanningTool,
    )

    print("\nPlanning tools:")
    tools = [PlanningTool, DelegateTaskTool, ReadPlanningTool]

    for tool_class in tools:
        tool = tool_class()
        print(f"\n  {tool.name}")
        print(f"    API Type: {tool.api_type}")
        params = tool.to_params()
        print(f"    Description: {params['description'][:100]}...")


async def test_agent_system():
    """Test agent system initialization."""
    print("\n" + "=" * 60)
    print("TEST 5: Agent System")
    print("=" * 60)

    from computer_use_demo.agents import (
        CEOAgent,
        DesignAgent,
        DeveloperAgent,
        MarketingAgent,
    )

    print("\nAgent classes:")
    agents = {
        "CEO": CEOAgent,
        "Marketing": MarketingAgent,
        "Developer": DeveloperAgent,
        "Design": DesignAgent,
    }

    for name, agent_class in agents.items():
        agent = agent_class()
        print(f"\n  {name} Agent")
        print(f"    Role: {agent.config.role}")
        print(f"    Name: {agent.config.name}")
        print(f"    Model: {agent.config.model}")
        print(f"    Max iterations: {agent.config.max_iterations}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PROTO PLANNING & MULTI-AGENT SYSTEM TEST")
    print("=" * 60)

    try:
        await test_complexity_analysis()
        await test_project_structure()
        await test_document_templates()
        await test_tool_availability()
        await test_agent_system()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nThe planning and multi-agent system is fully operational!")
        print("Next steps:")
        print("  1. Use the WebUI to test with real tasks")
        print("  2. Try the create_planning_docs tool")
        print("  3. Test delegation to specialist agents")
        print()

    except Exception as e:
        print("\n" + "=" * 60)
        print("TEST FAILED ✗")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
