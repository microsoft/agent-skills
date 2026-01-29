# Azure AI Inference Java SDK - Examples

Comprehensive code examples for the Azure AI Inference SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Basic Chat Completions](#basic-chat-completions)
- [Chat with Message History](#chat-with-message-history)
- [Streaming Chat Completions](#streaming-chat-completions)
- [Text Embeddings](#text-embeddings)
- [Vision (Image Analysis)](#vision-image-analysis)

---

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-inference</artifactId>
    <version>1.0.0-beta.5</version>
</dependency>

<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.15.3</version>
</dependency>
```

---

## Client Creation

### Sync Client with API Key

```java
import com.azure.ai.inference.ChatCompletionsClient;
import com.azure.ai.inference.ChatCompletionsClientBuilder;
import com.azure.core.credential.AzureKeyCredential;

ChatCompletionsClient client = new ChatCompletionsClientBuilder()
    .credential(new AzureKeyCredential("{key}"))
    .endpoint("{endpoint}")
    .buildClient();
```

### Async Client with API Key

```java
import com.azure.ai.inference.ChatCompletionsAsyncClient;

ChatCompletionsAsyncClient asyncClient = new ChatCompletionsClientBuilder()
    .credential(new AzureKeyCredential("{key}"))
    .endpoint("{endpoint}")
    .buildAsyncClient();
```

### Client with DefaultAzureCredential

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

ChatCompletionsClient client = new ChatCompletionsClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint("{endpoint}")
    .buildClient();
```

---

## Basic Chat Completions

### Simple Prompt

```java
import com.azure.ai.inference.ChatCompletionsClient;
import com.azure.ai.inference.ChatCompletionsClientBuilder;
import com.azure.ai.inference.models.ChatCompletions;
import com.azure.core.credential.AzureKeyCredential;
import com.azure.core.util.Configuration;

public class BasicChatSample {
    public static void main(String[] args) {
        String key = Configuration.getGlobalConfiguration().get("AZURE_API_KEY");
        String endpoint = Configuration.getGlobalConfiguration().get("MODEL_ENDPOINT");
        
        ChatCompletionsClient client = new ChatCompletionsClientBuilder()
            .credential(new AzureKeyCredential(key))
            .endpoint(endpoint)
            .buildClient();

        String prompt = "Tell me 3 jokes about trains";

        ChatCompletions completions = client.complete(prompt);

        System.out.printf("%s.%n", completions.getChoice().getMessage().getContent());
    }
}
```

---

## Chat with Message History

```java
import com.azure.ai.inference.models.*;
import java.util.ArrayList;
import java.util.List;

List<ChatRequestMessage> chatMessages = new ArrayList<>();
chatMessages.add(new ChatRequestSystemMessage("You are a helpful assistant. You will talk like a pirate."));
chatMessages.add(new ChatRequestUserMessage("Can you help me?"));
chatMessages.add(new ChatRequestAssistantMessage("Of course, me hearty! What can I do for ye?"));
chatMessages.add(new ChatRequestUserMessage("What's the best way to train a parrot?"));

ChatCompletions chatCompletions = client.complete(new ChatCompletionsOptions(chatMessages));

System.out.printf("Model ID=%s is created at %s.%n", chatCompletions.getId(), chatCompletions.getCreated());
for (ChatChoice choice : chatCompletions.getChoices()) {
    ChatResponseMessage message = choice.getMessage();
    System.out.printf("Index: %d, Chat Role: %s.%n", choice.getIndex(), message.getRole());
    System.out.println("Message:");
    System.out.println(message.getContent());
}
```

---

## Streaming Chat Completions

```java
import com.azure.ai.inference.ChatCompletionsClient;
import com.azure.ai.inference.ChatCompletionsClientBuilder;
import com.azure.ai.inference.models.*;
import com.azure.core.credential.AzureKeyCredential;
import com.azure.core.util.CoreUtils;
import com.azure.core.util.IterableStream;

import java.util.ArrayList;
import java.util.List;

public class StreamingChatSample {
    public static void main(String[] args) {
        String key = System.getenv("AZURE_API_KEY");
        String endpoint = System.getenv("MODEL_ENDPOINT");
        
        ChatCompletionsClient client = new ChatCompletionsClientBuilder()
            .credential(new AzureKeyCredential(key))
            .endpoint(endpoint)
            .buildClient();

        List<ChatRequestMessage> chatMessages = new ArrayList<>();
        chatMessages.add(new ChatRequestSystemMessage("You are a helpful assistant."));
        chatMessages.add(new ChatRequestUserMessage("What's the best way to train a parrot?"));

        IterableStream<StreamingChatCompletionsUpdate> chatCompletionsStream = 
            client.completeStream(new ChatCompletionsOptions(chatMessages));

        // Process streaming response
        chatCompletionsStream
            .stream()
            .forEach(chatCompletions -> {
                if (CoreUtils.isNullOrEmpty(chatCompletions.getChoices())) {
                    return;
                }

                StreamingChatResponseMessageUpdate delta = chatCompletions.getChoice().getDelta();

                if (delta.getRole() != null) {
                    System.out.println("Role = " + delta.getRole());
                }

                if (delta.getContent() != null) {
                    String content = delta.getContent();
                    System.out.print(content);
                }
            });
    }
}
```

### Alternative: Using forEach

```java
client.completeStream(new ChatCompletionsOptions(chatMessages))
    .forEach(chatCompletions -> {
        if (CoreUtils.isNullOrEmpty(chatCompletions.getChoices())) {
            return;
        }
        StreamingChatResponseMessageUpdate delta = chatCompletions.getChoice().getDelta();
        if (delta.getRole() != null) {
            System.out.println("Role = " + delta.getRole());
        }
        if (delta.getContent() != null) {
            System.out.print(delta.getContent());
        }
    });
```

---

## Text Embeddings

```java
import com.azure.ai.inference.EmbeddingsClient;
import com.azure.ai.inference.EmbeddingsClientBuilder;
import com.azure.ai.inference.models.EmbeddingsResult;
import com.azure.ai.inference.models.EmbeddingItem;
import com.azure.core.credential.AzureKeyCredential;

import java.util.ArrayList;
import java.util.List;

public class TextEmbeddingsSample {
    public static void main(String[] args) {
        String key = System.getenv("AZURE_EMBEDDINGS_KEY");
        String endpoint = System.getenv("EMBEDDINGS_MODEL_ENDPOINT");
        
        EmbeddingsClient client = new EmbeddingsClientBuilder()
            .credential(new AzureKeyCredential(key))
            .endpoint(endpoint)
            .buildClient();

        List<String> promptList = new ArrayList<>();
        String prompt = "Tell me 3 jokes about trains";
        promptList.add(prompt);

        EmbeddingsResult embeddings = client.embed(promptList);

        for (EmbeddingItem item : embeddings.getData()) {
            System.out.printf("Index: %d.%n", item.getIndex());
            for (Float embedding : item.getEmbeddingList()) {
                System.out.printf("%f;", embedding);
            }
        }
    }
}
```

---

## Vision (Image Analysis)

### Image from URL

```java
import com.azure.ai.inference.models.*;
import java.util.ArrayList;
import java.util.List;

public class ImageUrlChatSample {

    private static final String TEST_URL =
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg";

    public static void main(String[] args) {
        String key = System.getenv("AZURE_API_KEY");
        String endpoint = System.getenv("MODEL_ENDPOINT");
        
        ChatCompletionsClient client = new ChatCompletionsClientBuilder()
            .credential(new AzureKeyCredential(key))
            .endpoint(endpoint)
            .buildClient();

        List<ChatMessageContentItem> contentItems = new ArrayList<>();
        contentItems.add(new ChatMessageTextContentItem("Describe the image."));
        contentItems.add(new ChatMessageImageContentItem(
            new ChatMessageImageUrl(TEST_URL)));

        List<ChatRequestMessage> chatMessages = new ArrayList<>();
        chatMessages.add(new ChatRequestSystemMessage("You are a helpful assistant."));
        chatMessages.add(ChatRequestUserMessage.fromContentItems(contentItems));

        ChatCompletions completions = client.complete(new ChatCompletionsOptions(chatMessages));

        System.out.printf("%s.%n", completions.getChoice().getMessage().getContent());
    }
}
```

### Image from Local File

```java
import java.nio.file.Path;
import java.nio.file.Paths;

public class ImageFileChatSample {

    private static final String TEST_IMAGE_PATH = "./src/samples/resources/sample-images/sample.png";
    private static final String TEST_IMAGE_FORMAT = "png";

    public static void main(String[] args) {
        ChatCompletionsClient client = new ChatCompletionsClientBuilder()
            .credential(new AzureKeyCredential(key))
            .endpoint(endpoint)
            .buildClient();

        Path testFilePath = Paths.get(TEST_IMAGE_PATH);
        List<ChatMessageContentItem> contentItems = new ArrayList<>();
        contentItems.add(new ChatMessageTextContentItem("Describe the image."));
        contentItems.add(new ChatMessageImageContentItem(testFilePath, TEST_IMAGE_FORMAT));

        List<ChatRequestMessage> chatMessages = new ArrayList<>();
        chatMessages.add(new ChatRequestSystemMessage("You are a helpful assistant."));
        chatMessages.add(ChatRequestUserMessage.fromContentItems(contentItems));

        ChatCompletions completions = client.complete(new ChatCompletionsOptions(chatMessages));

        System.out.printf("%s.%n", completions.getChoice().getMessage().getContent());
    }
}
```
