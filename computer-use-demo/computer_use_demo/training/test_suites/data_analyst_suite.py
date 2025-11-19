"""
Test Suite for Data Analyst Agent.

This module contains test cases for evaluating the Data Analyst specialist agent's
ability to analyze data, create SQL queries, build dashboards, and provide insights.
"""

from computer_use_demo.training import TestCase, TestSuite


def score_sql_query(output: str) -> float:
    """Score SQL query quality."""
    score = 0.0
    output_lower = output.lower()

    # SELECT statement (20 points)
    if "select" in output_lower:
        score += 15
    if "*" in output or ("column" in output_lower or "field" in output_lower):
        score += 5

    # FROM clause (15 points)
    if "from" in output_lower:
        score += 10
    if "table" in output_lower or "join" in output_lower:
        score += 5

    # WHERE clause (15 points)
    if "where" in output_lower:
        score += 10
    if "and" in output_lower or "or" in output_lower:
        score += 5

    # Aggregation (15 points)
    agg_functions = ["count", "sum", "avg", "max", "min", "group by"]
    found_agg = sum(1 for func in agg_functions if func in output_lower)
    score += min(15, found_agg * 5)

    # JOIN operations (10 points)
    if "join" in output_lower:
        score += 10

    # ORDER BY (10 points)
    if "order by" in output_lower:
        score += 10

    # Comments/explanation (10 points)
    if "--" in output or "/*" in output or "explanation" in output_lower:
        score += 10

    # Proper formatting (5 points)
    if "\n" in output:  # Multi-line formatted
        score += 5

    return min(100, score)


def score_data_analysis(output: str) -> float:
    """Score data analysis quality."""
    score = 0.0
    output_lower = output.lower()

    # Key findings (25 points)
    if "finding" in output_lower or "insight" in output_lower or "discover" in output_lower:
        score += 15
    if "key" in output_lower or "important" in output_lower or "significant" in output_lower:
        score += 10

    # Data description (20 points)
    stat_terms = ["average", "median", "mean", "percentage", "total", "count"]
    found_stats = sum(1 for term in stat_terms if term in output_lower)
    score += min(20, found_stats * 4)

    # Trends and patterns (20 points)
    if "trend" in output_lower or "pattern" in output_lower or "correlation" in output_lower:
        score += 10
    if "increase" in output_lower or "decrease" in output_lower or "change" in output_lower:
        score += 10

    # Segmentation (15 points)
    if "segment" in output_lower or "group" in output_lower or "category" in output_lower:
        score += 10
    if "by" in output_lower:  # "by region", "by age", etc.
        score += 5

    # Actionable insights (15 points)
    if "recommend" in output_lower or "suggest" in output_lower or "should" in output_lower:
        score += 10
    if "action" in output_lower or "next step" in output_lower:
        score += 5

    # Data quality notes (5 points)
    if "limitation" in output_lower or "caveat" in output_lower or "note" in output_lower:
        score += 5

    return min(100, score)


def score_dashboard_design(output: str) -> float:
    """Score dashboard design quality."""
    score = 0.0
    output_lower = output.lower()

    # KPI definition (25 points)
    if "kpi" in output_lower or "metric" in output_lower or "measure" in output_lower:
        score += 15
    kpi_examples = ["revenue", "conversion", "retention", "churn", "growth"]
    found_kpis = sum(1 for kpi in kpi_examples if kpi in output_lower)
    score += min(10, found_kpis * 3)

    # Visualization types (20 points)
    viz_types = ["chart", "graph", "table", "pie", "bar", "line", "scatter"]
    found_viz = sum(1 for viz in viz_types if viz in output_lower)
    score += min(20, found_viz * 4)

    # Layout and organization (15 points)
    if "section" in output_lower or "layout" in output_lower or "organize" in output_lower:
        score += 10
    if "top" in output_lower or "left" in output_lower or "grid" in output_lower:
        score += 5

    # Filters and interactivity (15 points)
    if "filter" in output_lower or "dropdown" in output_lower or "select" in output_lower:
        score += 10
    if "interactive" in output_lower or "drill" in output_lower or "click" in output_lower:
        score += 5

    # Target audience consideration (10 points)
    if "executive" in output_lower or "user" in output_lower or "audience" in output_lower:
        score += 5
    if "simple" in output_lower or "clear" in output_lower or "easy" in output_lower:
        score += 5

    # Color and design (10 points)
    if "color" in output_lower or "visual" in output_lower or "design" in output_lower:
        score += 10

    # Update frequency (5 points)
    if "real-time" in output_lower or "daily" in output_lower or "refresh" in output_lower:
        score += 5

    return min(100, score)


def score_metric_definition(output: str) -> float:
    """Score metric definition quality."""
    score = 0.0
    output_lower = output.lower()

    # Clear definition (25 points)
    if "definition" in output_lower or "calculate" in output_lower or "formula" in output_lower:
        score += 15
    if "=" in output or "/" in output or "÷" in output:  # Formula notation
        score += 10

    # Purpose/why it matters (20 points)
    if "why" in output_lower or "purpose" in output_lower or "important" in output_lower:
        score += 10
    if "measure" in output_lower or "track" in output_lower or "monitor" in output_lower:
        score += 10

    # Target/benchmark (15 points)
    if "target" in output_lower or "goal" in output_lower or "benchmark" in output_lower:
        score += 10
    if "%" in output or "industry" in output_lower:
        score += 5

    # Data source (15 points)
    if "data" in output_lower or "source" in output_lower or "from" in output_lower:
        score += 10
    if "table" in output_lower or "database" in output_lower:
        score += 5

    # Interpretation guide (15 points)
    if "high" in output_lower or "low" in output_lower or "good" in output_lower:
        score += 7.5
    if "interpret" in output_lower or "mean" in output_lower:
        score += 7.5

    # Frequency of measurement (10 points)
    if "daily" in output_lower or "weekly" in output_lower or "monthly" in output_lower:
        score += 10

    return min(100, score)


def score_ab_test_analysis(output: str) -> float:
    """Score A/B test analysis quality."""
    score = 0.0
    output_lower = output.lower()

    # Hypothesis (15 points)
    if "hypothesis" in output_lower or "expected" in output_lower or "predict" in output_lower:
        score += 15

    # Sample size and duration (15 points)
    if "sample" in output_lower or "size" in output_lower:
        score += 7.5
    if "duration" in output_lower or "day" in output_lower or "week" in output_lower:
        score += 7.5

    # Results presentation (25 points)
    if "control" in output_lower and "variant" in output_lower:
        score += 15
    if "%" in output or "percentage" in output_lower or "rate" in output_lower:
        score += 10

    # Statistical significance (20 points)
    if "significant" in output_lower or "confidence" in output_lower:
        score += 10
    if "p-value" in output_lower or "statistical" in output_lower:
        score += 10

    # Winner declaration (10 points)
    if "winner" in output_lower or "better" in output_lower or "recommend" in output_lower:
        score += 10

    # Impact projection (10 points)
    if "impact" in output_lower or "revenue" in output_lower or "conversion" in output_lower:
        score += 10

    # Next steps (5 points)
    if "next" in output_lower or "action" in output_lower or "implement" in output_lower:
        score += 5

    return min(100, score)


def create_data_analyst_test_suite() -> TestSuite:
    """Create comprehensive test suite for Data Analyst agent."""
    suite = TestSuite(
        name="Data Analyst Agent Tests",
        agent_type="data-analyst",
        metadata={"version": "1.0", "created": "2025-01-19"},
    )

    # Test 1: SQL query
    suite.add_test(
        TestCase(
            name="Write SQL Query for User Engagement",
            task="""Write a SQL query to analyze user engagement with the following requirements:

Database schema:
- users table: user_id, email, signup_date, plan_type
- sessions table: session_id, user_id, start_time, end_time, page_views
- events table: event_id, user_id, event_type, timestamp

Goal: Find the top 10 most engaged users in the last 30 days

Engagement criteria:
- Number of sessions
- Total page views
- Number of events

Write a SQL query that:
- Calculates engagement score for each user
- Filters for last 30 days
- Returns top 10 users with their details
- Include comments explaining the logic""",
            success_criteria=score_sql_query,
            metadata={"difficulty": "medium", "category": "sql"},
        )
    )

    # Test 2: Data analysis
    suite.add_test(
        TestCase(
            name="Analyze Customer Churn Data",
            task="""Analyze this customer churn dataset and provide insights:

Data summary:
- Total customers: 1,000
- Churned in last quarter: 150 (15% churn rate)
- Churn by plan: Basic (25%), Pro (10%), Enterprise (5%)
- Churn by tenure: <3 months (30%), 3-12 months (15%), >12 months (8%)
- Churn by usage: Low usage (40%), Medium (12%), High (3%)
- Average customer lifetime: Basic (8 months), Pro (18 months), Enterprise (36 months)

Provide:
- Key findings from the data
- Trends and patterns you observe
- Customer segments most at risk
- Actionable recommendations to reduce churn
- Metrics to track improvement""",
            success_criteria=score_data_analysis,
            metadata={"difficulty": "hard", "category": "analysis"},
        )
    )

    # Test 3: Dashboard design
    suite.add_test(
        TestCase(
            name="Design Executive Dashboard",
            task="""Design a dashboard for company executives showing business health.

Requirements:
- Audience: C-level executives (non-technical)
- Update frequency: Daily
- Focus: High-level business metrics

Key metrics to include:
- Revenue (MRR, growth rate)
- Customer metrics (new, churned, total)
- Product usage (DAU, MAU, engagement)
- Sales pipeline (leads, conversion rate)

Deliverable: Dashboard design specification including:
- What KPIs to show (and why)
- Visualization types for each metric
- Layout and organization
- Filters and interactivity
- Color scheme and design principles
- Data sources""",
            success_criteria=score_dashboard_design,
            metadata={"difficulty": "hard", "category": "dashboard"},
        )
    )

    # Test 4: Metric definition
    suite.add_test(
        TestCase(
            name="Define Customer Lifetime Value Metric",
            task="""Define the "Customer Lifetime Value (CLV)" metric for a SaaS company.

Create a comprehensive metric definition including:
- Clear definition and calculation formula
- Why this metric matters for the business
- Target/benchmark values
- Data sources needed
- How to interpret high vs low values
- Frequency of measurement
- Related metrics to track alongside CLV
- Example calculation

Make it clear enough for non-technical stakeholders to understand.""",
            success_criteria=score_metric_definition,
            metadata={"difficulty": "medium", "category": "metrics"},
        )
    )

    # Test 5: A/B test analysis
    suite.add_test(
        TestCase(
            name="Analyze A/B Test Results",
            task="""Analyze the results of this A/B test:

Test: New checkout flow vs current flow
Duration: 14 days
Sample size: 10,000 users per variant

Results:
Control (current flow):
- Conversion rate: 12.5%
- Average order value: $85
- Cart abandonment: 45%

Variant (new flow):
- Conversion rate: 14.2%
- Average order value: $82
- Cart abandonment: 38%

Additional data:
- p-value: 0.02 (95% confidence level)
- Estimated annual impact: +$340K revenue

Provide:
- Clear summary of results
- Statistical significance assessment
- Winner recommendation
- Expected business impact
- Any concerns or caveats
- Next steps and recommendations""",
            success_criteria=score_ab_test_analysis,
            metadata={"difficulty": "medium", "category": "ab_testing"},
        )
    )

    return suite


# Export the test suite
data_analyst_suite = create_data_analyst_test_suite()
