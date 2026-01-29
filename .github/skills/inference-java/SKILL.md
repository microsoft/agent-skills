---
name: inference-java
description: |
  Azure AI Inference SDK for Java. Use for chat completions, embeddings, and model inference with Azure AI Foundry endpoints.
  Triggers: "ChatCompletionsClient java", "EmbeddingsClient java", "azure inference java", "model inference java", "Foundry models java".
---

# Azure AI Inference SDK for Java

Client library for Azure AI model inference with chat completions and embeddings.

## Installation

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-inference</artifactId>
    <version>1.0.0-beta.5</version>
</dependency>
```

## Environment Variables

```bash
AZURE_INFERENCE_ENDPOINT=https://<resource>.services.ai.azure.com/models
AZURE_INFERENCE_CREDENTIAL=<your-api-key>
AZURE_INFERENCE_MODEL=gpt-4o-mini
```

## Authentication

### API Key

```java
import com.azure.ai.inference.ChatCompletionsClient;
import com.azure.ai.inference.ChatCompletionsClientBuilder;
import com.azure.core.credential.AzureKeyCredential;

ChatCompletionsClient client = new ChatCompletionsClientBuilder()
    .endpoint(System.getenv("AZURE_INFERENCE_ENDPOINT"))
    .credential(new AzureKeyCredential(System.getenv("AZURE_INFERENCE_CREDENTIAL")))
    .buildClient();
```

### DefaultAzureCredential (Recommended)

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

ChatCompletionsClient client = new ChatCompletionsClientBuilder()
    .endpoint(System.getenv("AZURE_INFERENCE_ENDPOINT"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

## Client Types

| Client | Purpose |
|--------|---------|
| `ChatCompletionsClient` | Chat and text completions (sync) |
| `ChatCompletionsAsyncClient` | Chat completions (async) |
| `EmbeddingsClient` | Text embeddings (sync) |
| `EmbeddingsAsyncClient` | Text embeddings (async) |

## Chat Completions

### Basic Completion

```java
import com.azure.ai.inference.models.*;
import java.util.ArrayList;
import java.util.List;

List<ChatRequestMessage> messages = new ArrayList<>();
messages.add(new ChatRequestSystemMessage("You are a helpful assistant."));
messages.add(new ChatRequestUserMessage("What is Azure AI?"));

ChatCompletions response = client.complete(new ChatCompletionsOptions(messages));

for (ChatChoice choice : response.getChoices()) {
    System.out.println(choice.getMessage().getContent());
}
```

### Streaming Completions

```java
List<ChatRequestMessage> messages = new ArrayList<>();
messages.add(new ChatRequestSystemMessage("You are a helpful assistant."));
messages.add(new ChatRequestUserMessage("Write a poem about Azure."));

client.completeStream(new ChatCompletionsOptions(messages))
    .forEach(chatCompletions -> {
        if (!CoreUtils.isNullOrEmpty(chatCompletions.getChoices())) {
            StreamingChatResponseMessageUpdate delta = chatCompletions.getChoice().getDelta();
            if (delta.getContent() != null) {
                System.out.print(delta.getContent());
            }
        }
    });
```

### Chat with Image URL

```java
List<ChatMessageContentItem> contentItems = new ArrayList<>();
contentItems.add(new ChatMessageTextContentItem("Describe the image."));
contentItems.add(new ChatMessageImageContentItem(new ChatMessageImageUrl("<URL>")));

List<ChatRequestMessage> messages = new ArrayList<>();
messages.add(new ChatRequestSystemMessage("You are a helpful assistant."));
messages.add(ChatRequestUserMessage.fromContentItems(contentItems));

ChatCompletions response = client.complete(new ChatCompletionsOptions(messages));
System.out.println(response.getChoice().getMessage().getContent());
```

## Embeddings

```java
import com.azure.ai.inference.EmbeddingsClient;
import com.azure.ai.inference.EmbeddingsClientBuilder;
import com.azure.ai.inference.models.*;
import java.util.List;

EmbeddingsClient embeddingsClient = new EmbeddingsClientBuilder()
    .endpoint(endpoint)
    .credential(new AzureKeyCredential(key))
    .buildClient();

List<String> input = List.of("Your text string goes here");
EmbeddingsResult result = embeddingsClient.embed(input);

for (EmbeddingItem item : result.getData()) {
    System.out.println("Dimensions: " + item.getEmbeddingList().size());
}
```

## Message Types

| Type | Description |
|------|-------------|
| `ChatRequestSystemMessage` | System instructions |
| `ChatRequestUserMessage` | User input (text, images) |
| `ChatRequestAssistantMessage` | Model responses |
| `ChatRequestToolMessage` | Tool execution results |

## Model Information

```java
ModelInfo modelInfo = client.getModelInfo();
System.out.println("Model: " + modelInfo.getModelName());
System.out.println("Provider: " + modelInfo.getModelProviderName());
System.out.println("Type: " + modelInfo.getModelType());
```

## Best Practices

1. **Use DefaultAzureCredential** for production
2. **Use streaming** for long responses to improve UX
3. **Specify model** when endpoint serves multiple deployments
4. **Close async clients** explicitly or use try-with-resources
5. **Handle rate limits** with appropriate retry logic

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    ChatCompletions response = client.complete(options);
} catch (HttpResponseException e) {
    System.err.println("Error: " + e.getResponse().getStatusCode());
    System.err.println("Message: " + e.getMessage());
}
```

## Reference Links

| Resource | URL |
|----------|-----|
| API Reference | https://aka.ms/azsdk/azure-ai-inference/java/reference |
| GitHub Source | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-inference |
| Samples | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-inference/src/samples |
