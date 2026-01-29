# Azure AI Agents Java SDK - Examples

Comprehensive code examples for the Azure AI Agents SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Setup](#client-setup)
- [Agent CRUD Operations](#agent-crud-operations)
- [Conversation Management](#conversation-management)
- [Creating Responses](#creating-responses)
- [Complete Workflow](#complete-workflow)

---

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-agents</artifactId>
    <version>1.0.0-beta.1</version>
</dependency>

<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.15.3</version>
</dependency>
```

---

## Client Setup

### Creating Clients with DefaultAzureCredential

```java
import com.azure.ai.agents.*;
import com.azure.identity.DefaultAzureCredentialBuilder;

public class ClientSetup {
    public static void main(String[] args) {
        String endpoint = System.getenv("AZURE_AGENTS_ENDPOINT");
        
        // Create the builder (reusable for all sub-clients)
        AgentsClientBuilder builder = new AgentsClientBuilder()
            .credential(new DefaultAzureCredentialBuilder().build())
            .endpoint(endpoint)
            .serviceVersion(AgentsServiceVersion.V2025_05_15_PREVIEW);
        
        // Build different sub-clients from the same builder
        AgentsClient agentsClient = builder.buildAgentsClient();
        AgentsAsyncClient agentsAsyncClient = builder.buildAsyncClient();
        
        ConversationsClient conversationsClient = builder.buildConversationsClient();
        ConversationsAsyncClient conversationsAsyncClient = builder.buildConversationsAsyncClient();
        
        ResponsesClient responsesClient = builder.buildResponsesClient();
        ResponsesAsyncClient responsesAsyncClient = builder.buildResponsesAsyncClient();
        
        MemoryStoresClient memoryStoresClient = builder.buildMemoryStoresClient();
    }
}
```

---

## Agent CRUD Operations

### Create an Agent

```java
import com.azure.ai.agents.models.AgentVersionDetails;
import com.azure.ai.agents.models.PromptAgentDefinition;
import com.azure.identity.DefaultAzureCredentialBuilder;

public class CreateAgent {
    public static void main(String[] args) {
        String endpoint = System.getenv("AZURE_AGENTS_ENDPOINT");
        String model = System.getenv("AZURE_AGENT_MODEL"); // e.g., "gpt-4o"
        
        AgentsClient agentsClient = new AgentsClientBuilder()
            .credential(new DefaultAzureCredentialBuilder().build())
            .endpoint(endpoint)
            .buildAgentsClient();

        // Create a PromptAgentDefinition with the model
        PromptAgentDefinition request = new PromptAgentDefinition(model);
        
        // Create a versioned agent
        AgentVersionDetails agent = agentsClient.createAgentVersion("my-agent-name", request);

        System.out.println("Agent ID: " + agent.getId());
        System.out.println("Agent Name: " + agent.getName());
        System.out.println("Agent Version: " + agent.getVersion());
    }
}
```

### Get an Agent

```java
import com.azure.ai.agents.models.AgentDetails;

AgentDetails agent = agentsClient.getAgent("my-agent-name");

System.out.println("Agent ID: " + agent.getId());
System.out.println("Agent Name: " + agent.getName());
System.out.println("Agent Version: " + agent.getVersions().getLatest());
```

### List All Agents

```java
System.out.println("Listing all agents:");
for (AgentDetails agent : agentsClient.listAgents()) {
    System.out.println("Agent ID: " + agent.getId());
    System.out.println("Agent Name: " + agent.getName());
    if (agent.getVersions() != null && agent.getVersions().getLatest() != null) {
        System.out.println("Latest Version ID: " + agent.getVersions().getLatest().getId());
    }
    System.out.println("---");
}
```

### Delete an Agent

```java
import com.azure.ai.agents.models.DeleteAgentResponse;
import com.azure.ai.agents.models.DeleteAgentVersionResponse;

// Delete a specific version
DeleteAgentVersionResponse deletedVersion = agentsClient.deleteAgentVersion("my-agent-name", "1");
System.out.println("Deleted version: " + deletedVersion.getVersion());
System.out.println("Is deleted: " + deletedVersion.isDeleted());

// Delete the entire agent (all versions)
DeleteAgentResponse deletedAgent = agentsClient.deleteAgent("my-agent-name");
System.out.println("Deleted agent: " + deletedAgent.getName());
System.out.println("Is deleted: " + deletedAgent.isDeleted());
```

---

## Conversation Management

### Create a Conversation

```java
import com.openai.models.conversations.Conversation;

Conversation conversation = conversationsClient.getConversationService().create();

System.out.println("Conversation ID: " + conversation.id());
System.out.println("Conversation Created At: " + conversation.createdAt());
```

### Add Messages to a Conversation

```java
import com.openai.models.conversations.items.ConversationItemList;
import com.openai.models.conversations.items.ItemCreateParams;
import com.openai.models.responses.EasyInputMessage;

// Create a conversation first
Conversation conversation = conversationsClient.getConversationService().create();
String conversationId = conversation.id();

// Add multiple messages at once
ConversationItemList items = conversationsClient.getConversationService().items().create(
    ItemCreateParams.builder()
        .conversationId(conversationId)
        .addItem(EasyInputMessage.builder()
            .role(EasyInputMessage.Role.SYSTEM)
            .content("You are a helpful assistant that speaks like a pirate.")
            .build()
        )
        .addItem(EasyInputMessage.builder()
            .role(EasyInputMessage.Role.USER)
            .content("Hello, agent!")
            .build()
        )
        .build()
);

System.out.println("Added " + items.data().size() + " messages to conversation");
```

### Update Conversation Metadata

```java
import com.openai.core.JsonValue;
import com.openai.models.conversations.ConversationUpdateParams;

ConversationUpdateParams.Metadata metadata = ConversationUpdateParams.Metadata.builder()
    .putAdditionalProperty("updated_by", JsonValue.from("java_sample"))
    .putAdditionalProperty("update_timestamp", JsonValue.from(System.currentTimeMillis()))
    .build();

ConversationUpdateParams updateParams = ConversationUpdateParams.builder()
    .metadata(metadata)
    .build();

Conversation updatedConversation = conversationsClient.getConversationService()
    .update(conversationId, updateParams);

System.out.println("Updated Conversation ID: " + updatedConversation.id());
```

---

## Creating Responses

### Basic Response Creation

```java
import com.openai.models.responses.Response;
import com.openai.models.responses.ResponseCreateParams;

ResponseCreateParams responseRequest = new ResponseCreateParams.Builder()
    .input("Hello, how can you help me?")
    .model(model)
    .build();

Response response = responsesClient.getResponseService().create(responseRequest);

System.out.println("Response ID: " + response.id());
System.out.println("Response Model: " + response.model());
System.out.println("Response Created At: " + response.createdAt());
System.out.println("Response Output: " + response.output());
```

---

## Complete Workflow

### Agent with Conversation and Response

```java
import com.azure.ai.agents.*;
import com.azure.ai.agents.models.*;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.openai.models.conversations.Conversation;
import com.openai.models.conversations.items.ItemCreateParams;
import com.openai.models.responses.EasyInputMessage;
import com.openai.models.responses.Response;
import com.openai.models.responses.ResponseCreateParams;

public class CompleteWorkflow {
    public static void main(String[] args) {
        String endpoint = System.getenv("AZURE_AGENTS_ENDPOINT");
        String model = System.getenv("AZURE_AGENT_MODEL");
        
        AgentsClientBuilder builder = new AgentsClientBuilder()
            .credential(new DefaultAzureCredentialBuilder().build())
            .endpoint(endpoint);
        
        AgentsClient agentsClient = builder.buildAgentsClient();
        ConversationsClient conversationsClient = builder.buildConversationsClient();
        ResponsesClient responsesClient = builder.buildResponsesClient();

        // 1. Create an agent
        PromptAgentDefinition promptAgentDefinition = new PromptAgentDefinition(model);
        AgentVersionDetails agent = agentsClient.createAgentVersion("workflow-agent", promptAgentDefinition);
        System.out.println("Created agent: " + agent.getName());

        // 2. Create a conversation
        Conversation conversation = conversationsClient.getConversationService().create();
        System.out.println("Created conversation: " + conversation.id());

        // 3. Add messages
        conversationsClient.getConversationService().items().create(
            ItemCreateParams.builder()
                .conversationId(conversation.id())
                .addItem(EasyInputMessage.builder()
                    .role(EasyInputMessage.Role.USER)
                    .content("What is the capital of France?")
                    .build())
                .build()
        );

        // 4. Get response
        ResponseCreateParams responseRequest = new ResponseCreateParams.Builder()
            .input("What is the capital of France?")
            .model(model)
            .build();
        
        Response response = responsesClient.getResponseService().create(responseRequest);
        System.out.println("Response: " + response.output());

        // 5. Cleanup
        agentsClient.deleteAgent("workflow-agent");
        System.out.println("Deleted agent");
    }
}
```
