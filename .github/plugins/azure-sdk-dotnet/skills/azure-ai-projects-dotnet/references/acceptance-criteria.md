# Azure.AI.Projects SDK Acceptance Criteria (.NET)

**SDK**: `Azure.AI.Projects`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/ai/Azure.AI.Projects
**Package**: https://www.nuget.org/packages/Azure.AI.Projects
**Purpose**: Skill testing acceptance criteria for validating generated C# code correctness

---

## 1. Correct Using Statements

### 1.1 Core Imports

#### ✅ CORRECT: Basic Client Imports
```csharp
using Azure;
using Azure.AI.Projects;
using Azure.Identity;
```

#### ✅ CORRECT: For Persistent Agents
```csharp
using Azure.AI.Projects;
using Azure.AI.Agents.Persistent;
using Azure.Identity;
```

#### ✅ CORRECT: For Versioned Agents (Preview)
```csharp
using Azure.AI.Projects;
using Azure.AI.Projects.OpenAI;
using Azure.Identity;
```

#### ✅ CORRECT: For Azure OpenAI Integration
```csharp
using Azure.AI.Projects;
using Azure.AI.OpenAI;
using Azure.Identity;
using OpenAI.Chat;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using Azure.AI.Projects.Agents;
using Azure.AI.Projects.Models;
using Azure.AI.Foundry;
```

#### ❌ INCORRECT: Confusing with Inference SDK
```csharp
// WRONG - This is Azure.AI.Inference, not Azure.AI.Projects
using Azure.AI.Inference;
var client = new ChatCompletionsClient(endpoint, credential);
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: AIProjectClient Creation
```csharp
var endpoint = Environment.GetEnvironmentVariable("PROJECT_ENDPOINT");
AIProjectClient projectClient = new AIProjectClient(
    new Uri(endpoint), 
    new DefaultAzureCredential());
```

### 2.2 ✅ CORRECT: Get Persistent Agents Client
```csharp
AIProjectClient projectClient = new AIProjectClient(
    new Uri(endpoint), 
    new DefaultAzureCredential());

PersistentAgentsClient agentsClient = projectClient.GetPersistentAgentsClient();
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter order
```csharp
// WRONG - endpoint should be first, credential second
var client = new AIProjectClient(new DefaultAzureCredential(), new Uri(endpoint));
```

#### ❌ INCORRECT: Using string instead of Uri
```csharp
// WRONG - endpoint must be Uri, not string
var client = new AIProjectClient(endpoint, new DefaultAzureCredential());
```

#### ❌ INCORRECT: Creating AgentsClient directly
```csharp
// WRONG - Should get from AIProjectClient
var agentsClient = new PersistentAgentsClient(endpoint, credential);
```

---

## 3. Connections Operations

### 3.1 ✅ CORRECT: List All Connections
```csharp
foreach (AIProjectConnection connection in projectClient.Connections.GetConnections())
{
    Console.WriteLine($"{connection.Name}: {connection.ConnectionType}");
}
```

### 3.2 ✅ CORRECT: Get Specific Connection
```csharp
AIProjectConnection connection = projectClient.Connections.GetConnection(
    connectionName, 
    includeCredentials: true);

Console.WriteLine($"Name: {connection.Name}");
Console.WriteLine($"Type: {connection.ConnectionType}");
Console.WriteLine($"Endpoint: {connection.Endpoint}");
```

### 3.3 ✅ CORRECT: Get Default Connection
```csharp
AIProjectConnection defaultConnection = projectClient.Connections.GetDefaultConnection(
    includeCredentials: false);
```

### 3.4 ✅ CORRECT: Async Connections
```csharp
await foreach (AIProjectConnection connection in projectClient.Connections.GetConnectionsAsync())
{
    Console.WriteLine(connection.Name);
}

AIProjectConnection conn = await projectClient.Connections.GetConnectionAsync(
    connectionName, 
    includeCredentials: true);
```

### 3.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong method names
```csharp
// WRONG - Method names don't match
var conn = projectClient.Connections.Get(connectionName);  // Should be GetConnection
var conns = projectClient.Connections.List();               // Should be GetConnections
```

---

## 4. Deployments Operations

### 4.1 ✅ CORRECT: List All Deployments
```csharp
foreach (AIProjectDeployment deployment in projectClient.Deployments.GetDeployments())
{
    Console.WriteLine($"{deployment.Name}: {deployment.ModelName}");
}
```

### 4.2 ✅ CORRECT: Filter Deployments by Publisher
```csharp
foreach (var deployment in projectClient.Deployments.GetDeployments(modelPublisher: "Microsoft"))
{
    Console.WriteLine($"{deployment.Name}: {deployment.ModelName}");
}
```

### 4.3 ✅ CORRECT: Get Specific Deployment
```csharp
ModelDeployment deployment = (ModelDeployment)projectClient.Deployments.GetDeployment("gpt-4o-mini");
Console.WriteLine($"Model: {deployment.ModelName}");
Console.WriteLine($"Endpoint: {deployment.EndpointUrl}");
```

### 4.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong cast type
```csharp
// WRONG - Should cast to ModelDeployment
AIProjectDeployment deployment = projectClient.Deployments.GetDeployment("gpt-4o-mini");
// Correct: (ModelDeployment)projectClient.Deployments.GetDeployment("gpt-4o-mini")
```

---

## 5. Datasets Operations

### 5.1 ✅ CORRECT: Upload Single File
```csharp
FileDataset fileDataset = projectClient.Datasets.UploadFile(
    name: "my-dataset",
    version: "1.0",
    filePath: "data/training.txt",
    connectionName: connectionName);

Console.WriteLine($"Dataset ID: {fileDataset.Id}");
```

### 5.2 ✅ CORRECT: Upload Folder with Pattern
```csharp
FolderDataset folderDataset = projectClient.Datasets.UploadFolder(
    name: "training-data",
    version: "2.0",
    folderPath: "data/training",
    connectionName: connectionName,
    filePattern: new Regex(".*\\.txt"));

Console.WriteLine($"Dataset ID: {folderDataset.Id}");
```

### 5.3 ✅ CORRECT: Get and Delete Dataset
```csharp
// Get dataset
AIProjectDataset dataset = projectClient.Datasets.GetDataset("my-dataset", "1.0");

// List all datasets
foreach (var ds in projectClient.Datasets.GetDatasets())
{
    Console.WriteLine($"{ds.Name}: {ds.Version}");
}

// Delete dataset
projectClient.Datasets.Delete("my-dataset", "1.0");
```

### 5.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing required parameters
```csharp
// WRONG - Missing version parameter
projectClient.Datasets.UploadFile("my-dataset", "data.txt", connectionName);
```

---

## 6. Indexes Operations

### 6.1 ✅ CORRECT: Create Azure AI Search Index
```csharp
AzureAISearchIndex searchIndex = new(aiSearchConnectionName, aiSearchIndexName)
{
    Description = "Sample Index"
};

searchIndex = (AzureAISearchIndex)projectClient.Indexes.CreateOrUpdate(
    name: "my-index",
    version: "1.0",
    index: searchIndex);

Console.WriteLine($"Index ID: {searchIndex.Id}");
```

### 6.2 ✅ CORRECT: List and Delete Indexes
```csharp
// List all indexes
foreach (AIProjectIndex index in projectClient.Indexes.GetIndexes())
{
    Console.WriteLine($"{index.Name}: {index.Version}");
}

// Delete index
projectClient.Indexes.Delete(name: "my-index", version: "1.0");
```

---

## 7. Evaluations Operations

### 7.1 ✅ CORRECT: Create and Run Evaluation
```csharp
// Create evaluator configuration
var evaluatorConfig = new EvaluatorConfiguration(id: EvaluatorIDs.Relevance);
evaluatorConfig.InitParams.Add("deployment_name", BinaryData.FromObjectAsJson("gpt-4o"));

// Create evaluation
Evaluation evaluation = new Evaluation(
    data: new InputDataset("<dataset_id>"),
    evaluators: new Dictionary<string, EvaluatorConfiguration> 
    { 
        { "relevance", evaluatorConfig } 
    }
)
{
    DisplayName = "Sample Evaluation"
};

// Run evaluation
Evaluation result = projectClient.Evaluations.Create(evaluation: evaluation);
Console.WriteLine($"Evaluation ID: {result.Name}");
Console.WriteLine($"Status: {result.Status}");
```

### 7.2 ✅ CORRECT: Get and List Evaluations
```csharp
// Get specific evaluation
Evaluation evaluation = projectClient.Evaluations.Get("evaluation-name");

// List all evaluations
foreach (var eval in projectClient.Evaluations.GetAll())
{
    Console.WriteLine($"{eval.DisplayName}: {eval.Status}");
}
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong evaluator ID format
```csharp
// WRONG - Should use EvaluatorIDs constants
var config = new EvaluatorConfiguration(id: "relevance");  // Should be EvaluatorIDs.Relevance
```

---

## 8. Persistent Agents Operations

### 8.1 ✅ CORRECT: Create Agent with Code Interpreter
```csharp
PersistentAgentsClient agentsClient = projectClient.GetPersistentAgentsClient();

PersistentAgent agent = await agentsClient.Administration.CreateAgentAsync(
    model: "gpt-4o-mini",
    name: "Math Tutor",
    instructions: "You are a personal math tutor. Write and run code to answer math questions.",
    tools: [new CodeInterpreterToolDefinition()]
);
```

### 8.2 ✅ CORRECT: Full Agent Workflow
```csharp
PersistentAgentsClient agentsClient = projectClient.GetPersistentAgentsClient();

// Create agent
PersistentAgent agent = await agentsClient.Administration.CreateAgentAsync(
    model: "gpt-4o-mini",
    name: "Math Tutor",
    instructions: "You are a personal math tutor.");

// Create thread
PersistentAgentThread thread = await agentsClient.Threads.CreateThreadAsync();

// Add message
await agentsClient.Messages.CreateMessageAsync(
    thread.Id, 
    MessageRole.User, 
    "Solve 3x + 11 = 14");

// Create run
ThreadRun run = await agentsClient.Runs.CreateRunAsync(thread.Id, agent.Id);

// Poll for completion
do
{
    await Task.Delay(500);
    run = await agentsClient.Runs.GetRunAsync(thread.Id, run.Id);
}
while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress);

// Get messages
await foreach (var msg in agentsClient.Messages.GetMessagesAsync(thread.Id))
{
    foreach (var content in msg.ContentItems)
    {
        if (content is MessageTextContent textContent)
            Console.WriteLine(textContent.Text);
    }
}

// Cleanup
await agentsClient.Threads.DeleteThreadAsync(thread.Id);
await agentsClient.Administration.DeleteAgentAsync(agent.Id);
```

### 8.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not polling for run completion
```csharp
// WRONG - Must poll for completion before reading messages
var run = await agentsClient.Runs.CreateRunAsync(thread.Id, agent.Id);
var messages = await agentsClient.Messages.GetMessagesAsync(thread.Id);  // Run not completed yet!
```

#### ❌ INCORRECT: Missing cleanup
```csharp
// WRONG - Should clean up resources
var agent = await agentsClient.Administration.CreateAgentAsync(...);
var thread = await agentsClient.Threads.CreateThreadAsync();
// ... use agent ...
// Missing: DeleteThreadAsync, DeleteAgentAsync
```

---

## 9. Versioned Agents (Preview)

### 9.1 ✅ CORRECT: Create Versioned Agent
```csharp
using Azure.AI.Projects.OpenAI;

// Create agent definition
PromptAgentDefinition agentDefinition = new(model: "gpt-4o-mini")
{
    Instructions = "You are a helpful assistant that can search the web",
    Tools = {
        ResponseTool.CreateWebSearchTool(
            userLocation: WebSearchToolLocation.CreateApproximateLocation(
                country: "US",
                city: "Seattle",
                region: "Washington"
            )
        ),
    }
};

// Create versioned agent
AgentVersion agentVersion = await projectClient.Agents.CreateAgentVersionAsync(
    agentName: "myAgent",
    options: new(agentDefinition));

Console.WriteLine($"Agent: {agentVersion.Name}, Version: {agentVersion.Version}");
```

### 9.2 ✅ CORRECT: Use Versioned Agent
```csharp
// Get response client
ProjectResponsesClient responseClient = projectClient.OpenAI.GetProjectResponsesClientForAgent(agentVersion.Name);

// Create response
ResponseResult response = responseClient.CreateResponse("What's the weather in Seattle?");
Console.WriteLine(response.GetOutputText());

// Cleanup
projectClient.Agents.DeleteAgentVersion(agentName: agentVersion.Name, agentVersion: agentVersion.Version);
```

### 9.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using wrong client for versioned agents
```csharp
// WRONG - Versioned agents use Agents property, not GetPersistentAgentsClient
var agentsClient = projectClient.GetPersistentAgentsClient();
// For versioned agents, use projectClient.Agents instead
```

---

## 10. Azure OpenAI Integration

### 10.1 ✅ CORRECT: Get Azure OpenAI Chat Client
```csharp
using Azure.AI.OpenAI;
using OpenAI.Chat;

ClientConnection connection = projectClient.GetConnection(typeof(AzureOpenAIClient).FullName!);

if (!connection.TryGetLocatorAsUri(out Uri uri) || uri is null)
    throw new InvalidOperationException("Invalid URI.");

uri = new Uri($"https://{uri.Host}");

AzureOpenAIClient azureOpenAIClient = new AzureOpenAIClient(uri, new DefaultAzureCredential());
ChatClient chatClient = azureOpenAIClient.GetChatClient("gpt-4o-mini");

ChatCompletion result = chatClient.CompleteChat("List all rainbow colors");
Console.WriteLine(result.Content[0].Text);
```

---

## 11. Error Handling Patterns

### 11.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    var result = await projectClient.Evaluations.CreateAsync(evaluation);
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
    
    switch (ex.Status)
    {
        case 404:
            Console.WriteLine("Resource not found");
            break;
        case 409:
            Console.WriteLine("Conflict - resource may already exist");
            break;
        default:
            throw;
    }
}
```

---

## 12. Key Types Reference

| Type | Purpose |
|------|---------|
| `AIProjectClient` | Main entry point for all operations |
| `PersistentAgentsClient` | Low-level agent operations |
| `AIProjectAgentsOperations` | Versioned agents operations |
| `ConnectionsClient` | Connection management |
| `DatasetsClient` | Dataset upload and management |
| `DeploymentsClient` | Model deployment info |
| `EvaluationsClient` | Run and manage evaluations |
| `IndexesClient` | Search index management |
| `AIProjectConnection` | Connection metadata |
| `AIProjectDeployment` | Deployment metadata |
| `AIProjectDataset` | Dataset metadata |
| `AIProjectIndex` | Index metadata |
| `Evaluation` | Evaluation config and results |
| `PromptAgentDefinition` | Versioned agent definition |
| `AgentVersion` | Versioned agent instance |
| `EvaluatorConfiguration` | Evaluator setup |
| `EvaluatorIDs` | Standard evaluator IDs |

---

## 13. Available Agent Tools

| Tool | Class | Purpose |
|------|-------|---------|
| Code Interpreter | `CodeInterpreterToolDefinition` | Execute Python code |
| File Search | `FileSearchToolDefinition` | Search uploaded files |
| Function Calling | `FunctionToolDefinition` | Call custom functions |
| Bing Grounding | `BingGroundingToolDefinition` | Web search via Bing |
| Azure AI Search | `AzureAISearchToolDefinition` | Search Azure AI indexes |
| OpenAPI | `OpenApiToolDefinition` | Call external APIs |
| Azure Functions | `AzureFunctionToolDefinition` | Invoke Azure Functions |
| MCP | `MCPToolDefinition` | Model Context Protocol tools |

---

## 14. Best Practices Summary

1. **Use DefaultAzureCredential** — Prefer over API keys for production
2. **Use async methods** — `*Async` methods for all I/O operations
3. **Poll with appropriate delays** — 500ms recommended when waiting for runs
4. **Clean up resources** — Delete threads, agents, files when done
5. **Use versioned agents** — Via `Azure.AI.Projects.OpenAI` for production
6. **Store IDs not names** — Reference resources by ID when possible
7. **Use includeCredentials wisely** — Only true when credentials needed
8. **Handle pagination** — Use `AsyncPageable<T>` for listing operations
9. **Handle RequestFailedException** — Check status codes for retry logic
10. **Get PersistentAgentsClient from AIProjectClient** — Don't create directly
