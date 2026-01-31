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
# Install dependencies (from tests directory)
cd tests
pnpm install

# List available skills with acceptance criteria
pnpm harness --list

# Run evaluation in mock mode (no Copilot SDK required)
pnpm harness azure-ai-agents-py --mock --verbose

# Run tests
pnpm test
```

## Architecture

```
tests/
├── harness/
│   ├── types.ts              # Type definitions
│   ├── criteria-loader.ts    # Parses acceptance-criteria.md
│   ├── evaluator.ts          # Validates code against patterns
│   ├── copilot-client.ts     # Wraps Copilot SDK (with mock fallback)
│   ├── runner.ts             # Main CLI runner
│   ├── index.ts              # Package exports
│   └── reporters/
│       ├── console.ts        # Pretty console output
│       └── markdown.ts       # Markdown report generation
│
├── scenarios/
│   └── <skill-name>/
│       └── scenarios.yaml    # Test scenarios for the skill
│
├── fixtures/                 # Test fixtures (sample code, etc.)
├── reports/                  # Generated reports (gitignored)
├── package.json              # Dependencies (pnpm)
├── tsconfig.json             # TypeScript config
└── README.md                 # This file
```

## Usage

### CLI Runner

```bash
# Basic usage
pnpm harness <skill-name>

# Options
pnpm harness azure-ai-agents-py \
    --mock                  # Use mock responses (no Copilot SDK)
    --verbose               # Show detailed output
    --filter basic          # Filter scenarios by name/tag
    --output json           # Output format (text/json)
    --output-file report.json
```

### Tests

```bash
# Run all tests
pnpm test

# Run typecheck
pnpm typecheck
```

### Programmatic Usage

```typescript
import {
  AcceptanceCriteriaLoader,
  CodeEvaluator,
  SkillEvaluationRunner,
} from './harness';

// Load and evaluate code directly
const loader = new AcceptanceCriteriaLoader();
const criteria = loader.load('azure-ai-agents-py');
const evaluator = new CodeEvaluator(criteria);

const code = `
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
# ... your code
`;

const result = evaluator.evaluate(code, 'my-test');
console.log(`Passed: ${result.passed}, Score: ${result.score}`);

// Or run full evaluation
const runner = new SkillEvaluationRunner({ useMock: true });
const summary = await runner.run('azure-ai-agents-py');
console.log(`Pass rate: ${summary.passed}/${summary.totalScenarios}`);
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
pnpm harness <skill-name> --list

# Run evaluation
pnpm harness <skill-name> --mock --verbose

# Run all tests
pnpm test
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
- Requires Copilot CLI authentication
- Tests actual generation quality

```bash
# Run with real Copilot (if available)
pnpm harness azure-ai-agents-py
```

## Reports

### Console Output
```bash
pnpm harness azure-ai-agents-py --verbose
```

### Markdown Report
```typescript
import { MarkdownReporter } from './harness/reporters/markdown';

const reporter = new MarkdownReporter({ outputDir: 'tests/reports' });
const reportPath = reporter.generateReport(summary);
```

### JSON Output
```bash
pnpm harness azure-ai-agents-py --output json > report.json
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
- Install: `uv add github-copilot-sdk` (or use `--mock` flag)

### Tests pass in mock mode but fail with real Copilot
- Mock responses are manually crafted to be correct
- Real generated code may have different patterns
- Review acceptance criteria for flexibility

## Test Coverage Summary

**127 skills with 1128 test scenarios** — all skills have acceptance criteria and test scenarios.

| Language | Skills | Scenarios | Top Skills by Scenarios |
|----------|--------|-----------|-------------------------|
| Core | 5 | 40 | `azd-deployment` (8), `github-issue-creator` (8), `mcp-builder` (8) |
| Python | 41 | 358 | `azure-ai-projects-py` (12), `pydantic-models-py` (12), `azure-ai-translation-text-py` (11) |
| .NET | 29 | 296 | `azure-resource-manager-redis-dotnet` (14), `azure-resource-manager-sql-dotnet` (14), `azure-ai-projects-dotnet` (13) |
| TypeScript | 24 | 255 | `azure-storage-blob-ts` (17), `azure-servicebus-ts` (14), `azure-ai-contentsafety-ts` (12) |
| Java | 28 | 179 | `azure-identity-java` (12), `azure-storage-blob-java` (12), `azure-ai-agents-persistent-java` (11) |

For a complete list of skills with acceptance criteria, run:
```bash
uv run python -m harness.runner --list
```

## Contributing

1. Add acceptance criteria for new skills
2. Create comprehensive test scenarios
3. Ensure mock responses demonstrate correct patterns
4. Run full test suite before submitting
