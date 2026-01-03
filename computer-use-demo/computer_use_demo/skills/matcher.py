"""
Skill matcher - matches skills to context.
"""

import fnmatch
import re
import threading
from pathlib import Path
from typing import Any

from .loader import load_all_skills
from .types import Skill, SkillContext, SkillMatch


class SkillMatcher:
    """
    Matches skills to context based on triggers.

    Usage:
        matcher = SkillMatcher()

        # Match skills to a message
        matches = matcher.match(
            SkillContext(message="Please review this Python code")
        )

        for match in matches:
            print(f"Matched: {match.skill.name} ({match.match_reason})")
    """

    def __init__(
        self,
        project_root: Path | None = None,
        auto_load: bool = True,
    ):
        self._project_root = project_root
        self._skills: list[Skill] = []
        self._lock = threading.Lock()

        if auto_load:
            self.reload_skills()

    def reload_skills(self) -> None:
        """Reload skills from disk."""
        with self._lock:
            self._skills = load_all_skills(self._project_root)

    @property
    def skills(self) -> list[Skill]:
        """Get loaded skills."""
        return self._skills.copy()

    def add_skill(self, skill: Skill) -> None:
        """Add a skill programmatically."""
        with self._lock:
            self._skills.append(skill)

    def match(
        self,
        context: SkillContext,
        max_matches: int | None = None,
    ) -> list[SkillMatch]:
        """
        Match skills to a context.

        Args:
            context: The context to match against
            max_matches: Maximum number of matches to return

        Returns:
            List of SkillMatch, sorted by priority and confidence
        """
        matches = []

        for skill in self._skills:
            if not skill.enabled:
                continue

            match = self._match_skill(skill, context)
            if match:
                matches.append(match)

        # Sort by priority (higher first), then confidence (higher first)
        matches.sort(key=lambda m: (m.skill.priority, m.confidence), reverse=True)

        if max_matches:
            matches = matches[:max_matches]

        return matches

    def _match_skill(
        self,
        skill: Skill,
        context: SkillContext,
    ) -> SkillMatch | None:
        """
        Check if a skill matches the context.

        Returns SkillMatch if matched, None otherwise.
        """
        triggered_by = []
        total_confidence = 0.0
        match_reasons = []

        # Check keyword triggers
        if skill.triggers.keywords and context.message:
            message_lower = context.message.lower()
            matched_keywords = []

            for keyword in skill.triggers.keywords:
                if keyword.lower() in message_lower:
                    matched_keywords.append(keyword)

            if matched_keywords:
                triggered_by.extend(matched_keywords)
                match_reasons.append(f"keywords: {', '.join(matched_keywords)}")
                total_confidence += 0.5 * (len(matched_keywords) / len(skill.triggers.keywords))

        # Check file pattern triggers
        if skill.triggers.file_patterns and context.file_path:
            matched_patterns = []

            for pattern in skill.triggers.file_patterns:
                if fnmatch.fnmatch(context.file_path, pattern):
                    matched_patterns.append(pattern)

            if matched_patterns:
                triggered_by.extend(matched_patterns)
                match_reasons.append(f"file patterns: {', '.join(matched_patterns)}")
                total_confidence += 0.3

        # Check tool triggers
        if skill.triggers.tools and context.tools_in_use:
            matched_tools = set(skill.triggers.tools) & set(context.tools_in_use)

            if matched_tools:
                triggered_by.extend(list(matched_tools))
                match_reasons.append(f"tools: {', '.join(matched_tools)}")
                total_confidence += 0.2

        # If any triggers matched, return the match
        if triggered_by:
            return SkillMatch(
                skill=skill,
                match_reason="; ".join(match_reasons),
                confidence=min(1.0, total_confidence),
                triggered_by=triggered_by,
            )

        return None


# Global matcher instance
_global_matcher: SkillMatcher | None = None


def get_skill_matcher(project_root: Path | None = None) -> SkillMatcher:
    """Get or create the global skill matcher."""
    global _global_matcher

    if _global_matcher is None:
        _global_matcher = SkillMatcher(project_root)

    return _global_matcher


def match_skills(context: SkillContext) -> list[SkillMatch]:
    """
    Convenience function to match skills.

    Args:
        context: The context to match

    Returns:
        List of SkillMatch
    """
    matcher = get_skill_matcher()
    return matcher.match(context)
