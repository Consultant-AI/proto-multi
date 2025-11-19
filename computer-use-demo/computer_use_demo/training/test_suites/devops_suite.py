"""
Test Suite for DevOps Agent.

This module contains test cases for evaluating the DevOps specialist agent's
ability to handle infrastructure, CI/CD, deployment, monitoring, and automation tasks.
"""

from computer_use_demo.training import TestCase, TestSuite


def score_cicd_pipeline(output: str) -> float:
    """Score CI/CD pipeline design."""
    score = 0.0
    output_lower = output.lower()

    # Pipeline stages (25 points)
    stages = ["build", "test", "deploy"]
    found_stages = sum(1 for stage in stages if stage in output_lower)
    score += found_stages * 8.33

    # Testing integration (20 points)
    if "unit test" in output_lower or "test" in output_lower:
        score += 10
    if "integration test" in output_lower or "e2e" in output_lower:
        score += 10

    # Artifact management (15 points)
    if "artifact" in output_lower or "docker" in output_lower or "container" in output_lower:
        score += 10
    if "registry" in output_lower or "repository" in output_lower:
        score += 5

    # Environment deployment (15 points)
    envs = ["dev", "staging", "production"]
    found_envs = sum(1 for env in envs if env in output_lower)
    score += found_envs * 5

    # Automation and triggers (10 points)
    if "trigger" in output_lower or "webhook" in output_lower or "automatic" in output_lower:
        score += 5
    if "branch" in output_lower or "pull request" in output_lower or "merge" in output_lower:
        score += 5

    # Security and quality gates (10 points)
    if "security scan" in output_lower or "vulnerability" in output_lower:
        score += 5
    if "quality gate" in output_lower or "code coverage" in output_lower or "linting" in output_lower:
        score += 5

    # Rollback and error handling (5 points)
    if "rollback" in output_lower or "fail" in output_lower or "error" in output_lower:
        score += 5

    return min(100, score)


def score_infrastructure(output: str) -> float:
    """Score infrastructure as code."""
    score = 0.0
    output_lower = output.lower()

    # IaC tool usage (20 points)
    iac_tools = ["terraform", "cloudformation", "pulumi", "ansible"]
    if any(tool in output_lower for tool in iac_tools):
        score += 20

    # Resource definitions (25 points)
    resources = ["vpc", "subnet", "ec2", "instance", "load balancer", "database", "rds"]
    found_resources = sum(1 for res in resources if res in output_lower)
    score += min(25, found_resources * 5)

    # Network configuration (15 points)
    if "security group" in output_lower or "firewall" in output_lower:
        score += 7.5
    if "network" in output_lower or "cidr" in output_lower:
        score += 7.5

    # Scalability (15 points)
    if "auto scaling" in output_lower or "scale" in output_lower:
        score += 10
    if "high availability" in output_lower or "ha" in output_lower or "redundancy" in output_lower:
        score += 5

    # State management (10 points)
    if "state" in output_lower or "backend" in output_lower:
        score += 10

    # Variables and modularity (10 points)
    if "variable" in output_lower or "var" in output_lower or "parameter" in output_lower:
        score += 5
    if "module" in output_lower or "reusable" in output_lower:
        score += 5

    # Documentation (5 points)
    if len(output) > 500 or "comment" in output_lower or "documentation" in output_lower:
        score += 5

    return min(100, score)


def score_monitoring_setup(output: str) -> float:
    """Score monitoring and alerting setup."""
    score = 0.0
    output_lower = output.lower()

    # Monitoring tools (20 points)
    tools = ["prometheus", "grafana", "cloudwatch", "datadog", "new relic", "elk"]
    if any(tool in output_lower for tool in tools):
        score += 20

    # Metrics collection (25 points)
    metrics = ["cpu", "memory", "disk", "network", "latency", "throughput", "error rate"]
    found_metrics = sum(1 for metric in metrics if metric in output_lower)
    score += min(25, found_metrics * 4)

    # Alerting (20 points)
    if "alert" in output_lower or "notification" in output_lower:
        score += 10
    if "threshold" in output_lower or "trigger" in output_lower:
        score += 5
    if "slack" in output_lower or "email" in output_lower or "pagerduty" in output_lower:
        score += 5

    # Dashboard creation (15 points)
    if "dashboard" in output_lower or "visualization" in output_lower:
        score += 10
    if "graph" in output_lower or "chart" in output_lower or "panel" in output_lower:
        score += 5

    # Log aggregation (10 points)
    if "log" in output_lower or "logging" in output_lower:
        score += 5
    if "centralized" in output_lower or "aggregat" in output_lower:
        score += 5

    # Health checks (10 points)
    if "health check" in output_lower or "healthcheck" in output_lower or "probe" in output_lower:
        score += 10

    return min(100, score)


def score_deployment_strategy(output: str) -> float:
    """Score deployment strategy."""
    score = 0.0
    output_lower = output.lower()

    # Strategy type (25 points)
    strategies = ["blue-green", "canary", "rolling", "recreate"]
    found_strategies = sum(1 for s in strategies if s in output_lower)
    score += min(25, found_strategies * 12.5)

    # Zero downtime approach (20 points)
    if "zero downtime" in output_lower or "no downtime" in output_lower:
        score += 15
    if "gradual" in output_lower or "progressive" in output_lower:
        score += 5

    # Traffic management (15 points)
    if "traffic" in output_lower or "routing" in output_lower:
        score += 10
    if "percentage" in output_lower or "%" in output:
        score += 5

    # Rollback plan (20 points)
    if "rollback" in output_lower:
        score += 15
    if "automatic" in output_lower and "rollback" in output_lower:
        score += 5

    # Health monitoring (10 points)
    if "monitor" in output_lower or "health" in output_lower:
        score += 5
    if "metric" in output_lower or "error rate" in output_lower:
        score += 5

    # Risk mitigation (10 points)
    if "risk" in output_lower or "safe" in output_lower:
        score += 5
    if "test" in output_lower or "validation" in output_lower:
        score += 5

    return min(100, score)


def score_incident_response(output: str) -> float:
    """Score incident response plan."""
    score = 0.0
    output_lower = output.lower()

    # Detection and alerting (20 points)
    if "detect" in output_lower or "alert" in output_lower or "monitor" in output_lower:
        score += 10
    if "escalation" in output_lower or "on-call" in output_lower:
        score += 10

    # Response steps (25 points)
    if "step" in output_lower or "action" in output_lower:
        score += 10
    if "triage" in output_lower or "assess" in output_lower:
        score += 7.5
    if "mitigate" in output_lower or "resolve" in output_lower:
        score += 7.5

    # Communication plan (20 points)
    if "communication" in output_lower or "notify" in output_lower:
        score += 10
    if "stakeholder" in output_lower or "customer" in output_lower:
        score += 5
    if "status" in output_lower or "update" in output_lower:
        score += 5

    # Investigation and root cause (15 points)
    if "root cause" in output_lower or "rca" in output_lower:
        score += 10
    if "investigate" in output_lower or "analysis" in output_lower:
        score += 5

    # Documentation (10 points)
    if "document" in output_lower or "log" in output_lower or "record" in output_lower:
        score += 5
    if "postmortem" in output_lower or "post-mortem" in output_lower:
        score += 5

    # Prevention (10 points)
    if "prevent" in output_lower or "improve" in output_lower:
        score += 5
    if "action item" in output_lower or "follow-up" in output_lower:
        score += 5

    return min(100, score)


def create_devops_test_suite() -> TestSuite:
    """Create comprehensive test suite for DevOps agent."""
    suite = TestSuite(
        name="DevOps Agent Tests",
        agent_type="devops",
        metadata={"version": "1.0", "created": "2025-01-19"},
    )

    # Test 1: CI/CD pipeline
    suite.add_test(
        TestCase(
            name="Design CI/CD Pipeline for Node.js App",
            task="""Design a CI/CD pipeline for a Node.js web application that:
        - Runs on GitHub Actions
        - Includes unit tests, integration tests, and linting
        - Builds Docker images
        - Deploys to AWS (dev, staging, production environments)
        - Includes security scanning and quality gates

        Provide the pipeline configuration with all stages and explain each step.""",
            success_criteria=score_cicd_pipeline,
            metadata={"difficulty": "medium", "category": "cicd"},
        )
    )

    # Test 2: Infrastructure as code
    suite.add_test(
        TestCase(
            name="Create Infrastructure for Web Application",
            task="""Write Terraform code to provision infrastructure for a web application on AWS:
        - VPC with public and private subnets
        - Auto-scaling group for web servers
        - Application Load Balancer
        - RDS PostgreSQL database
        - Security groups with appropriate rules

        Include variables, outputs, and comments explaining the setup.""",
            success_criteria=score_infrastructure,
            metadata={"difficulty": "hard", "category": "infrastructure"},
        )
    )

    # Test 3: Monitoring setup
    suite.add_test(
        TestCase(
            name="Setup Monitoring and Alerting",
            task="""Design a comprehensive monitoring and alerting strategy for a production microservices application:
        - Define key metrics to track (infrastructure and application)
        - Recommend monitoring tools and setup
        - Create alerting rules with thresholds
        - Design dashboards for different audiences (ops, devs, business)
        - Include log aggregation approach

        Explain your choices and provide configuration examples.""",
            success_criteria=score_monitoring_setup,
            metadata={"difficulty": "medium", "category": "monitoring"},
        )
    )

    # Test 4: Deployment strategy
    suite.add_test(
        TestCase(
            name="Design Zero-Downtime Deployment Strategy",
            task="""Propose a zero-downtime deployment strategy for a high-traffic e-commerce application:
        - The application receives 10,000 requests per minute
        - Database schema changes are required
        - Need to minimize risk of issues affecting customers
        - Must be able to quickly rollback if problems occur

        Recommend a deployment strategy (blue-green, canary, rolling, etc.) and
        explain the implementation approach, rollback plan, and monitoring.""",
            success_criteria=score_deployment_strategy,
            metadata={"difficulty": "hard", "category": "deployment"},
        )
    )

    # Test 5: Incident response
    suite.add_test(
        TestCase(
            name="Create Incident Response Runbook",
            task="""Create an incident response runbook for a production outage scenario where
        the application becomes slow (response times >5 seconds) during peak hours.

        Include:
        - Detection and initial response steps
        - Triage checklist
        - Investigation procedures
        - Mitigation actions
        - Communication plan
        - Root cause analysis approach
        - Post-incident activities

        Make it actionable for on-call engineers.""",
            success_criteria=score_incident_response,
            metadata={"difficulty": "medium", "category": "incident_response"},
        )
    )

    return suite


# Export the test suite
devops_suite = create_devops_test_suite()
