# Test Harness Agent Instructions

This folder contains a test harness for evaluating AI-generated code against acceptance criteria for skills.

## Quick Context

**What we're testing:** Skills in `.github/skills/` that provide domain knowledge for Azure SDKs.

**How it works:**
1. Each skill has **acceptance criteria** (correct/incorrect code patterns)
2. Test **scenarios** prompt code generation and validate the output
3. The harness runs scenarios using the [GitHub Copilot SDK](https://github.com/github/copilot-sdk) and scores generated code against criteria

## Current State

| Skill | Criteria | Scenarios | Status |
|-------|----------|-----------|--------|
| `azure-ai-projects-py` | Complete | Complete | Passing |

Run `pnpm harness --list` from the `tests/` directory to see all skills with criteria.

---

## Task: Add Test Coverage for a New Skill

### Step 1: Create Acceptance Criteria

**Location:** `.github/skills/<skill-name>/references/acceptance-criteria.md`

**Source materials** (in order of priority):
1. `.github/skills/<skill-name>/references/*.md` — existing reference docs
2. Official Microsoft Learn docs via `microsoft-docs` MCP
3. SDK source code patterns

**Format:**
```markdown
# Acceptance Criteria: <skill-name>

## Section Name

### Correct
\`\`\`python
# Working pattern
from azure.module import Client
\`\`\`

### Incorrect
\`\`\`python
# Anti-pattern with explanation
from wrong.module import Client  # Wrong import path
\`\`\`
```

**Critical:** Document import distinctions carefully. Many Azure SDKs have models in different locations (e.g., `azure.ai.agents.models` vs `azure.ai.projects.models`).

### Step 2: Create Test Scenarios

**Location:** `tests/scenarios/<skill-name>/scenarios.yaml`

**Template:**
```yaml
config:
  model: gpt-4
  max_tokens: 2000
  temperature: 0.3

scenarios:
  - name: scenario_name
    prompt: |
      Clear instruction for what code to generate.
      Include specific requirements.
    expected_patterns:
      - "Pattern that MUST appear"
      - "Another required pattern"
    forbidden_patterns:
      - "Pattern that must NOT appear"
    tags:
      - category
    mock_response: |
      # Complete working code example
      # This is used in mock mode
```

**Scenario design principles:**
- Each scenario tests ONE specific pattern or feature
- `expected_patterns` — patterns that MUST appear in generated code
- `forbidden_patterns` — common mistakes that must NOT appear
- `mock_response` — complete, working code that passes all checks
- `tags` — for filtering (`basic`, `async`, `streaming`, `tools`, etc.)

### Step 3: Verify

```bash
# Install dependencies (from tests directory)
cd tests && pnpm install

# Check skill is discovered
pnpm harness --list

# Run in mock mode (fast, deterministic)
pnpm harness <skill-name> --mock --verbose

# Run specific scenario
pnpm harness <skill-name> --mock --filter scenario_name

# Run tests
pnpm test
```

**Success criteria:**
- All scenarios pass (100% pass rate)
- No false positives (mock responses should always pass)
- Patterns catch real mistakes (forbidden patterns are meaningful)

---

## File Structure

```
tests/
├── harness/
│   ├── types.ts              # Type definitions
│   ├── criteria-loader.ts    # Parses acceptance-criteria.md
│   ├── evaluator.ts          # Validates code against patterns
│   ├── copilot-client.ts     # Code generation (mock/real)
│   ├── runner.ts             # CLI: pnpm harness
│   ├── ralph-loop.ts         # Iterative improvement controller
│   ├── feedback-builder.ts   # LLM-actionable feedback generator
│   ├── index.ts              # Package exports
│   └── reporters/            # Output formatters
│       ├── console.ts        # Console output
│       └── markdown.ts       # Markdown reports
│
├── scenarios/
│   ├── azure-ai-projects-py/
│   │   └── scenarios.yaml    # 12 scenarios
│
├── package.json              # Dependencies (pnpm)
├── tsconfig.json             # TypeScript config
└── README.md                 # Detailed documentation
```

**Acceptance criteria location:**
```
.github/skills/<skill-name>/references/acceptance-criteria.md
```

---

## Common Patterns to Test

### For Azure SDK Skills

| Pattern | What to Check |
|---------|---------------|
| **Imports** | Correct module paths (e.g., `azure.ai.agents` vs `azure.ai.projects`) |
| **Authentication** | `DefaultAzureCredential`, not hardcoded credentials |
| **Client creation** | Context managers (`with client:`) for resource cleanup |
| **Async variants** | Correct `.aio` imports for async code |
| **Models** | Import from correct module (varies by SDK) |

### Example: Import Distinctions

```yaml
# azure-ai-projects-py scenarios.yaml excerpt
- name: agent_with_code_interpreter
  expected_patterns:
    - "from azure.ai.agents.models import CodeInterpreterTool"  # LOW-LEVEL
  forbidden_patterns:
    - "from azure.ai.projects.models import CodeInterpreterTool"  # WRONG
```

---

## Commands Reference

All commands should be run from the `tests/` directory after `pnpm install`.

```bash
# List available skills
pnpm harness --list

# Run all scenarios for a skill (mock mode)
pnpm harness <skill> --mock --verbose

# Run filtered scenarios
pnpm harness <skill> --mock --filter <name-or-tag>

# Run with Ralph Loop (iterative improvement)
pnpm harness <skill> --ralph --mock --max-iterations 5 --threshold 85

# Run tests (all tests)
pnpm test

# Run specific test file
pnpm test:run harness/ralph-loop.test.ts

# Run typecheck
pnpm typecheck
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Skill not discovered | Check `acceptance-criteria.md` exists in `references/` |
| Scenario fails | Check `mock_response` actually contains expected patterns |
| Pattern not matching | Escape regex special chars, use raw strings |
| YAML parse error | Check indentation, use `|` for multiline strings |

---

## Next Skills to Add Coverage

Priority skills without test coverage (check with `--list`):

1. `azure-cosmos-db-py` — Cosmos DB patterns
2. `azure-search-documents-py` — Vector search, hybrid search
3. `azure-identity-py` — Authentication patterns
4. `azure-ai-voicelive-py` — Real-time voice AI

For each, follow the 3-step process above.

---

## Ralph Loop Development

> **Task Plan:** `.sisyphus/plans/ralph-loop-quality-tasks.md`

The Ralph Loop is an iterative code generation and improvement system that re-generates code until quality thresholds are met.

### What is Ralph Loop?

```
┌─────────────────────────────────────────────────────────────────┐
│                        Ralph Loop Controller                     │
│   (Orchestrates iterations, tracks progress, manages state)     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │   Generate  │──>│  Evaluate   │──>│  Analyze Failures   │   │
│  │    Code     │   │   (Score)   │   │  (Build Feedback)   │   │
│  └─────────────┘   └─────────────┘   └─────────────────────┘   │
│         ^                                      │                 │
│         └──────────────────────────────────────┘                 │
│                     (Loop until threshold met)                   │
└─────────────────────────────────────────────────────────────────┘
```

**Core flow:**
1. **Generate** code for a given skill/scenario
2. **Evaluate** against acceptance criteria (score 0-100)
3. **Analyze** failures and determine corrective actions
4. **Re-generate** with feedback until quality threshold is met (or max iterations)
5. **Report** on quality improvements across iterations

### Implementation Status

| Component | File | Status |
|-----------|------|--------|
| Ralph Loop Controller | `harness/ralph-loop.ts` | Complete |
| Feedback Builder | `harness/feedback-builder.ts` | Complete |
| CLI Integration | `harness/runner.ts` | Complete |
| Unit Tests | `harness/*.test.ts` | Complete (45 tests) |

### Using Ralph Loop

```bash
# Basic usage
pnpm harness azure-ai-projects-py --ralph --mock

# With custom settings
pnpm harness azure-ai-projects-py --ralph --max-iterations 5 --threshold 85 --mock --verbose
```

**Stop conditions:**
- Quality threshold met (default: 80)
- Perfect score (100)
- Max iterations reached (default: 5)
- No improvement between iterations
- Score regression

### Key Patterns

#### Match Existing Style

Look at these files for patterns:
- `harness/evaluator.ts` — Scoring logic, `EvaluationResult` structure
- `harness/criteria-loader.ts` — File loading, parsing
- `harness/runner.ts` — CLI integration, `SkillEvaluationRunner`

#### Test-Driven Development

Create tests alongside implementation:
```bash
# Example test file structure
tests/
├── harness/
│   ├── ralph-loop.ts         # Implementation
│   └── ralph-loop.test.ts    # Tests
```

Run tests:
```bash
cd tests
pnpm install
pnpm test:run harness/ralph-loop.test.ts -v
```

### Success Criteria

**Phase 1 is complete when:**
- [x] `--ralph` flag runs iterative loop on any skill
- [x] Feedback mechanism improves scores across iterations
- [x] All new code has test coverage (45 tests passing)

**Full implementation success:**
- 127 skills can run through Ralph Loop
- Average convergence in <5 iterations
- Quality scores improve by >20% from iteration 1 to final

---

## Pattern Matching: How the Evaluator Works

The evaluator validates generated code against acceptance criteria patterns. Understanding how it works helps you write effective criteria and debug failing tests.

### Pattern Types

| Pattern Type | Purpose | Matching Strategy |
|--------------|---------|-------------------|
| **Correct patterns** | Document expected usage | FLEXIBLE matching (allows variations) |
| **Incorrect patterns** | Document anti-patterns | EXACT matching (catches specific errors) |
| **Import-only patterns** | Wrong import paths | ALL imports must match |
| **Mixed patterns** | Import + misuse context | ALL parts must match |

### How Incorrect Patterns Are Evaluated

The evaluator distinguishes between two types of incorrect patterns:

#### 1. Import-Only Patterns (Pure Import Errors)

These show wrong import paths where the import itself is the error:

```python
# WRONG - clients are in azure.ai.contentsafety, not models
from azure.ai.contentsafety.models import ContentSafetyClient
```

**Matching:** If ALL imports in the pattern are present, it's flagged as incorrect.

#### 2. Mixed Patterns (Import + Misuse)

These show a valid import being misused:

```python
# WRONG - AnalyzeTextOptions is for text analysis only
from azure.ai.contentsafety.models import AnalyzeTextOptions

request = AnalyzeTextOptions(text="image.jpg")
response = client.analyze_image(request)  # <-- The actual error
```

**Matching:** BOTH the imports AND the non-import code (the misuse) must be present. This prevents false positives when:
- The import is valid for its intended use
- Only the misuse context makes it incorrect

### Why This Matters

**Bad behavior (before fix):**
```
Code: from azure.ai.contentsafety.models import AnalyzeTextOptions
      request = AnalyzeTextOptions(text="Hello")
      response = client.analyze_text(request)  # CORRECT usage!
      
Result: ❌ FALSE POSITIVE - flagged as incorrect because the import appears
        in an incorrect pattern, even though the misuse isn't present
```

**Good behavior (after fix):**
```
Code: from azure.ai.contentsafety.models import AnalyzeTextOptions
      request = AnalyzeTextOptions(text="Hello")
      response = client.analyze_text(request)  # CORRECT usage!
      
Result: ✅ PASSES - the import is only flagged when used incorrectly
        (e.g., with analyze_image instead of analyze_text)
```

### Writing Effective Acceptance Criteria

#### For Import-Only Errors

Use when the import path itself is wrong:

```markdown
### ❌ Incorrect: Wrong import path
\`\`\`python
# WRONG - clients are not in models submodule
from azure.ai.contentsafety.models import ContentSafetyClient
\`\`\`
```

#### For Misuse Errors

Show the FULL context - both the import and how it's being misused:

```markdown
### ❌ Incorrect: Using text models for image analysis
\`\`\`python
# WRONG - AnalyzeTextOptions is for text, not images
from azure.ai.contentsafety.models import AnalyzeTextOptions

request = AnalyzeTextOptions(text="image.jpg")
response = client.analyze_image(request)
\`\`\`
```

**Key principle:** The incorrect pattern should be the COMPLETE anti-pattern. Don't just show the import if the error is in how it's used.

### Debugging Failing Tests

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| False positive (valid code flagged) | Mixed pattern only checking imports | Ensure non-import lines show the actual error |
| False negative (bad code passes) | Pattern too specific | Relax exact matching or add more pattern variations |
| Score lower than expected | Multiple patterns matching | Check for overlapping incorrect patterns |

**Debug command:**
```bash
pnpm harness <skill> --mock --verbose
```

This shows which patterns matched and why each scenario passed/failed.

### Key Files

| File | Purpose |
|------|---------|
| `harness/evaluator.ts` | Pattern matching logic (`patternMatches`, `checkImports`) |
| `harness/criteria-loader.ts` | Parses acceptance-criteria.md into structured patterns |
| `harness/types.ts` | `CodePattern`, `EvaluationResult` types |
