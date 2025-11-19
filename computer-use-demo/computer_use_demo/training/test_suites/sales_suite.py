"""
Test Suite for Sales Agent.

This module contains test cases for evaluating the Sales specialist agent's
ability to qualify leads, handle objections, create proposals, close deals,
and develop sales strategies.
"""

from computer_use_demo.training import TestCase, TestSuite


def score_lead_qualification(output: str) -> float:
    """Score lead qualification assessment."""
    score = 0.0
    output_lower = output.lower()

    # BANT/qualification framework (25 points)
    bant_criteria = ["budget", "authority", "need", "timeline"]
    found_bant = sum(1 for criteria in bant_criteria if criteria in output_lower)
    score += min(25, found_bant * 6.25)

    # Assessment and analysis (20 points)
    if "qualify" in output_lower or "qualified" in output_lower:
        score += 10
    if "score" in output_lower or "rating" in output_lower or "priority" in output_lower:
        score += 10

    # Pain points identification (15 points)
    if "pain" in output_lower or "challenge" in output_lower or "problem" in output_lower:
        score += 10
    if "goal" in output_lower or "objective" in output_lower:
        score += 5

    # Next steps recommendation (15 points)
    if "next step" in output_lower or "recommend" in output_lower or "action" in output_lower:
        score += 10
    if "demo" in output_lower or "meeting" in output_lower or "call" in output_lower:
        score += 5

    # Decision makers (10 points)
    if "decision maker" in output_lower or "stakeholder" in output_lower:
        score += 5
    if "champion" in output_lower or "influencer" in output_lower:
        score += 5

    # Fit assessment (10 points)
    if "fit" in output_lower or "match" in output_lower or "suitable" in output_lower:
        score += 10

    # Red flags or concerns (5 points)
    if "risk" in output_lower or "concern" in output_lower or "red flag" in output_lower:
        score += 5

    return min(100, score)


def score_objection_handling(output: str) -> float:
    """Score objection handling response."""
    score = 0.0
    output_lower = output.lower()

    # Acknowledge objection (20 points)
    if "understand" in output_lower or "appreciate" in output_lower or "hear" in output_lower:
        score += 15
    if "concern" in output_lower or "valid" in output_lower:
        score += 5

    # Empathy and validation (15 points)
    if "common" in output_lower or "other" in output_lower or "many" in output_lower:
        score += 10
    if "perspective" in output_lower or "point" in output_lower:
        score += 5

    # Address with value (25 points)
    if "however" in output_lower or "actually" in output_lower or "fact" in output_lower:
        score += 10
    value_terms = ["benefit", "value", "save", "roi", "return", "advantage"]
    found_value = sum(1 for term in value_terms if term in output_lower)
    score += min(15, found_value * 5)

    # Evidence or proof (15 points)
    if "customer" in output_lower or "client" in output_lower or "company" in output_lower:
        score += 7.5
    if "result" in output_lower or "success" in output_lower or "example" in output_lower:
        score += 7.5

    # Question back (10 points)
    if "?" in output:
        score += 10

    # Next step (10 points)
    if "show" in output_lower or "demonstrate" in output_lower or "prove" in output_lower:
        score += 5
    if "try" in output_lower or "test" in output_lower or "pilot" in output_lower:
        score += 5

    # Positive tone (5 points)
    if len(output) > 200:  # Detailed response
        score += 5

    return min(100, score)


def score_sales_proposal(output: str) -> float:
    """Score sales proposal quality."""
    score = 0.0
    output_lower = output.lower()

    # Executive summary (15 points)
    if "summary" in output_lower or "overview" in output_lower:
        score += 10
    if "challenge" in output_lower or "problem" in output_lower:
        score += 5

    # Solution description (20 points)
    if "solution" in output_lower or "approach" in output_lower:
        score += 10
    if "feature" in output_lower or "capability" in output_lower or "benefit" in output_lower:
        score += 10

    # Pricing and packages (20 points)
    if "pricing" in output_lower or "price" in output_lower or "cost" in output_lower:
        score += 10
    if "$" in output or "package" in output_lower or "tier" in output_lower:
        score += 10

    # Value proposition (15 points)
    if "roi" in output_lower or "return" in output_lower:
        score += 7.5
    if "save" in output_lower or "increase" in output_lower or "improve" in output_lower:
        score += 7.5

    # Implementation plan (10 points)
    if "implementation" in output_lower or "onboarding" in output_lower:
        score += 5
    if "timeline" in output_lower or "phase" in output_lower or "step" in output_lower:
        score += 5

    # Social proof (10 points)
    if "customer" in output_lower or "client" in output_lower or "case study" in output_lower:
        score += 5
    if "testimonial" in output_lower or "success" in output_lower or "result" in output_lower:
        score += 5

    # Next steps/CTA (10 points)
    if "next" in output_lower or "action" in output_lower or "step" in output_lower:
        score += 10

    return min(100, score)


def score_closing_strategy(output: str) -> float:
    """Score deal closing strategy."""
    score = 0.0
    output_lower = output.lower()

    # Buying signals identification (20 points)
    if "signal" in output_lower or "indicator" in output_lower or "ready" in output_lower:
        score += 15
    if "interest" in output_lower or "engaged" in output_lower:
        score += 5

    # Closing technique (25 points)
    closing_techniques = [
        "assumptive close",
        "trial close",
        "summary close",
        "urgency",
        "scarcity",
    ]
    found_techniques = sum(1 for tech in closing_techniques if tech in output_lower)
    score += min(25, found_techniques * 8)
    if "close" in output_lower:
        score += 5

    # Address final concerns (20 points)
    if "concern" in output_lower or "question" in output_lower or "hesitation" in output_lower:
        score += 10
    if "risk" in output_lower or "guarantee" in output_lower or "commitment" in output_lower:
        score += 10

    # Create urgency (15 points)
    if "deadline" in output_lower or "limited" in output_lower or "offer" in output_lower:
        score += 10
    if "discount" in output_lower or "bonus" in output_lower or "incentive" in output_lower:
        score += 5

    # Ask for the business (15 points)
    if "decision" in output_lower or "move forward" in output_lower or "proceed" in output_lower:
        score += 10
    if "?" in output and (
        "ready" in output_lower or "when" in output_lower or "what" in output_lower
    ):
        score += 5

    # Handle objections (5 points)
    if "if" in output_lower or "concern" in output_lower:
        score += 5

    return min(100, score)


def score_sales_strategy(output: str) -> float:
    """Score sales strategy development."""
    score = 0.0
    output_lower = output.lower()

    # Target market definition (20 points)
    if "target" in output_lower or "market" in output_lower or "segment" in output_lower:
        score += 10
    if "icp" in output_lower or "ideal customer" in output_lower or "persona" in output_lower:
        score += 10

    # Sales process/methodology (20 points)
    methodologies = ["meddic", "spin", "challenger", "solution selling", "consultative"]
    if any(method in output_lower for method in methodologies):
        score += 10
    if "process" in output_lower or "stage" in output_lower or "funnel" in output_lower:
        score += 10

    # Channel strategy (15 points)
    channels = ["inbound", "outbound", "partner", "direct", "channel"]
    found_channels = sum(1 for channel in channels if channel in output_lower)
    score += min(15, found_channels * 5)

    # Metrics and KPIs (15 points)
    if "metric" in output_lower or "kpi" in output_lower or "measure" in output_lower:
        score += 7.5
    metrics = ["conversion", "pipeline", "deal size", "cycle time", "quota"]
    found_metrics = sum(1 for metric in metrics if metric in output_lower)
    score += min(7.5, found_metrics * 2.5)

    # Team structure (10 points)
    if "team" in output_lower or "role" in output_lower or "structure" in output_lower:
        score += 5
    if "sdr" in output_lower or "ae" in output_lower or "account executive" in output_lower:
        score += 5

    # Tools and technology (10 points)
    if "crm" in output_lower or "tool" in output_lower or "technology" in output_lower:
        score += 10

    # Competitive positioning (10 points)
    if "competitive" in output_lower or "differentiat" in output_lower:
        score += 5
    if "advantage" in output_lower or "unique" in output_lower or "position" in output_lower:
        score += 5

    return min(100, score)


def create_sales_test_suite() -> TestSuite:
    """Create comprehensive test suite for Sales agent."""
    suite = TestSuite(
        name="Sales Agent Tests",
        agent_type="sales",
        metadata={"version": "1.0", "created": "2025-01-19"},
    )

    # Test 1: Lead qualification
    suite.add_test(
        TestCase(
            name="Qualify Enterprise Lead",
            task="""Analyze this lead and provide qualification assessment:

Lead Information:
- Company: TechCorp Inc (5,000 employees)
- Contact: Sarah Johnson, VP of Engineering
- Request: Interested in project management solution for 200-person engineering team
- Current tool: Using Jira, frustrated with complexity
- Budget: Not yet discussed
- Timeline: Mentioned "need solution in next quarter"
- Pain points: Team struggling with cross-functional collaboration

Qualify this lead using BANT or similar framework. Assess fit, identify gaps in
information, and recommend next steps.""",
            success_criteria=score_lead_qualification,
            metadata={"difficulty": "medium", "category": "qualification"},
        )
    )

    # Test 2: Objection handling
    suite.add_test(
        TestCase(
            name="Handle Price Objection",
            task="""A prospect says: "Your solution is 2x more expensive than your competitor.
Why should we pay that much more?"

Craft a response that:
- Acknowledges the concern
- Positions value over price
- Provides evidence or examples
- Moves the conversation forward
- Maintains positive relationship

Write the response you would give to this prospect.""",
            success_criteria=score_objection_handling,
            metadata={"difficulty": "medium", "category": "objection_handling"},
        )
    )

    # Test 3: Sales proposal
    suite.add_test(
        TestCase(
            name="Create SaaS Sales Proposal",
            task="""Create a sales proposal for:

Prospect: MidMarket Corp
- 500 employees, currently using spreadsheets for project tracking
- Pain points: No visibility, missed deadlines, poor collaboration
- Budget: $50K-75K annually
- Decision makers: CTO and VP Operations
- Timeline: Want to start Q2

Your product: Project management SaaS ($30/user/month)

Include: Executive summary, solution overview, pricing packages, value proposition,
implementation plan, and next steps. Make it compelling and address their specific needs.""",
            success_criteria=score_sales_proposal,
            metadata={"difficulty": "hard", "category": "proposal"},
        )
    )

    # Test 4: Closing strategy
    suite.add_test(
        TestCase(
            name="Develop Deal Closing Strategy",
            task="""You're working on a $100K annual contract deal that's been in progress for 2 months.

Situation:
- Champion loves the product and has run a successful pilot
- CFO is concerned about ROI and timing
- Competitor is also being evaluated
- Fiscal year ends in 6 weeks
- All technical requirements are met

Develop a closing strategy that includes:
- How to identify buying signals
- Which closing technique(s) to use
- How to create appropriate urgency
- Addressing CFO concerns
- Handling potential last-minute objections

Provide specific tactics and talking points.""",
            success_criteria=score_closing_strategy,
            metadata={"difficulty": "hard", "category": "closing"},
        )
    )

    # Test 5: Sales strategy
    suite.add_test(
        TestCase(
            name="Design GTM Sales Strategy",
            task="""Design a go-to-market sales strategy for a new B2B SaaS product targeting
mid-market companies (100-1000 employees) in the HR/recruiting space.

Product: AI-powered candidate screening tool
Price: $5K-25K annually depending on company size
Market: Very competitive with established players

Create a comprehensive sales strategy covering:
- Target customer profile and segmentation
- Sales methodology and process
- Channel strategy (inbound/outbound mix)
- Team structure and roles
- Key metrics and goals
- Competitive positioning
- Tools and technology needs

Provide rationale for your recommendations.""",
            success_criteria=score_sales_strategy,
            metadata={"difficulty": "hard", "category": "strategy"},
        )
    )

    return suite


# Export the test suite
sales_suite = create_sales_test_suite()
