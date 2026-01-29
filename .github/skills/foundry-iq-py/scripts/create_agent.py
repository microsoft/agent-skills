#!/usr/bin/env python3
"""
Foundry IQ Agent Creator

End-to-end script using Python SDK for creating Microsoft Foundry agents 
connected to Foundry IQ knowledge bases.

Prerequisites:
    pip install azure-ai-projects==2.0.0b1 azure-search-documents==11.7.0b2 azure-identity requests

Environment variables:
    AZURE_SEARCH_ENDPOINT      - Azure AI Search endpoint
    AZURE_OPENAI_ENDPOINT      - Azure OpenAI endpoint
    PROJECT_ENDPOINT           - Foundry project endpoint
    PROJECT_RESOURCE_ID        - Foundry project resource ID

Usage:
    python create_agent.py --index-name my-index --agent-name my-agent
"""

import os
import argparse
import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexKnowledgeSource, SearchIndexKnowledgeSourceParameters, SearchIndexFieldReference,
    KnowledgeBase, KnowledgeBaseAzureOpenAIModel, KnowledgeSourceReference,
    AzureOpenAIVectorizerParameters, KnowledgeRetrievalOutputMode,
    KnowledgeRetrievalMinimalReasoningEffort, KnowledgeRetrievalLowReasoningEffort,
    KnowledgeRetrievalMediumReasoningEffort
)
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest, KnowledgeBaseMessage,
    KnowledgeBaseMessageTextContent, SearchIndexKnowledgeSourceParams
)
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

# Required environment variables
REQUIRED_ENV_VARS = [
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_OPENAI_ENDPOINT",
    "PROJECT_ENDPOINT",
    "PROJECT_RESOURCE_ID",
]

API_VERSION = "2025-11-01-preview"
MGMT_API_VERSION = "2025-10-01-preview"

AGENT_INSTRUCTIONS = """You are a helpful assistant that must use the knowledge base to answer all questions from user. You must never answer from your own knowledge under any circumstances.
Every answer must always provide annotations for using the MCP knowledge base tool and render them as: 【message_idx:search_idx†source_name】
If you cannot find the answer in the provided knowledge base you must respond with "I don't know"."""


class FoundryIQAgentBuilder:
    """Builder for creating Foundry agents connected to Foundry IQ using Python SDK."""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
        self.aoai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        self.project_endpoint = os.environ["PROJECT_ENDPOINT"]
        self.project_resource_id = os.environ["PROJECT_RESOURCE_ID"]
        
        # Initialize SDK clients
        self.index_client = SearchIndexClient(endpoint=self.search_endpoint, credential=self.credential)
        self.project_client = AIProjectClient(endpoint=self.project_endpoint, credential=self.credential)
    
    def _get_management_token(self):
        """Get bearer token for Azure Management API."""
        return get_bearer_token_provider(self.credential, "https://management.azure.com/.default")()
    
    def create_knowledge_source(self, name: str, index_name: str, source_fields: list = None):
        """Create knowledge source from existing search index using SDK."""
        if source_fields is None:
            source_fields = ["id", "title", "content"]
        
        ks = SearchIndexKnowledgeSource(
            name=name,
            description=f"Knowledge source from index: {index_name}",
            search_index_parameters=SearchIndexKnowledgeSourceParameters(
                search_index_name=index_name,
                source_data_fields=[SearchIndexFieldReference(name=f) for f in source_fields]
            )
        )
        
        self.index_client.create_or_update_knowledge_source(knowledge_source=ks)
        print(f"✓ Knowledge source '{name}' created from index '{index_name}'")
        return ks
    
    def create_knowledge_base(self, name: str, source_names: list, model: str = "gpt-4.1-mini",
                              reasoning: str = "minimal"):
        """Create knowledge base using SDK."""
        reasoning_map = {
            "minimal": KnowledgeRetrievalMinimalReasoningEffort(),
            "low": KnowledgeRetrievalLowReasoningEffort(),
            "medium": KnowledgeRetrievalMediumReasoningEffort(),
        }
        
        aoai_params = AzureOpenAIVectorizerParameters(
            resource_url=self.aoai_endpoint,
            deployment_name=model,
            model_name=model
        )
        
        kb = KnowledgeBase(
            name=name,
            description=f"Knowledge base with sources: {', '.join(source_names)}",
            knowledge_sources=[KnowledgeSourceReference(name=s) for s in source_names],
            models=[KnowledgeBaseAzureOpenAIModel(azure_open_ai_parameters=aoai_params)],
            output_mode=KnowledgeRetrievalOutputMode.EXTRACTIVE_DATA,
            retrieval_reasoning_effort=reasoning_map.get(reasoning, KnowledgeRetrievalMinimalReasoningEffort())
        )
        
        self.index_client.create_or_update_knowledge_base(knowledge_base=kb)
        print(f"✓ Knowledge base '{name}' created")
        
        mcp_endpoint = f"{self.search_endpoint}/knowledgebases/{name}/mcp?api-version={API_VERSION}"
        return kb, mcp_endpoint
    
    def create_project_connection(self, connection_name: str, mcp_endpoint: str):
        """Create MCP connection via REST API (no SDK support yet)."""
        response = requests.put(
            f"https://management.azure.com{self.project_resource_id}/connections/{connection_name}?api-version={MGMT_API_VERSION}",
            headers={"Authorization": f"Bearer {self._get_management_token()}", "Content-Type": "application/json"},
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
        print(f"✓ Project connection '{connection_name}' created")
        return connection_name
    
    def create_agent(self, agent_name: str, mcp_endpoint: str, connection_name: str,
                     model: str = "gpt-4.1-mini", instructions: str = None):
        """Create agent with MCP tool using SDK."""
        mcp_tool = MCPTool(
            server_label="knowledge-base",
            server_url=mcp_endpoint,
            require_approval="never",
            allowed_tools=["knowledge_base_retrieve"],
            project_connection_id=connection_name
        )
        
        agent = self.project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model,
                instructions=instructions or AGENT_INSTRUCTIONS,
                tools=[mcp_tool]
            )
        )
        
        print(f"✓ Agent '{agent_name}' created (version: {agent.version})")
        return agent
    
    def query_knowledge_base(self, kb_name: str, ks_name: str, query: str):
        """Query knowledge base using SDK."""
        kb_client = KnowledgeBaseRetrievalClient(
            endpoint=self.search_endpoint,
            knowledge_base_name=kb_name,
            credential=self.credential
        )
        
        request = KnowledgeBaseRetrievalRequest(
            messages=[KnowledgeBaseMessage(role="user", content=[KnowledgeBaseMessageTextContent(text=query)])],
            knowledge_source_params=[SearchIndexKnowledgeSourceParams(
                knowledge_source_name=ks_name,
                include_references=True,
                include_reference_source_data=True
            )],
            include_activity=True
        )
        
        return kb_client.retrieve(request)
    
    def delete_resources(self, agent_name: str = None, agent_version: str = None,
                         connection_name: str = None, kb_name: str = None, ks_name: str = None):
        """Delete created resources using SDK."""
        if agent_name and agent_version:
            self.project_client.agents.delete_version(agent_name, agent_version)
            print(f"✓ Agent '{agent_name}' version '{agent_version}' deleted")
        
        if connection_name:
            requests.delete(
                f"https://management.azure.com{self.project_resource_id}/connections/{connection_name}?api-version={MGMT_API_VERSION}",
                headers={"Authorization": f"Bearer {self._get_management_token()}"}
            )
            print(f"✓ Connection '{connection_name}' deleted")
        
        if kb_name:
            self.index_client.delete_knowledge_base(kb_name)
            print(f"✓ Knowledge base '{kb_name}' deleted")
        
        if ks_name:
            self.index_client.delete_knowledge_source(ks_name)
            print(f"✓ Knowledge source '{ks_name}' deleted")


def validate_environment():
    """Check required environment variables."""
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        print("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Create Foundry IQ Agent using Python SDK")
    parser.add_argument("--index-name", required=True, help="Existing search index name")
    parser.add_argument("--agent-name", default="foundry-iq-agent", help="Agent name")
    parser.add_argument("--model", default="gpt-4.1-mini", help="LLM deployment name")
    parser.add_argument("--reasoning", default="minimal", choices=["minimal", "low", "medium"],
                        help="Retrieval reasoning effort")
    parser.add_argument("--source-fields", nargs="+", default=["id", "title"],
                        help="Fields to include in citations")
    parser.add_argument("--test-query", help="Optional test query")
    parser.add_argument("--cleanup", action="store_true", help="Delete resources after creation")
    
    args = parser.parse_args()
    
    if not validate_environment():
        return 1
    
    builder = FoundryIQAgentBuilder()
    
    # Derive names from agent name
    ks_name = f"ks-{args.agent_name}"
    kb_name = f"kb-{args.agent_name}"
    conn_name = f"conn-{args.agent_name}"
    agent = None
    
    try:
        # Step 1: Create knowledge source
        builder.create_knowledge_source(ks_name, args.index_name, args.source_fields)
        
        # Step 2: Create knowledge base
        kb, mcp_endpoint = builder.create_knowledge_base(kb_name, [ks_name], args.model, args.reasoning)
        
        # Step 3: Create project connection
        builder.create_project_connection(conn_name, mcp_endpoint)
        
        # Step 4: Create agent
        agent = builder.create_agent(args.agent_name, mcp_endpoint, conn_name, args.model)
        
        # Optional: Test query
        if args.test_query:
            print(f"\nTesting knowledge base: {args.test_query}")
            result = builder.query_knowledge_base(kb_name, ks_name, args.test_query)
            print(f"Response: {result.response[0].content[0].text[:500]}...")
        
        print(f"\n✓ Agent '{args.agent_name}' is ready!")
        print(f"  MCP Endpoint: {mcp_endpoint}")
        
        # Optional: Cleanup
        if args.cleanup:
            print("\nCleaning up...")
            builder.delete_resources(args.agent_name, agent.version, conn_name, kb_name, ks_name)
        
        return 0
        
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ API Error: {e}")
        if e.response is not None:
            print(f"  Response: {e.response.text[:500]}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
