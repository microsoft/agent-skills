# Azure AI Projects SDK Acceptance Criteria (TypeScript)

**SDK**: `@azure/ai-projects`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/ai/ai-projects
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Client Import
```typescript
import { AIProjectClient } from "@azure/ai-projects";
import { DefaultAzureCredential } from "@azure/identity";
```

### 1.2 ✅ CORRECT: Tool Utility Import
```typescript
import { AIProjectClient, ToolUtility } from "@azure/ai-projects";
```

### 1.3 ✅ CORRECT: Type Imports
```typescript
import type {
  Agent,
  AgentThread,
  ThreadMessage,
  ThreadRun,
} from "@azure/ai-projects";
```

### 1.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```typescript
// WRONG - AIProjectClient is in @azure/ai-projects
import { AIProjectClient } from "@azure/ai-projects/models";

// WRONG - using separate agents client package directly when projects is preferred
import { AgentsClient } from "@azure/ai-agents";
// Should use: const agents = projectClient.agents;
```

#### ❌ INCORRECT: Non-existent imports
```typescript
// WRONG - these don't exist in JS SDK
import { SystemMessage, UserMessage } from "@azure/ai-projects";
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Basic Client Creation
```typescript
import { AIProjectClient } from "@azure/ai-projects";
import { DefaultAzureCredential } from "@azure/identity";

const projectEndpoint = process.env.AZURE_AI_PROJECT_ENDPOINT!;
const client = new AIProjectClient(projectEndpoint, new DefaultAzureCredential());
```

### 2.2 ✅ CORRECT: Getting OpenAI Client
```typescript
import { AIProjectClient } from "@azure/ai-projects";
import { DefaultAzureCredential } from "@azure/identity";

const projectEndpoint = process.env.AZURE_AI_PROJECT_ENDPOINT!;
const project = new AIProjectClient(projectEndpoint, new DefaultAzureCredential());

const openAIClient = await project.getOpenAIClient();

// Use for responses/chat completions
const response = await openAIClient.responses.create({
  model: "gpt-4o",
  input: "What is the capital of France?",
});

console.log(response.output_text);
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing 'new' keyword
```typescript
// WRONG - AIProjectClient is a class
const client = AIProjectClient(endpoint, credential);
```

#### ❌ INCORRECT: Wrong parameter name
```typescript
// WRONG - should use projectEndpoint, not endpoint
const client = new AIProjectClient({
  endpoint: "https://...",
  credential: new DefaultAzureCredential(),
});
```

---

## 3. Agent Operations via Projects Client

### 3.1 ✅ CORRECT: Create Versioned Agent
```typescript
const deploymentName = process.env.MODEL_DEPLOYMENT_NAME || "gpt-4o";

const agent = await project.agents.createVersion("my-agent-basic", {
  kind: "prompt",
  model: deploymentName,
  instructions: "You are a helpful assistant that answers general questions",
});

console.log(`Agent created (id: ${agent.id}, name: ${agent.name}, version: ${agent.version})`);
```

### 3.2 ✅ CORRECT: Agent with Conversation
```typescript
const openAIClient = await project.getOpenAIClient();

// Create agent
const agent = await project.agents.createVersion("conversation-agent", {
  kind: "prompt",
  model: deploymentName,
  instructions: "You are a helpful assistant",
});

// Create conversation
const conversation = await openAIClient.conversations.create({
  items: [
    { type: "message", role: "user", content: "Hello!" },
  ],
});

// Generate response using agent
const response = await openAIClient.responses.create(
  {
    conversation: conversation.id,
  },
  {
    body: { agent: { name: agent.name, type: "agent_reference" } },
  },
);

console.log(`Response: ${response.output_text}`);
```

### 3.3 ✅ CORRECT: Delete Agent Version
```typescript
await project.agents.deleteVersion(agent.name, agent.version);
console.log("Agent deleted");
```

---

## 4. Agent Tools

### 4.1 ✅ CORRECT: Code Interpreter Tool
```typescript
const openAIClient = await project.getOpenAIClient();

const response = await openAIClient.responses.create({
  model: deploymentName,
  input: "I need to solve the equation 3x + 11 = 14. Can you help me?",
  tools: [{ type: "code_interpreter", container: { type: "auto" } }],
});

console.log(`Response: ${response.output_text}`);
```

### 4.2 ✅ CORRECT: File Search Tool with Vector Store
```typescript
import * as fs from "fs";
import * as path from "path";

const openAIClient = await project.getOpenAIClient();

// Create vector store
const vectorStore = await openAIClient.vectorStores.create({
  name: "ProductInfoStore",
});

// Upload file to vector store
const fileStream = fs.createReadStream("./assets/product_info.txt");
const uploadedFile = await openAIClient.vectorStores.files.uploadAndPoll(
  vectorStore.id,
  fileStream,
);

// Create agent with file search
const agent = await project.agents.createVersion("FileSearchAgent", {
  kind: "prompt",
  model: deploymentName,
  instructions: "You can search through product information",
  tools: [
    {
      type: "file_search",
      vector_store_ids: [vectorStore.id],
    },
  ],
});
```

### 4.3 ✅ CORRECT: Web Search Tool
```typescript
const agent = await project.agents.createVersion("WebSearchAgent", {
  kind: "prompt",
  model: deploymentName,
  instructions: "You can search the web to find current information",
  tools: [
    {
      type: "web_search_preview",
      user_location: {
        type: "approximate",
        country: "US",
        city: "Seattle",
        region: "Washington",
      },
    },
  ],
});
```

### 4.4 ✅ CORRECT: Image Generation Tool
```typescript
const agent = await project.agents.createVersion("ImageGenAgent", {
  kind: "prompt",
  model: deploymentName,
  instructions: "Generate images based on user prompts",
  tools: [
    {
      type: "image_generation",
      quality: "low",
      size: "1024x1024",
    },
  ],
});
```

### 4.5 ✅ CORRECT: Computer Use Tool
```typescript
const agent = await project.agents.createVersion("ComputerUseAgent", {
  kind: "prompt",
  model: deploymentName,
  instructions: "You are a computer automation assistant",
  tools: [
    {
      type: "computer_use_preview",
      display_width: 1026,
      display_height: 769,
      environment: "windows",
    },
  ],
});
```

---

## 5. Responses and Conversations

### 5.1 ✅ CORRECT: Simple Response
```typescript
const openAIClient = await project.getOpenAIClient();

const response = await openAIClient.responses.create({
  model: deploymentName,
  input: "What is the capital of France?",
});

console.log(response.output_text);
```

### 5.2 ✅ CORRECT: Multi-turn Conversation
```typescript
const openAIClient = await project.getOpenAIClient();

// First message
const response = await openAIClient.responses.create({
  model: deploymentName,
  input: "What is the size of France in square miles?",
});

console.log(response.output_text);

// Follow-up with previous_response_id
const followUp = await openAIClient.responses.create({
  model: deploymentName,
  input: "And what is the capital city?",
  previous_response_id: response.id,
});

console.log(followUp.output_text);
```

### 5.3 ✅ CORRECT: Conversation with Agent Reference
```typescript
const openAIClient = await project.getOpenAIClient();

// Create conversation
const conversation = await openAIClient.conversations.create({
  items: [
    { type: "message", role: "user", content: "Tell me about Azure" },
  ],
});

// Generate response with agent reference
const response = await openAIClient.responses.create(
  {
    conversation: conversation.id,
  },
  {
    body: { agent: { name: agent.name, type: "agent_reference" } },
  },
);

// Add follow-up message
await openAIClient.conversations.items.create(conversation.id, {
  items: [
    { type: "message", role: "user", content: "What services does it offer?" },
  ],
});

// Generate second response
const followUpResponse = await openAIClient.responses.create(
  {
    conversation: conversation.id,
  },
  {
    body: { agent: { name: agent.name, type: "agent_reference" } },
  },
);
```

---

## 6. Function Calling

### 6.1 ✅ CORRECT: Function Tool with Agent
```typescript
const agent = await project.agents.createVersion("FunctionAgent", {
  kind: "prompt",
  model: deploymentName,
  instructions: "You can help users with weather information",
  tools: [
    {
      type: "function",
      name: "get_weather",
      description: "Get current weather for a location",
      parameters: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "The city and state or country",
          },
        },
        required: ["location"],
      },
    },
  ],
  tool_choice: "auto",
});
```

### 6.2 ✅ CORRECT: Handling Function Call Results
```typescript
const subscription = session.subscribe({
  onResponseFunctionCallArgumentsDone: async (event, context) => {
    if (event.name === "get_weather") {
      const args = JSON.parse(event.arguments);
      const weatherData = await getWeatherData(args.location);

      // Send function result back
      await session.addConversationItem({
        type: "function_call_output",
        callId: event.callId,
        output: JSON.stringify(weatherData),
      });

      // Request response generation
      await session.sendEvent({
        type: "response.create",
      });
    }
  },
});
```

---

## 7. Connections Operations

### 7.1 ✅ CORRECT: List Connections
```typescript
const connections = await project.connections.list();

for await (const connection of connections) {
  console.log(`Connection: ${connection.name} (${connection.type})`);
}
```

### 7.2 ✅ CORRECT: Get Connection by Name
```typescript
const connection = await project.connections.get("my-aoai-connection");
console.log(`Endpoint: ${connection.endpoint}`);
```

---

## 8. Deployments Operations

### 8.1 ✅ CORRECT: List Deployments
```typescript
const deployments = await project.deployments.list();

for await (const deployment of deployments) {
  console.log(`Model: ${deployment.name}`);
}
```

---

## 9. Datasets and Indexes Operations

### 9.1 ✅ CORRECT: List Datasets
```typescript
const datasets = await project.datasets.list();

for await (const dataset of datasets) {
  console.log(`Dataset: ${dataset.name}`);
}
```

### 9.2 ✅ CORRECT: List Indexes
```typescript
const indexes = await project.indexes.list();

for await (const index of indexes) {
  console.log(`Index: ${index.name}`);
}
```

---

## 10. Evaluation Operations

### 10.1 ✅ CORRECT: List Evaluators
```typescript
const evaluators = await project.evaluators.list();

for await (const evaluator of evaluators) {
  console.log(`Evaluator: ${evaluator.name}`);
}
```

---

## 11. Memory Stores

### 11.1 ✅ CORRECT: Create Memory Store
```typescript
const memoryStore = await project.memoryStores.create({
  name: "my-memory-store",
  description: "Store for agent conversations",
});
```

---

## 12. Error Handling

### 12.1 ✅ CORRECT: Try-Catch Pattern
```typescript
try {
  const agent = await project.agents.createVersion("my-agent", {
    kind: "prompt",
    model: deploymentName,
    instructions: "You are helpful",
  });
} catch (error) {
  if (error instanceof Error) {
    console.error(`Failed to create agent: ${error.message}`);
  }
  throw error;
}
```

---

## 13. Cleanup Patterns

### 13.1 ✅ CORRECT: Full Cleanup
```typescript
// Delete conversation
await openAIClient.conversations.delete(conversation.id);
console.log("Conversation deleted");

// Delete agent
await project.agents.deleteVersion(agent.name, agent.version);
console.log("Agent deleted");

// Delete vector store
await openAIClient.vectorStores.delete(vectorStore.id);
console.log("Vector store deleted");
```

---

## 14. Environment Variables

### 14.1 ✅ CORRECT: Required Environment Variables
```typescript
const projectEndpoint = process.env.AZURE_AI_PROJECT_ENDPOINT!;
const deploymentName = process.env.MODEL_DEPLOYMENT_NAME || "gpt-4o";
```

### 14.2 ❌ INCORRECT: Hardcoded Values
```typescript
// WRONG - endpoints and keys should be from environment
const client = new AIProjectClient(
  "https://my-project.services.ai.azure.com",
  new DefaultAzureCredential(),
);
```
