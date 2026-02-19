# Azure AI Agents Persistent Java SDK - Examples

Comprehensive code examples for the Azure AI Agents Persistent SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Agent Operations](#agent-operations)
- [Thread Operations](#thread-operations)
- [Message Operations](#message-operations)
- [Run Operations](#run-operations)
- [Streaming Responses](#streaming-responses)
- [Tools Integration](#tools-integration)
- [File Operations](#file-operations)
- [Error Handling](#error-handling)
- [Complete Application Example](#complete-application-example)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-agents-persistent</artifactId>
    <version>1.0.0-beta.1</version>
</dependency>

<!-- For DefaultAzureCredential -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.14.2</version>
</dependency>
```

## Client Creation

### With DefaultAzureCredential (Recommended)

```java
import com.azure.ai.agents.persistent.PersistentAgentsClient;
import com.azure.ai.agents.persistent.PersistentAgentsClientBuilder;
import com.azure.identity.DefaultAzureCredentialBuilder;

String endpoint = System.getenv("PROJECT_ENDPOINT");

PersistentAgentsClient client = new PersistentAgentsClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### Async Client

```java
import com.azure.ai.agents.persistent.PersistentAgentsAsyncClient;

PersistentAgentsAsyncClient asyncClient = new PersistentAgentsClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

## Agent Operations

### Create Agent

```java
import com.azure.ai.agents.persistent.models.*;

String modelDeploymentName = System.getenv("MODEL_DEPLOYMENT_NAME");

PersistentAgent agent = client.createAgent(
    modelDeploymentName,
    "Math Tutor",                                    // Name
    "You are a personal math tutor. Help students understand mathematical concepts." // Instructions
);

System.out.println("Agent created:");
System.out.println("  ID: " + agent.getId());
System.out.println("  Name: " + agent.getName());
System.out.println("  Model: " + agent.getModel());
```

### Create Agent with Configuration

```java
CreateAgentOptions options = new CreateAgentOptions(modelDeploymentName)
    .setName("Customer Support Agent")
    .setInstructions("You are a customer support agent. Help users with their questions politely.")
    .setDescription("Handles customer inquiries")
    .setTemperature(0.7)
    .setTopP(0.9);

PersistentAgent agent = client.createAgent(options);
```

### Create Agent with Tools

```java
import java.util.Arrays;
import java.util.Map;

// Code Interpreter tool
ToolDefinition codeInterpreter = new CodeInterpreterToolDefinition();

// Function tool
FunctionDefinition functionDef = new FunctionDefinition("get_weather")
    .setDescription("Get current weather for a location")
    .setParameters(BinaryData.fromObject(Map.of(
        "type", "object",
        "properties", Map.of(
            "location", Map.of(
                "type", "string",
                "description", "City name"
            )
        ),
        "required", new String[]{"location"}
    )));

ToolDefinition functionTool = new FunctionToolDefinition(functionDef);

CreateAgentOptions options = new CreateAgentOptions(modelDeploymentName)
    .setName("Assistant with Tools")
    .setInstructions("You can run code and check weather.")
    .setTools(Arrays.asList(codeInterpreter, functionTool));

PersistentAgent agent = client.createAgent(options);
```

### Get Agent

```java
PersistentAgent agent = client.getAgent(agentId);

System.out.println("Agent: " + agent.getName());
System.out.println("Instructions: " + agent.getInstructions());
System.out.println("Tools: " + agent.getTools().size());
```

### List Agents

```java
import com.azure.core.http.rest.PagedIterable;

PagedIterable<PersistentAgent> agents = client.listAgents();

System.out.println("=== Available Agents ===");
for (PersistentAgent a : agents) {
    System.out.printf("%s: %s%n", a.getId(), a.getName());
}
```

### Update Agent

```java
UpdateAgentOptions updateOptions = new UpdateAgentOptions()
    .setName("Updated Agent Name")
    .setInstructions("Updated instructions for the agent.");

PersistentAgent updated = client.updateAgent(agentId, updateOptions);
System.out.println("Agent updated: " + updated.getName());
```

### Delete Agent

```java
client.deleteAgent(agentId);
System.out.println("Agent deleted: " + agentId);
```

## Thread Operations

### Create Thread

```java
PersistentAgentThread thread = client.createThread();

System.out.println("Thread created: " + thread.getId());
```

### Create Thread with Initial Messages

```java
import java.util.Arrays;

ThreadMessageOptions initialMessage = new ThreadMessageOptions(
    MessageRole.USER,
    "Hello, I need help with calculus."
);

CreateThreadOptions threadOptions = new CreateThreadOptions()
    .setMessages(Arrays.asList(initialMessage));

PersistentAgentThread thread = client.createThread(threadOptions);
```

### Create Thread with Metadata

```java
import java.util.Map;

CreateThreadOptions options = new CreateThreadOptions()
    .setMetadata(Map.of(
        "user_id", "user123",
        "session_type", "support"
    ));

PersistentAgentThread thread = client.createThread(options);
```

### Get Thread

```java
PersistentAgentThread thread = client.getThread(threadId);

System.out.println("Thread: " + thread.getId());
System.out.println("Created: " + thread.getCreatedAt());
System.out.println("Metadata: " + thread.getMetadata());
```

### Update Thread

```java
UpdateThreadOptions updateOptions = new UpdateThreadOptions()
    .setMetadata(Map.of("status", "resolved"));

PersistentAgentThread updated = client.updateThread(threadId, updateOptions);
```

### Delete Thread

```java
client.deleteThread(threadId);
System.out.println("Thread deleted: " + threadId);
```

## Message Operations

### Create Message

```java
PersistentThreadMessage message = client.createMessage(
    threadId,
    MessageRole.USER,
    "What is the derivative of x squared?"
);

System.out.println("Message created: " + message.getId());
```

### Create Message with Attachments

```java
// First upload a file
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

### List Messages

```java
PagedIterable<PersistentThreadMessage> messages = client.listMessages(threadId);

System.out.println("=== Conversation ===");
for (PersistentThreadMessage msg : messages) {
    String role = msg.getRole().toString();
    String content = extractTextContent(msg);
    System.out.printf("[%s]: %s%n", role, content);
}

private String extractTextContent(PersistentThreadMessage message) {
    StringBuilder text = new StringBuilder();
    for (MessageContent content : message.getContent()) {
        if (content instanceof MessageTextContent) {
            text.append(((MessageTextContent) content).getText().getValue());
        }
    }
    return text.toString();
}
```

### Get Message

```java
PersistentThreadMessage message = client.getMessage(threadId, messageId);

System.out.println("Message role: " + message.getRole());
System.out.println("Created: " + message.getCreatedAt());
```

## Run Operations

### Create Run

```java
ThreadRun run = client.createRun(threadId, agentId);

System.out.println("Run created: " + run.getId());
System.out.println("Status: " + run.getStatus());
```

### Create Run with Additional Instructions

```java
CreateRunOptions options = new CreateRunOptions(agentId)
    .setAdditionalInstructions("Please be very detailed in your response.")
    .setTemperature(0.5);

ThreadRun run = client.createRun(threadId, options);
```

### Poll for Run Completion

```java
ThreadRun run = client.createRun(threadId, agentId);

// Poll until completion
while (run.getStatus() == RunStatus.QUEUED || run.getStatus() == RunStatus.IN_PROGRESS) {
    Thread.sleep(500);  // Wait 500ms between polls
    run = client.getRun(threadId, run.getId());
    System.out.println("Status: " + run.getStatus());
}

// Check final status
switch (run.getStatus()) {
    case COMPLETED:
        System.out.println("Run completed successfully!");
        break;
    case FAILED:
        System.err.println("Run failed: " + run.getLastError().getMessage());
        break;
    case CANCELLED:
        System.out.println("Run was cancelled");
        break;
    case EXPIRED:
        System.out.println("Run expired");
        break;
    case REQUIRES_ACTION:
        System.out.println("Run requires action (tool calls)");
        handleRequiredActions(run);
        break;
}
```

### Handle Tool Calls

```java
private void handleRequiredActions(ThreadRun run) {
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
                
                // Execute function
                String result = executeFunction(functionName, arguments);
                
                outputs.add(new ToolOutput(toolCall.getId(), result));
            }
        }
        
        // Submit tool outputs
        run = client.submitToolOutputsToRun(threadId, run.getId(), outputs);
    }
}

private String executeFunction(String name, String arguments) {
    if ("get_weather".equals(name)) {
        // Parse arguments and call weather API
        return "{\"temperature\": 72, \"condition\": \"sunny\"}";
    }
    return "{\"error\": \"Unknown function\"}";
}
```

### Cancel Run

```java
ThreadRun cancelled = client.cancelRun(threadId, runId);
System.out.println("Run cancelled: " + cancelled.getStatus());
```

### List Runs

```java
PagedIterable<ThreadRun> runs = client.listRuns(threadId);

for (ThreadRun r : runs) {
    System.out.printf("Run %s: %s%n", r.getId(), r.getStatus());
}
```

### List Run Steps

```java
PagedIterable<RunStep> steps = client.listRunSteps(threadId, runId);

System.out.println("=== Run Steps ===");
for (RunStep step : steps) {
    System.out.printf("Step %s: %s - %s%n",
        step.getId(),
        step.getType(),
        step.getStatus());
}
```

## Streaming Responses

### Stream Run with Event Handler

```java
import com.azure.ai.agents.persistent.models.streaming.*;

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

### Stream with Async Client

```java
asyncClient.createRunStream(threadId, agentId)
    .subscribe(
        event -> handleStreamEvent(event),
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Stream completed")
    );
```

## Tools Integration

### Code Interpreter

```java
// Create agent with code interpreter
CreateAgentOptions options = new CreateAgentOptions(modelDeploymentName)
    .setName("Code Assistant")
    .setInstructions("You can write and run Python code to help users.")
    .setTools(Arrays.asList(new CodeInterpreterToolDefinition()));

PersistentAgent agent = client.createAgent(options);

// Create thread and message
PersistentAgentThread thread = client.createThread();
client.createMessage(thread.getId(), MessageRole.USER, 
    "Calculate the first 10 Fibonacci numbers");

// Run and wait
ThreadRun run = client.createRun(thread.getId(), agent.getId());
while (run.getStatus() == RunStatus.QUEUED || run.getStatus() == RunStatus.IN_PROGRESS) {
    Thread.sleep(500);
    run = client.getRun(thread.getId(), run.getId());
}

// Get response with code output
PagedIterable<PersistentThreadMessage> messages = client.listMessages(thread.getId());
for (PersistentThreadMessage msg : messages) {
    if (msg.getRole() == MessageRole.ASSISTANT) {
        for (MessageContent content : msg.getContent()) {
            if (content instanceof MessageTextContent) {
                System.out.println(((MessageTextContent) content).getText().getValue());
            }
        }
    }
}
```

### File Search

```java
// Create vector store
VectorStore vectorStore = client.createVectorStore(
    new CreateVectorStoreOptions().setName("Knowledge Base")
);

// Upload files to vector store
client.uploadFileToVectorStore(vectorStore.getId(), 
    BinaryData.fromFile(new File("document.pdf").toPath()));

// Create agent with file search
CreateAgentOptions options = new CreateAgentOptions(modelDeploymentName)
    .setName("Research Assistant")
    .setInstructions("Search the uploaded documents to answer questions.")
    .setTools(Arrays.asList(new FileSearchToolDefinition()))
    .setToolResources(new ToolResources()
        .setFileSearch(new FileSearchToolResource()
            .setVectorStoreIds(Arrays.asList(vectorStore.getId()))));

PersistentAgent agent = client.createAgent(options);
```

## File Operations

### Upload File

```java
import java.io.File;

File file = new File("data.csv");
AgentFile uploadedFile = client.uploadFile(
    BinaryData.fromFile(file.toPath()),
    AgentFilePurpose.AGENTS
);

System.out.println("File uploaded: " + uploadedFile.getId());
System.out.println("Filename: " + uploadedFile.getFilename());
System.out.println("Size: " + uploadedFile.getBytes() + " bytes");
```

### List Files

```java
PagedIterable<AgentFile> files = client.listFiles();

for (AgentFile file : files) {
    System.out.printf("%s: %s (%d bytes)%n",
        file.getId(),
        file.getFilename(),
        file.getBytes());
}
```

### Delete File

```java
client.deleteFile(fileId);
System.out.println("File deleted: " + fileId);
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    PersistentAgent agent = client.createAgent(
        modelDeploymentName,
        "Test Agent",
        "Test instructions"
    );
} catch (HttpResponseException e) {
    int statusCode = e.getResponse().getStatusCode();
    
    System.err.println("HTTP Status: " + statusCode);
    System.err.println("Error: " + e.getMessage());
    
    switch (statusCode) {
        case 400:
            System.err.println("Bad request - check parameters");
            break;
        case 401:
            System.err.println("Unauthorized - check credentials");
            break;
        case 404:
            System.err.println("Resource not found");
            break;
        case 429:
            System.err.println("Rate limited - retry with backoff");
            break;
        default:
            System.err.println("Unexpected error");
    }
} catch (Exception e) {
    System.err.println("Unexpected error: " + e.getMessage());
}
```

## Complete Application Example

```java
import com.azure.ai.agents.persistent.PersistentAgentsClient;
import com.azure.ai.agents.persistent.PersistentAgentsClientBuilder;
import com.azure.ai.agents.persistent.models.*;
import com.azure.core.http.rest.PagedIterable;
import com.azure.identity.DefaultAzureCredentialBuilder;

import java.util.*;

public class MathTutorBot {
    
    private final PersistentAgentsClient client;
    private final String modelDeploymentName;
    private PersistentAgent agent;
    
    public MathTutorBot() {
        this.client = new PersistentAgentsClientBuilder()
            .endpoint(System.getenv("PROJECT_ENDPOINT"))
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildClient();
        this.modelDeploymentName = System.getenv("MODEL_DEPLOYMENT_NAME");
    }
    
    public void initialize() {
        // Create agent with code interpreter for math calculations
        CreateAgentOptions options = new CreateAgentOptions(modelDeploymentName)
            .setName("Math Tutor")
            .setInstructions("""
                You are a friendly math tutor. Help students understand mathematical concepts.
                - Explain concepts clearly step by step
                - Use Python code to demonstrate calculations
                - Encourage students and be patient
                - Ask clarifying questions if needed
                """)
            .setTools(Arrays.asList(new CodeInterpreterToolDefinition()))
            .setTemperature(0.7);
        
        this.agent = client.createAgent(options);
        System.out.println("Math Tutor initialized: " + agent.getId());
    }
    
    public String chat(String threadId, String userMessage) {
        // Create message
        client.createMessage(threadId, MessageRole.USER, userMessage);
        
        // Create and wait for run
        ThreadRun run = client.createRun(threadId, agent.getId());
        run = waitForCompletion(threadId, run.getId());
        
        if (run.getStatus() != RunStatus.COMPLETED) {
            return "I encountered an error. Please try again.";
        }
        
        // Get assistant response
        return getLatestAssistantMessage(threadId);
    }
    
    private ThreadRun waitForCompletion(String threadId, String runId) {
        ThreadRun run;
        do {
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            run = client.getRun(threadId, runId);
        } while (run.getStatus() == RunStatus.QUEUED || run.getStatus() == RunStatus.IN_PROGRESS);
        
        return run;
    }
    
    private String getLatestAssistantMessage(String threadId) {
        PagedIterable<PersistentThreadMessage> messages = client.listMessages(threadId);
        
        for (PersistentThreadMessage msg : messages) {
            if (msg.getRole() == MessageRole.ASSISTANT) {
                StringBuilder response = new StringBuilder();
                for (MessageContent content : msg.getContent()) {
                    if (content instanceof MessageTextContent) {
                        response.append(((MessageTextContent) content).getText().getValue());
                    }
                }
                return response.toString();
            }
        }
        
        return "No response available.";
    }
    
    public String createConversation() {
        PersistentAgentThread thread = client.createThread();
        return thread.getId();
    }
    
    public void cleanup(String threadId) {
        try {
            client.deleteThread(threadId);
        } catch (Exception e) {
            System.err.println("Failed to delete thread: " + e.getMessage());
        }
    }
    
    public void shutdown() {
        if (agent != null) {
            try {
                client.deleteAgent(agent.getId());
                System.out.println("Agent cleaned up");
            } catch (Exception e) {
                System.err.println("Failed to delete agent: " + e.getMessage());
            }
        }
    }
    
    public static void main(String[] args) {
        MathTutorBot bot = new MathTutorBot();
        
        try {
            // Initialize
            bot.initialize();
            
            // Create conversation
            String threadId = bot.createConversation();
            System.out.println("Conversation started: " + threadId);
            
            // Chat
            Scanner scanner = new Scanner(System.in);
            System.out.println("\nMath Tutor ready! Type 'quit' to exit.\n");
            
            while (true) {
                System.out.print("You: ");
                String input = scanner.nextLine().trim();
                
                if ("quit".equalsIgnoreCase(input)) {
                    break;
                }
                
                if (input.isEmpty()) {
                    continue;
                }
                
                String response = bot.chat(threadId, input);
                System.out.println("\nTutor: " + response + "\n");
            }
            
            // Cleanup
            bot.cleanup(threadId);
            
        } finally {
            bot.shutdown();
        }
    }
}
```

## Environment Variables

```bash
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# For DefaultAzureCredential
AZURE_CLIENT_ID=<service-principal-client-id>
AZURE_CLIENT_SECRET=<service-principal-secret>
AZURE_TENANT_ID=<tenant-id>
```

## Best Practices

1. **Use DefaultAzureCredential** — Prefer managed identity over API keys in production
2. **Poll with appropriate delays** — 500ms between status checks is recommended
3. **Clean up resources** — Delete threads and agents when no longer needed
4. **Handle all run statuses** — Check for `REQUIRES_ACTION`, `FAILED`, `CANCELLED`, `EXPIRED`
5. **Use async client** — For better throughput in high-concurrency scenarios
6. **Implement retry logic** — Handle transient errors with exponential backoff
7. **Stream for long responses** — Use streaming for better user experience
8. **Store agent IDs** — Reuse agents across sessions instead of recreating
