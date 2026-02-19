# Async Patterns Reference

## Async Client Setup

```python
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

# Requires: pip install aiohttp

async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            credential=credential,
        ) as client,
    ):
        # Use async operations
        pass

asyncio.run(main())
```

## Async Agent Operations

### Create Agent

```python
async with AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
) as client:
    agent = await client.agents.create_agent(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        name="async-agent",
        instructions="You are helpful.",
    )
    print(f"Created agent: {agent.id}")
    
    # Clean up
    await client.agents.delete_agent(agent.id)
```

### Full Conversation Flow

```python
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

async def async_conversation():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            credential=credential,
        ) as client,
    ):
        # Create agent
        agent = await client.agents.create_agent(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            name="async-agent",
            instructions="You are a helpful assistant.",
        )
        
        # Create thread
        thread = await client.agents.threads.create()
        
        # Add message
        await client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content="What is the capital of Japan?",
        )
        
        # Create and process run
        run = await client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
        )
        
        # Get messages
        if run.status == "completed":
            messages = await client.agents.messages.list(thread_id=thread.id)
            async for msg in messages:
                if msg.role == "assistant":
                    print(f"Response: {msg.content[0].text.value}")
        
        # Clean up
        await client.agents.delete_agent(agent.id)

asyncio.run(async_conversation())
```

## Async File Operations

```python
from azure.ai.agents.models import FilePurpose

async with AIProjectClient(...) as client:
    # Upload file
    file = await client.agents.files.upload_and_poll(
        file_path="./data/document.pdf",
        purpose=FilePurpose.AGENTS,
    )
    
    # Create vector store
    vector_store = await client.agents.vector_stores.create_and_poll(
        file_ids=[file.id],
        name="async-vector-store",
    )
```

## Async Connections and Deployments

```python
async with AIProjectClient(...) as client:
    # List connections
    connections = client.connections.list()
    async for conn in connections:
        print(f"Connection: {conn.name}")
    
    # List deployments
    deployments = client.deployments.list()
    async for deployment in deployments:
        print(f"Deployment: {deployment.name}")
```

## Async Streaming

```python
from azure.ai.agents.aio import AsyncAgentEventHandler

class AsyncHandler(AsyncAgentEventHandler):
    async def on_message_delta(self, delta):
        if delta.text:
            print(delta.text.value, end="", flush=True)
    
    async def on_error(self, data):
        print(f"Error: {data}")

async with AIProjectClient(...) as client:
    async with client.agents.runs.stream(
        thread_id=thread.id,
        agent_id=agent.id,
        event_handler=AsyncHandler(),
    ) as stream:
        await stream.until_done()
```

## Concurrent Operations

```python
import asyncio

async def process_multiple_queries(client, agent_id, queries):
    """Process multiple queries concurrently."""
    
    async def process_query(query):
        thread = await client.agents.threads.create()
        await client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=query,
        )
        run = await client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent_id,
        )
        if run.status == "completed":
            messages = await client.agents.messages.list(thread_id=thread.id)
            async for msg in messages:
                if msg.role == "assistant":
                    return msg.content[0].text.value
        return None
    
    # Process all queries concurrently
    results = await asyncio.gather(*[process_query(q) for q in queries])
    return results

# Usage
async with AIProjectClient(...) as client:
    queries = [
        "What is Python?",
        "What is JavaScript?",
        "What is Rust?",
    ]
    results = await process_multiple_queries(client, agent.id, queries)
    for query, result in zip(queries, results):
        print(f"Q: {query}")
        print(f"A: {result}\n")
```

## Error Handling

```python
from azure.core.exceptions import HttpResponseError

async with AIProjectClient(...) as client:
    try:
        agent = await client.agents.create_agent(...)
    except HttpResponseError as e:
        print(f"HTTP Error: {e.status_code}")
        print(f"Message: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Context Manager Best Practices

```python
# RECOMMENDED: Use nested context managers
async with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as client,
):
    # Both credential and client are properly managed
    pass

# ALSO OK: Sequential context managers
async with DefaultAzureCredential() as credential:
    async with AIProjectClient(endpoint=endpoint, credential=credential) as client:
        pass

# AVOID: Manual resource management
client = AIProjectClient(endpoint=endpoint, credential=credential)
try:
    # ... operations
finally:
    await client.close()  # Easy to forget
```

## Async Memory Store Operations

```python
from azure.ai.projects.models import ItemParam, MemoryStoreUpdateCompletedResult
from azure.core.polling import AsyncLROPoller

async with AIProjectClient(...) as client:
    poller: AsyncLROPoller[MemoryStoreUpdateCompletedResult] = (
        await client.memory_stores.begin_update_memories(
            name="conversation-memory",
            scope="user123",
            items=[
                ItemParam(role="user", content="Hello!"),
                ItemParam(role="assistant", content="Hi there!"),
            ],
            previous_update_id=None,
            update_delay=300,
        )
    )
    result = await poller.result()
    print(f"Memory updated: {result}")
```
