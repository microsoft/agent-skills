# Microsoft 365 Agents SDK Acceptance Criteria (TypeScript)

**SDK**: `@microsoft/agents-hosting`, `@microsoft/agents-hosting-express`, `@microsoft/agents-activity`, `@microsoft/agents-copilotstudio-client`
**Repository**: https://github.com/microsoft/Agents-for-js
**Purpose**: Skill testing acceptance criteria for validating generated TypeScript code correctness

---

## 1. Correct Import Patterns

### 1.1 CORRECT: AgentApplication hosting
```typescript
import { AgentApplication, TurnContext, TurnState } from "@microsoft/agents-hosting";
import { startServer } from "@microsoft/agents-hosting-express";
```

### 1.2 CORRECT: Activity types
```typescript
import { Activity, ActivityTypes } from "@microsoft/agents-activity";
```

### 1.3 CORRECT: Copilot Studio client
```typescript
import { CopilotStudioClient, CopilotStudioWebChat } from "@microsoft/agents-copilotstudio-client";
```

### 1.4 INCORRECT: Bot Framework imports
```typescript
// WRONG - Bot Framework SDK is not used with Microsoft 365 Agents SDK
import { ActivityHandler } from "botbuilder";
import { BotFrameworkAdapter } from "botbuilder";
```

---

## 2. Express Hosting

### 2.1 CORRECT: AgentApplication with startServer
```typescript
const agent = new AgentApplication<TurnState>();

agent.onMessage("hello", async (context: TurnContext) => {
  await context.sendActivity("Hello!");
});

startServer(agent);
```

### 2.2 INCORRECT: Manual Express routing
```typescript
// WRONG - prefer startServer from @microsoft/agents-hosting-express
const app = express();
app.post("/api/messages", handler);
```

---

## 3. Streaming Responses

### 3.1 CORRECT: streamingResponse usage
```typescript
agent.onMessage("poem", async (context: TurnContext) => {
  context.streamingResponse.setFeedbackLoop(true);
  context.streamingResponse.setGeneratedByAILabel(true);
  await context.streamingResponse.queueInformativeUpdate("starting...");

  const { fullStream } = streamText({
    model: azure(process.env.AZURE_OPENAI_DEPLOYMENT_NAME || "gpt-4o-mini"),
    prompt: "Write a poem.",
  });

  try {
    for await (const part of fullStream) {
      if (part.type === "text-delta" && part.text.length > 0) {
        await context.streamingResponse.queueTextChunk(part.text);
      }
      if (part.type === "error") {
        throw new Error(`Streaming error: ${part.error}`);
      }
    }
  } finally {
    await context.streamingResponse.endStream();
  }
});
```

### 3.2 INCORRECT: Missing endStream
```typescript
// WRONG - endStream should always be called
await context.streamingResponse.queueTextChunk("partial");
```

---

## 4. Invoke Activities

### 4.1 CORRECT: Invoke response pattern
```typescript
agent.onActivity("invoke", async (context: TurnContext) => {
  const invokeResponse = Activity.fromObject({
    type: ActivityTypes.InvokeResponse,
    value: { status: 200 },
  });

  await context.sendActivity(invokeResponse);
});
```

---

## 5. Copilot Studio Client

### 5.1 CORRECT: CopilotStudioClient with token provider
```typescript
const client = new CopilotStudioClient(settings, async () => {
  return process.env.COPILOT_BEARER_TOKEN!;
});

const conversation = await client.startConversationAsync();
const reply = await client.askQuestionAsync("Hello!", conversation.id);
```

### 5.2 CORRECT: WebChat integration
```typescript
const directLine = CopilotStudioWebChat.createConnection(client, {
  showTyping: true,
});

window.WebChat.renderWebChat({ directLine }, document.getElementById("webchat")!);
```

### 5.3 INCORRECT: DirectLine client usage
```typescript
// WRONG - DirectLineClient is not part of Microsoft 365 Agents SDK
const directLine = new DirectLineClient();
```

---

## 6. Environment Variables

### 6.1 CORRECT: Using process.env
```typescript
const deployment = process.env.AZURE_OPENAI_DEPLOYMENT_NAME || "gpt-4o-mini";
const envId = process.env.COPILOT_ENVIRONMENT_ID!;
```

### 6.2 INCORRECT: Hardcoded secrets
```typescript
// WRONG - do not hardcode secrets
const clientSecret = "super-secret";
```
