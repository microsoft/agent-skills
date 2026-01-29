---
name: agents-java
description: |
  Azure AI Agents SDK for Java. Develop agents using Azure AI Foundry with models, tools, and capabilities from OpenAI and other providers.
  Triggers: "AgentsClient", "azure agents java", "PromptAgent", "ConversationsClient", "ResponsesClient", "agent conversations java".
---

# Azure AI Agents SDK for Java

Develop agents using Azure AI Foundry with an extensive ecosystem of models, tools, and capabilities.

## Installation

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-agents</artifactId>
    <version>1.0.0-beta.1</version>
</dependency>
```

## Environment Variables

```bash
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

## Authentication

```java
import com.azure.ai.agents.AgentsClient;
import com.azure.ai.agents.AgentsClientBuilder;
import com.azure.identity.DefaultAzureCredentialBuilder;

String endpoint = System.getenv("PROJECT_ENDPOINT");
AgentsClient agentsClient = new AgentsClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

## Client Hierarchy

The SDK provides three main sub-clients:

| Client | Purpose |
|--------|---------|
| `AgentsClient` / `AgentsAsyncClient` | Agent CRUD operations |
| `ConversationsClient` / `ConversationsAsyncClient` | Conversation management |
| `ResponsesClient` / `ResponsesAsyncClient` | Response generation |

```java
AgentsClientBuilder builder = new AgentsClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint);

// Build sub-clients
AgentsClient agentsClient = builder.buildClient();
ConversationsClient conversationsClient = builder.buildConversationsClient();
ResponsesClient responsesClient = builder.buildResponsesClient();
```

## Core Workflow

### 1. Create a Prompt Agent

```java
import com.azure.ai.agents.models.PromptAgentDefinition;
import com.azure.ai.agents.models.AgentVersionDetails;

PromptAgentDefinition definition = new PromptAgentDefinition("gpt-4o");
AgentVersionDetails agent = agentsClient.createAgentVersion("my-agent", definition);
```

### 2. Create Conversation

```java
Conversation conversation = conversationsClient.getConversationService().create();
```

### 3. Add Messages to Conversation

```java
import com.openai.models.EasyInputMessage;
import com.openai.models.ItemCreateParams;

conversationsClient.getConversationService().items().create(
    ItemCreateParams.builder()
        .conversationId(conversation.id())
        .addItem(EasyInputMessage.builder()
            .role(EasyInputMessage.Role.SYSTEM)
            .content("You are a helpful assistant.")
            .build())
        .addItem(EasyInputMessage.builder()
            .role(EasyInputMessage.Role.USER)
            .content("Hello, agent!")
            .build())
        .build()
);
```

### 4. Generate Response

```java
import com.azure.ai.agents.models.AgentReference;

AgentReference agentRef = new AgentReference(agent.getName())
    .setVersion(agent.getVersion());

Response response = responsesClient.createWithAgentConversation(
    agentRef,
    conversation.id()
);
```

## Using OpenAI's Official Library

The SDK transitively imports the OpenAI Java SDK:

```java
// Access OpenAI services directly
ResponsesService responsesService = responsesClient.getOpenAIClient();
ConversationService conversationService = conversationsClient.getOpenAIClient();
```

## Best Practices

1. **Use DefaultAzureCredential** for production authentication
2. **Share conversations** across multiple agents for centralized context
3. **Use async clients** for better throughput
4. **Clean up conversations** when no longer needed
5. **Handle errors** with appropriate exception handling

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    AgentVersionDetails agent = agentsClient.createAgentVersion(name, definition);
} catch (HttpResponseException e) {
    System.err.println("Error: " + e.getResponse().getStatusCode());
}
```

## Reference Links

| Resource | URL |
|----------|-----|
| Product Docs | https://aka.ms/azsdk/azure-ai-agents/product-doc |
| GitHub Source | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-agents |
| OpenAI Java SDK | https://github.com/openai/openai-java |
