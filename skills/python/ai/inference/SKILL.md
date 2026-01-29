---
name: azure-ai-inference-python
description: |
  Azure AI Inference SDK for Python. Use for chat completions, embeddings, and model inference with Azure AI Foundry endpoints.
  Triggers: "azure-ai-inference", "ChatCompletionsClient", "EmbeddingsClient", "model inference", "Foundry models".
---

# Azure AI Inference SDK for Python

Client library for Azure AI model inference with chat completions and embeddings.

## Installation

```bash
pip install azure-ai-inference

# With OpenTelemetry tracing
pip install azure-ai-inference[opentelemetry]
```

## Environment Variables

```bash
# Inference endpoint
AZURE_INFERENCE_ENDPOINT=https://<resource>.services.ai.azure.com/models
AZURE_INFERENCE_CREDENTIAL=<your-api-key>  # If using API key

# Optional: specific model deployment
AZURE_INFERENCE_MODEL=gpt-4o-mini
```

## Authentication

### API Key

```python
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
import os

client = ChatCompletionsClient(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_INFERENCE_CREDENTIAL"])
)
```

### Entra ID (Recommended)

```python
from azure.ai.inference import ChatCompletionsClient
from azure.identity import DefaultAzureCredential

client = ChatCompletionsClient(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

## Chat Completions

### Basic Completion

```python
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

response = client.complete(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="What is Azure AI?")
    ],
    model="gpt-4o-mini"  # Optional for single-model endpoints
)

print(response.choices[0].message.content)
```

### Streaming Completions

```python
response = client.complete(
    stream=True,
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="Write a poem about Azure.")
    ]
)

for update in response:
    if update.choices:
        print(update.choices[0].delta.content or "", end="")
```

### With Default Settings

```python
# Set defaults at client creation
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
    temperature=0.5,
    max_tokens=1000
)

# Defaults applied to all calls, can be overridden per-call
response = client.complete(
    messages=[UserMessage(content="Hello")],
    temperature=0.8  # Overrides default
)
```

## Embeddings

```python
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential

client = EmbeddingsClient(
    endpoint="https://<resource>.services.ai.azure.com/models",
    credential=AzureKeyCredential(os.environ["AZURE_INFERENCE_CREDENTIAL"])
)

response = client.embed(
    input=["Your text string goes here"],
    model="text-embedding-3-small"
)

embedding = response.data[0].embedding
print(f"Embedding dimensions: {len(embedding)}")
```

## Async Client

```python
import asyncio
from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

async def main():
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )
    
    response = await client.complete(
        messages=[
            SystemMessage(content="You are a helpful assistant."),
            UserMessage(content="What is Azure AI?")
        ]
    )
    
    print(response.choices[0].message.content)
    await client.close()

asyncio.run(main())
```

## Model Information

```python
# Get model info (Serverless API / Managed Compute only)
model_info = client.get_model_info()

print(f"Model name: {model_info.model_name}")
print(f"Model provider: {model_info.model_provider_name}")
print(f"Model type: {model_info.model_type}")
```

## Using load_client

```python
from azure.ai.inference import load_client
from azure.core.credentials import AzureKeyCredential

# Auto-detect client type based on endpoint
client = load_client(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

print(f"Created client of type: {type(client).__name__}")
```

## Tool Calling

```python
from azure.ai.inference.models import (
    SystemMessage, UserMessage, AssistantMessage, ToolMessage,
    ChatCompletionsToolDefinition, FunctionDefinition
)

tools = [
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_weather",
            description="Get current weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        )
    )
]

response = client.complete(
    messages=[UserMessage(content="What's the weather in Seattle?")],
    tools=tools
)

# Handle tool calls in response
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    # Execute tool and send result back
```

## Message Types

| Type | Description |
|------|-------------|
| `SystemMessage` | System instructions for the model |
| `UserMessage` | User input (text, images, audio) |
| `AssistantMessage` | Model responses |
| `ToolMessage` | Tool execution results |
| `DeveloperMessage` | Developer-level instructions |

## Client Types

| Client | Purpose |
|--------|---------|
| `ChatCompletionsClient` | Chat and text completions |
| `EmbeddingsClient` | Text and image embeddings |
| `load_client` | Auto-detect client from endpoint |

## Best Practices

1. **Use Entra ID** for production authentication
2. **Set defaults** at client creation for consistent behavior
3. **Handle streaming** for long responses to improve UX
4. **Close async clients** explicitly or use context managers
5. **Specify model** when endpoint serves multiple deployments
6. **Use load_client** when you don't know the endpoint type
7. **Cache model_info** — it's cached after first call

## Reference Files

| File | Contents |
|------|----------|
| [references/streaming.md](references/streaming.md) | Streaming responses, async iteration, SSE patterns, error handling |
| [references/tool-calling.md](references/tool-calling.md) | Function/tool calling patterns, tool registry, multi-turn conversations |
| [scripts/chat_completion.py](scripts/chat_completion.py) | CLI for chat completions, embeddings, and interactive mode |
