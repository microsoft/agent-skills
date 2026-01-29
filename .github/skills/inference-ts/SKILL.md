---
name: inference-ts
description: Azure AI Inference REST client for chat completions, embeddings, and image analysis (@azure-rest/ai-inference). Use when building chat applications, generating embeddings, or calling models with function tools.
---

# Azure AI Inference REST SDK for TypeScript

REST client for chat completions, embeddings, and model inference.

## Installation

```bash
npm install @azure-rest/ai-inference @azure/identity @azure/core-auth @azure/core-sse
```

## Environment Variables

```bash
AZURE_INFERENCE_ENDPOINT=https://<resource>.services.ai.azure.com/models
AZURE_INFERENCE_CREDENTIAL=<api-key>  # For API key auth
```

## Authentication

**Important**: This is a REST client. `ModelClient` is a **function**, not a class.

### DefaultAzureCredential

```typescript
import ModelClient from "@azure-rest/ai-inference";
import { DefaultAzureCredential } from "@azure/identity";

const client = ModelClient(
  process.env.AZURE_INFERENCE_ENDPOINT!,
  new DefaultAzureCredential()
);
```

### API Key

```typescript
import ModelClient from "@azure-rest/ai-inference";
import { AzureKeyCredential } from "@azure/core-auth";

const client = ModelClient(
  process.env.AZURE_INFERENCE_ENDPOINT!,
  new AzureKeyCredential(process.env.AZURE_INFERENCE_CREDENTIAL!)
);
```

## Chat Completions

### Basic Request

```typescript
import ModelClient, { isUnexpected } from "@azure-rest/ai-inference";

const response = await client.path("/chat/completions").post({
  body: {
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: "What is the capital of France?" }
    ],
    max_tokens: 128,
    temperature: 0.7
  }
});

if (isUnexpected(response)) {
  throw response.body.error;
}

console.log(response.body.choices[0].message.content);
```

### Streaming

```typescript
import ModelClient from "@azure-rest/ai-inference";
import { createSseStream } from "@azure/core-sse";
import { IncomingMessage } from "node:http";

const response = await client
  .path("/chat/completions")
  .post({
    body: {
      messages: [{ role: "user", content: "Tell me a story" }],
      stream: true,
      max_tokens: 500
    }
  })
  .asNodeStream();

if (response.status !== "200") {
  throw new Error("Stream failed");
}

const sses = createSseStream(response.body as IncomingMessage);

for await (const event of sses) {
  if (event.data === "[DONE]") break;
  
  const chunk = JSON.parse(event.data);
  const content = chunk.choices[0]?.delta?.content;
  if (content) {
    process.stdout.write(content);
  }
}
```

## Text Embeddings

```typescript
import ModelClient, { isUnexpected } from "@azure-rest/ai-inference";

const response = await client.path("/embeddings").post({
  body: {
    input: ["First sentence", "Second sentence", "Third sentence"],
    // Optional:
    // dimensions: 1024,
    // encoding_format: "float",
    // input_type: "query"
  }
});

if (isUnexpected(response)) {
  throw response.body.error;
}

for (const item of response.body.data) {
  console.log(`Embedding length: ${item.embedding.length}`);
}
```

## Image Embeddings

```typescript
import { readFileSync } from "node:fs";

function getImageDataUrl(path: string, format: string): string {
  const buffer = readFileSync(path);
  return `data:image/${format};base64,${buffer.toString("base64")}`;
}

const response = await client.path("/images/embeddings").post({
  body: {
    input: [{ image: getImageDataUrl("./image.png", "png") }]
  }
});

if (isUnexpected(response)) {
  throw response.body.error;
}
```

## Chat with Images (Vision)

```typescript
const response = await client.path("/chat/completions").post({
  body: {
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image_url",
            image_url: {
              url: "https://example.com/image.jpg",
              detail: "auto"  // "auto" | "low" | "high"
            }
          },
          { type: "text", text: "What's in this image?" }
        ]
      }
    ]
  }
});
```

## Function/Tool Calling

```typescript
const tools = [
  {
    type: "function" as const,
    function: {
      name: "get_weather",
      description: "Get current weather for a location",
      parameters: {
        type: "object",
        properties: {
          location: { type: "string", description: "City name" },
          unit: { type: "string", enum: ["celsius", "fahrenheit"] }
        },
        required: ["location"]
      }
    }
  }
];

const response = await client.path("/chat/completions").post({
  body: {
    messages: [{ role: "user", content: "What's the weather in Paris?" }],
    tools,
    tool_choice: "auto"
  }
});

if (isUnexpected(response)) {
  throw response.body.error;
}

const choice = response.body.choices[0];
if (choice.message.tool_calls) {
  for (const call of choice.message.tool_calls) {
    const args = JSON.parse(call.function.arguments);
    console.log(`Call ${call.function.name} with:`, args);
    // Execute function and continue conversation with tool message
  }
}
```

## JSON Mode / Structured Output

### JSON Object Mode

```typescript
const response = await client.path("/chat/completions").post({
  body: {
    messages: [{ role: "user", content: "Return a JSON with name and age" }],
    response_format: { type: "json_object" }
  }
});
```

### JSON Schema (Structured Output)

```typescript
const response = await client.path("/chat/completions").post({
  body: {
    messages: [{ role: "user", content: "Extract person info from: John is 30 years old" }],
    response_format: {
      type: "json_schema",
      json_schema: {
        name: "person_info",
        schema: {
          type: "object",
          properties: {
            name: { type: "string" },
            age: { type: "number" }
          },
          required: ["name", "age"]
        },
        strict: true
      }
    }
  }
});
```

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/chat/completions` | POST | Chat completions |
| `/embeddings` | POST | Text embeddings |
| `/images/embeddings` | POST | Image embeddings |
| `/info` | GET | Model information |

## Key Types

```typescript
import ModelClient, {
  isUnexpected,
  // Request types
  GetChatCompletionsBodyParam,
  GetEmbeddingsBodyParam,
  // Response types
  ChatCompletionsOutput,
  EmbeddingsResultOutput,
  // Message types
  ChatRequestMessage,
  ChatRequestSystemMessage,
  ChatRequestUserMessage,
  ChatRequestAssistantMessage,
  ChatRequestToolMessage
} from "@azure-rest/ai-inference";
```

## Error Handling

```typescript
import ModelClient, { isUnexpected } from "@azure-rest/ai-inference";

const response = await client.path("/chat/completions").post({ body: {...} });

// Type guard narrows response type
if (isUnexpected(response)) {
  // Error response
  console.error("Error:", response.body.error);
  throw new Error(response.body.error.message);
}

// Success response - TypeScript knows this is 200
console.log(response.body.choices[0].message.content);
```

## Best Practices

1. **Always use isUnexpected()** - Type guard for proper error handling
2. **Use streaming for long responses** - Better UX with `asNodeStream()` + `createSseStream()`
3. **Set max_tokens** - Prevent runaway token usage
4. **Handle tool calls** - Check for tool_calls in response and continue conversation
5. **Use structured output** - `json_schema` for predictable parsing
