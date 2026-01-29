# Tools Reference

Comprehensive guide to all tool types in the Azure AI Agents SDK.

## Table of Contents

- [Code Interpreter](#code-interpreter)
- [File Search](#file-search)
- [Bing Grounding](#bing-grounding)
- [Azure AI Search](#azure-ai-search)
- [Function Calling](#function-calling)
- [OpenAPI Tools](#openapi-tools)
- [MCP Tools](#mcp-tools)
- [Azure Functions](#azure-functions)
- [Fabric Tools](#fabric-tools)
- [Connected Agents](#connected-agents)

---

## Code Interpreter

Execute Python code, generate files, and analyze data.

```python
from azure.ai.agents import CodeInterpreterTool

# Basic usage
agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="code-agent",
    instructions="You can execute Python code.",
    tools=[CodeInterpreterTool()],
)

# With files
file = client.files.upload_and_poll(file_path="data.csv", purpose="assistants")
agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[CodeInterpreterTool()],
    tool_resources={"code_interpreter": {"file_ids": [file.id]}},
)
```

### Retrieving Generated Files

```python
run = client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

# Get file references from run steps
run_steps = client.run_steps.list(thread_id=thread.id, run_id=run.id)
for step in run_steps:
    if step.type == "tool_calls":
        for tool_call in step.step_details.tool_calls:
            if tool_call.type == "code_interpreter":
                for output in tool_call.code_interpreter.outputs:
                    if output.type == "image":
                        file_id = output.image.file_id
                        # Download: client.files.retrieve_content(file_id)
```

---

## File Search

RAG over uploaded documents using vector stores.

```python
from azure.ai.agents import FileSearchTool

# 1. Upload files
file = client.files.upload_and_poll(file_path="docs.pdf", purpose="assistants")

# 2. Create vector store
vector_store = client.vector_stores.create_and_poll(
    file_ids=[file.id],
    name="knowledge-base",
)

# 3. Create agent with file search
agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[FileSearchTool()],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)
```

### With Chunking Strategy

```python
from azure.ai.agents import (
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
    VectorStoreChunkingStrategyStaticConfiguration,
)

vector_store = client.vector_stores.create_and_poll(
    data_sources=[
        VectorStoreDataSource(
            asset_identifier=file.id,
            asset_type=VectorStoreDataSourceAssetType.FILE_ID,
        )
    ],
    chunking_strategy=VectorStoreChunkingStrategyStaticConfiguration(
        max_chunk_size_tokens=800,
        chunk_overlap_tokens=400,
    ),
)
```

### Attach to Thread (Thread-Level)

```python
thread = client.threads.create(
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)
```

---

## Bing Grounding

Web search using Bing.

```python
from azure.ai.agents import BingGroundingTool

# Requires Bing connection in Azure AI Foundry
bing_connection_id = "/subscriptions/.../connections/bing-connection"

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[BingGroundingTool(connection_id=bing_connection_id)],
    instructions="Search the web for current information.",
)
```

---

## Azure AI Search

Query your Azure AI Search indexes.

```python
from azure.ai.agents import AzureAISearchTool

search_connection_id = "/subscriptions/.../connections/search-connection"

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[
        AzureAISearchTool(
            index_connection_id=search_connection_id,
            index_name="products-index",
        )
    ],
)
```

---

## Function Calling

Call custom Python functions.

### Basic Function

```python
from azure.ai.agents import FunctionTool, ToolSet

def get_weather(location: str) -> str:
    """Get weather for a location.
    
    Args:
        location: City name
        
    Returns:
        Weather information
    """
    return f"Weather in {location}: 72F, sunny"

def get_time(timezone: str = "UTC") -> str:
    """Get current time in timezone."""
    from datetime import datetime
    return datetime.now().isoformat()

# Create function tool
functions = FunctionTool(functions=[get_weather, get_time])

# Add to toolset for auto-execution
toolset = ToolSet()
toolset.add(functions)

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    toolset=toolset,
)

# Run with toolset - functions auto-execute
run = client.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id,
    toolset=toolset,
)
```

### User-Defined Function with Schema

```python
from azure.ai.agents import FunctionTool

# Define schema explicitly
user_functions = [
    {
        "name": "search_products",
        "description": "Search product catalog",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    }
]

functions = FunctionTool(functions=user_functions)

# Manual handling (no toolset)
agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=functions.definitions,
)

run = client.runs.create(thread_id=thread.id, agent_id=agent.id)

# Poll and handle tool calls manually
while run.status in ["queued", "in_progress", "requires_action"]:
    if run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        for call in tool_calls:
            if call.function.name == "search_products":
                args = json.loads(call.function.arguments)
                result = my_search_function(args["query"])
                tool_outputs.append({"tool_call_id": call.id, "output": result})
        
        run = client.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs,
        )
    else:
        run = client.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(1)
```

---

## OpenAPI Tools

Call REST APIs defined by OpenAPI specs.

```python
from azure.ai.agents import OpenApiTool, OpenApiAnonymousAuthDetails

# Load spec
with open("weather_api.json") as f:
    spec = json.load(f)

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[
        OpenApiTool(
            name="weather_api",
            description="Weather service API",
            spec=spec,
            auth=OpenApiAnonymousAuthDetails(),
        )
    ],
)
```

### With Connection Auth

```python
from azure.ai.agents import OpenApiConnectionAuthDetails

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[
        OpenApiTool(
            name="secure_api",
            spec=spec,
            auth=OpenApiConnectionAuthDetails(
                security_scheme="api_key",
                connection_id="/subscriptions/.../connections/api-connection",
            ),
        )
    ],
)
```

### With Managed Identity

```python
from azure.ai.agents import OpenApiManagedAuthDetails

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[
        OpenApiTool(
            name="azure_api",
            spec=spec,
            auth=OpenApiManagedAuthDetails(
                security_scheme="oauth2",
                audience="https://management.azure.com",
            ),
        )
    ],
)
```

---

## MCP Tools

Model Context Protocol server integration.

```python
from azure.ai.agents import McpTool

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[
        McpTool(
            server_label="docs-server",
            server_url="https://mcp.example.com",
            allowed_tools=["search", "get_document"],  # Optional: limit tools
        )
    ],
)
```

---

## Azure Functions

Call Azure Functions directly.

```python
from azure.ai.agents import AzureFunctionTool, AzureFunctionStorageQueue

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[
        AzureFunctionTool(
            name="process_data",
            description="Process data using Azure Function",
            input_queue=AzureFunctionStorageQueue(
                queue_name="input-queue",
                storage_service_endpoint="https://storage.queue.core.windows.net",
            ),
            output_queue=AzureFunctionStorageQueue(
                queue_name="output-queue",
                storage_service_endpoint="https://storage.queue.core.windows.net",
            ),
            parameters={
                "type": "object",
                "properties": {
                    "data": {"type": "string"},
                },
            },
        )
    ],
)
```

---

## Fabric Tools

Microsoft Fabric integration for data analysis.

```python
from azure.ai.agents import FabricTool

fabric_connection_id = "/subscriptions/.../connections/fabric-connection"

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[FabricTool(connection_id=fabric_connection_id)],
)
```

---

## Connected Agents

Chain multiple agents together.

```python
from azure.ai.agents import ConnectedAgentTool

# Create sub-agent
research_agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="researcher",
    instructions="You research topics thoroughly.",
)

# Create main agent with connected agent
main_agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="coordinator",
    instructions="Delegate research to the research agent.",
    tools=[
        ConnectedAgentTool(
            id=research_agent.id,
            name="research_agent",
            description="Agent that performs research",
        )
    ],
)
```

---

## Combining Multiple Tools

```python
from azure.ai.agents import (
    CodeInterpreterTool,
    FileSearchTool,
    BingGroundingTool,
    FunctionTool,
    ToolSet,
)

def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))

functions = FunctionTool(functions=[calculate])
toolset = ToolSet()
toolset.add(functions)

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[
        CodeInterpreterTool(),
        FileSearchTool(),
        BingGroundingTool(connection_id=bing_connection),
    ],
    tool_resources={
        "file_search": {"vector_store_ids": [vs.id]},
        "code_interpreter": {"file_ids": [file.id]},
    },
    toolset=toolset,
)
```
