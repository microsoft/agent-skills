---
name: foundry-iq-py
description: Build agentic retrieval solutions with Azure AI Search knowledge bases and Foundry Agent Service using the Python SDK. Use when creating knowledge sources/bases, connecting agents via MCP for RAG, implementing hybrid search with semantic reranking, or building conversational apps with citation support. Covers SearchIndexClient, KnowledgeBaseRetrievalClient, and AIProjectClient.
---

# Foundry IQ Python SDK

Build agentic retrieval pipelines using Azure AI Search knowledge bases with the Python SDK.

## Installation

```bash
pip install azure-ai-projects==2.0.0b1 azure-search-documents==11.7.0b2 azure-identity
```

## Environment Variables

```bash
AZURE_SEARCH_ENDPOINT=https://<search-service>.search.windows.net
AZURE_OPENAI_ENDPOINT=https://<openai-resource>.openai.azure.com
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
```

## Authentication

```python
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient

credential = DefaultAzureCredential()
index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
```

## Architecture

```
User Query → Foundry Agent → MCP Tool → Knowledge Base → Knowledge Sources
                                              ↓
                              Query Planning + Hybrid Search + Reranking
                                              ↓
                              Extractive Data with Citations
```

## Core Workflow

### 1. Create Search Index (Semantic Config Required)

```python
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, VectorSearch, VectorSearchProfile,
    HnswAlgorithmConfiguration, AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters, SemanticSearch,
    SemanticConfiguration, SemanticPrioritizedFields, SemanticField
)

index = SearchIndex(
    name=index_name,
    fields=[
        SearchField(name="id", type="Edm.String", key=True, filterable=True),
        SearchField(name="content", type="Edm.String", searchable=True),
        SearchField(name="embedding", type="Collection(Edm.Single)",
                   stored=False, vector_search_dimensions=3072,
                   vector_search_profile_name="hnsw-profile"),
    ],
    vector_search=VectorSearch(
        profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw-algo", vectorizer_name="aoai-vectorizer")],
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
        vectorizers=[AzureOpenAIVectorizer(
            vectorizer_name="aoai-vectorizer",
            parameters=AzureOpenAIVectorizerParameters(
                resource_url=aoai_endpoint,
                deployment_name="text-embedding-3-large",
                model_name="text-embedding-3-large"
            )
        )]
    ),
    semantic_search=SemanticSearch(  # REQUIRED for agentic retrieval
        default_configuration_name="semantic-config",
        configurations=[SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            )
        )]
    )
)
index_client.create_or_update_index(index)
```

### 2. Create Knowledge Source

```python
from azure.search.documents.indexes.models import (
    SearchIndexKnowledgeSource, SearchIndexKnowledgeSourceParameters, SearchIndexFieldReference
)

ks = SearchIndexKnowledgeSource(
    name="my-knowledge-source",
    description="Knowledge source for retrieval",
    search_index_parameters=SearchIndexKnowledgeSourceParameters(
        search_index_name=index_name,
        source_data_fields=[SearchIndexFieldReference(name="id"), SearchIndexFieldReference(name="content")]
    )
)
index_client.create_or_update_knowledge_source(knowledge_source=ks)
```

### 3. Create Knowledge Base

```python
from azure.search.documents.indexes.models import (
    KnowledgeBase, KnowledgeBaseAzureOpenAIModel, KnowledgeSourceReference,
    AzureOpenAIVectorizerParameters, KnowledgeRetrievalOutputMode,
    KnowledgeRetrievalLowReasoningEffort
)

aoai_params = AzureOpenAIVectorizerParameters(
    resource_url=aoai_endpoint,
    deployment_name="gpt-4.1-mini",
    model_name="gpt-4.1-mini"
)

kb = KnowledgeBase(
    name="my-knowledge-base",
    knowledge_sources=[KnowledgeSourceReference(name="my-knowledge-source")],
    models=[KnowledgeBaseAzureOpenAIModel(azure_open_ai_parameters=aoai_params)],
    output_mode=KnowledgeRetrievalOutputMode.EXTRACTIVE_DATA,  # Recommended for agent integration
    retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort()
)
index_client.create_or_update_knowledge_base(knowledge_base=kb)

mcp_endpoint = f"{search_endpoint}/knowledgebases/{kb.name}/mcp?api-version=2025-11-01-preview"
```

### 4. Create Project Connection

```python
import requests
from azure.identity import get_bearer_token_provider

bearer_token = get_bearer_token_provider(credential, "https://management.azure.com/.default")()

response = requests.put(
    f"https://management.azure.com{project_resource_id}/connections/{connection_name}?api-version=2025-10-01-preview",
    headers={"Authorization": f"Bearer {bearer_token}"},
    json={
        "name": connection_name,
        "type": "Microsoft.MachineLearningServices/workspaces/connections",
        "properties": {
            "authType": "ProjectManagedIdentity",
            "category": "RemoteTool",
            "target": mcp_endpoint,
            "isSharedToAll": True,
            "audience": "https://search.azure.com/",
            "metadata": {"ApiType": "Azure"}
        }
    }
)
response.raise_for_status()
```

### 5. Create Agent with MCP Tool

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

client = AIProjectClient(endpoint=project_endpoint, credential=credential)

instructions = """You are a helpful assistant that must use the knowledge base to answer all questions from user. You must never answer from your own knowledge under any circumstances.
Every answer must always provide annotations for using the MCP knowledge base tool and render them as: 【message_idx:search_idx†source_name】
If you cannot find the answer in the provided knowledge base you must respond with "I don't know"."""

mcp_tool = MCPTool(
    server_label="knowledge-base",
    server_url=mcp_endpoint,
    require_approval="never",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id=connection_name
)

agent = client.agents.create_version(
    agent_name="my-agent",
    definition=PromptAgentDefinition(model="gpt-4.1-mini", instructions=instructions, tools=[mcp_tool])
)
```

### 6. Invoke Agent

```python
openai_client = client.get_openai_client()
conversation = openai_client.conversations.create()

response = openai_client.responses.create(
    conversation=conversation.id,
    tool_choice="required",  # Ensures agent always uses knowledge base
    input="What are the key findings?",
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
)
print(response.output_text)
```

## Query Knowledge Base Directly

```python
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest, KnowledgeBaseMessage,
    KnowledgeBaseMessageTextContent, SearchIndexKnowledgeSourceParams
)

kb_client = KnowledgeBaseRetrievalClient(endpoint=search_endpoint, knowledge_base_name="my-knowledge-base", credential=credential)

request = KnowledgeBaseRetrievalRequest(
    messages=[KnowledgeBaseMessage(role="user", content=[KnowledgeBaseMessageTextContent(text="What is vector search?")])],
    knowledge_source_params=[SearchIndexKnowledgeSourceParams(
        knowledge_source_name="my-knowledge-source",
        include_references=True,
        include_reference_source_data=True
    )],
    include_activity=True
)

result = kb_client.retrieve(request)
print(result.response[0].content[0].text)
```

## SharePoint with User Token

For remote SharePoint sources, pass user token for ACL trimming:

```python
from azure.identity import get_bearer_token_provider

mcp_tool = MCPTool(
    server_label="knowledge-base",
    server_url=mcp_endpoint,
    require_approval="never",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id=connection_name,
    headers={"x-ms-query-source-authorization": get_bearer_token_provider(credential, "https://search.azure.com/.default")()}
)
```

## Retrieval Reasoning Effort

| Level | Class | Best For |
|-------|-------|----------|
| Minimal | `KnowledgeRetrievalMinimalReasoningEffort()` | Simple lookups, lowest cost/latency |
| Low | `KnowledgeRetrievalLowReasoningEffort()` | Standard queries (default) |
| Medium | `KnowledgeRetrievalMediumReasoningEffort()` | Complex multi-hop questions |

## Output Modes

| Mode | Value | Use Case |
|------|-------|----------|
| Extractive Data | `KnowledgeRetrievalOutputMode.EXTRACTIVE_DATA` | Agent integration (recommended) |
| Answer Synthesis | `KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS` | Direct KB responses with citations |

## Supported LLMs

gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-5, gpt-5-mini, gpt-5-nano

## API Version

`api-version=2025-11-01-preview`

## Prerequisites

- Azure AI Search with semantic ranker enabled
- Microsoft Foundry project with LLM deployment and system-assigned managed identity
- Required roles:
  - **Search Service Contributor**: Create objects
  - **Search Index Data Reader**: Read indexed content (assign to project managed identity)
  - **Azure AI User**: Access model deployments, create agents
  - **Azure AI Project Manager**: Create project connections

## Reference Files

- [references/patterns.md](references/patterns.md): Complete SDK patterns for all operations
- [references/knowledge-sources.md](references/knowledge-sources.md): Knowledge source configurations
- [scripts/create_agent.py](scripts/create_agent.py): End-to-end script
