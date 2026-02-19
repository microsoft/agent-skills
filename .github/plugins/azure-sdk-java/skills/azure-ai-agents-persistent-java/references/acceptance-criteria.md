# Azure AI Agents Persistent SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-agents-persistent`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-agents-persistent
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync and Async Clients
```java
import com.azure.ai.agents.persistent.PersistentAgentsClient;
import com.azure.ai.agents.persistent.PersistentAgentsAsyncClient;
import com.azure.ai.agents.persistent.PersistentAgentsClientBuilder;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Agent Models
```java
import com.azure.ai.agents.persistent.models.PersistentAgent;
import com.azure.ai.agents.persistent.models.CreateAgentOptions;
import com.azure.ai.agents.persistent.models.UpdateAgentOptions;
```

#### ✅ CORRECT: Thread Models
```java
import com.azure.ai.agents.persistent.models.PersistentAgentThread;
import com.azure.ai.agents.persistent.models.CreateThreadOptions;
import com.azure.ai.agents.persistent.models.UpdateThreadOptions;
import com.azure.ai.agents.persistent.models.ThreadMessageOptions;
```

#### ✅ CORRECT: Message Models
```java
import com.azure.ai.agents.persistent.models.PersistentThreadMessage;
import com.azure.ai.agents.persistent.models.CreateMessageOptions;
import com.azure.ai.agents.persistent.models.MessageRole;
import com.azure.ai.agents.persistent.models.MessageContent;
import com.azure.ai.agents.persistent.models.MessageTextContent;
```

#### ✅ CORRECT: Run Models
```java
import com.azure.ai.agents.persistent.models.ThreadRun;
import com.azure.ai.agents.persistent.models.RunStatus;
import com.azure.ai.agents.persistent.models.CreateRunOptions;
import com.azure.ai.agents.persistent.models.RunStep;
```

#### ✅ CORRECT: Tool Models
```java
import com.azure.ai.agents.persistent.models.ToolDefinition;
import com.azure.ai.agents.persistent.models.CodeInterpreterToolDefinition;
import com.azure.ai.agents.persistent.models.FileSearchToolDefinition;
import com.azure.ai.agents.persistent.models.FunctionToolDefinition;
import com.azure.ai.agents.persistent.models.FunctionDefinition;
import com.azure.ai.agents.persistent.models.ToolResources;
import com.azure.ai.agents.persistent.models.FileSearchToolResource;
```

#### ✅ CORRECT: Tool Call Models
```java
import com.azure.ai.agents.persistent.models.RequiredAction;
import com.azure.ai.agents.persistent.models.SubmitToolOutputsAction;
import com.azure.ai.agents.persistent.models.RequiredToolCall;
import com.azure.ai.agents.persistent.models.RequiredFunctionToolCall;
import com.azure.ai.agents.persistent.models.ToolOutput;
```

#### ✅ CORRECT: File Models
```java
import com.azure.ai.agents.persistent.models.AgentFile;
import com.azure.ai.agents.persistent.models.AgentFilePurpose;
import com.azure.ai.agents.persistent.models.VectorStore;
import com.azure.ai.agents.persistent.models.CreateVectorStoreOptions;
```

#### ✅ CORRECT: Streaming Models
```java
import com.azure.ai.agents.persistent.models.streaming.ThreadRunCreatedEvent;
import com.azure.ai.agents.persistent.models.streaming.ThreadMessageDeltaEvent;
import com.azure.ai.agents.persistent.models.streaming.ThreadRunCompletedEvent;
import com.azure.ai.agents.persistent.models.streaming.MessageDeltaContent;
import com.azure.ai.agents.persistent.models.streaming.MessageDeltaTextContent;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```java
// WRONG - Using non-persistent SDK
import com.azure.ai.agents.AgentsClient;

// WRONG - Models in wrong package
import com.azure.ai.agents.persistent.PersistentAgent;
import com.azure.ai.agents.persistent.ThreadRun;

// WRONG - Non-existent classes
import com.azure.ai.agents.persistent.models.Agent;
import com.azure.ai.agents.persistent.models.Thread;
import com.azure.ai.agents.persistent.models.Message;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: With DefaultAzureCredential
```java
String endpoint = System.getenv("PROJECT_ENDPOINT");

PersistentAgentsClient client = new PersistentAgentsClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.2 ✅ CORRECT: Async Client
```java
PersistentAgentsAsyncClient asyncClient = new PersistentAgentsClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```java
// WRONG - hardcoded endpoint
PersistentAgentsClient client = new PersistentAgentsClientBuilder()
    .endpoint("https://myresource.services.ai.azure.com/api/projects/myproject")
    .credential(new AzureKeyCredential("sk-1234567890"))
    .buildClient();
```

---

## 3. Agent Operations

### 3.1 ✅ CORRECT: Create Agent (Simple)
```java
String modelDeploymentName = System.getenv("MODEL_DEPLOYMENT_NAME");

PersistentAgent agent = client.createAgent(
    modelDeploymentName,
    "Math Tutor",                    // name
    "You are a personal math tutor." // instructions
);

System.out.println("Agent ID: " + agent.getId());
System.out.println("Agent Name: " + agent.getName());
```

### 3.2 ✅ CORRECT: Create Agent with Options
```java
CreateAgentOptions options = new CreateAgentOptions(modelDeploymentName)
    .setName("Customer Support Agent")
    .setInstructions("You are a customer support agent.")
    .setDescription("Handles customer inquiries")
    .setTemperature(0.7)
    .setTopP(0.9);

PersistentAgent agent = client.createAgent(options);
```

### 3.3 ✅ CORRECT: Create Agent with Tools
```java
import java.util.Arrays;
import java.util.Map;
import com.azure.core.util.BinaryData;

ToolDefinition codeInterpreter = new CodeInterpreterToolDefinition();

FunctionDefinition funcDef = new FunctionDefinition("get_weather")
    .setDescription("Get weather for a location")
    .setParameters(BinaryData.fromObject(Map.of(
        "type", "object",
        "properties", Map.of(
            "location", Map.of("type", "string", "description", "City name")
        ),
        "required", new String[]{"location"}
    )));

ToolDefinition functionTool = new FunctionToolDefinition(funcDef);

CreateAgentOptions options = new CreateAgentOptions(modelDeploymentName)
    .setName("Assistant with Tools")
    .setInstructions("You can run code and check weather.")
    .setTools(Arrays.asList(codeInterpreter, functionTool));

PersistentAgent agent = client.createAgent(options);
```

### 3.4 ✅ CORRECT: List, Get, Update, Delete Agents
```java
// List agents
PagedIterable<PersistentAgent> agents = client.listAgents();
for (PersistentAgent a : agents) {
    System.out.println(a.getName());
}

// Get agent
PersistentAgent agent = client.getAgent(agentId);

// Update agent
UpdateAgentOptions updateOptions = new UpdateAgentOptions()
    .setName("Updated Name")
    .setInstructions("Updated instructions");
PersistentAgent updated = client.updateAgent(agentId, updateOptions);

// Delete agent
client.deleteAgent(agentId);
```

### 3.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong method signatures
```java
// WRONG - createAgentVersion doesn't exist in persistent SDK
client.createAgentVersion("name", definition);

// WRONG - missing required parameter
client.createAgent(options);  // Without model when using simple method
```

---

## 4. Thread Operations

### 4.1 ✅ CORRECT: Create Thread
```java
PersistentAgentThread thread = client.createThread();
System.out.println("Thread ID: " + thread.getId());
```

### 4.2 ✅ CORRECT: Create Thread with Options
```java
ThreadMessageOptions initialMessage = new ThreadMessageOptions(
    MessageRole.USER,
    "Hello, I need help with calculus."
);

CreateThreadOptions threadOptions = new CreateThreadOptions()
    .setMessages(Arrays.asList(initialMessage))
    .setMetadata(Map.of("user_id", "user123"));

PersistentAgentThread thread = client.createThread(threadOptions);
```

### 4.3 ✅ CORRECT: Get, Update, Delete Thread
```java
// Get thread
PersistentAgentThread thread = client.getThread(threadId);

// Update thread
UpdateThreadOptions updateOptions = new UpdateThreadOptions()
    .setMetadata(Map.of("status", "resolved"));
PersistentAgentThread updated = client.updateThread(threadId, updateOptions);

// Delete thread
client.deleteThread(threadId);
```

### 4.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong class names
```java
// WRONG - class is PersistentAgentThread, not Thread
Thread thread = client.createThread();

// WRONG - threads.create() doesn't exist
client.threads.create();
```

---

## 5. Message Operations

### 5.1 ✅ CORRECT: Create Message (Simple)
```java
PersistentThreadMessage message = client.createMessage(
    threadId,
    MessageRole.USER,
    "What is the derivative of x squared?"
);
```

### 5.2 ✅ CORRECT: Create Message with Attachments
```java
// Upload file
AgentFile file = client.uploadFile(
    BinaryData.fromFile(new File("data.csv").toPath()),
    AgentFilePurpose.AGENTS
);

MessageAttachment attachment = new MessageAttachment(file.getId())
    .setTools(Arrays.asList(new CodeInterpreterToolDefinition()));

CreateMessageOptions options = new CreateMessageOptions(MessageRole.USER, "Analyze this data")
    .setAttachments(Arrays.asList(attachment));

PersistentThreadMessage message = client.createMessage(threadId, options);
```

### 5.3 ✅ CORRECT: List Messages
```java
PagedIterable<PersistentThreadMessage> messages = client.listMessages(threadId);

for (PersistentThreadMessage msg : messages) {
    String role = msg.getRole().toString();
    for (MessageContent content : msg.getContent()) {
        if (content instanceof MessageTextContent) {
            String text = ((MessageTextContent) content).getText().getValue();
            System.out.printf("[%s]: %s%n", role, text);
        }
    }
}
```

### 5.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong role values
```java
// WRONG - role is not "human"
client.createMessage(threadId, MessageRole.HUMAN, "Hello");

// WRONG - using string instead of enum
client.createMessage(threadId, "user", "Hello");
```

---

## 6. Run Operations

### 6.1 ✅ CORRECT: Create and Poll Run
```java
ThreadRun run = client.createRun(threadId, agentId);

// Poll until completion
while (run.getStatus() == RunStatus.QUEUED || run.getStatus() == RunStatus.IN_PROGRESS) {
    Thread.sleep(500);  // Wait 500ms
    run = client.getRun(threadId, run.getId());
    System.out.println("Status: " + run.getStatus());
}

// Check final status
if (run.getStatus() == RunStatus.COMPLETED) {
    System.out.println("Run completed successfully!");
} else if (run.getStatus() == RunStatus.FAILED) {
    System.err.println("Run failed: " + run.getLastError().getMessage());
}
```

### 6.2 ✅ CORRECT: Create Run with Options
```java
CreateRunOptions options = new CreateRunOptions(agentId)
    .setAdditionalInstructions("Be very detailed.")
    .setTemperature(0.5);

ThreadRun run = client.createRun(threadId, options);
```

### 6.3 ✅ CORRECT: Handle Tool Calls
```java
if (run.getStatus() == RunStatus.REQUIRES_ACTION) {
    RequiredAction requiredAction = run.getRequiredAction();
    
    if (requiredAction instanceof SubmitToolOutputsAction) {
        SubmitToolOutputsAction submitAction = (SubmitToolOutputsAction) requiredAction;
        List<RequiredToolCall> toolCalls = submitAction.getSubmitToolOutputs().getToolCalls();
        
        List<ToolOutput> outputs = new ArrayList<>();
        
        for (RequiredToolCall toolCall : toolCalls) {
            if (toolCall instanceof RequiredFunctionToolCall) {
                RequiredFunctionToolCall funcCall = (RequiredFunctionToolCall) toolCall;
                String functionName = funcCall.getFunction().getName();
                String arguments = funcCall.getFunction().getArguments();
                
                // Execute function and get result
                String result = executeFunction(functionName, arguments);
                outputs.add(new ToolOutput(toolCall.getId(), result));
            }
        }
        
        // Submit tool outputs
        run = client.submitToolOutputsToRun(threadId, run.getId(), outputs);
    }
}
```

### 6.4 ✅ CORRECT: List Runs and Run Steps
```java
// List runs
PagedIterable<ThreadRun> runs = client.listRuns(threadId);
for (ThreadRun r : runs) {
    System.out.printf("Run %s: %s%n", r.getId(), r.getStatus());
}

// List run steps
PagedIterable<RunStep> steps = client.listRunSteps(threadId, runId);
for (RunStep step : steps) {
    System.out.printf("Step %s: %s%n", step.getId(), step.getStatus());
}

// Cancel run
ThreadRun cancelled = client.cancelRun(threadId, runId);
```

### 6.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong status checks
```java
// WRONG - using string comparison
if (run.getStatus().equals("completed")) { ... }

// WRONG - not polling, assuming immediate completion
ThreadRun run = client.createRun(threadId, agentId);
// Immediately accessing messages without checking status
```

---

## 7. Streaming

### 7.1 ✅ CORRECT: Stream Run Events
```java
client.createRunStream(threadId, agentId)
    .forEach(event -> {
        if (event instanceof ThreadRunCreatedEvent) {
            System.out.println("Run started");
        } else if (event instanceof ThreadMessageDeltaEvent) {
            ThreadMessageDeltaEvent delta = (ThreadMessageDeltaEvent) event;
            for (MessageDeltaContent content : delta.getDelta().getContent()) {
                if (content instanceof MessageDeltaTextContent) {
                    String text = ((MessageDeltaTextContent) content).getText().getValue();
                    System.out.print(text);
                }
            }
        } else if (event instanceof ThreadRunCompletedEvent) {
            System.out.println("\nRun completed");
        }
    });
```

### 7.2 ✅ CORRECT: Async Streaming
```java
asyncClient.createRunStream(threadId, agentId)
    .subscribe(
        event -> handleStreamEvent(event),
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Stream completed")
    );
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-streaming methods for streaming
```java
// WRONG - createRun doesn't return a stream
for (var event : client.createRun(threadId, agentId)) { ... }
```

---

## 8. File and Vector Store Operations

### 8.1 ✅ CORRECT: Upload File
```java
import java.io.File;
import com.azure.core.util.BinaryData;

File file = new File("data.csv");
AgentFile uploadedFile = client.uploadFile(
    BinaryData.fromFile(file.toPath()),
    AgentFilePurpose.AGENTS
);

System.out.println("File ID: " + uploadedFile.getId());
System.out.println("Filename: " + uploadedFile.getFilename());
```

### 8.2 ✅ CORRECT: Create Vector Store
```java
VectorStore vectorStore = client.createVectorStore(
    new CreateVectorStoreOptions().setName("Knowledge Base")
);

// Upload files to vector store
client.uploadFileToVectorStore(
    vectorStore.getId(),
    BinaryData.fromFile(new File("document.pdf").toPath())
);
```

### 8.3 ✅ CORRECT: Agent with File Search
```java
CreateAgentOptions options = new CreateAgentOptions(modelDeploymentName)
    .setName("Research Assistant")
    .setInstructions("Search documents to answer questions.")
    .setTools(Arrays.asList(new FileSearchToolDefinition()))
    .setToolResources(new ToolResources()
        .setFileSearch(new FileSearchToolResource()
            .setVectorStoreIds(Arrays.asList(vectorStore.getId()))));

PersistentAgent agent = client.createAgent(options);
```

### 8.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong file purpose
```java
// WRONG - using non-existent purpose
client.uploadFile(data, AgentFilePurpose.ASSISTANTS);

// WRONG - direct file path without BinaryData
client.uploadFile("data.csv", AgentFilePurpose.AGENTS);
```

---

## 9. Error Handling

### 9.1 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    PersistentAgent agent = client.createAgent(
        modelDeploymentName, "Test Agent", "Test instructions");
} catch (HttpResponseException e) {
    int statusCode = e.getResponse().getStatusCode();
    System.err.println("HTTP Status: " + statusCode);
    System.err.println("Error: " + e.getMessage());
    
    switch (statusCode) {
        case 400: System.err.println("Bad request"); break;
        case 401: System.err.println("Unauthorized"); break;
        case 404: System.err.println("Not found"); break;
        case 429: System.err.println("Rate limited"); break;
    }
}
```

### 9.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Empty catch blocks
```java
// WRONG - swallowing exceptions
try {
    client.createAgent(model, name, instructions);
} catch (Exception e) {
    // Do nothing
}
```

---

## 10. Best Practices Checklist

- [ ] Use `DefaultAzureCredentialBuilder` for production authentication
- [ ] Use environment variables for endpoint and model configuration
- [ ] Poll with appropriate delays (500ms recommended)
- [ ] Clean up resources — delete threads and agents when done
- [ ] Handle all run statuses — `REQUIRES_ACTION`, `FAILED`, `CANCELLED`, `EXPIRED`
- [ ] Use async client for better throughput in high-concurrency scenarios
- [ ] Implement retry logic for transient errors
- [ ] Use streaming for long responses to improve UX
- [ ] Store agent IDs — reuse agents across sessions instead of recreating
- [ ] Close file streams and handle resources properly
