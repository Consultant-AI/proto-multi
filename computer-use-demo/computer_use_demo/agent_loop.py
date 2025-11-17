"""
Agent SDK Loop - Drop-in replacement for loop.py using Agent SDK orchestration.

This provides the same interface as loop.py but with production-grade Agent SDK features:
- Feedback loops (gather → act → verify)
- Session persistence and resumption
- Subagent coordination
- Automatic verification
- Error recovery
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
from anthropic.types.beta import (
    BetaContentBlockParam,
    BetaMessageParam,
)

from .agent_sdk import AgentOrchestrator
from .tools import ToolResult, ToolVersion


async def sampling_loop(
    *,
    model: str,
    provider: Any,  # APIProvider or str
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
    # Agent SDK specific parameters
    session_id: str | None = None,
    enable_subagents: bool = True,
    enable_verification: bool = True,
    claude_home: Path | None = None,
) -> list[BetaMessageParam]:
    """
    Agent SDK enhanced sampling loop with production features.

    This function is a drop-in replacement for the original sampling_loop
    but provides additional capabilities:

    - Session persistence: Conversations saved and resumable
    - Feedback loops: Automatic verification after important actions
    - Context management: Automatic compaction to prevent exhaustion
    - Subagent support: Parallel execution for complex workflows
    - Error recovery: Automatic retry on failures

    All original parameters are preserved for compatibility.

    New parameters:
        session_id: Unique session ID for persistence (auto-generated if None)
        enable_subagents: Enable parallel subagent execution
        enable_verification: Enable automatic verification loops
        claude_home: Path to .claude directory (defaults to ~/.claude)

    Returns:
        List of conversation messages (same as original)
    """
    # Initialize Agent SDK orchestrator
    orchestrator = AgentOrchestrator(
        session_id=session_id,
        claude_home=claude_home,
        enable_subagents=enable_subagents,
        enable_verification=enable_verification,
    )

    # Convert provider to string if it's an enum
    provider_str = str(provider.value) if hasattr(provider, 'value') else str(provider)

    # Run orchestration loop
    result_messages = await orchestrator.orchestrate(
        model=model,
        provider=provider_str,
        system_prompt_suffix=system_prompt_suffix,
        messages=messages,
        output_callback=output_callback,
        tool_output_callback=tool_output_callback,
        api_response_callback=api_response_callback,
        api_key=api_key,
        only_n_most_recent_images=only_n_most_recent_images,
        max_tokens=max_tokens,
        tool_version=tool_version,
        thinking_budget=thinking_budget,
        token_efficient_tools_beta=token_efficient_tools_beta,
    )

    # Print session statistics
    session_stats = orchestrator.session_manager.get_session_stats()
    print(f"\n=== Session Statistics ===")
    print(f"Session ID: {session_stats['session_id']}")
    print(f"Messages: {session_stats['message_count']}")
    print(f"Tool executions: {session_stats['tool_executions']}")

    if orchestrator.enable_verification:
        context_stats = orchestrator.context_manager.get_context_stats(result_messages)
        print(f"Screenshots: {context_stats['screenshots']}")
        print(f"Context compactions: {context_stats['compactions_performed']}")

    return result_messages


# Export both the new agent loop and maintain compatibility
__all__ = ["sampling_loop"]
