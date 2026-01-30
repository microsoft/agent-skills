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

Run `python -m tests.harness.runner --list` to see all skills with criteria.

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
# Check skill is discovered
python -m tests.harness.runner --list

# Run in mock mode (fast, deterministic)
python -m tests.harness.runner <skill-name> --mock --verbose

# Run specific scenario
python -m tests.harness.runner <skill-name> --mock --filter scenario_name

# Run pytest
pytest tests/test_skills.py -v
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
│   ├── criteria_loader.py    # Parses acceptance-criteria.md
│   ├── evaluator.py          # Validates code against patterns
│   ├── copilot_client.py     # Code generation (mock/real)
│   ├── runner.py             # CLI: python -m tests.harness.runner
│   └── reporters/            # Output formatters
│
├── scenarios/
│   ├── azure-ai-agents-py/
│   │   └── scenarios.yaml    # 7 scenarios
│   └── azure-ai-projects-py/
│       └── scenarios.yaml    # 12 scenarios
│
├── test_skills.py            # Pytest integration
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

```bash
# List available skills
python -m tests.harness.runner --list

# Run all scenarios for a skill (mock mode)
python -m tests.harness.runner <skill> --mock --verbose

# Run filtered scenarios
python -m tests.harness.runner <skill> --mock --filter <name-or-tag>

# Run pytest (all tests)
pytest tests/ -v

# Run pytest (specific skill)
pytest tests/test_skills.py -k "<skill_name>" -v

# Check if criteria loads correctly
python -c "from tests.harness import AcceptanceCriteriaLoader; print(AcceptanceCriteriaLoader().load('<skill>'))"
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
