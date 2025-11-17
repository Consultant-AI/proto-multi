# Phase 2 Enforcement - Computer Tool Must Be Used!

## The Problem

You reported: "it didn't call print screens, mouse and keyboard use"

Looking at the logs:
```
✅ bash: 3 calls
✅ str_replace_editor: 6 calls
❌ computer: 0 calls  ← MISSING!
```

The agent completed **Phase 1** (file creation) but **skipped Phase 2** (browser testing).

## Why This Happened

The agent interpreted the task as "create files" and stopped there. It didn't understand that "test it on chrome" means:
1. Open Chrome (computer tool)
2. Navigate to localhost:8000 (computer tool)
3. Click and interact with the game (computer tool)
4. Take screenshots (computer tool)

## The Fix

Added **MANDATORY Phase 2 enforcement** to both system prompt and CLAUDE.md.

### 1. System Prompt ([orchestrator.py](computer_use_demo/agent_sdk/orchestrator.py:118-135))

**Added explicit warnings:**
```
**Phase 2 - Visual Testing (REQUIRED - DO NOT SKIP THIS!):**
4. Use computer tool with action="left_click" to open Chrome/Firefox
5. Use computer tool with action="type" to enter URL (localhost:8000)
6. Use computer tool with action="left_click" to interact with the application
7. Use computer tool with action="screenshot" to capture the result

⚠️ WARNING: If you complete Phase 1 but skip Phase 2, you have FAILED the task!
⚠️ The user EXPECTS to see computer tool usage for browser interaction!
⚠️ Creating files without testing them is INCOMPLETE work!
```

### 2. CLAUDE.md ([.claude/CLAUDE.md](computer_use_demo/.claude/CLAUDE.md:59-70))

**Added mandatory rules:**
```
**CRITICAL RULES - MANDATORY:**
- ⚠️ When asked to "test", "run", or "show" - YOU MUST DO BOTH PHASES!
- ⚠️ Phase 2 is NOT OPTIONAL - browser testing is REQUIRED
- ⚠️ If you create files but don't open browser = INCOMPLETE TASK = FAILURE

**How to know if you're doing it right:**
- ✅ Tool log shows: bash, str_replace_editor, AND computer
- ❌ If tool log only shows bash/edit but NO computer = YOU FORGOT PHASE 2!
```

## Expected Behavior Now

For "write tictactoe code in html css js and run it on chrome and test it":

### Phase 1 - File Creation ✅
```
bash: mkdir -p tic-tac-toe
str_replace_editor: create index.html
str_replace_editor: create style.css
str_replace_editor: create game.js
bash: python3 -m http.server 8000 &
```

### Phase 2 - Browser Testing ✅ (This was missing before!)
```
computer: action="left_click" → Click Chrome icon
computer: action="type" → Type "localhost:8000"
computer: action="key" → Press Enter
computer: action="screenshot" → Capture the game
computer: action="left_click" → Click a cell in the game
computer: action="screenshot" → Show the game being played
```

### Tool Log Should Show:
```
=== Tool Usage Summary ===
bash: 2 calls
str_replace_editor: 3 calls
computer: 6 calls  ← THIS WAS 0 BEFORE!
Total tool calls: 11
=========================
```

## Keywords That Trigger Phase 2

These words in the user's request mean Phase 2 is **MANDATORY**:
- "test it"
- "run it"
- "open in chrome"
- "show it in browser"
- "play it"
- "demonstrate it"
- "verify it works"

**All of these require computer tool usage for visual testing!**

## How to Verify It Works

After restarting the webui and running a task, check the logs:

```bash
cd ~/.claude/projects/
latest=$(ls -t | head -n 1)
cat "$latest/tool_log.jsonl" | jq -r '.tool' | sort | uniq -c
```

**Success looks like:**
```
  2 bash
  3 str_replace_based_edit_tool
  5 computer  ← MUST be present!
```

**Failure looks like:**
```
  2 bash
  3 str_replace_based_edit_tool
  (no computer entry)  ← Phase 2 was skipped!
```

## Files Modified

1. **`computer_use_demo/agent_sdk/orchestrator.py`**
   - Lines 118-135: Added mandatory Phase 2 warnings
   - Explicit statement: "If you complete Phase 1 but skip Phase 2, you have FAILED the task!"

2. **`.claude/CLAUDE.md`**
   - Lines 59-70: Added CRITICAL RULES section
   - Self-check criteria: "If tool log only shows bash/edit but NO computer = YOU FORGOT PHASE 2!"

## Why This Is Important

**Without Phase 2:**
- Files created ✅
- But user has to manually open browser ❌
- User has to manually navigate to URL ❌
- User has to manually test ❌
- **NOT autonomous!**

**With Phase 2:**
- Files created ✅
- Browser automatically opened ✅
- URL automatically entered ✅
- Application automatically tested ✅
- Screenshots showing it works ✅
- **FULLY autonomous!** 🎉

## Test Instructions

1. **Restart the webui:**
   ```bash
   python3 -m computer_use_demo.webui
   ```

2. **Give a task that requires both phases:**
   ```
   write tictactoe code in html css js and run it on chrome and test it
   ```

3. **Watch the console** - you should see:
   ```
   ✅ bash called (count: 1)
   ✅ str_replace_editor called (count: 1)
   ✅ str_replace_editor called (count: 2)
   ✅ str_replace_editor called (count: 3)
   ✅ bash called (count: 2)
   ⚠️ Computer tool used: left_click (count: 1)  ← Opening Chrome
   ⚠️ Computer tool used: type (count: 2)        ← Typing URL
   ⚠️ Computer tool used: screenshot (count: 3)  ← Capturing result
   ```

4. **Check the logs:**
   ```bash
   cat ~/.claude/projects/webui-*/tool_log.jsonl | jq -r '.tool' | sort | uniq -c
   ```

   Should show **computer** in the list!

---

## Status: ✅ Phase 2 Now Mandatory

The agent will now **automatically proceed to browser testing** after creating files!

The warnings and mandatory rules make it clear that skipping Phase 2 = incomplete work.

**Restart and test to see both phases in action!** 🚀
