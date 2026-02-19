#!/usr/bin/env python3
"""
Create an Azure AI Search index with vector search capabilities.

Usage:
    python setup_vector_index.py --index-name <name> [options]

Environment variables required:
    AZURE_SEARCH_ENDPOINT: Azure AI Search endpoint
    AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint (for integrated vectorization)
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: Embedding model deployment name
"""

import argparse
import os
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    HnswParameters,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SemanticSearch,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SearchableField,
    SimpleField,
)


def create_vector_index(
    client: SearchIndexClient,
    index_name: str,
    aoai_endpoint: str | None = None,
    embedding_deployment: str | None = None,
    dimensions: int = 1536,
    enable_semantic: bool = True,
) -> SearchIndex:
    """Create a search index with vector and optional semantic search."""

    # Define fields
    fields = [
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="title",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
        ),
        SimpleField(
            name="category",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            stored=False,
            vector_search_dimensions=dimensions,
            vector_search_profile_name="vector-profile",
        ),
    ]

    # Configure vector search
    vectorizers = []
    if aoai_endpoint and embedding_deployment:
        vectorizers.append(
            AzureOpenAIVectorizer(
                vectorizer_name="openai-vectorizer",
                parameters=AzureOpenAIVectorizerParameters(
                    resource_url=aoai_endpoint,
                    deployment_name=embedding_deployment,
                    model_name=embedding_deployment,
                ),
            )
        )

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-algo",
                parameters=HnswParameters(
                    m=4,
                    ef_construction=400,
                    ef_search=500,
                    metric="cosine",
                ),
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-algo",
                vectorizer_name="openai-vectorizer" if vectorizers else None,
            )
        ],
        vectorizers=vectorizers if vectorizers else None,
    )

    # Configure semantic search
    semantic_search = None
    if enable_semantic:
        semantic_search = SemanticSearch(
            default_configuration_name="semantic-config",
            configurations=[
                SemanticConfiguration(
                    name="semantic-config",
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                        keywords_fields=[SemanticField(field_name="category")],
                    ),
                )
            ],
        )

    # Create index
    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )

    return client.create_or_update_index(index)


def main():
    parser = argparse.ArgumentParser(
        description="Create an Azure AI Search index with vector search"
    )
    parser.add_argument("--index-name", required=True, help="Search index name")
    parser.add_argument(
        "--dimensions",
        type=int,
        default=1536,
        help="Vector dimensions (default: 1536 for ada-002, use 3072 for text-embedding-3-large)",
    )
    parser.add_argument(
        "--no-semantic",
        action="store_true",
        help="Disable semantic search configuration",
    )
    parser.add_argument(
        "--no-vectorizer",
        action="store_true",
        help="Skip integrated vectorization (provide vectors manually)",
    )
    args = parser.parse_args()

    # Load environment
    search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    aoai_endpoint = (
        os.environ.get("AZURE_OPENAI_ENDPOINT") if not args.no_vectorizer else None
    )
    embedding_deployment = (
        os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        if not args.no_vectorizer
        else None
    )

    credential = DefaultAzureCredential()
    client = SearchIndexClient(endpoint=search_endpoint, credential=credential)

    print(f"Creating index '{args.index_name}'...")
    index = create_vector_index(
        client=client,
        index_name=args.index_name,
        aoai_endpoint=aoai_endpoint,
        embedding_deployment=embedding_deployment,
        dimensions=args.dimensions,
        enable_semantic=not args.no_semantic,
    )

    print(f"  Index created: {index.name}")
    print(f"  Fields: {[f.name for f in index.fields]}")
    print(f"  Vector dimensions: {args.dimensions}")
    print(f"  Semantic search: {'enabled' if not args.no_semantic else 'disabled'}")
    print(f"  Integrated vectorization: {'enabled' if aoai_endpoint else 'disabled'}")


if __name__ == "__main__":
    main()
