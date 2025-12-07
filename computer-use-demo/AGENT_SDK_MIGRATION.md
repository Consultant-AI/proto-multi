# Claude Agent SDK Migration - Specialist Sub-Agents

## Overview

This document describes the migration of specialist agents from Python classes to Claude Agent SDK-style markdown files with YAML frontmatter.

## What Changed

### Before: Python Classes
Specialists were defined as Python classes in `computer_use_demo/agents/specialists/`:
```python
class SeniorDeveloperAgent(BaseSpecialist):
    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        super().__init__(
            role="senior-developer",
            name="Senior Developer Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        return """Software engineering, system architecture..."""
```

### After: Markdown Files
Specialists are now markdown files in `.claude/agents/specialists/`:
```markdown
---
name: senior-developer
description: |
  Expert software engineer for architecture, implementation, and code quality.
  Use PROACTIVELY for: complex features, architecture decisions, code reviews.
tools: Bash, Read, Write, Edit, Grep, Glob
model: sonnet
---

You are a Senior Developer Specialist in the Proto AI multi-agent system.

## Your Expertise
Software engineering, system architecture, full-stack development...
```

## Benefits of Migration

1. **Easier to Create/Modify**: No code changes needed, just edit markdown
2. **Automatic Delegation**: Claude automatically selects specialists based on descriptions
3. **Per-Agent Model Selection**: Can use Haiku for simple tasks, Sonnet for complex
4. **Better Portability**: Markdown files can be shared across projects
5. **Simpler Maintenance**: No Python class hierarchy to maintain
6. **Standard Format**: Follows Claude Agent SDK conventions

## Converted Specialists (19 total)

### Development & Technical
1. **senior-developer** - Architecture, implementation, code reviews
2. **devops** - CI/CD, infrastructure, containers, monitoring
3. **qa-testing** - Test planning, automated testing, quality metrics
4. **security** - Security audits, compliance, vulnerability assessment
5. **technical-writer** - API docs, user guides, technical documentation

### Product & Design
6. **product-manager** - Requirements, user stories, prioritization
7. **product-strategy** - Product vision, market research, GTM planning
8. **ux-designer** - UI/UX design, wireframes, design systems

### Data & Analytics
9. **data-analyst** - SQL queries, dashboards, statistical analysis
10. **growth-analytics** - Funnel optimization, user acquisition, A/B testing

### Business Functions
11. **sales** - Sales strategy, lead qualification, deal negotiation
12. **customer-success** - Onboarding, retention, account management
13. **marketing-strategy** - Marketing strategy, campaigns, brand development
14. **content-marketing** - Blog posts, SEO content, social media

### Operations & Support
15. **finance** - Budgeting, forecasting, financial reporting
16. **legal-compliance** - Contract review, privacy compliance, IP protection
17. **hr-people** - Recruitment, performance management, culture
18. **business-operations** - Process optimization, vendor management, OKRs
19. **admin-coordinator** - Meeting management, document organization (uses Haiku)

## How to Use Specialists

### Automatic Delegation (Recommended)

The CEO agent now knows about all 19 specialists. Simply describe what needs to be done and mention the specialist:

```python
ceo = CEOAgent()
result = await ceo.execute_with_planning(
    task="I need the senior-developer to implement user authentication based on the technical spec"
)
```

The system will:
1. See "senior-developer" mentioned
2. Load `.claude/agents/specialists/senior-developer.md`
3. Invoke the specialist with the task and context
4. Return the result to the CEO

### Manual Invocation (If Needed)

You can also manually invoke specialists using the SubagentCoordinator:

```python
from computer_use_demo.agent_sdk.subagents import SubagentCoordinator, SubagentTask, SubagentType

coordinator = SubagentCoordinator()
task = SubagentTask(
    task_id="impl-auth",
    subagent_type=SubagentType.EXECUTION,  # or use custom type
    prompt="Implement user authentication system",
    context={"technical_spec": "..."}
)
result = await coordinator.execute_task(task, orchestrator_callback)
```

## File Locations

- **Markdown Specialists**: `.claude/agents/specialists/*.md` (19 files)
- **Python CEO Agent**: `computer_use_demo/agents/ceo_agent.py` (updated with specialist list)
- **Original Python Classes**: `computer_use_demo/agents/specialists/*.py` (kept for reference, not used)
- **Test Script**: `test_markdown_specialists.py`

## Updated CEO Agent

The CEO agent's system prompt now includes:

```python
## Available Specialist Sub-Agents

You have access to 19 specialist sub-agents. Delegate tasks by describing what needs to be done
and which specialist should handle it. The system will automatically invoke the appropriate specialist.

### Development & Technical:
- **senior-developer**: Architecture, implementation, code reviews...
- **devops**: CI/CD, infrastructure, containers...
...
```

## Testing

Run the test script to verify all specialists are valid:

```bash
cd computer-use-demo
python3 test_markdown_specialists.py
```

Expected output:
```
✅ Found 19/19 specialists
🎉 All specialists validated successfully!
```

## Next Steps

1. ✅ **Create markdown specialists** - Done (19 files)
2. ✅ **Update CEO system prompt** - Done
3. ✅ **Test validation** - Done
4. **Integration testing** - Test actual delegation from CEO to specialists
5. **Documentation** - Update user-facing docs with new specialist usage
6. **Optional**: Deprecate Python specialist classes once markdown delegation is proven

## Migration Notes

- **Backward Compatibility**: Python specialist classes still exist but are not used
- **Model Selection**: Most specialists use Sonnet, admin-coordinator uses Haiku for cost efficiency
- **Tool Access**: All specialists have access to core tools (Bash, Read, Write, Edit, Grep, Glob)
- **Context Passing**: Planning documents and project context are passed to specialists via the task prompt
- **Session Management**: Each specialist invocation gets isolated context via SubagentCoordinator

## Example Usage

### Before (Manual Python)
```python
from computer_use_demo.agents.specialists import SeniorDeveloperAgent

dev_agent = SeniorDeveloperAgent(tools=coding_tools)
result = await dev_agent.execute(
    task="Implement authentication",
    context={"technical_spec": "..."}
)
```

### After (Auto Markdown)
```python
from computer_use_demo.agents import CEOAgent

ceo = CEOAgent()
result = await ceo.execute_with_planning(
    task="Have the senior-developer implement authentication based on the technical spec"
)
# CEO automatically invokes senior-developer.md
```

## Resources

- Claude Agent SDK Docs: https://docs.claude.com/agent-sdk
- Model Context Protocol: https://modelcontextprotocol.io
- Agent Markdown Format: `.claude/agents/README.md`

---

**Migration completed**: December 6, 2025
**Validated**: All 19 specialists ✅
