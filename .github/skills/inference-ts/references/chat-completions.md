# Chat Completions Reference

Chat completions, streaming, tool calling, and structured output using @azure-rest/ai-inference SDK.

## Overview

The Azure AI Inference REST client provides chat completions for Azure OpenAI and Azure AI model deployments. This reference covers:
- Basic and streaming chat completions
- Tool/function calling patterns
- JSON mode and structured output
- Vision (image) inputs

## Core Types

```typescript
import ModelClient, {
  isUnexpected,
  // Request types
  ChatCompletionsOutput,
  ChatRequestMessage,
  ChatRequestSystemMessage,
  ChatRequestUserMessage,
  ChatRequestAssistantMessage,
  ChatRequestToolMessage,
  // Tool types
  ChatCompletionsToolDefinition,
  ChatCompletionsFunctionToolDefinition,
  ChatCompletionsToolCall,
  // Response format
  ChatCompletionsResponseFormat,
  ChatCompletionsJsonSchemaResponseFormat
} from "@azure-rest/ai-inference";

import { createSseStream } from "@azure/core-sse";
```

## Client Initialization

```typescript
import ModelClient from "@azure-rest/ai-inference";
import { DefaultAzureCredential } from "@azure/identity";
import { AzureKeyCredential } from "@azure/core-auth";

// With DefaultAzureCredential (recommended)
const client = ModelClient(
  process.env.AZURE_INFERENCE_ENDPOINT!,
  new DefaultAzureCredential()
);

// With API key
const clientWithKey = ModelClient(
  process.env.AZURE_INFERENCE_ENDPOINT!,
  new AzureKeyCredential(process.env.AZURE_INFERENCE_CREDENTIAL!)
);
```

## Basic Chat Completion

```typescript
import ModelClient, { isUnexpected } from "@azure-rest/ai-inference";

const response = await client.path("/chat/completions").post({
  body: {
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: "What is TypeScript?" }
    ]
  }
});

if (isUnexpected(response)) {
  throw new Error(response.body.error.message);
}

const content = response.body.choices[0].message.content;
console.log(content);
```

## Request Parameters

```typescript
const response = await client.path("/chat/completions").post({
  body: {
    messages: [...],
    
    // Token limits
    max_tokens: 1000,           // Maximum tokens in response
    
    // Sampling parameters
    temperature: 0.7,           // 0-2, higher = more random
    top_p: 0.95,                // Nucleus sampling threshold
    
    // Repetition control
    frequency_penalty: 0,       // -2 to 2, penalize frequent tokens
    presence_penalty: 0,        // -2 to 2, penalize repeated topics
    
    // Output control
    n: 1,                       // Number of completions to generate
    stop: ["\n\n", "END"],      // Stop sequences
    
    // Reproducibility
    seed: 42,                   // For deterministic outputs
    
    // Model selection (for multi-model endpoints)
    model: "gpt-4o"             // Optional model override
  }
});
```

## Streaming

### Node.js Streaming Pattern

```typescript
import ModelClient from "@azure-rest/ai-inference";
import { createSseStream } from "@azure/core-sse";
import { IncomingMessage } from "node:http";

const response = await client
  .path("/chat/completions")
  .post({
    body: {
      messages: [{ role: "user", content: "Write a short poem about coding" }],
      stream: true,
      max_tokens: 500
    }
  })
  .asNodeStream();

if (response.status !== "200") {
  throw new Error(`Stream failed with status ${response.status}`);
}

const sses = createSseStream(response.body as IncomingMessage);

for await (const event of sses) {
  // Check for stream end
  if (event.data === "[DONE]") {
    console.log("\n--- Stream complete ---");
    break;
  }
  
  const chunk = JSON.parse(event.data);
  const delta = chunk.choices[0]?.delta;
  
  // Handle content
  if (delta?.content) {
    process.stdout.write(delta.content);
  }
  
  // Handle tool calls (in streaming)
  if (delta?.tool_calls) {
    for (const toolCall of delta.tool_calls) {
      console.log(`Tool call: ${toolCall.function?.name}`);
    }
  }
  
  // Check finish reason
  const finishReason = chunk.choices[0]?.finish_reason;
  if (finishReason) {
    console.log(`\nFinish reason: ${finishReason}`);
  }
}
```

### Streaming Chunk Structure

```typescript
interface StreamingChatCompletionChunk {
  id: string;
  object: "chat.completion.chunk";
  created: number;
  model: string;
  choices: Array<{
    index: number;
    delta: {
      role?: "assistant";
      content?: string;
      tool_calls?: Array<{
        index: number;
        id?: string;
        type?: "function";
        function?: {
          name?: string;
          arguments?: string;  // Partial JSON, accumulate across chunks
        };
      }>;
    };
    finish_reason: "stop" | "length" | "tool_calls" | "content_filter" | null;
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}
```

### Accumulating Streamed Content

```typescript
let fullContent = "";
let toolCalls: Map<number, { id: string; name: string; arguments: string }> = new Map();

for await (const event of sses) {
  if (event.data === "[DONE]") break;
  
  const chunk = JSON.parse(event.data);
  const delta = chunk.choices[0]?.delta;
  
  // Accumulate content
  if (delta?.content) {
    fullContent += delta.content;
  }
  
  // Accumulate tool calls (arguments come in chunks)
  if (delta?.tool_calls) {
    for (const tc of delta.tool_calls) {
      const existing = toolCalls.get(tc.index);
      if (existing) {
        existing.arguments += tc.function?.arguments || "";
      } else {
        toolCalls.set(tc.index, {
          id: tc.id || "",
          name: tc.function?.name || "",
          arguments: tc.function?.arguments || ""
        });
      }
    }
  }
}

console.log("Full content:", fullContent);
console.log("Tool calls:", Array.from(toolCalls.values()));
```

## Tool Calling (Function Calling)

### Define Tools

```typescript
const tools: ChatCompletionsToolDefinition[] = [
  {
    type: "function",
    function: {
      name: "get_weather",
      description: "Get current weather for a location",
      parameters: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "City name, e.g., 'San Francisco, CA'"
          },
          unit: {
            type: "string",
            enum: ["celsius", "fahrenheit"],
            description: "Temperature unit"
          }
        },
        required: ["location"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "search_database",
      description: "Search the product database",
      parameters: {
        type: "object",
        properties: {
          query: { type: "string", description: "Search query" },
          limit: { type: "number", description: "Max results (default 10)" },
          category: {
            type: "string",
            enum: ["electronics", "clothing", "books"]
          }
        },
        required: ["query"]
      }
    }
  }
];
```

### Request with Tools

```typescript
const response = await client.path("/chat/completions").post({
  body: {
    messages: [
      { role: "user", content: "What's the weather in Tokyo?" }
    ],
    tools,
    tool_choice: "auto"  // "auto" | "none" | { type: "function", function: { name: "..." } }
  }
});

if (isUnexpected(response)) {
  throw response.body.error;
}

const message = response.body.choices[0].message;

// Check if model wants to call tools
if (message.tool_calls && message.tool_calls.length > 0) {
  console.log("Tool calls requested:");
  for (const toolCall of message.tool_calls) {
    console.log(`  ${toolCall.function.name}(${toolCall.function.arguments})`);
  }
}
```

### Execute Tools and Continue

```typescript
// Tool implementations
function getWeather(location: string, unit: string = "celsius"): string {
  // Real implementation would call weather API
  return JSON.stringify({ location, temperature: 22, unit, condition: "sunny" });
}

function searchDatabase(query: string, limit: number = 10, category?: string): string {
  // Real implementation would query database
  return JSON.stringify({ results: [{ id: 1, name: "Product A" }], total: 1 });
}

// Process tool calls
const messages: ChatRequestMessage[] = [
  { role: "user", content: "What's the weather in Tokyo?" }
];

const response1 = await client.path("/chat/completions").post({
  body: { messages, tools, tool_choice: "auto" }
});

if (isUnexpected(response1)) throw response1.body.error;

const assistantMessage = response1.body.choices[0].message;

if (assistantMessage.tool_calls) {
  // Add assistant message with tool calls
  messages.push({
    role: "assistant",
    content: assistantMessage.content || "",
    tool_calls: assistantMessage.tool_calls
  });
  
  // Execute each tool and add results
  for (const toolCall of assistantMessage.tool_calls) {
    const args = JSON.parse(toolCall.function.arguments);
    let result: string;
    
    switch (toolCall.function.name) {
      case "get_weather":
        result = getWeather(args.location, args.unit);
        break;
      case "search_database":
        result = searchDatabase(args.query, args.limit, args.category);
        break;
      default:
        result = JSON.stringify({ error: "Unknown function" });
    }
    
    // Add tool result message
    messages.push({
      role: "tool",
      tool_call_id: toolCall.id,
      content: result
    });
  }
  
  // Get final response with tool results
  const response2 = await client.path("/chat/completions").post({
    body: { messages, tools }
  });
  
  if (isUnexpected(response2)) throw response2.body.error;
  
  console.log("Final response:", response2.body.choices[0].message.content);
}
```

### Parallel Tool Calls

```typescript
// Model may request multiple tools in parallel
const response = await client.path("/chat/completions").post({
  body: {
    messages: [
      { role: "user", content: "Get weather for Tokyo and New York" }
    ],
    tools,
    parallel_tool_calls: true  // Allow parallel calls (default true)
  }
});

// message.tool_calls may contain multiple calls
// Execute all in parallel:
const toolResults = await Promise.all(
  message.tool_calls!.map(async (tc) => {
    const args = JSON.parse(tc.function.arguments);
    const result = await executeToolAsync(tc.function.name, args);
    return {
      role: "tool" as const,
      tool_call_id: tc.id,
      content: result
    };
  })
);
```

## JSON Mode and Structured Output

### JSON Object Mode

```typescript
// Request JSON output (model decides structure)
const response = await client.path("/chat/completions").post({
  body: {
    messages: [
      { role: "system", content: "Return responses as JSON objects." },
      { role: "user", content: "List 3 programming languages with their main use case" }
    ],
    response_format: { type: "json_object" }
  }
});

const json = JSON.parse(response.body.choices[0].message.content!);
```

### Structured Output (JSON Schema)

```typescript
// Request output conforming to specific schema
const response = await client.path("/chat/completions").post({
  body: {
    messages: [
      { role: "user", content: "Extract person info: John Smith is a 35-year-old software engineer living in Seattle." }
    ],
    response_format: {
      type: "json_schema",
      json_schema: {
        name: "person_info",
        description: "Information about a person",
        schema: {
          type: "object",
          properties: {
            name: { type: "string", description: "Full name" },
            age: { type: "number", description: "Age in years" },
            occupation: { type: "string", description: "Job title" },
            location: { type: "string", description: "City of residence" }
          },
          required: ["name", "age", "occupation", "location"],
          additionalProperties: false
        },
        strict: true  // Enforce exact schema conformance
      }
    }
  }
});

interface PersonInfo {
  name: string;
  age: number;
  occupation: string;
  location: string;
}

const person: PersonInfo = JSON.parse(response.body.choices[0].message.content!);
console.log(`${person.name}, ${person.age}, ${person.occupation} in ${person.location}`);
```

### Complex Schema Example

```typescript
const orderSchema = {
  type: "json_schema" as const,
  json_schema: {
    name: "order_extraction",
    schema: {
      type: "object",
      properties: {
        order_id: { type: "string" },
        customer: {
          type: "object",
          properties: {
            name: { type: "string" },
            email: { type: "string" }
          },
          required: ["name"]
        },
        items: {
          type: "array",
          items: {
            type: "object",
            properties: {
              product: { type: "string" },
              quantity: { type: "number" },
              price: { type: "number" }
            },
            required: ["product", "quantity", "price"]
          }
        },
        total: { type: "number" },
        status: {
          type: "string",
          enum: ["pending", "shipped", "delivered", "cancelled"]
        }
      },
      required: ["order_id", "customer", "items", "total", "status"],
      additionalProperties: false
    },
    strict: true
  }
};
```

## Vision (Image Input)

### Image URL

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
    ],
    max_tokens: 300
  }
});
```

### Base64 Image

```typescript
import { readFileSync } from "node:fs";

function imageToDataUrl(path: string, mimeType: string): string {
  const buffer = readFileSync(path);
  return `data:${mimeType};base64,${buffer.toString("base64")}`;
}

const response = await client.path("/chat/completions").post({
  body: {
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image_url",
            image_url: {
              url: imageToDataUrl("./photo.png", "image/png")
            }
          },
          { type: "text", text: "Describe this image in detail" }
        ]
      }
    ]
  }
});
```

### Multiple Images

```typescript
const response = await client.path("/chat/completions").post({
  body: {
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image_url",
            image_url: { url: "https://example.com/image1.jpg" }
          },
          {
            type: "image_url",
            image_url: { url: "https://example.com/image2.jpg" }
          },
          { type: "text", text: "Compare these two images" }
        ]
      }
    ]
  }
});
```

## Error Handling

```typescript
import ModelClient, { isUnexpected } from "@azure-rest/ai-inference";

const response = await client.path("/chat/completions").post({
  body: { messages: [...] }
});

if (isUnexpected(response)) {
  const error = response.body.error;
  
  switch (response.status) {
    case "400":
      console.error("Bad request:", error.message);
      break;
    case "401":
      console.error("Authentication failed");
      break;
    case "403":
      console.error("Access denied");
      break;
    case "404":
      console.error("Model not found");
      break;
    case "429":
      console.error("Rate limited, retry after:", response.headers["retry-after"]);
      break;
    case "500":
      console.error("Server error");
      break;
    default:
      console.error(`Error ${response.status}:`, error.message);
  }
  
  throw new Error(error.message);
}
```

## Response Structure

```typescript
interface ChatCompletionsOutput {
  id: string;
  object: "chat.completion";
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: {
      role: "assistant";
      content: string | null;
      tool_calls?: Array<{
        id: string;
        type: "function";
        function: {
          name: string;
          arguments: string;
        };
      }>;
    };
    finish_reason: "stop" | "length" | "tool_calls" | "content_filter";
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}
```

## Best Practices

1. **Always use isUnexpected()** - Type guard ensures proper error handling
2. **Stream long responses** - Better UX for lengthy completions
3. **Set max_tokens** - Prevent runaway token usage and costs
4. **Handle tool calls in a loop** - Models may request tools multiple times
5. **Use structured output** - `json_schema` ensures parseable responses
6. **Accumulate streaming content** - Don't process partial chunks
7. **Check finish_reason** - Handle "length" (truncated) and "content_filter" cases
8. **Retry on 429** - Implement exponential backoff for rate limits

## See Also

- [embeddings.md](./embeddings.md) - Text and image embeddings
