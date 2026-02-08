# Agent Skills

[![Evals & Tests](https://img.shields.io/github/actions/workflow/status/microsoft/skills/test-harness.yml?branch=main&label=Evals%20%26%20Tests)](https://github.com/microsoft/skills/actions/workflows/test-harness.yml)
[![Copilot SDK Tests](https://img.shields.io/github/actions/workflow/status/microsoft/skills/skill-evaluation.yml?branch=main&label=Copilot%20SDK%20Tests)](https://github.com/microsoft/skills/actions/workflows/skill-evaluation.yml)
[![Install via skills.sh](https://img.shields.io/badge/skills.sh-install-blue)](https://skills.sh/microsoft/skills)
[![Documentation](https://img.shields.io/badge/docs-documentation-blue)](https://microsoft.github.io/skills/#documentation)

> [!NOTE]
> **Work in Progress** — This repository is under active development. More skills are being added, existing skills are being updated to use the latest SDK patterns, and tests are being expanded to ensure quality. Contributions welcome!

Skills, custom agents, AGENTS.md templates, and MCP configurations for AI coding agents working with Azure SDKs and Microsoft AI Foundry.

> **Blog post:** [Context-Driven Development: Agent Skills for Microsoft Foundry and Azure](https://devblogs.microsoft.com/all-things-azure/context-driven-development-agent-skills-for-microsoft-foundry-and-azure/)

> **🔍 Skill Explorer:** [Browse all 130 skills with 1-click install](https://microsoft.github.io/skills/)

## Quick Start

```bash
npx skills add microsoft/skills
```

Select the skills you need from the wizard. Skills are installed to your chosen agent's directory (e.g., `.github/skills/` for GitHub Copilot) and symlinked if you use multiple agents.

<details>
<summary>Alternative installation methods</summary>

**Manual installation (git clone)**

```bash
# Clone and copy specific skills
git clone https://github.com/microsoft/skills.git
cp -r agent-skills/.github/skills/azure-cosmos-db-py your-project/.github/skills/

# Or use symlinks for multi-project setups
ln -s /path/to/agent-skills/.github/skills/mcp-builder /path/to/your-project/.github/skills/mcp-builder

# Share skills across different agent configs in the same repo
ln -s ../.github/skills .opencode/skills
ln -s ../.github/skills .claude/skills
```

</details>

---

Coding agents like [Copilot CLI](https://github.com/features/copilot/cli) are powerful, but they lack domain knowledge about your SDKs. The patterns are already in their weights from pretraining. All you need is the right activation context to surface them.

> [!IMPORTANT]
> **Use skills selectively.** Loading all skills causes context rot: diluted attention, wasted tokens, conflated patterns. Only copy skills essential for your current project.

---

![Context-Driven Development Architecture](https://raw.githubusercontent.com/microsoft/skills/main/.github/assets/agent-skills-image.png)

---

## What's Inside

| Resource | Description |
|----------|-------------|
| **[125 Skills](#skill-catalog)** | Domain-specific knowledge for Azure SDK and Foundry development |
| **[Plugins](#plugins)** | Installable plugin packages (deep-wiki, and more) |
| **[Custom Agents](#agents)** | Role-specific agents (backend, frontend, infrastructure, planner) |
| **[AGENTS.md](AGENTS.md)** | Template for configuring agent behavior in your projects |
| **[MCP Configs](#mcp-servers)** | Pre-configured servers for docs, GitHub, browser automation |
| **[Documentation](https://microsoft.github.io/skills/#documentation)** | Repo docs and usage guides |

---

## Skill Catalog

> 130 skills in `.github/skills/` — flat structure with language suffixes for automatic discovery

| Language | Count | Suffix | 
|----------|-------|--------|
| [Core](#core) | 5 | — |
| [Python](#python) | 41 | `-py` |
| [.NET](#net) | 28 | `-dotnet` |
| [TypeScript](#typescript) | 24 | `-ts` |
| [Java](#java) | 25 | `-java` |
| [Rust](#rust) | 7 | `-rust` |

---

### Core

> 5 skills — tooling, infrastructure, language-agnostic

| Skill | Description |
|-------|-------------|
| [azd-deployment](.github/skills/azd-deployment/) | Deploy to Azure Container Apps with Azure Developer CLI (azd). Bicep infrastructure, remote builds, multi-service deployments. |
| [github-issue-creator](.github/skills/github-issue-creator/) | Convert raw notes, error logs, or screenshots into structured GitHub issues. |
| [mcp-builder](.github/skills/mcp-builder/) | Build MCP servers for LLM tool integration. Python (FastMCP), Node/TypeScript, or C#/.NET. |
| [podcast-generation](.github/skills/podcast-generation/) | Generate podcast-style audio with Azure OpenAI Realtime API. Full-stack React + FastAPI + WebSocket. |
| [skill-creator](.github/skills/skill-creator/) | Guide for creating effective skills for AI coding agents. |

---

### Python

> 41 skills • suffix: `-py`

<details>
<summary><strong>Foundry & AI</strong> (7 skills)</summary>

| Skill | Description |
|-------|-------------|
| [agent-framework-azure-ai-py](.github/skills/agent-framework-azure-ai-py/) | Agent Framework SDK — persistent agents, hosted tools, MCP servers, streaming. |
| [azure-ai-contentsafety-py](.github/skills/azure-ai-contentsafety-py/) | Content Safety SDK — detect harmful content in text/images with multi-severity classification. |
| [azure-ai-contentunderstanding-py](.github/skills/azure-ai-contentunderstanding-py/) | Content Understanding SDK — multimodal extraction from documents, images, audio, video. |
| [azure-ai-evaluation-py](.github/skills/azure-ai-evaluation-py/) | Evaluation SDK — quality, safety, and custom evaluators for generative AI apps. |
| [agents-v2-py](.github/skills/agents-v2-py/) | Foundry Agents SDK — container-based agents with ImageBasedHostedAgentDefinition, custom images, tools. |
| [azure-ai-projects-py](.github/skills/azure-ai-projects-py/) | High-level Foundry SDK — project client, versioned agents, evals, connections, OpenAI-compatible clients. |
| [azure-search-documents-py](.github/skills/azure-search-documents-py/) | AI Search SDK — vector search, hybrid search, semantic ranking, indexing, skillsets. |

</details>

<details>
<summary><strong>M365</strong> (1 skill)</summary>

| Skill | Description |
|-------|-------------|
| [m365-agents-py](.github/skills/m365-agents-py/) | Microsoft 365 Agents SDK — aiohttp hosting, AgentApplication routing, streaming, Copilot Studio client. |

</details>

<details>
<summary><strong>AI Services</strong> (8 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-ai-ml-py](.github/skills/azure-ai-ml-py/) | ML SDK v2 — workspaces, jobs, models, datasets, compute, pipelines. |
| [azure-ai-textanalytics-py](.github/skills/azure-ai-textanalytics-py/) | Text Analytics — sentiment, entities, key phrases, PII detection, healthcare NLP. |
| [azure-ai-transcription-py](.github/skills/azure-ai-transcription-py/) | Transcription SDK — real-time and batch speech-to-text with timestamps, diarization. |
| [azure-ai-translation-document-py](.github/skills/azure-ai-translation-document-py/) | Document Translation — batch translate Word, PDF, Excel with format preservation. |
| [azure-ai-translation-text-py](.github/skills/azure-ai-translation-text-py/) | Text Translation — real-time translation, transliteration, language detection. |
| [azure-ai-vision-imageanalysis-py](.github/skills/azure-ai-vision-imageanalysis-py/) | Vision SDK — captions, tags, objects, OCR, people detection, smart cropping. |
| [azure-ai-voicelive-py](.github/skills/azure-ai-voicelive-py/) | Voice Live SDK — real-time bidirectional voice AI with WebSocket, VAD, avatars. |
| [azure-speech-to-text-rest-py](.github/skills/azure-speech-to-text-rest-py/) | Speech to Text REST API — transcribe short audio (≤60 seconds) via HTTP without Speech SDK. |

</details>

<details>
<summary><strong>Data & Storage</strong> (7 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-cosmos-db-py](.github/skills/azure-cosmos-db-py/) | Cosmos DB patterns — FastAPI service layer, dual auth, partition strategies, TDD. |
| [azure-cosmos-py](.github/skills/azure-cosmos-py/) | Cosmos DB SDK — document CRUD, queries, containers, globally distributed data. |
| [azure-data-tables-py](.github/skills/azure-data-tables-py/) | Tables SDK — NoSQL key-value storage, entity CRUD, batch operations. |
| [azure-storage-blob-py](.github/skills/azure-storage-blob-py/) | Blob Storage — upload, download, list, containers, lifecycle management. |
| [azure-storage-file-datalake-py](.github/skills/azure-storage-file-datalake-py/) | Data Lake Gen2 — hierarchical file systems, big data analytics. |
| [azure-storage-file-share-py](.github/skills/azure-storage-file-share-py/) | File Share — SMB file shares, directories, cloud file operations. |
| [azure-storage-queue-py](.github/skills/azure-storage-queue-py/) | Queue Storage — reliable message queuing, task distribution. |

</details>

<details>
<summary><strong>Messaging & Events</strong> (4 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-eventgrid-py](.github/skills/azure-eventgrid-py/) | Event Grid — publish events, CloudEvents, event-driven architectures. |
| [azure-eventhub-py](.github/skills/azure-eventhub-py/) | Event Hubs — high-throughput streaming, producers, consumers, checkpointing. |
| [azure-messaging-webpubsubservice-py](.github/skills/azure-messaging-webpubsubservice-py/) | Web PubSub — real-time messaging, WebSocket connections, pub/sub. |
| [azure-servicebus-py](.github/skills/azure-servicebus-py/) | Service Bus — queues, topics, subscriptions, enterprise messaging. |

</details>

<details>
<summary><strong>Entra</strong> (2 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-identity-py](.github/skills/azure-identity-py/) | Identity SDK — DefaultAzureCredential, managed identity, service principals. |
| [azure-keyvault-py](.github/skills/azure-keyvault-py/) | Key Vault — secrets, keys, and certificates management. |

</details>

<details>
<summary><strong>Monitoring</strong> (4 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-monitor-ingestion-py](.github/skills/azure-monitor-ingestion-py/) | Monitor Ingestion — send custom logs via Logs Ingestion API. |
| [azure-monitor-opentelemetry-exporter-py](.github/skills/azure-monitor-opentelemetry-exporter-py/) | OpenTelemetry Exporter — low-level export to Application Insights. |
| [azure-monitor-opentelemetry-py](.github/skills/azure-monitor-opentelemetry-py/) | OpenTelemetry Distro — one-line App Insights setup with auto-instrumentation. |
| [azure-monitor-query-py](.github/skills/azure-monitor-query-py/) | Monitor Query — query Log Analytics workspaces and Azure metrics. |

</details>

<details>
<summary><strong>Integration & Management</strong> (5 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-appconfiguration-py](.github/skills/azure-appconfiguration-py/) | App Configuration — centralized config, feature flags, dynamic settings. |
| [azure-containerregistry-py](.github/skills/azure-containerregistry-py/) | Container Registry — manage container images, artifacts, repositories. |
| [azure-mgmt-apicenter-py](.github/skills/azure-mgmt-apicenter-py/) | API Center — API inventory, metadata, governance. |
| [azure-mgmt-apimanagement-py](.github/skills/azure-mgmt-apimanagement-py/) | API Management — APIM services, APIs, products, policies. |
| [azure-mgmt-botservice-py](.github/skills/azure-mgmt-botservice-py/) | Bot Service — create and manage Azure Bot resources. |

</details>

<details>
<summary><strong>Patterns & Frameworks</strong> (3 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-mgmt-fabric-py](.github/skills/azure-mgmt-fabric-py/) | Fabric Management — Microsoft Fabric capacities and resources. |
| [fastapi-router-py](.github/skills/fastapi-router-py/) | FastAPI routers — CRUD operations, auth dependencies, response models. |
| [pydantic-models-py](.github/skills/pydantic-models-py/) | Pydantic patterns — Base, Create, Update, Response, InDB model variants. |

</details>

---

### .NET

> 29 skills • suffix: `-dotnet`

<details>
<summary><strong>Foundry & AI</strong> (6 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-ai-document-intelligence-dotnet](.github/skills/azure-ai-document-intelligence-dotnet/) | Document Intelligence — extract text, tables from invoices, receipts, IDs, forms. |
| [azure-ai-openai-dotnet](.github/skills/azure-ai-openai-dotnet/) | Azure OpenAI — chat, embeddings, image generation, audio, assistants. |
| [azure-ai-projects-dotnet](.github/skills/azure-ai-projects-dotnet/) | AI Projects SDK — Foundry project client, agents, connections, evals. |
| [azure-ai-voicelive-dotnet](.github/skills/azure-ai-voicelive-dotnet/) | Voice Live — real-time voice AI with bidirectional WebSocket. |
| [azure-mgmt-weightsandbiases-dotnet](.github/skills/azure-mgmt-weightsandbiases-dotnet/) | Weights & Biases — ML experiment tracking via Azure Marketplace. |
| [azure-search-documents-dotnet](.github/skills/azure-search-documents-dotnet/) | AI Search — full-text, vector, semantic, hybrid search. |

</details>

<details>
<summary><strong>M365</strong> (1 skill)</summary>

| Skill | Description |
|-------|-------------|
| [m365-agents-dotnet](.github/skills/m365-agents-dotnet/) | Microsoft 365 Agents SDK — ASP.NET Core hosting, AgentApplication routing, Copilot Studio client. |

</details>

<details>
<summary><strong>Data & Storage</strong> (6 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-mgmt-fabric-dotnet](.github/skills/azure-mgmt-fabric-dotnet/) | Fabric ARM — provision, scale, suspend/resume Fabric capacities. |
| [azure-resource-manager-cosmosdb-dotnet](.github/skills/azure-resource-manager-cosmosdb-dotnet/) | Cosmos DB ARM — create accounts, databases, containers, RBAC. |
| [azure-resource-manager-mysql-dotnet](.github/skills/azure-resource-manager-mysql-dotnet/) | MySQL Flexible Server — servers, databases, firewall, HA. |
| [azure-resource-manager-postgresql-dotnet](.github/skills/azure-resource-manager-postgresql-dotnet/) | PostgreSQL Flexible Server — servers, databases, firewall, HA. |
| [azure-resource-manager-redis-dotnet](.github/skills/azure-resource-manager-redis-dotnet/) | Redis ARM — cache instances, firewall, geo-replication. |
| [azure-resource-manager-sql-dotnet](.github/skills/azure-resource-manager-sql-dotnet/) | SQL ARM — servers, databases, elastic pools, failover groups. |

</details>

<details>
<summary><strong>Messaging</strong> (3 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-eventgrid-dotnet](.github/skills/azure-eventgrid-dotnet/) | Event Grid — publish events, CloudEvents, EventGridEvents. |
| [azure-eventhub-dotnet](.github/skills/azure-eventhub-dotnet/) | Event Hubs — high-throughput streaming, producers, processors. |
| [azure-servicebus-dotnet](.github/skills/azure-servicebus-dotnet/) | Service Bus — queues, topics, sessions, dead letter handling. |

</details>

<details>
<summary><strong>Entra</strong> (3 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-identity-dotnet](.github/skills/azure-identity-dotnet/) | Identity SDK — DefaultAzureCredential, managed identity, service principals. |
| [azure-security-keyvault-keys-dotnet](.github/skills/azure-security-keyvault-keys-dotnet/) | Key Vault Keys — key creation, rotation, encrypt/decrypt, sign/verify. |
| [microsoft-azure-webjobs-extensions-authentication-events-dotnet](.github/skills/microsoft-azure-webjobs-extensions-authentication-events-dotnet/) | Entra Auth Events — custom claims, token enrichment, attribute collection. |

</details>

<details>
<summary><strong>Compute & Integration</strong> (6 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-maps-search-dotnet](.github/skills/azure-maps-search-dotnet/) | Azure Maps — geocoding, routing, map tiles, weather. |
| [azure-mgmt-apicenter-dotnet](.github/skills/azure-mgmt-apicenter-dotnet/) | API Center — API inventory, governance, versioning, discovery. |
| [azure-mgmt-apimanagement-dotnet](.github/skills/azure-mgmt-apimanagement-dotnet/) | API Management ARM — APIM services, APIs, products, policies. |
| [azure-mgmt-botservice-dotnet](.github/skills/azure-mgmt-botservice-dotnet/) | Bot Service ARM — bot resources, channels (Teams, DirectLine). |
| [azure-resource-manager-durabletask-dotnet](.github/skills/azure-resource-manager-durabletask-dotnet/) | Durable Task ARM — schedulers, task hubs, retention policies. |
| [azure-resource-manager-playwright-dotnet](.github/skills/azure-resource-manager-playwright-dotnet/) | Playwright Testing ARM — workspaces, quotas. |

</details>

<details>
<summary><strong>Monitoring & Partner</strong> (3 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-mgmt-applicationinsights-dotnet](.github/skills/azure-mgmt-applicationinsights-dotnet/) | Application Insights — components, web tests, workbooks. |
| [azure-mgmt-arizeaiobservabilityeval-dotnet](.github/skills/azure-mgmt-arizeaiobservabilityeval-dotnet/) | Arize AI — ML observability via Azure Marketplace. |
| [azure-mgmt-mongodbatlas-dotnet](.github/skills/azure-mgmt-mongodbatlas-dotnet/) | MongoDB Atlas — manage Atlas orgs as Azure ARM resources. |

</details>

---

### TypeScript

> 24 skills • suffix: `-ts`

<details>
<summary><strong>Foundry & AI</strong> (6 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-ai-contentsafety-ts](.github/skills/azure-ai-contentsafety-ts/) | Content Safety — moderate text/images, detect harmful content. |
| [azure-ai-document-intelligence-ts](.github/skills/azure-ai-document-intelligence-ts/) | Document Intelligence — extract from invoices, receipts, IDs, forms. |
| [azure-ai-projects-ts](.github/skills/azure-ai-projects-ts/) | AI Projects SDK — Foundry client, agents, connections, evals. |
| [azure-ai-translation-ts](.github/skills/azure-ai-translation-ts/) | Translation — text translation, transliteration, document batch. |
| [azure-ai-voicelive-ts](.github/skills/azure-ai-voicelive-ts/) | Voice Live — real-time voice AI with WebSocket, Node.js or browser. |
| [azure-search-documents-ts](.github/skills/azure-search-documents-ts/) | AI Search — vector/hybrid search, semantic ranking, knowledge bases. |

</details>

<details>
<summary><strong>M365</strong> (1 skill)</summary>

| Skill | Description |
|-------|-------------|
| [m365-agents-ts](.github/skills/m365-agents-ts/) | Microsoft 365 Agents SDK — AgentApplication routing, Express hosting, streaming, Copilot Studio client. |

</details>

<details>
<summary><strong>Data & Storage</strong> (5 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-cosmos-ts](.github/skills/azure-cosmos-ts/) | Cosmos DB — document CRUD, queries, bulk operations. |
| [azure-postgres-ts](.github/skills/azure-postgres-ts/) | PostgreSQL — connect to Azure Database for PostgreSQL with pg, pooling, Entra ID auth. |
| [azure-storage-blob-ts](.github/skills/azure-storage-blob-ts/) | Blob Storage — upload, download, list, SAS tokens, streaming. |
| [azure-storage-file-share-ts](.github/skills/azure-storage-file-share-ts/) | File Share — SMB shares, directories, file operations. |
| [azure-storage-queue-ts](.github/skills/azure-storage-queue-ts/) | Queue Storage — send, receive, peek, visibility timeout. |

</details>

<details>
<summary><strong>Messaging</strong> (3 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-eventhub-ts](.github/skills/azure-eventhub-ts/) | Event Hubs — high-throughput streaming, partitioned consumers. |
| [azure-servicebus-ts](.github/skills/azure-servicebus-ts/) | Service Bus — queues, topics, sessions, dead-letter handling. |
| [azure-web-pubsub-ts](.github/skills/azure-web-pubsub-ts/) | Web PubSub — WebSocket real-time features, group chat, notifications. |

</details>

<details>
<summary><strong>Entra & Integration</strong> (4 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-appconfiguration-ts](.github/skills/azure-appconfiguration-ts/) | App Configuration — settings, feature flags, Key Vault references. |
| [azure-identity-ts](.github/skills/azure-identity-ts/) | Identity SDK — DefaultAzureCredential, managed identity, browser login. |
| [azure-keyvault-keys-ts](.github/skills/azure-keyvault-keys-ts/) | Key Vault Keys — create, encrypt/decrypt, sign, rotate keys. |
| [azure-keyvault-secrets-ts](.github/skills/azure-keyvault-secrets-ts/) | Key Vault Secrets — store and retrieve application secrets. |

</details>

<details>
<summary><strong>Monitoring & Frontend</strong> (5 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-microsoft-playwright-testing-ts](.github/skills/azure-microsoft-playwright-testing-ts/) | Playwright Testing — scale browser tests, CI/CD integration. |
| [azure-monitor-opentelemetry-ts](.github/skills/azure-monitor-opentelemetry-ts/) | OpenTelemetry — tracing, metrics, logs with Application Insights. |
| [frontend-ui-dark-ts](.github/skills/frontend-ui-dark-ts/) | Frontend UI Dark — Vite + React + Tailwind + Framer Motion dark-themed UI design system. |
| [react-flow-node-ts](.github/skills/react-flow-node-ts/) | React Flow nodes — custom nodes with TypeScript, handles, Zustand. |
| [zustand-store-ts](.github/skills/zustand-store-ts/) | Zustand stores — TypeScript, subscribeWithSelector, state/action separation. |

</details>

---

### Java

> 26 skills • suffix: `-java`

<details>
<summary><strong>Foundry & AI</strong> (7 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-ai-anomalydetector-java](.github/skills/azure-ai-anomalydetector-java/) | Anomaly Detector — univariate/multivariate time-series analysis. |
| [azure-ai-contentsafety-java](.github/skills/azure-ai-contentsafety-java/) | Content Safety — text/image analysis, blocklist management. |
| [azure-ai-formrecognizer-java](.github/skills/azure-ai-formrecognizer-java/) | Form Recognizer — extract text, tables, key-value pairs from documents. |
| [azure-ai-projects-java](.github/skills/azure-ai-projects-java/) | AI Projects — Foundry project management, connections, datasets. |
| [azure-ai-vision-imageanalysis-java](.github/skills/azure-ai-vision-imageanalysis-java/) | Vision SDK — captions, OCR, object detection, tagging. |
| [azure-ai-voicelive-java](.github/skills/azure-ai-voicelive-java/) | Voice Live — real-time voice conversations with WebSocket. |

</details>

<details>
<summary><strong>Communication</strong> (5 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-communication-callautomation-java](.github/skills/azure-communication-callautomation-java/) | Call Automation — IVR, call routing, recording, DTMF, TTS. |
| [azure-communication-callingserver-java](.github/skills/azure-communication-callingserver-java/) | CallingServer (legacy) — deprecated, use callautomation for new projects. |
| [azure-communication-chat-java](.github/skills/azure-communication-chat-java/) | Chat SDK — threads, messaging, participants, read receipts. |
| [azure-communication-common-java](.github/skills/azure-communication-common-java/) | Common utilities — token credentials, user identifiers. |
| [azure-communication-sms-java](.github/skills/azure-communication-sms-java/) | SMS SDK — notifications, alerts, OTP delivery, bulk messaging. |

</details>

<details>
<summary><strong>Data & Storage</strong> (3 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-cosmos-java](.github/skills/azure-cosmos-java/) | Cosmos DB — NoSQL operations, global distribution, reactive patterns. |
| [azure-data-tables-java](.github/skills/azure-data-tables-java/) | Tables SDK — Table Storage or Cosmos DB Table API. |
| [azure-storage-blob-java](.github/skills/azure-storage-blob-java/) | Blob Storage — upload, download, containers, streaming. |

</details>

<details>
<summary><strong>Messaging</strong> (3 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-eventgrid-java](.github/skills/azure-eventgrid-java/) | Event Grid — publish events, pub/sub patterns. |
| [azure-eventhub-java](.github/skills/azure-eventhub-java/) | Event Hubs — high-throughput streaming, event-driven architectures. |
| [azure-messaging-webpubsub-java](.github/skills/azure-messaging-webpubsub-java/) | Web PubSub — WebSocket messaging, live updates, chat. |

</details>

<details>
<summary><strong>Entra</strong> (3 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-identity-java](.github/skills/azure-identity-java/) | Identity SDK — DefaultAzureCredential, managed identity, service principals. |
| [azure-security-keyvault-keys-java](.github/skills/azure-security-keyvault-keys-java/) | Key Vault Keys — RSA/EC keys, encrypt/decrypt, sign/verify, HSM. |
| [azure-security-keyvault-secrets-java](.github/skills/azure-security-keyvault-secrets-java/) | Key Vault Secrets — passwords, API keys, connection strings. |

</details>

<details>
<summary><strong>Monitoring & Integration</strong> (5 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-appconfiguration-java](.github/skills/azure-appconfiguration-java/) | App Configuration — settings, feature flags, snapshots. |
| [azure-compute-batch-java](.github/skills/azure-compute-batch-java/) | Batch SDK — large-scale parallel and HPC jobs. |
| [azure-monitor-ingestion-java](.github/skills/azure-monitor-ingestion-java/) | Monitor Ingestion — custom logs via Data Collection Rules. |
| [azure-monitor-opentelemetry-exporter-java](.github/skills/azure-monitor-opentelemetry-exporter-java/) | OpenTelemetry Exporter — traces, metrics, logs to Azure Monitor. (Deprecated) |
| [azure-monitor-query-java](.github/skills/azure-monitor-query-java/) | Monitor Query — Kusto queries, Log Analytics, metrics. (Deprecated) |

</details>

---

### Rust

> 7 skills • suffix: `-rust`

<details>
<summary><strong>Entra</strong> (4 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-identity-rust](.github/skills/azure-identity-rust/) | Identity SDK — DeveloperToolsCredential, ManagedIdentityCredential, ClientSecretCredential. |
| [azure-keyvault-certificates-rust](.github/skills/azure-keyvault-certificates-rust/) | Key Vault Certificates — create, import, manage certificates. |
| [azure-keyvault-keys-rust](.github/skills/azure-keyvault-keys-rust/) | Key Vault Keys — RSA/EC keys, encrypt/decrypt, sign/verify. |
| [azure-keyvault-secrets-rust](.github/skills/azure-keyvault-secrets-rust/) | Key Vault Secrets — passwords, API keys, connection strings. |

</details>

<details>
<summary><strong>Data & Storage</strong> (2 skills)</summary>

| Skill | Description |
|-------|-------------|
| [azure-cosmos-rust](.github/skills/azure-cosmos-rust/) | Cosmos DB SDK — document CRUD, queries, containers, partitions. |
| [azure-storage-blob-rust](.github/skills/azure-storage-blob-rust/) | Blob Storage — upload, download, containers, streaming. |

</details>

<details>
<summary><strong>Messaging</strong> (1 skill)</summary>

| Skill | Description |
|-------|-------------|
| [azure-eventhub-rust](.github/skills/azure-eventhub-rust/) | Event Hubs — high-throughput streaming, producers, consumers, batching. |

</details>

---

## Repository Structure

```
AGENTS.md                # Agent configuration template

.github/
├── skills/              # All 132 skills (flat structure)
├── plugins/             # Installable plugin packages
│   └── deep-wiki/       # AI-powered wiki generator
├── prompts/             # Reusable prompt templates
├── agents/              # Agent persona definitions
├── scripts/             # Automation scripts (doc scraping)
├── workflows/           # GitHub Actions (daily doc updates)
└── copilot-instructions.md

docs/                    # Generated llms.txt files (daily workflow) - GitHub Pages hosted
├── llms.txt             # Links + summaries
└── llms-full.txt        # Full content

skills/                  # Symlinks for backward compatibility
├── python/              # -> ../.github/skills/*-py
├── dotnet/              # -> ../.github/skills/*-dotnet
├── typescript/          # -> ../.github/skills/*-ts
├── java/                # -> ../.github/skills/*-java
└── rust/                # -> ../.github/skills/*-rust

.vscode/
└── mcp.json             # MCP server configurations
```

---

## Plugins

Plugins are installable packages containing curated sets of agents, commands, and skills. Install via the Copilot CLI:

```bash
copilot marketplace add microsoft/skills
copilot plugin install <plugin-name>@skills
```

| Plugin | Description | Commands |
|--------|-------------|----------|
| [deep-wiki](.github/plugins/deep-wiki/) | AI-powered wiki generator with Mermaid diagrams, architecture analysis, and source citations | `/deep-wiki:generate`, `/deep-wiki:catalogue`, `/deep-wiki:page`, `/deep-wiki:changelog`, `/deep-wiki:research`, `/deep-wiki:ask` |

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

Reusable prompt templates in [`.github/prompts/`](.github/prompts/):

| Prompt | Purpose |
|--------|---------|
| [`code-review.prompt.md`](.github/prompts/code-review.prompt.md) | Structured code review with security, performance, and maintainability checks |
| [`create-store.prompt.md`](.github/prompts/create-store.prompt.md) | Zustand store creation with TypeScript and subscribeWithSelector |
| [`create-node.prompt.md`](.github/prompts/create-node.prompt.md) | React Flow custom node creation with handles and Zustand integration |
| [`add-endpoint.prompt.md`](.github/prompts/add-endpoint.prompt.md) | FastAPI endpoint creation with Pydantic models and proper typing |

### Documentation

See the docs at https://microsoft.github.io/skills/#documentation.

---

## Testing Skills

The test harness validates that skills produce correct code patterns using the [GitHub Copilot SDK](https://github.com/github/copilot-sdk). It evaluates generated code against acceptance criteria defined for each skill.

```bash
# Install test dependencies (from tests directory)
cd tests
pnpm install

# List skills with test coverage
pnpm harness --list

# Run tests for a specific skill (mock mode for CI)
pnpm harness azure-ai-projects-py --mock --verbose

# Run with Ralph Loop (iterative improvement)
pnpm harness azure-ai-projects-py --ralph --mock --max-iterations 5 --threshold 85

# Run unit tests
pnpm test
```

### Test Coverage Summary

**125 skills with 1124 test scenarios** — all skills have acceptance criteria and test scenarios.

| Language | Skills | Scenarios | Top Skills by Scenarios |
|----------|--------|-----------|-------------------------|
| Core | 5 | 51 | `podcast-generation` (8), `skill-creator` (8) |
| Python | 41 | 331 | `azure-ai-projects-py` (12), `pydantic-models-py` (12), `azure-ai-translation-text-py` (11) |
| .NET | 29 | 290 | `azure-resource-manager-sql-dotnet` (14), `azure-resource-manager-redis-dotnet` (14), `azure-servicebus-dotnet` (13) |
| TypeScript | 24 | 257 | `azure-storage-blob-ts` (17), `azure-servicebus-ts` (14), `azure-microsoft-playwright-testing-ts` (13) |
| Java | 26 | 195 | `azure-storage-blob-java` (12), `azure-identity-java` (12), `azure-data-tables-java` (11) |

### Adding Test Coverage

See [`tests/README.md`](tests/README.md) for instructions on adding acceptance criteria and scenarios for new skills.

### Ralph Loop & Sensei Patterns

The test harness implements iterative quality improvement patterns inspired by [Sensei](https://github.com/microsoft/GitHub-Copilot-for-Azure/tree/main/.github/skills/sensei):

**Ralph Loop** — An iterative code generation and improvement system that:
1. **Generate** code for a given skill/scenario
2. **Evaluate** against acceptance criteria (score 0-100)
3. **Analyze** failures and build LLM-actionable feedback
4. **Re-generate** with feedback until quality threshold is met
5. **Report** on quality improvements across iterations

**Sensei-style Scoring** — Skills are evaluated on frontmatter compliance:

| Score | Requirements |
|-------|--------------|
| **Low** | Basic description only |
| **Medium** | Description > 150 chars, has trigger keywords |
| **Medium-High** | Has "USE FOR:" triggers AND "DO NOT USE FOR:" anti-triggers |
| **High** | Triggers + anti-triggers + compatibility field |

---

## Contributing

### Adding New Skills

New skills must follow the full workflow to ensure quality and discoverability:

**Prerequisites:**
- SDK package name (e.g., `azure-ai-agents`, `Azure.AI.OpenAI`)
- Microsoft Learn documentation URL or GitHub repository
- Target language (py/dotnet/ts/java)

**Workflow:**

1. **Create skill** in `.github/skills/<skill-name>/SKILL.md`
   - Naming: `azure-<service>-<language>` (e.g., `azure-ai-projects-py`)
   - Include YAML frontmatter with `name` and `description`
   - Reference official docs via `microsoft-docs` MCP

2. **Categorize with symlink** in `skills/<language>/<category>/`
   ```bash
   # Example: Python AI agent skill in foundry category
   cd skills/python/foundry
   ln -s ../../../.github/skills/azure-ai-projects-py projects
   ```
   
   Categories: `foundry`, `data`, `messaging`, `monitoring`, `entra`, `integration`, `compute`, `m365`, `general`

3. **Create acceptance criteria** in `.github/skills/<skill>/references/acceptance-criteria.md`
   - Document correct/incorrect import patterns
   - Document authentication patterns
   - Document async variants

4. **Create test scenarios** in `tests/scenarios/<skill>/scenarios.yaml`
   - Test basic usage, error handling, advanced features
   - Include mock responses for CI

5. **Verify tests pass**
   ```bash
   cd tests && pnpm harness <skill-name> --mock --verbose
   ```

6. **Update README.md** — Add to the appropriate language section in the Skill Catalog

> **Full guide:** See [`.github/skills/skill-creator/SKILL.md`](.github/skills/skill-creator/SKILL.md)

### Other Contributions

- Improve existing prompts and agents
- Share MCP server configurations
- Fix bugs in test harness

---

## License

MIT
