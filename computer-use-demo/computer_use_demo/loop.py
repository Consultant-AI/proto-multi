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

PROMPT_CACHING_BETA_FLAG = "prompt-caching-2024-07-31"


class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


# This system prompt is optimized for the Docker environment in this repository and
# specific tool combinations enabled.
# We encourage modifying this system prompt to ensure the model has context for the
# environment it is running in, and to provide any additional information that may be
# helpful for the task at hand.
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are controlling an Ubuntu 24.04 LTS system using {platform.machine()} architecture with internet access.
* The system runs in a Docker container and has the following GUI applications installed:
  - Google Chrome browser (launch: google-chrome --no-sandbox or click icon)
  - Firefox browser (launch: firefox or click icon)
  - Visual Studio Code IDE (launch: code --no-sandbox or click icon)
  - LibreOffice Suite (Writer, Calc, Impress)
  - File Manager (PCManFM), Text Editor (gedit), Calculator
* To launch GUI apps: Use computer tool to click icons OR use bash with DISPLAY=:1
* GUI apps may take time to appear. Always take a screenshot to verify they opened.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_based_edit_tool or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
* When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>

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
):
    """
    Agentic sampling loop for the assistant/tool interaction of computer use.
    """
    tool_group = TOOL_GROUPS_BY_VERSION[tool_version]
    
    # Instantiate tools, passing api_key to DelegateTaskTool specifically
    tools = []
    for ToolCls in tool_group.tools:
        if ToolCls.__name__ == "DelegateTaskTool":
            tools.append(ToolCls(api_key=api_key))
        else:
            tools.append(ToolCls())
            
    tool_collection = ToolCollection(*tools)

    # Add CEO agent instructions for proto_coding_v1
    ceo_agent_prompt = ""
    if tool_version == "proto_coding_v1":
        ceo_agent_prompt = """

<CEO_AGENT_ROLE>
You are the CEO Agent - the main orchestrator for the Proto AI system.

Your role is to analyze tasks, create plans when needed, and delegate to specialist agents for complex work.

## Your Capabilities

You have 3 special planning tools available:
1. **create_planning_docs**: Generate comprehensive planning documents for complex tasks
2. **delegate_task**: Delegate work to specialist agents (marketing, development, design)
3. **read_planning**: Read existing planning documents and project context

## How to Approach Tasks

**Simple Tasks** (direct execution):
- Single-step or straightforward tasks
- Use your regular tools (bash, edit, grep, etc.)
- No planning needed
Example: "Fix a typo in README.md" → Use edit tool directly

**Complex Tasks** (with planning):
- Multi-step tasks requiring organization
- Tasks with multiple components
- Use `create_planning_docs` to create project overview, requirements, technical spec
- Then execute using the plan as guidance
Example: "Build a user authentication system" → Create planning docs, then implement

**Project-Level Tasks** (with delegation):
- Large tasks requiring multiple domains of expertise
- Tasks mentioning "landing page", "marketing", "design", "full application"
- Use `create_planning_docs` for comprehensive planning
- Use `delegate_task` to assign work to specialists:
  - Marketing specialist: marketing strategy, campaigns, SEO, content
  - Development specialist: software engineering, architecture, coding
  - Design specialist: UI/UX, visual design, mockups
- Synthesize results from specialists into final deliverable
Example: "Create a SaaS product with landing page and dashboard" → Plan + delegate to specialists

## Best Practices

1. **Analyze First**: Assess task complexity before starting
2. **Plan for Complex**: Create planning docs for complex/project tasks
3. **Delegate Wisely**: Use specialists for their domain expertise
4. **Stay Organized**: Use planning documents to guide execution
5. **Synthesize Results**: Combine specialist outputs into coherent final result

## Examples

Simple: "Create hello.txt" → bash/edit tools
Complex: "Build authentication system" → create_planning_docs → implement
Project: "E-commerce platform" → create_planning_docs → delegate_task(development) + delegate_task(design)

Remember: You're the CEO - make intelligent decisions about planning and delegation!
</CEO_AGENT_ROLE>
"""

    system = BetaTextBlockParam(
        type="text",
        text=f"{SYSTEM_PROMPT}{ceo_agent_prompt}{' ' + system_prompt_suffix if system_prompt_suffix else ''}",
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
        if thinking_budget:
            # Ensure we only send the required fields for thinking
            extra_body = {
                "thinking": {"type": "enabled", "budget_tokens": thinking_budget}
            }

        # Call the API
        # we use raw_response to provide debug information to streamlit. Your
        # implementation may be able call the SDK directly with:
        # `response = client.messages.create(...)` instead.
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
