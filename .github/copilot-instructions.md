# Copilot Instructions for Agent Skills

## Project Overview

Agent Skills is a repository of skills, prompts, and MCP configurations for AI coding agents working with Azure SDKs and Microsoft AI Foundry services.

## ⚠️ Fresh Information First

**Azure SDKs and Foundry APIs change constantly. Never work with stale knowledge.**

Before implementing anything with Azure/Foundry SDKs:

1. **Search official docs first** — Use the Microsoft Docs MCP (`microsoft-docs`) to get current API signatures, parameters, and patterns
2. **Verify SDK versions** — Check `pip show <package>` for installed versions; APIs differ between versions
3. **Don't trust cached knowledge** — Your training data is outdated. The SDK you "know" may have breaking changes.

**If you skip this step and use outdated patterns, you will produce broken code.**

---

## Core Principles

Apply these principles to every task.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- If you write 200 lines and it could be 50, rewrite it.

**The test:** Would a senior engineer say this is overcomplicated? If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

**The test:** Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution (TDD)

**Define success criteria. Loop until verified.**

| Instead of... | Transform to... |
|---------------|-----------------|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Ensure tests pass before and after" |

---

## Repository Structure

```
.github/
├── skills/           # Domain-specific knowledge packages
│   └── */SKILL.md    # Each skill has YAML frontmatter + markdown body
├── prompts/          # Reusable prompt templates
├── agents/           # Agent persona definitions
└── copilot-instructions.md
```

## Skills

Skills are domain-specific knowledge packages in `.github/skills/`. Each skill has a `SKILL.md` with:
- **YAML frontmatter** (`name`, `description`) — triggers skill loading
- **Markdown body** — loaded only when skill activates

### Available Skills

| Skill | Purpose |
|-------|---------|
| `azure-ai-search-python` | Search SDK patterns, vector/hybrid search, agentic retrieval |
| `azure-ai-agents-python` | Low-level agents SDK for CRUD, threads, streaming, tools |
| `azure-ai-voicelive-skill` | Real-time voice AI with Azure AI Voice Live SDK |
| `foundry-sdk-python` | High-level Foundry project client, versioned agents, evals |
| `foundry-iq-python` | Agentic retrieval with knowledge bases |
| `foundry-nextgen-frontend` | NextGen Design System UI patterns (Vite + React) |
| `agent-framework-azure-hosted-agents` | Agent Framework SDK for persistent Azure agents |
| `azd-deployment` | Azure Developer CLI deployment to Container Apps with Bicep |
| `mcp-builder` | Building MCP servers (Python/Node) |
| `cosmos-db-python-skill` | Cosmos DB NoSQL with Python/FastAPI |
| `fastapi-router` | FastAPI routers with CRUD, auth, response models |
| `pydantic-models` | Pydantic v2 multi-model patterns |
| `zustand-store` | Zustand stores with TypeScript and subscribeWithSelector |
| `react-flow-node` | React Flow custom nodes with TypeScript |
| `podcast-generation` | Podcast generation workflows |
| `skill-creator` | Guide for creating new skills |
| `issue-creator` | GitHub issue creation patterns |

### Skill Selection

Only load skills relevant to the current task. Loading all skills causes context rot — diluted attention and conflated patterns.

---

## MCP Servers

Pre-configured Model Context Protocol servers in `.vscode/mcp.json` provide additional capabilities:

### Documentation & Search

| MCP | Purpose |
|-----|---------|
| `microsoft-docs` | **Search Microsoft Learn** — Official Azure/Foundry docs. Use this FIRST. |
| `context7` | Indexed documentation with semantic search |
| `deepwiki` | Ask questions about GitHub repositories |

### Development Tools

| MCP | Purpose |
|-----|---------|
| `github` | GitHub API operations |
| `playwright` | Browser automation and testing |
| `terraform` | Infrastructure as code |
| `eslint` | JavaScript/TypeScript linting |

### Utilities

| MCP | Purpose |
|-----|---------|
| `sequentialthinking` | Step-by-step reasoning for complex problems |
| `memory` | Persistent memory across sessions |
| `markitdown` | Convert documents to markdown |

**Usage:** MCPs are available when configured in your editor. Use `microsoft-docs` to search official documentation before implementing Azure SDK code.

---

## SDK Quick Reference

| Package | Purpose | Install |
|---------|---------|---------|
| `azure-ai-projects` | Foundry project client, agents, evals, connections | `pip install azure-ai-projects` |
| `azure-ai-agents` | Standalone agents client (use via projects) | `pip install azure-ai-agents` |
| `azure-search-documents` | Azure AI Search SDK | `pip install azure-search-documents` |
| `azure-identity` | Authentication | `pip install azure-identity` |

### Authentication Pattern

Always use `DefaultAzureCredential` for production:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

credential = DefaultAzureCredential()
client = AIProjectClient(
    endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
    credential=credential
)
```

### Environment Variables

```bash
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

---

## Conventions

### Code Style

- Prefer `async/await` for all Azure SDK I/O
- Use context managers: `with client:` or `async with client:`
- Close clients explicitly or use context managers
- Use `create_or_update_*` for idempotent operations
- Use type hints on all function signatures

### Clean Code Checklist

Before completing any code change:

- [ ] Functions do one thing
- [ ] Names are descriptive and intention-revealing
- [ ] No magic numbers or strings (use constants)
- [ ] Error handling is explicit (no empty catch blocks)
- [ ] No commented-out code
- [ ] Tests cover the change

### Testing Patterns

```python
# Arrange
service = ProjectService()
expected = Project(id="123", name="test")

# Act  
result = await service.get_project("123")

# Assert
assert result == expected
```

---

## Creating New Skills

1. Create a new directory under `.github/skills/<skill-name>/`
2. Add a `SKILL.md` file with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: Brief description of what the skill does and when to use it
   ---
   ```
3. Add detailed instructions in the markdown body
4. Keep skills focused on a single domain

---

## Do's and Don'ts

### Do

- ✅ Use `DefaultAzureCredential` for authentication
- ✅ Use async/await for all Azure SDK operations
- ✅ Write tests before or alongside implementation
- ✅ Keep functions small and focused
- ✅ Match existing patterns in the codebase

### Don't

- ❌ Hardcode credentials or endpoints
- ❌ Suppress type errors (`as any`, `@ts-ignore`, `# type: ignore`)
- ❌ Leave empty exception handlers
- ❌ Refactor unrelated code while fixing bugs
- ❌ Add dependencies without justification

---

## Success Indicators

These principles are working if you see:

- Fewer unnecessary changes in diffs
- Fewer rewrites due to overcomplication
- Clarifying questions come before implementation (not after mistakes)
- Clean, minimal PRs without drive-by refactoring
- Tests that document expected behavior
