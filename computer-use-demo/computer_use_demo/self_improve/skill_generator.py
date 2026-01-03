"""
Skill Generator.

Generates skills from patterns and code analysis.
"""

import json
from pathlib import Path
from typing import Any

from .types import SkillSpec, Modification, ModificationType, ModificationStatus


class SkillGenerator:
    """
    Generates skill files from patterns and analysis.

    Features:
    - Pattern extraction from code
    - Best practice compilation
    - Auto-trigger generation
    - Confidence scoring
    """

    def __init__(self, skills_dir: Path | None = None):
        self._skills_dir = skills_dir or Path.home() / ".claude" / "skills"
        self._skills_dir.mkdir(parents=True, exist_ok=True)

    def create_skill_spec(
        self,
        name: str,
        description: str,
        patterns: list[str],
        sections: list[dict[str, str]] | None = None,
        triggers: dict[str, list[str]] | None = None,
    ) -> SkillSpec:
        """Create a skill specification."""
        # Auto-generate triggers if not provided
        if not triggers:
            triggers = self._generate_triggers(name, patterns)

        # Auto-generate sections if not provided
        if not sections:
            sections = self._generate_sections(name, description, patterns)

        return SkillSpec(
            name=name,
            display_name=name.replace("-", " ").title(),
            description=description,
            triggers=triggers,
            sections=sections,
            patterns=patterns,
            generated_from="pattern_analysis",
            confidence=0.8,
        )

    def _generate_triggers(
        self,
        name: str,
        patterns: list[str],
    ) -> dict[str, list[str]]:
        """Generate trigger conditions from patterns."""
        # Keywords from name and patterns
        keywords = [name.lower()]
        keywords.extend(p.lower() for p in patterns)

        return {
            "keywords": keywords,
            "file_patterns": [],
            "tools": [],
        }

    def _generate_sections(
        self,
        name: str,
        description: str,
        patterns: list[str],
    ) -> list[dict[str, str]]:
        """Generate skill sections from patterns."""
        sections = [
            {
                "title": "Overview",
                "content": description,
            },
            {
                "title": "Key Concepts",
                "content": "\n".join(f"- {p}" for p in patterns),
            },
            {
                "title": "Best Practices",
                "content": "Follow established patterns and conventions.",
            },
            {
                "title": "Common Pitfalls",
                "content": "Avoid common mistakes when working with these patterns.",
            },
        ]

        return sections

    async def generate_skill_content(self, spec: SkillSpec) -> str:
        """Generate SKILL.md content."""
        # YAML frontmatter
        frontmatter = f"""---
name: {spec.name}
description: {spec.description}
triggers:
  keywords: {spec.triggers.get("keywords", [])}
  file_patterns: {spec.triggers.get("file_patterns", [])}
  tools: {spec.triggers.get("tools", [])}
auto_activate: true
---

"""

        # Sections
        content_parts = [frontmatter]

        for section in spec.sections:
            content_parts.append(f"# {section['title']}\n\n{section['content']}\n\n")

        # Add patterns reference
        if spec.patterns:
            content_parts.append("# Patterns\n\n")
            for pattern in spec.patterns:
                content_parts.append(f"- **{pattern}**: Best practices for {pattern.lower()}\n")

        return "".join(content_parts)

    async def create_skill(
        self,
        spec: SkillSpec,
        dry_run: bool = False,
    ) -> Modification:
        """
        Create a new skill.

        Args:
            spec: Skill specification
            dry_run: If True, don't actually create the file

        Returns:
            Modification record
        """
        content = await self.generate_skill_content(spec)
        filename = f"{spec.name}.md"
        target_path = self._skills_dir / filename

        modification = Modification(
            type=ModificationType.SKILL_CREATE,
            target=str(target_path),
            description=f"Create skill: {spec.display_name}",
            changes={
                "type": "create",
                "content": content,
                "spec": {
                    "name": spec.name,
                    "patterns": spec.patterns,
                    "triggers": spec.triggers,
                },
            },
            reason=f"Generate skill from patterns: {', '.join(spec.patterns)}",
            source="skill_generator",
        )

        if not dry_run:
            target_path.write_text(content)
            modification.status = ModificationStatus.APPLIED
            print(f"[SkillGenerator] Created skill: {spec.name}")

        return modification

    async def extract_patterns_from_code(
        self,
        code_path: Path,
    ) -> list[str]:
        """
        Extract patterns from code files.

        This is a simplified pattern extractor. A real implementation
        would use AST analysis and ML.
        """
        patterns = []

        if not code_path.exists():
            return patterns

        content = code_path.read_text()

        # Look for common patterns
        pattern_indicators = [
            ("class ", "Class-based design"),
            ("async def", "Async patterns"),
            ("@dataclass", "Dataclass usage"),
            ("try:", "Error handling"),
            ("with ", "Context managers"),
            ("@property", "Property decorators"),
            ("typing.", "Type hints"),
            ("logging.", "Logging patterns"),
            ("unittest", "Unit testing"),
            ("pytest", "Pytest patterns"),
        ]

        for indicator, pattern_name in pattern_indicators:
            if indicator in content:
                patterns.append(pattern_name)

        return list(set(patterns))

    async def generate_skill_from_codebase(
        self,
        codebase_path: Path,
        name: str,
    ) -> SkillSpec | None:
        """
        Generate a skill by analyzing a codebase.

        Args:
            codebase_path: Path to codebase
            name: Name for the skill

        Returns:
            Generated skill specification
        """
        if not codebase_path.exists():
            return None

        all_patterns = []

        # Analyze Python files
        for py_file in codebase_path.rglob("*.py"):
            patterns = await self.extract_patterns_from_code(py_file)
            all_patterns.extend(patterns)

        # Deduplicate and take top patterns
        pattern_counts = {}
        for p in all_patterns:
            pattern_counts[p] = pattern_counts.get(p, 0) + 1

        top_patterns = sorted(
            pattern_counts.keys(),
            key=lambda x: pattern_counts[x],
            reverse=True,
        )[:10]

        if not top_patterns:
            return None

        return self.create_skill_spec(
            name=name,
            description=f"Patterns and best practices from {codebase_path.name}",
            patterns=top_patterns,
        )

    def list_skills(self) -> list[dict[str, Any]]:
        """List existing generated skills."""
        skills = []

        for skill_file in self._skills_dir.glob("*.md"):
            try:
                content = skill_file.read_text()
                # Parse frontmatter (simplified)
                if content.startswith("---"):
                    end = content.find("---", 3)
                    if end > 0:
                        frontmatter = content[3:end].strip()
                        # Basic parsing
                        skill_info = {"file": skill_file.name}
                        for line in frontmatter.split("\n"):
                            if ":" in line:
                                key, value = line.split(":", 1)
                                skill_info[key.strip()] = value.strip()
                        skills.append(skill_info)
            except Exception:
                pass

        return skills
