"""
Growth Engine.

Marketing automation and analytics.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import (
    Campaign,
    CampaignStatus,
)


class GrowthEngine:
    """
    Growth and marketing automation engine.

    Features:
    - Campaign management
    - Marketing analytics
    - Lead scoring
    - A/B testing
    """

    def __init__(self, data_dir: Path | None = None):
        self._data_dir = data_dir or Path.home() / ".proto" / "company" / "business" / "growth"
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._campaigns: dict[str, Campaign] = {}
        self._metrics: dict[str, dict[str, float]] = {}

        self._load()

    def _load(self) -> None:
        """Load data from disk."""
        campaigns_file = self._data_dir / "campaigns.json"
        if campaigns_file.exists():
            try:
                with open(campaigns_file, "r") as f:
                    data = json.load(f)
                for camp in data:
                    c = Campaign(
                        id=camp["id"],
                        name=camp["name"],
                        type=camp.get("type", ""),
                        status=CampaignStatus(camp.get("status", "draft")),
                        budget=camp.get("budget", 0),
                    )
                    self._campaigns[c.id] = c
            except Exception:
                pass

    def _save(self) -> None:
        """Save data to disk."""
        campaigns_file = self._data_dir / "campaigns.json"
        with open(campaigns_file, "w") as f:
            json.dump(
                [
                    {
                        "id": c.id,
                        "name": c.name,
                        "type": c.type,
                        "status": c.status.value,
                        "budget": c.budget,
                    }
                    for c in self._campaigns.values()
                ],
                f, indent=2
            )

    # Campaign operations

    async def create_campaign(
        self,
        name: str,
        campaign_type: str,
        budget: float = 0.0,
        description: str = "",
        target_audience: dict[str, Any] | None = None,
    ) -> Campaign:
        """Create a new marketing campaign."""
        campaign = Campaign(
            name=name,
            type=campaign_type,
            description=description,
            budget=budget,
            target_audience=target_audience or {},
        )

        self._campaigns[campaign.id] = campaign
        self._save()

        print(f"[Growth] Created campaign: {name}")
        return campaign

    async def get_campaign(self, campaign_id: str) -> Campaign | None:
        """Get a campaign by ID."""
        return self._campaigns.get(campaign_id)

    async def list_campaigns(
        self,
        status: CampaignStatus | None = None,
        campaign_type: str | None = None,
    ) -> list[Campaign]:
        """List campaigns with optional filters."""
        campaigns = list(self._campaigns.values())

        if status:
            campaigns = [c for c in campaigns if c.status == status]
        if campaign_type:
            campaigns = [c for c in campaigns if c.type == campaign_type]

        return campaigns

    async def start_campaign(self, campaign_id: str) -> bool:
        """Start a campaign."""
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return False

        campaign.status = CampaignStatus.ACTIVE
        campaign.start_date = datetime.utcnow()
        self._save()

        print(f"[Growth] Started campaign: {campaign.name}")
        return True

    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a campaign."""
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return False

        campaign.status = CampaignStatus.PAUSED
        self._save()

        print(f"[Growth] Paused campaign: {campaign.name}")
        return True

    async def complete_campaign(self, campaign_id: str) -> bool:
        """Mark a campaign as completed."""
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return False

        campaign.status = CampaignStatus.COMPLETED
        campaign.end_date = datetime.utcnow()
        self._save()

        print(f"[Growth] Completed campaign: {campaign.name}")
        return True

    async def record_metric(
        self,
        campaign_id: str,
        metric_name: str,
        value: float,
    ) -> None:
        """Record a campaign metric."""
        if campaign_id not in self._metrics:
            self._metrics[campaign_id] = {}

        self._metrics[campaign_id][metric_name] = value

        # Update campaign metrics
        campaign = self._campaigns.get(campaign_id)
        if campaign:
            campaign.metrics[metric_name] = value

    async def record_spend(
        self,
        campaign_id: str,
        amount: float,
    ) -> None:
        """Record campaign spending."""
        campaign = self._campaigns.get(campaign_id)
        if campaign:
            campaign.spent += amount
            self._save()

    # Analytics

    def get_campaign_metrics(self, campaign_id: str) -> dict[str, float]:
        """Get metrics for a campaign."""
        return self._metrics.get(campaign_id, {})

    def get_campaign_roi(self, campaign_id: str) -> float | None:
        """Calculate ROI for a campaign."""
        campaign = self._campaigns.get(campaign_id)
        if not campaign or campaign.spent == 0:
            return None

        revenue = campaign.metrics.get("revenue", 0)
        return (revenue - campaign.spent) / campaign.spent

    def get_marketing_report(self) -> dict[str, Any]:
        """Generate a marketing report."""
        campaigns = list(self._campaigns.values())
        active = [c for c in campaigns if c.status == CampaignStatus.ACTIVE]
        completed = [c for c in campaigns if c.status == CampaignStatus.COMPLETED]

        total_budget = sum(c.budget for c in campaigns)
        total_spent = sum(c.spent for c in campaigns)
        total_revenue = sum(c.metrics.get("revenue", 0) for c in campaigns)

        return {
            "total_campaigns": len(campaigns),
            "active_campaigns": len(active),
            "completed_campaigns": len(completed),
            "total_budget": total_budget,
            "total_spent": total_spent,
            "total_revenue": total_revenue,
            "overall_roi": (total_revenue - total_spent) / total_spent if total_spent > 0 else 0,
        }

    # Lead scoring (placeholder)

    async def score_lead(
        self,
        lead_data: dict[str, Any],
    ) -> float:
        """
        Score a lead based on various factors.

        Returns a score from 0-100.
        """
        score = 50.0  # Base score

        # Company size factor
        company_size = lead_data.get("company_size", "")
        size_scores = {"enterprise": 20, "medium": 15, "small": 10, "startup": 5}
        score += size_scores.get(company_size, 0)

        # Engagement factor
        interactions = lead_data.get("interaction_count", 0)
        score += min(interactions * 2, 20)

        # Budget factor
        budget = lead_data.get("budget", 0)
        if budget > 100000:
            score += 15
        elif budget > 50000:
            score += 10
        elif budget > 10000:
            score += 5

        return min(score, 100)


# Global instance
_growth_engine: GrowthEngine | None = None


def get_growth_engine() -> GrowthEngine:
    """Get or create the global growth engine."""
    global _growth_engine
    if _growth_engine is None:
        _growth_engine = GrowthEngine()
    return _growth_engine
