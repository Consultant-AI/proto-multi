# Distribution Guide: Computer Use MCP Bridge

This guide explains how to package and distribute the Computer Use MCP Bridge to other users.

## Quick Start for End Users

If someone sent you this MCP server, follow these steps:

### 1. Prerequisites

**Install Python 3.10+**
```bash
python3 --version  # Should be 3.10 or higher
```

**Install platform-specific tools:**

- **macOS**: `brew install cliclick`
- **Linux**: `sudo apt-get install xdotool gnome-screenshot`
- **Windows**: No additional tools needed

### 2. Installation

```bash
# Clone or download this repository
cd computer-use-mcp-server

# Install the MCP server
pip3 install -e .
```

### 3. Get the Computer Use Demo

```bash
# Navigate to parent directory
cd ..

# Clone the computer-use demo
git clone https://github.com/anthropics/anthropic-quickstarts
mv anthropic-quickstarts/computer-use-demo .
rm -rf anthropic-quickstarts

# Install dependencies
cd computer-use-demo
pip3 install -r computer_use_demo/requirements.txt
cd ..
```

Your directory structure should be:
```
parent-dir/
├── computer-use-demo/
└── computer-use-mcp-server/
```

### 4. Set Up API Key

**Option A: Environment Variable**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Option B: File (Recommended)**
```bash
mkdir -p ~/.anthropic
echo 'your-api-key-here' > ~/.anthropic/api_key
chmod 600 ~/.anthropic/api_key
```

### 5. Configure Claude Code

**Method 1: Command Line**
```bash
claude mcp add computer-use computer-use-mcp
```

**Method 2: Manual Configuration**

Create or edit `.mcp.json` in your project root:
```json
{
  "mcpServers": {
    "computer-use": {
      "command": "computer-use-mcp",
      "transport": "stdio",
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 6. Grant Permissions (macOS)

1. Open System Settings > Privacy & Security > Accessibility
2. Add your terminal app and Python interpreter
3. Restart Claude Code

### 7. Usage

Ask Claude Code to control your computer:

```
You: Open Google Docs and create a new document
You: Take a screenshot and describe what you see
You: Search for flights from New York to Paris
```

Claude Code will use the `computer_use` MCP tool automatically!

---

## For Developers: How to Package & Distribute

### Option 1: GitHub Repository (Recommended)

1. **Create a GitHub repository** for your MCP server
2. **Remove sensitive data** (API keys, credentials)
3. **Add a clear README** with installation instructions
4. **Tag a release** for versioning

```bash
# Create repository
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/computer-use-mcp.git
git push -u origin main

# Tag release
git tag v1.0.0
git push origin v1.0.0
```

Users install with:
```bash
git clone https://github.com/yourusername/computer-use-mcp.git
cd computer-use-mcp
pip3 install -e .
```

### Option 2: PyPI Package

Package and publish to PyPI for easier installation:

```bash
# Install build tools
pip3 install build twine

# Build package
python3 -m build

# Upload to PyPI
python3 -m twine upload dist/*
```

Users install with:
```bash
pip3 install computer-use-mcp
```

### Option 3: Zip File Distribution

For simple sharing:

```bash
# Create distribution
cd computer-use-mcp-server
zip -r computer-use-mcp.zip . -x "*.pyc" -x "__pycache__/*" -x ".git/*"
```

Share the zip file with:
- README.md with installation instructions
- pyproject.toml for dependencies
- src/ directory with code

Users extract and install:
```bash
unzip computer-use-mcp.zip
cd computer-use-mcp-server
pip3 install -e .
```

---

## Configuration Options

### Environment Variables

The MCP server supports these environment variables:

- `ANTHROPIC_API_KEY` (required): Your Anthropic API key

### Claude Code MCP Configuration

**Basic (using environment API key):**
```json
{
  "mcpServers": {
    "computer-use": {
      "command": "computer-use-mcp",
      "transport": "stdio"
    }
  }
}
```

**With explicit API key:**
```json
{
  "mcpServers": {
    "computer-use": {
      "command": "computer-use-mcp",
      "transport": "stdio",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

**Using Python module directly:**
```json
{
  "mcpServers": {
    "computer-use": {
      "command": "python3",
      "args": ["-m", "computer_use_mcp.server"],
      "transport": "stdio"
    }
  }
}
```

---

## Cleanup Orphaned Processes

If Claude Code is force-quit or crashes, it may leave orphaned computer-use CLI processes running.

### Quick Fix

```bash
cd computer-use-mcp-server
./cleanup_orphans.sh
```

### Manual Cleanup

```bash
# Find orphaned processes
ps aux | grep computer_use_demo.cli

# Kill them
kill -9 [PID]
```

The latest version uses process groups to minimize this issue, but force-quits can still leave orphans.

---

## Troubleshooting for End Users

### "command not found: computer-use-mcp"

The script isn't in your PATH. Use the full path or Python module:

```json
{
  "command": "python3",
  "args": ["-m", "computer_use_mcp.server"]
}
```

### "ANTHROPIC_API_KEY not set"

Set the API key:
```bash
export ANTHROPIC_API_KEY='your-key'
# Or create ~/.anthropic/api_key
```

### "computer-use-demo directory not found"

Make sure the directory structure is:
```
parent-dir/
├── computer-use-demo/
└── computer-use-mcp-server/
```

### Permission Errors on macOS

Grant accessibility permissions:
1. System Settings > Privacy & Security > Accessibility
2. Add Terminal/Python
3. Restart Claude Code

---

## Support & Documentation

- **GitHub Issues**: [your-repo-url]/issues
- **Documentation**: See [README.md](README.md)
- **Computer Use Demo**: https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo
- **MCP Protocol**: https://modelcontextprotocol.io/

---

## Security Notes

**IMPORTANT:**
- Never commit API keys to version control
- Use environment variables or `.anthropic/api_key` file
- Add `*.env`, `.anthropic/`, and API key files to `.gitignore`
- Review the code before running - it has full computer control!

**For distributors:**
- Remove all hardcoded credentials
- Use environment variables for sensitive data
- Document security implications clearly
- Consider code signing for production use
