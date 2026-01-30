"""
Skill Evaluation Harness

A test framework for evaluating AI-generated code against acceptance criteria
defined in skill files. Uses the GitHub Copilot SDK to generate code and
validates it against patterns from acceptance criteria documents.

Architecture:
    - Skills live in .github/skills/<skill-name>/
    - Acceptance criteria in .github/skills/<skill-name>/references/acceptance-criteria.md
    - Test scenarios in tests/scenarios/<skill-name>/scenarios.yaml
    - Harness reads criteria, generates code via Copilot SDK, validates output

Usage:
    pytest tests/ -k "azure-ai-agents-py"
    python -m tests.harness.runner --skill azure-ai-agents-py
"""

from .criteria_loader import AcceptanceCriteriaLoader
from .evaluator import CodeEvaluator, EvaluationResult
from .runner import SkillEvaluationRunner

__all__ = [
    "AcceptanceCriteriaLoader",
    "CodeEvaluator", 
    "EvaluationResult",
    "SkillEvaluationRunner",
]
