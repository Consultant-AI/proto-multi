"""
Test script to verify markdown specialist sub-agents can be loaded.

This script tests that:
1. All 19 specialist markdown files exist
2. They have valid YAML frontmatter
3. They have proper structure (name, description, tools, model)
"""

import os
from pathlib import Path
import yaml


def test_specialist_files():
    """Test that all specialist markdown files exist and are valid."""
    specialists_dir = Path(".claude/agents/specialists")

    # Expected specialists
    expected_specialists = [
        "senior-developer",
        "product-manager",
        "qa-testing",
        "devops",
        "ux-designer",
        "marketing-strategy",
        "technical-writer",
        "data-analyst",
        "customer-success",
        "sales",
        "finance",
        "security",
        "content-marketing",
        "growth-analytics",
        "legal-compliance",
        "hr-people",
        "business-operations",
        "product-strategy",
        "admin-coordinator",
    ]

    print(f"Testing specialist markdown files in: {specialists_dir}")
    print(f"Expected {len(expected_specialists)} specialists\n")

    found_specialists = []
    errors = []

    for specialist_name in expected_specialists:
        file_path = specialists_dir / f"{specialist_name}.md"

        if not file_path.exists():
            errors.append(f"❌ {specialist_name}: File not found at {file_path}")
            continue

        # Read file
        with open(file_path, 'r') as f:
            content = f.read()

        # Check for YAML frontmatter
        if not content.startswith('---'):
            errors.append(f"❌ {specialist_name}: Missing YAML frontmatter")
            continue

        # Extract YAML frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            errors.append(f"❌ {specialist_name}: Invalid YAML frontmatter format")
            continue

        try:
            frontmatter = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            errors.append(f"❌ {specialist_name}: Invalid YAML: {e}")
            continue

        # Validate required fields
        required_fields = ['name', 'description', 'tools', 'model']
        missing_fields = [field for field in required_fields if field not in frontmatter]

        if missing_fields:
            errors.append(f"❌ {specialist_name}: Missing fields: {', '.join(missing_fields)}")
            continue

        # Validate name matches filename
        if frontmatter['name'] != specialist_name:
            errors.append(f"❌ {specialist_name}: Name mismatch (expected {specialist_name}, got {frontmatter['name']})")
            continue

        # Validate model
        valid_models = ['sonnet', 'haiku', 'opus']
        if frontmatter['model'] not in valid_models:
            errors.append(f"❌ {specialist_name}: Invalid model '{frontmatter['model']}' (must be one of {valid_models})")
            continue

        # Check system prompt exists
        system_prompt = parts[2].strip()
        if not system_prompt:
            errors.append(f"❌ {specialist_name}: Empty system prompt")
            continue

        found_specialists.append(specialist_name)
        print(f"✅ {specialist_name}")
        print(f"   Model: {frontmatter['model']}")
        print(f"   Tools: {frontmatter['tools']}")
        print(f"   Description: {frontmatter['description'][:80]}...")
        print()

    # Summary
    print("\n" + "="*80)
    print(f"SUMMARY")
    print("="*80)
    print(f"✅ Found {len(found_specialists)}/{len(expected_specialists)} specialists")

    if errors:
        print(f"\n❌ {len(errors)} errors:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("\n🎉 All specialists validated successfully!")
        return True


if __name__ == "__main__":
    success = test_specialist_files()
    exit(0 if success else 1)
