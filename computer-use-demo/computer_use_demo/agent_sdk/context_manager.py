"""
Context Manager - Automatic context compaction and management.

Implements Agent SDK's context management to prevent context window exhaustion
while preserving important information.
"""

from typing import cast

from anthropic.types.beta import BetaMessageParam, BetaToolResultBlockParam


class ContextManager:
    """
    Manages conversation context to prevent exhaustion.

    Features:
    - Automatic image truncation with caching optimization
    - Important message preservation
    - Screenshot deduplication
    - Context statistics tracking
    """

    def __init__(self, max_images: int = 10, min_removal_threshold: int = 5):
        """
        Initialize context manager.

        Args:
            max_images: Maximum number of images to keep
            min_removal_threshold: Minimum images to remove at once (for cache optimization)
        """
        self.max_images = max_images
        self.min_removal_threshold = min_removal_threshold
        self.compaction_count = 0

    async def maybe_compact_context(
        self,
        messages: list[BetaMessageParam],
        only_n_most_recent_images: int | None = None,
    ) -> list[BetaMessageParam]:
        """
        Compact context if needed.

        Args:
            messages: Conversation messages
            only_n_most_recent_images: Override for image limit (0 = no truncation)

        Returns:
            Compacted messages
        """
        if only_n_most_recent_images is None:
            only_n_most_recent_images = self.max_images

        if only_n_most_recent_images == 0:
            return messages

        # Filter images
        self._filter_to_n_most_recent_images(
            messages,
            only_n_most_recent_images,
            self.min_removal_threshold,
        )

        self.compaction_count += 1
        return messages

    def _filter_to_n_most_recent_images(
        self,
        messages: list[BetaMessageParam],
        images_to_keep: int,
        min_removal_threshold: int,
    ):
        """
        Remove old screenshots, keeping only the most recent ones.

        This preserves prompt cache by removing in chunks.

        Args:
            messages: Messages to filter (modified in place)
            images_to_keep: Number of images to retain
            min_removal_threshold: Minimum to remove at once
        """
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
        # Remove in chunks for better cache behavior
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

    def get_context_stats(self, messages: list[BetaMessageParam]) -> dict:
        """
        Get statistics about current context usage.

        Args:
            messages: Messages to analyze

        Returns:
            Dictionary with context statistics
        """
        total_messages = len(messages)
        user_messages = sum(1 for m in messages if m["role"] == "user")
        assistant_messages = sum(1 for m in messages if m["role"] == "assistant")

        # Count tool uses and results
        tool_uses = 0
        tool_results = 0
        screenshots = 0

        for message in messages:
            if isinstance(message["content"], list):
                for item in message["content"]:
                    if isinstance(item, dict):
                        if item.get("type") == "tool_use":
                            tool_uses += 1
                        elif item.get("type") == "tool_result":
                            tool_results += 1
                            # Count images in tool results
                            for content in item.get("content", []):
                                if isinstance(content, dict) and content.get("type") == "image":
                                    screenshots += 1

        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "tool_uses": tool_uses,
            "tool_results": tool_results,
            "screenshots": screenshots,
            "compactions_performed": self.compaction_count,
        }

    def mark_important(self, message_index: int):
        """
        Mark a message as important (should not be compacted).

        Note: This is a placeholder for future enhancement where we could
        tag certain messages to preserve during aggressive compaction.

        Args:
            message_index: Index of message to preserve
        """
        # TODO: Implement message importance tagging
        pass

    def estimate_token_usage(self, messages: list[BetaMessageParam]) -> int:
        """
        Rough estimate of token usage.

        Args:
            messages: Messages to estimate

        Returns:
            Estimated token count
        """
        # Rough estimation: 4 characters per token
        total_chars = 0

        for message in messages:
            if isinstance(message["content"], str):
                total_chars += len(message["content"])
            elif isinstance(message["content"], list):
                for item in message["content"]:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            total_chars += len(item.get("text", ""))
                        elif item.get("type") == "image":
                            # Images use ~1500 tokens each
                            total_chars += 6000

        return total_chars // 4
