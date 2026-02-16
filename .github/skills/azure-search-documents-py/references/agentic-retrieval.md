# Agentic Retrieval with Knowledge Bases

Agentic retrieval integrates an LLM to process queries, retrieve content, and generate grounded answers.

## Architecture

```
Knowledge Base (wraps LLM + sources)
    ├── Knowledge Source 1 → Search Index A
    ├── Knowledge Source 2 → Search Index B
    └── Azure OpenAI Model (query planning + answer synthesis)
```

## Setup Workflow

### 1. Create Index with Semantic Configuration

```python
from azure.search.documents.indexes import SearchIndexClient
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
        SearchField(name="content", type="Edm.String", filterable=False),
        SearchField(name="embedding", type="Collection(Edm.Single)",
                   stored=False, vector_search_dimensions=3072,
                   vector_search_profile_name="hnsw-profile"),
        SearchField(name="category", type="Edm.String", filterable=True, facetable=True)
    ],
    vector_search=VectorSearch(
        profiles=[VectorSearchProfile(
            name="hnsw-profile",
            algorithm_configuration_name="hnsw-algo",
            vectorizer_name="aoai-vectorizer"
        )],
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
    # REQUIRED for agentic retrieval
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

### 2. Create Knowledge Source

```python
from azure.search.documents.indexes.models import (
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
    SearchIndexFieldReference
)

knowledge_source = SearchIndexKnowledgeSource(
    name="my-knowledge-source",
    description="Knowledge source for document retrieval",
    search_index_parameters=SearchIndexKnowledgeSourceParameters(
        search_index_name="my-index",
        source_data_fields=[
            SearchIndexFieldReference(name="id"),
            SearchIndexFieldReference(name="category")
        ]
    )
)

index_client.create_or_update_knowledge_source(knowledge_source)
```

### 3. Create Knowledge Base

```python
from azure.search.documents.indexes.models import (
    KnowledgeBase, KnowledgeBaseAzureOpenAIModel,
    KnowledgeSourceReference, AzureOpenAIVectorizerParameters,
    KnowledgeRetrievalOutputMode
)

knowledge_base = KnowledgeBase(
    name="my-knowledge-base",
    models=[KnowledgeBaseAzureOpenAIModel(
        azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
            resource_url=aoai_endpoint,
            deployment_name="gpt-4o-mini",
            model_name="gpt-4o-mini"
        )
    )],
    knowledge_sources=[KnowledgeSourceReference(name="my-knowledge-source")],
    output_mode=KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS,
    answer_instructions="Provide concise, well-cited answers based on retrieved documents."
)

index_client.create_or_update_knowledge_base(knowledge_base)
```

## Querying the Knowledge Base

```python
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest,
    KnowledgeRetrievalSemanticIntent,
    KnowledgeRetrievalMinimalReasoningEffort,
)

client = KnowledgeBaseRetrievalClient(
    endpoint=endpoint,
    credential=credential,
)

# Build retrieval request with semantic intents
request = KnowledgeBaseRetrievalRequest(
    intents=[KnowledgeRetrievalSemanticIntent(search="What is vector search?")]
)

result = client.retrieve(
    knowledge_base_name="my-knowledge-base",
    retrieval_request=request,
)
```

## Processing Results

```python
import json

# Extract response content
response_parts = []
for resp in result.response or []:
    for content in resp.content or []:
        if hasattr(content, "text"):
            response_parts.append(content.text)

if response_parts:
    response_content = "\n\n".join(response_parts)
    print(response_content)

# Extract references (source documents)
if result.references:
    for ref in result.references:
        print(f"Reference ID: {ref.id}")
        if hasattr(ref, 'reranker_score'):
            print(f"  Score: {ref.reranker_score}")
        if ref.source_data:
            print(f"  Content: {ref.source_data.get('content', '')[:200]}")
```

## Multi-turn Conversations

```python
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest,
    KnowledgeRetrievalSemanticIntent,
)

def ask(question: str) -> str:
    """Ask a question against the knowledge base."""
    request = KnowledgeBaseRetrievalRequest(
        intents=[KnowledgeRetrievalSemanticIntent(search=question)]
    )
    
    result = client.retrieve(
        knowledge_base_name="my-knowledge-base",
        retrieval_request=request,
    )
    
    # Extract response
    response_text = "\n\n".join(
        content.text
        for resp in (result.response or [])
        for content in (resp.content or [])
        if hasattr(content, "text")
    )
    
    return response_text
```

## Output Modes

| Mode | Description |
|------|-------------|
| `EXTRACTIVE_DATA` | Return raw chunks from knowledge sources |
| `ANSWER_SYNTHESIS` | LLM generates answers citing retrieved content |

## Reasoning Effort Levels

| Level | Class |
|-------|-------|
| `KnowledgeRetrievalMinimalReasoningEffort` | No query planning or iterative search |
| `KnowledgeRetrievalLowReasoningEffort` | Basic query decomposition |
| `KnowledgeRetrievalMediumReasoningEffort` | More sophisticated reasoning |

**Usage:**
```python
from azure.search.documents.knowledgebases.models import KnowledgeRetrievalMinimalReasoningEffort

knowledge_base = KnowledgeBase(
    name="my-knowledge-base",
    knowledge_sources=[KnowledgeSourceReference(name="my-knowledge-source")],
    retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
)
```

## Async Pattern

```python
from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient

async with KnowledgeBaseRetrievalClient(endpoint, credential=credential) as client:
    result = await client.retrieve(
        knowledge_base_name="my-knowledge-base",
        retrieval_request=request,
    )
```

## Clean Up

```python
# Delete in reverse order of creation
index_client.delete_knowledge_base("my-knowledge-base")
index_client.delete_knowledge_source("my-knowledge-source")
index_client.delete_index("my-index")
```
