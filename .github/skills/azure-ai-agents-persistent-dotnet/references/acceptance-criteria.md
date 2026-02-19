# Azure.AI.Agents.Persistent SDK Acceptance Criteria (.NET)

**SDK**: `Azure.AI.Agents.Persistent`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/ai/Azure.AI.Agents.Persistent
**Package**: https://www.nuget.org/packages/Azure.AI.Agents.Persistent
**Purpose**: Skill testing acceptance criteria for validating generated C# code correctness

---

## 1. Correct Using Statements

### 1.1 Core Imports

#### ✅ CORRECT: Basic Client Imports
```csharp
using Azure;
using Azure.AI.Agents.Persistent;
using Azure.Identity;
```

#### ✅ CORRECT: For Tool Definitions
```csharp
using Azure.AI.Agents.Persistent;
using System.Text.Json;
```

#### ✅ CORRECT: For Streaming
```csharp
using Azure.AI.Agents.Persistent;
using System.ClientModel;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using Azure.AI.Agents;
using Azure.AI.Agents.Persistent.Models;
using Azure.AI.Agents.Persistent.Tools;
```

#### ❌ INCORRECT: Confusing with Python SDK types
```csharp
// WRONG - These are Python SDK patterns
using Azure.AI.Agents.Models;  // Doesn't exist in .NET
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Direct Client Creation
```csharp
var projectEndpoint = Environment.GetEnvironmentVariable("PROJECT_ENDPOINT");
PersistentAgentsClient client = new(projectEndpoint, new DefaultAzureCredential());
```

### 2.2 ✅ CORRECT: From AIProjectClient (Recommended)
```csharp
using Azure.AI.Projects;
using Azure.AI.Agents.Persistent;
using Azure.Identity;

AIProjectClient projectClient = new AIProjectClient(
    new Uri(endpoint), 
    new DefaultAzureCredential());

PersistentAgentsClient client = projectClient.GetPersistentAgentsClient();
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing credential
```csharp
// WRONG - Must provide credential
PersistentAgentsClient client = new(projectEndpoint);
```

#### ❌ INCORRECT: Wrong client type
```csharp
// WRONG - AgentsClient doesn't exist, use PersistentAgentsClient
var client = new AgentsClient(endpoint, credential);
```

---

## 3. Agent CRUD Operations

### 3.1 ✅ CORRECT: Create Basic Agent
```csharp
var modelDeploymentName = Environment.GetEnvironmentVariable("MODEL_DEPLOYMENT_NAME");

PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Math Tutor",
    instructions: "You are a personal math tutor."
);

Console.WriteLine($"Agent ID: {agent.Id}");
```

### 3.2 ✅ CORRECT: Create Agent with Code Interpreter
```csharp
PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Code Assistant",
    instructions: "You are a coding assistant. Write and run code to answer questions.",
    tools: [new CodeInterpreterToolDefinition()]
);
```

### 3.3 ✅ CORRECT: Create Agent with File Search
```csharp
// Upload file first
PersistentAgentFileInfo file = await client.Files.UploadFileAsync(
    filePath: "document.txt",
    purpose: PersistentAgentFilePurpose.Agents
);

// Create vector store
PersistentAgentsVectorStore vectorStore = await client.VectorStores.CreateVectorStoreAsync(
    fileIds: [file.Id],
    name: "my_vector_store"
);

// Create file search resource
FileSearchToolResource fileSearchResource = new();
fileSearchResource.VectorStoreIds.Add(vectorStore.Id);

// Create agent with file search
PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Document Assistant",
    instructions: "You help users find information in documents.",
    tools: [new FileSearchToolDefinition()],
    toolResources: new ToolResources { FileSearch = fileSearchResource }
);
```

### 3.4 ✅ CORRECT: List and Delete Agents
```csharp
// List agents
await foreach (PersistentAgent agent in client.Administration.GetAgentsAsync())
{
    Console.WriteLine($"{agent.Id}: {agent.Name}");
}

// Delete agent
await client.Administration.DeleteAgentAsync(agent.Id);
```

### 3.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong method names
```csharp
// WRONG - Method is CreateAgentAsync, not CreateAsync
var agent = await client.Administration.CreateAsync(model, name, instructions);
```

#### ❌ INCORRECT: Missing tool resources for file-based tools
```csharp
// WRONG - FileSearchToolDefinition needs toolResources with vector store
PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    tools: [new FileSearchToolDefinition()]
    // Missing: toolResources: new ToolResources { FileSearch = ... }
);
```

---

## 4. Thread Operations

### 4.1 ✅ CORRECT: Create Thread
```csharp
PersistentAgentThread thread = await client.Threads.CreateThreadAsync();
Console.WriteLine($"Thread ID: {thread.Id}");
```

### 4.2 ✅ CORRECT: Create Thread with Messages
```csharp
PersistentAgentThread thread = await client.Threads.CreateThreadAsync(
    messages: [
        new ThreadInitializationMessage(MessageRole.User, "Hello, I need help with math.")
    ]
);
```

### 4.3 ✅ CORRECT: Get and Delete Thread
```csharp
// Get thread
PersistentAgentThread thread = await client.Threads.GetThreadAsync(threadId);

// Delete thread
await client.Threads.DeleteThreadAsync(thread.Id);
```

### 4.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using wrong role enum
```csharp
// WRONG - Use MessageRole enum
var thread = await client.Threads.CreateThreadAsync(
    messages: [new ThreadInitializationMessage("user", "Hello")]  // Should be MessageRole.User
);
```

---

## 5. Message Operations

### 5.1 ✅ CORRECT: Create Message
```csharp
await client.Messages.CreateMessageAsync(
    thread.Id,
    MessageRole.User,
    "I need to solve the equation 3x + 11 = 14. Can you help me?"
);
```

### 5.2 ✅ CORRECT: List Messages
```csharp
await foreach (PersistentThreadMessage message in client.Messages.GetMessagesAsync(
    threadId: thread.Id, 
    order: ListSortOrder.Ascending))
{
    Console.Write($"{message.Role}: ");
    foreach (MessageContent content in message.ContentItems)
    {
        if (content is MessageTextContent textContent)
            Console.WriteLine(textContent.Text);
    }
}
```

### 5.3 ✅ CORRECT: Get Specific Message
```csharp
PersistentThreadMessage message = await client.Messages.GetMessageAsync(thread.Id, messageId);
```

### 5.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong content access pattern
```csharp
// WRONG - Must check content type
foreach (var msg in messages)
{
    Console.WriteLine(msg.Content);  // Content is ContentItems, not Content
}
```

#### ❌ INCORRECT: Missing thread ID
```csharp
// WRONG - Thread ID is required
await client.Messages.CreateMessageAsync(MessageRole.User, "Hello");
```

---

## 6. Run Operations

### 6.1 ✅ CORRECT: Create and Poll Run
```csharp
// Create run
ThreadRun run = await client.Runs.CreateRunAsync(
    thread.Id,
    agent.Id,
    additionalInstructions: "Please address the user as Jane Doe."
);

// Poll for completion
do
{
    await Task.Delay(TimeSpan.FromMilliseconds(500));
    run = await client.Runs.GetRunAsync(thread.Id, run.Id);
}
while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress);

// Check result
if (run.Status == RunStatus.Completed)
{
    Console.WriteLine("Run completed successfully!");
}
else if (run.Status == RunStatus.Failed)
{
    Console.WriteLine($"Run failed: {run.LastError?.Message}");
}
```

### 6.2 ✅ CORRECT: Create Run with Additional Instructions
```csharp
ThreadRun run = await client.Runs.CreateRunAsync(
    threadId: thread.Id,
    assistantId: agent.Id,
    additionalInstructions: "Be concise and use bullet points."
);
```

### 6.3 ✅ CORRECT: Cancel Run
```csharp
run = await client.Runs.CancelRunAsync(thread.Id, run.Id);
```

### 6.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not checking for failed status
```csharp
// WRONG - Should check run.Status for failure
do
{
    await Task.Delay(500);
    run = await client.Runs.GetRunAsync(thread.Id, run.Id);
}
while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress);
// Missing: if (run.Status == RunStatus.Failed) handling
```

#### ❌ INCORRECT: Missing RequiresAction handling
```csharp
// WRONG - Should handle RequiresAction status for function calling
while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress)
{
    await Task.Delay(500);
    run = await client.Runs.GetRunAsync(thread.Id, run.Id);
    // Missing: if (run.Status == RunStatus.RequiresAction) handling
}
```

---

## 7. Streaming Operations

### 7.1 ✅ CORRECT: Basic Streaming
```csharp
AsyncCollectionResult<StreamingUpdate> stream = client.Runs.CreateRunStreamingAsync(
    thread.Id, 
    agent.Id
);

await foreach (StreamingUpdate update in stream)
{
    if (update.UpdateKind == StreamingUpdateReason.RunCreated)
    {
        Console.WriteLine("--- Run started! ---");
    }
    else if (update is MessageContentUpdate contentUpdate)
    {
        Console.Write(contentUpdate.Text);
    }
    else if (update.UpdateKind == StreamingUpdateReason.RunCompleted)
    {
        Console.WriteLine("\n--- Run completed! ---");
    }
}
```

### 7.2 ✅ CORRECT: Streaming with All Update Types
```csharp
AsyncCollectionResult<StreamingUpdate> stream = client.Runs.CreateRunStreamingAsync(
    thread.Id, 
    agent.Id
);

await foreach (StreamingUpdate update in stream)
{
    switch (update.UpdateKind)
    {
        case StreamingUpdateReason.RunCreated:
            Console.WriteLine("Run started");
            break;
        case StreamingUpdateReason.RunInProgress:
            Console.WriteLine("Run in progress");
            break;
        case StreamingUpdateReason.RunCompleted:
            Console.WriteLine("Run completed");
            break;
        case StreamingUpdateReason.RunFailed:
            Console.WriteLine("Run failed");
            break;
    }

    if (update is MessageContentUpdate contentUpdate)
    {
        Console.Write(contentUpdate.Text);
    }
    else if (update is RunStepUpdate stepUpdate)
    {
        Console.WriteLine($"Step: {stepUpdate.UpdateKind}");
    }
}
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using wrong streaming method
```csharp
// WRONG - Use CreateRunStreamingAsync, not CreateRunAsync with stream parameter
var response = await client.Runs.CreateRunAsync(threadId, agentId, stream: true);
```

---

## 8. Function Calling

### 8.1 ✅ CORRECT: Define Function Tool
```csharp
FunctionToolDefinition weatherTool = new(
    name: "getCurrentWeather",
    description: "Gets the current weather at a location.",
    parameters: BinaryData.FromObjectAsJson(new
    {
        Type = "object",
        Properties = new
        {
            Location = new { Type = "string", Description = "City and state, e.g. San Francisco, CA" },
            Unit = new { Type = "string", Enum = new[] { "c", "f" } }
        },
        Required = new[] { "location" }
    }, new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase })
);

PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Weather Bot",
    instructions: "You are a weather bot.",
    tools: [weatherTool]
);
```

### 8.2 ✅ CORRECT: Handle Function Calls
```csharp
ThreadRun run = await client.Runs.CreateRunAsync(thread.Id, agent.Id);

do
{
    await Task.Delay(500);
    run = await client.Runs.GetRunAsync(thread.Id, run.Id);

    if (run.Status == RunStatus.RequiresAction 
        && run.RequiredAction is SubmitToolOutputsAction submitAction)
    {
        List<ToolOutput> outputs = [];
        foreach (RequiredToolCall toolCall in submitAction.ToolCalls)
        {
            if (toolCall is RequiredFunctionToolCall funcCall)
            {
                // Execute function and get result
                string result = ExecuteFunction(funcCall.Name, funcCall.Arguments);
                outputs.Add(new ToolOutput(toolCall, result));
            }
        }
        run = await client.Runs.SubmitToolOutputsToRunAsync(run, outputs, toolApprovals: null);
    }
}
while (run.Status == RunStatus.Queued 
    || run.Status == RunStatus.InProgress 
    || run.Status == RunStatus.RequiresAction);
```

### 8.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing RequiresAction check in loop condition
```csharp
// WRONG - Will exit loop when RequiresAction, but function calls need handling
while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress)
{
    await Task.Delay(500);
    run = await client.Runs.GetRunAsync(thread.Id, run.Id);
}
// If run.Status == RequiresAction, it's not handled!
```

#### ❌ INCORRECT: Wrong tool output format
```csharp
// WRONG - ToolOutput requires the tool call reference
outputs.Add(new ToolOutput(result));  // Missing tool call reference
```

---

## 9. Bing Grounding Tool

### 9.1 ✅ CORRECT: Create Agent with Bing Grounding
```csharp
var bingConnectionId = Environment.GetEnvironmentVariable("AZURE_BING_CONNECTION_ID");

BingGroundingToolDefinition bingTool = new(
    new BingGroundingSearchToolParameters(
        [new BingGroundingSearchConfiguration(bingConnectionId)]
    )
);

PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Search Agent",
    instructions: "Use Bing to answer questions about current events.",
    tools: [bingTool]
);
```

---

## 10. Azure AI Search Tool

### 10.1 ✅ CORRECT: Create Agent with Azure AI Search
```csharp
AzureAISearchToolResource searchResource = new(
    connectionId: searchConnectionId,
    indexName: "my_index",
    topK: 5,
    filter: "category eq 'documentation'",
    queryType: AzureAISearchQueryType.Simple
);

PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Search Agent",
    instructions: "Search the documentation index to answer questions.",
    tools: [new AzureAISearchToolDefinition()],
    toolResources: new ToolResources { AzureAISearch = searchResource }
);
```

---

## 11. File Operations

### 11.1 ✅ CORRECT: Upload File
```csharp
PersistentAgentFileInfo file = await client.Files.UploadFileAsync(
    filePath: "document.txt",
    purpose: PersistentAgentFilePurpose.Agents
);

Console.WriteLine($"File ID: {file.Id}");
```

### 11.2 ✅ CORRECT: List and Delete Files
```csharp
// List files
await foreach (PersistentAgentFileInfo file in client.Files.GetFilesAsync())
{
    Console.WriteLine($"{file.Id}: {file.Filename}");
}

// Delete file
await client.Files.DeleteFileAsync(file.Id);
```

---

## 12. Vector Store Operations

### 12.1 ✅ CORRECT: Create Vector Store
```csharp
PersistentAgentsVectorStore vectorStore = await client.VectorStores.CreateVectorStoreAsync(
    fileIds: [file.Id],
    name: "my_vector_store"
);

Console.WriteLine($"Vector Store ID: {vectorStore.Id}");
```

### 12.2 ✅ CORRECT: Delete Vector Store
```csharp
await client.VectorStores.DeleteVectorStoreAsync(vectorStore.Id);
```

---

## 13. Error Handling Patterns

### 13.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    var agent = await client.Administration.CreateAgentAsync(
        model: modelDeploymentName,
        name: "My Agent",
        instructions: "You are helpful."
    );
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Resource not found");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

---

## 14. Resource Cleanup Patterns

### 14.1 ✅ CORRECT: Full Cleanup
```csharp
// Always clean up in reverse order of creation
await client.Threads.DeleteThreadAsync(thread.Id);
await client.Administration.DeleteAgentAsync(agent.Id);
await client.VectorStores.DeleteVectorStoreAsync(vectorStore.Id);
await client.Files.DeleteFileAsync(file.Id);
```

---

## 15. Key Types Reference

| Type | Purpose |
|------|---------|
| `PersistentAgentsClient` | Main entry point |
| `PersistentAgent` | Agent with model, instructions, tools |
| `PersistentAgentThread` | Conversation thread |
| `PersistentThreadMessage` | Message in thread |
| `ThreadRun` | Execution of agent against thread |
| `RunStatus` | Queued, InProgress, RequiresAction, Completed, Failed, etc. |
| `ToolResources` | Combined tool resources |
| `ToolOutput` | Function call response |
| `StreamingUpdate` | Base type for streaming updates |
| `MessageContentUpdate` | Text content in stream |
| `RunStepUpdate` | Step status in stream |
| `PersistentAgentFileInfo` | Uploaded file info |
| `PersistentAgentsVectorStore` | Vector store for file search |
| `MessageRole` | User, Assistant |
| `ListSortOrder` | Ascending, Descending |

---

## 16. Available Tool Types

| Tool | Class | Purpose |
|------|-------|---------|
| Code Interpreter | `CodeInterpreterToolDefinition` | Execute Python code, generate visualizations |
| File Search | `FileSearchToolDefinition` | Search uploaded files via vector stores |
| Function Calling | `FunctionToolDefinition` | Call custom functions |
| Bing Grounding | `BingGroundingToolDefinition` | Web search via Bing |
| Azure AI Search | `AzureAISearchToolDefinition` | Search Azure AI Search indexes |
| OpenAPI | `OpenApiToolDefinition` | Call external APIs via OpenAPI spec |
| Azure Functions | `AzureFunctionToolDefinition` | Invoke Azure Functions |
| MCP | `MCPToolDefinition` | Model Context Protocol tools |
| SharePoint | `SharepointToolDefinition` | Access SharePoint content |
| Microsoft Fabric | `MicrosoftFabricToolDefinition` | Access Fabric data |

---

## 17. Streaming Update Types

| Update Reason | Description |
|---------------|-------------|
| `RunCreated` | Run started |
| `RunInProgress` | Run processing |
| `RunCompleted` | Run finished successfully |
| `RunFailed` | Run errored |
| `RunCancelled` | Run was cancelled |
| `ThreadCreated` | Thread was created |
| `MessageCreated` | New message created |
| `MessageCompleted` | Message finished |

---

## 18. Best Practices Summary

1. **Get client from AIProjectClient** — Use `projectClient.GetPersistentAgentsClient()`
2. **Use async methods** — All operations should use `*Async` methods
3. **Poll with appropriate delays** — 500ms recommended between status checks
4. **Handle all run statuses** — Check for `RequiresAction`, `Failed`, `Cancelled`
5. **Use streaming for real-time UX** — Better user experience than polling
6. **Clean up resources** — Delete threads, agents, files when done
7. **Store IDs not objects** — Reference agents/threads by ID
8. **Handle function calls** — Include `RequiresAction` in polling loop
9. **Use ToolResources** — Required for file-based tools (FileSearch, CodeInterpreter with files)
10. **Check content type** — Use `is MessageTextContent` pattern
