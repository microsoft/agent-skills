# Agent Skills

Skills, prompts, and MCP configurations for AI coding agents working with Azure SDKs and Microsoft AI Foundry.

> **Blog post:** [Context-Driven Development: Agent Skills for Microsoft Foundry and Azure](https://devblogs.microsoft.com/all-things-azure/context-driven-development-agent-skills-for-microsoft-foundry-and-azure/)

![Context-Driven Development Architecture](https://raw.githubusercontent.com/microsoft/agent-skills/main/.github/assets/agent-skills-image.png)

---

Coding agents like [Copilot CLI](https://github.com/features/copilot/cli) are powerful, but they lack domain knowledge about your SDKs. The patterns are already in their weights from pretraining. All you need is the right activation context to surface them.

This repo provides that context:

- **[127 skills](#skill-catalog)** for Azure SDK and Microsoft Foundry development
- **[Live Foundry docs](https://context7.com/microsoft/agent-skills)** — Context7-indexed documentation, updated via GitHub Actions workflow
- **[MCP servers](https://github.com/microsoft/mcp)** — Full Model Context Protocol implementations for Azure services
- **Agent personas** — Role-specific agents (backend, frontend, infrastructure, planner) with domain expertise
- **[AGENTS.md](AGENTS.md)** — Template for configuring agent behavior in your projects

> [!IMPORTANT]
> **Use skills selectively.** Loading all skills causes context rot: diluted attention, wasted tokens, conflated patterns. Only copy skills essential for your current project.

---

## Quick Start

```bash
npx skills add microsoft/agent-skills
```

Select the skills you need from the wizard. Skills are installed to `.github/skills/` and auto-discovered by VS Code Copilot.

<details>
<summary>Manual installation</summary>

```bash
# Clone and copy specific skills
git clone https://github.com/microsoft/agent-skills.git
cp -r agent-skills/.github/skills/cosmos-db-py your-project/.github/skills/

# Or use symlinks for multi-project setups
ln -s /path/to/agent-skills/.github/skills/mcp-builder /path/to/your-project/.github/skills/mcp-builder

# Share skills across different agent configs in the same repo
ln -s ../.github/skills .opencode/skills
ln -s ../.github/skills .claude/skills
```

</details>

---

## Skill Catalog

> Location: `.github/skills/` • 127 skills

All skills in a flat structure for automatic discovery by `skills.sh` and VS Code Copilot.

| Language | Skills | Suffix | Examples |
|----------|--------|--------|----------|
| **Core** | 5 | — | `mcp-builder`, `skill-creator`, `azd-deployment` |
| [**Python**](CATALOG.md#python) | 42 | `-py` | `inference-py`, `cosmos-py`, `foundry-sdk-py` |
| [**.NET**](CATALOG.md#net) | 29 | `-dotnet` | `inference-dotnet`, `cosmosdb-dotnet`, `keyvault-dotnet` |
| [**TypeScript**](CATALOG.md#typescript) | 23 | `-ts` | `inference-ts`, `agents-ts`, `blob-ts` |
| [**Java**](CATALOG.md#java) | 28 | `-java` | `inference-java`, `cosmos-java`, `eventhubs-java` |

📖 **[Full skill catalog →](CATALOG.md)**

---

## Repository Structure

```
AGENTS.md                # Agent configuration template
CATALOG.md               # Full skill catalog

.github/
├── skills/              # All 127 skills (flat structure)
├── prompts/             # Reusable prompt templates
├── agents/              # Agent persona definitions
├── scripts/             # Automation scripts (doc scraping)
├── workflows/           # GitHub Actions (daily doc updates)
└── copilot-instructions.md

output/                  # Generated llms.txt files (daily workflow)
├── llms.txt             # Links + summaries
└── llms-full.txt        # Full content

skills/                  # Symlinks for backward compatibility
├── python/              # -> ../.github/skills/*-py
├── dotnet/              # -> ../.github/skills/*-dotnet
├── typescript/          # -> ../.github/skills/*-ts
└── java/                # -> ../.github/skills/*-java

.vscode/
└── mcp.json             # MCP server configurations
```

---

## MCP Servers

Reference configurations in [`.vscode/mcp.json`](.vscode/mcp.json):

| Category | Servers |
|----------|---------|
| **Documentation** | `microsoft-docs`, `context7`, `deepwiki` |
| **Development** | `github`, `playwright`, `terraform`, `eslint` |
| **Utilities** | `sequentialthinking`, `memory`, `markitdown` |

For full MCP server implementations for Azure services, see **[microsoft/mcp](https://github.com/microsoft/mcp)**.

---

## Additional Resources

### Agents

Role-specific agent personas in [`.github/agents/`](.github/agents/):

| Agent | Expertise |
|-------|-----------|
| `backend.agent.md` | FastAPI, Pydantic, Cosmos DB, Azure services |
| `frontend.agent.md` | React, TypeScript, React Flow, Zustand, Tailwind |
| `infrastructure.agent.md` | Bicep, Azure CLI, Container Apps, networking |
| `planner.agent.md` | Task decomposition, architecture decisions |
| `presenter.agent.md` | Documentation, demos, technical writing |

Use [`AGENTS.md`](AGENTS.md) as a template for configuring agent behavior in your own projects.

### Prompts

Reusable prompt templates in [`.github/prompts/`](.github/prompts/) for code reviews, component creation, and common workflows.

### Live Documentation

[Context7](https://context7.com/microsoft/agent-skills) indexes this repo's Foundry documentation with semantic search. Updated daily via [GitHub workflow](.github/workflows/update-llms-txt.md):

1. Scrapes the latest [Azure AI Foundry TOC](https://learn.microsoft.com/en-us/azure/ai-foundry/) from Microsoft Learn
2. Generates `llms.txt` (links + summaries) and `llms-full.txt` (full content)
3. Creates a PR if documentation has changed

These files follow the [llms.txt specification](https://llmstxt.org/) for LLM-friendly documentation.

---

## Contributing

- Add new skills for Azure SDKs
- Improve existing prompts and agents
- Share MCP server configurations

---

## License

MIT
