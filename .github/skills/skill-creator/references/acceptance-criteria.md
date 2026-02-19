# Skill Creator Acceptance Criteria

**Skill**: `skill-creator`
**Purpose**: Guide for creating effective skills for AI coding agents
**Focus**: SKILL.md format, YAML frontmatter, bundled resources, Azure SDK patterns

---

## 1. SKILL.md Structure

### 1.1 ✅ CORRECT: Complete SKILL.md with Frontmatter

```markdown
---
name: azure-example-py
description: |
  Azure Example SDK for Python. Use for creating and managing examples.
  Triggers: "create example", "list examples", "azure example sdk".
---

# Azure Example SDK

## Installation

\`\`\`bash
pip install azure-example
\`\`\`

## Environment Variables

\`\`\`bash
AZURE_EXAMPLE_ENDPOINT=https://<resource>.example.azure.com
\`\`\`

## Authentication

\`\`\`python
from azure.identity import DefaultAzureCredential
from azure.example import ExampleClient

credential = DefaultAzureCredential()
client = ExampleClient(
    endpoint=os.environ["AZURE_EXAMPLE_ENDPOINT"],
    credential=credential
)
\`\`\`

## Core Workflow

\`\`\`python
# Create
item = client.create_item(name="example")

# List
for item in client.list_items():
    print(item.name)

# Delete
client.delete_item(item_id)
\`\`\`

## Reference Files

| File | Contents |
|------|----------|
| [references/tools.md](references/tools.md) | Tool integrations |
```

### 1.2 ❌ INCORRECT: Missing Frontmatter

```markdown
# My Skill

This skill does stuff.
```

### 1.3 ❌ INCORRECT: Triggers in Body Instead of Description

```markdown
---
name: my-skill
description: A skill for doing things.
---

# My Skill

**When to use:** Use this skill when you need to do X, Y, or Z.
```

---

## 2. YAML Frontmatter

### 2.1 ✅ CORRECT: Complete Frontmatter

```yaml
---
name: azure-ai-agents-py
description: |
  Azure AI Agents SDK for Python. Use for creating agents with tools,
  managing threads, streaming responses, and function calling.
  Triggers: "create agent", "azure agents", "function calling", "streaming agents".
---
```

### 2.2 ✅ CORRECT: Single-Line Description

```yaml
---
name: pydantic-models-py
description: Pydantic v2 model patterns for FastAPI. Use for request/response models, validation, and serialization.
---
```

### 2.3 ❌ INCORRECT: Missing Name

```yaml
---
description: A skill for something.
---
```

### 2.4 ❌ INCORRECT: Missing Description

```yaml
---
name: my-skill
---
```

### 2.5 ❌ INCORRECT: No Trigger Phrases

```yaml
---
name: azure-search-py
description: Azure Search SDK for Python.
---
```

---

## 3. Skill Naming Convention

### 3.1 ✅ CORRECT: Language-Suffixed Names

| Pattern | Examples |
|---------|----------|
| Python | `azure-ai-agents-py`, `fastapi-router-py` |
| .NET | `azure-ai-agents-dotnet`, `azure-openai-dotnet` |
| TypeScript | `azure-ai-agents-ts`, `react-flow-node-ts` |
| Java | `azure-ai-agents-java`, `azure-cosmos-java` |
| Cross-language | `mcp-builder`, `skill-creator`, `copilot-sdk` |

### 3.2 ❌ INCORRECT: Wrong Naming Patterns

```
azure-ai-agents       # Missing language suffix
azure_ai_agents_py    # Uses underscores
AzureAiAgentsPy       # Uses camelCase
```

---

## 4. Description Best Practices

### 4.1 ✅ CORRECT: Description with What + When + Triggers

```yaml
description: |
  Azure AI Search SDK for Python. Use for vector search, hybrid search,
  index management, and document operations.
  Triggers: "semantic search", "vector index", "azure search", "hybrid search".
```

### 4.2 ✅ CORRECT: Concise Single-Line

```yaml
description: FastAPI router patterns with CRUD, auth, and response models. Triggers on "create router", "FastAPI endpoint", "API route".
```

### 4.3 ❌ INCORRECT: Too Verbose

```yaml
description: |
  This is a comprehensive skill that covers all aspects of the Azure AI Search
  SDK for Python. It includes detailed information about how to create indexes,
  manage documents, perform searches, and configure analyzers. The skill also
  covers advanced topics like vector search with embeddings, hybrid search
  combining keyword and vector approaches, and semantic ranking. Additionally,
  it provides guidance on authentication patterns using DefaultAzureCredential
  and environment variable configuration.
```

### 4.4 ❌ INCORRECT: No Usage Context

```yaml
description: Azure AI Search SDK for Python.
```

---

## 5. Skill Body Structure

### 5.1 ✅ CORRECT: Section Order for Azure SDK Skills

```markdown
# SDK Name

## Installation
[pip/npm/dotnet install commands]

## Environment Variables
[Required configuration]

## Authentication
[DefaultAzureCredential pattern]

## Core Workflow
[Minimal working example]

## Feature Tables
[Clients, methods, options]

## Best Practices
[Numbered list]

## Reference Files
[Table linking to /references/*.md]
```

### 5.2 ✅ CORRECT: Reference File Table

```markdown
## Reference Files

| File | Contents |
|------|----------|
| [references/tools.md](references/tools.md) | Tool configurations |
| [references/streaming.md](references/streaming.md) | Event streaming patterns |
| [references/async.md](references/async.md) | Async/await patterns |
```

### 5.3 ❌ INCORRECT: Missing Authentication Section

```markdown
# Azure Example SDK

## Installation
\`\`\`bash
pip install azure-example
\`\`\`

## Core Workflow
\`\`\`python
client = ExampleClient()  # How to authenticate?
\`\`\`
```

---

## 6. Authentication Patterns

### 6.1 ✅ CORRECT: DefaultAzureCredential (Python)

```python
from azure.identity import DefaultAzureCredential
from azure.example import ExampleClient

credential = DefaultAzureCredential()
client = ExampleClient(
    endpoint=os.environ["AZURE_EXAMPLE_ENDPOINT"],
    credential=credential
)
```

### 6.2 ✅ CORRECT: DefaultAzureCredential (.NET)

```csharp
using Azure.Identity;
using Azure.Example;

var credential = new DefaultAzureCredential();
var client = new ExampleClient(
    new Uri(Environment.GetEnvironmentVariable("AZURE_EXAMPLE_ENDPOINT")),
    credential
);
```

### 6.3 ✅ CORRECT: DefaultAzureCredential (TypeScript)

```typescript
import { DefaultAzureCredential } from "@azure/identity";
import { ExampleClient } from "@azure/example";

const credential = new DefaultAzureCredential();
const client = new ExampleClient(
  process.env.AZURE_EXAMPLE_ENDPOINT!,
  credential
);
```

### 6.4 ❌ INCORRECT: Hardcoded Credentials

```python
# WRONG - Never hardcode credentials
client = ExampleClient(
    endpoint="https://my-resource.azure.com",
    api_key="sk-12345"
)
```

---

## 7. Directory Structure

### 7.1 ✅ CORRECT: Standard Skill Structure

```
skill-name/
├── SKILL.md              # Required - main skill file
└── references/           # Optional - detailed docs
    ├── tools.md
    ├── streaming.md
    └── acceptance-criteria.md
```

### 7.2 ✅ CORRECT: Skill with Scripts

```
skill-name/
├── SKILL.md
├── scripts/              # Executable utilities
│   ├── init_project.py
│   └── validate.py
└── references/
    └── patterns.md
```

### 7.3 ❌ INCORRECT: README in Skill Directory

```
skill-name/
├── SKILL.md
├── README.md            # Don't include - agents don't need meta-docs
└── CHANGELOG.md         # Don't include
```

---

## 8. Progressive Disclosure

### 8.1 ✅ CORRECT: Main Content in SKILL.md, Details in References

**SKILL.md (under 500 lines):**
```markdown
# Azure AI Agents SDK

## Quick Start
[Minimal example]

## Tools
For detailed tool configurations, see [references/tools.md](references/tools.md)

## Streaming
For streaming patterns, see [references/streaming.md](references/streaming.md)
```

**references/tools.md:**
```markdown
# Tool Configurations

## FunctionTool
[Detailed content...]

## CodeInterpreterTool
[Detailed content...]
```

### 8.2 ❌ INCORRECT: Everything in SKILL.md

```markdown
# Azure AI Agents SDK

[800+ lines of content including every tool, every pattern, 
every edge case, making the skill too large to be useful]
```

---

## 9. Code Examples

### 9.1 ✅ CORRECT: Complete, Runnable Examples

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

# Initialize
credential = DefaultAzureCredential()
client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=credential
)

# Create agent
agent = client.create_agent(
    model="gpt-4o",
    name="my-agent",
    instructions="You are a helpful assistant."
)

# Cleanup
client.delete_agent(agent.id)
```

### 9.2 ❌ INCORRECT: Incomplete Examples

```python
# Create agent
agent = client.create_agent(...)  # What parameters?

# Missing: imports, initialization, cleanup
```

---

## 10. Content Guidelines

### 10.1 ✅ CORRECT: Concise, Actionable Content

```markdown
## Best Practices

1. Always use `DefaultAzureCredential` for authentication
2. Close clients with context managers: `with client:`
3. Use `create_or_update_*` for idempotent operations
4. Handle pagination with `for item in client.list_items():`
```

### 10.2 ❌ INCORRECT: Redundant Explanations

```markdown
## Best Practices

The DefaultAzureCredential class is a credential that provides a default
authentication flow for applications that will be deployed to Azure. It
attempts to authenticate using multiple methods in a specific order until
one succeeds. The methods tried are, in order: EnvironmentCredential,
WorkloadIdentityCredential, ManagedIdentityCredential, SharedTokenCacheCredential,
VisualStudioCredential, VisualStudioCodeCredential, AzureCliCredential, and
AzurePowerShellCredential. Each credential type has its own set of requirements...
[continues for 500 more words]
```

---

## 11. Anti-Patterns Summary

| Anti-Pattern | Impact | Fix |
|--------------|--------|-----|
| Missing frontmatter | Skill won't load | Add `---` delimited YAML |
| No triggers in description | Won't activate correctly | Add "Use when..." and trigger phrases |
| Hardcoded credentials | Security risk | Use `DefaultAzureCredential` |
| Missing auth section | Agents improvise poorly | Always include auth pattern |
| Too verbose description | Token waste | Keep under 200 words |
| Everything in SKILL.md | Context overflow | Split into references |
| README.md included | Unnecessary | Agents don't need meta-docs |
| Incomplete examples | Agents fill gaps poorly | Show full working code |

---

## 12. Checklist for New Skills

### Frontmatter
- [ ] Has `name` field with correct format (e.g., `azure-example-py`)
- [ ] Has `description` with what it does AND when to use it
- [ ] Description includes trigger phrases

### Structure
- [ ] SKILL.md under 500 lines
- [ ] Follows section order: Install → Env → Auth → Core → Features → References
- [ ] Large content split into `references/` files

### Authentication
- [ ] Uses `DefaultAzureCredential` (never hardcoded)
- [ ] Shows environment variable configuration
- [ ] Includes cleanup/close in examples

### Quality
- [ ] No README.md, CHANGELOG.md, or meta-docs
- [ ] All code examples are complete and runnable
- [ ] References organized by feature, not by length
- [ ] Instructs to search `microsoft-docs` MCP for current APIs

### Naming
- [ ] Uses lowercase with hyphens
- [ ] Has language suffix (`-py`, `-dotnet`, `-ts`, `-java`) unless cross-language
- [ ] Matches existing naming conventions in repository
