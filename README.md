# Agent Skills

> [!WARNING]
> **Work in Progress** — This repository is actively being developed.

A collection of **skills**, **prompts**, **agents**, and **MCP server configurations** designed to supercharge your AI coding agents when working with Microsoft AI SDKs and Azure services.

> **📖 Read the full blog post:** [Context-Driven Development: Agent Skills for Microsoft Foundry and Azure](https://devblogs.microsoft.com/all-things-azure/context-driven-development-agent-skills-for-microsoft-foundry-and-azure/)

## What's This About?

This repo embraces **context-driven development** — the practice of providing AI coding agents with precisely the right context at the right time. The quality of agent output is directly proportional to the quality and relevance of context it receives.

![Context-Driven Development Architecture](https://raw.githubusercontent.com/microsoft/agent-skills/main/assets/context-driven-development.png)

Modern coding agents (GitHub Copilot CLI, [Claude Code](https://devblogs.microsoft.com/all-things-azure/claude-code-microsoft-foundry-enterprise-ai-coding-agent-setup/), [Codex](https://devblogs.microsoft.com/all-things-azure/codex-azure-openai-integration-fast-secure-code-development/), etc.) are powerful out of the box, but they lack domain-specific knowledge about your SDKs, patterns, and best practices. This repo provides the "onboarding guides" that turn general-purpose agents into specialized experts.

> [!IMPORTANT]
> **Don't Use All Skills at Once — Avoid Context Rot**
>
> Skills are designed to be used selectively. **Context rot** occurs when an agent's context window becomes cluttered with irrelevant or outdated information, degrading response quality and causing the agent to lose focus on what matters.
>
> Loading all skills at once will:
> - Dilute the agent's attention across unrelated domains
> - Waste precious context window tokens
> - Cause the agent to conflate patterns from different frameworks
>
> **Only copy the specific skills that are absolutely essential for your current project.**

## Repository Structure

```
.github/
├── skills/           # Modular knowledge packages for specific domains
├── prompts/          # Reusable prompt templates (.prompt.md)
├── agents/           # Agent persona definitions (.agent.md)
├── agents.md         # Project-wide agent instructions
├── copilot-instructions.md
└── workflows/        # Automated workflows (e.g., docs sync)

.vscode/
└── mcp.json          # MCP server configurations
```

## Available Skills

Each skill is a self-contained knowledge package with a `SKILL.md` file. **Copy only the skills you need** to your project's `.github/skills/` directory.

| Skill | Location | Description |
|-------|----------|-------------|
| `azd-deployment` | `.github/skills/azd-deployment/` | Azure Developer CLI deployment to Container Apps with Bicep |
| `azure-ai-search-python` | `.github/skills/azure-ai-search-python/` | Azure AI Search SDK patterns, vector/hybrid search, agentic retrieval |
| `azure-ai-voicelive-skill` | `.github/skills/azure-ai-voicelive-skill/` | Azure AI Voice Live SDK integration |
| `cosmos-db-python-skill` | `.github/skills/cosmos-db-python-skill/` | Cosmos DB NoSQL with Python/FastAPI, CRUD patterns |
| `fastapi-router` | `.github/skills/fastapi-router/` | FastAPI routers with CRUD, auth, and response models |
| `foundry-iq-python` | `.github/skills/foundry-iq-python/` | Agentic retrieval with knowledge bases and Foundry Agent Service |
| `foundry-nextgen-frontend` | `.github/skills/foundry-nextgen-frontend/` | NextGen Design System UI patterns (Vite + React) |
| `issue-creator` | `.github/skills/issue-creator/` | GitHub issue creation patterns |
| `mcp-builder` | `.github/skills/mcp-builder/` | Building MCP servers (Python/Node) |
| `podcast-generation` | `.github/skills/podcast-generation/` | Podcast generation workflows |
| `pydantic-models` | `.github/skills/pydantic-models/` | Pydantic v2 multi-model patterns (Base/Create/Update/Response) |
| `react-flow-node` | `.github/skills/react-flow-node/` | React Flow custom nodes with TypeScript and Zustand |
| `skill-creator` | `.github/skills/skill-creator/` | Guide for creating new skills |
| `zustand-store` | `.github/skills/zustand-store/` | Zustand stores with TypeScript and subscribeWithSelector |

### Using Skills with Multiple Agents

If you want to use skills across multiple projects or with different agents, you can create symlinks instead of copying files:

<details>
<summary><strong>macOS/Linux</strong></summary>

```bash
# Create the skills directory if it doesn't exist
mkdir -p /path/to/your-project/.github/skills

# Symlink a specific skill
ln -s /path/to/agent-skills/.github/skills/mcp-builder /path/to/your-project/.github/skills/mcp-builder
```

</details>

<details>
<summary><strong>Windows (Command Prompt as Administrator)</strong></summary>

```cmd
:: Create the skills directory if it doesn't exist
mkdir "C:\path\to\your-project\.github\skills"

:: Symlink a specific skill (use mklink /D for directories)
mklink /D "C:\path\to\your-project\.github\skills\mcp-builder" "C:\path\to\agent-skills\.github\skills\mcp-builder"
```

</details>

<details>
<summary><strong>Windows (PowerShell as Administrator)</strong></summary>

```powershell
New-Item -ItemType SymbolicLink -Path "C:\path\to\your-project\.github\skills\mcp-builder" -Target "C:\path\to\agent-skills\.github\skills\mcp-builder"
```

</details>

### Prompts

Reusable prompt templates for common tasks like code reviews, creating components, and adding endpoints.

### Agents

Persona definitions that give coding agents specific roles and context (e.g., `backend.agent.md`, `frontend.agent.md`, `planner.agent.md`).

### MCP Servers

Pre-configured Model Context Protocol servers in `.vscode/mcp.json` for tools like:
- GitHub, Playwright, Terraform
- Microsoft Docs, DeepWiki, Context7
- Sequential Thinking, Memory, and more

## Scaling to Larger Codebases

For larger codebases where static skills aren't enough, consider these approaches:

- **Graph RAG for Code** — Systems that build a retrieval-augmented generation layer over your codebase, enabling semantic search across functions, classes, and modules
- **AST-based Memory Systems** — Tools that maintain a hierarchical graph representation of your code's abstract syntax tree, allowing agents to navigate and understand code structure
- **Context Graph** — Memory systems that build knowledge graphs from your codebase, tracking relationships between components, dependencies, and call patterns

These approaches help agents maintain understanding of large codebases without cramming everything into the context window.

## Foundry Documentation via Context7

This repo includes indexed Microsoft Foundry documentation available through [Context7](https://context7.com). If you want Foundry docs accessible to your agent:

**Use this Context7 URL:** https://context7.com/microsoft/agent-skills

A GitHub workflow (`.github/workflows/update-llms-txt.md`) runs weekly to automatically sync the latest Foundry documentation updates to Context7. This ensures the indexed docs stay current with Microsoft Learn.

> [!NOTE]
> We're working towards streamlining this directly from Foundry itself. For now, use the Context7 integration.

## Quick Start

1. **Copy only the skills you need** to your project's `.github/skills/` directory (or use symlinks)
2. **Configure your agent** to use the instruction files:
   - For VS Code Copilot: Skills are auto-discovered from `.github/skills/`
   - For Claude: Reference `SKILL.md` files in your project instructions
3. **Use MCP servers** by copying `.vscode/mcp.json` to your project
4. **(Optional)** Add Context7 MCP server for Foundry docs access

## Contributing

This is an evolving collection. Feel free to:
- Add new skills for AI SDKs and Azure services
- Improve existing prompts and agent definitions
- Share MCP server configurations that work well

## License

MIT
