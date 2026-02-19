# Azure OpenAI SDK Acceptance Criteria (.NET)

**SDK**: `Azure.AI.OpenAI`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/openai/Azure.AI.OpenAI
**NuGet Package**: https://www.nuget.org/packages/Azure.AI.OpenAI
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Imports

### 1.1 ✅ CORRECT: Client Imports
```csharp
using Azure.AI.OpenAI;
using OpenAI.Chat;
using Azure.Identity;
```

### 1.2 ✅ CORRECT: Streaming Imports
```csharp
using OpenAI.Chat;
// StreamingChatCompletionUpdate is in OpenAI.Chat namespace
```

### 1.3 ✅ CORRECT: Tool/Function Imports
```csharp
using OpenAI.Chat;
using System.Text.Json;
// ChatTool, ChatToolCall, ToolChatMessage are in OpenAI.Chat namespace
```

### 1.4 ✅ CORRECT: Assistants API Imports
```csharp
using OpenAI.Assistants;
// Assistants API is experimental - requires #pragma warning disable OPENAI001
```

### 1.5 ❌ INCORRECT: Wrong import paths
```csharp
// WRONG - using old Azure.AI.OpenAI namespaces for chat models
using Azure.AI.OpenAI.Chat;

// WRONG - ChatCompletionsClient doesn't exist in current SDK
using Azure.AI.OpenAI;
var client = new ChatCompletionsClient(...);

// WRONG - mixing OpenAI and Azure.AI.OpenAI incorrectly
using OpenAI;
var client = new OpenAI.OpenAIClient(...); // Different from AzureOpenAIClient
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Recommended)
```csharp
AzureOpenAIClient azureClient = new(
    new Uri("https://your-resource.openai.azure.com"),
    new DefaultAzureCredential());

ChatClient chatClient = azureClient.GetChatClient("my-gpt-4o-deployment");
```

### 2.2 ✅ CORRECT: API Key Credential
```csharp
string apiKey = Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY")
    ?? throw new InvalidOperationException("AZURE_OPENAI_API_KEY not set");

AzureOpenAIClient azureClient = new(
    new Uri("https://your-resource.openai.azure.com"),
    new ApiKeyCredential(apiKey));

ChatClient chatClient = azureClient.GetChatClient("my-gpt-4o-deployment");
```

### 2.3 ✅ CORRECT: Environment Variables for Configuration
```csharp
string endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException("AZURE_OPENAI_ENDPOINT not set");
string deploymentName = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT")
    ?? throw new InvalidOperationException("AZURE_OPENAI_DEPLOYMENT not set");

AzureOpenAIClient azureClient = new(new Uri(endpoint), new DefaultAzureCredential());
ChatClient chatClient = azureClient.GetChatClient(deploymentName);
```

### 2.4 ❌ INCORRECT: Hardcoded credentials
```csharp
// WRONG - hardcoded API key
AzureOpenAIClient azureClient = new(
    new Uri("https://my-resource.openai.azure.com"),
    new ApiKeyCredential("sk-hardcoded-key"));

// WRONG - hardcoded endpoint in production
AzureOpenAIClient azureClient = new(
    new Uri("https://production-resource.openai.azure.com"),
    new DefaultAzureCredential());
```

---

## 3. Chat Completions

### 3.1 ✅ CORRECT: Basic Chat Completion
```csharp
AzureOpenAIClient azureClient = new(
    new Uri(endpoint),
    new DefaultAzureCredential());

ChatClient chatClient = azureClient.GetChatClient("gpt-4o-deployment");

ChatCompletion completion = chatClient.CompleteChat(
    [
        new SystemChatMessage("You are a helpful assistant."),
        new UserChatMessage("What is Azure OpenAI?"),
    ]);

Console.WriteLine($"{completion.Role}: {completion.Content[0].Text}");
```

### 3.2 ✅ CORRECT: Multi-turn Conversation
```csharp
ChatCompletion completion = chatClient.CompleteChat(
    [
        new SystemChatMessage("You are a helpful assistant that talks like a pirate."),
        new UserChatMessage("Hi, can you help me?"),
        new AssistantChatMessage("Arrr! Of course, me hearty! What can I do for ye?"),
        new UserChatMessage("What's the best way to train a parrot?"),
    ]);
```

### 3.3 ❌ INCORRECT: Using wrong message types
```csharp
// WRONG - using string array instead of ChatMessage types
var completion = chatClient.CompleteChat(new[] { "Hello", "How are you?" });

// WRONG - mixing old SDK patterns
var options = new ChatCompletionsOptions
{
    Messages = { new ChatMessage(ChatRole.User, "Hello") }
};
```

---

## 4. Streaming

### 4.1 ✅ CORRECT: Streaming Chat Completions
```csharp
CollectionResult<StreamingChatCompletionUpdate> completionUpdates = chatClient.CompleteChatStreaming(
    [
        new SystemChatMessage("You are a helpful assistant."),
        new UserChatMessage("Write a short poem about Azure."),
    ]);

foreach (StreamingChatCompletionUpdate update in completionUpdates)
{
    foreach (ChatMessageContentPart contentPart in update.ContentUpdate)
    {
        Console.Write(contentPart.Text);
    }
}
```

### 4.2 ✅ CORRECT: Async Streaming
```csharp
AsyncCollectionResult<StreamingChatCompletionUpdate> completionUpdates = 
    chatClient.CompleteChatStreamingAsync(
        [
            new SystemChatMessage("You are a helpful assistant."),
            new UserChatMessage("Tell me about cloud computing."),
        ]);

await foreach (StreamingChatCompletionUpdate update in completionUpdates)
{
    foreach (ChatMessageContentPart contentPart in update.ContentUpdate)
    {
        Console.Write(contentPart.Text);
    }
}
```

### 4.3 ❌ INCORRECT: Not handling streaming updates properly
```csharp
// WRONG - treating streaming result as single response
var result = chatClient.CompleteChatStreaming([...]);
Console.WriteLine(result.Content); // Streaming doesn't work this way
```

---

## 5. Tool/Function Calling

### 5.1 ✅ CORRECT: Define Function Tool
```csharp
ChatTool getCurrentWeatherTool = ChatTool.CreateFunctionTool(
    functionName: "get_current_weather",
    functionDescription: "Get the current weather in a given location",
    functionParameters: BinaryData.FromString("""
    {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. Boston, MA"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "The temperature unit to use"
            }
        },
        "required": ["location"]
    }
    """)
);
```

### 5.2 ✅ CORRECT: Handle Tool Calls
```csharp
ChatCompletionOptions options = new()
{
    Tools = { getCurrentWeatherTool },
};

List<ChatMessage> messages =
    [
        new UserChatMessage("What's the weather like in Seattle?"),
    ];

ChatCompletion completion = chatClient.CompleteChat(messages, options);

if (completion.FinishReason == ChatFinishReason.ToolCalls)
{
    // Add the assistant message with tool calls to history
    messages.Add(new AssistantChatMessage(completion));
    
    foreach (ChatToolCall toolCall in completion.ToolCalls)
    {
        // Process the tool call and get result
        string result = ProcessToolCall(toolCall);
        
        // Add tool result to messages
        messages.Add(new ToolChatMessage(toolCall.Id, result));
    }
    
    // Continue the conversation with tool results
    completion = chatClient.CompleteChat(messages, options);
}
```

### 5.3 ✅ CORRECT: Streaming Tool Calls
```csharp
StringBuilder contentBuilder = new();
StreamingChatToolCallsBuilder toolCallsBuilder = new();

foreach (StreamingChatCompletionUpdate update in chatClient.CompleteChatStreaming(messages, options))
{
    foreach (ChatMessageContentPart contentPart in update.ContentUpdate)
    {
        contentBuilder.Append(contentPart.Text);
    }
    
    foreach (StreamingChatToolCallUpdate toolCallUpdate in update.ToolCallUpdates)
    {
        toolCallsBuilder.Append(toolCallUpdate);
    }
}

IReadOnlyList<ChatToolCall> toolCalls = toolCallsBuilder.Build();
```

### 5.4 ❌ INCORRECT: Old function calling patterns
```csharp
// WRONG - using deprecated Functions property
var options = new ChatCompletionOptions
{
    Functions = { ... } // Functions is deprecated, use Tools
};
```

---

## 6. Azure-Specific Features

### 6.1 ✅ CORRECT: On Your Data (Azure AI Search)
```csharp
#pragma warning disable AOAI001

ChatCompletionOptions options = new();
options.AddDataSource(new AzureSearchChatDataSource()
{
    Endpoint = new Uri("https://your-search-resource.search.windows.net"),
    IndexName = "contoso-products-index",
    Authentication = DataSourceAuthentication.FromApiKey(
        Environment.GetEnvironmentVariable("AZURE_SEARCH_KEY")),
});

ChatCompletion completion = chatClient.CompleteChat(
    [
        new UserChatMessage("What are the best-selling Contoso products?"),
    ],
    options);

ChatMessageContext context = completion.GetMessageContext();
if (context?.Intent is not null)
{
    Console.WriteLine($"Intent: {context.Intent}");
}
foreach (ChatCitation citation in context?.Citations ?? [])
{
    Console.WriteLine($"Citation: {citation.Content}");
}
```

### 6.2 ✅ CORRECT: Government Cloud Configuration
```csharp
AzureOpenAIClientOptions options = new()
{
    Audience = AzureOpenAIAudience.AzureGovernment,
};

AzureOpenAIClient azureClient = new(
    new Uri("https://your-resource.openai.azure.us"),
    new DefaultAzureCredential(),
    options);
```

---

## 7. Assistants API

### 7.1 ✅ CORRECT: Create and Use Assistants
```csharp
#pragma warning disable OPENAI001

AssistantClient assistantClient = azureClient.GetAssistantClient();

Assistant assistant = await assistantClient.CreateAssistantAsync(
    model: "my-gpt-4o-deployment",
    new AssistantCreationOptions()
    {
        Name = "Math Tutor",
        Instructions = "You help with math problems. Use the code interpreter when needed.",
        Tools = { ToolDefinition.CreateCodeInterpreter() },
    });

ThreadInitializationMessage initialMessage = new(
    MessageRole.User,
    ["Calculate the factorial of 10"]);

AssistantThread thread = await assistantClient.CreateThreadAsync(new ThreadCreationOptions()
{
    InitialMessages = { initialMessage },
});
```

### 7.2 ✅ CORRECT: Stream Assistant Run
```csharp
await foreach (StreamingUpdate update in assistantClient.CreateRunStreamingAsync(thread.Id, assistant.Id))
{
    if (update.UpdateKind == StreamingUpdateReason.RunCreated)
    {
        Console.WriteLine("--- Run started ---");
    }
    else if (update is MessageContentUpdate contentUpdate)
    {
        Console.Write(contentUpdate.Text);
    }
}
```

### 7.3 ✅ CORRECT: Cleanup Assistants Resources
```csharp
// Delete resources when no longer needed
await assistantClient.DeleteAssistantAsync(assistant.Id);
await assistantClient.DeleteThreadAsync(thread.Id);
```

---

## 8. Embeddings

### 8.1 ✅ CORRECT: Generate Embeddings
```csharp
EmbeddingClient embeddingClient = azureClient.GetEmbeddingClient("text-embedding-ada-002-deployment");

EmbeddingCollection embeddings = embeddingClient.GenerateEmbeddings(
    [
        "First text to embed",
        "Second text to embed",
    ]);

foreach (Embedding embedding in embeddings)
{
    ReadOnlyMemory<float> vector = embedding.ToFloats();
    Console.WriteLine($"Embedding dimensions: {vector.Length}");
}
```

---

## 9. Image Generation (DALL-E)

### 9.1 ✅ CORRECT: Generate Image
```csharp
ImageClient imageClient = azureClient.GetImageClient("dall-e-3-deployment");

GeneratedImage image = imageClient.GenerateImage(
    "A futuristic cityscape with flying cars at sunset",
    new ImageGenerationOptions()
    {
        Size = GeneratedImageSize.W1024xH1024,
        Quality = GeneratedImageQuality.High,
    });

Console.WriteLine($"Image URL: {image.ImageUri}");
```

---

## 10. Error Handling

### 10.1 ✅ CORRECT: Handle API Errors
```csharp
try
{
    ChatCompletion completion = await chatClient.CompleteChatAsync(messages);
}
catch (ClientResultException ex) when (ex.Status == 429)
{
    Console.WriteLine("Rate limited. Retry after delay.");
}
catch (ClientResultException ex)
{
    Console.WriteLine($"API error ({ex.Status}): {ex.Message}");
}
```

### 10.2 ❌ INCORRECT: Swallowing errors
```csharp
// WRONG - empty catch block
try
{
    var completion = await chatClient.CompleteChatAsync(messages);
}
catch { }
```

---

## 11. Best Practices

### 11.1 ✅ CORRECT: Reuse Client Instances
```csharp
public class OpenAIService
{
    private readonly ChatClient _chatClient;
    
    public OpenAIService(string endpoint, string deployment)
    {
        var azureClient = new AzureOpenAIClient(
            new Uri(endpoint),
            new DefaultAzureCredential());
        _chatClient = azureClient.GetChatClient(deployment);
    }
    
    public async Task<string> GetCompletionAsync(string prompt)
    {
        var completion = await _chatClient.CompleteChatAsync([new UserChatMessage(prompt)]);
        return completion.Value.Content[0].Text;
    }
}
```

### 11.2 ❌ INCORRECT: Creating clients per request
```csharp
// WRONG - wasteful to create new client for each request
public async Task<string> GetCompletion(string prompt)
{
    var client = new AzureOpenAIClient(new Uri(endpoint), new DefaultAzureCredential());
    var chatClient = client.GetChatClient(deployment);
    // ...
}
```
