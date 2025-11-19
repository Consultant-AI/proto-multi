"""
Test Suite for Customer Success Agent.

This module contains test cases for evaluating the Customer Success specialist agent's
ability to onboard customers, drive adoption, handle escalations, prevent churn,
and grow accounts.
"""

from computer_use_demo.training import TestCase, TestSuite


def score_onboarding_plan(output: str) -> float:
    """Score customer onboarding plan."""
    score = 0.0
    output_lower = output.lower()

    # Onboarding phases (25 points)
    phases = ["kickoff", "setup", "training", "launch", "adoption"]
    found_phases = sum(1 for phase in phases if phase in output_lower)
    score += min(25, found_phases * 6.25)

    # Timeline and milestones (20 points)
    if "timeline" in output_lower or "schedule" in output_lower:
        score += 10
    if "milestone" in output_lower or "goal" in output_lower or "target" in output_lower:
        score += 10

    # Success criteria (15 points)
    if "success" in output_lower or "criteria" in output_lower or "metric" in output_lower:
        score += 10
    if "kpi" in output_lower or "measure" in output_lower:
        score += 5

    # Stakeholder engagement (15 points)
    if "stakeholder" in output_lower or "champion" in output_lower:
        score += 7.5
    if "executive" in output_lower or "sponsor" in output_lower:
        score += 7.5

    # Training and enablement (15 points)
    if "training" in output_lower or "documentation" in output_lower:
        score += 10
    if "workshop" in output_lower or "session" in output_lower or "webinar" in output_lower:
        score += 5

    # Risk mitigation (10 points)
    if "risk" in output_lower or "challenge" in output_lower or "blocker" in output_lower:
        score += 10

    return min(100, score)


def score_adoption_strategy(output: str) -> float:
    """Score product adoption strategy."""
    score = 0.0
    output_lower = output.lower()

    # Usage analysis (20 points)
    if "usage" in output_lower or "adoption" in output_lower or "engagement" in output_lower:
        score += 10
    if "data" in output_lower or "analytics" in output_lower or "metric" in output_lower:
        score += 10

    # Barriers identification (20 points)
    if "barrier" in output_lower or "challenge" in output_lower or "obstacle" in output_lower:
        score += 10
    if "reason" in output_lower or "why" in output_lower or "cause" in output_lower:
        score += 10

    # Engagement tactics (25 points)
    tactics = ["training", "webinar", "workshop", "check-in", "email", "campaign"]
    found_tactics = sum(1 for tactic in tactics if tactic in output_lower)
    score += min(25, found_tactics * 5)

    # Value demonstration (15 points)
    if "value" in output_lower or "benefit" in output_lower or "roi" in output_lower:
        score += 10
    if "success" in output_lower or "win" in output_lower or "result" in output_lower:
        score += 5

    # Feature adoption (10 points)
    if "feature" in output_lower or "capability" in output_lower:
        score += 5
    if "advanced" in output_lower or "power user" in output_lower:
        score += 5

    # Measurement plan (10 points)
    if "measure" in output_lower or "track" in output_lower or "monitor" in output_lower:
        score += 10

    return min(100, score)


def score_escalation_response(output: str) -> float:
    """Score customer escalation handling."""
    score = 0.0
    output_lower = output.lower()

    # Immediate acknowledgment (20 points)
    if "understand" in output_lower or "appreciate" in output_lower or "sorry" in output_lower:
        score += 15
    if "urgency" in output_lower or "priority" in output_lower or "immediately" in output_lower:
        score += 5

    # Ownership and accountability (20 points)
    if "own" in output_lower or "responsible" in output_lower or "personally" in output_lower:
        score += 10
    if "ensure" in output_lower or "commit" in output_lower or "guarantee" in output_lower:
        score += 10

    # Action plan (25 points)
    if "plan" in output_lower or "action" in output_lower or "step" in output_lower:
        score += 15
    if "timeline" in output_lower or "by" in output or "when" in output_lower:
        score += 10

    # Stakeholder communication (15 points)
    if "update" in output_lower or "communicate" in output_lower or "inform" in output_lower:
        score += 10
    if "regular" in output_lower or "frequent" in output_lower or "daily" in output_lower:
        score += 5

    # Root cause and prevention (10 points)
    if "root cause" in output_lower or "why" in output_lower or "prevent" in output_lower:
        score += 10

    # Relationship preservation (10 points)
    if "relationship" in output_lower or "trust" in output_lower or "partnership" in output_lower:
        score += 5
    if "value" in output_lower or "important" in output_lower:
        score += 5

    return min(100, score)


def score_churn_prevention(output: str) -> float:
    """Score churn prevention strategy."""
    score = 0.0
    output_lower = output.lower()

    # Risk indicators identification (25 points)
    risk_signals = [
        "usage decline",
        "low engagement",
        "support ticket",
        "complaint",
        "champion left",
    ]
    found_signals = sum(1 for signal in risk_signals if signal in output_lower)
    score += min(15, found_signals * 5)
    if "risk" in output_lower or "signal" in output_lower or "indicator" in output_lower:
        score += 10

    # Intervention tactics (25 points)
    if "reach out" in output_lower or "contact" in output_lower or "call" in output_lower:
        score += 10
    if "meeting" in output_lower or "review" in output_lower or "check-in" in output_lower:
        score += 10
    if "executive" in output_lower or "escalate" in output_lower:
        score += 5

    # Value reinforcement (20 points)
    if "value" in output_lower or "roi" in output_lower or "benefit" in output_lower:
        score += 10
    if "success" in output_lower or "win" in output_lower or "achievement" in output_lower:
        score += 10

    # Problem resolution (15 points)
    if "issue" in output_lower or "problem" in output_lower or "concern" in output_lower:
        score += 10
    if "resolve" in output_lower or "fix" in output_lower or "address" in output_lower:
        score += 5

    # Retention incentives (10 points)
    if "discount" in output_lower or "offer" in output_lower or "incentive" in output_lower:
        score += 5
    if "upgrade" in output_lower or "additional" in output_lower:
        score += 5

    # Timeline and urgency (5 points)
    if "immediately" in output_lower or "asap" in output_lower or "urgent" in output_lower:
        score += 5

    return min(100, score)


def score_account_growth(output: str) -> float:
    """Score account expansion/growth strategy."""
    score = 0.0
    output_lower = output.lower()

    # Opportunity identification (25 points)
    if "opportunity" in output_lower or "potential" in output_lower:
        score += 10
    opportunities = [
        "upsell",
        "cross-sell",
        "expansion",
        "additional users",
        "new features",
    ]
    found_opps = sum(1 for opp in opportunities if opp in output_lower)
    score += min(15, found_opps * 5)

    # Customer health assessment (20 points)
    if "health" in output_lower or "satisfaction" in output_lower or "nps" in output_lower:
        score += 10
    if "successful" in output_lower or "value" in output_lower or "roi" in output_lower:
        score += 10

    # Expansion approach (20 points)
    if "approach" in output_lower or "strategy" in output_lower or "plan" in output_lower:
        score += 10
    if "timing" in output_lower or "when" in output_lower or "ready" in output_lower:
        score += 10

    # Value proposition (15 points)
    if "benefit" in output_lower or "value" in output_lower or "return" in output_lower:
        score += 10
    if "case study" in output_lower or "success story" in output_lower or "example" in output_lower:
        score += 5

    # Stakeholder alignment (10 points)
    if "stakeholder" in output_lower or "decision maker" in output_lower:
        score += 5
    if "champion" in output_lower or "sponsor" in output_lower:
        score += 5

    # Metrics and goals (10 points)
    if "goal" in output_lower or "target" in output_lower or "revenue" in output_lower:
        score += 10

    return min(100, score)


def create_customer_success_test_suite() -> TestSuite:
    """Create comprehensive test suite for Customer Success agent."""
    suite = TestSuite(
        name="Customer Success Agent Tests",
        agent_type="customer-success",
        metadata={"version": "1.0", "created": "2025-01-19"},
    )

    # Test 1: Onboarding plan
    suite.add_test(
        TestCase(
            name="Create Enterprise Onboarding Plan",
            task="""Create a comprehensive onboarding plan for a new enterprise customer:

Customer: FinanceHub Corp
- 500 employees, purchasing 200 licenses
- Complex integration requirements (Salesforce, Slack, SSO)
- Executive sponsor: CTO (very engaged)
- Users: Sales (100), Support (50), Product (50)
- Previous tool: Legacy custom-built system
- Timeline: Want to be live in 60 days

Create a detailed onboarding plan covering:
- Phases and timeline
- Key milestones and success criteria
- Training and enablement approach
- Stakeholder engagement strategy
- Risk mitigation
- Success metrics

Make it actionable and comprehensive.""",
            success_criteria=score_onboarding_plan,
            metadata={"difficulty": "hard", "category": "onboarding"},
        )
    )

    # Test 2: Adoption strategy
    suite.add_test(
        TestCase(
            name="Increase Product Adoption",
            task="""Develop a strategy to increase adoption for an existing customer:

Current State:
- Customer for 6 months, 100 licenses
- Only 45 users are active (45% adoption)
- Average session time: 10 minutes (healthy users do 30+ minutes)
- Not using advanced features (only basic functionality)
- Support tickets are low (good sign or bad?)
- Renewal in 6 months

Goal: Increase to 80% active users and drive advanced feature adoption

Create a detailed adoption strategy including:
- Analysis of current barriers
- Engagement tactics to increase usage
- Feature adoption roadmap
- Success metrics and timeline
- Risk mitigation for renewal""",
            success_criteria=score_adoption_strategy,
            metadata={"difficulty": "hard", "category": "adoption"},
        )
    )

    # Test 3: Escalation handling
    suite.add_test(
        TestCase(
            name="Handle Critical Customer Escalation",
            task="""Handle this escalation:

Email from customer's CEO:
"Our team has been experiencing major performance issues with your platform for the past week.
This is costing us thousands of dollars daily in lost productivity. We've submitted multiple
support tickets but haven't seen resolution. If this isn't fixed by Friday, we'll need to
explore alternatives. This is unacceptable for a tool we're paying $100K/year for."

Current context:
- Customer is normally very happy (NPS 9)
- Engineering team is aware, working on fix (ETA: 3 days)
- Account is up for renewal in 2 months
- No other recent issues

Draft a response and outline your immediate action plan to:
- De-escalate the situation
- Restore trust and confidence
- Prevent churn
- Turn this into a positive outcome""",
            success_criteria=score_escalation_response,
            metadata={"difficulty": "hard", "category": "escalation"},
        )
    )

    # Test 4: Churn prevention
    suite.add_test(
        TestCase(
            name="Develop Churn Prevention Plan",
            task="""A customer is showing churn risk signals:

Customer: TechStart Inc (paying $50K/year)
- Renewal date: 45 days away
- Recent activity: Usage down 40% over last 2 months
- Champion (original buyer) left company 3 months ago
- New champion seems less engaged
- Haven't responded to last 2 check-in emails
- Support tickets up 3x (mostly "how do I..." questions)
- Haven't attended last 3 webinars (used to be regular attendees)

Develop a comprehensive churn prevention strategy:
- Assessment of churn risk level
- Root cause analysis
- Immediate intervention tactics
- Value reinforcement approach
- Stakeholder engagement plan
- Timeline and milestones
- Escalation if needed""",
            success_criteria=score_churn_prevention,
            metadata={"difficulty": "hard", "category": "retention"},
        )
    )

    # Test 5: Account expansion
    suite.add_test(
        TestCase(
            name="Identify and Execute Account Growth",
            task="""Develop an account expansion strategy for a healthy customer:

Customer: MarketCo
- Current: 50 licenses at $200/seat = $10K/year
- Health score: 95/100 (excellent)
- NPS: 10 (promoter)
- Usage: 90% adoption, heavy use of advanced features
- Champion is very happy and influential (VP Marketing)
- Company is growing fast (doubled headcount in last year)
- Recently asked about features only in higher tier plan
- Has referred 2 new customers to us

Potential opportunities:
1. Expand to 100 users (Sales team could use it)
2. Upgrade to Pro tier ($300/seat, includes AI features)
3. Add-on: Advanced analytics module ($5K/year)

Create an expansion strategy including:
- Opportunity prioritization and rationale
- Customer health/readiness assessment
- Approach and timing
- Value proposition for each opportunity
- Expected revenue impact
- Risk mitigation""",
            success_criteria=score_account_growth,
            metadata={"difficulty": "medium", "category": "expansion"},
        )
    )

    return suite


# Export the test suite
customer_success_suite = create_customer_success_test_suite()
