# Streaming Responses with Azure AI Inference

Advanced patterns for handling streaming chat completions efficiently.

## Basic Streaming

```python
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

response = client.complete(
    stream=True,
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="Explain quantum computing.")
    ]
)

for update in response:
    if update.choices:
        content = update.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
print()  # Final newline
```

## Async Streaming

```python
import asyncio
from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

async def stream_completion():
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )
    
    try:
        response = await client.complete(
            stream=True,
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content="Write a short story.")
            ]
        )
        
        async for update in response:
            if update.choices:
                content = update.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
    finally:
        await client.close()

asyncio.run(stream_completion())
```

## Collecting Full Response

```python
def stream_and_collect(client, messages: list) -> str:
    """Stream response while collecting full content."""
    full_content = []
    
    response = client.complete(
        stream=True,
        messages=messages
    )
    
    for update in response:
        if update.choices:
            content = update.choices[0].delta.content
            if content:
                full_content.append(content)
                print(content, end="", flush=True)
    
    print()
    return "".join(full_content)
```

## Streaming with Metadata

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class StreamResult:
    content: str
    model: str
    finish_reason: Optional[str]
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]

def stream_with_metadata(client, messages: list) -> StreamResult:
    """Stream response and capture metadata from final chunk."""
    chunks = []
    model = None
    finish_reason = None
    usage = None
    
    response = client.complete(
        stream=True,
        messages=messages
    )
    
    for update in response:
        if update.model:
            model = update.model
        
        if update.choices:
            choice = update.choices[0]
            if choice.delta.content:
                chunks.append(choice.delta.content)
                print(choice.delta.content, end="", flush=True)
            if choice.finish_reason:
                finish_reason = choice.finish_reason
        
        # Usage info appears in final chunk (if supported by model)
        if hasattr(update, 'usage') and update.usage:
            usage = update.usage
    
    print()
    
    return StreamResult(
        content="".join(chunks),
        model=model or "unknown",
        finish_reason=finish_reason,
        prompt_tokens=usage.prompt_tokens if usage else None,
        completion_tokens=usage.completion_tokens if usage else None
    )
```

## Streaming with Timeout

```python
import asyncio
from typing import AsyncIterator

async def stream_with_timeout(
    client,
    messages: list,
    chunk_timeout: float = 30.0,
    total_timeout: float = 300.0
) -> str:
    """Stream with per-chunk and total timeouts."""
    chunks = []
    
    async def process_stream():
        response = await client.complete(stream=True, messages=messages)
        async for update in response:
            if update.choices:
                content = update.choices[0].delta.content
                if content:
                    chunks.append(content)
                    yield content
    
    try:
        async with asyncio.timeout(total_timeout):
            last_chunk_time = asyncio.get_event_loop().time()
            
            async for content in process_stream():
                current_time = asyncio.get_event_loop().time()
                if current_time - last_chunk_time > chunk_timeout:
                    raise TimeoutError("Chunk timeout exceeded")
                last_chunk_time = current_time
                print(content, end="", flush=True)
    
    except asyncio.TimeoutError:
        print("\n[Timeout - partial response]")
    
    return "".join(chunks)
```

## Streaming to Server-Sent Events (SSE)

```python
from typing import Generator
import json

def stream_to_sse(client, messages: list) -> Generator[str, None, None]:
    """Convert streaming response to SSE format for web clients."""
    response = client.complete(
        stream=True,
        messages=messages
    )
    
    for update in response:
        if update.choices:
            choice = update.choices[0]
            
            # Build SSE event data
            event_data = {
                "content": choice.delta.content or "",
                "finish_reason": choice.finish_reason
            }
            
            yield f"data: {json.dumps(event_data)}\n\n"
            
            if choice.finish_reason:
                yield "data: [DONE]\n\n"
                break

# FastAPI example
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/chat/stream")
async def chat_stream(prompt: str):
    messages = [UserMessage(content=prompt)]
    return StreamingResponse(
        stream_to_sse(client, messages),
        media_type="text/event-stream"
    )
```

## Streaming with Tool Calls

```python
from azure.ai.inference.models import (
    ChatCompletionsToolDefinition, FunctionDefinition
)
import json

tools = [
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_weather",
            description="Get weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        )
    )
]

def stream_with_tools(client, messages: list, tools: list) -> dict:
    """Stream response that may include tool calls."""
    content_chunks = []
    tool_calls = {}
    
    response = client.complete(
        stream=True,
        messages=messages,
        tools=tools
    )
    
    for update in response:
        if not update.choices:
            continue
            
        choice = update.choices[0]
        delta = choice.delta
        
        # Collect content
        if delta.content:
            content_chunks.append(delta.content)
            print(delta.content, end="", flush=True)
        
        # Collect tool calls (streamed incrementally)
        if delta.tool_calls:
            for tc in delta.tool_calls:
                idx = tc.index
                if idx not in tool_calls:
                    tool_calls[idx] = {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": "", "arguments": ""}
                    }
                
                if tc.function:
                    if tc.function.name:
                        tool_calls[idx]["function"]["name"] = tc.function.name
                    if tc.function.arguments:
                        tool_calls[idx]["function"]["arguments"] += tc.function.arguments
    
    print()
    
    return {
        "content": "".join(content_chunks),
        "tool_calls": list(tool_calls.values()) if tool_calls else None
    }
```

## Parallel Streaming

```python
import asyncio
from typing import List

async def parallel_stream(
    client,
    prompts: List[str],
    system_prompt: str = "You are a helpful assistant."
) -> List[str]:
    """Stream multiple completions in parallel."""
    
    async def stream_one(prompt: str, index: int) -> str:
        chunks = []
        messages = [
            SystemMessage(content=system_prompt),
            UserMessage(content=prompt)
        ]
        
        response = await client.complete(stream=True, messages=messages)
        
        async for update in response:
            if update.choices:
                content = update.choices[0].delta.content
                if content:
                    chunks.append(content)
                    # Print with prefix to identify stream
                    print(f"[{index}] {content}", end="", flush=True)
        
        return "".join(chunks)
    
    tasks = [stream_one(prompt, i) for i, prompt in enumerate(prompts)]
    results = await asyncio.gather(*tasks)
    
    return results
```

## Error Handling in Streams

```python
from azure.core.exceptions import (
    HttpResponseError,
    ServiceRequestError,
    ClientAuthenticationError
)

def stream_with_error_handling(client, messages: list) -> str:
    """Stream with comprehensive error handling."""
    chunks = []
    
    try:
        response = client.complete(stream=True, messages=messages)
        
        for update in response:
            if update.choices:
                content = update.choices[0].delta.content
                if content:
                    chunks.append(content)
                    print(content, end="", flush=True)
    
    except ClientAuthenticationError as e:
        print(f"\n[Auth Error: {e.message}]")
        raise
    
    except HttpResponseError as e:
        print(f"\n[HTTP Error {e.status_code}: {e.message}]")
        # Return partial content if available
        if chunks:
            return "".join(chunks) + "\n[Response truncated due to error]"
        raise
    
    except ServiceRequestError as e:
        print(f"\n[Network Error: {e.message}]")
        raise
    
    except Exception as e:
        print(f"\n[Unexpected Error: {type(e).__name__}: {e}]")
        raise
    
    print()
    return "".join(chunks)
```

## Streaming Configuration Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `stream` | `bool` | Enable streaming (required: `True`) |
| `stream_options` | `dict` | Additional streaming config |

### Stream Options (Model Dependent)

```python
response = client.complete(
    stream=True,
    messages=messages,
    stream_options={
        "include_usage": True  # Include token usage in final chunk
    }
)
```

## Best Practices

1. **Always check for content** — `delta.content` may be `None` or empty string
2. **Use `flush=True`** — Ensures immediate output to terminal/client
3. **Handle partial responses** — Network issues may truncate streams
4. **Close async clients** — Use `async with` or explicit `await client.close()`
5. **Set timeouts** — Prevent hanging on slow/stalled streams
6. **Buffer for post-processing** — Collect chunks if you need the full response
7. **Use SSE for web** — Server-Sent Events are the standard for streaming to browsers
