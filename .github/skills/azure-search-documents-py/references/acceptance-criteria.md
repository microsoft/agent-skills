# Azure AI Search SDK Acceptance Criteria

**SDK**: `azure-search-documents`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 SearchClient Imports

#### ✅ CORRECT: SearchClient with DefaultAzureCredential
```python
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential

client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=DefaultAzureCredential()
)
```

#### ✅ CORRECT: SearchClient with API Key
```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
)
```

### 1.2 SearchIndexClient Imports

#### ✅ CORRECT: Index Management
```python
from azure.search.documents.indexes import SearchIndexClient
from azure.identity import DefaultAzureCredential

client = SearchIndexClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

### 1.3 SearchIndexerClient Imports

#### ✅ CORRECT: Indexer Management
```python
from azure.search.documents.indexes import SearchIndexerClient
from azure.identity import DefaultAzureCredential

client = SearchIndexerClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

### 1.4 Model & Query Imports

#### ✅ CORRECT: Vector and Query Models
```python
from azure.search.documents.models import VectorizedQuery, QueryType
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
```

### 1.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```python
# WRONG - SearchClient not in indexes module
from azure.search.documents.indexes import SearchClient

# WRONG - VectorizedQuery wrong location
from azure.search.documents import VectorizedQuery  # Should be from models

# WRONG - Wrong module entirely
from azure.search import SearchClient
```

#### ❌ INCORRECT: Mixing auth credentials
```python
# WRONG - hardcoded key instead of DefaultAzureCredential
client = SearchClient(
    endpoint=endpoint,
    index_name=index,
    credential=AzureKeyCredential("hardcoded-key-123")  # Not production-safe
)
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: SearchClient with Context Manager
```python
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential

with SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=DefaultAzureCredential()
) as client:
    results = client.search(search_text="query")
```

### 2.2 ✅ CORRECT: Explicit Client Closure
```python
client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=credential
)

try:
    results = client.search(search_text="query")
finally:
    client.close()
```

### 2.3 ✅ CORRECT: Async Client
```python
from azure.search.documents.aio import SearchClient
from azure.identity.aio import DefaultAzureCredential

async with SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=DefaultAzureCredential()
) as client:
    results = await client.search(search_text="query")
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - parameter is 'endpoint', not 'url'
client = SearchClient(url=endpoint, index_name=index, credential=cred)

# WRONG - parameter is 'index_name', not 'index'
client = SearchClient(endpoint=endpoint, index=index_name, credential=cred)
```

#### ❌ INCORRECT: Not using async credential with async client
```python
# WRONG - mixing sync credential with async client
from azure.search.documents.aio import SearchClient
from azure.identity import DefaultAzureCredential  # Should be from .aio

async with SearchClient(..., credential=DefaultAzureCredential()):
    ...
```

---

## 3. Index Creation Patterns

### 3.1 ✅ CORRECT: Vector Index with HNSW
```python
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SimpleField,
    SearchableField,
)

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchField(
        name="embedding",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        vector_search_dimensions=1536,
        vector_search_profile_name="my-vector-profile",
    ),
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

### 3.2 ✅ CORRECT: Semantic Configuration
```python
from azure.search.documents.indexes.models import (
    SemanticSearch,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
)

semantic_search = SemanticSearch(
    default_configuration_name="my-semantic-config",
    configurations=[
        SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            )
        )
    ]
)

index = SearchIndex(
    name="my-index",
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search
)
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong vector dimensions
```python
# WRONG - dimensions should match embedding model
SearchField(
    name="embedding",
    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
    vector_search_dimensions=999,  # Wrong - use 1536 for text-embedding-3-small
)
```

#### ❌ INCORRECT: Missing vector search profile
```python
# WRONG - referenced profile doesn't exist
SearchField(
    name="embedding",
    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
    vector_search_profile_name="nonexistent-profile",  # Not defined in VectorSearch
)
```

---

## 4. Document Upload Patterns

### 4.1 ✅ CORRECT: Upload Documents
```python
documents = [
    {
        "id": "1",
        "title": "Azure Search",
        "content": "Full-text and vector search",
        "embedding": [0.1, 0.2, ...]  # 1536 dimensions
    }
]

result = client.upload_documents(documents)
```

### 4.2 ✅ CORRECT: Batch Upload with BufferedSender
```python
from azure.search.documents import SearchIndexingBufferedSender

with SearchIndexingBufferedSender(endpoint, index_name, credential) as sender:
    sender.upload_documents(documents)
```

### 4.3 ✅ CORRECT: Merge/Upsert Operations
```python
# Update existing documents
client.merge_documents(documents)

# Insert or update
client.merge_or_upload_documents(documents)

# Delete documents
client.delete_documents(documents)
```

### 4.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong document structure
```python
# WRONG - embedding field missing vector data
documents = [
    {
        "id": "1",
        "content": "text",
        "embedding": None  # Vector fields cannot be null
    }
]

# WRONG - embedding wrong dimensions
documents = [
    {
        "id": "1",
        "embedding": [0.1, 0.2]  # Should be 1536 dims
    }
]
```

---

## 5. Search Patterns

### 5.1 ✅ CORRECT: Keyword Search
```python
results = client.search(
    search_text="azure search",
    select=["id", "title", "content"],
    top=10
)

for result in results:
    print(f"{result['title']}: {result['@search.score']}")
```

### 5.2 ✅ CORRECT: Vector Search
```python
from azure.search.documents.models import VectorizedQuery

query_vector = [0.1, 0.2, ...]  # 1536 dimensions

vector_query = VectorizedQuery(
    vector=query_vector,
    k_nearest_neighbors=10,
    fields="embedding"
)

results = client.search(
    search_text=None,
    vector_queries=[vector_query],
    select=["id", "title", "content"]
)
```

### 5.3 ✅ CORRECT: Hybrid Search (Vector + Keyword)
```python
vector_query = VectorizedQuery(
    vector=query_vector,
    k_nearest_neighbors=10,
    fields="embedding"
)

results = client.search(
    search_text="azure search",
    vector_queries=[vector_query],
    select=["id", "title", "content"],
    top=10
)
```

### 5.4 ✅ CORRECT: Semantic Ranking
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
    print(f"Title: {result['title']}")
    if "@search.captions" in result:
        print(f"Caption: {result['@search.captions'][0]['text']}")
```

### 5.5 ✅ CORRECT: Filtered Search
```python
results = client.search(
    search_text="*",
    filter="category eq 'Technology' and rating gt 4",
    order_by=["rating desc"],
    select=["id", "title", "category", "rating"]
)
```

### 5.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Vector dimensions mismatch
```python
# WRONG - vector length doesn't match k_nearest_neighbors use
query_vector = [0.1, 0.2]  # Should be 1536 dimensions

vector_query = VectorizedQuery(
    vector=query_vector,
    k_nearest_neighbors=10,
    fields="embedding"
)
```

#### ❌ INCORRECT: Missing semantic configuration
```python
# WRONG - QueryType.SEMANTIC requires semantic_configuration_name
results = client.search(
    search_text="query",
    query_type=QueryType.SEMANTIC,
    # Missing: semantic_configuration_name="config"
)
```

---

## 6. Facets & Aggregations

### 6.1 ✅ CORRECT: Facet Query
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

### 6.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong facet syntax
```python
# WRONG - missing comma for count specifier
facets=["category count:10"]  # Should be "category,count:10"

# WRONG - requesting facets with non-zero top may return unwanted documents
results = client.search(
    search_text="*",
    facets=["category"],
    top=100  # Should be 0 for facet-only queries
)
```

---

## 7. Autocomplete & Suggest

### 7.1 ✅ CORRECT: Autocomplete
```python
results = client.autocomplete(
    search_text="sea",
    suggester_name="my-suggester",
    mode="twoTerms"
)

for result in results:
    print(result["text"])
```

### 7.2 ✅ CORRECT: Suggest
```python
results = client.suggest(
    search_text="sea",
    suggester_name="my-suggester",
    select=["title"]
)

for result in results:
    print(result["title"])
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent suggester
```python
# WRONG - suggester must be created during index creation
results = client.autocomplete(
    search_text="sea",
    suggester_name="nonexistent-suggester"  # Will fail
)
```

---

## 8. Indexer & Skillset Patterns

### 8.1 ✅ CORRECT: Create Data Source
```python
from azure.search.documents.indexes.models import SearchIndexerDataSourceConnection

data_source = SearchIndexerDataSourceConnection(
    name="my-datasource",
    type="azureblob",
    connection_string=connection_string,
    container={"name": "documents"}
)

indexer_client.create_or_update_data_source_connection(data_source)
```

### 8.2 ✅ CORRECT: Create Skillset
```python
from azure.search.documents.indexes.models import (
    SearchIndexerSkillset,
    EntityRecognitionSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
)

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
```

### 8.3 ✅ CORRECT: Create Indexer
```python
from azure.search.documents.indexes.models import SearchIndexer

indexer = SearchIndexer(
    name="my-indexer",
    data_source_name="my-datasource",
    target_index_name="my-index",
    skillset_name="my-skillset"
)

indexer_client.create_or_update_indexer(indexer)
```

### 8.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Referencing non-existent datasource
```python
# WRONG - datasource must exist first
indexer = SearchIndexer(
    data_source_name="nonexistent-datasource",  # Will fail
    target_index_name="my-index"
)
```

#### ❌ INCORRECT: Circular dependency in skillset
```python
# WRONG - skill output overwrites same field it reads from
EntityRecognitionSkill(
    inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
    outputs=[OutputFieldMappingEntry(name="content", target_name="content")]  # Overwrites input
)
```

---

## 9. Async Patterns

### 9.1 ✅ CORRECT: Async Search
```python
from azure.search.documents.aio import SearchClient

async with SearchClient(endpoint, index_name, credential) as client:
    results = await client.search(search_text="query")
    async for result in results:
        print(result["title"])
```

### 9.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing await
```python
# WRONG - async operations require await
async def bad_search():
    results = client.search(search_text="query")  # Missing await
    for result in results:  # Should be async for
        print(result)
```

#### ❌ INCORRECT: Wrong iteration syntax
```python
# WRONG - use async for with async results
async for result in results:
    print(result)

# But also this is wrong:
for result in results:  # Should use async for
    print(result)
```

---

## 10. Authentication Patterns

### 10.1 ✅ CORRECT: DefaultAzureCredential
```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SearchClient(endpoint, index_name, credential)
```

### 10.2 ✅ CORRECT: API Key (Test/Dev Only)
```python
from azure.core.credentials import AzureKeyCredential

credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
client = SearchClient(endpoint, index_name, credential)
```

### 10.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - never hardcode API keys
credential = AzureKeyCredential("12345-hardcoded-key")

# WRONG - hardcoded in endpoint
endpoint = "https://mysearch.search.windows.net/?key=12345"
```

#### ❌ INCORRECT: Empty/invalid credentials
```python
# WRONG - missing credential
client = SearchClient(endpoint, index_name)  # Will fail authentication

# WRONG - None credential
client = SearchClient(endpoint, index_name, credential=None)
```

---

## 11. Error Handling Patterns

### 11.1 ✅ CORRECT: Exception Handling
```python
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
)

try:
    result = client.get_document(key="123")
except ResourceNotFoundError:
    print("Document not found")
except HttpResponseError as e:
    print(f"Search error: {e.message}")
    print(f"Status code: {e.status_code}")
```

### 11.2 ✅ CORRECT: Batch Error Handling
```python
from azure.search.documents import SearchIndexingBufferedSender

with SearchIndexingBufferedSender(endpoint, index_name, credential) as sender:
    try:
        sender.upload_documents(documents)
    except HttpResponseError as e:
        print(f"Batch error: {e.message}")
```

### 11.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Ignoring errors
```python
# WRONG - empty exception handler
try:
    result = client.search(search_text="query")
except Exception:
    pass  # Silently fails

# WRONG - catching all exceptions
try:
    result = client.search(search_text="query")
except:
    print("error")  # Too broad
```

---

## 12. Environment Variables

### ✅ CORRECT: Required Variables
```bash
AZURE_SEARCH_ENDPOINT=https://mysearch.search.windows.net
AZURE_SEARCH_INDEX_NAME=my-index
# For DefaultAzureCredential (no explicit key needed)
# For API key auth:
AZURE_SEARCH_API_KEY=your-api-key
```

### ✅ CORRECT: Usage
```python
endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
```

---

## 13. Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: 'VectorizedQuery' not found` | Wrong import | Import from `azure.search.documents.models` |
| `HttpResponseError 400: invalid field` | Wrong field type | Use correct EDM type (e.g., `Collection(Single)` for vectors) |
| `InvalidOperationError: No indexer` | Indexer not running | Call `indexer_client.run_indexer()` |
| `ResourceNotFoundError: Index not found` | Index deleted/doesn't exist | Create index with `create_or_update_index()` |
| `HttpResponseError 401: Unauthorized` | Invalid credentials | Ensure DefaultAzureCredential or correct API key |
| `Vector dimensions mismatch` | Wrong embedding size | Ensure dimensions match model (e.g., 1536 for OpenAI) |
| `Semantic config not found` | Config not in index | Define SemanticSearch during index creation |

---

## 14. Test Scenarios Checklist

### Client Operations
- [ ] Client creation with DefaultAzureCredential
- [ ] Client creation with API key credential
- [ ] Context manager usage
- [ ] Explicit client closure

### Index Management
- [ ] Create vector index with HNSW
- [ ] Create index with semantic configuration
- [ ] Update existing index
- [ ] Idempotent create_or_update_index

### Document Operations
- [ ] Upload documents
- [ ] Batch upload with BufferedSender
- [ ] Merge/update documents
- [ ] Delete documents

### Search Patterns
- [ ] Keyword search
- [ ] Vector search
- [ ] Hybrid search (keyword + vector)
- [ ] Semantic ranking
- [ ] Filtered search
- [ ] Faceted search

### Advanced Features
- [ ] Autocomplete with suggester
- [ ] Suggest feature
- [ ] Indexer with data source
- [ ] Skillset with entity recognition
- [ ] Error handling (ResourceNotFoundError, HttpResponseError)

### Async Operations
- [ ] Async search
- [ ] Async document upload
- [ ] Async index creation

---
