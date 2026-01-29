---
name: agents-ts
description: Build AI agents using Azure AI Agents SDK for JavaScript (@azure/ai-agents). Use when creating agents with tools (Code Interpreter, File Search, Function Calling), managing threads and messages, or implementing streaming responses.
---

# Azure AI Agents SDK for TypeScript

Build AI agents hosted on Azure AI Foundry with tools, threads, and streaming.

## Installation

```bash
npm install @azure/ai-agents @azure/identity
```

## Environment Variables

```bash
AZURE_AI_AGENTS_ENDPOINT=https://<resource>.services.ai.azure.com
```

## Authentication

```typescript
import { AgentsClient } from "@azure/ai-agents";
import { DefaultAzureCredential } from "@azure/identity";

const client = new AgentsClient(
  process.env.AZURE_AI_AGENTS_ENDPOINT!,
  new DefaultAzureCredential()
);
```

## Core Workflow

### Create Agent

```typescript
const agent = await client.createAgent("gpt-4o", {
  name: "my-assistant",
  instructions: "You are a helpful assistant.",
  tools: [{ type: "code_interpreter" }]
});
```

### Create Thread and Run

```typescript
// Create thread
const thread = await client.createThread();

// Add message
await client.createMessage(thread.id, {
  role: "user",
  content: "What is 2 + 2?"
});

// Run agent
const run = await client.createRun(thread.id, agent.id);

// Wait for completion
let status = run.status;
while (status === "queued" || status === "in_progress") {
  await new Promise(r => setTimeout(r, 1000));
  const updatedRun = await client.getRun(thread.id, run.id);
  status = updatedRun.status;
}

// Get messages
const messages = await client.listMessages(thread.id);
for (const msg of messages.data) {
  if (msg.role === "assistant") {
    console.log(msg.content[0].text.value);
  }
}
```

### One-Shot: Create and Run Thread

```typescript
const run = await client.createAndRunThread({
  assistantId: agent.id,
  thread: {
    messages: [{ role: "user", content: "Hello!" }]
  }
});
```

## Agent Tools

### Code Interpreter

```typescript
const agent = await client.createAgent("gpt-4o", {
  name: "code-agent",
  instructions: "You can execute Python code.",
  tools: [{ type: "code_interpreter" }]
});
```

### File Search with Vector Store

```typescript
// Create vector store
const vectorStore = await client.createVectorStore({ name: "my-docs" });

// Upload file
const file = await client.uploadFileAndPoll(
  "./document.pdf",
  "assistants"
);

// Add file to vector store
await client.createVectorStoreFile(vectorStore.id, file.id);

// Create agent with file search
const agent = await client.createAgent("gpt-4o", {
  name: "search-agent",
  instructions: "Search documents to answer questions.",
  tools: [{ type: "file_search" }],
  tool_resources: {
    file_search: { vector_store_ids: [vectorStore.id] }
  }
});
```

### Function Calling

```typescript
const weatherTool = {
  type: "function" as const,
  function: {
    name: "get_weather",
    description: "Get current weather for a location",
    parameters: {
      type: "object",
      properties: {
        location: { type: "string", description: "City name" }
      },
      required: ["location"]
    }
  }
};

const agent = await client.createAgent("gpt-4o", {
  name: "weather-agent",
  tools: [weatherTool]
});

// Handle tool calls in run
const run = await client.createRun(thread.id, agent.id);

if (run.status === "requires_action") {
  const toolCalls = run.required_action.submit_tool_outputs.tool_calls;
  
  const toolOutputs = toolCalls.map(tc => ({
    tool_call_id: tc.id,
    output: JSON.stringify({ temperature: 72, condition: "sunny" })
  }));
  
  await client.submitToolOutputs(thread.id, run.id, toolOutputs);
}
```

## Streaming Responses

```typescript
const stream = await client.createRunStream(thread.id, agent.id);

for await (const event of stream) {
  if (event.event === "thread.message.delta") {
    const delta = event.data.delta;
    if (delta.content?.[0]?.type === "text") {
      process.stdout.write(delta.content[0].text.value);
    }
  }
  
  if (event.event === "thread.run.completed") {
    console.log("\n[Done]");
  }
}
```

## Cleanup

```typescript
// Delete agent when done
await client.deleteAgent(agent.id);

// Delete thread
await client.deleteThread(thread.id);

// Delete vector store
await client.deleteVectorStore(vectorStore.id);
```

## Key Types

```typescript
import {
  AgentsClient,
  Agent,
  AgentThread,
  ThreadMessage,
  ThreadRun,
  ToolDefinition,
  CodeInterpreterToolDefinition,
  FileSearchToolDefinition,
  FunctionToolDefinition,
  VectorStore
} from "@azure/ai-agents";
```

## Best Practices

1. **Always clean up** - Delete agents, threads, and vector stores when done
2. **Poll with backoff** - Use exponential backoff when polling run status
3. **Handle tool calls** - Check for `requires_action` status and submit tool outputs
4. **Use streaming** - For real-time responses, use `createRunStream`
5. **Scope vector stores** - Create dedicated vector stores per use case
