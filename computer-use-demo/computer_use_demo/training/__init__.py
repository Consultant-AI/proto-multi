"""
Training Infrastructure for Proto Multi-Agent System.

Provides automated testing, scoring, and training capabilities
for specialist agents.
"""

from .harness import TrainingHarness
from .test_case import TestCase, TestResult, TestSuite

__all__ = [
    "TrainingHarness",
    "TestCase",
    "TestResult",
    "TestSuite",
]
