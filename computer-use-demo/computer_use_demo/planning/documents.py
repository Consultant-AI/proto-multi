"""
Planning Document Framework for Proto.

Provides document templates, generation prompts, and structure
for creating comprehensive planning documentation.
"""

from dataclasses import dataclass
from typing import Literal

DocumentType = Literal[
    "project_overview",
    "requirements",
    "technical_spec",
    "roadmap",
    "knowledge_base",
    "decisions",
    "specialist_plan",
]


@dataclass
class DocumentTemplate:
    """Template for a planning document."""

    doc_type: DocumentType
    filename: str
    title: str
    generation_prompt: str
    template_structure: str


class PlanningDocuments:
    """
    Framework for planning document generation.

    Provides templates and prompts for each document type.
    """

    TEMPLATES = {
        "project_overview": DocumentTemplate(
            doc_type="project_overview",
            filename="PROJECT_OVERVIEW.md",
            title="Project Overview",
            generation_prompt="""
Generate a comprehensive project overview for the following task:

Task: {task}

Create a markdown document that includes:
1. **Project Name**: A clear, concise name for this project/task
2. **Purpose**: What this project aims to achieve
3. **Scope**: What is included and what is out of scope
4. **Success Criteria**: How we'll know when this is successful
5. **Key Stakeholders**: Who is involved or affected
6. **High-Level Timeline**: Rough estimate of timeframes
7. **Dependencies**: What this project depends on
8. **Risks**: Potential challenges or blockers

Keep it concise but comprehensive. Focus on the "what" and "why", not implementation details.
""",
            template_structure="""# {project_name}

## Purpose
[Brief description of what this project aims to achieve]

## Scope

### In Scope
- [Item 1]
- [Item 2]

### Out of Scope
- [Item 1]
- [Item 2]

## Success Criteria
1. [Criterion 1]
2. [Criterion 2]

## Key Stakeholders
- **Role 1**: Description
- **Role 2**: Description

## High-Level Timeline
- **Phase 1**: [Timeframe]
- **Phase 2**: [Timeframe]

## Dependencies
- [Dependency 1]
- [Dependency 2]

## Risks & Mitigation
| Risk | Impact | Mitigation Strategy |
|------|--------|-------------------|
| [Risk 1] | High/Med/Low | [Strategy] |
""",
        ),
        "requirements": DocumentTemplate(
            doc_type="requirements",
            filename="REQUIREMENTS.md",
            title="Requirements Document",
            generation_prompt="""
Generate a detailed requirements document (PRD-style) for the following task:

Task: {task}
Context: {context}

Create a markdown document that includes:
1. **User Stories**: Key user journeys and needs
2. **Functional Requirements**: What the system must do
3. **Non-Functional Requirements**: Performance, security, usability constraints
4. **User Interface Requirements**: Key UI/UX needs
5. **Data Requirements**: What data is needed
6. **Integration Requirements**: External systems or APIs
7. **Acceptance Criteria**: How to verify each requirement

Be specific and measurable. Use "must", "should", "could" to indicate priority.
""",
            template_structure="""# Requirements Document

## User Stories

### Story 1: [Title]
**As a** [user type]
**I want** [goal]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

## Functional Requirements

### FR-1: [Requirement Name]
**Priority**: Must/Should/Could
**Description**: [Detailed description]
**Acceptance Criteria**: [How to verify]

## Non-Functional Requirements

### NFR-1: Performance
- [Requirement]

### NFR-2: Security
- [Requirement]

### NFR-3: Usability
- [Requirement]

## Data Requirements
| Data Entity | Fields | Source | Validation Rules |
|------------|--------|--------|-----------------|
| [Entity 1] | [Fields] | [Source] | [Rules] |

## Integration Requirements
- **System 1**: [Purpose and integration points]
- **System 2**: [Purpose and integration points]
""",
        ),
        "technical_spec": DocumentTemplate(
            doc_type="technical_spec",
            filename="TECHNICAL_SPEC.md",
            title="Technical Specification",
            generation_prompt="""
Generate a technical specification document for the following task:

Task: {task}
Requirements: {requirements}

Create a markdown document that includes:
1. **System Architecture**: High-level components and their relationships
2. **Technology Stack**: Languages, frameworks, tools to be used
3. **Data Models**: Key data structures and schemas
4. **API Design**: Endpoints, request/response formats (if applicable)
5. **File Structure**: Project organization
6. **Key Algorithms**: Important logic or processing steps
7. **Security Considerations**: Authentication, authorization, data protection
8. **Performance Considerations**: Scalability, caching, optimization
9. **Testing Strategy**: Unit, integration, e2e testing approach

Be technical but clear. Include diagrams where helpful (as ASCII or mermaid).
""",
            template_structure="""# Technical Specification

## System Architecture

```
[High-level architecture diagram]
```

**Components:**
- **Component 1**: [Description and responsibility]
- **Component 2**: [Description and responsibility]

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | [Tech] | [Why] |
| Backend | [Tech] | [Why] |
| Database | [Tech] | [Why] |
| Infrastructure | [Tech] | [Why] |

## Data Models

### Model 1: [Name]
```
{
  field1: type,
  field2: type,
  relationships: []
}
```

## API Design

### Endpoint 1: `POST /api/resource`
**Purpose**: [What it does]
**Request:**
```json
{
  "field": "value"
}
```
**Response:**
```json
{
  "result": "data"
}
```

## File Structure
```
project/
├── src/
│   ├── components/
│   ├── services/
│   └── utils/
├── tests/
└── docs/
```

## Security Considerations
- **Authentication**: [Approach]
- **Authorization**: [Approach]
- **Data Protection**: [Approach]

## Performance Considerations
- **Caching Strategy**: [Approach]
- **Optimization**: [Key optimizations]
- **Scalability**: [How it scales]

## Testing Strategy
- **Unit Tests**: [Coverage and approach]
- **Integration Tests**: [Key integration points]
- **E2E Tests**: [Critical user flows]
""",
        ),
        "roadmap": DocumentTemplate(
            doc_type="roadmap",
            filename="ROADMAP.md",
            title="Project Roadmap",
            generation_prompt="""
Generate a project roadmap for the following task:

Task: {task}
Requirements: {requirements}
Technical Spec: {technical_spec}

Create a markdown document that includes:
1. **Milestones**: Major delivery points with dates
2. **Phases**: Logical groupings of work
3. **Task Breakdown**: Specific tasks for each phase
4. **Dependencies**: What must happen before what
5. **Timeline Visualization**: Gantt-style representation
6. **Resource Allocation**: Who works on what (if multi-agent)

Be realistic about timeframes. Include buffer time for testing and iteration.
""",
            template_structure="""# Project Roadmap

## Timeline Overview

```
Week 1-2: [Phase 1]
Week 3-4: [Phase 2]
Week 5-6: [Phase 3]
```

## Milestones

| Milestone | Date | Deliverables | Success Criteria |
|-----------|------|--------------|-----------------|
| M1: [Name] | [Date] | [Items] | [Criteria] |
| M2: [Name] | [Date] | [Items] | [Criteria] |

## Phase Breakdown

### Phase 1: [Name] (Week 1-2)

**Goal**: [What this phase achieves]

**Tasks:**
- [ ] Task 1 (Agent: [which agent], Est: [time])
- [ ] Task 2 (Agent: [which agent], Est: [time])

**Dependencies**: [What must be done first]
**Deliverables**: [What's produced]

### Phase 2: [Name] (Week 3-4)

[Similar structure]

## Critical Path
1. Task A → Task B → Task C
2. Task D can happen in parallel with Task B

## Risk Buffer
- **Time Buffer**: [X days] built in for unexpected issues
- **Scope Buffer**: [Optional features] can be deferred if needed
""",
        ),
        "knowledge_base": DocumentTemplate(
            doc_type="knowledge_base",
            filename="KNOWLEDGE_BASE.md",
            title="Knowledge Base",
            generation_prompt="""
Generate a knowledge base document for the following task:

Task: {task}
Domain: {domain}

Create a markdown document that includes:
1. **Domain Context**: Background information about this domain
2. **Key Concepts**: Important terms and definitions
3. **Best Practices**: Industry standards and conventions
4. **Common Patterns**: Reusable approaches for this type of work
5. **Constraints**: Known limitations or requirements
6. **Resources**: Links to documentation, tutorials, references
7. **Examples**: Similar projects or code examples

This serves as a reference guide for agents working on this project.
""",
            template_structure="""# Knowledge Base

## Domain Context
[Background information about this domain/industry/problem space]

## Key Concepts

### Concept 1: [Name]
**Definition**: [Clear explanation]
**Importance**: [Why it matters]
**Example**: [Concrete example]

## Best Practices

### Practice 1: [Name]
**Description**: [What to do]
**Rationale**: [Why this is best practice]
**Implementation**: [How to apply it]

## Common Patterns

### Pattern 1: [Name]
**Problem**: [What problem it solves]
**Solution**: [How the pattern works]
**When to Use**: [Scenarios where this applies]

## Constraints
- **Constraint 1**: [Description and impact]
- **Constraint 2**: [Description and impact]

## Resources
- [Resource Name](URL) - Description
- [Resource Name](URL) - Description

## Examples

### Example 1: [Similar Project]
**Description**: [What it does]
**Approach**: [How it was built]
**Learnings**: [What we can apply]
""",
        ),
        "decisions": DocumentTemplate(
            doc_type="decisions",
            filename="DECISIONS.md",
            title="Decision Log",
            generation_prompt="""
Create a decision log template for tracking key decisions during this project.

This document will be updated as decisions are made.
""",
            template_structure="""# Decision Log

## Decision 1: [Title]

**Date**: [YYYY-MM-DD]
**Decision Maker**: [Agent or team]
**Status**: Proposed / Accepted / Implemented

**Context**: [What led to this decision]

**Options Considered**:
1. **Option A**: [Description]
   - Pros: [List]
   - Cons: [List]
2. **Option B**: [Description]
   - Pros: [List]
   - Cons: [List]

**Decision**: [What was chosen]

**Rationale**: [Why this option]

**Implications**: [What this means for the project]

**Follow-up Actions**:
- [ ] Action 1
- [ ] Action 2
""",
        ),
        "specialist_plan": DocumentTemplate(
            doc_type="specialist_plan",
            filename="agents/{specialist}_plan.md",
            title="{specialist} Plan",
            generation_prompt="""
Generate a specialized plan for the {specialist} agent working on this task:

Task: {task}
Domain: {specialist}
Overall Requirements: {requirements}

Create a markdown document focused on {specialist}-specific concerns:
1. **Scope**: What the {specialist} agent is responsible for
2. **Deliverables**: What this agent will produce
3. **Tasks**: Step-by-step breakdown
4. **Dependencies**: What this agent needs from other agents
5. **Outputs**: What this agent provides to other agents
6. **Success Criteria**: How to measure this agent's work

Make it specific to the {specialist} domain.
""",
            template_structure="""# {specialist} Plan

## Scope
This agent is responsible for:
- [Responsibility 1]
- [Responsibility 2]

## Deliverables
1. **[Deliverable 1]**: Description
2. **[Deliverable 2]**: Description

## Task Breakdown
- [ ] Task 1: [Description] (Est: [time])
- [ ] Task 2: [Description] (Est: [time])

## Dependencies
**From Other Agents:**
- Requires [X] from [Agent Y]
- Needs [A] from [Agent B]

**Provides to Other Agents:**
- Delivers [X] to [Agent Y]
- Supplies [A] to [Agent B]

## Domain-Specific Considerations
- [Consideration 1]
- [Consideration 2]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Resources
- [Relevant links, examples, references]
""",
        ),
    }

    @classmethod
    def get_template(cls, doc_type: DocumentType) -> DocumentTemplate:
        """Get template for a specific document type."""
        return cls.TEMPLATES[doc_type]

    @classmethod
    def get_all_templates(cls) -> dict[DocumentType, DocumentTemplate]:
        """Get all available templates."""
        return cls.TEMPLATES.copy()

    @classmethod
    def format_prompt(
        cls, doc_type: DocumentType, **kwargs
    ) -> str:
        """
        Format a generation prompt with provided context.

        Args:
            doc_type: Type of document to generate
            **kwargs: Context variables to fill in the prompt

        Returns:
            Formatted prompt ready for LLM generation
        """
        template = cls.get_template(doc_type)
        return template.generation_prompt.format(**kwargs)
