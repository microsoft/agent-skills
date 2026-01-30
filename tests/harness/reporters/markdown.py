"""
Markdown Reporter

Generates markdown reports for evaluation results.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..evaluator import EvaluationResult
    from ..runner import EvaluationSummary


class MarkdownReporter:
    """
    Generates markdown reports for evaluation results.
    
    Outputs:
    - Summary tables
    - Detailed findings
    - Code snippets with issues highlighted
    """
    
    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path("tests/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self, 
        summary: EvaluationSummary,
        filename: str | None = None
    ) -> Path:
        """Generate a markdown report for an evaluation summary."""
        filename = filename or f"{summary.skill_name}-report.md"
        output_path = self.output_dir / filename
        
        content = self._build_report(summary)
        output_path.write_text(content, encoding="utf-8")
        
        return output_path
    
    def _build_report(self, summary: EvaluationSummary) -> str:
        """Build the full markdown report content."""
        lines = []
        
        # Header
        lines.extend(self._build_header(summary))
        
        # Summary section
        lines.extend(self._build_summary_section(summary))
        
        # Results table
        lines.extend(self._build_results_table(summary))
        
        # Detailed findings
        if summary.failed > 0:
            lines.extend(self._build_detailed_findings(summary))
        
        # Footer
        lines.extend(self._build_footer())
        
        return "\n".join(lines)
    
    def _build_header(self, summary: EvaluationSummary) -> list[str]:
        """Build the report header."""
        status_emoji = "✅" if summary.failed == 0 else "❌"
        
        return [
            f"# {status_emoji} Skill Evaluation Report: {summary.skill_name}",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
    
    def _build_summary_section(self, summary: EvaluationSummary) -> list[str]:
        """Build the summary metrics section."""
        pass_rate = (summary.passed / summary.total_scenarios * 100) if summary.total_scenarios else 0
        
        status = "🟢 PASSED" if summary.failed == 0 else "🔴 FAILED"
        
        return [
            "## Summary",
            "",
            f"**Status:** {status}",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Scenarios | {summary.total_scenarios} |",
            f"| Passed | {summary.passed} |",
            f"| Failed | {summary.failed} |",
            f"| Pass Rate | {pass_rate:.1f}% |",
            f"| Average Score | {summary.avg_score:.1f} |",
            f"| Duration | {summary.duration_ms:.0f}ms |",
            "",
        ]
    
    def _build_results_table(self, summary: EvaluationSummary) -> list[str]:
        """Build the results overview table."""
        lines = [
            "## Scenario Results",
            "",
            "| Scenario | Status | Score | Errors | Warnings |",
            "|----------|--------|-------|--------|----------|",
        ]
        
        for result in summary.results:
            status = "✅ Pass" if result.passed else "❌ Fail"
            lines.append(
                f"| {result.scenario} | {status} | {result.score:.1f} | "
                f"{result.error_count} | {result.warning_count} |"
            )
        
        lines.append("")
        return lines
    
    def _build_detailed_findings(self, summary: EvaluationSummary) -> list[str]:
        """Build detailed findings for failed scenarios."""
        lines = [
            "## Detailed Findings",
            "",
        ]
        
        for result in summary.results:
            if not result.passed:
                lines.extend(self._build_result_details(result))
        
        return lines
    
    def _build_result_details(self, result: EvaluationResult) -> list[str]:
        """Build details for a single failed result."""
        lines = [
            f"### {result.scenario}",
            "",
            f"**Score:** {result.score:.1f}",
            "",
        ]
        
        if result.findings:
            lines.append("#### Findings")
            lines.append("")
            
            for finding in result.findings:
                severity_emoji = {
                    "error": "🔴",
                    "warning": "🟡",
                    "info": "🔵",
                }.get(finding.severity.value, "⚪")
                
                lines.append(f"- {severity_emoji} **{finding.rule}**: {finding.message}")
                
                if finding.suggestion:
                    lines.append(f"  - 💡 *Suggestion:* {finding.suggestion}")
                
                if finding.code_snippet:
                    lines.append(f"  ```python")
                    lines.append(f"  {finding.code_snippet}")
                    lines.append(f"  ```")
            
            lines.append("")
        
        # Show matched patterns
        if result.matched_incorrect:
            lines.append("#### Incorrect Patterns Detected")
            lines.append("")
            for pattern in result.matched_incorrect:
                lines.append(f"- `{pattern}`")
            lines.append("")
        
        if result.matched_correct:
            lines.append("#### Correct Patterns Found")
            lines.append("")
            for pattern in result.matched_correct:
                lines.append(f"- `{pattern}`")
            lines.append("")
        
        return lines
    
    def _build_footer(self) -> list[str]:
        """Build the report footer."""
        return [
            "---",
            "",
            "*Report generated by Skill Evaluation Harness*",
        ]
    
    def generate_multi_skill_report(
        self,
        summaries: list[EvaluationSummary],
        filename: str = "evaluation-report.md"
    ) -> Path:
        """Generate a combined report for multiple skills."""
        output_path = self.output_dir / filename
        
        lines = [
            "# Skill Evaluation Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Skills Evaluated:** {len(summaries)}",
            "",
            "## Overview",
            "",
            "| Skill | Status | Pass Rate | Avg Score |",
            "|-------|--------|-----------|-----------|",
        ]
        
        total_passed = 0
        total_scenarios = 0
        
        for summary in summaries:
            status = "✅" if summary.failed == 0 else "❌"
            pass_rate = (summary.passed / summary.total_scenarios * 100) if summary.total_scenarios else 0
            
            lines.append(
                f"| {summary.skill_name} | {status} | {pass_rate:.1f}% | "
                f"{summary.avg_score:.1f} |"
            )
            
            total_passed += summary.passed
            total_scenarios += summary.total_scenarios
        
        lines.append("")
        
        # Overall summary
        overall_pass_rate = (total_passed / total_scenarios * 100) if total_scenarios else 0
        lines.extend([
            "## Overall Statistics",
            "",
            f"- **Total Scenarios:** {total_scenarios}",
            f"- **Total Passed:** {total_passed}",
            f"- **Overall Pass Rate:** {overall_pass_rate:.1f}%",
            "",
        ])
        
        # Detailed sections for each skill
        for summary in summaries:
            if summary.failed > 0:
                lines.append(f"## {summary.skill_name}")
                lines.append("")
                lines.extend(self._build_summary_section(summary)[2:])  # Skip header
                lines.extend(self._build_detailed_findings(summary))
        
        lines.extend(self._build_footer())
        
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path
