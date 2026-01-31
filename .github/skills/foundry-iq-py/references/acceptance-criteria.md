# Foundry IQ Python SDK Acceptance Criteria

**SDK**: `azure-search-documents`, `azure-ai-projects`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: Latest (2025-11-01-preview API)
**Purpose**: Skill testing acceptance criteria for validating agentic retrieval code correctness

---

## 1. Correct Import Patterns

### 1.1 SearchIndexClient Imports

#### ✅ CORRECT: Import from indexes module
```python
from azure.search.documents.indexes import SearchIndexClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Knowledge base related imports
```python
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    VectorSearch,
    SemanticSearch,
    KnowledgeBase,
    KnowledgeSource,
)
```

#### ✅ CORRECT: Retrieval client imports
```python
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest,
    KnowledgeBaseMessage,
    KnowledgeBaseMessageTextContent,
)
```

### 1.2 AIProjectClient Imports

#### ✅ CORRECT: Project client for MCP connections
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: MCP and agent models
```python
from azure.ai.projects.models import MCPTool, PromptAgentDefinition
```

### 1.3 Authentication Imports

#### ✅ CORRECT: DefaultAzureCredential
```python
from azure.identity import DefaultAzureCredential
from azure.identity import get_bearer_token_provider
```

#### ✅ CORRECT: Async authentication
```python
from azure.identity.aio import DefaultAzureCredential
from azure.identity import get_bearer_token_provider
```

### 1.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module paths
```python
# WRONG - SearchIndexClient is not in models
from azure.search.documents.models import SearchIndexClient

# WRONG - KnowledgeBase models are not directly accessible
from azure.search.documents import KnowledgeBase

# WRONG - Old API version imports
from azure.search.documents.v11 import SearchIndexClient
```

#### ❌ INCORRECT: Mixing incompatible SDKs
```python
# WRONG - Using old api_version parameter (deprecated)
from WRONG_old_api_version import SearchIndexClient_with_api_version
client = SearchIndexClient_with_api_version(endpoint, api_version="2021-04-30-preview")

# WRONG - Hardcoded credentials
from WRONG_hardcoded_credentials import SearchIndexClient_with_api_key
client = SearchIndexClient_with_api_key(endpoint=endpoint, api_key="hardcoded-key")
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: SearchIndexClient with Context Manager
```python
from azure.search.documents.indexes import SearchIndexClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
index_client = SearchIndexClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    credential=credential
)
```

### 2.2 ✅ CORRECT: KnowledgeBaseRetrievalClient
```python
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.identity import DefaultAzureCredential

kb_client = KnowledgeBaseRetrievalClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    knowledge_base_name="my-knowledge-base",
    credential=DefaultAzureCredential()
)
```

### 2.3 ✅ CORRECT: AIProjectClient for Connections
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)

with project_client:
    # Use project_client for connection management
    pass
```

### 2.4 ✅ CORRECT: Async Client
```python
from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
from azure.identity.aio import DefaultAzureCredential

async with KnowledgeBaseRetrievalClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    knowledge_base_name="my-knowledge-base",
    credential=DefaultAzureCredential()
) as kb_client:
    result = await kb_client.retrieve(request)
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - using 'url' instead of 'endpoint'
client = SearchIndexClient(url=endpoint, credential=credential)

# WRONG - mixing positional arguments incorrectly
client = SearchIndexClient(os.environ["AZURE_SEARCH_ENDPOINT"], None)
```

#### ❌ INCORRECT: Missing context manager
```python
# WRONG - not using context manager
client = SearchIndexClient(endpoint=endpoint, credential=credential)
index = client.create_or_update_index(index)
# Missing: client.close()
```

---

## 3. Search Index Creation Patterns

### 3.1 ✅ CORRECT: Index with Semantic Configuration (Required)
```python
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SemanticSearch,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
)

index = SearchIndex(
    name="my-index",
    fields=[
        SearchField(name="id", type="Edm.String", key=True, filterable=True),
        SearchField(name="content", type="Edm.String", searchable=True),
        SearchField(
            name="embedding",
            type="Collection(Edm.Single)",
            stored=False,
            vector_search_dimensions=3072,
            vector_search_profile_name="hnsw-profile"
        ),
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
                resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
                deployment_name="text-embedding-3-large",
                model_name="text-embedding-3-large"
            )
        )]
    ),
    semantic_search=SemanticSearch(  # REQUIRED for agentic retrieval
        default_configuration_name="semantic-config",
        configurations=[SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            )
        )]
    )
)

index_client.create_or_update_index(index)
```

### 3.2 ✅ CORRECT: Hybrid Search Index
```python
index = SearchIndex(
    name="hybrid-index",
    fields=[
        SearchField(name="id", type="Edm.String", key=True),
        SearchField(name="content", type="Edm.String", searchable=True, analyzer_name="standard.lucene"),
        SearchField(
            name="vector",
            type="Collection(Edm.Single)",
            vector_search_dimensions=3072,
            vector_search_profile_name="hnsw-profile"
        ),
    ],
    vector_search=VectorSearch(...),
    semantic_search=SemanticSearch(...)
)
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing semantic configuration
```python
# WRONG - semantic_search is required for agentic retrieval
WRONG_index_missing_semantic = WRONG_SearchIndex(
    name="wrong-missing-semantic-config",
    fields=[...],
    vector_search=WRONG_VectorSearch(...),
    # Missing: semantic_search=SemanticSearch(...)
)
```

#### ❌ INCORRECT: Wrong field types
```python
# WRONG - embedding field must be Collection(Edm.Single)
WRONG_SearchField(name="wrong-embedding", type="Edm.String")

# WRONG - dimension mismatch
WRONG_SearchField(name="wrong-embedding", type="Collection(Edm.Single)", vector_search_dimensions=768)
# But using text-embedding-3-large (3072 dimensions)
```

#### ❌ INCORRECT: Missing vectorizer configuration
```python
# WRONG - vector search without vectorizer
WRONG_VectorSearch_no_vectorizer(
    profiles=[...],
    algorithms=[...],
    # Missing: vectorizers=[...]
)
```

---

## 4. Knowledge Source Patterns

### 4.1 ✅ CORRECT: Create Knowledge Source
```python
from azure.search.documents.indexes.models import (
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
    SearchIndexFieldReference,
)

ks = SearchIndexKnowledgeSource(
    name="my-knowledge-source",
    description="Knowledge source for retrieval",
    search_index_parameters=SearchIndexKnowledgeSourceParameters(
        search_index_name="my-index",
        source_data_fields=[
            SearchIndexFieldReference(name="id"),
            SearchIndexFieldReference(name="content"),
        ]
    )
)

index_client.create_or_update_knowledge_source(knowledge_source=ks)
```

### 4.2 ✅ CORRECT: Multiple Field References
```python
source_data_fields=[
    SearchIndexFieldReference(name="id"),
    SearchIndexFieldReference(name="content"),
    SearchIndexFieldReference(name="metadata"),
]
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Empty field references
```python
# WRONG - no source_data_fields
SearchIndexKnowledgeSourceParameters(
    search_index_name="my-index",
    # Missing: source_data_fields=...
)
```

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - using 'index_name' instead of 'search_index_name'
SearchIndexKnowledgeSourceParameters(
    index_name="my-index"
)
```

---

## 5. Knowledge Base Creation Patterns

### 5.1 ✅ CORRECT: Create Knowledge Base with Extractive Output
```python
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeBaseAzureOpenAIModel,
    KnowledgeSourceReference,
    AzureOpenAIVectorizerParameters,
    KnowledgeRetrievalOutputMode,
    KnowledgeRetrievalLowReasoningEffort,
)

aoai_params = AzureOpenAIVectorizerParameters(
    resource_url=os.environ["AZURE_OPENAI_ENDPOINT"],
    deployment_name="gpt-4.1-mini",
    model_name="gpt-4.1-mini"
)

kb = KnowledgeBase(
    name="my-knowledge-base",
    knowledge_sources=[KnowledgeSourceReference(name="my-knowledge-source")],
    models=[KnowledgeBaseAzureOpenAIModel(azure_open_ai_parameters=aoai_params)],
    output_mode=KnowledgeRetrievalOutputMode.EXTRACTIVE_DATA,  # Recommended for agents
    retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort()
)

index_client.create_or_update_knowledge_base(knowledge_base=kb)

# Generate MCP endpoint
mcp_endpoint = f"{search_endpoint}/knowledgebases/{kb.name}/mcp?api-version=2025-11-01-preview"
```

### 5.2 ✅ CORRECT: Different Reasoning Effort Levels
```python
from azure.search.documents.indexes.models import (
    KnowledgeRetrievalMinimalReasoningEffort,
    KnowledgeRetrievalMediumReasoningEffort,
)

# Minimal - fastest, cheapest
KnowledgeRetrievalMinimalReasoningEffort()

# Low - balanced (default)
KnowledgeRetrievalLowReasoningEffort()

# Medium - best quality for complex queries
KnowledgeRetrievalMediumReasoningEffort()
```

### 5.3 ✅ CORRECT: Answer Synthesis Output Mode
```python
kb = KnowledgeBase(
    name="my-knowledge-base",
    knowledge_sources=[...],
    models=[...],
    output_mode=KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS,  # For direct responses with citations
    retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort()
)
```

### 5.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing output_mode
```python
# WRONG - output_mode is required
WRONG_kb_missing_output_mode = WRONG_KnowledgeBase(
    name="wrong-missing-output-mode",
    knowledge_sources=[...],
    models=[...],
    # Missing: output_mode=...
)
```

#### ❌ INCORRECT: Wrong model type
```python
# WRONG - using incompatible model configuration
models=[WRONG_AzureOpenAIModel_not_KB(...)]  # Should be KnowledgeBaseAzureOpenAIModel

# WRONG - missing azure_open_ai_parameters
WRONG_KnowledgeBaseAzureOpenAIModel_no_params()
```

---

## 6. Project Connection Patterns

### 6.1 ✅ CORRECT: Create Connection with Bearer Token
```python
import requests
from azure.identity import get_bearer_token_provider

credential = DefaultAzureCredential()
bearer_token = get_bearer_token_provider(credential, "https://management.azure.com/.default")()

response = requests.put(
    f"https://management.azure.com{project_resource_id}/connections/{connection_name}?api-version=2025-10-01-preview",
    headers={"Authorization": f"Bearer {bearer_token}"},
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
```

### 6.2 ✅ CORRECT: Connection with SharePoint User Token
```python
bearer_token_provider = get_bearer_token_provider(credential, "https://search.azure.com/.default")

# Use in MCP tool headers
mcp_tool_headers = {
    "x-ms-query-source-authorization": bearer_token_provider()
}
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong audience scope
```python
# WRONG - using wrong scope for search
bearer_token = get_bearer_token_provider(credential, "https://graph.microsoft.com/.default")()
```

**Correct approach:** Use `https://management.azure.com/.default` as the scope for Azure Search operations, not Graph or other services.

#### ❌ INCORRECT: Missing error handling
```python
# WRONG - not checking response
response = requests.put(...)
# Missing: response.raise_for_status()
```

---

## 7. MCP Tool Integration Patterns

### 7.1 ✅ CORRECT: Create MCPTool for Agent
```python
from azure.ai.projects.models import MCPTool

mcp_tool = MCPTool(
    server_label="knowledge-base",
    server_url=mcp_endpoint,
    require_approval="never",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id=connection_name
)

agent = client.agents.create_version(
    agent_name="rag-agent",
    definition=PromptAgentDefinition(
        model="gpt-4.1-mini",
        instructions="Use the knowledge base to answer questions.",
        tools=[mcp_tool]
    )
)
```

### 7.2 ✅ CORRECT: MCPTool with User Token Headers
```python
from azure.identity import get_bearer_token_provider

mcp_tool = MCPTool(
    server_label="knowledge-base",
    server_url=mcp_endpoint,
    require_approval="never",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id=connection_name,
    headers={
        "x-ms-query-source-authorization": get_bearer_token_provider(
            credential,
            "https://search.azure.com/.default"
        )()
    }
)
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong tool names
```python
# WRONG - allowed_tools must match actual MCP tool names
WRONG_allowed_tools=["retrieve", "search"]  # Should be ["knowledge_base_retrieve"]
```

#### ❌ INCORRECT: Missing project_connection_id
```python
# WRONG - connection_id is required
WRONG_MCPTool_missing_connection(
    wrong_server_label="wrong-label",
    wrong_server_url=wrong_endpoint,
    # Missing: project_connection_id=...
)
```

---

## 8. Knowledge Base Retrieval Patterns

### 8.1 ✅ CORRECT: Direct KB Query with Citations
```python
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest,
    KnowledgeBaseMessage,
    KnowledgeBaseMessageTextContent,
    SearchIndexKnowledgeSourceParams,
)

kb_client = KnowledgeBaseRetrievalClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    knowledge_base_name="my-knowledge-base",
    credential=DefaultAzureCredential()
)

request = KnowledgeBaseRetrievalRequest(
    messages=[KnowledgeBaseMessage(
        role="user",
        content=[KnowledgeBaseMessageTextContent(text="What is vector search?")]
    )],
    knowledge_source_params=[SearchIndexKnowledgeSourceParams(
        knowledge_source_name="my-knowledge-source",
        include_references=True,
        include_reference_source_data=True
    )],
    include_activity=True
)

result = kb_client.retrieve(request)
print(result.response[0].content[0].text)
```

### 8.2 ✅ CORRECT: Async Retrieval
```python
from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient

async with KnowledgeBaseRetrievalClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    knowledge_base_name="my-knowledge-base",
    credential=DefaultAzureCredential()
) as kb_client:
    result = await kb_client.retrieve(request)
```

### 8.3 ✅ CORRECT: Multiple Knowledge Sources
```python
knowledge_source_params=[
    SearchIndexKnowledgeSourceParams(
        knowledge_source_name="source-1",
        include_references=True,
        include_reference_source_data=True
    ),
    SearchIndexKnowledgeSourceParams(
        knowledge_source_name="source-2",
        include_references=True,
        include_reference_source_data=True
    ),
]
```

### 8.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing knowledge_base_name
```python
# WRONG - knowledge_base_name is required
KnowledgeBaseRetrievalClient(
    endpoint=endpoint,
    credential=credential
    # Missing: knowledge_base_name=...
)
```

#### ❌ INCORRECT: Not including references
```python
# WRONG - references needed for citations
SearchIndexKnowledgeSourceParams(
    knowledge_source_name="source",
    include_references=False,  # Should be True for RAG
)
```

---

## 9. Agent Integration Patterns

### 9.1 ✅ CORRECT: Agent with KB Instructions
```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)

instructions = """You are a helpful assistant that must use the knowledge base to answer all questions.
Every answer must provide annotations: 【message_idx:search_idx†source_name】
If you cannot find the answer in the provided knowledge base, respond with "I don't know"."""

mcp_tool = MCPTool(
    server_label="knowledge-base",
    server_url=mcp_endpoint,
    require_approval="never",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id=connection_name
)

agent = client.agents.create_version(
    agent_name="kb-agent",
    definition=PromptAgentDefinition(
        model="gpt-4.1-mini",
        instructions=instructions,
        tools=[mcp_tool]
    )
)
```

### 9.2 ✅ CORRECT: Invoke Agent with Tool Choice Required
```python
openai_client = client.get_openai_client()
conversation = openai_client.conversations.create()

response = openai_client.responses.create(
    conversation=conversation.id,
    tool_choice="required",  # Ensures agent always uses KB
    input="What are the key findings?",
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
)

print(response.output_text)
```

### 9.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing tool_choice="required"
```python
# WRONG - agent might not use knowledge base
WRONG_response = wrong_client.WRONG_responses_create(
    WRONG_conversation=wrong_conversation_id,
    # Missing: tool_choice="required"
    WRONG_input="Question"
)
```

#### ❌ INCORRECT: Wrong agent reference format
```python
# WRONG - missing type specification
WRONG_extra_body={"WRONG_agent": {"WRONG_name": wrong_agent_name}}
```

**Correct approach:** Always include the `"type": "agent_reference"` field in the agent specification. This tells the API that you're referencing an existing agent by name, not creating a new one.

---

## 10. Hybrid Search Patterns

### 10.1 ✅ CORRECT: Semantic Reranking Query
```python
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

search_client = SearchClient(endpoint=endpoint, index_name="my-index", credential=credential)

# Hybrid search with semantic reranking
results = search_client.search(
    search_text="vector search benefits",
    vector_queries=[
        VectorizedQuery(
            vector=embedding_vector,
            k_nearest_neighbors=50,
            fields="embedding"
        )
    ],
    select=["id", "content"],
    query_type="semantic",
    semantic_configuration_name="semantic-config",
)

for result in results:
    print(f"Score: {result['@search.score']}")
    print(f"Content: {result['content']}")
```

### 10.2 ✅ CORRECT: Pure Vector Search
```python
results = search_client.search(
    search_text=None,
    vector_queries=[
        VectorizedQuery(
            vector=embedding_vector,
            k_nearest_neighbors=10,
            fields="embedding"
        )
    ]
)
```

### 10.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing query_type for semantic
```python
# WRONG - semantic_configuration_name without query_type
results = search_client.search(
    search_text="query",
    semantic_configuration_name="semantic-config"
    # Missing: query_type="semantic"
)
```

#### ❌ INCORRECT: Wrong embedding vector format
```python
# WRONG - vector must be a list of floats
VectorizedQuery(
    vector="embedding_string",  # Should be list of floats
    k_nearest_neighbors=10
)
```

---

## 11. Environment Variables

### ✅ CORRECT: Required Configuration
```bash
AZURE_SEARCH_ENDPOINT=https://<search-service>.search.windows.net
AZURE_OPENAI_ENDPOINT=https://<openai-resource>.openai.azure.com
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
```

### ✅ CORRECT: Optional for Specific Scenarios
```bash
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4.1-mini
AZURE_SEARCH_SEMANTIC_RANKER=default
```

---

## 12. API Version Reference

### ✅ CORRECT: Current API Version
```
api-version=2025-11-01-preview
```

Used in:
- Knowledge base MCP endpoint generation
- Project connection creation (2025-10-01-preview)

---

## 13. Quick Reference: Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `KnowledgeBase not found` | Wrong KB name or not created | Verify KB exists, check name |
| `Semantic search failed` | Missing semantic configuration | Add `semantic_search=SemanticSearch(...)` to index |
| `MCP tool not called` | Missing `tool_choice="required"` | Set `tool_choice="required"` in response creation |
| `Bearer token expired` | Token cached too long | Regenerate bearer token on each request |
| `Connection not found` | Missing project connection | Create connection with requests API first |
| `Vector dimension mismatch` | Wrong embedding size | Ensure dimensions match deployment (3072 for text-embedding-3-large) |
| `Field reference invalid` | Non-existent field name | Verify field exists in index definition |

---

## 14. Test Scenarios Checklist

### Index Creation
- [ ] Index with required semantic configuration
- [ ] Hybrid search with vector + text fields
- [ ] Correct vector dimensions (3072 for text-embedding-3-large)

### Knowledge Sources & Bases
- [ ] Create knowledge source with field references
- [ ] Create knowledge base with extractive output
- [ ] Create knowledge base with answer synthesis output
- [ ] Test different reasoning effort levels

### Project Connections
- [ ] Create connection with bearer token
- [ ] Handle authentication properly
- [ ] Support SharePoint with user token

### Agentic Retrieval
- [ ] Create MCPTool for knowledge base
- [ ] Invoke agent with `tool_choice="required"`
- [ ] Agent uses knowledge base for RAG

### Direct Retrieval
- [ ] Query knowledge base directly
- [ ] Include citations in responses
- [ ] Handle multiple knowledge sources

### Hybrid Search
- [ ] Semantic reranking queries
- [ ] Pure vector search
- [ ] Text + vector hybrid search

### Error Handling
- [ ] Check for missing semantic configuration
- [ ] Validate bearer token availability
- [ ] Handle API version compatibility
