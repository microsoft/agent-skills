# Agent Skills

> [!WARNING]
> **Work in Progress** — This repository is actively being developed.

A collection of **skills**, **prompts**, **agents**, and **MCP server configurations** designed to supercharge your AI coding agents when working with Microsoft AI SDKs and Azure services.

> **Read the full blog post:** [Context-Driven Development: Agent Skills for Microsoft Foundry and Azure](https://devblogs.microsoft.com/all-things-azure/context-driven-development-agent-skills-for-microsoft-foundry-and-azure/)

---

## What's This About?

This repo embraces **context-driven development** — providing AI coding agents with precisely the right context at the right time. The quality of agent output is directly proportional to the quality and relevance of context it receives.

![Context-Driven Development Architecture](https://raw.githubusercontent.com/microsoft/agent-skills/main/assets/agent-skills-image.png)

Modern coding agents (GitHub Copilot CLI, [Claude Code](https://devblogs.microsoft.com/all-things-azure/claude-code-microsoft-foundry-enterprise-ai-coding-agent-setup/), [Codex](https://devblogs.microsoft.com/all-things-azure/codex-azure-openai-integration-fast-secure-code-development/), etc.) are powerful out of the box, but lack domain-specific knowledge about your SDKs, patterns, and best practices. This repo provides the "onboarding guides" that turn general-purpose agents into specialized experts.

> [!IMPORTANT]
> **Don't Use All Skills at Once — Avoid Context Rot**
>
> Skills are designed to be used selectively. **Context rot** occurs when an agent's context window becomes cluttered with irrelevant information, degrading response quality.
>
> Loading all skills at once will:
> - Dilute the agent's attention across unrelated domains
> - Waste precious context window tokens
> - Cause the agent to conflate patterns from different frameworks
>
> **Only copy the specific skills essential for your current project.**

---

## Repository Structure

```
.github/
├── skills/           # Core + Python skills (auto-discovered by agents)
├── prompts/          # Reusable prompt templates (.prompt.md)
├── agents/           # Agent persona definitions (.agent.md)
├── agents.md         # Project-wide agent instructions
├── copilot-instructions.md
└── workflows/        # Automated workflows (e.g., docs sync)

skills/               # Extended skill catalog (copy what you need)
├── python/           # Python SDK skills organized by product area
├── dotnet/           # .NET SDK skills organized by product area
└── typescript/       # TypeScript/frontend skills

.vscode/
└── mcp.json          # MCP server configurations
```

---

## Quick Start

1. **Browse the skill catalog** and identify skills relevant to your project
2. **Copy the skill folder** to your project's `.github/skills/` directory:
   ```bash
   cp -r skills/dotnet/messaging/servicebus /path/to/your-project/.github/skills/
   ```
3. **Configure your agent** to use the skill files:
   - **VS Code Copilot:** Skills are auto-discovered from `.github/skills/`
   - **Claude:** Reference `SKILL.md` files in your project instructions
4. **(Optional)** Copy `.vscode/mcp.json` to enable MCP servers

---

## Skill Catalog

### Core Skills

> Location: `.github/skills/` — Auto-discovered by agents

| Skill | Description |
|-------|-------------|
| [skill-creator](.github/skills/skill-creator/) | Guide for creating new skills — based on [Anthropic's skill-creator](https://github.com/anthropics/anthropic-quickstarts/tree/main/skills/skill-creator) |
| [mcp-builder](.github/skills/mcp-builder/) | Building MCP servers (TypeScript, Python, C#/.NET) |
| [github-issue-creator](.github/skills/github-issue-creator/) | Convert raw notes, error logs, or screenshots into structured GitHub issues |
| [azd-deployment](.github/skills/azd-deployment/) | Azure Developer CLI deployment to Container Apps with Bicep |

---

### Python Skills (Core)

> Location: `.github/skills/` — Auto-discovered by agents

#### Azure AI & Foundry

| Skill | Description |
|-------|-------------|
| [azure-ai-agents-python](.github/skills/azure-ai-agents-python/) | Low-level Azure AI Agents SDK — agent CRUD, threads, streaming, tools |
| [azure-ai-search-python](.github/skills/azure-ai-search-python/) | Azure AI Search SDK — vector/hybrid search, agentic retrieval |
| [azure-ai-voicelive](.github/skills/azure-ai-voicelive/) | Real-time voice AI with bidirectional WebSocket communication |
| [agent-framework-azure-hosted-agents](.github/skills/agent-framework-azure-hosted-agents/) | Microsoft Agent Framework SDK for persistent Azure AI Foundry agents |
| [foundry-iq-python](.github/skills/foundry-iq-python/) | Agentic retrieval with knowledge bases and Foundry Agent Service |
| [foundry-sdk-python](.github/skills/foundry-sdk-python/) | High-level Azure AI Projects SDK for Foundry integration and evaluations |

#### Backend & Data

| Skill | Description |
|-------|-------------|
| [cosmos-db-python-skill](.github/skills/cosmos-db-python-skill/) | Cosmos DB NoSQL with Python/FastAPI, CRUD patterns |
| [fastapi-router](.github/skills/fastapi-router/) | FastAPI routers with CRUD, auth, and response models |
| [pydantic-models](.github/skills/pydantic-models/) | Pydantic v2 multi-model patterns (Base/Create/Update/Response) |
| [podcast-generation](.github/skills/podcast-generation/) | Podcast generation workflows |

---

### Python Skills (Extended)

> Location: `skills/python/` — Copy to your project's `.github/skills/` as needed

<details>
<summary><strong>Foundry</strong> (3 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [contentsafety](skills/python/foundry/contentsafety/) | `azure-ai-contentsafety` | Content moderation and safety |
| [contentunderstanding](skills/python/foundry/contentunderstanding/) | `azure-ai-contentunderstanding` | Document and media understanding |
| [evaluation](skills/python/foundry/evaluation/) | `azure-ai-evaluation` | AI model evaluation and metrics |

</details>

<details>
<summary><strong>AI</strong> (9 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [inference](skills/python/ai/inference/) | `azure-ai-inference` | Azure AI Model Inference for chat, embeddings |
| [ml](skills/python/ai/ml/) | `azure-ai-ml` | Azure Machine Learning SDK v2 |
| [textanalytics](skills/python/ai/textanalytics/) | `azure-ai-textanalytics` | Text Analytics — NER, sentiment, key phrases |
| [transcription](skills/python/ai/transcription/) | `azure-cognitiveservices-speech` | Speech-to-text transcription |
| [translation-document](skills/python/ai/translation-document/) | `azure-ai-translation-document` | Document translation (batch) |
| [translation-text](skills/python/ai/translation-text/) | `azure-ai-translation-text` | Text translation API |
| [vision-imageanalysis](skills/python/ai/vision-imageanalysis/) | `azure-ai-vision-imageanalysis` | Image analysis, captions, tags, objects |
| [weightsandbiases](skills/python/ai/weightsandbiases/) | `wandb` | Weights & Biases ML experiment tracking |

</details>

<details>
<summary><strong>Search</strong> (1 skill)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [documents](skills/python/search/documents/) | `azure-search-documents` | Azure AI Search indexing and querying |

</details>

<details>
<summary><strong>Data</strong> (8 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [blob](skills/python/data/blob/) | `azure-storage-blob` | Blob storage operations, containers, SAS tokens |
| [cosmos](skills/python/data/cosmos/) | `azure-cosmos` | Cosmos DB NoSQL API operations |
| [datalake](skills/python/data/datalake/) | `azure-storage-file-datalake` | Data Lake Storage Gen2, hierarchical namespace |
| [fileshare](skills/python/data/fileshare/) | `azure-storage-file-share` | Azure Files SMB shares |
| [queue](skills/python/data/queue/) | `azure-storage-queue` | Queue storage for async messaging |
| [storage-general](skills/python/data/storage-general/) | `azure-storage-*` | Common storage patterns and utilities |
| [tables](skills/python/data/tables/) | `azure-data-tables` | Azure Tables / Cosmos DB Table API |

</details>

<details>
<summary><strong>Identity</strong> (1 skill)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [azure-identity](skills/python/identity/azure-identity/) | `azure-identity` | DefaultAzureCredential, managed identity, service principals |

</details>

<details>
<summary><strong>Security</strong> (1 skill)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [keyvault](skills/python/security/keyvault/) | `azure-keyvault-*` | Key Vault secrets, keys, certificates |

</details>

<details>
<summary><strong>Integration</strong> (3 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [appconfiguration](skills/python/integration/appconfiguration/) | `azure-appconfiguration` | App Configuration key-values, feature flags |
| [apicenter](skills/python/integration/apicenter/) | `azure-mgmt-apicenter` | API Center for API inventory management |
| [apimanagement](skills/python/integration/apimanagement/) | `azure-mgmt-apimanagement` | API Management services, APIs, products |

</details>

<details>
<summary><strong>Messaging</strong> (5 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [eventgrid](skills/python/messaging/eventgrid/) | `azure-eventgrid` | Event Grid publishing and consumption |
| [eventhub](skills/python/messaging/eventhub/) | `azure-eventhub` | Event Hubs streaming data ingestion |
| [servicebus](skills/python/messaging/servicebus/) | `azure-servicebus` | Service Bus queues, topics, subscriptions |
| [webpubsub-client](skills/python/messaging/webpubsub-client/) | `azure-messaging-webpubsubclient` | Web PubSub real-time messaging (client-side) |
| [webpubsub-service](skills/python/messaging/webpubsub-service/) | `azure-messaging-webpubsubservice` | Web PubSub real-time messaging (server-side) |

</details>

<details>
<summary><strong>Monitoring</strong> (5 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [applicationinsights](skills/python/monitoring/applicationinsights/) | `azure-mgmt-applicationinsights` | Application Insights management |
| [ingestion](skills/python/monitoring/ingestion/) | `azure-monitor-ingestion` | Custom logs ingestion via DCR |
| [opentelemetry](skills/python/monitoring/opentelemetry/) | `azure-monitor-opentelemetry` | OpenTelemetry auto-instrumentation |
| [opentelemetry-exporter](skills/python/monitoring/opentelemetry-exporter/) | `azure-monitor-opentelemetry-exporter` | Manual OpenTelemetry export |
| [query](skills/python/monitoring/query/) | `azure-monitor-query` | Log Analytics and Metrics queries |

</details>

<details>
<summary><strong>Compute</strong> (2 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [botservice](skills/python/compute/botservice/) | `azure-mgmt-botservice` | Azure Bot Service management |
| [fabric](skills/python/compute/fabric/) | `azure-mgmt-fabric` | Microsoft Fabric capacity management |

</details>

<details>
<summary><strong>Container</strong> (1 skill)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [containerregistry](skills/python/container/containerregistry/) | `azure-containerregistry` | Container Registry operations |

</details>

<details>
<summary><strong>Partner</strong> (2 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [arize-ai-observability-eval](skills/python/partner/arize-ai-observability-eval/) | `arize` | Arize AI observability & evaluation |
| [mongodbatlas](skills/python/partner/mongodbatlas/) | `pymongo` | MongoDB Atlas with Python |

</details>

---

### .NET Skills

> Location: `skills/dotnet/` — Copy to your project's `.github/skills/` as needed

<details>
<summary><strong>AI</strong> (3 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [inference](skills/dotnet/ai/inference/) | `Azure.AI.Inference` | Azure AI Model Inference for chat completions, embeddings |
| [openai](skills/dotnet/ai/openai/) | `Azure.AI.OpenAI` | Azure OpenAI SDK for GPT models, DALL-E, embeddings |
| [weightsandbiases](skills/dotnet/ai/weightsandbiases/) | `Azure.ResourceManager.WeightsAndBiases` | Weights & Biases ML experiment tracking via Azure |

</details>

<details>
<summary><strong>Compute</strong> (3 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [botservice](skills/dotnet/compute/botservice/) | `Azure.ResourceManager.BotService` | Azure Bot Service management |
| [durabletask](skills/dotnet/compute/durabletask/) | `Azure.ResourceManager.DurableTask` | Durable Task Scheduler for orchestrations |
| [playwright](skills/dotnet/compute/playwright/) | `Microsoft.Playwright.Testing` | Azure Playwright Testing for browser automation |

</details>

<details>
<summary><strong>Data</strong> (6 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [cosmosdb](skills/dotnet/data/cosmosdb/) | `Azure.ResourceManager.CosmosDB` | Cosmos DB account, database, container management |
| [fabric](skills/dotnet/data/fabric/) | `Azure.ResourceManager.Fabric` | Microsoft Fabric capacity management |
| [mysql](skills/dotnet/data/mysql/) | `Azure.ResourceManager.MySql` | Azure Database for MySQL Flexible Server |
| [postgresql](skills/dotnet/data/postgresql/) | `Azure.ResourceManager.PostgreSql` | Azure Database for PostgreSQL Flexible Server |
| [redis](skills/dotnet/data/redis/) | `Azure.ResourceManager.Redis` | Azure Cache for Redis management |
| [sql](skills/dotnet/data/sql/) | `Azure.ResourceManager.Sql` | Azure SQL Database, servers, elastic pools |

**Reference docs available:** cosmosdb, sql

</details>

<details>
<summary><strong>Foundry</strong> (4 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [agents-persistent](skills/dotnet/foundry/agents-persistent/) | `Azure.AI.Agents.Persistent` | Persistent Azure AI Foundry agents with .NET |
| [document-intelligence](skills/dotnet/foundry/document-intelligence/) | `Azure.AI.DocumentIntelligence` | Document analysis, extraction, custom models |
| [projects](skills/dotnet/foundry/projects/) | `Azure.AI.Projects` | Azure AI Projects SDK for Foundry |
| [voicelive](skills/dotnet/foundry/voicelive/) | `Azure.AI.VoiceLive` | Real-time voice AI with .NET |

</details>

<details>
<summary><strong>Identity</strong> (2 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [azure-identity](skills/dotnet/identity/azure-identity/) | `Azure.Identity` | DefaultAzureCredential, managed identity, service principals |
| [authentication-events](skills/dotnet/identity/authentication-events/) | `Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents` | Entra ID authentication event handlers |

</details>

<details>
<summary><strong>Integration</strong> (2 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [apicenter](skills/dotnet/integration/apicenter/) | `Azure.ResourceManager.ApiCenter` | Azure API Center for API inventory management |
| [apimanagement](skills/dotnet/integration/apimanagement/) | `Azure.ResourceManager.ApiManagement` | Azure API Management services, APIs, products |

**Reference docs available:** apimanagement

</details>

<details>
<summary><strong>Location</strong> (1 skill)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [maps](skills/dotnet/location/maps/) | `Azure.Maps.*` | Azure Maps for geocoding, routing, search, rendering |

</details>

<details>
<summary><strong>Messaging</strong> (3 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [eventgrid](skills/dotnet/messaging/eventgrid/) | `Azure.Messaging.EventGrid` | Event Grid for event-driven architectures |
| [eventhubs](skills/dotnet/messaging/eventhubs/) | `Azure.Messaging.EventHubs` | Event Hubs for streaming data ingestion |
| [servicebus](skills/dotnet/messaging/servicebus/) | `Azure.Messaging.ServiceBus` | Service Bus for enterprise messaging |

</details>

<details>
<summary><strong>Monitoring</strong> (1 skill)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [applicationinsights](skills/dotnet/monitoring/applicationinsights/) | `Azure.ResourceManager.ApplicationInsights` | Application Insights for telemetry and diagnostics |

</details>

<details>
<summary><strong>Partner</strong> (2 skills)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [arize-ai-observability-eval](skills/dotnet/partner/arize-ai-observability-eval/) | `Azure.ResourceManager.Arize` | Arize AI observability & evaluation via Azure Marketplace |
| [mongodbatlas](skills/dotnet/partner/mongodbatlas/) | `Azure.ResourceManager.MongoCluster` | MongoDB Atlas organizations via Azure Marketplace |

</details>

<details>
<summary><strong>Search</strong> (1 skill)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [documents](skills/dotnet/search/documents/) | `Azure.Search.Documents` | Azure AI Search — vector, hybrid, semantic search |

**Reference docs available:** documents (vector-search, semantic-search)

</details>

<details>
<summary><strong>Security</strong> (1 skill)</summary>

| Skill | Package | Description |
|-------|---------|-------------|
| [keyvault](skills/dotnet/security/keyvault/) | `Azure.Security.KeyVault.Keys` | Key Vault for keys, secrets, certificates |

</details>

---

### TypeScript Skills

> Location: `skills/typescript/` — Copy to your project's `.github/skills/` as needed

<details>
<summary><strong>Frontend</strong> (2 skills)</summary>

| Skill | Description |
|-------|-------------|
| [zustand-store](skills/typescript/frontend/zustand-store/) | Zustand stores with TypeScript and subscribeWithSelector |
| [react-flow-node](skills/typescript/frontend/react-flow-node/) | React Flow custom nodes with TypeScript |

</details>

<details>
<summary><strong>Foundry</strong> (1 skill)</summary>

| Skill | Description |
|-------|-------------|
| [nextgen-frontend](skills/typescript/foundry/nextgen-frontend/) | NextGen Design System UI patterns (Vite + React + Framer Motion) |

**Reference docs available:** nextgen-frontend (components, design-tokens, patterns)

</details>

---

## Using Skills with Symlinks

If you want to share skills across projects without duplicating files:

<details>
<summary><strong>macOS / Linux</strong></summary>

```bash
mkdir -p /path/to/your-project/.github/skills
ln -s /path/to/agent-skills/skills/dotnet/messaging/servicebus \
      /path/to/your-project/.github/skills/servicebus
```

</details>

<details>
<summary><strong>Windows (Command Prompt as Admin)</strong></summary>

```cmd
mkdir "C:\project\.github\skills"
mklink /D "C:\project\.github\skills\servicebus" ^
          "C:\agent-skills\skills\dotnet\messaging\servicebus"
```

</details>

<details>
<summary><strong>Windows (PowerShell as Admin)</strong></summary>

```powershell
New-Item -ItemType SymbolicLink `
  -Path "C:\project\.github\skills\servicebus" `
  -Target "C:\agent-skills\skills\dotnet\messaging\servicebus"
```

</details>

---

## MCP Servers

Pre-configured Model Context Protocol servers in `.vscode/mcp.json`:

| Category | Servers |
|----------|---------|
| **Documentation** | `microsoft-docs`, `context7`, `deepwiki` |
| **Development** | `github`, `playwright`, `terraform`, `eslint` |
| **Utilities** | `sequentialthinking`, `memory`, `markitdown` |

Copy `.vscode/mcp.json` to your project to enable these integrations.

---

## Additional Resources

### Prompts

Reusable prompt templates (`.prompt.md`) for code reviews, component creation, and endpoint scaffolding.

### Agents

Persona definitions (`.agent.md`) that give coding agents specific roles: `backend`, `frontend`, `planner`, etc.

### Scaling to Larger Codebases

For codebases where static skills aren't enough:

- **Graph RAG for Code** — Retrieval-augmented generation over your codebase
- **AST-based Memory Systems** — Hierarchical graph of your code's abstract syntax tree
- **Context Graph** — Knowledge graphs tracking component relationships and dependencies

---

## Foundry Documentation via Context7

Indexed Microsoft Foundry documentation is available through [Context7](https://context7.com):

**URL:** https://context7.com/microsoft/agent-skills

A GitHub workflow runs weekly to sync the latest Foundry documentation updates.

---

## Contributing

This is an evolving collection. Contributions welcome:

- Add new skills for AI SDKs and Azure services
- Improve existing prompts and agent definitions
- Share MCP server configurations

---

## License

MIT
