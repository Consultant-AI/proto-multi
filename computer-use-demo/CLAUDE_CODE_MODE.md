# Claude Code Mode - Optimized Configuration

## ✅ Now Running in "Claude Code Mode"

The system is now configured to work **exactly like Claude Code** - preferring direct file operations and commands over GUI automation.

## 🎯 What Changed

### Before (GUI-heavy):
```
User: "Create a tic-tac-toe game"
Agent:
  1. Takes screenshot 📸
  2. Opens text editor via GUI 🖱️
  3. Types code using keyboard simulation ⌨️
  4. Takes more screenshots 📸
  = SLOW and screenshot-heavy
```

### After (Direct tools):
```
User: "Create a tic-tac-toe game"
Agent:
  1. Uses bash: mkdir tic-tac-toe ⚡
  2. Uses edit tool: creates index.html ⚡
  3. Uses edit tool: creates game.js ⚡
  4. Uses bash: python3 -m http.server ⚡
  = FAST and efficient (like Claude Code!)
```

## 🚀 Configuration Applied

**`.claude/settings.json` - Optimized:**
- ❌ Auto-verification: **DISABLED**
- ❌ Visual verification: **DISABLED**
- ❌ Subagents: **DISABLED**
- ❌ Feedback loops: **DISABLED**
- ✅ Session persistence: **ENABLED**
- ✅ Direct tools (bash, edit): **PREFERRED**
- ✅ GUI tools (computer): **Available when needed**

**`webui.py` - Updated:**
```python
self.enable_verification = False  # Fast, direct execution
self.enable_subagents = False     # Simpler workflow
```

## 📋 Tool Usage Guide

### ✅ CORRECT Usage (Claude Code Style)

**Creating Files:**
```python
# Uses str_replace_editor tool directly
create file: index.html
content: <html>...</html>
```

**Running Commands:**
```bash
# Uses bash tool directly
npm install
python3 script.py
mkdir my-project
```

**File Editing:**
```python
# Uses str_replace_editor tool
str_replace in file.js:
  old: function old()
  new: function new()
```

### ❌ AVOID (GUI-heavy approach)

**Don't do this:**
```
❌ Take screenshot first
❌ Open text editor via computer tool
❌ Type code using keyboard simulation
❌ Take screenshot to verify
```

## 🎨 When to Use GUI (Computer Tool)

Use GUI **ONLY** for:
- ✅ Opening browsers and clicking links
- ✅ Visual verification (optional screenshots)
- ✅ Applications that REQUIRE GUI interaction
- ✅ Testing UI manually

**Example - Good use of computer tool:**
```
"Open Chrome, navigate to localhost:8000, and show me what the game looks like"
✅ This REQUIRES browser interaction
```

**Example - Bad use of computer tool:**
```
"Create index.html with game code"
❌ This should use edit tool directly!
```

## 🧪 Test the New Behavior

Try this prompt:

```
Create a simple Python web server project:
1. Create folder 'web-server'
2. Create app.py with a Flask hello world
3. Create requirements.txt
4. Show me the file contents
```

**Expected behavior (Claude Code mode):**
- ✅ Uses `bash` to create directory
- ✅ Uses `str_replace_editor` to create app.py
- ✅ Uses `str_replace_editor` to create requirements.txt
- ✅ Uses `bash` to show contents
- ❌ NO screenshots taken
- ❌ NO GUI interaction
- ⚡ FAST execution

## 📊 Comparison

| Task | GUI Mode | Claude Code Mode |
|------|----------|------------------|
| Create 3 files | 15 tool calls | 4 tool calls |
| Screenshots | 5-10 images | 0-1 images |
| Speed | Slow | Fast |
| Context usage | High | Low |
| Behavior | Like human using GUI | Like programmer using CLI |

## 🔧 Re-Enable Advanced Features

If you want verification/subagents for complex tasks:

**Edit `.claude/settings.json`:**
```json
{
  "agent_sdk": {
    "auto_verification": true,    // Enable verification
    "subagents_enabled": true     // Enable parallelization
  }
}
```

**Or edit `webui.py` line 96-97:**
```python
self.enable_verification = True   # Enable verification
self.enable_subagents = True      # Enable subagents
```

Then restart the webui.

## 🎯 Current Mode Benefits

✅ **Fast**: Direct tool execution (no GUI overhead)
✅ **Efficient**: Minimal context usage
✅ **Claude Code-like**: Same workflow as Claude Code
✅ **Session persistence**: Still saves everything
✅ **GUI available**: Can still use when needed

## 🚀 Start Using

```bash
cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-demo
python3 -m computer_use_demo.webui
```

Open http://localhost:8000

Now it works like Claude Code - fast, direct, efficient! 🎉

---

## 💡 Pro Tips

1. **File operations**: Agent will use `str_replace_editor` tool
2. **Commands**: Agent will use `bash` tool
3. **GUI**: Only used when explicitly needed
4. **Verification**: Manual (you verify the output yourself)
5. **Sessions**: Still persisted in `~/.claude/projects/`

## 🆘 Troubleshooting

**If agent still takes too many screenshots:**
- Check `.claude/CLAUDE.md` has the tool priority guidance
- Verify `.claude/settings.json` has verification disabled
- Restart the webui

**To see what mode you're in:**
```python
# Check session settings
cat ~/.claude/projects/webui-*/metadata.json
```

Enjoy the optimized Claude Code experience! ⚡
