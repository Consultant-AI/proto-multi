# Complete Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER / APPLICATION                             │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT SDK ORCHESTRATION LAYER                        │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │              AgentOrchestrator (orchestrator.py)               │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │         Feedback Loop: GATHER → ACT → VERIFY             │  │    │
│  │  │  • Enhanced system prompt with conventions               │  │    │
│  │  │  • Verification after important actions                  │  │    │
│  │  │  • Automatic retry on failures                           │  │    │
│  │  │  • Session persistence every iteration                   │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  └──────────────────┬───────────────────┬──────────────────────────┘    │
│                     │                   │                               │
│    ┌────────────────▼───────────┐  ┌───▼──────────────────────┐        │
│    │ SessionManager             │  │ ContextManager           │        │
│    │ (session.py)               │  │ (context_manager.py)     │        │
│    │ • JSONL transcripts        │  │ • Auto compaction        │        │
│    │ • CLAUDE.md conventions    │  │ • Image truncation       │        │
│    │ • Metadata tracking        │  │ • Token estimation       │        │
│    │ • Tool statistics          │  │ • Cache preservation     │        │
│    └────────────────────────────┘  └──────────────────────────┘        │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   SUBAGENT COORDINATION LAYER                           │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │         SubagentCoordinator (subagents.py)                     │    │
│  │  • Parallel execution (max 3 concurrent)                       │    │
│  │  • Task queue management                                       │    │
│  │  • Isolated context windows                                    │    │
│  │  • Result aggregation                                          │    │
│  └──────┬──────────────┬────────────────┬─────────────────┬───────┘    │
│         │              │                │                 │            │
│    ┌────▼─────┐  ┌────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐     │
│    │Execution │  │Verification│  │File         │  │Research     │     │
│    │Subagent  │  │Subagent    │  │Operations   │  │Subagent     │     │
│    │          │  │            │  │Subagent     │  │             │     │
│    │• GUI     │  │• Screenshot│  │• Edit tool  │  │• Web browse │     │
│    │  control │  │  analysis  │  │• File ops   │  │• Docs       │     │
│    │• Commands│  │• Structural│  │• Code       │  │• Search     │     │
│    │          │  │  checks    │  │  search     │  │             │     │
│    └──────────┘  └────────────┘  └─────────────┘  └─────────────┘     │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      VERIFICATION LAYER                                 │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │           FeedbackLoop (feedback_loop.py)                      │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │   GATHER → ACT → VERIFY (visual + structural) → REPEAT   │  │    │
│  │  └──────────────┬────────────────────┬──────────────────────┘  │    │
│  │                 │                    │                         │    │
│  │    ┌────────────▼──────────┐  ┌──────▼──────────────────┐     │    │
│  │    │ ScreenshotAnalyzer    │  │ StructuralChecker       │     │    │
│  │    │ (screenshot_analyzer) │  │ (structural_checker.py) │     │    │
│  │    │ • Visual verification │  │ • File checks           │     │    │
│  │    │ • Error detection     │  │ • Process validation    │     │    │
│  │    │ • Confidence scoring  │  │ • Command verification  │     │    │
│  │    │ • Screenshot compare  │  │ • Port listening        │     │    │
│  │    └───────────────────────┘  └─────────────────────────┘     │    │
│  └────────────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         TOOL LAYER                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │         ToolCollection (Unified Registry)                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │   │
│  │  │ ComputerTool │  │   BashTool   │  │ Str_Replace_Editor   │  │   │
│  │  │ (computer.py)│  │   (bash.py)  │  │      (edit.py)       │  │   │
│  │  │              │  │              │  │                      │  │   │
│  │  │ • Screenshot │  │ • Commands   │  │ • File create        │  │   │
│  │  │ • Mouse      │  │ • Persistent │  │ • Str replace        │  │   │
│  │  │ • Keyboard   │  │   session    │  │ • View/Insert        │  │   │
│  │  │ • Scaling    │  │ • Output     │  │ • Undo edit          │  │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │   │
│  └─────────┼──────────────────┼─────────────────────┼──────────────┘   │
└────────────┼──────────────────┼─────────────────────┼──────────────────┘
             │                  │                     │
             ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DOCKER CONTAINER ENVIRONMENT                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    Ubuntu 24.04 Desktop                        │    │
│  │                                                                │    │
│  │  ┌──────────────────┐  ┌─────────────────┐  ┌─────────────┐  │    │
│  │  │  X11 Display :1  │  │  Bash Shell     │  │ Filesystem  │  │    │
│  │  │  (1024x768)      │  │  (persistent)   │  │ Operations  │  │    │
│  │  │                  │  │                 │  │             │  │    │
│  │  │  • xdotool       │  │  • Environment  │  │  • /tmp     │  │    │
│  │  │  • scrot         │  │    vars         │  │  • /home    │  │    │
│  │  │  • GUI apps      │  │  • History      │  │  • Working  │  │    │
│  │  │                  │  │                 │  │    dir      │  │    │
│  │  └──────────────────┘  └─────────────────┘  └─────────────┘  │    │
│  │                                                                │    │
│  │  Pre-installed Applications:                                  │    │
│  │  • Chrome  • Firefox  • VS Code  • LibreOffice               │    │
│  │  • File Manager  • Text Editor  • Calculator                 │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘


CONFIGURATION & STATE
━━━━━━━━━━━━━━━━━━━━━
┌────────────────────────────────────────┐
│  .claude/ (Configuration Directory)    │
│  ├── settings.json                     │
│  │   └── All Agent SDK configuration   │
│  ├── CLAUDE.md                         │
│  │   └── Learned conventions & patterns│
│  └── agents/                           │
│      ├── execution_agent.md            │
│      ├── verification_agent.md         │
│      └── file_operations_agent.md      │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  ~/.claude/projects/                   │
│  └── computer-use-{session-id}/        │
│      ├── transcript.jsonl              │
│      ├── CLAUDE.md (session-specific)  │
│      └── metadata.json                 │
└────────────────────────────────────────┘
```

## Data Flow Diagram

```
USER REQUEST
     │
     ▼
┌────────────────────────────────────────────────────┐
│ 1. INITIALIZATION                                  │
│ ────────────────                                   │
│ • Load session (if exists)                         │
│ • Load conventions from CLAUDE.md                  │
│ • Initialize context manager                       │
│ • Setup verification system                        │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ 2. CONTEXT PREPARATION                             │
│ ──────────────────────                             │
│ • Build enhanced system prompt                     │
│ • Add conventions to prompt                        │
│ • Compact context if needed                        │
│ • Setup prompt caching                             │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ 3. CLAUDE API CALL                                 │
│ ──────────────────                                 │
│ • Send messages + tools + system prompt            │
│ • Receive response with thinking & tool uses       │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ 4. TOOL EXECUTION                                  │
│ ─────────────────                                  │
│ For each tool use:                                 │
│   • Execute via ToolCollection.run()               │
│   • Track execution (SessionManager)               │
│   • Collect results                                │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ 5. VERIFICATION (if enabled & needed)              │
│ ────────────────────────────────────               │
│ • Check if action needs verification               │
│   (GUI actions, file edits, commands)              │
│ • If yes:                                          │
│   ├─→ Capture screenshot (visual)                  │
│   ├─→ Run structural checks (commands)             │
│   ├─→ Evaluate success                             │
│   └─→ Retry if failed (up to max_retries)         │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ 6. SESSION PERSISTENCE                             │
│ ──────────────────────                             │
│ • Append to transcript.jsonl                       │
│ • Update metadata.json                             │
│ • Save verification results                        │
│ • Update conventions if learned                    │
└──────────────────────┬─────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────┐
│ 7. FEEDBACK LOOP DECISION                          │
│ ─────────────────────────                          │
│ • Tool results present? → Continue loop (goto 2)   │
│ • No tool uses? → Return to user                   │
│ • Max iterations? → Return to user                 │
└────────────────────────────────────────────────────┘
```

## Verification Flow

```
ACTION EXECUTED
     │
     ▼
┌──────────────────────────────┐
│ NEEDS VERIFICATION?          │
│ • GUI interaction?           │
│ • File operation?            │
│ • Non-readonly command?      │
└──────┬───────────────────────┘
       │
       ▼
  ┌────────┐
  │  YES   │
  └───┬────┘
      │
      ▼
┌──────────────────────────────────────────────┐
│ VISUAL VERIFICATION                          │
│ ──────────────────                           │
│ 1. Capture screenshot                        │
│ 2. Analyze for:                              │
│    • Expected state visible                  │
│    • Error dialogs                           │
│    • Success indicators                      │
│ 3. Score confidence                          │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ STRUCTURAL VERIFICATION                      │
│ ───────────────────────                      │
│ Run checks based on action type:             │
│ • File created → check file exists           │
│ • App launched → check process running       │
│ • Server started → check port listening      │
│ • Command executed → check exit code         │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ AGGREGATE RESULTS                            │
│ ─────────────────                            │
│ Overall Success = Visual ✓ AND Structural ✓  │
└──────────┬───────────────────────────────────┘
           │
      ┌────┴────┐
      │         │
   ✓ YES     ✗ NO
      │         │
      │         ▼
      │    ┌──────────────────┐
      │    │ RETRY?           │
      │    │ • Auto-retry on? │
      │    │ • Under max?     │
      │    └────┬─────────────┘
      │         │
      │         ▼
      │    ┌────────┐
      │    │  YES   │
      │    └────┬───┘
      │         │
      │         ▼
      │    Wait 2s
      │         │
      │         └─→ (RETRY ACTION)
      │
      ▼
┌─────────────┐
│ RETURN      │
│ ActionResult│
└─────────────┘
```

## Session Lifecycle

```
SESSION START
     │
     ▼
┌─────────────────────────────┐
│ Check session_id provided?  │
└──────┬──────────────────────┘
       │
   ┌───┴───┐
   │       │
  YES     NO
   │       │
   │       ▼
   │  Generate new
   │  session_id
   │       │
   └───┬───┘
       ▼
┌─────────────────────────────┐
│ Session directory exists?   │
└──────┬──────────────────────┘
       │
   ┌───┴───┐
   │       │
  YES     NO
   │       │
   │       ▼
   │  Create directory
   │  & metadata.json
   │       │
   ▼       ▼
┌─────────────────────────────┐
│ Load existing session:      │
│ • transcript.jsonl          │
│ • CLAUDE.md                 │
│ • metadata.json             │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ ORCHESTRATION LOOP          │
│ (See Data Flow above)       │
└──────┬──────────────────────┘
       │
       │ After each iteration:
       ▼
┌─────────────────────────────┐
│ SAVE SESSION STATE          │
│ • Append messages to JSONL  │
│ • Update metadata           │
│ • Increment counters        │
└──────┬──────────────────────┘
       │
       │ (Loop continues...)
       │
       ▼
┌─────────────────────────────┐
│ SESSION END                 │
│ • Final save                │
│ • Print statistics          │
│ • Session ready to resume   │
└─────────────────────────────┘
```

## Tool Execution Flow

```
TOOL USE RECEIVED
     │
     ▼
┌─────────────────────────────────┐
│ ToolCollection.run(name, input) │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Find tool in tool_map           │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Execute tool.__call__(**input)  │
│                                 │
│ COMPUTER TOOL:                  │
│ ├─→ screenshot → scrot + base64 │
│ ├─→ mouse_move → xdotool        │
│ ├─→ click → xdotool click       │
│ ├─→ type → xdotool type         │
│ └─→ key → xdotool key           │
│                                 │
│ BASH TOOL:                      │
│ ├─→ Run in persistent shell     │
│ ├─→ Capture stdout/stderr       │
│ └─→ Return with exit code       │
│                                 │
│ EDIT TOOL:                      │
│ ├─→ view → read file            │
│ ├─→ create → write new file     │
│ ├─→ str_replace → edit file     │
│ └─→ undo_edit → restore         │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Return ToolResult               │
│ • output: str                   │
│ • error: str | None             │
│ • base64_image: str | None      │
│ • system: str | None            │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Track execution in session:     │
│ • Increment tool counter        │
│ • Record success/failure        │
│ • Update tool-specific stats    │
└─────────────────────────────────┘
```

## Context Management Flow

```
MESSAGES READY FOR API
     │
     ▼
┌────────────────────────────────────┐
│ ContextManager.maybe_compact()     │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ Count total images in messages    │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ Total > max_images?                │
└──────┬─────────────────────────────┘
       │
   ┌───┴───┐
   │       │
  YES     NO
   │       │
   │       └─→ (No compaction needed)
   │
   ▼
┌────────────────────────────────────┐
│ Calculate images_to_remove         │
│ = total - max_images               │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ Round down to min_removal_threshold│
│ (preserves prompt cache)           │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ Iterate messages oldest→newest:    │
│ • Find tool_result blocks          │
│ • Remove images from oldest first  │
│ • Keep text content                │
│ • Preserve recent images           │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ Return compacted messages          │
│ Increment compaction_count         │
└────────────────────────────────────┘
```

---

**Legend:**
- ┌─┐ = Component/Process
- │ = Data flow
- ▼ = Direction
- ✓ = Success path
- ✗ = Failure path
