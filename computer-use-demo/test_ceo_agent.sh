#!/bin/bash
# Test script for CEO agent with medium-level task

# Set API key from environment or fail
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY environment variable is not set"
    exit 1
fi

cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-demo

TASK="Create a simple user authentication system with the following:
1. A user registration module that validates email and password
2. A login function that checks credentials
3. Password hashing for security using bcrypt
4. Basic error handling
5. Unit tests for the key functions

Place all files in a new 'auth_system' directory."

echo "================================================================================"
echo "CEO AGENT TEST - Medium Complexity Task"
echo "================================================================================"
echo ""
echo "Task: $TASK"
echo ""
echo "Expected behavior:"
echo "  - CEO agent should analyze task complexity"
echo "  - May create planning documents (look for create_planning_docs tool)"
echo "  - Should implement systematically"
echo "  - Check for .proto/planning/ folder creation"
echo ""
echo "================================================================================"
echo ""

# Run CLI in test mode
python3 -m computer_use_demo.cli \
    --test-mode \
    --test-task "$TASK" \
    --model claude-sonnet-4-5-20250929 \
    --tool-version proto_coding_v1 \
    --log-dir /tmp/ceo-test-logs \
    2>&1 | tee /tmp/ceo_test_output.txt

echo ""
echo "================================================================================"
echo "ANALYZING RESULTS"
echo "================================================================================"
echo ""

# Check for planning documents
if [ -d ".proto/planning" ]; then
    echo "✓ Planning directory exists"
    PROJECT_COUNT=$(find .proto/planning -mindepth 1 -maxdepth 1 -type d | wc -l)
    echo "  Projects found: $PROJECT_COUNT"
    if [ "$PROJECT_COUNT" -gt 0 ]; then
        echo "  Projects:"
        for proj in .proto/planning/*/; do
            if [ -d "$proj" ]; then
                DOC_COUNT=$(find "$proj" -name "*.md" | wc -l)
                echo "    - $(basename "$proj"): $DOC_COUNT documents"
            fi
        done
    fi
else
    echo "⚠ No .proto/planning directory found"
fi

echo ""

# Check for auth_system directory
if [ -d "auth_system" ]; then
    echo "✓ auth_system directory created"
    PY_COUNT=$(find auth_system -name "*.py" | wc -l)
    echo "  Python files: $PY_COUNT"
    if [ "$PY_COUNT" -gt 0 ]; then
        echo "  Files:"
        find auth_system -name "*.py" | while read file; do
            echo "    - $(basename "$file")"
        done
    fi
else
    echo "⚠ auth_system directory not found"
fi

echo ""

# Check for planning tool usage
echo "Checking for planning tool usage in logs..."
if grep -q "create_planning_docs" /tmp/ceo_test_output.txt; then
    echo "✓ create_planning_docs tool was used"
else
    echo "⚠ create_planning_docs tool was NOT used"
fi

if grep -q "delegate_task" /tmp/ceo_test_output.txt; then
    echo "✓ delegate_task tool was used"
else
    echo "⚠ delegate_task tool was NOT used"
fi

if grep -q "read_planning" /tmp/ceo_test_output.txt; then
    echo "✓ read_planning tool was used"
else
    echo "⚠ read_planning tool was NOT used"
fi

echo ""
echo "================================================================================"
echo "Test logs saved to: /tmp/ceo_test_output.txt"
echo "Session logs saved to: /tmp/ceo-test-logs/"
echo "================================================================================"
