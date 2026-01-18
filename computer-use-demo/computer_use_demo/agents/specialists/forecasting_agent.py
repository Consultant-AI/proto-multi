"""
Forecasting Agent.

Expertise in:
- Revenue forecasting
- Demand prediction
- Churn prediction
- Staffing forecasts
- Time series analysis
- Predictive modeling
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ForecastingAgent(BaseSpecialist):
    """Forecasting specialist focused on revenue, demand, churn, and staffing predictions."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize forecasting agent."""
        super().__init__(
            role="forecasting",
            name="Forecasting Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get forecasting domain expertise description."""
        return """Revenue forecasting, demand prediction, churn prediction, staffing forecasts,
time series analysis, predictive modeling, seasonality detection, trend analysis,
forecast accuracy measurement, scenario modeling, confidence intervals,
forecast communication, and forecast model selection."""
