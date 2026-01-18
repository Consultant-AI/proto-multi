"""
ML Engineer Agent.

Expertise in:
- Model training
- Model evaluation
- Model deployment
- Feature engineering
- MLOps
- Model monitoring
"""

from typing import Any

from .base_specialist import BaseSpecialist


class MLEngineerAgent(BaseSpecialist):
    """ML Engineer specialist focused on models, training, evaluation, and deployment."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize ML engineer agent."""
        super().__init__(
            role="ml-engineer",
            name="ML Engineer Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get ML engineer domain expertise description."""
        return """Model training, model evaluation, model deployment, feature engineering,
MLOps practices, model monitoring, experiment tracking (MLflow, Weights & Biases),
model versioning, A/B testing ML models, model serving, batch inference,
real-time inference, model optimization, and model governance."""
