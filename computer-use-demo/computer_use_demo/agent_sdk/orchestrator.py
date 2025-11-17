"""
Agent SDK Orchestrator - Production-grade feedback loop implementation.

This replaces the simple sampling loop with a sophisticated orchestration layer
that implements the Agent SDK's gather → act → verify → repeat pattern.
"""

import asyncio
import platform
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Any, cast
from pathlib import Path

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

from ..tools import ToolCollection, ToolResult, ToolVersion, TOOL_GROUPS_BY_VERSION
from .session import SessionManager
from .context_manager import ContextManager
from .subagents import SubagentCoordinator, SubagentType
from .tool_logger import ToolLogger


class FeedbackPhase(Enum):
    """Phases of the Agent SDK feedback loop"""
    GATHER_CONTEXT = "gather_context"
    TAKE_ACTION = "take_action"
    VERIFY_WORK = "verify_work"
    COMPLETE = "complete"


class APIProvider(Enum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


PROMPT_CACHING_BETA_FLAG = "prompt-caching-2024-07-31"


# Enhanced system prompt with Agent SDK capabilities
SYSTEM_PROMPT_BASE = f"""<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu 24.04 LTS virtual machine using {platform.machine()} architecture with internet access.
* You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
* The system has a modern desktop environment with the following pre-installed applications:
  - Google Chrome (browser) - Launch with: google-chrome --no-sandbox
  - Firefox (browser) - Click the Firefox icon or use: firefox
  - Visual Studio Code (IDE) - Click the VS Code icon or use: code --no-sandbox
  - LibreOffice (office suite) - Click the LibreOffice icon or use: libreoffice
  - File Manager (PCManFM), Text Editor (gedit), and Calculator (galculator)
* Using bash tool you can start GUI applications, but you need to set export DISPLAY=:1 and use a subshell. For example "(DISPLAY=:1 xterm &)". GUI apps run with bash tool will appear within your desktop environment, but they may take some time to appear. Take a screenshot to confirm it did.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_based_edit_tool or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
* When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>

<CRITICAL_TOOL_USAGE_PRIORITY>
⚠️ IMPORTANT: You have THREE types of tools - choose based on what you're interacting with!

**🎯 TOOL SELECTION - SIMPLE RULE:**

**COMPUTER TOOL** = Anything involving the GUI (screen, mouse, keyboard on visible apps)
**BASH TOOL** = Running terminal commands
**EDIT TOOL** = Creating or modifying file contents directly

**1. COMPUTER TOOL - Use for ALL visual/GUI tasks:**
   ✅ **Browser interactions** (opening Chrome/Firefox, clicking buttons, typing in web forms, navigating websites)
   ✅ **Desktop apps** (opening apps, clicking menus, interacting with GUI elements)
   ✅ **Screenshots** (taking screenshots to see what's on screen)
   ✅ **Mouse/keyboard on GUI** (clicking, typing in visible applications)

   **Examples that REQUIRE computer tool:**
   - "Open Chrome" → computer tool
   - "Click the search button" → computer tool
   - "Play chess in browser" → computer tool
   - "Type in the search box" → computer tool (if it's a GUI search box)
   - "Navigate to website" → computer tool
   - "Test the web app" → computer tool
   - "Show me what's on screen" → computer tool (screenshot)

**2. BASH TOOL - Use for terminal commands:**
   ✅ Running server commands (python3 -m http.server)
   ✅ Installing packages (apt install, pip install)
   ✅ File system operations (mkdir, cd, ls)
   ✅ Starting background processes

   **Examples:**
   - "Start a web server" → bash tool
   - "Install a package" → bash tool
   - "Create a directory" → bash tool

**3. EDIT TOOL - Use for file content:**
   ✅ Creating new files
   ✅ Editing existing files
   ✅ Reading file contents

   **Examples:**
   - "Create index.html" → edit tool
   - "Fix the bug in app.js" → edit tool
   - "Add a function to utils.py" → edit tool

**🚨 CRITICAL RULES:**

1. **User asks to interact with browser/GUI → ALWAYS use computer tool**
   - "Open Chrome and go to X" → computer tool (not bash)
   - "Click on Y" → computer tool
   - "Play Z" → computer tool (if it's a game/web app)

2. **User asks about files/code → Use edit tool** (not computer tool)
   - "Create file X" → edit tool (not opening text editor with computer)
   - "Fix bug in Y" → edit tool (not clicking in IDE with computer)

3. **User asks to run commands → Use bash tool** (not computer tool)
   - "Start server" → bash tool (not typing in terminal with computer)

**Example - Creating HTML/CSS/JS project (CORRECT - USE BOTH TOOLS):**
```
Step 1: bash tool → mkdir tic-tac-toe
Step 2: str_replace_editor → create index.html (full HTML in one call)
Step 3: str_replace_editor → create style.css (full CSS in one call)
Step 4: str_replace_editor → create game.js (full JS in one call)
Step 5: bash tool → cd tic-tac-toe && python3 -m http.server 8000 &
Step 6: computer tool → open Chrome to localhost:8000 ← IMPORTANT: Do this!
Step 7: computer tool → click/test the application ← IMPORTANT: Do this!
Step 8: computer tool → screenshot to show result ← IMPORTANT: Do this!
Total: 5 tool calls (direct tools) + 3 computer calls (GUI tasks) = PERFECT!
```

**Common Workflows:**

**Creating a web project and testing it:**
```
1. bash → mkdir project-name
2. edit → create index.html
3. edit → create style.css
4. edit → create script.js
5. bash → python3 -m http.server 8000 &
6. computer → open Chrome to localhost:8000
7. computer → test the application (click buttons, navigate, etc.)
8. computer → screenshot to show result
```

**Running a React/Node.js project (FAST):**
```
1. bash → cd project-dir && [ -d node_modules ] || npm install
   (Only install if node_modules doesn't exist - saves time!)
2. bash → npm start &
   (Run in background with & so you can continue immediately)
3. bash → sleep 10
   (Wait for server to start - don't take screenshots to check!)
4. computer → open Chrome to localhost:3000
5. computer → test the app
6. computer → screenshot to show result

⚠️ CRITICAL for React/Node projects:
- Check if node_modules exists BEFORE running npm install
- Run dev server in BACKGROUND with & symbol
- Use sleep command to wait instead of taking screenshots
- Don't waste time checking if server is ready with screenshots
```

**Making improvements to existing code:**
```
1. edit → view file to understand current code
2. edit → str_replace to fix bugs or add features
3. bash → restart server if needed (kill old process, start new one in background)
4. computer → refresh browser and test changes
5. computer → screenshot to verify improvements
```

**Testing a GUI application:**
```
1. computer → screenshot to see current state
2. computer → open the application (click icon or type URL)
3. computer → interact with the application (click, type, navigate)
4. computer → screenshot to show result
```

**⚠️ CRITICAL REMINDERS:**

1. **Never use computer tool for file editing** - always use edit tool for code changes
2. **Never use computer tool for commands** - always use bash tool for terminal operations
3. **Always use computer tool for browser/GUI** - this includes opening apps, clicking, typing in GUI
4. **Complete the full request** - if user asks to test, you must open browser and test (don't just create files)
5. **Work autonomously** - don't ask questions, make decisions and keep working until done

**🚨 AUTONOMOUS OPERATION - DO NOT ASK PERMISSION:**

When the user gives you a clear instruction, JUST DO IT. Don't ask for permission or confirmation.

**Examples:**
- User: "play chess on chrome" → Take screenshot, click on a chess piece, click where to move it (DON'T ask "would you like to make a move?")
- User: "open website X" → Open Chrome, navigate to X (DON'T ask "should I open it?")
- User: "test the app" → Open browser, test it (DON'T ask "would you like me to test?")
- User: "click the login button" → Click it (DON'T ask "should I click?")

❌ WRONG: Taking a screenshot, explaining what you see, then asking "Would you like me to do X?"
✅ CORRECT: Taking action immediately based on the user's instruction

The user already told you what to do. Just do it without asking again!
</CRITICAL_TOOL_USAGE_PRIORITY>

<AGENT_SDK_CAPABILITIES>
* You are running with Agent SDK orchestration providing advanced capabilities:
  - Session persistence: Your work is automatically saved and can be resumed
  - Verification loops: After important actions, verify results both visually and programmatically
  - Hybrid tool usage: Prefer direct file tools (edit, bash) over GUI when possible for reliability
  - Context awareness: You have access to session history and can reference previous work
* Feedback loop pattern: gather context → take action → verify work → iterate
  - Use computer tool for GUI automation and visual verification
  - Use bash tool for command execution and structural validation
  - Use edit tool for precise file modifications
  - Always verify critical operations with screenshots or checks
</AGENT_SDK_CAPABILITIES>

<IMPORTANT>
* When using Chrome or Firefox, if a startup wizard appears, IGNORE IT.  Do not even click "skip this step".  Instead, click on the address bar and enter the appropriate search term or URL there.
* Chrome runs with --no-sandbox flag for container compatibility.
* VSCode runs with --no-sandbox flag for container compatibility.
* If the item you are looking at is a pdf, if after taking a single screenshot of the pdf it seems that you want to read the entire document instead of trying to continue to read the pdf from your screenshots + navigation, determine the URL, use curl to download the pdf, install and use pdftotext to convert it to a text file, and then read that text file directly with your str_replace_based_edit_tool.
* VERIFICATION: After significant actions (file creation, app launching, command execution), take a screenshot or run a check to verify success.
</IMPORTANT>"""


class AgentOrchestrator:
    """
    Production-grade agent orchestrator implementing Agent SDK's feedback loop model.

    This orchestrator manages:
    - Feedback loops (gather → act → verify)
    - Session persistence and resumption
    - Context management and automatic compaction
    - Subagent coordination
    - Tool execution with verification
    """

    def __init__(
        self,
        session_id: str | None = None,
        claude_home: Path | None = None,
        enable_subagents: bool = True,
        enable_verification: bool = True,
    ):
        """
        Initialize the Agent SDK orchestrator.

        Args:
            session_id: Unique session identifier for persistence
            claude_home: Path to .claude directory (defaults to ~/.claude)
            enable_subagents: Whether to enable subagent coordination
            enable_verification: Whether to enable automatic verification loops
        """
        self.enable_subagents = enable_subagents
        self.enable_verification = enable_verification

        # Initialize core components
        self.session_manager = SessionManager(session_id, claude_home)
        self.context_manager = ContextManager()
        self.subagent_coordinator = SubagentCoordinator() if enable_subagents else None
        self.tool_logger = ToolLogger(session_id or "unknown")

        # Current phase in feedback loop
        self.current_phase = FeedbackPhase.GATHER_CONTEXT

        # Load session conventions (CLAUDE.md equivalent)
        self.conventions = self.session_manager.load_conventions()

    async def orchestrate(
        self,
        *,
        model: str,
        provider: str,
        system_prompt_suffix: str,
        messages: list[BetaMessageParam],
        output_callback: Callable[[BetaContentBlockParam], None],
        tool_output_callback: Callable[[ToolResult, str], None],
        api_response_callback: Callable[
            [httpx.Request, httpx.Response | object | None, Exception | None], None
        ],
        api_key: str,
        only_n_most_recent_images: int | None = None,
        max_tokens: int = 4096,
        tool_version: ToolVersion,
        thinking_budget: int | None = None,
        token_efficient_tools_beta: bool = False,
    ) -> list[BetaMessageParam]:
        """
        Main orchestration loop implementing Agent SDK feedback model.

        This is the drop-in replacement for the simple sampling_loop that adds:
        - Feedback loops with verification
        - Session persistence
        - Context management
        - Subagent coordination
        """
        # Initialize tools
        tool_group = TOOL_GROUPS_BY_VERSION[tool_version]
        tool_collection = ToolCollection(*(ToolCls() for ToolCls in tool_group.tools))

        # Build enhanced system prompt
        system_text = self._build_system_prompt(system_prompt_suffix)
        system = BetaTextBlockParam(type="text", text=system_text)

        # Load session if resuming
        if self.session_manager.session_exists():
            session_messages = self.session_manager.load_session()
            if session_messages:
                messages = session_messages

        # Main orchestration loop
        iteration = 0
        max_iterations = 100  # Safety limit

        while iteration < max_iterations:
            iteration += 1

            # Configure API client
            api_provider = self._get_api_provider(provider)
            enable_prompt_caching = api_provider == APIProvider.ANTHROPIC
            betas = [tool_group.beta_flag] if tool_group.beta_flag else []
            if token_efficient_tools_beta:
                betas.append("token-efficient-tools-2025-02-19")

            if api_provider == APIProvider.ANTHROPIC:
                client = Anthropic(api_key=api_key, max_retries=4)
            elif api_provider == APIProvider.VERTEX:
                client = AnthropicVertex()
            elif api_provider == APIProvider.BEDROCK:
                client = AnthropicBedrock()
            else:
                raise ValueError(f"Unknown provider: {provider}")

            # Context management
            if enable_prompt_caching:
                betas.append(PROMPT_CACHING_BETA_FLAG)
                self._inject_prompt_caching(messages)
                only_n_most_recent_images = 0
                system["cache_control"] = {"type": "ephemeral"}  # type: ignore

            # Compact context if needed
            messages = await self.context_manager.maybe_compact_context(
                messages, only_n_most_recent_images
            )

            # Build extra parameters
            extra_body = {}
            if thinking_budget:
                extra_body = {
                    "thinking": {"type": "enabled", "budget_tokens": thinking_budget}
                }

            # Call Claude API
            try:
                raw_response = client.beta.messages.with_raw_response.create(
                    max_tokens=max_tokens,
                    messages=messages,
                    model=model,
                    system=[system],
                    tools=tool_collection.to_params(),
                    betas=betas,
                    extra_body=extra_body,
                )
            except (APIStatusError, APIResponseValidationError) as e:
                api_response_callback(e.request, e.response, e)
                await self.session_manager.save_session(messages)
                return messages
            except APIError as e:
                api_response_callback(e.request, e.body, e)
                await self.session_manager.save_session(messages)
                return messages

            api_response_callback(
                raw_response.http_response.request, raw_response.http_response, None
            )

            response = raw_response.parse()
            response_params = self._response_to_params(response)

            messages.append({
                "role": "assistant",
                "content": response_params,
            })

            # Execute tools with verification
            tool_result_content: list[BetaToolResultBlockParam] = []
            has_verification_needed = False

            for content_block in response_params:
                output_callback(content_block)

                if isinstance(content_block, dict) and content_block.get("type") == "tool_use":
                    tool_use_block = cast(BetaToolUseBlockParam, content_block)
                    tool_name = tool_use_block["name"]
                    tool_input = cast(dict[str, Any], tool_use_block.get("input", {}))

                    # Log tool call for debugging
                    self.tool_logger.log_tool_call(tool_name, tool_input)

                    # Execute tool
                    result = await tool_collection.run(
                        name=tool_name,
                        tool_input=tool_input,
                    )

                    # Check if verification needed
                    if self.enable_verification and self._needs_verification(tool_name, tool_input):
                        has_verification_needed = True

                    tool_result_content.append(
                        self._make_api_tool_result(result, tool_use_block["id"])
                    )
                    tool_output_callback(result, tool_use_block["id"])

            # Save session after each iteration
            await self.session_manager.save_session(messages)

            # If no tool calls, we're done
            if not tool_result_content:
                await self.session_manager.save_session(messages)
                # Print tool usage summary for debugging
                self.tool_logger.print_summary()
                return messages

            # Add tool results
            messages.append({"content": tool_result_content, "role": "user"})

            # Verification phase: if important actions taken, request verification
            if has_verification_needed and self.current_phase == FeedbackPhase.TAKE_ACTION:
                self.current_phase = FeedbackPhase.VERIFY_WORK
                # Add system message prompting verification
                verification_prompt = self._create_verification_prompt(tool_result_content)
                if verification_prompt:
                    messages.append({
                        "role": "user",
                        "content": [{"type": "text", "text": verification_prompt}]
                    })
            else:
                self.current_phase = FeedbackPhase.TAKE_ACTION

        # Max iterations reached
        await self.session_manager.save_session(messages)

        # Print tool usage summary for debugging
        self.tool_logger.print_summary()

        return messages

    def _build_system_prompt(self, suffix: str) -> str:
        """Build enhanced system prompt with conventions"""
        prompt = SYSTEM_PROMPT_BASE

        # Add conventions from session
        if self.conventions:
            prompt += f"\n\n<SESSION_CONVENTIONS>\n{self.conventions}\n</SESSION_CONVENTIONS>"

        # Add user suffix
        if suffix:
            prompt += f"\n\n{suffix}"

        return prompt

    def _get_api_provider(self, provider: str) -> APIProvider:
        """Convert string provider to enum"""
        provider_map = {
            "anthropic": APIProvider.ANTHROPIC,
            "bedrock": APIProvider.BEDROCK,
            "vertex": APIProvider.VERTEX,
        }
        return provider_map.get(provider.lower(), APIProvider.ANTHROPIC)

    def _needs_verification(self, tool_name: str, tool_input: dict[str, Any]) -> bool:
        """Determine if a tool execution needs verification

        DISABLED: Verification loops add significant latency (extra API calls after each action).
        The agent already receives tool results, so additional verification is unnecessary.
        This was causing slow performance, especially for:
        - Running React/Node projects (npm install, npm start each triggered verification)
        - Playing chess (each click triggered verification)
        - Any multi-step workflow

        By disabling verification, we:
        1. Reduce API calls by ~50%
        2. Cut execution time significantly
        3. Still maintain accuracy (agent sees all tool results anyway)
        """
        # Verification disabled for performance
        return False

    def _create_verification_prompt(self, tool_results: list[BetaToolResultBlockParam]) -> str | None:
        """Create a prompt requesting verification of recent actions"""
        if not tool_results:
            return None

        return (
            "<verification_request>\n"
            "Please verify the results of your recent actions:\n"
            "- If you performed GUI actions, take a screenshot to confirm success\n"
            "- If you executed commands, check output and exit codes\n"
            "- If you edited files, verify the changes are correct\n"
            "Respond with your verification findings.\n"
            "</verification_request>"
        )

    def _response_to_params(self, response: BetaMessage) -> list[BetaContentBlockParam]:
        """Convert API response to parameter format"""
        res: list[BetaContentBlockParam] = []
        for block in response.content:
            if isinstance(block, BetaTextBlock):
                if block.text:
                    res.append(BetaTextBlockParam(type="text", text=block.text))
                elif getattr(block, "type", None) == "thinking":
                    thinking_block = {
                        "type": "thinking",
                        "thinking": getattr(block, "thinking", None),
                    }
                    if hasattr(block, "signature"):
                        thinking_block["signature"] = getattr(block, "signature", None)
                    res.append(cast(BetaContentBlockParam, thinking_block))
            else:
                res.append(cast(BetaToolUseBlockParam, block.model_dump()))
        return res

    def _inject_prompt_caching(self, messages: list[BetaMessageParam]):
        """Set cache breakpoints for recent turns"""
        breakpoints_remaining = 3
        for message in reversed(messages):
            if message["role"] == "user" and isinstance(content := message["content"], list):
                if breakpoints_remaining:
                    breakpoints_remaining -= 1
                    content[-1]["cache_control"] = BetaCacheControlEphemeralParam(  # type: ignore
                        {"type": "ephemeral"}
                    )
                else:
                    if isinstance(content[-1], dict) and "cache_control" in content[-1]:
                        del content[-1]["cache_control"]  # type: ignore
                    break

    def _make_api_tool_result(
        self, result: ToolResult, tool_use_id: str
    ) -> BetaToolResultBlockParam:
        """Convert tool result to API format"""
        tool_result_content: list[BetaTextBlockParam | BetaImageBlockParam] | str = []
        is_error = False

        if result.error:
            is_error = True
            tool_result_content = self._maybe_prepend_system_tool_result(result, result.error)
        else:
            if result.output:
                tool_result_content.append({
                    "type": "text",
                    "text": self._maybe_prepend_system_tool_result(result, result.output),
                })
            if result.base64_image:
                tool_result_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": result.base64_image,
                    },
                })

        return {
            "type": "tool_result",
            "content": tool_result_content,
            "tool_use_id": tool_use_id,
            "is_error": is_error,
        }

    def _maybe_prepend_system_tool_result(self, result: ToolResult, result_text: str) -> str:
        """Prepend system message if present"""
        if result.system:
            result_text = f"<system>{result.system}</system>\n{result_text}"
        return result_text
