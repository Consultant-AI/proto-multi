#!/bin/bash
# Test script for CEO agent with medium-level task via CLI

# Set API key from environment or fail
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY environment variable is not set"
    exit 1
fi

cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-demo

echo "Starting CLI test with medium-level task..."
echo ""
echo "Task: Create a user authentication system with:"
echo "  1. User registration with email/password validation"
echo "  2. Login function with credential checking"
echo "  3. Password hashing for security"
echo "  4. Error handling"
echo "  5. Unit tests"
echo ""
echo "This should trigger CEO agent planning capabilities."
echo ""
echo "=================================================="

# Create input file with the task
cat > /tmp/cli_input.txt << 'EOF'
Create a simple user authentication system with the following:
1. A user registration module that validates email and password
2. A login function that checks credentials
3. Password hashing for security
4. Basic error handling
5. Unit tests for the key functions

Place all files in a new 'auth_system' directory. Use Python with bcrypt for password hashing.
EOF

# Run CLI with the task
python3 -m computer_use_demo.cli --model claude-sonnet-4-5-20250929 --tool-version proto_coding_v1 < /tmp/cli_input.txt

echo ""
echo "=================================================="
echo "Test completed. Checking results..."
