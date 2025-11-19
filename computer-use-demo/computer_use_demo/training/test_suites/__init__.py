"""
Test Suites for Agent Training.

This module contains test suites for training and evaluating specialist agents.
Each test suite includes multiple test cases that assess different aspects
of an agent's capabilities.
"""

from .customer_success_suite import customer_success_suite
from .data_analyst_suite import data_analyst_suite
from .devops_suite import devops_suite
from .example_test_suite import product_manager_suite
from .qa_testing_suite import qa_testing_suite
from .sales_suite import sales_suite
from .senior_developer_suite import senior_developer_suite
from .technical_writer_suite import technical_writer_suite

__all__ = [
    "product_manager_suite",
    "qa_testing_suite",
    "devops_suite",
    "senior_developer_suite",
    "sales_suite",
    "customer_success_suite",
    "technical_writer_suite",
    "data_analyst_suite",
]
