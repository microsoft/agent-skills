# Async Patterns Reference

Async client usage patterns for the Azure AI Agents SDK.

## Table of Contents

- [Basic Async Setup](#basic-async-setup)
- [Context Manager Pattern](#context-manager-pattern)
- [Full Async Workflow](#full-async-workflow)
- [Async File Operations](#async-file-operations)
- [Async Streaming](#async-streaming)
- [Async with Functions](#async-with-functions)
- [Concurrent Operations](#concurrent-operations)
- [Error Handling](#error-handling)

---

## Basic Async Setup

```python
import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.aio import AgentsClient

async def main():
    credential = DefaultAzureCredential()
    client = AgentsClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=credential,
    )
    
    try:
        agent = await client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="async-agent",
            instructions="You are helpful.",
        )
        # ... work with agent
    finally:
        await client.close()
        await credential.close()

asyncio.run(main())
```

---

## Context Manager Pattern

**Recommended**: Use async context managers for automatic cleanup.

```python
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.aio import AgentsClient

async def main():
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=credential,
        ) as client:
            agent = await client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="async-agent",
                instructions="You are helpful.",
            )
            
            thread = await client.threads.create()
            await client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Hello!",
            )
            
            run = await client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id,
            )
            
            if run.status == "completed":
                messages = client.messages.list(thread_id=thread.id)
                async for msg in messages:
                    if msg.role == "assistant":
                        print(msg.content[0].text.value)
            
            await client.delete_agent(agent.id)

asyncio.run(main())
```

---

## Full Async Workflow

Complete workflow with tools and file operations.

```python
import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents import CodeInterpreterTool, FileSearchTool

async def main():
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=credential,
        ) as client:
            # Upload file
            file = await client.files.upload_and_poll(
                file_path="data.csv",
                purpose="assistants",
            )
            
            # Create vector store
            vector_store = await client.vector_stores.create_and_poll(
                file_ids=[file.id],
                name="async-store",
            )
            
            # Create agent with tools
            agent = await client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="multi-tool-agent",
                instructions="You can analyze data and search files.",
                tools=[CodeInterpreterTool(), FileSearchTool()],
                tool_resources={
                    "code_interpreter": {"file_ids": [file.id]},
                    "file_search": {"vector_store_ids": [vector_store.id]},
                },
            )
            
            # Create thread and message
            thread = await client.threads.create()
            await client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Analyze the data in the file.",
            )
            
            # Process run
            run = await client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id,
            )
            
            # Get response
            if run.status == "completed":
                messages = client.messages.list(thread_id=thread.id)
                async for msg in messages:
                    if msg.role == "assistant":
                        print(msg.content[0].text.value)
            
            # Cleanup
            await client.delete_agent(agent.id)
            await client.vector_stores.delete(vector_store.id)
            await client.files.delete(file.id)

asyncio.run(main())
```

---

## Async File Operations

```python
async def upload_files(client, file_paths):
    """Upload multiple files concurrently."""
    tasks = [
        client.files.upload_and_poll(file_path=path, purpose="assistants")
        for path in file_paths
    ]
    return await asyncio.gather(*tasks)

async def main():
    async with AgentsClient(...) as client:
        # Upload files concurrently
        files = await upload_files(client, ["doc1.pdf", "doc2.pdf", "doc3.pdf"])
        file_ids = [f.id for f in files]
        
        # Create vector store with all files
        vector_store = await client.vector_stores.create_and_poll(
            file_ids=file_ids,
            name="multi-file-store",
        )
```

---

## Async Streaming

```python
from azure.ai.agents import AsyncAgentEventHandler

class AsyncHandler(AsyncAgentEventHandler):
    def __init__(self):
        super().__init__()
        self.text = ""
    
    async def on_message_delta(self, delta):
        if delta.text:
            self.text += delta.text.value
            print(delta.text.value, end="", flush=True)
    
    async def on_thread_run(self, run):
        if run.status == "completed":
            print("\n[Completed]")
    
    async def on_error(self, data):
        print(f"\n[Error: {data}]")

async def main():
    async with AgentsClient(...) as client:
        agent = await client.create_agent(...)
        thread = await client.threads.create()
        await client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Tell me a story.",
        )
        
        handler = AsyncHandler()
        async with client.runs.stream(
            thread_id=thread.id,
            agent_id=agent.id,
            event_handler=handler,
        ) as stream:
            await stream.until_done()
        
        print(f"Full text: {handler.text}")
```

### Async Iteration

```python
async with client.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
) as stream:
    async for event_type, event_data, _ in stream:
        if event_type == "thread.message.delta":
            if event_data.delta.content:
                for part in event_data.delta.content:
                    if part.type == "text" and part.text:
                        print(part.text.value, end="", flush=True)
```

---

## Async with Functions

```python
from azure.ai.agents import FunctionTool, ToolSet

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72F, sunny"

async def main():
    functions = FunctionTool(functions=[get_weather])
    toolset = ToolSet()
    toolset.add(functions)
    
    async with AgentsClient(...) as client:
        agent = await client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            toolset=toolset,
        )
        
        thread = await client.threads.create()
        await client.messages.create(
            thread_id=thread.id,
            role="user",
            content="What's the weather in Seattle?",
        )
        
        # Process with toolset - auto handles function calls
        run = await client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
            toolset=toolset,
        )
```

---

## Concurrent Operations

### Parallel Agent Conversations

```python
async def run_conversation(client, agent_id, user_message):
    """Run a single conversation."""
    thread = await client.threads.create()
    await client.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message,
    )
    run = await client.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent_id,
    )
    
    if run.status == "completed":
        messages = client.messages.list(thread_id=thread.id)
        async for msg in messages:
            if msg.role == "assistant":
                return msg.content[0].text.value
    return None

async def main():
    async with AgentsClient(...) as client:
        agent = await client.create_agent(...)
        
        # Run multiple conversations concurrently
        questions = [
            "What is Python?",
            "What is JavaScript?",
            "What is Rust?",
        ]
        
        tasks = [
            run_conversation(client, agent.id, q)
            for q in questions
        ]
        results = await asyncio.gather(*tasks)
        
        for q, r in zip(questions, results):
            print(f"Q: {q}\nA: {r}\n")
```

### Semaphore for Rate Limiting

```python
async def rate_limited_run(semaphore, client, agent_id, message):
    async with semaphore:
        return await run_conversation(client, agent_id, message)

async def main():
    # Limit to 5 concurrent requests
    semaphore = asyncio.Semaphore(5)
    
    async with AgentsClient(...) as client:
        agent = await client.create_agent(...)
        
        tasks = [
            rate_limited_run(semaphore, client, agent.id, msg)
            for msg in messages
        ]
        results = await asyncio.gather(*tasks)
```

---

## Error Handling

```python
from azure.core.exceptions import HttpResponseError

async def safe_create_agent(client, **kwargs):
    """Create agent with error handling."""
    try:
        return await client.create_agent(**kwargs)
    except HttpResponseError as e:
        print(f"Failed to create agent: {e.message}")
        raise

async def safe_run(client, thread_id, agent_id, **kwargs):
    """Run with timeout and error handling."""
    try:
        run = await asyncio.wait_for(
            client.runs.create_and_process(
                thread_id=thread_id,
                agent_id=agent_id,
                **kwargs,
            ),
            timeout=60.0,  # 60 second timeout
        )
        
        if run.status == "failed":
            print(f"Run failed: {run.last_error}")
            return None
        return run
        
    except asyncio.TimeoutError:
        print("Run timed out")
        return None
    except HttpResponseError as e:
        print(f"Run error: {e.message}")
        return None

async def main():
    async with AgentsClient(...) as client:
        try:
            agent = await safe_create_agent(
                client,
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="safe-agent",
            )
            
            thread = await client.threads.create()
            await client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Hello!",
            )
            
            run = await safe_run(client, thread.id, agent.id)
            if run:
                # Process successful run
                pass
                
        finally:
            # Always cleanup
            if agent:
                await client.delete_agent(agent.id)
```

---

## Complete Example

```python
import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents import (
    AsyncAgentEventHandler,
    CodeInterpreterTool,
    FunctionTool,
    ToolSet,
)

def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

class StreamHandler(AsyncAgentEventHandler):
    async def on_message_delta(self, delta):
        if delta.text:
            print(delta.text.value, end="", flush=True)

async def main():
    functions = FunctionTool(functions=[calculate])
    toolset = ToolSet()
    toolset.add(functions)
    
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=credential,
        ) as client:
            # Create agent
            agent = await client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="async-calculator",
                instructions="You help with calculations.",
                tools=[CodeInterpreterTool()],
                toolset=toolset,
            )
            
            # Create thread
            thread = await client.threads.create()
            await client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Calculate 25 * 17 + 42",
            )
            
            # Stream response
            print("Assistant: ", end="")
            async with client.runs.stream(
                thread_id=thread.id,
                agent_id=agent.id,
                toolset=toolset,
                event_handler=StreamHandler(),
            ) as stream:
                await stream.until_done()
            print()
            
            # Cleanup
            await client.delete_agent(agent.id)

if __name__ == "__main__":
    asyncio.run(main())
```
