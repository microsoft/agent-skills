---
name: azure-ai-search-py
description: Clean code patterns for Azure AI Search Python SDK (azure-search-documents). Use when building search applications, creating/managing indexes, implementing agentic retrieval with knowledge bases, or working with vector/hybrid search. Covers SearchClient, SearchIndexClient, SearchIndexerClient, and KnowledgeBaseRetrievalClient.
---

# Azure AI Search Python SDK

Write clean, idiomatic Python code for Azure AI Search using `azure-search-documents`.

## Installation

```bash
pip install azure-search-documents azure-identity
```

## Environment Variables

```bash
AZURE_SEARCH_ENDPOINT=https://<search-service>.search.windows.net
AZURE_SEARCH_INDEX_NAME=<index-name>
# For API key auth (not recommended for production)
AZURE_SEARCH_API_KEY=<api-key>
```

## Authentication

**DefaultAzureCredential (preferred)**:
```python
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

credential = DefaultAzureCredential()
client = SearchClient(endpoint, index_name, credential)
```

**API Key**:
```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

client = SearchClient(endpoint, index_name, AzureKeyCredential(api_key))
```

## Client Selection

| Client | Purpose |
|--------|---------|
| `SearchClient` | Query indexes, upload/update/delete documents |
| `SearchIndexClient` | Create/manage indexes, knowledge sources, knowledge bases |
| `SearchIndexerClient` | Manage indexers, skillsets, data sources |
| `KnowledgeBaseRetrievalClient` | Agentic retrieval with LLM-powered Q&A |

## Index Creation Pattern

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
        SearchField(name="id", type="Edm.String", key=True),
        SearchField(name="content", type="Edm.String", searchable=True),
        SearchField(name="embedding", type="Collection(Edm.Single)",
                   vector_search_dimensions=3072,
                   vector_search_profile_name="vector-profile"),
    ],
    vector_search=VectorSearch(
        profiles=[VectorSearchProfile(
            name="vector-profile",
            algorithm_configuration_name="hnsw-algo",
            vectorizer_name="openai-vectorizer"
        )],
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
        vectorizers=[AzureOpenAIVectorizer(
            vectorizer_name="openai-vectorizer",
            parameters=AzureOpenAIVectorizerParameters(
                resource_url=aoai_endpoint,
                deployment_name=embedding_deployment,
                model_name=embedding_model
            )
        )]
    ),
    semantic_search=SemanticSearch(
        default_configuration_name="semantic-config",
        configurations=[SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            )
        )]
    )
)

index_client = SearchIndexClient(endpoint, credential)
index_client.create_or_update_index(index)
```

## Document Operations

```python
from azure.search.documents import SearchIndexingBufferedSender

# Batch upload with automatic batching
with SearchIndexingBufferedSender(endpoint, index_name, credential) as sender:
    sender.upload_documents(documents)

# Direct operations via SearchClient
search_client = SearchClient(endpoint, index_name, credential)
search_client.upload_documents(documents)      # Add new
search_client.merge_documents(documents)       # Update existing
search_client.merge_or_upload_documents(documents)  # Upsert
search_client.delete_documents(documents)      # Remove
```

## Search Patterns

```python
# Basic search
results = search_client.search(search_text="query")

# Vector search
from azure.search.documents.models import VectorizedQuery

results = search_client.search(
    search_text=None,
    vector_queries=[VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=5,
        fields="embedding"
    )]
)

# Hybrid search (vector + keyword)
results = search_client.search(
    search_text="query",
    vector_queries=[VectorizedQuery(vector=embedding, k_nearest_neighbors=5, fields="embedding")],
    query_type="semantic",
    semantic_configuration_name="semantic-config"
)

# With filters
results = search_client.search(
    search_text="query",
    filter="category eq 'technology'",
    select=["id", "title", "content"],
    top=10
)
```

## Agentic Retrieval (Knowledge Bases)

For LLM-powered Q&A with answer synthesis, see [references/agentic-retrieval.md](references/agentic-retrieval.md).

Key concepts:
- **Knowledge Source**: Points to a search index
- **Knowledge Base**: Wraps knowledge sources + LLM for query planning and synthesis
- **Output modes**: `EXTRACTIVE_DATA` (raw chunks) or `ANSWER_SYNTHESIS` (LLM-generated answers)

## Async Pattern

```python
from azure.search.documents.aio import SearchClient

async with SearchClient(endpoint, index_name, credential) as client:
    results = await client.search(search_text="query")
    async for result in results:
        print(result["title"])
```

## Best Practices

1. **Use environment variables** for endpoints, keys, and deployment names
2. **Prefer `DefaultAzureCredential`** over API keys for production
3. **Use `SearchIndexingBufferedSender`** for batch uploads (handles batching/retries)
4. **Always define semantic configuration** for agentic retrieval indexes
5. **Use `create_or_update_index`** for idempotent index creation
6. **Close clients** with context managers or explicit `close()`

## Field Types Reference

| EDM Type | Python | Notes |
|----------|--------|-------|
| `Edm.String` | str | Searchable text |
| `Edm.Int32` | int | Integer |
| `Edm.Int64` | int | Long integer |
| `Edm.Double` | float | Floating point |
| `Edm.Boolean` | bool | True/False |
| `Edm.DateTimeOffset` | datetime | ISO 8601 |
| `Collection(Edm.Single)` | List[float] | Vector embeddings |
| `Collection(Edm.String)` | List[str] | String arrays |

## Error Handling

```python
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError
)

try:
    result = search_client.get_document(key="123")
except ResourceNotFoundError:
    print("Document not found")
except HttpResponseError as e:
    print(f"Search error: {e.message}")
```
