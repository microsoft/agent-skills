---
name: inference-dotnet
description: |
  Azure AI Inference SDK for .NET. Chat completions, embeddings, and model inference for AI models deployed via Azure AI Foundry and Azure Machine Learning Studio. Use for serverless API endpoints and managed compute endpoints. Triggers: "Azure.AI.Inference", "ChatCompletionsClient", "EmbeddingsClient", "model inference", "chat completions .NET", "text embeddings .NET", "Azure AI Foundry inference".
---

# Azure.AI.Inference (.NET)

Azure AI Inference client library for chat completions, embeddings, and model inference for AI models deployed by Azure AI Foundry and Azure Machine Learning Studio.

## Installation

```bash
dotnet add package Azure.AI.Inference --prerelease
dotnet add package Azure.Identity
```

**Current Version**: v1.0.0-beta.5 (preview)

## Environment Variables

```bash
AZURE_AI_CHAT_ENDPOINT=https://<your-host-name>.<region>.inference.ai.azure.com
AZURE_AI_CHAT_KEY=<your-api-key>
AZURE_AI_EMBEDDINGS_ENDPOINT=https://<your-host-name>.<region>.inference.ai.azure.com
AZURE_AI_EMBEDDINGS_KEY=<your-api-key>
# Or for Foundry models endpoint
AZURE_INFERENCE_CREDENTIAL=<your-api-key>
```

## Authentication

### API Key Authentication

```csharp
using Azure;
using Azure.AI.Inference;

var endpoint = new Uri(Environment.GetEnvironmentVariable("AZURE_AI_CHAT_ENDPOINT"));
var credential = new AzureKeyCredential(Environment.GetEnvironmentVariable("AZURE_AI_CHAT_KEY"));

var client = new ChatCompletionsClient(endpoint, credential, new AzureAIInferenceClientOptions());
```

### Microsoft Entra ID (Recommended for Production)

```csharp
using Azure.Identity;
using Azure.AI.Inference;

var endpoint = new Uri("https://<resource>.services.ai.azure.com/models");
var client = new ChatCompletionsClient(endpoint, new DefaultAzureCredential());
```

### ASP.NET Core Dependency Injection

```csharp
services.AddAzureClients(builder =>
{
    builder.AddChatCompletionsClient(new Uri("<endpoint>"));
    builder.UseCredential(new DefaultAzureCredential());
});
```

## Client Hierarchy

```
ChatCompletionsClient
├── Complete(ChatCompletionsOptions)           → Response<ChatCompletions>
├── CompleteAsync(ChatCompletionsOptions)      → Task<Response<ChatCompletions>>
├── CompleteStreaming(ChatCompletionsOptions)  → StreamingResponse<StreamingChatCompletionsUpdate>
├── CompleteStreamingAsync(...)                → AsyncStreamingResponse<...>
└── GetModelInfo()                             → Response<ModelInfo>

EmbeddingsClient
├── Embed(EmbeddingsOptions)                   → Response<EmbeddingsResult>
├── EmbedAsync(EmbeddingsOptions)              → Task<Response<EmbeddingsResult>>
└── GetModelInfo()                             → Response<ModelInfo>

ImageEmbeddingsClient
├── Embed(ImageEmbeddingsOptions)              → Response<EmbeddingsResult>
└── EmbedAsync(ImageEmbeddingsOptions)         → Task<Response<EmbeddingsResult>>
```

## Core Workflows

### 1. Chat Completions

```csharp
using Azure;
using Azure.AI.Inference;

var endpoint = new Uri(Environment.GetEnvironmentVariable("AZURE_AI_CHAT_ENDPOINT"));
var credential = new AzureKeyCredential(Environment.GetEnvironmentVariable("AZURE_AI_CHAT_KEY"));

var client = new ChatCompletionsClient(endpoint, credential, new AzureAIInferenceClientOptions());

var requestOptions = new ChatCompletionsOptions()
{
    Messages =
    {
        new ChatRequestSystemMessage("You are a helpful assistant."),
        new ChatRequestUserMessage("How many feet are in a mile?"),
    },
};

Response<ChatCompletions> response = client.Complete(requestOptions);
Console.WriteLine(response.Value.Content);
```

### 2. Streaming Chat Completions

```csharp
var requestOptions = new ChatCompletionsOptions()
{
    Messages =
    {
        new ChatRequestSystemMessage("You are a helpful assistant."),
        new ChatRequestUserMessage("Write a poem about Azure."),
    },
    Model = "gpt-4o-mini",  // Optional for single-model endpoints
};

StreamingResponse<StreamingChatCompletionsUpdate> response = await client.CompleteStreamingAsync(requestOptions);

StringBuilder contentBuilder = new();
await foreach (StreamingChatCompletionsUpdate chatUpdate in response)
{
    if (!string.IsNullOrEmpty(chatUpdate.ContentUpdate))
    {
        contentBuilder.Append(chatUpdate.ContentUpdate);
    }
}

Console.WriteLine(contentBuilder.ToString());
```

### 3. Chat with Images (Multi-modal)

```csharp
var requestOptions = new ChatCompletionsOptions()
{
    Messages =
    {
        new ChatRequestSystemMessage("You are a helpful assistant that describes images."),
        new ChatRequestUserMessage(
            new ChatMessageTextContentItem("What's in this image?"),
            new ChatMessageImageContentItem(new Uri("https://example.com/image.jpg"))
        ),
    },
};

Response<ChatCompletions> response = client.Complete(requestOptions);
Console.WriteLine(response.Value.Choices[0].Message.Content);
```

### 4. Chat with Tools (Function Calling)

```csharp
var getWeatherTool = new ChatCompletionsFunctionToolDefinition(
    new FunctionDefinition("get_weather")
    {
        Description = "Get the weather in a location",
        Parameters = BinaryData.FromString("""
        {
            "type": "object",
            "properties": {
                "location": { "type": "string", "description": "The city and state" }
            },
            "required": ["location"]
        }
        """)
    });

var requestOptions = new ChatCompletionsOptions()
{
    Messages =
    {
        new ChatRequestUserMessage("What's the weather in Seattle?"),
    },
    Tools = { getWeatherTool }
};

Response<ChatCompletions> response = client.Complete(requestOptions);

// Handle tool calls
var assistantMessage = response.Value.Choices[0].Message;
if (assistantMessage.ToolCalls?.Count > 0)
{
    foreach (var toolCall in assistantMessage.ToolCalls)
    {
        if (toolCall is ChatCompletionsFunctionToolCall functionCall)
        {
            // Execute the function and add result
            string result = ExecuteFunction(functionCall.Name, functionCall.Arguments);
            
            requestOptions.Messages.Add(new ChatRequestAssistantMessage(assistantMessage));
            requestOptions.Messages.Add(new ChatRequestToolMessage(result, functionCall.Id));
        }
    }
    
    // Get final response
    response = client.Complete(requestOptions);
}
```

### 5. Text Embeddings

```csharp
using Azure;
using Azure.AI.Inference;

var endpoint = new Uri(Environment.GetEnvironmentVariable("AZURE_AI_EMBEDDINGS_ENDPOINT"));
var credential = new AzureKeyCredential(Environment.GetEnvironmentVariable("AZURE_AI_EMBEDDINGS_KEY"));

var client = new EmbeddingsClient(endpoint, credential, new AzureAIInferenceClientOptions());

var input = new List<string> { "King", "Queen", "Jack", "Page" };
var requestOptions = new EmbeddingsOptions(input);

Response<EmbeddingsResult> response = client.Embed(requestOptions);
foreach (EmbeddingItem item in response.Value.Data)
{
    List<float> embedding = item.Embedding.ToObjectFromJson<List<float>>();
    Console.WriteLine($"Index: {item.Index}, Embedding length: {embedding.Count}");
}
```

### 6. Get Model Information

```csharp
Response<ModelInfo> modelInfo = client.GetModelInfo();

Console.WriteLine($"Model name: {modelInfo.Value.ModelName}");
Console.WriteLine($"Model type: {modelInfo.Value.ModelType}");
Console.WriteLine($"Model provider: {modelInfo.Value.ModelProviderName}");
```

### 7. Additional Model-Specific Parameters

```csharp
var requestOptions = new ChatCompletionsOptions()
{
    Messages =
    {
        new ChatRequestSystemMessage("You are a helpful assistant."),
        new ChatRequestUserMessage("How many feet are in a mile?"),
    },
    // Pass additional model-specific parameters
    AdditionalProperties = { { "foo", BinaryData.FromString("\"bar\"") } },
};

Response<ChatCompletions> response = client.Complete(requestOptions);
Console.WriteLine(response.Value.Choices[0].Message.Content);
```

### 8. Using with Azure OpenAI Endpoints

```csharp
// The SDK can be configured to work with Azure OpenAI endpoints
// with minor adjustments to the endpoint URL format
var endpoint = new Uri("https://<resource>.openai.azure.com/openai/deployments/<deployment>/");
var credential = new AzureKeyCredential("<api-key>");

var client = new ChatCompletionsClient(endpoint, credential, new AzureAIInferenceClientOptions());
```

## Key Types Reference

| Type | Purpose |
|------|---------|
| `ChatCompletionsClient` | Main client for chat completions |
| `EmbeddingsClient` | Client for text embeddings |
| `ImageEmbeddingsClient` | Client for image embeddings |
| `ChatCompletionsOptions` | Request options for chat completions |
| `EmbeddingsOptions` | Request options for embeddings |
| `ChatCompletions` | Response containing chat completion |
| `EmbeddingsResult` | Response containing embeddings |
| `StreamingChatCompletionsUpdate` | Streaming response update |
| `ChatRequestSystemMessage` | System message in conversation |
| `ChatRequestUserMessage` | User message in conversation |
| `ChatRequestAssistantMessage` | Assistant message in conversation |
| `ChatRequestToolMessage` | Tool result message |
| `ChatCompletionsFunctionToolDefinition` | Function tool definition |
| `ModelInfo` | Information about the deployed model |
| `AzureAIInferenceClientOptions` | Client configuration options |

## Best Practices

1. **Reuse clients** — Clients are thread-safe; create once and reuse
2. **Use DefaultAzureCredential** — Prefer over API keys for production
3. **Handle streaming for long responses** — Reduces time-to-first-token
4. **Set appropriate timeouts** — Configure via `AzureAIInferenceClientOptions`
5. **Cache model info** — `GetModelInfo()` results are cached in the client
6. **Use async methods** — For better scalability in web applications
7. **Handle tool calls iteratively** — Loop until no more tool calls are returned

## Error Handling

```csharp
try
{
    Response<ChatCompletions> response = client.Complete(requestOptions);
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Status: {ex.Status}");
    Console.WriteLine($"Error: {ex.Message}");
    
    // Handle specific status codes
    switch (ex.Status)
    {
        case 429:
            // Rate limited - implement backoff
            break;
        case 400:
            // Bad request - check parameters
            break;
    }
}
```

## OpenTelemetry Observability

```csharp
// Enable experimental tracing
AppContext.SetSwitch("Azure.Experimental.EnableActivitySource", true);

// Enable content recording (optional - can contain sensitive data)
AppContext.SetSwitch("Azure.Experimental.TraceGenAIMessageContent", true);

using var tracerProvider = Sdk.CreateTracerProviderBuilder()
    .AddSource("Azure.AI.Inference.*")
    .AddConsoleExporter()
    .Build();

using var meterProvider = Sdk.CreateMeterProviderBuilder()
    .AddMeter("Azure.AI.Inference.*")
    .AddConsoleExporter()
    .Build();
```

## Related SDKs

| SDK | Purpose | Install |
|-----|---------|---------|
| `Azure.AI.Inference` | Model inference (this SDK) | `dotnet add package Azure.AI.Inference --prerelease` |
| `Azure.AI.OpenAI` | Azure OpenAI specific features | `dotnet add package Azure.AI.OpenAI` |
| `Azure.AI.Projects` | Azure AI Foundry projects | `dotnet add package Azure.AI.Projects --prerelease` |

## Reference Links

| Resource | URL |
|----------|-----|
| NuGet Package | https://www.nuget.org/packages/Azure.AI.Inference |
| API Reference | https://learn.microsoft.com/dotnet/api/azure.ai.inference |
| GitHub Source | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/ai/Azure.AI.Inference |
| Samples | https://aka.ms/azsdk/azure-ai-inference/csharp/samples |
| REST API Reference | https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-api |
