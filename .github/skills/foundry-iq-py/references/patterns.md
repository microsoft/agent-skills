````markdown
# Foundry IQ Python SDK Patterns

Complete Python SDK patterns for building agentic retrieval solutions with Azure AI Search.

## Setup

```python
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents.indexes import SearchIndexClient

search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
aoai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
project_endpoint = os.environ["PROJECT_ENDPOINT"]
project_resource_id = os.environ["PROJECT_RESOURCE_ID"]

credential = DefaultAzureCredential()
index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
```

## Create Search Index (Semantic Config Required)

```python
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, VectorSearch, VectorSearchProfile,
    HnswAlgorithmConfiguration, AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters, SemanticSearch,
    SemanticConfiguration, SemanticPrioritizedFields, SemanticField
)

index = SearchIndex(
    name="my-index",
    fields=[
        SearchField(name="id", type="Edm.String", key=True, filterable=True),
        SearchField(name="content", type="Edm.String", searchable=True),
        SearchField(name="title", type="Edm.String", searchable=True, filterable=True),
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
    semantic_search=SemanticSearch(
        default_configuration_name="semantic-config",
        configurations=[SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                content_fields=[SemanticField(field_name="content")]
            )
        )]
    )
)
index_client.create_or_update_index(index)
```

## Upload Documents

```python
from azure.search.documents import SearchIndexingBufferedSender

documents = [{"id": "1", "content": "Content here", "title": "Doc 1"}]

with SearchIndexingBufferedSender(endpoint=search_endpoint, index_name="my-index", credential=credential) as client:
    client.upload_documents(documents=documents)
```

## Create Knowledge Source (Search Index)

```python
from azure.search.documents.indexes.models import (
    SearchIndexKnowledgeSource, SearchIndexKnowledgeSourceParameters, SearchIndexFieldReference
)

ks = SearchIndexKnowledgeSource(
    name="my-knowledge-source",
    description="Knowledge source from search index",
    search_index_parameters=SearchIndexKnowledgeSourceParameters(
        search_index_name="my-index",
        source_data_fields=[SearchIndexFieldReference(name="id"), SearchIndexFieldReference(name="title")]
    )
)
index_client.create_or_update_knowledge_source(knowledge_source=ks)
```

## Create Knowledge Source (Remote SharePoint)

```python
from azure.search.documents.indexes.models import RemoteSharePointKnowledgeSource

remote_sp_ks = RemoteSharePointKnowledgeSource(
    name="sharepoint-source",
    description="Live SharePoint content"
)
index_client.create_or_update_knowledge_source(knowledge_source=remote_sp_ks)
```

## Create Knowledge Base

```python
from azure.search.documents.indexes.models import (
    KnowledgeBase, KnowledgeBaseAzureOpenAIModel, KnowledgeSourceReference,
    AzureOpenAIVectorizerParameters, KnowledgeRetrievalOutputMode,
    KnowledgeRetrievalMinimalReasoningEffort
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
    output_mode=KnowledgeRetrievalOutputMode.EXTRACTIVE_DATA,
    retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort()
)
index_client.create_or_update_knowledge_base(knowledge_base=kb)

mcp_endpoint = f"{search_endpoint}/knowledgebases/{kb.name}/mcp?api-version=2025-11-01-preview"
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

## Multi-turn Conversations

```python
conversation = []

def chat(user_message: str) -> str:
    conversation.append(KnowledgeBaseMessage(role="user", content=[KnowledgeBaseMessageTextContent(text=user_message)]))
    request = KnowledgeBaseRetrievalRequest(messages=conversation, knowledge_source_params=[
        SearchIndexKnowledgeSourceParams(knowledge_source_name="my-knowledge-source", include_references=True)
    ])
    result = kb_client.retrieve(request)
    response_text = "".join(c.text for r in result.response for c in r.content)
    conversation.append(KnowledgeBaseMessage(role="assistant", content=[KnowledgeBaseMessageTextContent(text=response_text)]))
    return response_text
```

## Create Project Connection

```python
import requests

connection_name = "my-kb-connection"
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

## Create Agent with MCP Tool

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)

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

agent = project_client.agents.create_version(
    agent_name="my-agent",
    definition=PromptAgentDefinition(model="gpt-4.1-mini", instructions=instructions, tools=[mcp_tool])
)
```

## SharePoint with User Token

```python
mcp_tool = MCPTool(
    server_label="knowledge-base",
    server_url=mcp_endpoint,
    require_approval="never",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id=connection_name,
    headers={"x-ms-query-source-authorization": get_bearer_token_provider(credential, "https://search.azure.com/.default")()}
)
```

## Invoke Agent

```python
openai_client = project_client.get_openai_client()
conversation = openai_client.conversations.create()

response = openai_client.responses.create(
    conversation=conversation.id,
    tool_choice="required",
    input="What are the key findings?",
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
)
print(response.output_text)
```

## Async Patterns

```python
from azure.search.documents.indexes.aio import SearchIndexClient as AsyncSearchIndexClient
from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient as AsyncKBClient

async with AsyncSearchIndexClient(endpoint=search_endpoint, credential=credential) as client:
    await client.create_or_update_knowledge_base(knowledge_base=kb)

async with AsyncKBClient(endpoint=search_endpoint, knowledge_base_name="my-kb", credential=credential) as client:
    result = await client.retrieve(request)
```

## Cleanup

```python
project_client.agents.delete_version(agent.name, agent.version)
index_client.delete_knowledge_base("my-knowledge-base")
index_client.delete_knowledge_source("my-knowledge-source")
index_client.delete_index("my-index")
```

## Reasoning Effort Options

| Level | Class | Use Case |
|-------|-------|----------|
| Minimal | `KnowledgeRetrievalMinimalReasoningEffort()` | Simple lookups, lowest cost |
| Low | `KnowledgeRetrievalLowReasoningEffort()` | Standard queries (default) |
| Medium | `KnowledgeRetrievalMediumReasoningEffort()` | Complex multi-hop |

## Output Modes

| Mode | Use Case |
|------|----------|
| `EXTRACTIVE_DATA` | Agent integration (recommended) |
| `ANSWER_SYNTHESIS` | Direct KB usage with citations |

````
