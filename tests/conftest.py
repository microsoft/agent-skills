"""
Pytest Configuration and Fixtures

Provides fixtures for skill evaluation testing.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from harness import (
    AcceptanceCriteriaLoader,
    CodeEvaluator,
    SkillEvaluationRunner,
)
from harness.copilot_client import SkillCopilotClient, GenerationConfig


@pytest.fixture(scope="session")
def base_path() -> Path:
    """Get the repository base path."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def criteria_loader(base_path: Path) -> AcceptanceCriteriaLoader:
    """Create a criteria loader for the test session."""
    return AcceptanceCriteriaLoader(base_path)


@pytest.fixture(scope="session")
def mock_runner(base_path: Path) -> SkillEvaluationRunner:
    """Create a mock runner for testing without Copilot SDK."""
    return SkillEvaluationRunner(
        base_path=base_path,
        use_mock=True,
        verbose=False,
    )


@pytest.fixture(scope="session")
def verbose_mock_runner(base_path: Path) -> SkillEvaluationRunner:
    """Create a verbose mock runner for debugging."""
    return SkillEvaluationRunner(
        base_path=base_path,
        use_mock=True,
        verbose=True,
    )


@pytest.fixture
def copilot_client(base_path: Path) -> SkillCopilotClient:
    """Create a mock Copilot client."""
    return SkillCopilotClient(base_path, use_mock=True)


@pytest.fixture
def generation_config() -> GenerationConfig:
    """Default generation configuration."""
    return GenerationConfig(
        model="gpt-4",
        max_tokens=2000,
        temperature=0.3,
    )


@pytest.fixture(scope="session")
def available_skills(criteria_loader: AcceptanceCriteriaLoader) -> list[str]:
    """List all skills with acceptance criteria."""
    return criteria_loader.list_skills_with_criteria()


# Parametrized fixtures for skill testing
def pytest_generate_tests(metafunc):
    """Generate test parameters for skill tests."""
    if "skill_name" in metafunc.fixturenames:
        # Only parametrize if the test requests it
        base_path = Path(__file__).parent.parent
        loader = AcceptanceCriteriaLoader(base_path)
        skills = loader.list_skills_with_criteria()

        if skills:
            metafunc.parametrize("skill_name", skills)


# Markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "requires_copilot: marks tests that require Copilot SDK")
    config.addinivalue_line("markers", "skill(name): marks test as testing a specific skill")
