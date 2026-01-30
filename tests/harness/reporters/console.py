"""
Console Reporter

Pretty console output for evaluation results using optional Rich library.
Falls back to plain text if Rich is not installed.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..evaluator import EvaluationResult, Finding
    from ..runner import EvaluationSummary

# Try to import Rich for pretty output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ConsoleReporter:
    """
    Reports evaluation results to the console.
    
    Uses Rich for pretty formatting if available, otherwise plain text.
    """
    
    def __init__(self, verbose: bool = False, use_color: bool = True):
        self.verbose = verbose
        self.use_color = use_color and RICH_AVAILABLE
        
        if self.use_color:
            self.console = Console()
        else:
            self.console = None
    
    def report_summary(self, summary: EvaluationSummary) -> None:
        """Print a summary of evaluation results."""
        if self.use_color:
            self._report_summary_rich(summary)
        else:
            self._report_summary_plain(summary)
    
    def report_result(self, result: EvaluationResult) -> None:
        """Print a single evaluation result."""
        if self.use_color:
            self._report_result_rich(result)
        else:
            self._report_result_plain(result)
    
    def _report_summary_rich(self, summary: EvaluationSummary) -> None:
        """Print summary using Rich formatting."""
        # Header
        status_color = "green" if summary.failed == 0 else "red"
        status_emoji = "✅" if summary.failed == 0 else "❌"
        
        self.console.print()
        self.console.print(Panel(
            f"[bold]{summary.skill_name}[/bold] Evaluation",
            style=status_color,
        ))
        
        # Summary table
        table = Table(box=box.SIMPLE)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        table.add_row("Total Scenarios", str(summary.total_scenarios))
        table.add_row("Passed", f"[green]{summary.passed}[/green]")
        table.add_row("Failed", f"[red]{summary.failed}[/red]" if summary.failed else "0")
        
        pass_rate = (summary.passed / summary.total_scenarios * 100) if summary.total_scenarios else 0
        rate_color = "green" if pass_rate >= 80 else "yellow" if pass_rate >= 50 else "red"
        table.add_row("Pass Rate", f"[{rate_color}]{pass_rate:.1f}%[/{rate_color}]")
        
        score_color = "green" if summary.avg_score >= 80 else "yellow" if summary.avg_score >= 50 else "red"
        table.add_row("Average Score", f"[{score_color}]{summary.avg_score:.1f}[/{score_color}]")
        table.add_row("Duration", f"{summary.duration_ms:.0f}ms")
        
        self.console.print(table)
        
        # Failed scenarios
        if summary.failed > 0 and self.verbose:
            self.console.print("\n[bold red]Failed Scenarios:[/bold red]")
            for result in summary.results:
                if not result.passed:
                    self._report_result_rich(result)
    
    def _report_summary_plain(self, summary: EvaluationSummary) -> None:
        """Print summary using plain text."""
        print()
        print("=" * 60)
        print(f"Evaluation Summary: {summary.skill_name}")
        print("=" * 60)
        print(f"Scenarios: {summary.total_scenarios}")
        print(f"Passed: {summary.passed}")
        print(f"Failed: {summary.failed}")
        
        pass_rate = (summary.passed / summary.total_scenarios * 100) if summary.total_scenarios else 0
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"Average Score: {summary.avg_score:.1f}")
        print(f"Duration: {summary.duration_ms:.0f}ms")
        
        if summary.failed > 0 and self.verbose:
            print("\nFailed Scenarios:")
            for result in summary.results:
                if not result.passed:
                    self._report_result_plain(result)
    
    def _report_result_rich(self, result: EvaluationResult) -> None:
        """Print a single result using Rich formatting."""
        status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        
        self.console.print(f"\n  {status} {result.scenario} (score: {result.score:.1f})")
        
        if self.verbose or not result.passed:
            for finding in result.findings:
                severity_style = {
                    "error": "red",
                    "warning": "yellow",
                    "info": "blue",
                }.get(finding.severity.value, "white")
                
                self.console.print(
                    f"    [{severity_style}][{finding.severity.value.upper()}][/{severity_style}] "
                    f"{finding.rule}: {finding.message}"
                )
                
                if finding.suggestion:
                    self.console.print(f"      💡 {finding.suggestion}")
    
    def _report_result_plain(self, result: EvaluationResult) -> None:
        """Print a single result using plain text."""
        status = "PASS" if result.passed else "FAIL"
        print(f"\n  [{status}] {result.scenario} (score: {result.score:.1f})")
        
        if self.verbose or not result.passed:
            for finding in result.findings:
                print(f"    [{finding.severity.value.upper()}] {finding.rule}: {finding.message}")
                if finding.suggestion:
                    print(f"      Suggestion: {finding.suggestion}")
    
    def print_header(self, text: str) -> None:
        """Print a section header."""
        if self.use_color:
            self.console.print(f"\n[bold blue]{text}[/bold blue]")
        else:
            print(f"\n{text}")
            print("-" * len(text))
    
    def print_error(self, text: str) -> None:
        """Print an error message."""
        if self.use_color:
            self.console.print(f"[red]Error:[/red] {text}")
        else:
            print(f"Error: {text}", file=sys.stderr)
    
    def print_warning(self, text: str) -> None:
        """Print a warning message."""
        if self.use_color:
            self.console.print(f"[yellow]Warning:[/yellow] {text}")
        else:
            print(f"Warning: {text}", file=sys.stderr)
    
    def print_success(self, text: str) -> None:
        """Print a success message."""
        if self.use_color:
            self.console.print(f"[green]✓[/green] {text}")
        else:
            print(f"✓ {text}")
