````markdown
# Knowledge Source Configurations

Python SDK patterns for knowledge sources in Foundry IQ.

## Search Index Knowledge Source

References an existing Azure AI Search index.

```python
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexKnowledgeSource, SearchIndexKnowledgeSourceParameters, SearchIndexFieldReference
)

ks = SearchIndexKnowledgeSource(
    name="my-knowledge-source",
    description="Knowledge source from existing search index",
    search_index_parameters=SearchIndexKnowledgeSourceParameters(
        search_index_name="my-index",
        source_data_fields=[
            SearchIndexFieldReference(name="id"),
            SearchIndexFieldReference(name="title"),
            SearchIndexFieldReference(name="page_number")
        ]  # Fields returned in citations - exclude embeddings!
    )
)

index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
index_client.create_or_update_knowledge_source(knowledge_source=ks)
print(f"Knowledge source '{ks.name}' created")
```

**Parameters:**
- `search_index_name`: Name of existing search index
- `source_data_fields`: Fields to include in citation references (exclude embeddings for clean output)

## Remote SharePoint Knowledge Source

Queries SharePoint directly without indexing. Requires user token for ACL trimming.

```python
from azure.search.documents.indexes.models import RemoteSharePointKnowledgeSource

remote_sp_ks = RemoteSharePointKnowledgeSource(
    name="sharepoint-source",
    description="Live SharePoint content"
)

index_client.create_or_update_knowledge_source(knowledge_source=remote_sp_ks)
print(f"Remote SharePoint source '{remote_sp_ks.name}' created")
```

**Important**: When using with agents, pass user token via headers:

```python
from azure.identity import get_bearer_token_provider
from azure.ai.projects.models import MCPTool

mcp_tool = MCPTool(
    server_label="knowledge-base",
    server_url=mcp_endpoint,
    require_approval="never",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id=connection_name,
    headers={
        "x-ms-query-source-authorization": get_bearer_token_provider(credential, "https://search.azure.com/.default")()
    }
)
```

## Knowledge Base with Multiple Sources

```python
from azure.search.documents.indexes.models import (
    KnowledgeBase, KnowledgeBaseAzureOpenAIModel, KnowledgeSourceReference,
    AzureOpenAIVectorizerParameters, KnowledgeRetrievalOutputMode,
    KnowledgeRetrievalMinimalReasoningEffort
)

# Create multiple knowledge sources first
index_ks = SearchIndexKnowledgeSource(
    name="index-source",
    search_index_parameters=SearchIndexKnowledgeSourceParameters(
        search_index_name="docs-index",
        source_data_fields=[SearchIndexFieldReference(name="id"), SearchIndexFieldReference(name="title")]
    )
)
index_client.create_or_update_knowledge_source(knowledge_source=index_ks)

sp_ks = RemoteSharePointKnowledgeSource(name="sharepoint-source", description="SharePoint content")
index_client.create_or_update_knowledge_source(knowledge_source=sp_ks)

# Combine in knowledge base
aoai_params = AzureOpenAIVectorizerParameters(
    resource_url=aoai_endpoint,
    deployment_name="gpt-4.1-mini",
    model_name="gpt-4.1-mini"
)

kb = KnowledgeBase(
    name="multi-source-kb",
    description="Knowledge base with multiple sources",
    knowledge_sources=[
        KnowledgeSourceReference(name="index-source"),
        KnowledgeSourceReference(name="sharepoint-source")
    ],
    models=[KnowledgeBaseAzureOpenAIModel(azure_open_ai_parameters=aoai_params)],
    output_mode=KnowledgeRetrievalOutputMode.EXTRACTIVE_DATA,
    retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
    retrieval_instructions="Prioritize indexed documents, fall back to SharePoint for recent updates."
)
index_client.create_or_update_knowledge_base(knowledge_base=kb)
```

## Knowledge Base Configuration Options

### Reasoning Effort Levels

```python
from azure.search.documents.indexes.models import (
    KnowledgeRetrievalMinimalReasoningEffort,
    KnowledgeRetrievalLowReasoningEffort,
    KnowledgeRetrievalMediumReasoningEffort
)

# Minimal - No LLM query planning, lowest cost/latency
kb.retrieval_reasoning_effort = KnowledgeRetrievalMinimalReasoningEffort()

# Low - Basic query decomposition (default)
kb.retrieval_reasoning_effort = KnowledgeRetrievalLowReasoningEffort()

# Medium - Multi-hop reasoning for complex queries
kb.retrieval_reasoning_effort = KnowledgeRetrievalMediumReasoningEffort()
```

### Output Modes

```python
from azure.search.documents.indexes.models import KnowledgeRetrievalOutputMode

# Extractive Data - Returns raw content for agent to synthesize (recommended for agents)
kb.output_mode = KnowledgeRetrievalOutputMode.EXTRACTIVE_DATA

# Answer Synthesis - KB generates answers with citations (for direct KB usage)
kb.output_mode = KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS
```

## Query-Time Knowledge Source Parameters

```python
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest, KnowledgeBaseMessage,
    KnowledgeBaseMessageTextContent, SearchIndexKnowledgeSourceParams
)

kb_client = KnowledgeBaseRetrievalClient(
    endpoint=search_endpoint,
    knowledge_base_name="my-kb",
    credential=credential
)

request = KnowledgeBaseRetrievalRequest(
    messages=[
        KnowledgeBaseMessage(
            role="user",
            content=[KnowledgeBaseMessageTextContent(text="What is vector search?")]
        )
    ],
    knowledge_source_params=[
        SearchIndexKnowledgeSourceParams(
            knowledge_source_name="my-knowledge-source",
            include_references=True,           # Include source citations
            include_reference_source_data=True, # Include field values in citations
            always_query_source=True           # Always query this source
        )
    ],
    include_activity=True  # Include query planning details
)

result = kb_client.retrieve(request)
```

## Response Structure

```python
# Extract response text
response_text = result.response[0].content[0].text
print(f"Answer: {response_text}")

# Extract references with scores
if result.references:
    for ref in result.references:
        print(f"Reference ID: {ref.id}")
        print(f"Reranker Score: {ref.reranker_score}")
        if ref.source_data:
            print(f"Source Data: {ref.source_data}")

# Inspect activity (query planning)
if result.activity:
    for activity in result.activity:
        print(f"Activity: {activity}")
```

## Knowledge Source Operations

### List Knowledge Sources

```python
sources = index_client.list_knowledge_sources()
for source in sources:
    print(f"Source: {source.name}")
```

### Get Knowledge Source

```python
source = index_client.get_knowledge_source("my-knowledge-source")
print(f"Source: {source.name}, Description: {source.description}")
```

### Delete Knowledge Source

```python
index_client.delete_knowledge_source("my-knowledge-source")
print("Knowledge source deleted")
```

### List Knowledge Bases

```python
kbs = index_client.list_knowledge_bases()
for kb in kbs:
    print(f"Knowledge Base: {kb.name}")
```

### Get Knowledge Base

```python
kb = index_client.get_knowledge_base("my-kb")
print(f"KB: {kb.name}, Sources: {[s.name for s in kb.knowledge_sources]}")
```

### Delete Knowledge Base

```python
index_client.delete_knowledge_base("my-kb")
print("Knowledge base deleted")
```

## Best Practices

1. **Use EXTRACTIVE_DATA mode** for agent integration - gives agent full control over synthesis
2. **Exclude embeddings from source_data_fields** - return only human-readable fields in citations
3. **Use minimal reasoning effort** for simple lookups to reduce latency/cost
4. **Combine multiple sources** in one knowledge base for comprehensive retrieval
5. **Enable include_activity** during development to debug query planning
6. **Use include_references=True** to get source citations for grounding
7. **Pass user token** for SharePoint sources to respect ACL permissions

````
