"""
Skill Evaluation Tests

Pytest tests for evaluating AI-generated code against skill acceptance criteria.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from tests.harness import (
    AcceptanceCriteriaLoader,
    CodeEvaluator,
    EvaluationResult,
    SkillEvaluationRunner,
)
from tests.harness.copilot_client import SkillCopilotClient
from tests.harness.reporters import ConsoleReporter, MarkdownReporter


class TestCriteriaLoader:
    """Tests for AcceptanceCriteriaLoader."""
    
    def test_list_skills_with_criteria(self, criteria_loader: AcceptanceCriteriaLoader):
        """Should list skills that have acceptance criteria files."""
        skills = criteria_loader.list_skills_with_criteria()
        
        # At minimum, azure-ai-agents-py should have criteria
        assert isinstance(skills, list)
        # This will pass once we have at least one skill with criteria
        if skills:
            assert "azure-ai-agents-py" in skills
    
    def test_load_criteria(self, criteria_loader: AcceptanceCriteriaLoader):
        """Should load and parse acceptance criteria."""
        skills = criteria_loader.list_skills_with_criteria()
        
        if not skills:
            pytest.skip("No skills with acceptance criteria found")
        
        skill_name = skills[0]
        criteria = criteria_loader.load(skill_name)
        
        assert criteria.skill_name == skill_name
        assert criteria.source_path.exists()
        # Should have parsed some patterns
        assert len(criteria.correct_patterns) > 0 or len(criteria.incorrect_patterns) > 0
    
    def test_load_nonexistent_skill_raises(self, criteria_loader: AcceptanceCriteriaLoader):
        """Should raise FileNotFoundError for nonexistent skill."""
        with pytest.raises(FileNotFoundError):
            criteria_loader.load("nonexistent-skill-xyz")


class TestCodeEvaluator:
    """Tests for CodeEvaluator."""
    
    @pytest.fixture
    def sample_criteria(self, criteria_loader: AcceptanceCriteriaLoader):
        """Load sample criteria for testing."""
        skills = criteria_loader.list_skills_with_criteria()
        if not skills:
            pytest.skip("No skills with acceptance criteria found")
        return criteria_loader.load(skills[0])
    
    def test_evaluate_valid_syntax(self, sample_criteria):
        """Should accept code with valid Python syntax."""
        evaluator = CodeEvaluator(sample_criteria)
        
        code = """
import os
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
print("Hello, World!")
"""
        result = evaluator.evaluate(code, scenario="test")
        
        assert isinstance(result, EvaluationResult)
        # Should not have syntax errors
        syntax_errors = [f for f in result.findings if f.rule == "syntax"]
        assert len(syntax_errors) == 0
    
    def test_evaluate_invalid_syntax(self, sample_criteria):
        """Should detect code with invalid Python syntax."""
        evaluator = CodeEvaluator(sample_criteria)
        
        code = """
def broken(
    print("missing closing paren"
"""
        result = evaluator.evaluate(code, scenario="test")
        
        assert not result.passed
        assert result.error_count > 0
        # Should have a syntax error finding
        syntax_errors = [f for f in result.findings if f.rule == "syntax"]
        assert len(syntax_errors) > 0
    
    def test_score_calculation(self, sample_criteria):
        """Should calculate a reasonable score."""
        evaluator = CodeEvaluator(sample_criteria)
        
        code = """
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
"""
        result = evaluator.evaluate(code, scenario="test")
        
        # Score should be between 0 and 100
        assert 0 <= result.score <= 100


class TestSkillEvaluationRunner:
    """Tests for the main evaluation runner."""
    
    def test_list_available_skills(self, mock_runner: SkillEvaluationRunner):
        """Should list skills with both criteria and scenarios."""
        skills = mock_runner.list_available_skills()
        
        assert isinstance(skills, list)
        # We have scenarios for azure-ai-agents-py
        if skills:
            assert "azure-ai-agents-py" in skills
    
    def test_load_scenarios(self, mock_runner: SkillEvaluationRunner):
        """Should load test scenarios from YAML."""
        skills = mock_runner.list_available_skills()
        
        if not skills:
            pytest.skip("No skills with both criteria and scenarios")
        
        suite = mock_runner.load_scenarios(skills[0])
        
        assert suite.skill_name == skills[0]
        assert len(suite.scenarios) > 0
    
    def test_run_evaluation_mock_mode(self, mock_runner: SkillEvaluationRunner):
        """Should run evaluation in mock mode."""
        skills = mock_runner.list_available_skills()
        
        if not skills:
            pytest.skip("No skills with both criteria and scenarios")
        
        summary = mock_runner.run(skills[0])
        
        assert summary.skill_name == skills[0]
        assert summary.total_scenarios > 0
        assert summary.passed + summary.failed == summary.total_scenarios
        assert 0 <= summary.avg_score <= 100
    
    def test_run_with_scenario_filter(self, mock_runner: SkillEvaluationRunner):
        """Should filter scenarios by name or tag."""
        skills = mock_runner.list_available_skills()
        
        if not skills:
            pytest.skip("No skills with both criteria and scenarios")
        
        # Filter to just "basic" scenarios
        summary = mock_runner.run(skills[0], scenario_filter="basic")
        
        # Should have fewer scenarios than full run
        full_summary = mock_runner.run(skills[0])
        assert summary.total_scenarios <= full_summary.total_scenarios


class TestAzureAIAgentsPy:
    """Specific tests for azure-ai-agents-py skill."""
    
    SKILL_NAME = "azure-ai-agents-py"
    
    @pytest.fixture
    def runner(self, mock_runner: SkillEvaluationRunner) -> SkillEvaluationRunner:
        """Get a runner configured for this skill."""
        return mock_runner
    
    def test_skill_has_criteria(self, criteria_loader: AcceptanceCriteriaLoader):
        """Should have acceptance criteria file."""
        skills = criteria_loader.list_skills_with_criteria()
        
        if self.SKILL_NAME not in skills:
            pytest.skip(f"{self.SKILL_NAME} does not have acceptance criteria")
        
        criteria = criteria_loader.load(self.SKILL_NAME)
        assert criteria.skill_name == self.SKILL_NAME
        assert len(criteria.correct_patterns) > 0
        assert len(criteria.incorrect_patterns) > 0
    
    def test_basic_agent_scenario(self, runner: SkillEvaluationRunner):
        """Test basic agent creation scenario."""
        if self.SKILL_NAME not in runner.list_available_skills():
            pytest.skip(f"{self.SKILL_NAME} not available")
        
        summary = runner.run(self.SKILL_NAME, scenario_filter="basic_agent")
        
        assert summary.total_scenarios >= 1
        # With mock responses, this should pass
        assert summary.passed >= 1
    
    def test_function_tool_scenario(self, runner: SkillEvaluationRunner):
        """Test function tool usage scenario."""
        if self.SKILL_NAME not in runner.list_available_skills():
            pytest.skip(f"{self.SKILL_NAME} not available")
        
        summary = runner.run(self.SKILL_NAME, scenario_filter="function_tool")
        
        assert summary.total_scenarios >= 1
    
    def test_streaming_scenario(self, runner: SkillEvaluationRunner):
        """Test streaming event handler scenario."""
        if self.SKILL_NAME not in runner.list_available_skills():
            pytest.skip(f"{self.SKILL_NAME} not available")
        
        summary = runner.run(self.SKILL_NAME, scenario_filter="streaming")
        
        assert summary.total_scenarios >= 1
    
    def test_async_scenario(self, runner: SkillEvaluationRunner):
        """Test async client usage scenario."""
        if self.SKILL_NAME not in runner.list_available_skills():
            pytest.skip(f"{self.SKILL_NAME} not available")
        
        summary = runner.run(self.SKILL_NAME, scenario_filter="async")
        
        assert summary.total_scenarios >= 1
    
    def test_all_scenarios(self, runner: SkillEvaluationRunner):
        """Run all scenarios for the skill."""
        if self.SKILL_NAME not in runner.list_available_skills():
            pytest.skip(f"{self.SKILL_NAME} not available")
        
        summary = runner.run(self.SKILL_NAME)
        
        # We have 8 scenarios defined
        assert summary.total_scenarios >= 8
        
        # Report results
        print(f"\n{self.SKILL_NAME} Evaluation Summary:")
        print(f"  Total: {summary.total_scenarios}")
        print(f"  Passed: {summary.passed}")
        print(f"  Failed: {summary.failed}")
        print(f"  Avg Score: {summary.avg_score:.1f}")


class TestReporters:
    """Tests for report generators."""
    
    @pytest.fixture
    def sample_summary(self, mock_runner: SkillEvaluationRunner):
        """Generate a sample summary for testing reporters."""
        skills = mock_runner.list_available_skills()
        if not skills:
            pytest.skip("No skills available")
        return mock_runner.run(skills[0])
    
    def test_console_reporter(self, sample_summary, capsys):
        """Console reporter should output without errors."""
        reporter = ConsoleReporter(verbose=True, use_color=False)
        reporter.report_summary(sample_summary)
        
        captured = capsys.readouterr()
        assert sample_summary.skill_name in captured.out
        assert "Passed" in captured.out or "Pass" in captured.out
    
    def test_markdown_reporter(self, sample_summary, tmp_path):
        """Markdown reporter should generate valid report file."""
        reporter = MarkdownReporter(output_dir=tmp_path)
        report_path = reporter.generate_report(sample_summary)
        
        assert report_path.exists()
        content = report_path.read_text()
        
        # Should contain expected sections
        assert "# " in content  # Has headers
        assert sample_summary.skill_name in content
        assert "Summary" in content


# Parametrized tests for all available skills
class TestAllSkills:
    """Run evaluation for all available skills."""
    
    @pytest.mark.slow
    def test_skill_evaluation(
        self, 
        mock_runner: SkillEvaluationRunner,
        skill_name: str  # Parametrized by conftest.py
    ):
        """Evaluate a skill against its acceptance criteria."""
        if skill_name not in mock_runner.list_available_skills():
            pytest.skip(f"{skill_name} does not have test scenarios")
        
        summary = mock_runner.run(skill_name)
        
        # Basic assertions
        assert summary.total_scenarios > 0
        assert summary.passed + summary.failed == summary.total_scenarios
        
        # Report any failures
        if summary.failed > 0:
            failure_details = []
            for result in summary.results:
                if not result.passed:
                    errors = [f.message for f in result.findings if f.severity.value == "error"]
                    failure_details.append(f"{result.scenario}: {errors}")
            
            # Don't fail the test, but report issues
            print(f"\n{skill_name} had {summary.failed} failures:")
            for detail in failure_details:
                print(f"  - {detail}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
