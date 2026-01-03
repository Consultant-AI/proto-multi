"""
Task Complexity Analyzer for Proto Planning System.

Analyzes incoming tasks to determine:
1. Complexity level (simple/medium/complex/project)
2. Planning depth required
3. Required specialist domains
4. Planning strategy
"""

from dataclasses import dataclass
from typing import Literal

ComplexityLevel = Literal["simple", "medium", "complex", "project"]
SpecialistDomain = Literal[
    "marketing", "development", "design", "analytics", "content", "research"
]


@dataclass
class TaskAnalysis:
    """Result of task complexity analysis."""

    complexity: ComplexityLevel
    planning_required: bool
    estimated_steps: int
    required_specialists: list[SpecialistDomain]
    planning_strategy: dict[str, bool]  # Which planning docs to create
    reasoning: str


class TaskComplexityAnalyzer:
    """
    Analyzes task complexity to determine planning requirements.

    Uses keyword matching and heuristics to assess task complexity.
    In future iterations, this could use LLM-based analysis.
    """

    # Keywords that indicate high complexity
    PROJECT_KEYWORDS = [
        "create company",
        "build startup",
        "launch business",
        "full application",
        "end-to-end system",
        "complete platform",
    ]

    COMPLEX_KEYWORDS = [
        "implement",
        "build",
        "create",
        "make",
        "design system",
        "architecture",
        "integrate",
        "refactor",
        "migrate",
        # Project-type nouns that always need planning
        "game",
        "app",
        "application",
        "website",
        "webapp",
        "web app",
        "tool",
        "system",
        "platform",
        "clone",
        "dashboard",
        "portal",
        "service",
        "api",
        "bot",
    ]

    MEDIUM_KEYWORDS = [
        "add feature",
        "fix bug",
        "update",
        "enhance",
        "improve",
        "modify",
        "extend",
    ]

    # Keywords that indicate specialist requirements
    SPECIALIST_INDICATORS = {
        "marketing": ["marketing", "seo", "campaign", "brand", "audience", "conversion"],
        "development": ["code", "implement", "build", "api", "backend", "frontend", "database"],
        "design": ["design", "ui", "ux", "interface", "mockup", "prototype", "wireframe"],
        "analytics": ["analyze", "metrics", "data", "insights", "report", "dashboard"],
        "content": ["content", "copy", "writing", "documentation", "blog", "article"],
        "research": ["research", "investigate", "analyze", "study", "explore"],
    }

    def analyze(self, task: str, context: dict | None = None) -> TaskAnalysis:
        """
        Analyze task complexity and planning requirements.

        Args:
            task: The user's task description
            context: Optional context (existing project, session history, etc.)

        Returns:
            TaskAnalysis with complexity assessment and planning strategy
        """
        task_lower = task.lower()
        context = context or {}

        # Determine complexity level
        complexity = self._determine_complexity(task_lower, context)

        # Determine if planning is required (any non-simple task needs planning)
        planning_required = complexity in ["medium", "complex", "project"]

        # Estimate number of steps
        estimated_steps = self._estimate_steps(complexity, task_lower)

        # Identify required specialists
        required_specialists = self._identify_specialists(task_lower)

        # Determine planning strategy (which docs to create)
        planning_strategy = self._determine_planning_strategy(
            complexity, required_specialists
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            complexity, estimated_steps, required_specialists
        )

        return TaskAnalysis(
            complexity=complexity,
            planning_required=planning_required,
            estimated_steps=estimated_steps,
            required_specialists=required_specialists,
            planning_strategy=planning_strategy,
            reasoning=reasoning,
        )

    def _determine_complexity(
        self, task_lower: str, context: dict
    ) -> ComplexityLevel:
        """Determine task complexity level."""
        # Check for project-level keywords
        if any(keyword in task_lower for keyword in self.PROJECT_KEYWORDS):
            return "project"

        # Check for complex keywords
        if any(keyword in task_lower for keyword in self.COMPLEX_KEYWORDS):
            # Check if this is part of existing project
            if context.get("existing_project"):
                return "complex"
            # Standalone complex task might be project
            if len(task_lower.split()) > 20:  # Long description = more complex
                return "project"
            return "complex"

        # Check for medium keywords
        if any(keyword in task_lower for keyword in self.MEDIUM_KEYWORDS):
            return "medium"

        # Default to simple
        return "simple"

    def _estimate_steps(self, complexity: ComplexityLevel, task_lower: str) -> int:
        """Estimate number of steps required."""
        base_steps = {
            "simple": 3,
            "medium": 8,
            "complex": 15,
            "project": 30,
        }

        # Adjust based on task length and keywords
        steps = base_steps[complexity]

        # Add steps for each "and" or "then" (indicates multiple sub-tasks)
        connector_count = task_lower.count(" and ") + task_lower.count(" then ")
        steps += connector_count * 2

        return steps

    def _identify_specialists(self, task_lower: str) -> list[SpecialistDomain]:
        """Identify which specialist agents might be needed."""
        specialists = []

        for domain, keywords in self.SPECIALIST_INDICATORS.items():
            if any(keyword in task_lower for keyword in keywords):
                specialists.append(domain)  # type: ignore

        # Default to development if no specialists identified
        if not specialists:
            specialists.append("development")

        return specialists

    def _determine_planning_strategy(
        self, complexity: ComplexityLevel, specialists: list[SpecialistDomain]
    ) -> dict[str, bool]:
        """
        Determine which planning documents to create.

        Returns dict indicating which planning docs are needed.
        """
        if complexity == "simple":
            return {
                "project_overview": False,
                "requirements": False,
                "technical_spec": False,
                "roadmap": False,
                "knowledge_base": False,
                "specialist_plans": False,
            }

        if complexity == "medium":
            return {
                "project_overview": True,
                "requirements": True,
                "technical_spec": False,
                "roadmap": False,
                "knowledge_base": False,
                "specialist_plans": False,
            }

        if complexity == "complex":
            return {
                "project_overview": True,
                "requirements": True,
                "technical_spec": True,
                "roadmap": True,
                "knowledge_base": False,
                "specialist_plans": False,  # All agents use shared planning documents
            }

        # Project level - full planning (shared by all agents)
        return {
            "project_overview": True,
            "requirements": True,
            "technical_spec": True,
            "roadmap": True,
            "knowledge_base": True,
            "specialist_plans": False,  # All agents collaborate on ONE shared plan
        }

    def _generate_reasoning(
        self,
        complexity: ComplexityLevel,
        estimated_steps: int,
        specialists: list[SpecialistDomain],
    ) -> str:
        """Generate human-readable reasoning for the analysis."""
        reasoning = f"Task assessed as {complexity} complexity. "
        reasoning += f"Estimated {estimated_steps} steps required. "

        if specialists:
            specialist_str = ", ".join(specialists)
            reasoning += f"Requires expertise in: {specialist_str}. "

        if complexity in ["complex", "project"]:
            reasoning += "Full planning documentation will be generated."
        elif complexity == "medium":
            reasoning += "Basic planning documentation will be generated."
        else:
            reasoning += "No planning documentation needed - direct execution."

        return reasoning
