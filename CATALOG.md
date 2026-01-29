# Skill Catalog

All 127 skills in `.github/skills/` — flat structure for automatic discovery.

## Quick Start

Install skills using `skills.sh`:

```bash
# Interactive wizard - select skills to install
npx skills add microsoft/agent-skills

# Install specific skills
npx skills add microsoft/agent-skills --skills cosmos-py,servicebus-py,inference-py

# List available skills
npx skills list microsoft/agent-skills
```

Skills are installed to your project's `.github/skills/` directory and auto-discovered by VS Code Copilot.

---

## Skills by Language

### Core (Language-agnostic)

> 5 skills — tooling, infrastructure

| Skill | Description |
|-------|-------------|
| [azd-deployment](.github/skills/azd-deployment/) | Deploy containerized applications to Azure Container Apps using Azure Develop... |
| [github-issue-creator](.github/skills/github-issue-creator/) | Convert raw notes, error logs, voice dictation, or screenshots into crisp Git... |
| [mcp-builder](.github/skills/mcp-builder/) | Guide for creating high-quality MCP (Model Context Protocol) servers that ena... |
| [podcast-generation](.github/skills/podcast-generation/) | Generate AI-powered podcast-style audio narratives using Azure OpenAI's GPT R... |
| [skill-creator](.github/skills/skill-creator/) | Guide for creating effective skills for AI coding agents working with Azure S... |

---

### Python

> 42 skills • suffix: `-py`

#### AI

| Skill | Package | Description |
|-------|---------|-------------|
| [inference-py](.github/skills/inference-py/) | `azure-ai-inference` | Azure AI Inference SDK for Python |
| [ml-py](.github/skills/ml-py/) | `azure-ai-ml` | Azure Machine Learning SDK v2 for Python |
| [textanalytics-py](.github/skills/textanalytics-py/) | `azure-ai-textanalytics` | Azure AI Text Analytics SDK for sentiment analysis, entity recognition, key p... |
| [transcription-py](.github/skills/transcription-py/) | `azure-cognitiveservices-speech` | Azure Speech SDK for speech-to-text, text-to-speech, translation, and speaker... |
| [translation-document-py](.github/skills/translation-document-py/) | `azure-ai-translation-document` | Azure AI Document Translation SDK for batch translation of documents with for... |
| [translation-text-py](.github/skills/translation-text-py/) | `azure-ai-translation-text` | Azure AI Text Translation SDK for real-time text translation, transliteration... |
| [vision-imageanalysis-py](.github/skills/vision-imageanalysis-py/) | `azure-ai-vision-imageanalysis` | Azure AI Vision Image Analysis SDK for captions, tags, objects, OCR, people d... |

#### Backend

| Skill | Package | Description |
|-------|---------|-------------|
| [fastapi-router-py](.github/skills/fastapi-router-py/) | `fastapi` | Create FastAPI routers with CRUD operations, authentication dependencies, and... |
| [pydantic-models-py](.github/skills/pydantic-models-py/) | `pydantic` | Create Pydantic models following the multi-model pattern with Base, Create, U... |

#### Compute

| Skill | Package | Description |
|-------|---------|-------------|
| [botservice-py](.github/skills/botservice-py/) | `azure-mgmt-botservice` | Azure Bot Service Management SDK for Python |
| [containerregistry-py](.github/skills/containerregistry-py/) | `azure-containerregistry` | Azure Container Registry SDK for Python |

#### Data

| Skill | Package | Description |
|-------|---------|-------------|
| [blob-py](.github/skills/blob-py/) | `azure-storage-blob` | Azure Blob Storage SDK for Python |
| [cosmos-db-py](.github/skills/cosmos-db-py/) | `azure-cosmos` | Build Azure Cosmos DB NoSQL services with Python/FastAPI following production... |
| [cosmos-py](.github/skills/cosmos-py/) | `azure-cosmos` | Azure Cosmos DB SDK for Python (NoSQL API) |
| [datalake-py](.github/skills/datalake-py/) | `azure-storage-file-datalake` | Azure Data Lake Storage Gen2 SDK for Python |
| [fabric-py](.github/skills/fabric-py/) | `azure-mgmt-fabric` | Azure Fabric Management SDK for Python |
| [fileshare-py](.github/skills/fileshare-py/) | `azure-storage-file-share` | Azure Storage File Share SDK for Python |
| [queue-py](.github/skills/queue-py/) | `azure-storage-queue` | Azure Queue Storage SDK for Python |
| [tables-py](.github/skills/tables-py/) | `azure-data-tables` | Azure Tables SDK for Python (Storage and Cosmos DB) |

#### Foundry

| Skill | Package | Description |
|-------|---------|-------------|
| [agent-framework-py](.github/skills/agent-framework-py/) | `agent-framework-azure-ai` | Build Azure AI Foundry agents using the Microsoft Agent Framework Python SDK ... |
| [azure-ai-agents-py](.github/skills/azure-ai-agents-py/) | `azure-ai-agents` | Build AI agents using the Azure AI Agents Python SDK (azure-ai-agents) |
| [azure-ai-voicelive-py](.github/skills/azure-ai-voicelive-py/) | `azure-ai-voicelive` | Build real-time voice AI applications using Azure AI Voice Live SDK (azure-ai... |
| [contentsafety-py](.github/skills/contentsafety-py/) | `azure-ai-contentsafety` | Azure AI Content Safety SDK for Python |
| [contentunderstanding-py](.github/skills/contentunderstanding-py/) | `azure-ai-contentunderstanding` | Azure AI Content Understanding SDK for Python |
| [evaluation-py](.github/skills/evaluation-py/) | `azure-ai-evaluation` | Azure AI Evaluation SDK for Python |
| [foundry-iq-py](.github/skills/foundry-iq-py/) | `azure-ai-projects` | Build agentic retrieval solutions with Azure AI Search knowledge bases and Fo... |
| [foundry-sdk-py](.github/skills/foundry-sdk-py/) | `azure-ai-projects` | Build AI applications using the Azure AI Projects Python SDK (azure-ai-projects) |

#### Identity

| Skill | Package | Description |
|-------|---------|-------------|
| [azure-identity-py](.github/skills/azure-identity-py/) | `azure-identity` | Azure Identity SDK for Python authentication |

#### Integration

| Skill | Package | Description |
|-------|---------|-------------|
| [apicenter-py](.github/skills/apicenter-py/) | `azure-mgmt-apicenter` | Azure API Center Management SDK for Python |
| [apimanagement-py](.github/skills/apimanagement-py/) | `azure-mgmt-apimanagement` | Azure API Management SDK for Python |
| [appconfiguration-py](.github/skills/appconfiguration-py/) | `azure-appconfiguration` | Azure App Configuration SDK for Python |

#### Messaging

| Skill | Package | Description |
|-------|---------|-------------|
| [eventgrid-py](.github/skills/eventgrid-py/) | `azure-eventgrid` | Azure Event Grid SDK for Python |
| [eventhub-py](.github/skills/eventhub-py/) | `azure-eventhub` | Azure Event Hubs SDK for Python streaming |
| [servicebus-py](.github/skills/servicebus-py/) | `azure-servicebus` | Azure Service Bus SDK for Python messaging |
| [webpubsub-service-py](.github/skills/webpubsub-service-py/) | `azure-messaging-webpubsubservice` | Azure Web PubSub Service SDK for Python |

#### Monitoring

| Skill | Package | Description |
|-------|---------|-------------|
| [ingestion-py](.github/skills/ingestion-py/) | `azure-monitor-ingestion` | Azure Monitor Ingestion SDK for Python |
| [opentelemetry-exporter-py](.github/skills/opentelemetry-exporter-py/) | `azure-monitor-opentelemetry-exporter` | Azure Monitor OpenTelemetry Exporter for Python |
| [opentelemetry-py](.github/skills/opentelemetry-py/) | `azure-monitor-opentelemetry` | Azure Monitor OpenTelemetry Distro for Python |
| [query-py](.github/skills/query-py/) | `azure-monitor-query` | Azure Monitor Query SDK for Python |

#### Search

| Skill | Package | Description |
|-------|---------|-------------|
| [azure-ai-search-py](.github/skills/azure-ai-search-py/) | `azure-search-documents` | Clean code patterns for Azure AI Search Python SDK (azure-search-documents) |
| [documents-py](.github/skills/documents-py/) | `azure-search-documents` | Azure AI Search SDK for Python |

#### Security

| Skill | Package | Description |
|-------|---------|-------------|
| [keyvault-py](.github/skills/keyvault-py/) | `azure-keyvault-secrets` | Azure Key Vault SDK for Python |

---

### .NET

> 29 skills • suffix: `-dotnet`

#### AI

| Skill | Package | Description |
|-------|---------|-------------|
| [inference-dotnet](.github/skills/inference-dotnet/) | `Azure.AI.Inference` | Azure AI Inference SDK for .NET |
| [openai-dotnet](.github/skills/openai-dotnet/) | `Azure.AI.OpenAI` | Azure OpenAI SDK for .NET |

#### Compute

| Skill | Package | Description |
|-------|---------|-------------|
| [botservice-dotnet](.github/skills/botservice-dotnet/) | `Azure.ResourceManager.BotService` | Azure Resource Manager SDK for Bot Service in .NET |
| [durabletask-dotnet](.github/skills/durabletask-dotnet/) | `Azure.ResourceManager.DurableTask` | Azure Resource Manager SDK for Durable Task Scheduler in .NET |
| [playwright-dotnet](.github/skills/playwright-dotnet/) | `Azure.ResourceManager.Playwright` | Azure Resource Manager SDK for Microsoft Playwright Testing in .NET |

#### Data

| Skill | Package | Description |
|-------|---------|-------------|
| [cosmosdb-dotnet](.github/skills/cosmosdb-dotnet/) | `Azure.ResourceManager.CosmosDB` | Azure Resource Manager SDK for Cosmos DB in .NET |
| [fabric-dotnet](.github/skills/fabric-dotnet/) | `Azure.ResourceManager.Fabric` | Azure Resource Manager SDK for Fabric in .NET |
| [mysql-dotnet](.github/skills/mysql-dotnet/) | `Azure.ResourceManager.MySql` | Azure MySQL Flexible Server SDK for .NET |
| [postgresql-dotnet](.github/skills/postgresql-dotnet/) | `Azure.ResourceManager.PostgreSql` | Azure PostgreSQL Flexible Server SDK for .NET |
| [redis-dotnet](.github/skills/redis-dotnet/) | `Azure.ResourceManager.Redis` | Azure Resource Manager SDK for Redis in .NET |
| [sql-dotnet](.github/skills/sql-dotnet/) | `Azure.ResourceManager.Sql` | Azure Resource Manager SDK for Azure SQL in .NET |

#### Foundry

| Skill | Package | Description |
|-------|---------|-------------|
| [agents-persistent-dotnet](.github/skills/agents-persistent-dotnet/) | `Azure.AI.Agents.Persistent` | Azure AI Agents Persistent SDK for .NET |
| [document-intelligence-dotnet](.github/skills/document-intelligence-dotnet/) | `Azure.AI.DocumentIntelligence` | Azure AI Document Intelligence SDK for .NET |
| [projects-dotnet](.github/skills/projects-dotnet/) | `Azure.AI.Projects` | Azure AI Projects SDK for .NET |
| [voicelive-dotnet](.github/skills/voicelive-dotnet/) | `Azure.AI.VoiceLive` | Azure AI Voice Live SDK for .NET |

#### Identity

| Skill | Package | Description |
|-------|---------|-------------|
| [authentication-events-dotnet](.github/skills/authentication-events-dotnet/) | `Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents` | Microsoft Entra Authentication Events SDK for .NET |
| [azure-identity-dotnet](.github/skills/azure-identity-dotnet/) | `Azure.Identity` | Azure Identity SDK for .NET |

#### Integration

| Skill | Package | Description |
|-------|---------|-------------|
| [apicenter-dotnet](.github/skills/apicenter-dotnet/) | `Azure.ResourceManager.ApiCenter` | Azure API Center SDK for .NET |
| [apimanagement-dotnet](.github/skills/apimanagement-dotnet/) | `Azure.ResourceManager.ApiManagement` | Azure Resource Manager SDK for API Management in .NET |

#### Location

| Skill | Package | Description |
|-------|---------|-------------|
| [maps-dotnet](.github/skills/maps-dotnet/) | `Azure.Maps.Search` | Azure Maps SDK for .NET |

#### Messaging

| Skill | Package | Description |
|-------|---------|-------------|
| [eventgrid-dotnet](.github/skills/eventgrid-dotnet/) | `Azure.Messaging.EventGrid` | Azure Event Grid SDK for .NET |
| [eventhubs-dotnet](.github/skills/eventhubs-dotnet/) | `Azure.Messaging.EventHubs` | Azure Event Hubs SDK for .NET |
| [servicebus-dotnet](.github/skills/servicebus-dotnet/) | `Azure.Messaging.ServiceBus` | Azure Service Bus SDK for .NET |

#### Monitoring

| Skill | Package | Description |
|-------|---------|-------------|
| [applicationinsights-dotnet](.github/skills/applicationinsights-dotnet/) | `Azure.ResourceManager.ApplicationInsights` | Azure Application Insights SDK for .NET |

#### Partner

| Skill | Package | Description |
|-------|---------|-------------|
| [arize-ai-observability-eval-dotnet](.github/skills/arize-ai-observability-eval-dotnet/) | `Azure.ResourceManager.ArizeAIObservabilityEval` | Azure Resource Manager SDK for Arize AI Observability and Evaluation (.NET) |
| [mongodbatlas-dotnet](.github/skills/mongodbatlas-dotnet/) | `Azure.ResourceManager.MongoDBAtlas` | Manage MongoDB Atlas Organizations as Azure ARM resources using Azure.Resourc... |
| [weightsandbiases-dotnet](.github/skills/weightsandbiases-dotnet/) | `wandb` | Azure Weights & Biases SDK for .NET |

#### Search

| Skill | Package | Description |
|-------|---------|-------------|
| [documents-dotnet](.github/skills/documents-dotnet/) | `Azure.Search.Documents` | Azure AI Search SDK for .NET (Azure.Search.Documents) |

#### Security

| Skill | Package | Description |
|-------|---------|-------------|
| [keyvault-dotnet](.github/skills/keyvault-dotnet/) | `Azure.Security.KeyVault.Keys` | Azure Key Vault Keys SDK for .NET |

---

### TypeScript

> 23 skills • suffix: `-ts`

#### AI

| Skill | Package | Description |
|-------|---------|-------------|
| [inference-ts](.github/skills/inference-ts/) | `@azure-rest/ai-inference` | Azure AI Inference REST client for chat completions, embeddings, and image an... |
| [translation-ts](.github/skills/translation-ts/) | `@azure-rest/ai-translation-text` | Build translation applications using Azure Translation SDKs for JavaScript (@... |

#### Compute

| Skill | Package | Description |
|-------|---------|-------------|
| [playwright-ts](.github/skills/playwright-ts/) | `@azure/microsoft-playwright-testing` | Run Playwright tests at scale using Microsoft Playwright Testing service |

#### Data

| Skill | Package | Description |
|-------|---------|-------------|
| [blob-ts](.github/skills/blob-ts/) | `@azure/storage-blob` | Azure Blob Storage JavaScript/TypeScript SDK (@azure/storage-blob) for blob o... |
| [cosmosdb-ts](.github/skills/cosmosdb-ts/) | `@azure/cosmos` | Azure Cosmos DB JavaScript/TypeScript SDK (@azure/cosmos) for data plane oper... |
| [fileshare-ts](.github/skills/fileshare-ts/) | `@azure/storage-file-share` | Azure File Share JavaScript/TypeScript SDK (@azure/storage-file-share) for SM... |
| [queue-ts](.github/skills/queue-ts/) | `@azure/storage-queue` | Azure Queue Storage JavaScript/TypeScript SDK (@azure/storage-queue) for mess... |

#### Foundry

| Skill | Package | Description |
|-------|---------|-------------|
| [agents-ts](.github/skills/agents-ts/) | `@azure/ai-agents` | Build AI agents using Azure AI Agents SDK for JavaScript (@azure/ai-agents) |
| [contentsafety-ts](.github/skills/contentsafety-ts/) | `@azure-rest/ai-content-safety` | Analyze text and images for harmful content using Azure AI Content Safety (@a... |
| [document-intelligence-ts](.github/skills/document-intelligence-ts/) | `@azure-rest/ai-document-intelligence` | Extract text, tables, and structured data from documents using Azure Document... |
| [projects-ts](.github/skills/projects-ts/) | `@azure/ai-projects` | Build AI applications using Azure AI Projects SDK for JavaScript (@azure/ai-p... |
| [voicelive-ts](.github/skills/voicelive-ts/) | `@azure/ai-voicelive` | Azure AI Voice Live SDK for JavaScript/TypeScript |

#### Frontend

| Skill | Package | Description |
|-------|---------|-------------|
| [nextgen-frontend-ts](.github/skills/nextgen-frontend-ts/) | — | Build elegant frontend UIs following Microsoft Foundry's NextGen Design Syste... |
| [react-flow-node-ts](.github/skills/react-flow-node-ts/) | — | Create React Flow node components with TypeScript types, handles, and Zustand... |
| [zustand-store-ts](.github/skills/zustand-store-ts/) | — | Create Zustand stores with TypeScript, subscribeWithSelector middleware, and ... |

#### Identity

| Skill | Package | Description |
|-------|---------|-------------|
| [azure-identity-ts](.github/skills/azure-identity-ts/) | `@azure/identity` | Authenticate to Azure services using Azure Identity SDK for JavaScript (@azur... |

#### Integration

| Skill | Package | Description |
|-------|---------|-------------|
| [appconfiguration-ts](.github/skills/appconfiguration-ts/) | `@azure/app-configuration` | Build applications using Azure App Configuration SDK for JavaScript (@azure/a... |

#### Messaging

| Skill | Package | Description |
|-------|---------|-------------|
| [eventhubs-ts](.github/skills/eventhubs-ts/) | `@azure/event-hubs` | Build event streaming applications using Azure Event Hubs SDK for JavaScript ... |
| [servicebus-ts](.github/skills/servicebus-ts/) | `@azure/service-bus` | Build messaging applications using Azure Service Bus SDK for JavaScript (@azu... |
| [webpubsub-ts](.github/skills/webpubsub-ts/) | `@azure/web-pubsub` | Build real-time messaging applications using Azure Web PubSub SDKs for JavaSc... |

#### Monitoring

| Skill | Package | Description |
|-------|---------|-------------|
| [opentelemetry-ts](.github/skills/opentelemetry-ts/) | `@azure/monitor-opentelemetry` | Instrument applications with Azure Monitor and OpenTelemetry for JavaScript (... |

#### Search

| Skill | Package | Description |
|-------|---------|-------------|
| [documents-ts](.github/skills/documents-ts/) | `@azure/search-documents` | Build search applications using Azure AI Search SDK for JavaScript (@azure/se... |

#### Security

| Skill | Package | Description |
|-------|---------|-------------|
| [keyvault-ts](.github/skills/keyvault-ts/) | `@azure/keyvault-keys` | Manage cryptographic keys and secrets using Azure Key Vault SDKs for JavaScri... |

---

### Java

> 28 skills • suffix: `-java`

#### AI

| Skill | Package | Description |
|-------|---------|-------------|
| [anomalydetector-java](.github/skills/anomalydetector-java/) | — | Build anomaly detection applications with Azure AI Anomaly Detector SDK for Java |
| [formrecognizer-java](.github/skills/formrecognizer-java/) | — | Build document analysis applications with Azure Document Intelligence (Form R... |
| [inference-java](.github/skills/inference-java/) | — | Azure AI Inference SDK for Java |
| [vision-imageanalysis-java](.github/skills/vision-imageanalysis-java/) | — | Build image analysis applications with Azure AI Vision SDK for Java |

#### Communication

| Skill | Package | Description |
|-------|---------|-------------|
| [callautomation-java](.github/skills/callautomation-java/) | — | Build call automation workflows with Azure Communication Services Call Automa... |
| [callingserver-java](.github/skills/callingserver-java/) | — | Azure Communication Services CallingServer (legacy) Java SDK |
| [chat-java](.github/skills/chat-java/) | — | Build real-time chat applications with Azure Communication Services Chat Java... |
| [common-java](.github/skills/common-java/) | — | Azure Communication Services common utilities for Java |
| [sms-java](.github/skills/sms-java/) | — | Send SMS messages with Azure Communication Services SMS Java SDK |

#### Compute

| Skill | Package | Description |
|-------|---------|-------------|
| [batch-java](.github/skills/batch-java/) | — | Azure Batch SDK for Java |

#### Data

| Skill | Package | Description |
|-------|---------|-------------|
| [blob-java](.github/skills/blob-java/) | — | Build blob storage applications with Azure Storage Blob SDK for Java |
| [cosmos-java](.github/skills/cosmos-java/) | — | Azure Cosmos DB SDK for Java |
| [tables-java](.github/skills/tables-java/) | — | Build table storage applications with Azure Tables SDK for Java |

#### Foundry

| Skill | Package | Description |
|-------|---------|-------------|
| [agents-java](.github/skills/agents-java/) | — | Azure AI Agents SDK for Java |
| [agents-persistent-java](.github/skills/agents-persistent-java/) | — | Azure AI Agents Persistent SDK for Java |
| [contentsafety-java](.github/skills/contentsafety-java/) | — | Build content moderation applications with Azure AI Content Safety SDK for Java |
| [projects-java](.github/skills/projects-java/) | — | Azure AI Projects SDK for Java |
| [voicelive-java](.github/skills/voicelive-java/) | — | Azure AI VoiceLive SDK for Java |

#### Identity

| Skill | Package | Description |
|-------|---------|-------------|
| [azure-identity-java](.github/skills/azure-identity-java/) | — | Azure Identity Java SDK for authentication with Azure services |

#### Integration

| Skill | Package | Description |
|-------|---------|-------------|
| [appconfiguration-java](.github/skills/appconfiguration-java/) | — | Azure App Configuration SDK for Java |

#### Messaging

| Skill | Package | Description |
|-------|---------|-------------|
| [eventgrid-java](.github/skills/eventgrid-java/) | — | Build event-driven applications with Azure Event Grid SDK for Java |
| [eventhubs-java](.github/skills/eventhubs-java/) | — | Build real-time streaming applications with Azure Event Hubs SDK for Java |
| [webpubsub-java](.github/skills/webpubsub-java/) | — | Build real-time web applications with Azure Web PubSub SDK for Java |

#### Monitoring

| Skill | Package | Description |
|-------|---------|-------------|
| [ingestion-java](.github/skills/ingestion-java/) | — | Azure Monitor Ingestion SDK for Java |
| [opentelemetry-exporter-java](.github/skills/opentelemetry-exporter-java/) | — | Azure Monitor OpenTelemetry Exporter for Java |
| [query-java](.github/skills/query-java/) | — | Azure Monitor Query SDK for Java |

#### Security

| Skill | Package | Description |
|-------|---------|-------------|
| [keyvault-keys-java](.github/skills/keyvault-keys-java/) | — | Azure Key Vault Keys Java SDK for cryptographic key management |
| [keyvault-secrets-java](.github/skills/keyvault-secrets-java/) | — | Azure Key Vault Secrets Java SDK for secret management |

---

## Symlinks for Backward Compatibility

Original paths in `skills/{language}/` are preserved as symlinks:

```
skills/python/ai/inference -> ../../../.github/skills/inference-py
skills/typescript/foundry/agents -> ../../../.github/skills/agents-ts
```

This maintains compatibility with existing documentation links.

---

## Installation Methods

### Method 1: skills.sh (Recommended)

```bash
npx skills add microsoft/agent-skills
```

### Method 2: Manual Copy

```bash
# Clone repository
git clone https://github.com/microsoft/agent-skills.git

# Copy specific skills
cp -r agent-skills/.github/skills/cosmos-py your-project/.github/skills/
```

### Method 3: Symlinks

For multi-project setups, symlink to a central clone:

```bash
ln -s /path/to/agent-skills/.github/skills/cosmos-py \
      /path/to/your-project/.github/skills/cosmos-py
```

