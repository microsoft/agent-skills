# Semantic Ranking Patterns

Semantic ranking uses machine learning to re-rank search results for better relevance.

## Semantic Configuration

### Basic Semantic Configuration

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
                title_field=SemanticField(field_name="title"),
                content_fields=[
                    SemanticField(field_name="content"),
                    SemanticField(field_name="summary")
                ],
                keywords_fields=[
                    SemanticField(field_name="tags")
                ]
            )
        )
    ]
)
```

### Field Priority Rules

| Field Type | Max Fields | Purpose |
|------------|------------|---------|
| `title_field` | 1 | Most important for ranking |
| `content_fields` | 10 | Main content, ordered by priority |
| `keywords_fields` | 10 | Keywords/tags for matching |

## Semantic Queries

### Basic Semantic Query

```python
from azure.search.documents.models import QueryType

def semantic_search(client, query: str):
    """Execute a semantic search query."""
    results = client.search(
        search_text=query,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name="my-semantic-config",
        select=["id", "title", "content"]
    )
    
    return list(results)
```

### Semantic Search with Captions

Captions provide extractive summaries highlighting relevant passages.

```python
from azure.search.documents.models import QueryType, QueryCaptionType

def semantic_search_with_captions(client, query: str):
    """Semantic search with extractive captions."""
    results = client.search(
        search_text=query,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name="my-semantic-config",
        query_caption=QueryCaptionType.EXTRACTIVE,
        select=["id", "title", "content"]
    )
    
    for result in results:
        print(f"Title: {result['title']}")
        print(f"Score: {result['@search.score']}")
        print(f"Reranker Score: {result.get('@search.reranker_score', 'N/A')}")
        
        # Extract captions
        captions = result.get("@search.captions", [])
        for caption in captions:
            print(f"Caption: {caption.text}")
            print(f"Highlights: {caption.highlights}")
```

### Semantic Search with Answers

Answers extract specific text that directly answers the query.

```python
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType

def semantic_search_with_answers(client, query: str):
    """Semantic search with extractive answers."""
    results = client.search(
        search_text=query,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name="my-semantic-config",
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
        query_answer_count=3,  # Request up to 3 answers
        select=["id", "title", "content"]
    )
    
    # Get semantic answers (top-level, not per-document)
    answers = results.get_answers()
    if answers:
        for answer in answers:
            print(f"Answer: {answer.text}")
            print(f"Highlights: {answer.highlights}")
            print(f"Score: {answer.score}")
            print(f"Key: {answer.key}")
    
    # Process documents
    for result in results:
        print(f"Document: {result['title']}")
```

## Hybrid Search with Semantic Ranking

Combine keyword, vector, and semantic ranking for best results.

```python
from azure.search.documents.models import (
    VectorizedQuery,
    QueryType,
    QueryCaptionType,
)

def hybrid_semantic_search(
    client,
    query: str,
    query_vector: list[float],
    top: int = 10
):
    """Hybrid search with semantic re-ranking."""
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=50,  # Over-fetch for re-ranking
        fields="content_vector"
    )
    
    results = client.search(
        search_text=query,
        vector_queries=[vector_query],
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name="my-semantic-config",
        query_caption=QueryCaptionType.EXTRACTIVE,
        top=top,
        select=["id", "title", "content"]
    )
    
    return list(results)
```

## Semantic Configuration for Different Content Types

### Document Search

```python
doc_semantic_config = SemanticConfiguration(
    name="document-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="document_title"),
        content_fields=[
            SemanticField(field_name="body_text"),
            SemanticField(field_name="abstract")
        ],
        keywords_fields=[
            SemanticField(field_name="categories"),
            SemanticField(field_name="authors")
        ]
    )
)
```

### Product Search

```python
product_semantic_config = SemanticConfiguration(
    name="product-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="product_name"),
        content_fields=[
            SemanticField(field_name="description"),
            SemanticField(field_name="features")
        ],
        keywords_fields=[
            SemanticField(field_name="brand"),
            SemanticField(field_name="category")
        ]
    )
)
```

### FAQ Search

```python
faq_semantic_config = SemanticConfiguration(
    name="faq-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="question"),
        content_fields=[
            SemanticField(field_name="answer")
        ],
        keywords_fields=[
            SemanticField(field_name="topic")
        ]
    )
)
```

## Multiple Semantic Configurations

Define different configurations for different query patterns.

```python
semantic_search = SemanticSearch(
    default_configuration_name="general-config",
    configurations=[
        SemanticConfiguration(
            name="general-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                content_fields=[SemanticField(field_name="content")]
            )
        ),
        SemanticConfiguration(
            name="qa-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="question"),
                content_fields=[SemanticField(field_name="answer")]
            )
        )
    ]
)

# Use specific config at query time
results = client.search(
    search_text=query,
    query_type=QueryType.SEMANTIC,
    semantic_configuration_name="qa-config"  # Override default
)
```

## Best Practices

1. **Title field**: Always specify a title field for best ranking
2. **Content field order**: List most important content fields first
3. **Over-fetch**: Request more results than needed, let semantic re-ranking select the best
4. **Captions for UI**: Use captions to show relevant snippets in search results
5. **Answers for Q&A**: Use answers for question-answering scenarios
6. **Combine with hybrid**: Semantic ranking works best with hybrid (keyword + vector) search
