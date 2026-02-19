#!/usr/bin/env python3
"""
Create Azure AI Search agentic retrieval infrastructure.

Usage:
    python setup_agentic_retrieval.py --index-name <name> --kb-name <name> [options]

Environment variables required:
    SEARCH_ENDPOINT: Azure AI Search endpoint
    AOAI_ENDPOINT: Azure OpenAI endpoint
    AOAI_EMBEDDING_MODEL: Embedding model name (default: text-embedding-3-large)
    AOAI_EMBEDDING_DEPLOYMENT: Embedding deployment name
    AOAI_GPT_MODEL: GPT model name (default: gpt-4o-mini)
    AOAI_GPT_DEPLOYMENT: GPT deployment name
"""

import argparse
import os
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, VectorSearch, VectorSearchProfile,
    HnswAlgorithmConfiguration, AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters, SemanticSearch,
    SemanticConfiguration, SemanticPrioritizedFields, SemanticField,
    SearchIndexKnowledgeSource, SearchIndexKnowledgeSourceParameters,
    SearchIndexFieldReference, KnowledgeBase, KnowledgeBaseAzureOpenAIModel,
    KnowledgeSourceReference, KnowledgeRetrievalOutputMode
)


def create_index(client: SearchIndexClient, name: str, aoai_endpoint: str,
                 embedding_deployment: str, embedding_model: str,
                 dimensions: int = 3072) -> SearchIndex:
    """Create a search index with vector and semantic search."""
    index = SearchIndex(
        name=name,
        fields=[
            SearchField(name="id", type="Edm.String", key=True,
                       filterable=True, sortable=True),
            SearchField(name="content", type="Edm.String",
                       filterable=False, sortable=False),
            SearchField(name="embedding", type="Collection(Edm.Single)",
                       stored=False, vector_search_dimensions=dimensions,
                       vector_search_profile_name="hnsw-profile"),
            SearchField(name="metadata", type="Edm.String",
                       filterable=True, sortable=False)
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
    return client.create_or_update_index(index)


def create_knowledge_source(client: SearchIndexClient, name: str,
                           index_name: str, description: str = "") -> None:
    """Create a knowledge source pointing to an index."""
    ks = SearchIndexKnowledgeSource(
        name=name,
        description=description or f"Knowledge source for {index_name}",
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
            source_data_fields=[
                SearchIndexFieldReference(name="id"),
                SearchIndexFieldReference(name="metadata")
            ]
        )
    )
    client.create_or_update_knowledge_source(ks)


def create_knowledge_base(client: SearchIndexClient, name: str,
                         knowledge_source_name: str, aoai_endpoint: str,
                         gpt_deployment: str, gpt_model: str,
                         answer_instructions: str = "") -> None:
    """Create a knowledge base with LLM integration."""
    kb = KnowledgeBase(
        name=name,
        models=[KnowledgeBaseAzureOpenAIModel(
            azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                resource_url=aoai_endpoint,
                deployment_name=gpt_deployment,
                model_name=gpt_model
            )
        )],
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
        output_mode=KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS,
        answer_instructions=answer_instructions or
            "Provide concise, accurate answers citing the retrieved documents."
    )
    client.create_or_update_knowledge_base(kb)


def main():
    parser = argparse.ArgumentParser(
        description="Set up Azure AI Search agentic retrieval infrastructure"
    )
    parser.add_argument("--index-name", required=True, help="Search index name")
    parser.add_argument("--kb-name", required=True, help="Knowledge base name")
    parser.add_argument("--ks-name", help="Knowledge source name (default: <index>-source)")
    parser.add_argument("--dimensions", type=int, default=3072,
                       help="Vector dimensions (default: 3072)")
    parser.add_argument("--answer-instructions", default="",
                       help="Custom answer synthesis instructions")
    args = parser.parse_args()

    # Load environment
    search_endpoint = os.environ["SEARCH_ENDPOINT"]
    aoai_endpoint = os.environ["AOAI_ENDPOINT"]
    embedding_model = os.environ.get("AOAI_EMBEDDING_MODEL", "text-embedding-3-large")
    embedding_deployment = os.environ.get("AOAI_EMBEDDING_DEPLOYMENT", embedding_model)
    gpt_model = os.environ.get("AOAI_GPT_MODEL", "gpt-4o-mini")
    gpt_deployment = os.environ.get("AOAI_GPT_DEPLOYMENT", gpt_model)

    ks_name = args.ks_name or f"{args.index_name}-source"

    credential = DefaultAzureCredential()
    client = SearchIndexClient(endpoint=search_endpoint, credential=credential)

    print(f"Creating index '{args.index_name}'...")
    create_index(client, args.index_name, aoai_endpoint,
                embedding_deployment, embedding_model, args.dimensions)
    print(f"  ✓ Index created")

    print(f"Creating knowledge source '{ks_name}'...")
    create_knowledge_source(client, ks_name, args.index_name)
    print(f"  ✓ Knowledge source created")

    print(f"Creating knowledge base '{args.kb_name}'...")
    create_knowledge_base(client, args.kb_name, ks_name, aoai_endpoint,
                         gpt_deployment, gpt_model, args.answer_instructions)
    print(f"  ✓ Knowledge base created")

    print(f"\nAgentic retrieval setup complete!")
    print(f"  Index: {args.index_name}")
    print(f"  Knowledge Source: {ks_name}")
    print(f"  Knowledge Base: {args.kb_name}")


if __name__ == "__main__":
    main()
