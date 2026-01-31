# Test Harness Agent Instructions

This folder contains a test harness for evaluating AI-generated code against acceptance criteria for skills.

## Quick Context

**What we're testing:** Skills in `.github/skills/` that provide domain knowledge for Azure SDKs.

**How it works:**
1. Each skill has **acceptance criteria** (correct/incorrect code patterns)
2. Test **scenarios** prompt code generation and validate the output
3. The harness runs scenarios and scores generated code against criteria

## Current State

| Skill | Criteria | Scenarios | Status |
|-------|----------|-----------|--------|
| `azure-ai-agents-py` | ✅ Complete | ✅ Complete | Passing |
| `azure-ai-projects-py` | ✅ Complete | ✅ Complete | Passing |

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

### ✅ Correct
```python
# Working pattern
from azure.module import Client
```

### ❌ Incorrect
```python
# Anti-pattern with explanation
from wrong.module import Client  # Wrong import path
```
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
│   ├── index.ts              # Package exports
│   └── reporters/            # Output formatters
│       ├── console.ts        # Console output
│       └── markdown.ts       # Markdown reports
│
├── scenarios/
│   ├── azure-ai-agents-py/
│   │   └── scenarios.yaml    # 7 scenarios
│   └── azure-ai-projects-py/
│       └── scenarios.yaml    # 12 scenarios
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

# Run tests (all tests)
pnpm test

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

1. `azure-ai-inference-py` — Chat completions, embeddings
2. `azure-cosmos-db-py` — Cosmos DB patterns
3. `azure-search-documents-py` — Vector search, hybrid search
4. `azure-identity-py` — Authentication patterns
5. `azure-ai-voicelive-py` — Real-time voice AI

For each, follow the 3-step process above.

---

## Ralph Loop Development

> **Task Plan:** `.sisyphus/plans/ralph-loop-quality-tasks.md`

The Ralph Loop is an iterative code generation and improvement system that re-generates code until quality thresholds are met. This section guides agents working on Ralph Loop implementation across multiple sessions.

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

### Development Phases

| Phase | Description | Priority | Status |
|-------|-------------|----------|--------|
| **Phase 1** | Core Ralph Loop Implementation | High | 🔲 Not Started |
| **Phase 2** | Extended Quality Scoring | Medium | 🔲 Blocked by Phase 1 |
| **Phase 3** | Advanced Features | Low | 🔲 Blocked by Phase 2 |
| **Phase 4** | Integration & Automation | Medium | 🔲 Blocked by Phase 1 |

### Multi-Session Workflow

#### Before Starting

1. **Read the task plan** — `.sisyphus/plans/ralph-loop-quality-tasks.md`
2. **Check phase dependencies** — Don't start Phase 2 until Phase 1 is complete
3. **Check task status** — Look for `🔄 In Progress` markers in the task plan
4. **Claim your task** — Add your session ID to the task you're working on

#### Claiming a Task

Edit the task plan to mark your task as in-progress:

```markdown
### Task 1.1: Create Ralph Loop Controller
**Status:** 🔄 In Progress (session: abc123)
**Started:** 2026-01-31
```

#### Completing a Task

Before marking complete:
- [ ] Implementation complete
- [ ] Tests written and passing (`tests/test_*.py`)
- [ ] Documentation updated (docstrings, inline comments)
- [ ] This file (`tests/AGENTS.md`) updated if public API changed
- [ ] Task plan updated with completion status

Update the task plan:
```markdown
### Task 1.1: Create Ralph Loop Controller
**Status:** ✅ Complete (session: abc123)
**Completed:** 2026-01-31
```

### Phase 1 Tasks (Start Here)

| Task | File | Description |
|------|------|-------------|
| 1.1 | `harness/ralph_loop.py` | Core loop controller with config, iteration tracking |
| 1.2 | `harness/feedback_builder.py` | Build LLM-actionable feedback from findings |
| 1.3 | `harness/runner.py` (modify) | Add `--ralph` CLI flag and loop mode |
| 1.4 | `harness/reporters/ralph_reporter.py` | Iteration progress reporting |

**Start with Task 1.1** — All other Phase 1 tasks depend on it.

### Key Patterns to Follow

#### Match Existing Style

Look at these files for patterns:
- `harness/evaluator.py` — Scoring logic, `EvaluationResult` structure
- `harness/criteria_loader.py` — File loading, parsing
- `harness/runner.py` — CLI integration, `SkillEvaluationRunner`

#### Test-Driven Development

Create tests alongside implementation:
```bash
# Example for Task 1.1
tests/
├── harness/
│   └── ralph_loop.py         # Implementation
└── test_ralph_loop.py        # Tests
```

Run tests:
```bash
cd tests
uv sync
uv run pytest test_ralph_loop.py -v
```

### Commands Reference

```bash
# Install dependencies
cd tests && uv sync

# List skills with test coverage
uv run python -m harness.runner --list

# Run existing harness (verify nothing broken)
uv run python -m harness.runner azure-ai-agents-py --mock --verbose

# Run tests
uv run pytest test_*.py -v

# After Ralph Loop is implemented:
uv run python -m harness.runner azure-ai-agents-py --ralph --max-iterations 5 --threshold 85
```

### Success Criteria

**Phase 1 is complete when:**
- [ ] `--ralph` flag runs iterative loop on any skill
- [ ] Feedback mechanism improves scores across iterations
- [ ] Markdown reports show iteration progress
- [ ] All new code has test coverage

**Full implementation success:**
- 127 skills can run through Ralph Loop
- Average convergence in <5 iterations
- Quality scores improve by >20% from iteration 1 to final
