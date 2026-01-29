# @azure/ai-agents - Tool Integration Patterns

Reference documentation for tool integration in the Azure AI Agents TypeScript SDK.

**Source**: [Azure SDK for JS - ai-agents](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/ai/ai-agents)

---

## Installation

```bash
npm install @azure/ai-agents @azure/identity
```

---

## Client Setup

```typescript
import { AgentsClient, ToolUtility, ToolSet } from "@azure/ai-agents";
import { DefaultAzureCredential } from "@azure/identity";

const client = new AgentsClient(
  process.env["PROJECT_ENDPOINT"]!,
  new DefaultAzureCredential()
);
```

---

## Function Tools

Define custom functions the agent can call. You provide definitions only—implementations run in your code.

```typescript
import {
  FunctionToolDefinition,
  ToolUtility,
  RequiredToolCall,
  ToolOutput,
  SubmitToolOutputsAction,
  isOutputOfType,
} from "@azure/ai-agents";

// Define function tools
const weatherTool = ToolUtility.createFunctionTool({
  name: "getWeather",
  description: "Gets the weather for a location.",
  parameters: {
    type: "object",
    properties: {
      location: { type: "string", description: "City and state, e.g. Seattle, WA" },
      unit: { type: "string", enum: ["c", "f"] },
    },
  },
});

const cityTool = ToolUtility.createFunctionTool({
  name: "getUserFavoriteCity",
  description: "Gets the user's favorite city.",
  parameters: {},
});

// Create agent with function tools
const agent = await client.createAgent("gpt-4o", {
  name: "weather-bot",
  instructions: "You are a weather bot. Use provided functions to answer questions.",
  tools: [weatherTool.definition, cityTool.definition],
});

// Handle function calls during run polling
const run = await client.runs.createAndPoll(thread.id, agent.id, {
  onResponse: async (response) => {
    const run = response.parsedBody;
    if (run.status === "requires_action" && run.requiredAction) {
      if (isOutputOfType<SubmitToolOutputsAction>(run.requiredAction, "submit_tool_outputs")) {
        const toolCalls = run.requiredAction.submitToolOutputs.toolCalls;
        const toolOutputs: ToolOutput[] = toolCalls.map((call) => ({
          toolCallId: call.id,
          output: JSON.stringify(executeFunction(call)), // Your implementation
        }));
        await client.runs.submitToolOutputs(thread.id, run.id, toolOutputs);
      }
    }
  },
});
```

---

## Code Interpreter Tool

Execute Python code for data analysis, file processing, and visualization.

```typescript
import { ToolUtility } from "@azure/ai-agents";
import fs from "node:fs";

// Upload file for code interpreter
const fileStream = fs.createReadStream("./data/quarterly_results.csv");
const file = await client.files.upload(fileStream, "assistants", {
  fileName: "quarterly_results.csv",
});

// Create code interpreter tool with file
const codeInterpreterTool = ToolUtility.createCodeInterpreterTool([file.id]);

// Create agent with code interpreter
const agent = await client.createAgent("gpt-4o", {
  name: "data-analyst",
  instructions: "You are a data analyst. Analyze uploaded files and create visualizations.",
  tools: [codeInterpreterTool.definition],
  toolResources: codeInterpreterTool.resources,
});

// Create message with file attachment
const message = await client.messages.create(
  thread.id,
  "user",
  "Create a bar chart of operating profit by sector from the CSV file.",
  {
    attachments: [
      {
        fileId: file.id,
        tools: [codeInterpreterTool.definition],
      },
    ],
  }
);
```

---

## File Search Tool

Search through uploaded documents using vector stores.

```typescript
import { ToolUtility } from "@azure/ai-agents";
import fs from "node:fs";

// Upload file
const fileStream = fs.createReadStream("./data/product_docs.txt");
const file = await client.files.upload(fileStream, "assistants", {
  fileName: "product_docs.txt",
});

// Create vector store with file
const vectorStore = await client.vectorStores.create({
  fileIds: [file.id],
  name: "product-documentation",
});

// Create file search tool
const fileSearchTool = ToolUtility.createFileSearchTool([vectorStore.id]);

// Create agent with file search
const agent = await client.createAgent("gpt-4o", {
  name: "doc-search-agent",
  instructions: "You help users find information in product documentation.",
  tools: [fileSearchTool.definition],
  toolResources: fileSearchTool.resources,
});

// Attach file to message for search
const message = await client.messages.create(
  thread.id,
  "user",
  "What features does the Smart Eyewear product offer?",
  {
    attachments: [
      {
        fileId: file.id,
        tools: [fileSearchTool.definition],
      },
    ],
  }
);
```

---

## Bing Grounding Tool

Enable web search via Bing Search API.

```typescript
import { ToolUtility } from "@azure/ai-agents";

const connectionId = process.env["AZURE_BING_CONNECTION_ID"]!;

// Create Bing grounding tool
const bingTool = ToolUtility.createBingGroundingTool([
  {
    connectionId: connectionId,
    market: "en-US",      // Optional: market locale
    count: 10,            // Optional: number of results
    freshness: "Week",    // Optional: "Day", "Week", "Month"
  },
]);

// Create agent with Bing search
const agent = await client.createAgent("gpt-4o", {
  name: "search-agent",
  instructions: "You are a helpful agent that can search the web for current information.",
  tools: [bingTool.definition],
});
```

---

## Azure AI Search Tool

Integrate enterprise search with Azure AI Search indexes.

```typescript
import { ToolUtility } from "@azure/ai-agents";

const connectionName = process.env["AZURE_AI_SEARCH_CONNECTION_NAME"]!;

// Create Azure AI Search tool
const searchTool = ToolUtility.createAzureAISearchTool(
  connectionName,
  "products-index",
  {
    queryType: "simple",  // "simple", "semantic", "vector", "hybrid"
    topK: 5,              // Number of results to return
    filter: "",           // OData filter expression
  }
);

// Create agent with Azure AI Search
const agent = await client.createAgent("gpt-4o", {
  name: "enterprise-search-agent",
  instructions: "You help users find information in our product catalog.",
  tools: [searchTool.definition],
  toolResources: searchTool.resources,
});
```

---

## Using ToolSet for Multiple Tools

Combine multiple tools using the `ToolSet` class.

```typescript
import { ToolSet } from "@azure/ai-agents";

const toolSet = new ToolSet();

// Add file search tool
toolSet.addFileSearchTool([vectorStore.id]);

// Add code interpreter tool
toolSet.addCodeInterpreterTool([dataFile.id]);

// Add Bing grounding tool
toolSet.addBingGroundingTool([{ connectionId: bingConnectionId }]);

// Create agent with all tools
const agent = await client.createAgent("gpt-4o", {
  name: "multi-tool-agent",
  instructions: "You can search files, analyze data, and search the web.",
  tools: toolSet.toolDefinitions,
  toolResources: toolSet.toolResources,
});
```

---

## Tool Choice Configuration

Control which tools the agent uses.

```typescript
// Let the agent decide (default)
const run1 = await client.runs.create(thread.id, agent.id);

// Force a specific tool
const run2 = await client.runs.createAndPoll(thread.id, agent.id, {
  toolChoice: {
    type: "function",
    function: { name: "getWeather" },
  },
});

// Disable all tools for this run
const run3 = await client.runs.createAndPoll(thread.id, agent.id, {
  toolChoice: "none",
});

// Require at least one tool call
const run4 = await client.runs.createAndPoll(thread.id, agent.id, {
  toolChoice: "required",
});
```

---

## OpenAPI Tool

Call REST APIs defined by OpenAPI specifications.

```typescript
import { ToolUtility } from "@azure/ai-agents";
import fs from "node:fs";

// Load OpenAPI spec
const openApiSpec = JSON.parse(fs.readFileSync("./weather-api.json", "utf-8"));

// Create OpenAPI tool
const openApiTool = ToolUtility.createOpenApiTool({
  name: "getWeather",
  spec: openApiSpec,
  description: "Retrieve weather information for a location",
  auth: { type: "anonymous" },
  default_params: ["format"],
});

// Create agent with OpenAPI tool
const agent = await client.createAgent("gpt-4o", {
  name: "api-agent",
  instructions: "You can fetch weather data from the weather API.",
  tools: [openApiTool.definition],
});
```

---

## Connected Agents Tool

Connect multiple agents together.

```typescript
import { ToolUtility } from "@azure/ai-agents";

// Create a specialized agent
const stockAgent = await client.createAgent("gpt-4o", {
  name: "stock-price-agent",
  instructions: "Your job is to get stock prices for companies.",
});

// Create connected agent tool
const connectedAgentTool = ToolUtility.createConnectedAgentTool(
  stockAgent.id,
  "stock_price_bot",
  "Gets the stock price of a company"
);

// Create main agent with connected agent
const mainAgent = await client.createAgent("gpt-4o", {
  name: "financial-assistant",
  instructions: "You help with financial questions. Use the connected agent for stock prices.",
  tools: [connectedAgentTool.definition],
});
```

---

## Cleanup

```typescript
// Delete resources when done
await client.vectorStores.delete(vectorStore.id);
await client.files.delete(file.id);
await client.deleteAgent(agent.id);
```

---

## Best Practices

1. **Validate tool parameters** - Always validate inputs before executing function tools
2. **Handle timeouts** - Set reasonable timeouts for tool execution
3. **Clean up resources** - Delete files and vector stores when no longer needed
4. **Use specific instructions** - Guide the agent on when to use each tool
5. **Error handling** - Implement proper error handling in function tool implementations
6. **Tool choice** - Use `toolChoice` to constrain agent behavior when needed

---

## See Also

- [Streaming Patterns](./streaming.md) - Streaming responses with tools
- [Official Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/ai/ai-agents/samples)
