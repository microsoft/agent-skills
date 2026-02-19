# Acceptance Criteria: copilot-sdk

## Client Creation (TypeScript)

### Correct
```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({ model: "gpt-4.1" });
const response = await session.sendAndWait({ prompt: "Hello" });
console.log(response?.data.content);
await client.stop();
```

### Incorrect
```typescript
// WRONG - Hardcoded API key
const client = new CopilotClient({ apiKey: "sk-abc123" });
```

## Client Creation (Python)

### Correct
```python
import asyncio
from copilot import CopilotClient

async def main():
    client = CopilotClient()
    await client.start()
    session = await client.create_session({"model": "gpt-4.1"})
    response = await session.send_and_wait({"prompt": "Hello"})
    print(response.data.content)
    await client.stop()

asyncio.run(main())
```

### Incorrect
```python
# WRONG - Wrong import path
import copilot_sdk
```

## Client Creation (Go)

### Correct
```go
import copilot "github.com/github/copilot-sdk/go"

client := copilot.NewClient(nil)
if err := client.Start(ctx); err != nil {
    log.Fatal(err)
}
defer client.Stop()

session, err := client.CreateSession(ctx, &copilot.SessionConfig{
    Model: "gpt-4.1",
})
```

### Incorrect
```go
// WRONG - Using panic instead of proper error handling
session, _ := client.CreateSession(ctx, config)
panic("failed")
```

## Streaming

### Correct
```typescript
const session = await client.createSession({
  model: "gpt-4.1",
  streaming: true,
});

session.on("assistant.message_delta", (event) => {
  process.stdout.write(event.data.deltaContent);
});

session.on("session.idle", () => {
  console.log("Stream complete");
});

await session.sendAndWait({ prompt: "Write a haiku" });
```

## Custom Tools (TypeScript)

### Correct
```typescript
import { CopilotClient, defineTool } from "@github/copilot-sdk";

const myTool = defineTool("tool_name", {
  description: "Tool description",
  parameters: {
    type: "object",
    properties: {
      param: { type: "string", description: "Parameter description" },
    },
    required: ["param"],
  },
  handler: async ({ param }) => {
    return { result: param };
  },
});

const session = await client.createSession({
  model: "gpt-4.1",
  tools: [myTool],
});
```

### Incorrect
```typescript
// WRONG - Using 'any' type for handler parameters
const myTool = defineTool("tool", {
  handler: async (params: any) => { return params; },
});
```

## Custom Tools (Python)

### Correct
```python
from copilot.tools import define_tool
from pydantic import BaseModel, Field

class MyParams(BaseModel):
    value: str = Field(description="Input value")

@define_tool(description="Process a value")
async def process_value(params: MyParams) -> dict:
    return {"result": params.value}
```

### Incorrect
```python
# WRONG - Using **kwargs instead of typed parameters
@define_tool(description="Bad tool")
def bad_tool(**kwargs):
    return kwargs
```

## Hooks — Pre Tool Use

### Correct
```typescript
const session = await client.createSession({
  model: "gpt-4.1",
  hooks: {
    onPreToolUse: async (input) => {
      if (["shell", "bash"].includes(input.toolName)) {
        return {
          permissionDecision: "deny",
          permissionDecisionReason: "Shell access not permitted",
        };
      }
      return { permissionDecision: "allow" };
    },
  },
});
```

## MCP Server Integration

### Correct
```typescript
const session = await client.createSession({
  model: "gpt-4.1",
  mcpServers: {
    github: {
      type: "http",
      url: "https://api.githubcopilot.com/mcp/",
      tools: ["*"],
    },
    filesystem: {
      type: "local",
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
      tools: ["*"],
    },
  },
});
```

## BYOK (Bring Your Own Key)

### Correct
```typescript
const session = await client.createSession({
  model: "gpt-5.2-codex",
  provider: {
    type: "openai",
    baseUrl: "https://my-resource.openai.azure.com/openai/v1/",
    wireApi: "responses",
    apiKey: process.env.AZURE_OPENAI_API_KEY,
  },
});
```

### Incorrect
```typescript
// WRONG - Hardcoded API key in source code
const session = await client.createSession({
  provider: {
    apiKey: "sk-abc123def456ghi789",
  },
});
```

## Session Persistence

### Correct
```typescript
// Create resumable session
const session = await client.createSession({
  sessionId: "project-alpha-task-1",
  model: "gpt-4.1",
});
await session.sendAndWait({ prompt: "Remember this context" });

// Resume later
const resumed = await client.resumeSession("project-alpha-task-1");
const response = await resumed.sendAndWait({ prompt: "What did I say?" });
```

## Custom Agents

### Correct
```typescript
const session = await client.createSession({
  model: "gpt-4.1",
  customAgents: [
    {
      name: "code-reviewer",
      displayName: "Code Reviewer",
      description: "Reviews code for bugs and best practices",
      prompt: "You are an expert code reviewer...",
    },
  ],
});
```
