# Vector Search Patterns

Detailed patterns for vector search with Azure AI Search.

## Vector Search Configuration

### HNSW Algorithm Configuration

HNSW (Hierarchical Navigable Small World) is the recommended algorithm for large-scale vector search.

```python
from azure.search.documents.indexes.models import (
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    HnswParameters,
)

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="hnsw-config",
            parameters=HnswParameters(
                m=4,              # Bi-directional links per node (default: 4)
                ef_construction=400,  # Size of dynamic candidate list during indexing
                ef_search=500,    # Size of dynamic candidate list during search
                metric="cosine"   # Distance metric: cosine, euclidean, dotProduct
            )
        )
    ],
    profiles=[
        VectorSearchProfile(
            name="vector-profile",
            algorithm_configuration_name="hnsw-config"
        )
    ]
)
```

### Parameter Tuning Guide

| Parameter | Range | Trade-off |
|-----------|-------|-----------|
| `m` | 4-16 | Higher = better recall, more memory |
| `ef_construction` | 100-1000 | Higher = better index quality, slower indexing |
| `ef_search` | 100-1000 | Higher = better recall, slower queries |

## Integrated Vectorization

Let Azure AI Search generate embeddings automatically using Azure OpenAI.

### Vectorizer Configuration

```python
from azure.search.documents.indexes.models import (
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
)

vectorizer = AzureOpenAIVectorizer(
    vectorizer_name="openai-vectorizer",
    parameters=AzureOpenAIVectorizerParameters(
        resource_url="https://<resource>.openai.azure.com",
        deployment_name="text-embedding-3-large",
        model_name="text-embedding-3-large"
    )
)
```

### Vector Field with Integrated Vectorization

```python
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
)

vector_field = SearchField(
    name="content_vector",
    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
    searchable=True,
    stored=False,  # Don't store vectors to save space
    vector_search_dimensions=3072,  # text-embedding-3-large
    vector_search_profile_name="vector-profile"
)
```

## Vector Query Patterns

### Basic Vector Query

```python
from azure.search.documents.models import VectorizedQuery

def vector_search(client, query_vector: list[float], k: int = 10):
    """Execute a pure vector search."""
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=k,
        fields="content_vector"
    )
    
    results = client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["id", "title", "content"]
    )
    
    return list(results)
```

### Multi-Vector Query

Search across multiple vector fields simultaneously.

```python
from azure.search.documents.models import VectorizedQuery

def multi_vector_search(client, title_vector: list[float], content_vector: list[float]):
    """Search across title and content vectors."""
    results = client.search(
        search_text=None,
        vector_queries=[
            VectorizedQuery(
                vector=title_vector,
                k_nearest_neighbors=10,
                fields="title_vector"
            ),
            VectorizedQuery(
                vector=content_vector,
                k_nearest_neighbors=10,
                fields="content_vector"
            )
        ],
        select=["id", "title", "content"]
    )
    
    return list(results)
```

### Vector Search with Filters

Pre-filter documents before vector search for better performance.

```python
def filtered_vector_search(
    client,
    query_vector: list[float],
    category: str,
    min_rating: float = 4.0
):
    """Vector search with pre-filtering."""
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=10,
        fields="content_vector"
    )
    
    results = client.search(
        search_text=None,
        vector_queries=[vector_query],
        filter=f"category eq '{category}' and rating ge {min_rating}",
        select=["id", "title", "content", "category", "rating"]
    )
    
    return list(results)
```

## Exhaustive KNN Search

For exact nearest neighbor search (smaller indexes or when precision is critical).

```python
from azure.search.documents.indexes.models import (
    VectorSearch,
    ExhaustiveKnnAlgorithmConfiguration,
    ExhaustiveKnnParameters,
    VectorSearchProfile,
)

vector_search = VectorSearch(
    algorithms=[
        ExhaustiveKnnAlgorithmConfiguration(
            name="exhaustive-knn",
            parameters=ExhaustiveKnnParameters(
                metric="cosine"
            )
        )
    ],
    profiles=[
        VectorSearchProfile(
            name="exhaustive-profile",
            algorithm_configuration_name="exhaustive-knn"
        )
    ]
)
```

## Scalar Quantization (Preview)

Reduce vector storage size with minimal quality loss.

```python
from azure.search.documents.indexes.models import (
    VectorSearch,
    VectorSearchProfile,
    ScalarQuantizationCompression,
    ScalarQuantizationParameters,
)

vector_search = VectorSearch(
    profiles=[
        VectorSearchProfile(
            name="quantized-profile",
            algorithm_configuration_name="hnsw-config",
            compression_name="scalar-quantization"
        )
    ],
    compressions=[
        ScalarQuantizationCompression(
            compression_name="scalar-quantization",
            parameters=ScalarQuantizationParameters(
                quantized_data_type="int8"
            )
        )
    ]
)
```

## Async Vector Search

```python
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizedQuery

async def async_vector_search(client: SearchClient, query_vector: list[float]):
    """Async vector search."""
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=10,
        fields="content_vector"
    )
    
    results = client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["id", "title", "content"]
    )
    
    docs = []
    async for result in results:
        docs.append(result)
    
    return docs
```

## Best Practices

1. **Dimensions**: Match your embedding model (text-embedding-3-large = 3072, ada-002 = 1536)
2. **Stored vectors**: Set `stored=False` to save storage if you don't need to retrieve vectors
3. **Pre-filtering**: Use filters to narrow search space before vector comparison
4. **Hybrid search**: Combine with keyword search for best relevance (see hybrid-search.md)
5. **Compression**: Use scalar quantization for large indexes to reduce costs
