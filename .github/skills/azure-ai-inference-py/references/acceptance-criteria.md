# Azure AI Inference SDK Acceptance Criteria

**SDK**: `azure-ai-inference`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Imports

### 1.1 ✅ CORRECT: Client Imports
```python
from azure.ai.inference import ChatCompletionsClient, EmbeddingsClient
from azure.core.credentials import AzureKeyCredential
```

### 1.2 ✅ CORRECT: Model Imports
```python
from azure.ai.inference.models import SystemMessage, UserMessage
```

### 1.3 ✅ CORRECT: Async Client Imports
```python
from azure.ai.inference.aio import ChatCompletionsClient, EmbeddingsClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.4 ✅ CORRECT: Tool Calling Models
```python
from azure.ai.inference.models import (
    ChatCompletionsToolDefinition,
    FunctionDefinition,
    AssistantMessage,
    ToolMessage,
)
```

### 1.5 ❌ INCORRECT: Wrong import paths
```python
# WRONG - message models are in azure.ai.inference.models
from azure.ai.inference import SystemMessage, UserMessage

# WRONG - clients are not in models
from azure.ai.inference.models import ChatCompletionsClient

# WRONG - async clients must be imported from .aio
from azure.ai.inference import ChatCompletionsClientAsync
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: API Key Credential
```python
client = ChatCompletionsClient(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_INFERENCE_CREDENTIAL"]),
)
```

### 2.2 ✅ CORRECT: Entra ID Credential
```python
from azure.identity import DefaultAzureCredential

client = ChatCompletionsClient(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
```

### 2.3 ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - hardcoded secrets
client = ChatCompletionsClient(
    endpoint="https://example.services.ai.azure.com/models",
    credential=AzureKeyCredential("hardcoded-key"),
)
```

---

## 3. Chat Completions

### 3.1 ✅ CORRECT: Basic Completion
```python
response = client.complete(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="What is Azure AI?"),
    ],
    model=os.environ.get("AZURE_INFERENCE_MODEL"),
)

print(response.choices[0].message.content)
```

### 3.2 ✅ CORRECT: Tool Calling
```python
tools = [
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_weather",
            description="Get current weather for a location",
            parameters={
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"],
            },
        )
    )
]

response = client.complete(
    messages=[UserMessage(content="What's the weather in Seattle?")],
    tools=tools,
)
```

### 3.3 ❌ INCORRECT: Using OpenAI SDK instead of Azure SDK
```python
# WRONG - should use azure.ai.inference
from openai import OpenAI
```

---

## 4. Embeddings

### 4.1 ✅ CORRECT: Text Embeddings
```python
client = EmbeddingsClient(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_INFERENCE_CREDENTIAL"]),
)

response = client.embed(
    input=["first phrase", "second phrase"],
    model="text-embedding-3-small",
)

embedding = response.data[0].embedding
print(len(embedding))
```

### 4.2 ❌ INCORRECT: Wrong method name
```python
# WRONG - method is embed, not embeddings
response = client.embeddings(input=["text"])
```

---

## 5. Streaming

### 5.1 ✅ CORRECT: Streaming Chat Completions
```python
response = client.complete(
    stream=True,
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="Write a poem about Azure."),
    ],
)

for update in response:
    if update.choices and update.choices[0].delta:
        print(update.choices[0].delta.content or "", end="", flush=True)
```

### 5.2 ❌ INCORRECT: Treating non-streaming response as stream
```python
# WRONG - missing stream=True
non_stream_response = wrong_client.complete(messages=[UserMessage(content="Hello")])
for wrong_update in non_stream_response:  # WRONG - non-streaming response is not iterable
    print(wrong_update)
```

---

## 6. Async Variants

### 6.1 ✅ CORRECT: Async Client and Completion
```python
import asyncio
from azure.ai.inference.aio import ChatCompletionsClient
from azure.identity.aio import DefaultAzureCredential

async def main():
    client = ChatCompletionsClient(
        endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    try:
        response = await client.complete(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content="What is Azure AI?"),
            ],
        )
        print(response.choices[0].message.content)
    finally:
        await client.close()

asyncio.run(main())
```

### 6.2 ✅ CORRECT: Async Streaming
```python
async def stream_completion(client):
    response = await client.complete(
        stream=True,
        messages=[UserMessage(content="Stream this response")],
    )
    async for update in response:
        if update.choices:
            content = update.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
```

### 6.3 ❌ INCORRECT: Mixing sync credential with async client
```python
# WRONG - async client needs azure.identity.aio DefaultAzureCredential
from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatClient
from azure.identity import DefaultAzureCredential as SyncCredential  # WRONG - should use .aio

async_client = AsyncChatClient(
    endpoint=os.environ["WRONG_ENDPOINT"],
    credential=SyncCredential(),  # WRONG - sync credential with async client
)
```
