"""
Agentic sampling loop that calls the Claude API and local implementation of anthropic-defined computer use tools.
"""

import platform
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

import httpx
from anthropic import (
    Anthropic,
    AnthropicBedrock,
    AnthropicVertex,
    APIError,
    APIResponseValidationError,
    APIStatusError,
)
from anthropic.types.beta import (
    BetaCacheControlEphemeralParam,
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
    BetaToolUseBlockParam,
)

from .tools import (
    TOOL_GROUPS_BY_VERSION,
    ToolCollection,
    ToolResult,
    ToolVersion,
)

# Import reliability module
try:
    from .reliability import (
        get_circuit_breaker,
        CircuitOpenError,
        RETRY_API_CONFIG,
        retry_sync,
    )
    RELIABILITY_AVAILABLE = True
except ImportError:
    RELIABILITY_AVAILABLE = False
    get_circuit_breaker = None
    CircuitOpenError = Exception
    RETRY_API_CONFIG = None
    retry_sync = None

# Import memory module (CLAUDE.md hierarchy)
try:
    from .memory import get_memory_injection
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    get_memory_injection = None

# Import skills module (auto-activated knowledge)
try:
    from .skills import get_skill_injection
    SKILLS_AVAILABLE = True
except ImportError:
    SKILLS_AVAILABLE = False
    get_skill_injection = None

# Import thinking module (auto-detect thinking budget)
try:
    from .thinking import auto_detect_budget
    THINKING_AVAILABLE = True
except ImportError:
    THINKING_AVAILABLE = False
    auto_detect_budget = None

# Import smart selector module (intelligent model + thinking selection)
try:
    from .smart_selector import SmartSelector
    SMART_SELECTOR_AVAILABLE = True
except ImportError:
    SMART_SELECTOR_AVAILABLE = False
    SmartSelector = None

PROMPT_CACHING_BETA_FLAG = "prompt-caching-2024-07-31"


class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


# This system prompt is optimized for the current environment and
# specific tool combinations enabled.
# We encourage modifying this system prompt to ensure the model has context for the
# environment it is running in, and to provide any additional information that may be
# helpful for the task at hand.
import os
import platform

def get_system_prompt():
    is_mac = platform.system() == "Darwin"
    arch = platform.machine()
    home = os.path.expanduser("~")
    
    if is_mac:
        os_info = f"macOS ({platform.mac_ver()[0]})"
        gui_apps = """
  - Google Chrome browser (launch: use computer tool to click icon or open via Terminal)
  - Visual Studio Code (launch: code --no-sandbox or click icon)
  - Terminal/iTerm2
  - Finder for file management
"""
    else:
        os_info = "Ubuntu 24.04 LTS"
        gui_apps = """
  - Google Chrome browser (launch: google-chrome --no-sandbox or click icon)
  - Firefox browser (launch: firefox or click icon)
  - Visual Studio Code IDE (launch: code --no-sandbox or click icon)
  - LibreOffice Suite (Writer, Calc, Impress)
  - File Manager (PCManFM), Text Editor (gedit), Calculator
"""

    return f"""<SYSTEM_CAPABILITY>
* You are controlling a {os_info} system using {arch} architecture.
* The system is running LOCALLY on the user's computer (not in a Docker container).
* GUI applications installed: {gui_apps}
* To launch GUI apps: Use computer tool to click icons OR use bash.
* GUI apps may take time to appear. Always take a screenshot to verify they opened.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_based_edit_tool or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page. Either that, or make sure you scroll down to see everything before deciding something isn't available.
* When using your computer function calls, they take a while to run and send back to you. Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
* Your home directory is {home}.
</SYSTEM_CAPABILITY>

<DEFAULT_PROJECT_FOLDER>
**CRITICAL: All user-facing projects must be created in the default Proto folder:**

- **Default folder path**: ~/Proto (the Proto folder in the user's home directory)
- **When creating new projects or folders**: ALWAYS create them in ~/Proto/{{project-name}}/
- **For user-facing projects** (like "make tetris game", "create todo app", "build calculator"): Create in ~/Proto/{{project-name}}/
- **Never** create projects in random locations like ~/tetris-game, /tmp/tetris, or the current working directory unless explicitly requested
- **Use absolute paths**: When using bash commands like mkdir or cd, always use the full path: ~/Proto/{{project-name}}

**Examples:**
- User: "make tetris game project"
- You: Create it in ~/Proto/tetris-game/ (NOT ~/tetris-game/ or /tmp/tetris)
- Correct command: mkdir -p ~/Proto/tetris-game && cd ~/Proto/tetris-game
- Wrong commands: mkdir -p ~/tetris-game OR mkdir -p /tmp/tetris OR mkdir -p tetris-game

**When to use ~/Proto:**
- ANY time the user asks you to create a new project, game, app, or website
- When building something user-facing that they will want to find later
- Unless the user explicitly specifies a different location

**When NOT to use ~/Proto:**
- Temporary files or test files
- System configuration files
- When user explicitly specifies a different path
</DEFAULT_PROJECT_FOLDER>

<CRITICAL_TOOL_USAGE_PRIORITY>
⚠️ IMPORTANT: You have THREE primary ways to interact - choose the right tool!

**1. COMPUTER TOOL - Use for VISUAL/GUI tasks:**
   ✅ **Browser** (opening Chrome, clicking, typing in forms, navigating)
   ✅ **Screenshots** (verifying what's on screen)
   ✅ **Mouse/Keyboard** on visible applications

**2. BASH TOOL - Use for TERMINAL commands:**
   ✅ Running servers (python3 -m http.server)
   ✅ File system (mkdir, ls, cd)
   ✅ Installing packages (pip install)

**3. EDIT TOOL - Use for FILE CONTENT:**
   ✅ **Creating new files** (MUST provide complete `file_text` with full file content)
   ✅ **Editing code** (use `str_replace` or `insert`)
   ✅ **Reading files** (to understand current project)
   ⚠️ CRITICAL: When using command='create', ALWAYS generate the complete file content first, then pass it in file_text parameter. NEVER call create with empty file_text!

**🚨 CRITICAL RULES:**
- User asks for browser/GUI → Use **computer** tool
- User asks to create/edit code → Use **edit** tool (NEVER try to type in an IDE with computer tool)
- User asks to run commands → Use **bash** tool
</CRITICAL_TOOL_USAGE_PRIORITY>

<IMPORTANT>
* When using browsers, if a startup wizard appears, IGNORE IT. Instead, click on the address bar and enter the URL or search term.
* If viewing a PDF and you need to read the entire document, download it with curl and use pdftotext to convert to text for easier reading.
* Always verify GUI applications opened successfully by taking a screenshot after launching them.
</IMPORTANT>

<CRITICAL_WORKFLOWS>
**NEVER GIVE UP - Always complete the task!**

If a command fails or produces an error:
1. Read the error message
2. Try a different approach immediately
3. Use computer tool as fallback for GUI tasks
4. Keep trying until the task is complete

**Example: Command fails → Try different approach**
```
Attempt 1: bash → google-chrome
Result: "command not found" ❌
Attempt 2: computer → Take screenshot, click Chrome icon ✅
Result: Chrome opens successfully!
```

**CRITICAL RULES:**
- NEVER stop after a single error - try alternative approaches
- If bash command fails for GUI apps, use computer tool to click icons
- If computer tool fails, try bash commands with DISPLAY=:1
- Take screenshot after errors to see current state
- Keep working until user's request is fully completed

**Example: "open chrome and search for weather"**
```
Step 1: bash → google-chrome (might fail - that's OK!)
Step 2: If failed → computer screenshot
Step 3: computer → Click Chrome icon on screen
Step 4: computer → Click address bar
Step 5: computer → Type "weather" and Enter
Step 6: computer → Screenshot to show result
DONE - Task complete!
```

**Example: "open React project in chrome"**
```
Step 1: bash → npm start &
Step 2: bash → sleep 10
Step 3: bash → google-chrome localhost:3000 (might fail)
Step 4: If failed → computer screenshot
Step 5: computer → Click Chrome icon
Step 6: computer → Click address bar
Step 7: computer → Type "localhost:3000" + Enter
Step 8: computer → Screenshot showing app
DONE - Task complete!
```

**REMEMBER:**
- One error = Try different tool (bash fails → use computer)
- Always finish what user asked for
- Screenshot after each step to verify progress
</CRITICAL_WORKFLOWS>"""

SYSTEM_PROMPT = get_system_prompt()



async def sampling_loop(
    *,
    model: str,
    provider: APIProvider,
    system_prompt_suffix: str,
    messages: list[BetaMessageParam],
    output_callback: Callable[[BetaContentBlockParam], None],
    tool_output_callback: Callable[[ToolResult, str, str, dict[str, Any]], None],
    api_response_callback: Callable[
        [httpx.Request, httpx.Response | object | None, Exception | None], None
    ],
    api_key: str,
    only_n_most_recent_images: int | None = None,
    max_tokens: int = 4096,
    tool_version: ToolVersion,
    thinking_budget: int | None = None,
    token_efficient_tools_beta: bool = False,
    stop_flag: Callable[[], bool] | None = None,
    planning_progress_callback: Callable[[str], None] | None = None,
    delegation_status_callback: Callable[[str], None] | None = None,
    target_computer_id: str = "local",
    computer_registry: Any = None,
    ssh_manager: Any = None,
    smart_selection: bool = True,  # Enable smart model + thinking selection
):
    """
    Agentic sampling loop for the assistant/tool interaction of computer use.
    """
    tool_group = TOOL_GROUPS_BY_VERSION[tool_version]

    # Instantiate tools, passing api_key and progress callback to tools that need it
    # For DelegateTaskTool, we need to pass tools after they're all created
    tools = []
    delegate_tool_index = None

    for i, ToolCls in enumerate(tool_group.tools):
        if ToolCls.__name__ == "PlanningTool":
            tools.append(ToolCls(api_key=api_key, progress_callback=planning_progress_callback))
        elif ToolCls.__name__ == "DelegateTaskTool":
            # Placeholder - we'll replace it after all tools are created
            tools.append(None)
            delegate_tool_index = i
        elif ToolCls.__name__ == "UniversalComputerTool":
            # Route to remote computer if target_computer_id is not 'local'
            if target_computer_id != "local" and computer_registry and ssh_manager:
                # Use RemoteComputerTool for remote execution
                from .remote import RemoteComputerTool as RemoteToolImpl

                computer = computer_registry.get(target_computer_id)
                if computer:
                    tools.append(RemoteToolImpl(target_computer_id, ssh_manager, computer))
                else:
                    # Fall back to local if computer not found
                    tools.append(ToolCls())
            else:
                # Use local computer tool
                tools.append(ToolCls())
        else:
            tools.append(ToolCls())

    # Now create DelegateTaskTool with all tools (including itself for recursive delegation)
    if delegate_tool_index is not None:
        from .tools.planning import DelegateTaskTool

        # Create progress callback wrapper for delegation streaming
        async def delegation_progress_callback(response, tool_results):
            """Forward specialist agent progress to UI via tool_output_callback."""
            # Extract tool use blocks from response and report them
            if hasattr(response, 'content'):
                for block in response.content:
                    if hasattr(block, 'type') and block.type == 'tool_use':
                        # Extract tool details
                        tool_name = block.name if hasattr(block, 'name') else 'unknown'
                        tool_input = block.input if hasattr(block, 'input') else {}
                        tool_id = block.id if hasattr(block, 'id') else 'unknown'

                        # Find the corresponding result from tool_results
                        tool_result = None
                        if isinstance(tool_results, list):
                            for result_block in tool_results:
                                if (hasattr(result_block, 'type') and
                                    result_block.type == 'tool_result' and
                                    hasattr(result_block, 'tool_use_id') and
                                    result_block.tool_use_id == tool_id):
                                    # Extract the ToolResult from the block content
                                    if hasattr(result_block, 'content'):
                                        # The content should be the ToolResult output
                                        tool_result = ToolResult(
                                            output=str(result_block.content) if result_block.content else "",
                                            error=None,
                                            base64_image=None
                                        )
                                    break

                        # If we didn't find the result, create a placeholder
                        if tool_result is None:
                            tool_result = ToolResult(output="", error=None, base64_image=None)

                        # Call the tool_output_callback to stream this to the UI
                        tool_output_callback(tool_result, tool_id, tool_name, tool_input)

        tools[delegate_tool_index] = DelegateTaskTool(
            available_tools=tools,
            api_key=api_key,
            delegation_depth=0,  # CEO starts at depth 0 (used for tracking/visualization only, no limits)
            stop_flag=stop_flag,  # Pass stop_flag so delegated specialists can be stopped
            progress_callback=delegation_progress_callback,  # Pass progress callback for streaming
            delegation_status_callback=delegation_status_callback,  # Pass status callback for UI updates
        )

    tool_collection = ToolCollection(*tools)

    # Add CEO agent instructions for proto_coding_v1
    ceo_agent_prompt = ""
    if tool_version == "proto_coding_v1":
        ceo_agent_prompt = """

<CEO_AGENT_ROLE>
You are the CEO Agent for the Proto AI system - the main orchestrator and planner.

Your responsibilities:
1. **Task Analysis**: Understand user requests and assess complexity
2. **Project Management**: Determine if task relates to existing project or needs new one
3. **Planning**: For complex tasks, create comprehensive planning documents
4. **Task & Knowledge Tracking**: Create tasks, store knowledge, maintain context
5. **Delegation**: Identify which specialist agents are needed and delegate work
6. **Coordination**: Manage workflow between multiple agents
7. **Synthesis**: Combine results from specialists into final deliverable
8. **Execution**: For simple tasks, execute directly using available tools

## Default Project Folder

**CRITICAL: All projects must be created in the default Proto folder:**

- **Default folder path**: `~/Proto` (the Proto folder in the user's home directory)
- **When creating new projects or folders**: ALWAYS create them in `~/Proto/{project-name}/`
- **For user-facing projects** (like "make snake game", "create todo app"): Create in `~/Proto/{project-name}/`
- **Never** create projects in random locations like `~/snake-game` or the current working directory unless explicitly requested
- **Use absolute paths**: When using bash commands like `mkdir` or `cd`, always use the full path: `~/Proto/{project-name}` or `/Users/$(whoami)/Proto/{project-name}`

**Example:**
- User: "make snake game project"
- You: Create it in `~/Proto/snake-game/` (NOT `~/snake-game/` or `/tmp/snake-game`)
- Correct command: `mkdir -p ~/Proto/snake-game && cd ~/Proto/snake-game`
- Wrong command: `mkdir -p ~/snake-game` or `mkdir -p snake-game`

## Project Selection Workflow

**IMPORTANT: At the start of each conversation:**

1. **List existing projects** using `manage_projects(operation="list")` to see what exists
2. **Determine project context**:
   - If task relates to existing project: Use `manage_projects(operation="context", project_name="...")` to load context
   - If starting new work: Create new project with unique name in `~/Proto/`
   - If unclear: Ask user which project or create new one in `~/Proto/`

3. **Use project context**:
   - Review pending tasks and in-progress work
   - Check knowledge base for relevant decisions and patterns
   - Build upon existing planning documents
   - Maintain continuity across conversations

## Planning Approach

**Simple tasks** (e.g., "fix this bug", "add a button"):
- Execute directly using tools
- No planning needed
- **DO NOT use TodoWrite** - these are too small to track

**Medium tasks** (e.g., "add user authentication"):
- **Use `create_planning_docs` tool** to create basic planning documents
- Project will be created in `~/Proto/{project-name}/planning/`
- Creates: requirements.md, technical.md, **TASKS.md** (contains all tasks)
- Execute with minimal delegation
- **Track progress in TASKS.md using `manage_tasks` tool** (NOT TodoWrite!)

**Complex tasks** (e.g., "build a dashboard", "create a SaaS product", "make Instagram clone"):
- **STEP 1**: Use `create_planning_docs` tool first (REQUIRED!)
  - Creates planning structure in `~/Proto/{project-name}/planning/`
  - Generates: project_overview.md, requirements.md, technical_spec.md, roadmap.md, **TASKS.md**
  - Planning tool will tell you which specialist to delegate to
- **STEP 2**: Read the planning tool output - it includes "NEXT STEPS" with delegation guidance
- **STEP 3**: **IMMEDIATELY delegate to the recommended specialist** (REQUIRED for complex projects!):
  - **Coding/development work** → `delegate_task(specialist="senior-developer", task="Implement [project-name] per planning documents", project_name="project-name")`
  - **UI/UX design work** → `delegate_task(specialist="ux-designer", task="Design UI per REQUIREMENTS.md", project_name="project-name")`
  - **Testing/QA work** → `delegate_task(specialist="qa-testing", task="Test application per REQUIREMENTS.md", project_name="project-name")`
  - **DevOps/infrastructure** → `delegate_task(specialist="devops", task="Setup infrastructure per TECHNICAL_SPEC.md", project_name="project-name")`
  - **Content writing** → `delegate_task(specialist="content-marketing", task="Create content per REQUIREMENTS.md", project_name="project-name")`
  - **⚠️ CRITICAL**: DO NOT implement complex projects yourself - always delegate to specialists!
  - **⚠️ CRITICAL**: Delegation must happen immediately after planning - don't end turn without delegating!
- **STEP 4**: Specialists will update TASKS.md using `manage_tasks` as they complete work
- **STEP 5**: Coordinate handoffs between specialists

**MANDATORY WORKFLOW FOR COMPLEX PROJECTS**:
```
Planning (create_planning_docs) → THEN delegation (delegate_task) → THEN end_turn
NEVER: Planning → end_turn (this leaves work incomplete!)
```

**Project-level tasks** (e.g., "create a company", "build a platform"):
- **STEP 1**: Use `create_planning_docs` tool (REQUIRED!)
  - Creates full planning suite with all documents and TASKS.md
  - Planning tool will recommend which specialist to delegate to
- **STEP 2**: **IMMEDIATELY delegate to specialist** (REQUIRED!):
  - Development work → `delegate_task(specialist="senior-developer", task="Implement [project] per planning documents", project_name="my-project")`
  - Design work → `delegate_task(specialist="ux-designer", task="Create complete UI design system per REQUIREMENTS.md", project_name="my-project")`
  - Infrastructure → `delegate_task(specialist="devops", task="Setup deployment pipeline", project_name="my-project")`
  - **⚠️ DO NOT implement complex projects yourself** - you are the orchestrator, not the implementer!
- **STEP 3**: Specialists track progress using `manage_tasks` to update TASKS.md
- **STEP 4**: Monitor specialist progress by checking TASKS.md updates

**CEO Delegation Philosophy**:
- **Complex projects (coding, design, QA, DevOps, etc.) → ALWAYS delegate to specialists** - This is MANDATORY!
- **Simple coordination tasks** → You can execute directly (e.g., creating simple text files, basic file operations)
- **Delegation rule**: If a specialist exists for the work type, you MUST delegate to them
- **Why delegate?** Specialists have domain expertise and update TASKS.md for progress tracking
- **Available specialists**: senior-developer, ux-designer, qa-testing, devops, product-manager, content-marketing, technical-writer, data-analyst, security, and more

**When NOT to delegate** (only these cases):
- Simple text file creation (README, basic docs)
- Coordination between specialists
- Reading/reviewing documents
- Updating planning documents

**CRITICAL: Task Management Rules**
- **NEVER use TodoWrite for project-level tasks** - it creates duplicate tracking and poor visibility
- **ALWAYS use TASKS.md** for project task tracking (via `manage_tasks` tool)
- **TodoWrite is DEPRECATED** for CEO and specialist agents - only use for trivial, non-project work
- **TASKS.md is the single source of truth** for all project tasks
- Planning tool creates TASKS.md automatically - specialists update it using `manage_tasks`
- User can see progress by viewing TASKS.md in the file explorer

## Task and Knowledge Management

**Track tasks in TASKS.md** (the single source of truth):
- Use `manage_tasks` to update task status (pending → in_progress → completed)
- All specialists and CEO use the SAME TASKS.md file
- NO duplicate todo lists - everything goes in TASKS.md
- Example: `manage_tasks(operation="update_status", project_name="instagram-clone", task_id="1.1", status="in_progress")`

**Store knowledge** as you learn:
- Use `manage_knowledge` to capture important decisions, patterns, learnings
- Technical decisions: Architecture choices, technology selections
- Best practices: Proven approaches and guidelines
- Lessons learned: What worked and what didn't
- Context: Domain knowledge and business rules

**Example workflow:**
1. Load project context to see TASKS.md and knowledge
2. Delegate work to specialists
3. Specialists update TASKS.md as they complete tasks
4. Store key learnings in knowledge base
5. Verify work with tests or visual checks

Remember: You're the CEO - orchestrate, delegate, and track progress in TASKS.md!
</CEO_AGENT_ROLE>
"""

    # === NEW ARCHITECTURE INTEGRATION ===

    # Extract user's latest message for context-aware injections
    user_message_text = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", [])
            if isinstance(content, str):
                user_message_text = content
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        user_message_text = item.get("text", "")
                        break
            break

    # Inject memory (CLAUDE.md hierarchy)
    memory_injection = ""
    if MEMORY_AVAILABLE and get_memory_injection:
        try:
            memory_injection = get_memory_injection()
            if memory_injection:
                print(f"[Memory] Injected CLAUDE.md content ({len(memory_injection)} chars)")
        except Exception as e:
            print(f"[Memory] Failed to load: {e}")

    # Inject skills based on context
    skills_injection = ""
    if SKILLS_AVAILABLE and get_skill_injection and user_message_text:
        try:
            skills_injection = get_skill_injection(message=user_message_text)
            if skills_injection:
                print(f"[Skills] Injected matching skills ({len(skills_injection)} chars)")
        except Exception as e:
            print(f"[Skills] Failed to load: {e}")

    # Smart model and thinking selection
    effective_thinking_budget = thinking_budget
    effective_model = model  # Default to passed model

    if smart_selection and SMART_SELECTOR_AVAILABLE and SmartSelector and user_message_text:
        try:
            # Use SmartSelector for intelligent model + thinking selection
            selector = SmartSelector(api_key=api_key)
            selection = selector.select_sync(
                task=user_message_text,
                context={"tool_version": tool_version},
            )

            # Use selected model (unless explicit model was requested)
            if not thinking_budget:  # Only override if not explicitly set
                effective_model = selection.model_id
                effective_thinking_budget = selection.thinking_budget

            print(f"[SmartSelector] Model: {selection.model} | Thinking: {selection.thinking_budget}")
            print(f"[SmartSelector] Reason: {selection.reasoning}")
            print(f"[SmartSelector] Task type: {selection.task_type.value} | Mechanical: {selection.is_mechanical}")

        except Exception as e:
            print(f"[SmartSelector] Failed: {e}, falling back to auto-detect")
            # Fallback to old thinking auto-detection
            if THINKING_AVAILABLE and auto_detect_budget and not thinking_budget:
                try:
                    detection_result = auto_detect_budget(user_message_text)
                    if detection_result.budget > 0:
                        effective_thinking_budget = detection_result.budget
                        print(f"[Thinking] Auto-detected budget: {detection_result.budget} ({detection_result.reason})")
                except Exception as e2:
                    print(f"[Thinking] Auto-detection also failed: {e2}")

    elif THINKING_AVAILABLE and auto_detect_budget and user_message_text and not thinking_budget:
        # Fallback: use old auto-detect if SmartSelector not available
        try:
            detection_result = auto_detect_budget(user_message_text)
            if detection_result.budget > 0:
                effective_thinking_budget = detection_result.budget
                print(f"[Thinking] Auto-detected budget: {detection_result.budget} ({detection_result.reason})")
        except Exception as e:
            print(f"[Thinking] Auto-detection failed: {e}")

    # Build the complete system prompt with injections
    prompt_parts = [SYSTEM_PROMPT, ceo_agent_prompt]
    if memory_injection:
        prompt_parts.append(f"\n\n<MEMORY_CONTEXT>\n{memory_injection}\n</MEMORY_CONTEXT>")
    if skills_injection:
        prompt_parts.append(f"\n\n<ACTIVE_SKILLS>\n{skills_injection}\n</ACTIVE_SKILLS>")
    if system_prompt_suffix:
        prompt_parts.append(f" {system_prompt_suffix}")

    system = BetaTextBlockParam(
        type="text",
        text="".join(prompt_parts),
    )

    while True:
        # Check if stop was requested
        if stop_flag and stop_flag():
            print("Stop requested, breaking sampling loop")
            break

        enable_prompt_caching = False
        betas = [tool_group.beta_flag] if tool_group.beta_flag else []
        if token_efficient_tools_beta:
            betas.append("token-efficient-tools-2025-02-19")
        image_truncation_threshold = only_n_most_recent_images or 0
        if provider == APIProvider.ANTHROPIC:
            client = Anthropic(api_key=api_key, max_retries=4)
            enable_prompt_caching = True
        elif provider == APIProvider.VERTEX:
            client = AnthropicVertex()
        elif provider == APIProvider.BEDROCK:
            client = AnthropicBedrock()

        if enable_prompt_caching:
            betas.append(PROMPT_CACHING_BETA_FLAG)
            _inject_prompt_caching(messages)
            # Because cached reads are 10% of the price, we don't think it's
            # ever sensible to break the cache by truncating images
            only_n_most_recent_images = 0
            # Use type ignore to bypass TypedDict check until SDK types are updated
            system["cache_control"] = {"type": "ephemeral"}  # type: ignore

        if only_n_most_recent_images:
            _maybe_filter_to_n_most_recent_images(
                messages,
                only_n_most_recent_images,
                min_removal_threshold=image_truncation_threshold,
            )
        extra_body = {}
        # Dynamically adjust max_tokens for thinking
        effective_max_tokens = max_tokens
        if effective_thinking_budget:
            # max_tokens MUST be greater than thinking.budget_tokens
            # Add a buffer for the actual response (at least 1000 tokens for response)
            min_required_max_tokens = effective_thinking_budget + 1000
            if effective_max_tokens < min_required_max_tokens:
                effective_max_tokens = min_required_max_tokens
                print(f"[Thinking] Adjusted max_tokens to {effective_max_tokens} (thinking budget: {effective_thinking_budget})")
            extra_body = {
                "thinking": {"type": "enabled", "budget_tokens": effective_thinking_budget}
            }

        # Call the API with reliability patterns (circuit breaker + retry)
        # we use raw_response to provide debug information to streamlit. Your
        # implementation may be able call the SDK directly with:
        # `response = client.messages.create(...)` instead.
        try:
            if RELIABILITY_AVAILABLE:
                # Get circuit breaker for main sampling loop
                circuit_breaker = get_circuit_breaker("anthropic_api_sampling_loop")

                # Check if circuit is available
                if not circuit_breaker.is_available():
                    circuit_breaker.record_rejection()
                    raise CircuitOpenError("Sampling loop circuit breaker is open")

                try:
                    # Define the API call function for retry
                    def make_api_call():
                        return client.beta.messages.with_raw_response.create(
                            max_tokens=effective_max_tokens,
                            messages=messages,
                            model=effective_model,  # Use SmartSelector's model choice
                            system=[system],
                            tools=tool_collection.to_params(),
                            betas=betas,
                            extra_body=extra_body,
                        )

                    # Execute with retry
                    raw_response, retry_stats = retry_sync(
                        make_api_call,
                        config=RETRY_API_CONFIG,
                    )

                    # Record success
                    circuit_breaker.record_success()

                except Exception as e:
                    circuit_breaker.record_failure(e)
                    raise
            else:
                # Fallback: direct API call without reliability
                raw_response = client.beta.messages.with_raw_response.create(
                    max_tokens=effective_max_tokens,
                    messages=messages,
                    model=effective_model,  # Use SmartSelector's model choice
                    system=[system],
                    tools=tool_collection.to_params(),
                    betas=betas,
                    extra_body=extra_body,
                )
        except CircuitOpenError as e:
            # Circuit breaker is open - return error but don't retry
            api_response_callback(None, None, e)
            return messages
        except (APIStatusError, APIResponseValidationError) as e:
            api_response_callback(e.request, e.response, e)
            return messages
        except APIError as e:
            api_response_callback(e.request, e.body, e)
            return messages

        api_response_callback(
            raw_response.http_response.request, raw_response.http_response, None
        )

        response = raw_response.parse()

        response_params = _response_to_params(response)
        messages.append(
            {
                "role": "assistant",
                "content": response_params,
            }
        )

        tool_result_content: list[BetaToolResultBlockParam] = []
        for content_block in response_params:
            output_callback(content_block)
            if isinstance(content_block, dict) and content_block.get("type") == "tool_use":
                # Type narrowing for tool use blocks
                tool_use_block = cast(BetaToolUseBlockParam, content_block)
                result = await tool_collection.run(
                    name=tool_use_block["name"],
                    tool_input=cast(dict[str, Any], tool_use_block.get("input", {})),
                )
                tool_result_content.append(
                    _make_api_tool_result(result, tool_use_block["id"])
                )
                tool_output_callback(
                    result,
                    tool_use_block["id"],
                    tool_use_block["name"],
                    cast(dict[str, Any], tool_use_block.get("input", {}))
                )

        if not tool_result_content:
            return messages

        messages.append({"content": tool_result_content, "role": "user"})


def _maybe_filter_to_n_most_recent_images(
    messages: list[BetaMessageParam],
    images_to_keep: int,
    min_removal_threshold: int,
):
    """
    With the assumption that images are screenshots that are of diminishing value as
    the conversation progresses, remove all but the final `images_to_keep` tool_result
    images in place, with a chunk of min_removal_threshold to reduce the amount we
    break the implicit prompt cache.
    """
    if images_to_keep is None:
        return messages

    tool_result_blocks = cast(
        list[BetaToolResultBlockParam],
        [
            item
            for message in messages
            for item in (
                message["content"] if isinstance(message["content"], list) else []
            )
            if isinstance(item, dict) and item.get("type") == "tool_result"
        ],
    )

    total_images = sum(
        1
        for tool_result in tool_result_blocks
        for content in tool_result.get("content", [])
        if isinstance(content, dict) and content.get("type") == "image"
    )

    images_to_remove = total_images - images_to_keep
    # for better cache behavior, we want to remove in chunks
    images_to_remove -= images_to_remove % min_removal_threshold

    for tool_result in tool_result_blocks:
        if isinstance(tool_result.get("content"), list):
            new_content = []
            for content in tool_result.get("content", []):
                if isinstance(content, dict) and content.get("type") == "image":
                    if images_to_remove > 0:
                        images_to_remove -= 1
                        continue
                new_content.append(content)
            tool_result["content"] = new_content


def _response_to_params(
    response: BetaMessage,
) -> list[BetaContentBlockParam]:
    res: list[BetaContentBlockParam] = []
    for block in response.content:
        if isinstance(block, BetaTextBlock):
            if block.text:
                res.append(BetaTextBlockParam(type="text", text=block.text))
            elif getattr(block, "type", None) == "thinking":
                # Handle thinking blocks - include signature field
                thinking_block = {
                    "type": "thinking",
                    "thinking": getattr(block, "thinking", None),
                }
                if hasattr(block, "signature"):
                    thinking_block["signature"] = getattr(block, "signature", None)
                res.append(cast(BetaContentBlockParam, thinking_block))
        else:
            # Handle tool use blocks normally
            res.append(cast(BetaToolUseBlockParam, block.model_dump()))
    return res


def _inject_prompt_caching(
    messages: list[BetaMessageParam],
):
    """
    Set cache breakpoints for the 2 most recent turns
    one cache breakpoint is left for tools/system prompt, to be shared across sessions
    (Total of 3 cache blocks max to stay under API limit of 4)
    """

    breakpoints_remaining = 2
    for message in reversed(messages):
        if message["role"] == "user" and isinstance(
            content := message["content"], list
        ):
            if breakpoints_remaining:
                breakpoints_remaining -= 1
                # Use type ignore to bypass TypedDict check until SDK types are updated
                content[-1]["cache_control"] = BetaCacheControlEphemeralParam(  # type: ignore
                    {"type": "ephemeral"}
                )
            else:
                if isinstance(content[-1], dict) and "cache_control" in content[-1]:
                    del content[-1]["cache_control"]  # type: ignore
                # we'll only every have one extra turn per loop
                break


def _make_api_tool_result(
    result: ToolResult, tool_use_id: str
) -> BetaToolResultBlockParam:
    """Convert an agent ToolResult to an API ToolResultBlockParam."""
    tool_result_content: list[BetaTextBlockParam | BetaImageBlockParam] | str = []
    is_error = False
    if result.error:
        is_error = True
        tool_result_content = _maybe_prepend_system_tool_result(result, result.error)
    else:
        if result.output:
            tool_result_content.append(
                {
                    "type": "text",
                    "text": _maybe_prepend_system_tool_result(result, result.output),
                }
            )
        if result.base64_image:
            tool_result_content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": result.base64_image,
                    },
                }
            )
    return {
        "type": "tool_result",
        "content": tool_result_content,
        "tool_use_id": tool_use_id,
        "is_error": is_error,
    }


def _maybe_prepend_system_tool_result(result: ToolResult, result_text: str):
    if result.system:
        result_text = f"<system>{result.system}</system>\n{result_text}"
    return result_text
