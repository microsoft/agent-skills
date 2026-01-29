---
name: azure-ai-agents-py
description: Build AI agents using the Azure AI Agents Python SDK (azure-ai-agents). Use when creating agents hosted on Azure AI Foundry with tools (File Search, Code Interpreter, Bing Grounding, Azure AI Search, Function Calling, OpenAPI, MCP), managing threads and messages, implementing streaming responses, or working with vector stores. This is the low-level SDK - for higher-level abstractions, use the agent-framework skill instead.
---

# Azure AI Agents Python SDK

Build agents hosted on Azure AI Foundry using the `azure-ai-agents` SDK.

## Installation

```bash
pip install azure-ai-agents azure-identity
# Or with azure-ai-projects for additional features
pip install azure-ai-projects azure-identity
```

## Environment Variables

```bash
PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project>"
MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
```

## Authentication

```python
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

credential = DefaultAzureCredential()
client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=credential,
)
```

## Core Workflow

The basic agent lifecycle: **create agent → create thread → create message → create run → get response**

### Minimal Example

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# 1. Create agent
agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are a helpful assistant.",
)

# 2. Create thread
thread = client.threads.create()

# 3. Add message
client.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hello!",
)

# 4. Create and process run
run = client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

# 5. Get response
if run.status == "completed":
    messages = client.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.role == "assistant":
            print(msg.content[0].text.value)

# Cleanup
client.delete_agent(agent.id)
```

## Tools Overview

| Tool | Class | Use Case |
|------|-------|----------|
| Code Interpreter | `CodeInterpreterTool` | Execute Python, generate files |
| File Search | `FileSearchTool` | RAG over uploaded documents |
| Bing Grounding | `BingGroundingTool` | Web search |
| Azure AI Search | `AzureAISearchTool` | Search your indexes |
| Function Calling | `FunctionTool` | Call your Python functions |
| OpenAPI | `OpenApiTool` | Call REST APIs |
| MCP | `McpTool` | Model Context Protocol servers |

See [references/tools.md](references/tools.md) for detailed patterns.

## Adding Tools

```python
from azure.ai.agents import CodeInterpreterTool, FileSearchTool

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="tool-agent",
    instructions="You can execute code and search files.",
    tools=[CodeInterpreterTool()],
    tool_resources={"code_interpreter": {"file_ids": [file.id]}},
)
```

## Function Calling

```python
from azure.ai.agents import FunctionTool, ToolSet

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72F, sunny"

functions = FunctionTool(functions=[get_weather])
toolset = ToolSet()
toolset.add(functions)

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="function-agent",
    instructions="Help with weather queries.",
    toolset=toolset,
)

# Process run - toolset auto-executes functions
run = client.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id,
    toolset=toolset,  # Pass toolset for auto-execution
)
```

## Streaming

```python
from azure.ai.agents import AgentEventHandler

class MyHandler(AgentEventHandler):
    def on_message_delta(self, delta):
        if delta.text:
            print(delta.text.value, end="", flush=True)

    def on_error(self, data):
        print(f"Error: {data}")

with client.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
    event_handler=MyHandler(),
) as stream:
    stream.until_done()
```

See [references/streaming.md](references/streaming.md) for advanced patterns.

## File Operations

### Upload File

```python
file = client.files.upload_and_poll(
    file_path="data.csv",
    purpose="assistants",
)
```

### Create Vector Store

```python
vector_store = client.vector_stores.create_and_poll(
    file_ids=[file.id],
    name="my-store",
)

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    tools=[FileSearchTool()],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)
```

## Async Client

```python
from azure.ai.agents.aio import AgentsClient

async with AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
) as client:
    agent = await client.create_agent(...)
    # ... async operations
```

See [references/async-patterns.md](references/async-patterns.md) for async patterns.

## Response Format

### JSON Mode

```python
agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    response_format={"type": "json_object"},
)
```

### JSON Schema

```python
agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "weather_response",
            "schema": {
                "type": "object",
                "properties": {
                    "temperature": {"type": "number"},
                    "conditions": {"type": "string"},
                },
                "required": ["temperature", "conditions"],
            },
        },
    },
)
```

## Thread Management

### Continue Conversation

```python
# Save thread_id for later
thread_id = thread.id

# Resume later
client.messages.create(
    thread_id=thread_id,
    role="user",
    content="Follow-up question",
)
run = client.runs.create_and_process(thread_id=thread_id, agent_id=agent.id)
```

### List Messages

```python
messages = client.messages.list(thread_id=thread.id, order="asc")
for msg in messages:
    role = msg.role
    content = msg.content[0].text.value
    print(f"{role}: {content}")
```

## Best Practices

1. **Use context managers** for async client
2. **Clean up agents** when done: `client.delete_agent(agent.id)`
3. **Use `create_and_process`** for simple cases, **streaming** for real-time UX
4. **Pass toolset to run** for automatic function execution
5. **Poll operations** use `*_and_poll` methods for long operations

## Reference Files

- [references/tools.md](references/tools.md): All tool types with detailed examples
- [references/streaming.md](references/streaming.md): Event handlers and streaming patterns
- [references/async-patterns.md](references/async-patterns.md): Async client usage
