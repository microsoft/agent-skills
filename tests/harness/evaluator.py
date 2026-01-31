"""
Code Evaluator

Validates generated code against acceptance criteria patterns.
Performs static analysis to check for correct/incorrect usage patterns.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .criteria_loader import AcceptanceCriteria, CodePattern, ValidationRule


class Severity(Enum):
    """Severity levels for evaluation findings."""

    ERROR = "error"  # Incorrect pattern found
    WARNING = "warning"  # Missing recommended pattern
    INFO = "info"  # Informational finding


@dataclass
class Finding:
    """A single finding from code evaluation."""

    severity: Severity
    rule: str
    message: str
    line: int | None = None
    column: int | None = None
    code_snippet: str = ""
    suggestion: str = ""


@dataclass
class EvaluationResult:
    """Result of evaluating code against criteria."""

    skill_name: str
    scenario: str
    generated_code: str
    findings: list[Finding] = field(default_factory=list)
    matched_correct: list[str] = field(default_factory=list)
    matched_incorrect: list[str] = field(default_factory=list)
    score: float = 0.0

    @property
    def passed(self) -> bool:
        """Check if evaluation passed (no errors)."""
        return not any(f.severity == Severity.ERROR for f in self.findings)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.WARNING)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "skill_name": self.skill_name,
            "scenario": self.scenario,
            "passed": self.passed,
            "score": self.score,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "findings": [
                {
                    "severity": f.severity.value,
                    "rule": f.rule,
                    "message": f.message,
                    "line": f.line,
                    "suggestion": f.suggestion,
                }
                for f in self.findings
            ],
            "matched_correct": self.matched_correct,
            "matched_incorrect": self.matched_incorrect,
        }


class CodeEvaluator:
    """
    Evaluates generated code against acceptance criteria.

    Performs:
    - Import validation (correct modules used)
    - Pattern matching (correct/incorrect patterns)
    - AST analysis (structure validation)
    - Best practice checks
    """

    def __init__(self, criteria: AcceptanceCriteria):
        self.criteria = criteria
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for efficiency."""
        self._correct_regexes: list[tuple[str, re.Pattern]] = []
        self._incorrect_regexes: list[tuple[str, re.Pattern]] = []

        for pattern in self.criteria.correct_patterns:
            regex = self._code_to_regex(pattern.code)
            if regex:
                self._correct_regexes.append((pattern.section, regex))

        for pattern in self.criteria.incorrect_patterns:
            regex = self._code_to_regex(pattern.code)
            if regex:
                self._incorrect_regexes.append((pattern.section, regex))

    def _code_to_regex(self, code: str) -> re.Pattern | None:
        """Convert a code snippet to a flexible regex pattern."""
        # Extract key identifiers and structure
        # This is simplified - production would use AST matching

        # Escape special regex chars but keep structure
        pattern = re.escape(code.strip())

        # Make whitespace flexible
        pattern = re.sub(r"\\ +", r"\\s+", pattern)
        pattern = re.sub(r"\\n", r"\\s*", pattern)

        # Make string quotes flexible
        pattern = pattern.replace(r"\"", r'["\']')
        pattern = pattern.replace(r"\'", r'["\']')

        try:
            return re.compile(pattern, re.DOTALL | re.MULTILINE)
        except re.error:
            return None

    def evaluate(self, code: str, scenario: str = "") -> EvaluationResult:
        """Evaluate code against acceptance criteria."""
        result = EvaluationResult(
            skill_name=self.criteria.skill_name,
            scenario=scenario,
            generated_code=code,
        )

        # Check for syntax errors first
        if not self._check_syntax(code, result):
            result.score = 0.0
            return result

        # Check imports
        self._check_imports(code, result)

        # Check for incorrect patterns
        self._check_incorrect_patterns(code, result)

        # Check for correct patterns
        self._check_correct_patterns(code, result)

        # Check rule-specific criteria
        for rule in self.criteria.rules:
            self._check_rule(code, rule, result)

        # Calculate score
        result.score = self._calculate_score(result)

        return result

    def _check_syntax(self, code: str, result: EvaluationResult) -> bool:
        """Check if code has valid syntax (Python only; skip for other languages)."""
        if self.criteria.language.lower() != "python":
            return True

        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            result.findings.append(
                Finding(
                    severity=Severity.ERROR,
                    rule="syntax",
                    message=f"Syntax error: {e.msg}",
                    line=e.lineno,
                    column=e.offset,
                )
            )
            return False

    def _check_imports(self, code: str, result: EvaluationResult) -> None:
        """Check import statements using AST for precision (Python only)."""
        if self.criteria.language.lower() != "python":
            return

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return

        # Build a set of actual imports in the code
        actual_imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    # Store as "from module import name"
                    actual_imports.add(f"from {node.module} import {alias.name}")

        # Check incorrect import patterns from criteria
        for pattern in self.criteria.incorrect_patterns:
            if "import" not in pattern.code.lower():
                continue

            # Extract import statements from the pattern (ignoring comments)
            for line in pattern.code.split("\n"):
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if not (line.startswith("from ") or line.startswith("import ")):
                    continue

                # Normalize and check for exact match
                normalized_pattern = " ".join(line.split())
                for actual_import in actual_imports:
                    if normalized_pattern == actual_import:
                        result.findings.append(
                            Finding(
                                severity=Severity.ERROR,
                                rule="imports",
                                message=f"Incorrect import: {line}",
                                suggestion=f"Check acceptance criteria section: {pattern.section}",
                            )
                        )

    def _check_incorrect_patterns(self, code: str, result: EvaluationResult) -> None:
        """Check for incorrect patterns in the code."""
        for section, regex in self._incorrect_regexes:
            if regex.search(code):
                result.matched_incorrect.append(section)
                result.findings.append(
                    Finding(
                        severity=Severity.ERROR,
                        rule=f"pattern:{section}",
                        message=f"Incorrect pattern found from section: {section}",
                        suggestion="Review acceptance criteria for correct usage",
                    )
                )

    def _check_correct_patterns(self, code: str, result: EvaluationResult) -> None:
        """Check for presence of correct patterns."""
        for section, regex in self._correct_regexes:
            if regex.search(code):
                result.matched_correct.append(section)

    def _check_rule(self, code: str, rule: ValidationRule, result: EvaluationResult) -> None:
        """Check code against a specific validation rule."""
        # Check for incorrect patterns in this rule
        for pattern in rule.incorrect_patterns:
            if self._pattern_matches(code, pattern, is_incorrect=True):
                result.findings.append(
                    Finding(
                        severity=Severity.ERROR,
                        rule=rule.name,
                        message=f"Incorrect usage in {rule.name}",
                        code_snippet=pattern.code[:100],
                    )
                )

        # Check for required patterns
        for req_pattern in rule.required_patterns:
            if req_pattern not in code:
                result.findings.append(
                    Finding(
                        severity=Severity.WARNING,
                        rule=rule.name,
                        message=f"Missing recommended pattern: {req_pattern}",
                    )
                )

    def _pattern_matches(self, code: str, pattern: CodePattern, is_incorrect: bool = True) -> bool:
        """Check if a code pattern matches in the generated code.

        Uses more precise matching:
        - For imports: exact statement matching
        - For incorrect patterns: EXACT line matching (to catch specific errors)
        - For correct patterns: FLEXIBLE matching (to allow variations)
        """
        pattern_code = pattern.code.strip()

        # Remove comment lines from the pattern
        code_lines = [
            line.strip()
            for line in pattern_code.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

        if not code_lines:
            return False

        # Check if this is primarily an import pattern
        first_line = code_lines[0]
        if first_line.startswith("from ") or first_line.startswith("import "):
            return self._import_pattern_matches(code, code_lines)

        # For non-import patterns, use different matching based on pattern type
        if is_incorrect:
            # Incorrect patterns: use EXACT matching to catch specific errors
            return self._multi_line_pattern_matches_exact(code, code_lines)
        else:
            # Correct patterns: use FLEXIBLE matching to allow variations
            return self._multi_line_pattern_matches_flexible(code, code_lines)

    def _import_pattern_matches(self, code: str, import_lines: list[str]) -> bool:
        """Check if import patterns match exactly in the code (Python only)."""
        if self.criteria.language.lower() != "python":
            return False

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False

        actual_imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    actual_imports.add(f"from {node.module} import {alias.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    actual_imports.add(f"import {alias.name}")

        # Check if any of the pattern's import lines match exactly
        for import_line in import_lines:
            if not (import_line.startswith("from ") or import_line.startswith("import ")):
                continue

            # Normalize whitespace
            normalized_pattern = " ".join(import_line.split())

            # Check for exact match in actual imports
            if normalized_pattern in actual_imports:
                return True

        return False

    def _multi_line_pattern_matches_exact(self, code: str, pattern_lines: list[str]) -> bool:
        """Check if pattern lines match EXACTLY in code.

        Used for incorrect patterns (anti-patterns).
        Requires exact line matching to catch specific errors.
        For example: 'url=' in pattern should not match 'endpoint=' in code.
        """
        if not pattern_lines:
            return False

        code_lines_normalized = [
            " ".join(line.split())
            for line in code.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

        matched_count = 0
        for pattern_line in pattern_lines:
            normalized_pattern = " ".join(pattern_line.split())

            if len(normalized_pattern) < 15:
                continue

            for code_line in code_lines_normalized:
                if normalized_pattern == code_line:
                    matched_count += 1
                    break

        significant_lines = [l for l in pattern_lines if len(l) >= 15]
        if len(significant_lines) <= 2:
            return matched_count >= 1 and matched_count == len(significant_lines)

        return matched_count >= 2

    def _multi_line_pattern_matches_flexible(self, code: str, pattern_lines: list[str]) -> bool:
        """Check if pattern lines match FLEXIBLY in code.

        Used for correct patterns (documentation examples).
        Allows variations like different formatting, extra parameters, or comments.
        """
        if not pattern_lines:
            return False

        code_lines_normalized = [
            " ".join(line.split())
            for line in code.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

        matched_count = 0
        for pattern_line in pattern_lines:
            normalized_pattern = " ".join(pattern_line.split())

            if len(normalized_pattern) < 15:
                continue

            for code_line in code_lines_normalized:
                if normalized_pattern in code_line or code_line in normalized_pattern:
                    matched_count += 1
                    break

        significant_lines = [l for l in pattern_lines if len(l) >= 15]
        if len(significant_lines) <= 2:
            return matched_count >= 1 and matched_count == len(significant_lines)

        return matched_count >= 2

    def _calculate_score(self, result: EvaluationResult) -> float:
        """Calculate a score from 0-100 based on findings."""
        if not result.findings and not result.matched_correct:
            return 50.0  # Neutral - no patterns matched

        # Start with base score
        score = 100.0

        # Deduct for errors
        score -= result.error_count * 20

        # Deduct for warnings
        score -= result.warning_count * 5

        # Bonus for matching correct patterns
        score += len(result.matched_correct) * 5

        # Major penalty for incorrect patterns
        score -= len(result.matched_incorrect) * 15

        return max(0.0, min(100.0, score))


# Quick self-test
if __name__ == "__main__":
    from .criteria_loader import AcceptanceCriteriaLoader
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m tests.harness.evaluator <skill-name> <code-file>")
        sys.exit(1)

    skill_name = sys.argv[1]
    code_file = sys.argv[2]

    loader = AcceptanceCriteriaLoader()
    criteria = loader.load(skill_name)

    with open(code_file) as f:
        code = f.read()

    evaluator = CodeEvaluator(criteria)
    result = evaluator.evaluate(code, scenario="manual-test")

    print(f"\nEvaluation Result for {skill_name}")
    print("=" * 50)
    print(f"Passed: {result.passed}")
    print(f"Score: {result.score:.1f}")
    print(f"Errors: {result.error_count}")
    print(f"Warnings: {result.warning_count}")

    if result.findings:
        print("\nFindings:")
        for f in result.findings:
            print(f"  [{f.severity.value}] {f.rule}: {f.message}")

    if result.matched_correct:
        print(f"\nMatched correct patterns: {result.matched_correct}")
    if result.matched_incorrect:
        print(f"\nMatched incorrect patterns: {result.matched_incorrect}")
