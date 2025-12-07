"""
Knowledge Management Tool for Proto Multi-Agent System.

Enables agents to store and retrieve knowledge within projects.
"""

from pathlib import Path
from typing import Any, Optional

from ...logging import get_logger
from ...planning.knowledge_store import KnowledgeStore, KnowledgeType
from ...planning.project_manager import ProjectManager
from ..base import BaseAnthropicTool, CLIResult, ToolError, ToolResult


class KnowledgeTool(BaseAnthropicTool):
    """
    Tool for managing project knowledge base.

    This tool allows agents to persist learnings, decisions, patterns,
    and context across project execution.
    """

    name: str = "manage_knowledge"
    api_type: str = "custom"

    def to_params(self):
        """Return tool parameter schema for Anthropic API."""
        return {
            "name": self.name,
            "description": """Manage the project knowledge base.

Use this tool to:
- Store important decisions, learnings, and patterns
- Search for relevant knowledge from past work
- Build up project context over time
- Link knowledge to tasks and other entries
- Track best practices and lessons learned

Knowledge types:
- technical_decision: Important technical choices and rationale
- learning: Insights gained during work
- pattern: Recurring patterns or solutions
- reference: External references and documentation
- context: Project context and domain knowledge
- best_practice: Proven approaches and guidelines
- lesson_learned: What worked and what didn't

Operations:
- add: Add new knowledge entry
- search: Search knowledge base by keywords
- get: Get a specific entry by ID
- update: Update an existing entry
- list: List entries (optionally filtered)
- summary: Get knowledge base statistics
- link_to_task: Link knowledge to a task

Returns knowledge entry information or search results.""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "search", "get", "update", "list", "summary", "link_to_task"],
                        "description": "The operation to perform",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project (required for all operations)",
                    },
                    "entry_id": {
                        "type": "string",
                        "description": "Knowledge entry ID (required for: get, update, link_to_task)",
                    },
                    "title": {
                        "type": "string",
                        "description": "Entry title/summary (required for: add)",
                    },
                    "content": {
                        "type": "string",
                        "description": "Entry content (required for: add; optional for: update)",
                    },
                    "knowledge_type": {
                        "type": "string",
                        "enum": [
                            "technical_decision",
                            "learning",
                            "pattern",
                            "reference",
                            "context",
                            "best_practice",
                            "lesson_learned",
                        ],
                        "description": "Type of knowledge (optional for: add, update)",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorization (optional for: add, update)",
                    },
                    "source": {
                        "type": "string",
                        "description": "Source of knowledge (agent name, document, etc.) (optional for: add)",
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (required for: search)",
                    },
                    "filter_type": {
                        "type": "string",
                        "enum": [
                            "technical_decision",
                            "learning",
                            "pattern",
                            "reference",
                            "context",
                            "best_practice",
                            "lesson_learned",
                        ],
                        "description": "Filter by knowledge type (optional for: list)",
                    },
                    "filter_tag": {
                        "type": "string",
                        "description": "Filter by tag (optional for: list)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to link to (required for: link_to_task)",
                    },
                },
                "required": ["operation", "project_name"],
            },
        }

    async def __call__(
        self,
        operation: str,
        project_name: str,
        entry_id: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        tags: Optional[list[str]] = None,
        source: Optional[str] = None,
        query: Optional[str] = None,
        filter_type: Optional[str] = None,
        filter_tag: Optional[str] = None,
        task_id: Optional[str] = None,
        **kwargs,
    ) -> ToolResult | CLIResult:
        """
        Manage project knowledge base.

        Args:
            operation: Operation to perform
            project_name: Name of the project
            entry_id: Knowledge entry ID (for operations that need it)
            title: Entry title (for add)
            content: Entry content
            knowledge_type: Type of knowledge
            tags: Tags for categorization
            source: Source of knowledge
            query: Search query (for search)
            filter_type: Type filter (for list)
            filter_tag: Tag filter (for list)
            task_id: Task ID (for link_to_task)

        Returns:
            ToolResult with knowledge information
        """
        logger = get_logger()

        try:
            # Get project path
            project_manager = ProjectManager()
            project_slug = project_manager.slugify_project_name(project_name)
            project_path = project_manager.planning_root / project_slug

            if not project_path.exists() and operation != "add":
                raise ToolError(
                    f"Project '{project_name}' not found. Create planning docs first."
                )

            # Ensure project exists for add operation
            if operation == "add":
                project_path.mkdir(parents=True, exist_ok=True)

            # Initialize knowledge store
            knowledge_store = KnowledgeStore(project_path)

            # Execute operation
            if operation == "add":
                if not title or not content:
                    raise ToolError("title and content are required for add operation")

                entry = knowledge_store.add_entry(
                    title=title,
                    content=content,
                    knowledge_type=KnowledgeType(knowledge_type) if knowledge_type else KnowledgeType.CONTEXT,
                    tags=tags,
                    source=source,
                )

                logger.log_event(
                    event_type="knowledge_added",
                    session_id="knowledge-tool",
                    data={
                        "entry_id": entry.id,
                        "title": entry.title,
                        "type": entry.type.value,
                        "project": project_name,
                    },
                )

                return ToolResult(
                    output=f"Added knowledge entry '{entry.title}' (ID: {entry.id})",
                    system=f"Knowledge entry created:\n"
                    f"  ID: {entry.id}\n"
                    f"  Title: {entry.title}\n"
                    f"  Type: {entry.type.value}\n"
                    f"  Tags: {', '.join(entry.tags) if entry.tags else 'None'}",
                )

            elif operation == "search":
                if not query:
                    raise ToolError("query is required for search operation")

                entries = knowledge_store.search_entries(query)

                if not entries:
                    return ToolResult(
                        output=f"No knowledge entries found matching '{query}'",
                        system="Search returned no results",
                    )

                # Format search results (top 10)
                results = []
                for entry in entries[:10]:
                    results.append(
                        f"- [{entry.type.value}] {entry.title} (ID: {entry.id[:8]})\n"
                        f"  {entry.content[:100]}{'...' if len(entry.content) > 100 else ''}"
                    )

                return ToolResult(
                    output=f"Found {len(entries)} result(s) for '{query}':\n\n" + "\n\n".join(results),
                    system=f"Search completed: {len(entries)} entries found",
                )

            elif operation == "get":
                if not entry_id:
                    raise ToolError("entry_id is required for get operation")

                entry = knowledge_store.get_entry(entry_id)
                if not entry:
                    raise ToolError(f"Knowledge entry {entry_id} not found")

                details = [
                    f"Title: {entry.title}",
                    f"ID: {entry.id}",
                    f"Type: {entry.type.value}",
                    f"Content:\n{entry.content}",
                    f"\nTags: {', '.join(entry.tags)}" if entry.tags else "",
                    f"Source: {entry.source}" if entry.source else "",
                    f"Related Tasks: {len(entry.related_tasks)}" if entry.related_tasks else "",
                    f"Related Entries: {len(entry.related_entries)}" if entry.related_entries else "",
                    f"Created: {entry.created_at}",
                    f"Updated: {entry.updated_at}",
                ]

                return ToolResult(
                    output="\n".join([d for d in details if d]),
                    system=f"Retrieved knowledge entry {entry_id}",
                )

            elif operation == "update":
                if not entry_id:
                    raise ToolError("entry_id is required for update operation")

                entry = knowledge_store.update_entry(
                    entry_id=entry_id,
                    title=title,
                    content=content,
                    add_tags=tags,
                )

                if not entry:
                    raise ToolError(f"Knowledge entry {entry_id} not found")

                return ToolResult(
                    output=f"Updated knowledge entry '{entry.title}'",
                    system=f"Entry {entry_id} updated successfully",
                )

            elif operation == "list":
                # Apply filters
                if filter_type:
                    entries = knowledge_store.get_entries_by_type(KnowledgeType(filter_type))
                elif filter_tag:
                    entries = knowledge_store.get_entries_by_tag(filter_tag)
                else:
                    entries = knowledge_store.get_all_entries()

                if not entries:
                    return ToolResult(
                        output="No knowledge entries found matching the criteria",
                        system="Knowledge list is empty",
                    )

                # Format entry list (top 20)
                entry_list = []
                for entry in entries[:20]:
                    entry_list.append(
                        f"- [{entry.type.value}] {entry.title} (ID: {entry.id[:8]})"
                    )

                return ToolResult(
                    output=f"Found {len(entries)} knowledge entr{'ies' if len(entries) != 1 else 'y'}:\n"
                    + "\n".join(entry_list)
                    + (f"\n\n(Showing first 20 of {len(entries)})" if len(entries) > 20 else ""),
                    system=f"Listed {min(20, len(entries))} of {len(entries)} entries",
                )

            elif operation == "summary":
                summary = knowledge_store.get_knowledge_summary()

                output = [
                    f"Knowledge Base Summary for '{project_name}':",
                    f"  Total Entries: {summary['total']}",
                    f"  Average Relevance: {summary['avg_relevance']:.2f}",
                    f"",
                    f"By Type:",
                    f"  Technical Decisions: {summary['by_type']['technical_decisions']}",
                    f"  Learnings: {summary['by_type']['learnings']}",
                    f"  Patterns: {summary['by_type']['patterns']}",
                    f"  References: {summary['by_type']['references']}",
                    f"  Context: {summary['by_type']['context']}",
                    f"  Best Practices: {summary['by_type']['best_practices']}",
                    f"  Lessons Learned: {summary['by_type']['lessons_learned']}",
                ]

                return ToolResult(
                    output="\n".join(output),
                    system=f"Knowledge summary generated for {project_name}",
                )

            elif operation == "link_to_task":
                if not entry_id or not task_id:
                    raise ToolError("entry_id and task_id are required for link_to_task operation")

                success = knowledge_store.link_to_task(entry_id, task_id)
                if not success:
                    raise ToolError(f"Knowledge entry {entry_id} not found")

                entry = knowledge_store.get_entry(entry_id)
                return ToolResult(
                    output=f"Linked knowledge entry '{entry.title}' to task {task_id}",
                    system=f"Entry {entry_id} linked to task {task_id}",
                )

            else:
                raise ToolError(f"Unknown operation: {operation}")

        except ToolError:
            raise
        except Exception as e:
            logger.log_event(
                event_type="knowledge_error",
                session_id="knowledge-tool",
                data={"error": str(e), "operation": operation},
            )
            raise ToolError(f"Knowledge management error: {e}")
