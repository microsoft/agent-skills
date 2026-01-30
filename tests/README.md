# Skill Evaluation Test Harness

A test framework for evaluating AI-generated code against acceptance criteria defined in skill files.

## Overview

This harness:
1. **Loads acceptance criteria** from `.github/skills/<skill>/references/acceptance-criteria.md`
2. **Runs test scenarios** defined in `tests/scenarios/<skill>/scenarios.yaml`
3. **Generates code** using GitHub Copilot SDK (or mock responses)
4. **Evaluates code** against correct/incorrect patterns from criteria
5. **Reports results** via console, markdown, or JSON

## Quick Start

```bash
# Install dependencies
pip install -r tests/requirements.txt

# List available skills with acceptance criteria
python -m tests.harness.runner --list

# Run evaluation in mock mode (no Copilot SDK required)
python -m tests.harness.runner azure-ai-agents-py --mock --verbose

# Run with pytest
pytest tests/ -v

# Run specific skill tests
pytest tests/test_skills.py -k "azure_ai_agents" -v
```

## Architecture

```
tests/
├── harness/
│   ├── __init__.py           # Package exports
│   ├── criteria_loader.py    # Parses acceptance-criteria.md
│   ├── evaluator.py          # Validates code against patterns
│   ├── copilot_client.py     # Wraps Copilot SDK (with mock fallback)
│   ├── runner.py             # Main CLI runner
│   └── reporters/
│       ├── console.py        # Pretty console output
│       └── markdown.py       # Markdown report generation
│
├── scenarios/
│   └── <skill-name>/
│       └── scenarios.yaml    # Test scenarios for the skill
│
├── fixtures/                 # Test fixtures (sample code, etc.)
├── reports/                  # Generated reports (gitignored)
├── conftest.py              # Pytest fixtures
├── requirements.txt         # Test dependencies
├── test_skills.py           # Main test file
└── README.md                # This file
```

## Usage

### CLI Runner

```bash
# Basic usage
python -m tests.harness.runner <skill-name>

# Options
python -m tests.harness.runner azure-ai-agents-py \
    --mock                  # Use mock responses (no Copilot SDK)
    --verbose               # Show detailed output
    --filter basic          # Filter scenarios by name/tag
    --output json           # Output format (text/json)
    --output-file report.json
```

### Pytest

```bash
# Run all tests
pytest tests/ -v

# Run tests for a specific skill
pytest tests/test_skills.py -k "azure_ai_agents" -v

# Run with coverage
pytest tests/ --cov=tests.harness --cov-report=html

# Skip slow tests
pytest tests/ -m "not slow"

# Run in parallel
pytest tests/ -n auto
```

### Programmatic Usage

```python
from tests.harness import (
    AcceptanceCriteriaLoader,
    CodeEvaluator,
    SkillEvaluationRunner,
)

# Load and evaluate code directly
loader = AcceptanceCriteriaLoader()
criteria = loader.load("azure-ai-agents-py")
evaluator = CodeEvaluator(criteria)

code = '''
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
# ... your code
'''

result = evaluator.evaluate(code, scenario="my-test")
print(f"Passed: {result.passed}, Score: {result.score}")

# Or run full evaluation
runner = SkillEvaluationRunner(use_mock=True)
summary = runner.run("azure-ai-agents-py")
print(f"Pass rate: {summary.passed}/{summary.total_scenarios}")
```

## Adding Tests for a New Skill

### 1. Create Acceptance Criteria

Create `.github/skills/<skill-name>/references/acceptance-criteria.md`:

```markdown
# Acceptance Criteria: skill-name

## Imports

### ✅ Correct
```python
from azure.ai.mymodule import MyClient
```

### ❌ Incorrect
```python
from azure.ai.mymodule.models import MyClient  # Wrong location
```

## Basic Usage

### ✅ Correct
```python
client = MyClient(endpoint=os.environ["ENDPOINT"])
```

### ❌ Incorrect
```python
client = MyClient("hardcoded-endpoint")  # Don't hardcode
```
```

### 2. Create Test Scenarios

Create `tests/scenarios/<skill-name>/scenarios.yaml`:

```yaml
config:
  model: gpt-4
  max_tokens: 2000
  temperature: 0.3

scenarios:
  - name: basic_usage
    prompt: |
      Create a basic example using the SDK.
      Include authentication and proper cleanup.
    expected_patterns:
      - "DefaultAzureCredential"
      - "MyClient"
    forbidden_patterns:
      - "hardcoded-endpoint"
    tags:
      - basic
      - authentication
    mock_response: |
      import os
      from azure.identity import DefaultAzureCredential
      from azure.ai.mymodule import MyClient
      
      client = MyClient(
          endpoint=os.environ["ENDPOINT"],
          credential=DefaultAzureCredential(),
      )
      # ... rest of example
```

### 3. Run Tests

```bash
# Verify criteria loads correctly
python -m tests.harness.criteria_loader <skill-name>

# Run evaluation
python -m tests.harness.runner <skill-name> --mock --verbose

# Run pytest
pytest tests/test_skills.py -k "<skill_name>" -v
```

## Evaluation Scoring

The evaluator calculates a score (0-100) based on:

| Factor | Impact |
|--------|--------|
| Syntax error | -100 (fails immediately) |
| Incorrect pattern found | -15 each |
| Error finding | -20 each |
| Warning finding | -5 each |
| Correct pattern matched | +5 each |

A result **passes** if it has no error-severity findings.

## Mock Mode vs Real Mode

### Mock Mode (Default)
- Uses predefined responses from `scenarios.yaml`
- No external dependencies required
- Fast, deterministic results
- Good for CI/CD and development

### Real Mode (Copilot SDK)
- Generates code using GitHub Copilot SDK
- Requires `pip install github-copilot-sdk`
- Requires Copilot CLI authentication
- Tests actual generation quality

```bash
# Check if Copilot is available
python -m tests.harness.copilot_client

# Run with real Copilot (if available)
python -m tests.harness.runner azure-ai-agents-py
```

## Reports

### Console Output
```bash
python -m tests.harness.runner azure-ai-agents-py --verbose
```

### Markdown Report
```python
from tests.harness.reporters import MarkdownReporter

reporter = MarkdownReporter(output_dir=Path("tests/reports"))
report_path = reporter.generate_report(summary)
```

### JSON Output
```bash
python -m tests.harness.runner azure-ai-agents-py --output json > report.json
```

## Key Classes

### `AcceptanceCriteriaLoader`
Parses acceptance criteria markdown files and extracts:
- Correct code patterns (✅ sections)
- Incorrect code patterns (❌ sections)
- Validation rules

### `CodeEvaluator`
Validates generated code against criteria:
- Syntax checking (AST parsing)
- Pattern matching (regex + AST)
- Import validation
- Score calculation

### `SkillCopilotClient`
Wraps code generation:
- Loads skill context from SKILL.md and references
- Calls Copilot SDK for generation
- Falls back to mock client if SDK unavailable

### `SkillEvaluationRunner`
Orchestrates the full evaluation:
- Loads scenarios and criteria
- Generates code for each scenario
- Evaluates results
- Produces summary statistics

## Troubleshooting

### "No skills with acceptance criteria found"
- Ensure `.github/skills/<skill>/references/acceptance-criteria.md` exists
- Check file path and naming

### "Copilot SDK not available"
- Install: `pip install github-copilot-sdk`
- Or use `--mock` flag

### Tests pass in mock mode but fail with real Copilot
- Mock responses are manually crafted to be correct
- Real generated code may have different patterns
- Review acceptance criteria for flexibility

## Contributing

1. Add acceptance criteria for new skills
2. Create comprehensive test scenarios
3. Ensure mock responses demonstrate correct patterns
4. Run full test suite before submitting
