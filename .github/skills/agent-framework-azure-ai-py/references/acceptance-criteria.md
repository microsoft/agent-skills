# Agent Framework Azure AI Python Acceptance Criteria

**SDK**: `agent-framework-azure-ai`
**Repository**: https://github.com/microsoft/agent-framework
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Provider & Credential Imports

#### ✅ CORRECT: Provider and async credentials
```python
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential
```

### 1.2 Hosted Tools Imports

#### ✅ CORRECT: Hosted tool classes
```python
from agent_framework import (
    HostedCodeInterpreterTool,
    HostedFileSearchTool,
    HostedWebSearchTool,
    HostedFileContent,
    HostedVectorStoreContent,
)
```

### 1.3 MCP Tool Imports

#### ✅ CORRECT: MCP tool classes
```python
from agent_framework import HostedMCPTool, MCPStreamableHTTPTool
```

### 1.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing from wrong modules
```python
# WRONG - Hosted tools are in agent_framework, not agent_framework.azure
from agent_framework.azure import HostedCodeInterpreterTool

# WRONG - Provider is not in agent_framework directly
from agent_framework import AzureAIAgentsProvider

# WRONG - sync credential for async usage
from azure.identity import DefaultAzureCredential
```

---

## 2. AzureAIAgentsProvider Patterns

### 2.1 ✅ CORRECT: Async context manager usage
```python
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential

async with (
    AzureCliCredential() as credential,
    AzureAIAgentsProvider(credential=credential) as provider,
):
    agent = await provider.create_agent(
        name="MyAgent",
        instructions="You are a helpful assistant.",
    )
```

### 2.2 ✅ CORRECT: Provider with explicit configuration
```python
provider = AzureAIAgentsProvider(
    credential=credential,
    project_endpoint="https://example.services.ai.azure.com/api/projects/my-project",
    model_deployment_name="gpt-4o-mini",
)
```

### 2.3 ✅ CORRECT: Provider with existing AgentsClient
```python
from azure.ai.agents.aio import AgentsClient
from agent_framework.azure import AzureAIAgentsProvider

agents_client = AgentsClient(endpoint=endpoint, credential=credential)
provider = AzureAIAgentsProvider(agents_client=agents_client)
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using context manager
```python
provider = AzureAIAgentsProvider(credential=credential)
agent = await provider.create_agent(...)  # Missing async context manager
```

#### ❌ INCORRECT: Mixing sync credential with async provider
```python
from azure.identity import DefaultAzureCredential

async with AzureAIAgentsProvider(credential=DefaultAzureCredential()) as provider:
    ...
```

---

## 3. Persistent Agents & Threads

### 3.1 ✅ CORRECT: Multi-turn conversation with a thread
```python
thread = agent.get_new_thread()

result1 = await agent.run("My name is Alice", thread=thread)
result2 = await agent.run("What is my name?", thread=thread)
print(thread.conversation_id)
```

### 3.2 ✅ CORRECT: Retrieve existing agent by ID
```python
agent = await provider.get_agent(agent_id=agent_id)
```

### 3.3 ✅ CORRECT: Resume with existing service thread ID
```python
from agent_framework import AgentThread

thread = AgentThread(service_thread_id=service_thread_id)
result = await agent.run("Continue our conversation", thread=thread)
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Creating a new thread per message
```python
for message in messages:
    thread = agent.get_new_thread()  # Loses context
    await agent.run(message, thread=thread)
```

#### ❌ INCORRECT: Omitting thread for multi-turn conversations
```python
await agent.run("Message 1")
await agent.run("Message 2")  # No thread; context not preserved
```

---

## 4. Hosted Tools

### 4.1 ✅ CORRECT: HostedCodeInterpreterTool
```python
from agent_framework import HostedCodeInterpreterTool, HostedFileContent

code_tool = HostedCodeInterpreterTool(
    inputs=[HostedFileContent(file_id="file-abc123")],
)

agent = await provider.create_agent(
    name="DataAnalyst",
    instructions="Analyze the provided file.",
    tools=code_tool,
)
```

### 4.2 ✅ CORRECT: HostedFileSearchTool with vector store
```python
from agent_framework import HostedFileSearchTool, HostedVectorStoreContent

file_search_tool = HostedFileSearchTool(
    inputs=[HostedVectorStoreContent(vector_store_id=vector_store.id)],
    max_results=10,
)

agent = await provider.create_agent(
    name="ResearchAgent",
    instructions="Search uploaded documents.",
    tools=file_search_tool,
)
```

### 4.3 ✅ CORRECT: HostedWebSearchTool (Bing)
```python
from agent_framework import HostedWebSearchTool

agent = await provider.create_agent(
    name="SearchAgent",
    instructions="Use web search for current info.",
    tools=HostedWebSearchTool(
        name="Bing Grounding Search",
        description="Search the web for current information",
    ),
)
```

### 4.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Passing tool names as strings
```python
agent = await provider.create_agent(
    name="BadAgent",
    instructions="...",
    tools=["code_interpreter"],
)
```

#### ❌ INCORRECT: File search without vector store inputs
```python
file_search_tool = HostedFileSearchTool(inputs=[])
agent = await provider.create_agent(tools=file_search_tool)
```

---

## 5. MCP Server Integration

### 5.1 ✅ CORRECT: HostedMCPTool (service-managed)
```python
from agent_framework import HostedMCPTool

agent = await provider.create_agent(
    name="DocsAgent",
    instructions="Use Microsoft Learn MCP.",
    tools=HostedMCPTool(
        name="Microsoft Learn MCP",
        url="https://learn.microsoft.com/api/mcp",
        approval_mode="never_require",
        allowed_tools=["microsoft_docs_search", "microsoft_docs_read"],
    ),
)
```

### 5.2 ✅ CORRECT: MCPStreamableHTTPTool (client-managed)
```python
from agent_framework import MCPStreamableHTTPTool

async with MCPStreamableHTTPTool(
    name="Docs MCP",
    url="https://learn.microsoft.com/api/mcp",
) as mcp_tool:
    agent = await provider.create_agent(
        name="DocsAgent",
        instructions="Answer questions using docs.",
        tools=mcp_tool,
    )
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing context manager for MCPStreamableHTTPTool
```python
mcp_tool = MCPStreamableHTTPTool(name="Docs MCP", url="https://learn.microsoft.com/api/mcp")
agent = await provider.create_agent(tools=mcp_tool)  # Missing async context manager
```

---

## 6. Streaming Patterns

### 6.1 ✅ CORRECT: Stream responses with async iterator
```python
print("Agent:", end=" ")
async for chunk in agent.run_stream("Tell me a story"):
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

### 6.2 ✅ CORRECT: Streaming with threads
```python
thread = agent.get_new_thread()
async for chunk in agent.run_stream("Continue", thread=thread):
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using sync iteration for streaming
```python
for chunk in agent.run_stream("Hello"):
    print(chunk.text)
```

#### ❌ INCORRECT: Deprecated stream flag
```python
response = await agent.run("Hello", stream=True)
```
