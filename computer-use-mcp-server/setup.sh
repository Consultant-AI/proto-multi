#!/bin/bash
# Setup script for Computer Use MCP Server

echo "🚀 Computer Use MCP Server Setup"
echo "=================================="
echo ""

# Check if cliclick is installed
echo "1. Checking prerequisites..."
if command -v cliclick &> /dev/null; then
    echo "   ✅ cliclick is installed"
else
    echo "   ❌ cliclick is NOT installed"
    echo "   📦 Installing cliclick..."
    if command -v brew &> /dev/null; then
        brew install cliclick
    else
        echo "   ❌ Homebrew not found. Please install Homebrew first:"
        echo "      /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
fi

echo ""
echo "2. Checking Python module..."
if python3 -c "import computer_use_mcp" 2>/dev/null; then
    VERSION=$(python3 -c "import computer_use_mcp; print(computer_use_mcp.__version__)")
    echo "   ✅ Module installed (v$VERSION)"
else
    echo "   ❌ Module not installed"
    echo "   📦 Installing..."
    pip3 install -e .
fi

echo ""
echo "3. Registering with Claude Code..."
echo "   Using Python module method..."

# Use python3 -m method which should always work
claude mcp add --scope user --transport stdio computer-use python3 -m computer_use_mcp.server

if [ $? -eq 0 ]; then
    echo "   ✅ Registered successfully!"
else
    echo "   ⚠️  Registration may have failed. Trying alternative method..."
    # Try with full path
    claude mcp add --scope user --transport stdio computer-use /Library/Frameworks/Python.framework/Versions/3.13/bin/computer-use-mcp
fi

echo ""
echo "4. Verifying registration..."
if claude mcp list 2>/dev/null | grep -q "computer-use"; then
    echo "   ✅ Server is registered!"
else
    echo "   ⚠️  Could not verify registration"
    echo "   Run manually: claude mcp list"
fi

echo ""
echo "============================================"
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Grant accessibility permissions:"
echo "   System Settings > Privacy & Security > Accessibility"
echo "   Add: Terminal, Python, cliclick"
echo ""
echo "2. Restart Claude Code to load the MCP server"
echo ""
echo "3. Test it! Ask Claude Code:"
echo "   - 'Take a screenshot'"
echo "   - 'Get cursor position'"
echo "   - 'Type Hello World'"
echo ""
echo "📚 Documentation: See README.md and QUICK_START.md"
echo "============================================"
