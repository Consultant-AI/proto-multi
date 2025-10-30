# Quick Start Guide - Computer Use Demo Enhanced Edition

## Prerequisites

1. **Docker Desktop** installed and running
2. **Anthropic API Key** - Get one from [Claude Console](https://console.anthropic.com/)
3. **8GB RAM minimum** (16GB recommended)
4. **10GB free disk space**

## Installation (3 steps)

### Step 1: Build the Container

```bash
cd computer-use-demo
./build-and-run.sh
```

This will take 10-15 minutes on first build (downloads Ubuntu 24.04 and all applications).

### Step 2: Set Your API Key

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Or add to your shell profile (~/.bashrc or ~/.zshrc):
```bash
echo 'export ANTHROPIC_API_KEY=sk-ant-api03-your-key-here' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Run the Container

```bash
./run.sh
```

## Access the Demo

Once running, open your browser to:
- **Main Interface**: http://localhost:8080 ← Start here!
- Chat Only: http://localhost:8501
- Desktop Only: http://localhost:6080/vnc.html

## First Steps

1. **Open the interface** at http://localhost:8080
2. **Type a message** to Claude, for example:
   - "Open Chromium and search for cat pictures"
   - "Create a new document in LibreOffice Writer"
   - "Open VS Code and write a hello world Python script"
3. **Watch Claude work** in the desktop view
4. **See responses** in the chat interface

## Example Tasks to Try

### Web Browsing
```
"Open Chromium and go to wikipedia.org, then search for 'artificial intelligence'"
```

### Document Creation
```
"Create a new LibreOffice Writer document with a resume template"
```

### Coding
```
"Open VS Code and create a new Python file called hello.py with a hello world script"
```

### Research
```
"Search for the latest news about AI, open the first 3 articles in separate tabs, and summarize what you find"
```

### Data Work
```
"Create a spreadsheet in LibreOffice Calc with monthly expenses for 2025"
```

## Available Applications

The desktop comes with these pre-installed apps (visible in the taskbar):

1. **Chromium** - Web browser
2. **Firefox** - Alternative web browser
3. **VS Code** - Code editor and IDE
4. **LibreOffice** - Office suite (Writer, Calc, Impress, Draw)
5. **Terminal** - Command line access
6. **Text Editor** - Simple text editing (gedit)
7. **File Manager** - Browse files (PCManFM)
8. **Calculator** - Basic calculations

## Stopping the Demo

Press `Ctrl+C` in the terminal where the container is running, or:

```bash
docker stop $(docker ps -q --filter ancestor=computer-use-demo:local)
```

## Restarting

Just run again:
```bash
./run.sh
```

Your API key and settings are saved in `~/.anthropic/` and will persist.

## Troubleshooting

### "docker: command not found"
→ Install Docker Desktop from https://www.docker.com/products/docker-desktop/

### "API key not set"
→ Make sure you exported your ANTHROPIC_API_KEY before running ./run.sh

### "Port already in use"
→ Another instance is running. Stop it first:
```bash
docker ps  # Find the container ID
docker stop <container-id>
```

### Build fails on Apple Silicon (M1/M2/M3)
→ This is now fixed! The enhanced version uses Chromium which supports ARM64.

### Desktop not showing
→ Wait 30-60 seconds after starting. The desktop environment takes time to initialize.

### Applications won't launch
→ Try clicking the icon again or wait a few seconds. GUI apps in containers can be slow to start initially.

## Tips for Best Results

1. **Be specific**: Instead of "open a browser", say "open Chromium and go to google.com"

2. **One task at a time**: Let Claude complete one task before asking for another

3. **Use screenshots**: Ask Claude to "take a screenshot" to see what's on screen

4. **Check the desktop view**: Watch what Claude is doing in real-time

5. **Be patient**: Some operations take time, especially first launch of applications

## Advanced Configuration

### Custom Screen Resolution

```bash
docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -e WIDTH=1920 \
    -e HEIGHT=1080 \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 -p 8501:8501 -p 6080:6080 -p 8080:8080 \
    -it computer-use-demo:local
```

Recommended: 1024x768 (default) for best Claude vision performance.

### Different Claude Model

In the Streamlit sidebar (http://localhost:8501):
- Change "Model" field
- Options: claude-sonnet-4-5-20250929 (default), claude-opus-4-20250514, etc.

### Custom System Prompt

In the Streamlit sidebar:
- Use "Custom System Prompt Suffix" field
- Add additional instructions for Claude

### AWS Bedrock or Google Vertex

See the main [README.md](README.md#bedrock) for instructions on using alternative API providers.

## What Makes This Enhanced?

Compared to the original demo, this version has:

✅ **Ubuntu 24.04** (vs 22.04)
✅ **Chromium** (works on ARM Macs!)
✅ **VS Code** (full IDE)
✅ **LibreOffice** (complete office suite)
✅ **Modern UI** (Arc-Dark theme, Papirus icons)
✅ **Better documentation** (you're reading it!)

## Learn More

- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- **Changes**: See [CHANGES.md](CHANGES.md) for full changelog
- **README**: See [README.md](README.md) for complete documentation

## Getting Help

If you encounter issues:

1. Check the logs:
   ```bash
   docker logs $(docker ps -q --filter ancestor=computer-use-demo:local)
   ```

2. Review the HTTP Exchange Logs tab in the UI (http://localhost:8501)

3. Check the [Anthropic Documentation](https://docs.claude.com/en/docs/build-with-claude/computer-use)

4. File an issue on GitHub (if this is a public repo)

## Security Reminder

⚠️ This is a demo environment. Do not:
- Access sensitive accounts
- Enter passwords or API keys (except in the Streamlit UI)
- Process confidential data
- Allow access from untrusted networks

The container provides isolation, but Claude has full control within it.

---

**Ready to start?** Run `./build-and-run.sh` and enjoy! 🚀
