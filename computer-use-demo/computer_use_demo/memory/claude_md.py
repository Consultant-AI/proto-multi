"""
CLAUDE.md file parser.

Parses markdown files into structured sections for memory management.
"""

import re
from pathlib import Path

from .types import MemoryFile, MemoryLevel, MemorySection


def parse_claude_md(path: Path, level: MemoryLevel) -> MemoryFile:
    """
    Parse a CLAUDE.md file into structured sections.

    Args:
        path: Path to the CLAUDE.md file
        level: Memory hierarchy level

    Returns:
        Parsed MemoryFile
    """
    memory_file = MemoryFile(
        path=path,
        level=level,
        exists=path.exists(),
    )

    if not memory_file.exists:
        return memory_file

    try:
        content = path.read_text(encoding="utf-8")
        memory_file.raw_content = content
        memory_file.modified_at = path.stat().st_mtime
        memory_file.sections = _parse_sections(content)
    except Exception:
        # If we can't read the file, return empty
        pass

    return memory_file


def _parse_sections(content: str) -> list[MemorySection]:
    """
    Parse markdown content into sections.

    Sections are delimited by markdown headers (# Header).
    """
    sections = []

    # Pattern to match markdown headers
    header_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    # Find all headers and their positions
    headers = list(header_pattern.finditer(content))

    if not headers:
        # No headers - treat entire content as one section
        if content.strip():
            sections.append(
                MemorySection(
                    title="default",
                    content=content.strip(),
                    level=0,
                )
            )
        return sections

    # Process each header and its content
    for i, match in enumerate(headers):
        header_level = len(match.group(1))
        title = match.group(2).strip()

        # Get content from after this header to next header (or end)
        start = match.end()
        if i + 1 < len(headers):
            end = headers[i + 1].start()
        else:
            end = len(content)

        section_content = content[start:end].strip()

        # Extract tags from content (lines starting with @tag or #tag)
        tags = _extract_tags(section_content)

        sections.append(
            MemorySection(
                title=title,
                content=section_content,
                level=header_level,
                tags=tags,
            )
        )

    return sections


def _extract_tags(content: str) -> list[str]:
    """Extract tags from section content."""
    tags = []

    # Look for @tag patterns
    at_tags = re.findall(r"@(\w+)", content)
    tags.extend(at_tags)

    # Look for inline #tag patterns (but not headers)
    hash_tags = re.findall(r"(?<!^)#(\w+)", content, re.MULTILINE)
    tags.extend(hash_tags)

    return list(set(tags))


def format_section(section: MemorySection) -> str:
    """Format a section back to markdown."""
    header = "#" * section.level
    return f"{header} {section.title}\n\n{section.content}"


def format_memory_file(memory_file: MemoryFile) -> str:
    """Format a memory file back to markdown."""
    if not memory_file.sections:
        return memory_file.raw_content

    parts = []
    for section in memory_file.sections:
        if section.level > 0:
            parts.append(format_section(section))
        else:
            parts.append(section.content)

    return "\n\n".join(parts)
