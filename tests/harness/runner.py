"""
Skill Evaluation Runner

Main entry point for running skill evaluations. Coordinates loading scenarios,
generating code via Copilot, and evaluating against acceptance criteria.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from .copilot_client import SkillCopilotClient, GenerationConfig, check_copilot_available
from .criteria_loader import AcceptanceCriteriaLoader
from .evaluator import CodeEvaluator, EvaluationResult

if TYPE_CHECKING:
    from .criteria_loader import AcceptanceCriteria


@dataclass
class TestScenario:
    """A test scenario for skill evaluation."""
    
    name: str
    prompt: str
    expected_patterns: list[str] = field(default_factory=list)
    forbidden_patterns: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    mock_response: str | None = None  # For testing without Copilot


@dataclass 
class SkillTestSuite:
    """Collection of test scenarios for a skill."""
    
    skill_name: str
    scenarios: list[TestScenario] = field(default_factory=list)
    config: GenerationConfig = field(default_factory=GenerationConfig)


@dataclass
class EvaluationSummary:
    """Summary of all evaluation results."""
    
    skill_name: str
    total_scenarios: int
    passed: int
    failed: int
    avg_score: float
    duration_ms: float
    results: list[EvaluationResult] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "total_scenarios": self.total_scenarios,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.passed / self.total_scenarios if self.total_scenarios else 0,
            "avg_score": self.avg_score,
            "duration_ms": self.duration_ms,
            "results": [r.to_dict() for r in self.results],
        }


class SkillEvaluationRunner:
    """
    Runs skill evaluations end-to-end.
    
    Workflow:
    1. Load test scenarios from tests/scenarios/<skill>/
    2. Load acceptance criteria from .github/skills/<skill>/
    3. Generate code for each scenario using Copilot SDK
    4. Evaluate generated code against criteria
    5. Report results
    """
    
    SCENARIOS_DIR = Path("tests/scenarios")
    
    def __init__(
        self, 
        base_path: Path | None = None,
        use_mock: bool = False,
        verbose: bool = False
    ):
        self.base_path = base_path or Path.cwd()
        self.scenarios_dir = self.base_path / self.SCENARIOS_DIR
        self._use_mock = use_mock
        self._verbose = verbose
        
        self.criteria_loader = AcceptanceCriteriaLoader(self.base_path)
        self.copilot_client = SkillCopilotClient(
            self.base_path, 
            use_mock=use_mock
        )
    
    def list_available_skills(self) -> list[str]:
        """List skills that have both criteria and scenarios."""
        skills_with_criteria = set(self.criteria_loader.list_skills_with_criteria())
        skills_with_scenarios = set()
        
        if self.scenarios_dir.exists():
            for scenario_dir in self.scenarios_dir.iterdir():
                if scenario_dir.is_dir():
                    scenarios_file = scenario_dir / "scenarios.yaml"
                    if scenarios_file.exists():
                        skills_with_scenarios.add(scenario_dir.name)
        
        return sorted(skills_with_criteria & skills_with_scenarios)
    
    def load_scenarios(self, skill_name: str) -> SkillTestSuite:
        """Load test scenarios for a skill."""
        scenarios_file = self.scenarios_dir / skill_name / "scenarios.yaml"
        
        if not scenarios_file.exists():
            # Return default scenarios if no file exists
            return self._default_scenarios(skill_name)
        
        with open(scenarios_file) as f:
            data = yaml.safe_load(f)
        
        scenarios = []
        for sc in data.get("scenarios", []):
            scenarios.append(TestScenario(
                name=sc.get("name", "unnamed"),
                prompt=sc.get("prompt", ""),
                expected_patterns=sc.get("expected_patterns", []),
                forbidden_patterns=sc.get("forbidden_patterns", []),
                tags=sc.get("tags", []),
                mock_response=sc.get("mock_response"),
            ))
        
        config_data = data.get("config", {})
        config = GenerationConfig(
            model=config_data.get("model", "gpt-4"),
            max_tokens=config_data.get("max_tokens", 2000),
            temperature=config_data.get("temperature", 0.3),
        )
        
        return SkillTestSuite(
            skill_name=skill_name,
            scenarios=scenarios,
            config=config,
        )
    
    def _default_scenarios(self, skill_name: str) -> SkillTestSuite:
        """Generate default test scenarios based on skill name."""
        # Default scenarios based on common patterns
        scenarios = [
            TestScenario(
                name="basic_usage",
                prompt=f"Write a basic example using the {skill_name} SDK",
                tags=["basic"],
            ),
            TestScenario(
                name="authentication",
                prompt=f"Show how to authenticate with {skill_name}",
                tags=["auth"],
            ),
        ]
        
        return SkillTestSuite(skill_name=skill_name, scenarios=scenarios)
    
    def run(
        self, 
        skill_name: str,
        scenario_filter: str | None = None
    ) -> EvaluationSummary:
        """Run evaluation for a skill."""
        start_time = time.time()
        
        # Load criteria and scenarios
        criteria = self.criteria_loader.load(skill_name)
        suite = self.load_scenarios(skill_name)
        
        # Filter scenarios if requested
        scenarios = suite.scenarios
        if scenario_filter:
            scenarios = [
                s for s in scenarios 
                if scenario_filter.lower() in s.name.lower() or
                   scenario_filter.lower() in s.tags
            ]
        
        # Create evaluator
        evaluator = CodeEvaluator(criteria)
        
        # Run each scenario
        results: list[EvaluationResult] = []
        
        for scenario in scenarios:
            if self._verbose:
                print(f"  Running scenario: {scenario.name}")
            
            # Setup mock response if provided
            if scenario.mock_response and self._use_mock:
                self.copilot_client.add_mock_response(
                    scenario.name, 
                    scenario.mock_response
                )
            
            # Generate code
            gen_result = self.copilot_client.generate(
                prompt=scenario.prompt,
                skill_name=skill_name,
                config=suite.config,
            )
            
            # Evaluate
            eval_result = evaluator.evaluate(
                gen_result.code,
                scenario=scenario.name
            )
            
            # Add scenario-specific checks
            self._check_scenario_patterns(
                eval_result, 
                scenario,
                gen_result.code
            )
            
            results.append(eval_result)
            
            if self._verbose:
                status = "✓" if eval_result.passed else "✗"
                print(f"    {status} Score: {eval_result.score:.1f}")
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Calculate summary
        passed = sum(1 for r in results if r.passed)
        avg_score = sum(r.score for r in results) / len(results) if results else 0
        
        return EvaluationSummary(
            skill_name=skill_name,
            total_scenarios=len(results),
            passed=passed,
            failed=len(results) - passed,
            avg_score=avg_score,
            duration_ms=duration_ms,
            results=results,
        )
    
    def _check_scenario_patterns(
        self,
        result: EvaluationResult,
        scenario: TestScenario,
        code: str
    ) -> None:
        """Check scenario-specific expected/forbidden patterns."""
        from .evaluator import Finding, Severity
        
        # Check expected patterns
        for pattern in scenario.expected_patterns:
            if pattern not in code:
                result.findings.append(Finding(
                    severity=Severity.WARNING,
                    rule=f"scenario:{scenario.name}",
                    message=f"Expected pattern not found: {pattern}",
                ))
        
        # Check forbidden patterns
        for pattern in scenario.forbidden_patterns:
            if pattern in code:
                result.findings.append(Finding(
                    severity=Severity.ERROR,
                    rule=f"scenario:{scenario.name}",
                    message=f"Forbidden pattern found: {pattern}",
                ))


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run skill evaluations against acceptance criteria"
    )
    parser.add_argument(
        "skill",
        nargs="?",
        help="Skill name to evaluate (e.g., azure-ai-agents-py)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available skills with test scenarios"
    )
    parser.add_argument(
        "--filter",
        help="Filter scenarios by name or tag"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock responses instead of Copilot SDK"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--output-file",
        help="Write results to file"
    )
    
    args = parser.parse_args()
    
    # Check Copilot availability
    copilot_available = check_copilot_available()
    use_mock = args.mock or not copilot_available
    
    if not copilot_available and not args.mock:
        print("⚠️  Copilot SDK not available, using mock mode")
        print("   Install: pip install github-copilot-sdk")
        print("   Install CLI: https://docs.github.com/copilot/cli")
        print()
    
    runner = SkillEvaluationRunner(use_mock=use_mock, verbose=args.verbose)
    
    if args.list:
        skills = runner.list_available_skills()
        if not skills:
            print("No skills with both acceptance criteria and test scenarios found.")
            print("\nSkills with criteria only:")
            for skill in runner.criteria_loader.list_skills_with_criteria():
                print(f"  - {skill}")
        else:
            print(f"Available skills ({len(skills)}):")
            for skill in skills:
                print(f"  - {skill}")
        return 0
    
    if not args.skill:
        parser.print_help()
        return 1
    
    # Run evaluation
    print(f"Evaluating skill: {args.skill}")
    print(f"Mode: {'mock' if use_mock else 'copilot'}")
    print("-" * 50)
    
    try:
        summary = runner.run(args.skill, scenario_filter=args.filter)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    # Output results
    if args.output == "json":
        output = json.dumps(summary.to_dict(), indent=2)
    else:
        lines = [
            f"\nEvaluation Summary: {summary.skill_name}",
            "=" * 50,
            f"Scenarios: {summary.total_scenarios}",
            f"Passed: {summary.passed}",
            f"Failed: {summary.failed}",
            f"Pass Rate: {summary.passed/summary.total_scenarios*100:.1f}%" if summary.total_scenarios else "N/A",
            f"Average Score: {summary.avg_score:.1f}",
            f"Duration: {summary.duration_ms:.0f}ms",
        ]
        
        if summary.failed > 0:
            lines.append("\nFailed Scenarios:")
            for result in summary.results:
                if not result.passed:
                    lines.append(f"  - {result.scenario}")
                    for finding in result.findings:
                        if finding.severity.value == "error":
                            lines.append(f"      [{finding.severity.value}] {finding.message}")
        
        output = "\n".join(lines)
    
    if args.output_file:
        Path(args.output_file).write_text(output)
        print(f"Results written to: {args.output_file}")
    else:
        print(output)
    
    # Return exit code based on pass rate
    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
