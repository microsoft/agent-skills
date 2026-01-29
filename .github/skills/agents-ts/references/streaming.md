# @azure/ai-agents - Streaming Response Patterns

Reference documentation for streaming responses in the Azure AI Agents TypeScript SDK.

**Source**: [Azure SDK for JS - ai-agents](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/ai/ai-agents)

---

## Installation

```bash
npm install @azure/ai-agents @azure/identity
```

---

## Core Streaming Types

```typescript
import {
  AgentsClient,
  // Stream event enums
  RunStreamEvent,
  MessageStreamEvent,
  ErrorEvent,
  DoneEvent,
  // Data types
  ThreadRun,
  MessageDeltaChunk,
  MessageDeltaTextContent,
  RunStepDeltaChunk,
  AgentThread,
  ThreadMessage,
  RunStep,
} from "@azure/ai-agents";
```

---

## Basic Streaming Example

```typescript
import {
  AgentsClient,
  RunStreamEvent,
  MessageStreamEvent,
  ErrorEvent,
  DoneEvent,
  type ThreadRun,
  type MessageDeltaChunk,
  type MessageDeltaTextContent,
} from "@azure/ai-agents";
import { DefaultAzureCredential } from "@azure/identity";

const client = new AgentsClient(
  process.env["PROJECT_ENDPOINT"]!,
  new DefaultAzureCredential()
);

// Create agent and thread
const agent = await client.createAgent("gpt-4o", {
  name: "streaming-agent",
  instructions: "You are a helpful assistant.",
});
const thread = await client.threads.create();
await client.messages.create(thread.id, "user", "Tell me a joke");

// Start streaming run
const stream = await client.runs.create(thread.id, agent.id).stream();

// Process stream events
for await (const event of stream) {
  switch (event.event) {
    case RunStreamEvent.ThreadRunCreated:
      console.log(`Run started: ${(event.data as ThreadRun).status}`);
      break;

    case MessageStreamEvent.ThreadMessageDelta:
      const delta = event.data as MessageDeltaChunk;
      delta.delta.content?.forEach((part) => {
        if (part.type === "text") {
          const text = (part as MessageDeltaTextContent).text?.value || "";
          process.stdout.write(text);
        }
      });
      break;

    case RunStreamEvent.ThreadRunCompleted:
      console.log("\nRun completed");
      break;

    case ErrorEvent.Error:
      console.error("Error:", event.data);
      break;

    case DoneEvent.Done:
      console.log("Stream finished");
      break;
  }
}
```

---

## Stream Event Types

### Run Events (`RunStreamEvent`)

| Event | Description | Data Type |
|-------|-------------|-----------|
| `ThreadRunCreated` | Run was created | `ThreadRun` |
| `ThreadRunQueued` | Run is queued | `ThreadRun` |
| `ThreadRunInProgress` | Run started processing | `ThreadRun` |
| `ThreadRunRequiresAction` | Run needs tool outputs | `ThreadRun` |
| `ThreadRunCompleted` | Run finished successfully | `ThreadRun` |
| `ThreadRunIncomplete` | Run ended incomplete | `ThreadRun` |
| `ThreadRunFailed` | Run failed | `ThreadRun` |
| `ThreadRunCancelling` | Run is being cancelled | `ThreadRun` |
| `ThreadRunCancelled` | Run was cancelled | `ThreadRun` |
| `ThreadRunExpired` | Run expired | `ThreadRun` |

### Message Events (`MessageStreamEvent`)

| Event | Description | Data Type |
|-------|-------------|-----------|
| `ThreadMessageCreated` | Message was created | `ThreadMessage` |
| `ThreadMessageInProgress` | Message is being generated | `ThreadMessage` |
| `ThreadMessageDelta` | Message content chunk | `MessageDeltaChunk` |
| `ThreadMessageCompleted` | Message finished | `ThreadMessage` |
| `ThreadMessageIncomplete` | Message ended incomplete | `ThreadMessage` |

### Run Step Events (`RunStepStreamEvent`)

| Event | Description | Data Type |
|-------|-------------|-----------|
| `ThreadRunStepCreated` | Step was created | `RunStep` |
| `ThreadRunStepInProgress` | Step started processing | `RunStep` |
| `ThreadRunStepDelta` | Step progress chunk | `RunStepDeltaChunk` |
| `ThreadRunStepCompleted` | Step finished | `RunStep` |
| `ThreadRunStepFailed` | Step failed | `RunStep` |
| `ThreadRunStepCancelled` | Step was cancelled | `RunStep` |
| `ThreadRunStepExpired` | Step expired | `RunStep` |

### Other Events

| Event | Description | Data Type |
|-------|-------------|-----------|
| `ErrorEvent.Error` | An error occurred | `string` |
| `DoneEvent.Done` | Stream completed | `string` |

---

## Processing Delta Events

```typescript
import {
  MessageDeltaChunk,
  MessageDeltaTextContent,
  MessageDeltaImageFileContent,
} from "@azure/ai-agents";

for await (const event of stream) {
  if (event.event === MessageStreamEvent.ThreadMessageDelta) {
    const delta = event.data as MessageDeltaChunk;

    // Access message metadata
    console.log(`Message ID: ${delta.id}`);

    // Process content parts
    delta.delta.content?.forEach((part) => {
      switch (part.type) {
        case "text":
          const textPart = part as MessageDeltaTextContent;
          const text = textPart.text?.value || "";
          // Handle annotations (citations, file paths)
          textPart.text?.annotations?.forEach((annotation) => {
            console.log("Annotation:", annotation);
          });
          process.stdout.write(text);
          break;

        case "image_file":
          const imagePart = part as MessageDeltaImageFileContent;
          console.log("Image file:", imagePart.imageFile?.fileId);
          break;
      }
    });
  }
}
```

---

## Streaming with Function Tools

Handle tool calls during streaming:

```typescript
import {
  RunStreamEvent,
  MessageStreamEvent,
  ToolOutput,
  isOutputOfType,
  SubmitToolOutputsAction,
} from "@azure/ai-agents";

const stream = await client.runs.create(thread.id, agent.id).stream();

for await (const event of stream) {
  switch (event.event) {
    case RunStreamEvent.ThreadRunRequiresAction:
      const run = event.data as ThreadRun;
      
      if (run.requiredAction && 
          isOutputOfType<SubmitToolOutputsAction>(run.requiredAction, "submit_tool_outputs")) {
        
        const toolCalls = run.requiredAction.submitToolOutputs.toolCalls;
        const toolOutputs: ToolOutput[] = [];

        for (const toolCall of toolCalls) {
          if (toolCall.type === "function") {
            const args = JSON.parse(toolCall.function.arguments);
            const result = await executeFunction(toolCall.function.name, args);
            toolOutputs.push({
              toolCallId: toolCall.id,
              output: JSON.stringify(result),
            });
          }
        }

        // Submit outputs and continue streaming
        const newStream = await client.runs
          .submitToolOutputs(thread.id, run.id, toolOutputs)
          .stream();
        
        // Process the new stream
        for await (const newEvent of newStream) {
          // Handle events from continued stream
        }
      }
      break;

    case MessageStreamEvent.ThreadMessageDelta:
      // Handle message deltas
      break;
  }
}
```

---

## Streaming with Code Interpreter

```typescript
import { RunStepStreamEvent, RunStepDeltaChunk } from "@azure/ai-agents";

for await (const event of stream) {
  switch (event.event) {
    case RunStepStreamEvent.ThreadRunStepDelta:
      const stepDelta = event.data as RunStepDeltaChunk;
      
      // Check for code interpreter output
      if (stepDelta.delta.stepDetails?.type === "tool_calls") {
        const toolCalls = stepDelta.delta.stepDetails.toolCalls;
        toolCalls?.forEach((toolCall) => {
          if (toolCall.type === "code_interpreter") {
            // Stream code input
            if (toolCall.codeInterpreter?.input) {
              console.log("Code:", toolCall.codeInterpreter.input);
            }
            // Stream code outputs
            toolCall.codeInterpreter?.outputs?.forEach((output) => {
              if (output.type === "logs") {
                console.log("Output:", output.logs);
              } else if (output.type === "image") {
                console.log("Image generated:", output.image?.fileId);
              }
            });
          }
        });
      }
      break;
  }
}
```

---

## Error Handling in Streams

```typescript
try {
  const stream = await client.runs.create(thread.id, agent.id).stream();

  for await (const event of stream) {
    switch (event.event) {
      case ErrorEvent.Error:
        console.error("Stream error:", event.data);
        break;

      case RunStreamEvent.ThreadRunFailed:
        const failedRun = event.data as ThreadRun;
        console.error("Run failed:", failedRun.lastError);
        break;

      case RunStreamEvent.ThreadRunExpired:
        console.error("Run expired");
        break;

      // Handle other events...
    }
  }
} catch (error) {
  // Handle network errors, authentication errors, etc.
  console.error("Stream failed:", error);
}
```

---

## Complete Streaming Example

```typescript
import {
  AgentsClient,
  RunStreamEvent,
  MessageStreamEvent,
  RunStepStreamEvent,
  ErrorEvent,
  DoneEvent,
  type ThreadRun,
  type ThreadMessage,
  type MessageDeltaChunk,
  type MessageDeltaTextContent,
  type RunStep,
  type RunStepDeltaChunk,
} from "@azure/ai-agents";
import { DefaultAzureCredential } from "@azure/identity";

async function runWithStreaming() {
  const client = new AgentsClient(
    process.env["PROJECT_ENDPOINT"]!,
    new DefaultAzureCredential()
  );

  // Create agent with tools
  const agent = await client.createAgent("gpt-4o", {
    name: "streaming-demo",
    instructions: "You are a helpful assistant.",
  });

  const thread = await client.threads.create();
  await client.messages.create(thread.id, "user", "Tell me about TypeScript");

  const stream = await client.runs.create(thread.id, agent.id).stream();
  let fullResponse = "";

  for await (const event of stream) {
    switch (event.event) {
      // Run lifecycle events
      case RunStreamEvent.ThreadRunCreated:
        console.log("[Run Created]");
        break;

      case RunStreamEvent.ThreadRunInProgress:
        console.log("[Run In Progress]");
        break;

      case RunStreamEvent.ThreadRunCompleted:
        console.log("\n[Run Completed]");
        break;

      case RunStreamEvent.ThreadRunFailed:
        const failedRun = event.data as ThreadRun;
        console.error("[Run Failed]", failedRun.lastError);
        break;

      // Message events
      case MessageStreamEvent.ThreadMessageCreated:
        console.log("[Message Created]");
        break;

      case MessageStreamEvent.ThreadMessageDelta:
        const delta = event.data as MessageDeltaChunk;
        delta.delta.content?.forEach((part) => {
          if (part.type === "text") {
            const text = (part as MessageDeltaTextContent).text?.value || "";
            fullResponse += text;
            process.stdout.write(text);
          }
        });
        break;

      case MessageStreamEvent.ThreadMessageCompleted:
        const message = event.data as ThreadMessage;
        console.log(`\n[Message Completed: ${message.id}]`);
        break;

      // Run step events
      case RunStepStreamEvent.ThreadRunStepCreated:
        const step = event.data as RunStep;
        console.log(`[Step Created: ${step.type}]`);
        break;

      case RunStepStreamEvent.ThreadRunStepCompleted:
        console.log("[Step Completed]");
        break;

      // Terminal events
      case ErrorEvent.Error:
        console.error("[Error]", event.data);
        break;

      case DoneEvent.Done:
        console.log("[Stream Done]");
        break;
    }
  }

  // Cleanup
  await client.deleteAgent(agent.id);

  return fullResponse;
}

runWithStreaming().catch(console.error);
```

---

## Non-Streaming Alternative

For simpler use cases, use `createAndPoll`:

```typescript
// Polling approach (waits for completion)
const run = await client.runs.createAndPoll(thread.id, agent.id);

if (run.status === "completed") {
  const messages = await client.messages.list(thread.id);
  const lastMessage = messages.data[0];
  console.log(lastMessage.content);
}
```

---

## Best Practices

1. **Always handle errors** - Check for `ErrorEvent.Error` and `ThreadRunFailed`
2. **Process deltas incrementally** - Don't buffer entire response unless needed
3. **Handle tool calls properly** - Submit outputs and continue the stream
4. **Clean up resources** - Delete agents and threads when done
5. **Use timeouts** - Implement client-side timeouts for long-running streams
6. **Log events for debugging** - Event types help diagnose issues

---

## See Also

- [Tool Integration Patterns](./tools.md) - Using tools with streaming
- [Official Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/ai/ai-agents/samples)
