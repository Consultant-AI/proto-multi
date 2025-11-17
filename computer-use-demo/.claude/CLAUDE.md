# Desktop Automation Conventions

This file contains learned conventions and patterns for desktop automation in this environment.

## 🎯 TOOL USAGE PRIORITY (Claude Code Style)

**ALWAYS prefer direct tools over GUI when possible:**

1. **For File Operations**: Use `str_replace_editor` tool (NOT computer tool)
   - Create files: `command="create"`
   - Edit files: `command="str_replace"`
   - View files: `command="view"`

2. **For Commands**: Use `bash` tool (NOT computer tool with terminal)
   - Run commands directly
   - Check output
   - Execute scripts

3. **For GUI Tasks**: Use `computer` tool for visual interaction:
   - ✅ Opening browsers (Chrome, Firefox)
   - ✅ Clicking links and testing web applications
   - ✅ Visual verification with screenshots
   - ✅ Applications that REQUIRE GUI interaction
   - ❌ NOT for file operations (use str_replace_editor)
   - ❌ NOT for running commands (use bash)

**Example - Creating AND testing a web project (CORRECT - HYBRID WORKFLOW):**
```bash
# Phase 1: Use direct tools (FAST)
1. bash → mkdir -p my-project
2. str_replace_editor → create index.html
3. str_replace_editor → create style.css
4. str_replace_editor → create script.js
5. bash → cd my-project && python3 -m http.server 8000 &

# Phase 2: Use GUI tools (VISUAL)
6. computer → open Chrome to localhost:8000
7. computer → click and test the application
8. computer → screenshot to show results

BOTH phases are important!
```

**Example - What NOT to do (WRONG):**
```
❌ Phase 1: Use computer tool for file creation
❌ computer → screenshot first
❌ computer → click file manager
❌ computer → open text editor
❌ computer → type code character by character

OR

❌ Phase 2: Skip GUI testing entirely
❌ Create files with bash/edit but never open browser
❌ Never test or verify the application works
```

**KEY PRINCIPLES - Use the RIGHT tool for the job:**

1. **Tool Selection Based on Task Type:**
   - File/command tasks → bash, str_replace_editor (FAST, DIRECT)
   - Visual/GUI tasks → computer (for seeing and interacting)

2. **Understanding User Intent:**
   - "Create X" → Use bash/edit to create files
   - "Show me X" → Use computer to display visually
   - "Test X" or "Run X in browser" → Use computer for interaction
   - "Create and test X" → Use bash/edit THEN computer

3. **Don't Hardcode - Be Intelligent:**
   - Not every task needs both tool types
   - Some tasks only need file tools (create files)
   - Some tasks only need computer tool (click a button)
   - Some tasks need both (create files AND test in browser)
   - **Read the user's request carefully and choose appropriately**

4. **Examples of Tool Matching:**
   - "Create index.html" → str_replace_editor only
   - "Open Chrome" → computer tool only
   - "Create game and play it" → str_replace_editor + computer
   - "Click the submit button" → computer tool only
   - "Run npm install" → bash tool only

5. **AUTONOMOUS OPERATION - NEVER STOP UNTIL COMPLETE:**
   - ❌ DO NOT ask user questions mid-task
   - ❌ DO NOT wait for user approval
   - ❌ DO NOT stop after partial completion
   - ✅ Make all decisions autonomously
   - ✅ Complete the ENTIRE task before stopping
   - ✅ If user says "test it" - you open browser and test it yourself
   - ✅ Work continuously from start to finish

## System Information

- **OS**: Ubuntu 24.04 LTS
- **Display**: :1 (1024x768 or configured resolution)
- **Desktop**: Modern desktop environment with pre-installed applications
- **Prefer**: Direct file/command tools (like Claude Code)
- **GUI**: Available but use sparingly

## Application Launching

### GUI Applications
All GUI applications run on DISPLAY=:1. Use subshells with bash tool:

```bash
(DISPLAY=:1 application-name &)
```

### Common Applications

**Google Chrome:**
```bash
(DISPLAY=:1 google-chrome --no-sandbox &)
```
- Always use --no-sandbox flag for container compatibility
- If startup wizard appears, IGNORE it - click address bar and enter URL

**Firefox:**
```bash
(DISPLAY=:1 firefox &)
```
or click Firefox icon on desktop
- Ignore startup wizards
- Click address bar to navigate

**VS Code:**
```bash
(DISPLAY=:1 code --no-sandbox &)
```
or click VS Code icon
- Use --no-sandbox flag for container compatibility
- Takes a few seconds to appear

**LibreOffice:**
```bash
(DISPLAY=:1 libreoffice &)
```
or click LibreOffice icon

**Terminal:**
- Use bash tool directly instead of launching GUI terminal
- Only launch xterm if visual terminal needed: `(DISPLAY=:1 xterm &)`

## Verification Best Practices

### After GUI Actions
1. **Always** take a screenshot after launching applications
2. **Wait** 2-3 seconds for applications to fully appear
3. **Verify** window is visible before interacting

### After File Operations
1. Use bash tool to verify file exists: `ls -la /path/to/file`
2. Check file contents: `head -n 10 /path/to/file`
3. For code files, consider opening in VS Code for visual verification

### After Commands
1. **Check exit codes**: Commands should return 0 for success
2. **Validate output**: Look for success indicators in stdout
3. **Monitor errors**: Check stderr for warnings/errors

## Common Patterns

### Multi-Step Workflows
For complex tasks, use this pattern:
1. **Gather**: Take screenshot to see current state
2. **Act**: Perform action (click, type, run command)
3. **Verify**: Take screenshot or run check command
4. **Iterate**: If failed, analyze and retry with corrections

### File Editing
**Prefer direct file tools over GUI:**
- For simple edits: Use str_replace_editor tool
- For bash scripts: Edit directly with tool, then execute
- For visual verification: Open in VS Code after editing

**When to use GUI editor:**
- Complex IDE features needed (debugging, refactoring)
- Working with multiple files simultaneously
- Visual feedback required (syntax highlighting, errors)

### Web Browsing
1. Launch browser first
2. Wait for window to appear (take screenshot)
3. Click address bar (important - don't use startup wizard)
4. Type URL or search term
5. Wait for page load
6. Zoom out if needed to see full page: `Ctrl+-`

### PDF Handling
If reading entire PDF:
1. Determine PDF URL from browser
2. Download with curl: `curl -o /tmp/document.pdf URL`
3. Install pdftotext if needed: `apt-get install -y poppler-utils`
4. Convert: `pdftotext /tmp/document.pdf /tmp/document.txt`
5. Read text file with str_replace_editor tool

## Error Recovery

### Common Errors and Solutions

**Application won't launch:**
- Check DISPLAY variable is set correctly
- Verify application is installed: `which application-name`
- Check for error in stderr
- Try killing existing process: `pkill application-name`

**Click/type not working:**
- Verify window has focus (take screenshot)
- Check coordinates are within screen bounds (0-1023, 0-767 for 1024x768)
- Wait longer for application to be ready

**Command timeout:**
- For long-running commands, redirect output to file
- Monitor with tail: `tail -f /tmp/output.log`
- Run in background if appropriate

**Permission denied:**
- Check file permissions: `ls -la`
- Some operations may need different approach (not sudo in container)

## Performance Tips

1. **Chain computer tool actions** when possible to reduce round-trips
2. **Use bash tool** for read-only checks instead of screenshots
3. **Redirect large output** to files instead of returning via tool
4. **Reuse applications** - don't relaunch if already open

## Session Management

This environment supports session persistence:
- Your work is automatically saved
- Sessions can be resumed
- Use CLAUDE.md (this file) to track discoveries
- Convention updates are preserved across sessions

## Agent SDK Features Available

- **Subagents**: Can delegate specialized tasks
- **Verification loops**: Automatic verification of important actions
- **Context management**: Long conversations automatically optimized
- **Error recovery**: Failed actions can be retried automatically

---

*This file is automatically updated as new patterns and conventions are discovered.*
