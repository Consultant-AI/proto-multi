"""
Test Suites for Agent Training.

This module contains test suites for training and evaluating specialist agents.
Each test suite includes multiple test cases that assess different aspects
of an agent's capabilities.
"""

from .devops_suite import devops_suite
from .example_test_suite import product_manager_suite
from .qa_testing_suite import qa_testing_suite
from .senior_developer_suite import senior_developer_suite

__all__ = [
    "product_manager_suite",
    "qa_testing_suite",
    "devops_suite",
    "senior_developer_suite",
]
