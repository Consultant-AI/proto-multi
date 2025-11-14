#!/bin/bash
# Cleanup script to kill orphaned computer-use CLI processes
# Run this if Claude Code was force-quit and left processes behind

echo "Checking for orphaned computer-use CLI processes..."

# Find all computer_use_demo.cli processes
PIDS=$(ps aux | grep "computer_use_demo.cli" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "✓ No orphaned processes found"
    exit 0
fi

echo "Found orphaned processes:"
ps aux | grep "computer_use_demo.cli" | grep -v grep

echo ""
echo "Killing processes: $PIDS"
kill -9 $PIDS

sleep 1

# Verify they're gone
REMAINING=$(ps aux | grep "computer_use_demo.cli" | grep -v grep | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo "✓ All orphaned processes cleaned up successfully"
else
    echo "⚠ Some processes may still be running"
    ps aux | grep "computer_use_demo.cli" | grep -v grep
fi
