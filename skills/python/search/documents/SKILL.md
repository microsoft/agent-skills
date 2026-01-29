---
name: azure-search-documents-python
description: |
  Azure AI Search SDK for Python. Use for vector search, hybrid search, semantic ranking, indexing, and skillsets.
  Triggers: "azure-search-documents", "SearchClient", "SearchIndexClient", "vector search", "hybrid search", "semantic search".
---

# Azure AI Search SDK for Python

Full-text, vector, and hybrid search with AI enrichment capabilities.

## Installation

```bash
pip install azure-search-documents
```

## Environment Variables

```bash
AZURE_SEARCH_ENDPOINT=https://<service-name>.search.windows.net
AZURE_SEARCH_API_KEY=<your-api-key>
AZURE_SEARCH_INDEX_NAME=<your-index-name>
```

## Authentication

### API Key

```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
)
```

### Entra ID (Recommended)

```python
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential

client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=DefaultAzureCredential()
)
```

## Client Types

| Client | Purpose |
|--------|---------|
| `SearchClient` | Search and document operations |
| `SearchIndexClient` | Index management, synonym maps |
| `SearchIndexerClient` | Indexers, data sources, skillsets |

## Create Index with Vector Field

```python
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchableField,
    SimpleField
)

index_client = SearchIndexClient(endpoint, AzureKeyCredential(key))

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="title", type=SearchFieldDataType.String),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="my-vector-profile"
    )
]

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(name="my-hnsw")
    ],
    profiles=[
        VectorSearchProfile(
            name="my-vector-profile",
            algorithm_configuration_name="my-hnsw"
        )
    ]
)

index = SearchIndex(
    name="my-index",
    fields=fields,
    vector_search=vector_search
)

index_client.create_or_update_index(index)
```

## Upload Documents

```python
from azure.search.documents import SearchClient

client = SearchClient(endpoint, "my-index", AzureKeyCredential(key))

documents = [
    {
        "id": "1",
        "title": "Azure AI Search",
        "content": "Full-text and vector search service",
        "content_vector": [0.1, 0.2, ...]  # 1536 dimensions
    }
]

result = client.upload_documents(documents)
print(f"Uploaded {len(result)} documents")
```

## Keyword Search

```python
results = client.search(
    search_text="azure search",
    select=["id", "title", "content"],
    top=10
)

for result in results:
    print(f"{result['title']}: {result['@search.score']}")
```

## Vector Search

```python
from azure.search.documents.models import VectorizedQuery

# Your query embedding (1536 dimensions)
query_vector = get_embedding("semantic search capabilities")

vector_query = VectorizedQuery(
    vector=query_vector,
    k_nearest_neighbors=10,
    fields="content_vector"
)

results = client.search(
    vector_queries=[vector_query],
    select=["id", "title", "content"]
)

for result in results:
    print(f"{result['title']}: {result['@search.score']}")
```

## Hybrid Search (Vector + Keyword)

```python
from azure.search.documents.models import VectorizedQuery

vector_query = VectorizedQuery(
    vector=query_vector,
    k_nearest_neighbors=10,
    fields="content_vector"
)

results = client.search(
    search_text="azure search",
    vector_queries=[vector_query],
    select=["id", "title", "content"],
    top=10
)
```

## Semantic Ranking

```python
from azure.search.documents.models import QueryType

results = client.search(
    search_text="what is azure search",
    query_type=QueryType.SEMANTIC,
    semantic_configuration_name="my-semantic-config",
    select=["id", "title", "content"],
    top=10
)

for result in results:
    print(f"{result['title']}")
    if result.get("@search.captions"):
        print(f"  Caption: {result['@search.captions'][0].text}")
```

## Filters

```python
results = client.search(
    search_text="*",
    filter="category eq 'Technology' and rating gt 4",
    order_by=["rating desc"],
    select=["id", "title", "category", "rating"]
)
```

## Facets

```python
results = client.search(
    search_text="*",
    facets=["category,count:10", "rating"],
    top=0  # Only get facets, no documents
)

for facet_name, facet_values in results.get_facets().items():
    print(f"{facet_name}:")
    for facet in facet_values:
        print(f"  {facet['value']}: {facet['count']}")
```

## Autocomplete & Suggest

```python
# Autocomplete
results = client.autocomplete(
    search_text="sea",
    suggester_name="my-suggester",
    mode="twoTerms"
)

# Suggest
results = client.suggest(
    search_text="sea",
    suggester_name="my-suggester",
    select=["title"]
)
```

## Indexer with Skillset

```python
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer,
    SearchIndexerDataSourceConnection,
    SearchIndexerSkillset,
    EntityRecognitionSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry
)

indexer_client = SearchIndexerClient(endpoint, AzureKeyCredential(key))

# Create data source
data_source = SearchIndexerDataSourceConnection(
    name="my-datasource",
    type="azureblob",
    connection_string=connection_string,
    container={"name": "documents"}
)
indexer_client.create_or_update_data_source_connection(data_source)

# Create skillset
skillset = SearchIndexerSkillset(
    name="my-skillset",
    skills=[
        EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")]
        )
    ]
)
indexer_client.create_or_update_skillset(skillset)

# Create indexer
indexer = SearchIndexer(
    name="my-indexer",
    data_source_name="my-datasource",
    target_index_name="my-index",
    skillset_name="my-skillset"
)
indexer_client.create_or_update_indexer(indexer)
```

## Best Practices

1. **Use hybrid search** for best relevance combining vector and keyword
2. **Enable semantic ranking** for natural language queries
3. **Index in batches** of 100-1000 documents for efficiency
4. **Use filters** to narrow results before ranking
5. **Configure vector dimensions** to match your embedding model
6. **Use HNSW algorithm** for large-scale vector search
7. **Create suggesters** at index creation time (cannot add later)

## Reference Files

| File | Contents |
|------|----------|
| [references/vector-search.md](references/vector-search.md) | HNSW configuration, integrated vectorization, multi-vector queries |
| [references/semantic-ranking.md](references/semantic-ranking.md) | Semantic configuration, captions, answers, hybrid patterns |
| [scripts/setup_vector_index.py](scripts/setup_vector_index.py) | CLI script to create vector-enabled search index |
