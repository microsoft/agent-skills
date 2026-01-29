# Function Calling Reference

Tool definitions and function call handling patterns for Azure AI Voice Live using the @azure/ai-voicelive TypeScript SDK.

## Overview

Voice Live supports function calling (tools) that allow the voice assistant to execute actions and retrieve information during a conversation. This reference covers tool definitions, handling function call events, and sending function results.

## Tool Definition Schema

Tools are defined using JSON Schema in the session configuration:

```typescript
interface FunctionTool {
  type: "function";
  name: string;
  description?: string;
  parameters?: {
    type: "object";
    properties: Record<string, {
      type: string;
      description?: string;
      enum?: string[];
    }>;
    required?: string[];
  };
}
```

## Session Configuration with Tools

```typescript
import { VoiceLiveClient } from "@azure/ai-voicelive";
import { DefaultAzureCredential } from "@azure/identity";

const client = new VoiceLiveClient(endpoint, new DefaultAzureCredential());
const session = await client.startSession("gpt-4o-mini-realtime-preview");

await session.updateSession({
  modalities: ["audio", "text"],
  instructions: "You are a helpful assistant with access to weather data.",
  voice: {
    type: "azure-standard",
    name: "en-US-AvaNeural",
  },
  turnDetection: {
    type: "server_vad",
    threshold: 0.5,
    silenceDurationMs: 500,
  },
  tools: [
    {
      type: "function",
      name: "get_weather",
      description: "Get the current weather for a location",
      parameters: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "City and state, e.g., San Francisco, CA",
          },
          unit: {
            type: "string",
            enum: ["celsius", "fahrenheit"],
            description: "Temperature unit",
          },
        },
        required: ["location"],
      },
    },
    {
      type: "function",
      name: "search_products",
      description: "Search for products in the catalog",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "Search query",
          },
          category: {
            type: "string",
            enum: ["electronics", "clothing", "home", "sports"],
          },
          max_results: {
            type: "integer",
            description: "Maximum number of results to return",
          },
        },
        required: ["query"],
      },
    },
  ],
  toolChoice: "auto",  // "auto", "none", "required", or { type: "function", name: "..." }
});
```

## Handling Function Calls

### Basic Pattern

```typescript
const subscription = session.subscribe({
  onResponseFunctionCallArgumentsDone: async (event, context) => {
    console.log(`Function called: ${event.name}`);
    console.log(`Call ID: ${event.callId}`);
    console.log(`Arguments: ${event.arguments}`);

    // Parse arguments
    const args = JSON.parse(event.arguments);

    // Execute function based on name
    let result: string;
    
    switch (event.name) {
      case "get_weather":
        result = await getWeather(args.location, args.unit ?? "celsius");
        break;
      case "search_products":
        result = await searchProducts(args.query, args.category, args.max_results);
        break;
      default:
        result = JSON.stringify({ error: `Unknown function: ${event.name}` });
    }

    // Send function result back
    await session.addConversationItem({
      type: "function_call_output",
      callId: event.callId,
      output: result,
    });

    // Trigger response generation
    await session.sendEvent({ type: "response.create" });
  },
});
```

### Complete Example with Multiple Tools

```typescript
import { VoiceLiveClient, VoiceLiveSession } from "@azure/ai-voicelive";
import { DefaultAzureCredential } from "@azure/identity";

// Function implementations
async function getWeather(location: string, unit: string): Promise<string> {
  // In production, call actual weather API
  const temp = unit === "celsius" ? "22°C" : "72°F";
  return JSON.stringify({
    location,
    temperature: temp,
    conditions: "Partly cloudy",
    humidity: "45%",
  });
}

async function searchProducts(
  query: string,
  category?: string,
  maxResults = 5
): Promise<string> {
  // In production, query product database
  const products = [
    { id: "1", name: `${query} - Premium`, price: 99.99 },
    { id: "2", name: `${query} - Standard`, price: 49.99 },
  ];
  return JSON.stringify({
    query,
    category: category ?? "all",
    results: products.slice(0, maxResults),
  });
}

async function bookAppointment(
  date: string,
  time: string,
  service: string
): Promise<string> {
  // In production, book in calendar system
  return JSON.stringify({
    success: true,
    confirmation: `APT-${Date.now()}`,
    date,
    time,
    service,
  });
}

// Function dispatcher
async function handleFunctionCall(
  name: string,
  args: Record<string, unknown>
): Promise<string> {
  switch (name) {
    case "get_weather":
      return getWeather(
        args.location as string,
        (args.unit as string) ?? "celsius"
      );
    case "search_products":
      return searchProducts(
        args.query as string,
        args.category as string | undefined,
        args.max_results as number | undefined
      );
    case "book_appointment":
      return bookAppointment(
        args.date as string,
        args.time as string,
        args.service as string
      );
    default:
      return JSON.stringify({ error: `Unknown function: ${name}` });
  }
}

// Main voice assistant
async function startAssistant() {
  const client = new VoiceLiveClient(endpoint, new DefaultAzureCredential());
  const session = await client.startSession("gpt-4o-mini-realtime-preview");

  await session.updateSession({
    modalities: ["audio", "text"],
    instructions: `You are a helpful assistant that can:
      - Get weather information
      - Search for products
      - Book appointments
      Always confirm details with the user before booking.`,
    tools: [
      {
        type: "function",
        name: "get_weather",
        description: "Get current weather",
        parameters: {
          type: "object",
          properties: {
            location: { type: "string", description: "City name" },
            unit: { type: "string", enum: ["celsius", "fahrenheit"] },
          },
          required: ["location"],
        },
      },
      {
        type: "function",
        name: "search_products",
        description: "Search product catalog",
        parameters: {
          type: "object",
          properties: {
            query: { type: "string" },
            category: { type: "string", enum: ["electronics", "clothing", "home"] },
            max_results: { type: "integer" },
          },
          required: ["query"],
        },
      },
      {
        type: "function",
        name: "book_appointment",
        description: "Book an appointment",
        parameters: {
          type: "object",
          properties: {
            date: { type: "string", description: "Date in YYYY-MM-DD format" },
            time: { type: "string", description: "Time in HH:MM format" },
            service: { type: "string", description: "Type of service" },
          },
          required: ["date", "time", "service"],
        },
      },
    ],
    toolChoice: "auto",
  });

  const subscription = session.subscribe({
    onResponseFunctionCallArgumentsDone: async (event, context) => {
      console.log(`Executing: ${event.name}`);
      
      try {
        const args = JSON.parse(event.arguments);
        const result = await handleFunctionCall(event.name, args);

        await session.addConversationItem({
          type: "function_call_output",
          callId: event.callId,
          output: result,
        });

        await session.sendEvent({ type: "response.create" });
      } catch (error) {
        // Send error as function output
        await session.addConversationItem({
          type: "function_call_output",
          callId: event.callId,
          output: JSON.stringify({ error: String(error) }),
        });
        await session.sendEvent({ type: "response.create" });
      }
    },

    onResponseTextDelta: async (event) => {
      process.stdout.write(event.delta);
    },

    onError: async (args) => {
      console.error("Session error:", args.error);
    },
  });

  return { session, subscription };
}
```

## Streaming Function Arguments

For long-running function calls, you can process arguments as they stream in:

```typescript
const pendingCalls = new Map<string, { name: string; arguments: string }>();

const subscription = session.subscribe({
  // Arguments arrive in chunks
  onResponseFunctionCallArgumentsDelta: async (event, context) => {
    const callId = event.callId;
    
    if (!pendingCalls.has(callId)) {
      pendingCalls.set(callId, { name: event.name ?? "", arguments: "" });
    }
    
    const pending = pendingCalls.get(callId)!;
    if (event.name) {
      pending.name = event.name;
    }
    if (event.delta) {
      pending.arguments += event.delta;
    }
  },

  // All arguments received
  onResponseFunctionCallArgumentsDone: async (event, context) => {
    const callId = event.callId;
    const pending = pendingCalls.get(callId);
    pendingCalls.delete(callId);

    if (!pending) {
      console.error("No pending call found for:", callId);
      return;
    }

    // Now process the complete function call
    const args = JSON.parse(pending.arguments || event.arguments);
    const result = await handleFunctionCall(pending.name || event.name, args);

    await session.addConversationItem({
      type: "function_call_output",
      callId,
      output: result,
    });

    await session.sendEvent({ type: "response.create" });
  },
});
```

## Parallel Function Calls

Voice Live may invoke multiple functions in parallel. Handle them all before triggering response:

```typescript
const pendingCalls = new Map<string, Promise<string>>();
let pendingCount = 0;

const subscription = session.subscribe({
  onResponseFunctionCallArgumentsDone: async (event, context) => {
    pendingCount++;
    
    // Start function execution (don't await)
    const resultPromise = handleFunctionCall(
      event.name,
      JSON.parse(event.arguments)
    );
    pendingCalls.set(event.callId, resultPromise);
  },

  onResponseDone: async (event, context) => {
    // Check if there are pending function calls
    if (pendingCalls.size === 0) return;

    // Wait for all functions to complete
    for (const [callId, promise] of pendingCalls) {
      const result = await promise;
      await session.addConversationItem({
        type: "function_call_output",
        callId,
        output: result,
      });
    }

    pendingCalls.clear();
    
    // Trigger response generation after all results sent
    await session.sendEvent({ type: "response.create" });
  },
});
```

## Error Handling

```typescript
const subscription = session.subscribe({
  onResponseFunctionCallArgumentsDone: async (event, context) => {
    try {
      const args = JSON.parse(event.arguments);
      const result = await handleFunctionCall(event.name, args);

      await session.addConversationItem({
        type: "function_call_output",
        callId: event.callId,
        output: result,
      });
    } catch (error) {
      // Send error message so assistant can respond appropriately
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      await session.addConversationItem({
        type: "function_call_output",
        callId: event.callId,
        output: JSON.stringify({
          error: true,
          message: `Function execution failed: ${errorMessage}`,
        }),
      });
    }

    await session.sendEvent({ type: "response.create" });
  },
});
```

## Tool Choice Options

Control how the model selects tools:

```typescript
// Auto - model decides when to use tools
await session.updateSession({ toolChoice: "auto" });

// None - disable tool usage
await session.updateSession({ toolChoice: "none" });

// Required - model must use a tool
await session.updateSession({ toolChoice: "required" });

// Force specific function
await session.updateSession({
  toolChoice: {
    type: "function",
    name: "get_weather",
  },
});
```

## Conversation Item Types

```typescript
// Add user message
await session.addConversationItem({
  type: "message",
  role: "user",
  content: [{ type: "text", text: "What's the weather in Seattle?" }],
});

// Add function call output
await session.addConversationItem({
  type: "function_call_output",
  callId: "call_abc123",
  output: JSON.stringify({ temperature: "72°F", conditions: "Sunny" }),
});

// Trigger response
await session.sendEvent({ type: "response.create" });
```

## Best Practices

1. **Return JSON from functions** - Structured data is easier for the model to interpret
2. **Include error information** - Return `{ error: true, message: "..." }` on failure
3. **Handle timeouts** - Set reasonable timeouts for external API calls
4. **Validate arguments** - Check required fields before executing functions
5. **Use descriptive names** - Function and parameter names help the model understand usage
6. **Provide examples in description** - E.g., "City and state, e.g., San Francisco, CA"
7. **Handle parallel calls** - Don't assume functions are called sequentially

## See Also

- [Audio Streaming Reference](./audio-streaming.md)
- [SKILL.md](../SKILL.md) - Main skill documentation
- [Azure Voice Live API Reference](https://learn.microsoft.com/javascript/api/@azure/ai-voicelive)
