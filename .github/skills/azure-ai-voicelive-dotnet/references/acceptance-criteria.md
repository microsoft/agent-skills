# Azure VoiceLive SDK Acceptance Criteria (.NET)

**SDK**: `Azure.AI.VoiceLive`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/ai/Azure.AI.VoiceLive
**NuGet Package**: https://www.nuget.org/packages/Azure.AI.VoiceLive
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Imports

### 1.1 ✅ CORRECT: Client Imports
```csharp
using Azure.AI.VoiceLive;
using Azure.Identity;
using Azure;
```

### 1.2 ✅ CORRECT: Model Imports (all in main namespace)
```csharp
using Azure.AI.VoiceLive;
// VoiceLiveSession, VoiceLiveSessionOptions, SessionUpdate, etc. are in main namespace
```

### 1.3 ❌ INCORRECT: Wrong import paths
```csharp
// WRONG - no sub-namespaces exist
using Azure.AI.VoiceLive.Models;

// WRONG - using Speech SDK instead of VoiceLive
using Microsoft.CognitiveServices.Speech;
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Recommended)
```csharp
Uri endpoint = new Uri("https://your-resource.cognitiveservices.azure.com");
DefaultAzureCredential credential = new DefaultAzureCredential();
VoiceLiveClient client = new VoiceLiveClient(endpoint, credential);
```

### 2.2 ✅ CORRECT: Environment Variables for Configuration
```csharp
string endpoint = Environment.GetEnvironmentVariable("AZURE_VOICELIVE_ENDPOINT")
    ?? throw new InvalidOperationException("AZURE_VOICELIVE_ENDPOINT not set");

Uri endpointUri = new Uri(endpoint);
VoiceLiveClient client = new VoiceLiveClient(endpointUri, new DefaultAzureCredential());
```

### 2.3 ✅ CORRECT: API Key Authentication
```csharp
Uri endpoint = new Uri("https://your-resource.cognitiveservices.azure.com");
AzureKeyCredential credential = new AzureKeyCredential("your-api-key");
VoiceLiveClient client = new VoiceLiveClient(endpoint, credential);
```

### 2.4 ❌ INCORRECT: Hardcoded credentials
```csharp
// WRONG - hardcoded API key
VoiceLiveClient client = new VoiceLiveClient(
    new Uri("https://my-resource.cognitiveservices.azure.com"),
    new AzureKeyCredential("sk-hardcoded-key"));
```

---

## 3. Session Management

### 3.1 ✅ CORRECT: Start a Session
```csharp
var model = "gpt-4o-mini-realtime-preview";
VoiceLiveSession session = await client.StartSessionAsync(model);
```

### 3.2 ✅ CORRECT: Configure Session Options
```csharp
VoiceLiveSessionOptions sessionOptions = new()
{
    Model = "gpt-4o-mini-realtime-preview",
    Instructions = "You are a helpful AI assistant. Respond naturally and conversationally.",
    Voice = new AzureStandardVoice("en-US-AvaNeural"),
    TurnDetection = new AzureSemanticVadTurnDetection()
    {
        Threshold = 0.5f,
        PrefixPadding = TimeSpan.FromMilliseconds(300),
        SilenceDuration = TimeSpan.FromMilliseconds(500)
    },
    InputAudioFormat = InputAudioFormat.Pcm16,
    OutputAudioFormat = OutputAudioFormat.Pcm16
};

// Set modalities
sessionOptions.Modalities.Clear();
sessionOptions.Modalities.Add(InteractionModality.Text);
sessionOptions.Modalities.Add(InteractionModality.Audio);

await session.ConfigureSessionAsync(sessionOptions);
```

### 3.3 ❌ INCORRECT: Not configuring session before use
```csharp
// WRONG - session needs configuration before sending audio
VoiceLiveSession session = await client.StartSessionAsync(model);
await session.SendAudioAsync(audioData); // Missing ConfigureSessionAsync
```

---

## 4. Voice Configuration

### 4.1 ✅ CORRECT: Standard Azure Voice
```csharp
VoiceLiveSessionOptions options = new()
{
    Voice = new AzureStandardVoice("en-US-AvaNeural")
};
```

### 4.2 ✅ CORRECT: Custom Voice
```csharp
VoiceLiveSessionOptions options = new()
{
    Voice = new AzureCustomVoice("your-custom-voice-name", "your-custom-voice-endpoint-id")
    {
        Temperature = 0.8f
    }
};
```

### 4.3 ✅ CORRECT: High-Definition Voice
```csharp
VoiceLiveSessionOptions options = new()
{
    Voice = new AzureHdVoice("en-US-Ava:DragonHDLatestNeural")
};
```

---

## 5. Turn Detection

### 5.1 ✅ CORRECT: Azure Semantic VAD
```csharp
VoiceLiveSessionOptions options = new()
{
    TurnDetection = new AzureSemanticVadTurnDetection()
    {
        Threshold = 0.5f,
        PrefixPadding = TimeSpan.FromMilliseconds(300),
        SilenceDuration = TimeSpan.FromMilliseconds(500),
        RemoveFillerWords = true
    }
};
```

### 5.2 ✅ CORRECT: Server VAD
```csharp
VoiceLiveSessionOptions options = new()
{
    TurnDetection = new ServerVadTurnDetection()
    {
        Threshold = 0.5f,
        PrefixPadding = TimeSpan.FromMilliseconds(300),
        SilenceDuration = TimeSpan.FromMilliseconds(500)
    }
};
```

---

## 6. Processing Session Updates

### 6.1 ✅ CORRECT: Process Updates with GetUpdatesAsync
```csharp
await foreach (SessionUpdate serverEvent in session.GetUpdatesAsync())
{
    if (serverEvent is SessionUpdateResponseAudioDelta audioDelta)
    {
        // Handle audio response
        byte[] audioData = audioDelta.Delta.ToArray();
        await PlayAudioAsync(audioData);
    }
    else if (serverEvent is SessionUpdateResponseTextDelta textDelta)
    {
        // Handle text response
        Console.Write(textDelta.Delta);
    }
    else if (serverEvent is SessionUpdateResponseAudioTranscriptDelta transcriptDelta)
    {
        // Handle transcript
        Console.Write($"[Transcript] {transcriptDelta.Delta}");
    }
}
```

### 6.2 ✅ CORRECT: Handle Different Event Types
```csharp
await foreach (SessionUpdate update in session.GetUpdatesAsync())
{
    switch (update)
    {
        case SessionUpdateResponseAudioDelta audioDelta:
            // Process audio data
            break;
        case SessionUpdateResponseTextDelta textDelta:
            // Process text
            break;
        case SessionUpdateResponseFunctionCallArgumentsDone functionCall:
            // Handle function call
            break;
        case SessionUpdateError error:
            // Handle error
            Console.WriteLine($"Error: {error.Error}");
            break;
    }
}
```

### 6.3 ❌ INCORRECT: Not using async iteration
```csharp
// WRONG - GetUpdatesAsync returns IAsyncEnumerable, not a list
var updates = session.GetUpdatesAsync().ToList();
```

---

## 7. Function Calling

### 7.1 ✅ CORRECT: Define Function Tool
```csharp
var getCurrentWeatherFunction = new VoiceLiveFunctionDefinition("get_current_weather")
{
    Description = "Get the current weather for a given location",
    Parameters = BinaryData.FromString("""
        {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state or country"
                }
            },
            "required": ["location"]
        }
        """)
};

VoiceLiveSessionOptions options = new()
{
    Model = model,
    Instructions = "You are a weather assistant.",
    Voice = new AzureStandardVoice("en-US-AvaNeural"),
    InputAudioFormat = InputAudioFormat.Pcm16,
    OutputAudioFormat = OutputAudioFormat.Pcm16
};

options.Tools.Add(getCurrentWeatherFunction);
```

### 7.2 ✅ CORRECT: Handle Function Calls
```csharp
await foreach (SessionUpdate serverEvent in session.GetUpdatesAsync())
{
    if (serverEvent is SessionUpdateResponseFunctionCallArgumentsDone functionCall)
    {
        if (functionCall.Name == "get_current_weather")
        {
            // Parse arguments
            var args = JsonSerializer.Deserialize<Dictionary<string, string>>(functionCall.Arguments);
            string location = args?["location"] ?? "unknown";
            
            // Call external service and get result
            string weatherResult = await GetWeatherAsync(location);
            
            // Send function response back
            await session.AddItemAsync(new FunctionCallOutputItem(functionCall.CallId, weatherResult));
            
            // Continue the conversation
            await session.StartResponseAsync();
        }
    }
}
```

---

## 8. Sending Input

### 8.1 ✅ CORRECT: Send Audio Data
```csharp
byte[] audioChunk = GetAudioFromMicrophone();
await session.SendAudioAsync(BinaryData.FromBytes(audioChunk));
```

### 8.2 ✅ CORRECT: Add User Text Message
```csharp
await session.AddItemAsync(new UserMessageItem("Hello, can you help me with my account?"));
await session.StartResponseAsync();
```

### 8.3 ✅ CORRECT: Commit Audio and Trigger Response
```csharp
// After sending audio chunks, commit and start response
await session.CommitAudioAsync();
await session.StartResponseAsync();
```

---

## 9. Model Selection

### 9.1 ✅ CORRECT: Available Models
```csharp
// GPT-4o with real-time audio processing
var model1 = "gpt-4o-realtime-preview";

// Lightweight GPT-4o variant
var model2 = "gpt-4o-mini-realtime-preview";

// Phi model with multimodal support
var model3 = "phi4-mm-realtime";
```

### 9.2 ❌ INCORRECT: Using non-realtime models
```csharp
// WRONG - standard chat models don't work with VoiceLive
var model = "gpt-4o"; // Not a realtime model
```

---

## 10. API Versioning

### 10.1 ✅ CORRECT: Specify API Version
```csharp
VoiceLiveClientOptions options = new(VoiceLiveClientOptions.ServiceVersion.V2025_10_01);
VoiceLiveClient client = new VoiceLiveClient(endpoint, credential, options);
```

---

## 11. Error Handling

### 11.1 ✅ CORRECT: Handle Session Errors
```csharp
try
{
    VoiceLiveSession session = await client.StartSessionAsync(model);
    
    await foreach (SessionUpdate update in session.GetUpdatesAsync())
    {
        if (update is SessionUpdateError error)
        {
            Console.WriteLine($"Session error: {error.Error}");
            break;
        }
        // Process other updates...
    }
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Service error ({ex.Status}): {ex.Message}");
}
```

### 11.2 ❌ INCORRECT: Swallowing exceptions
```csharp
// WRONG - empty catch block
try
{
    var session = await client.StartSessionAsync(model);
}
catch { }
```

---

## 12. Best Practices

### 12.1 ✅ CORRECT: Full Voice Assistant Example
```csharp
public class VoiceAssistant
{
    private readonly VoiceLiveClient _client;
    
    public VoiceAssistant(string endpoint)
    {
        _client = new VoiceLiveClient(
            new Uri(endpoint),
            new DefaultAzureCredential());
    }
    
    public async Task StartConversationAsync()
    {
        var model = "gpt-4o-mini-realtime-preview";
        VoiceLiveSession session = await _client.StartSessionAsync(model);
        
        VoiceLiveSessionOptions options = new()
        {
            Model = model,
            Instructions = "You are a helpful assistant.",
            Voice = new AzureStandardVoice("en-US-AvaNeural"),
            TurnDetection = new AzureSemanticVadTurnDetection()
            {
                Threshold = 0.5f,
                SilenceDuration = TimeSpan.FromMilliseconds(500)
            },
            InputAudioFormat = InputAudioFormat.Pcm16,
            OutputAudioFormat = OutputAudioFormat.Pcm16
        };
        
        options.Modalities.Clear();
        options.Modalities.Add(InteractionModality.Text);
        options.Modalities.Add(InteractionModality.Audio);
        
        await session.ConfigureSessionAsync(options);
        
        await foreach (SessionUpdate update in session.GetUpdatesAsync())
        {
            switch (update)
            {
                case SessionUpdateResponseAudioDelta audioDelta:
                    await ProcessAudioAsync(audioDelta.Delta.ToArray());
                    break;
                case SessionUpdateResponseTextDelta textDelta:
                    Console.Write(textDelta.Delta);
                    break;
            }
        }
    }
    
    private Task ProcessAudioAsync(byte[] audio)
    {
        // Audio playback logic
        return Task.CompletedTask;
    }
}
```

### 12.2 ✅ CORRECT: Reuse Client Instance
```csharp
// Create once and reuse - clients are thread-safe
public class VoiceLiveService
{
    private readonly VoiceLiveClient _client;
    
    public VoiceLiveService(string endpoint)
    {
        _client = new VoiceLiveClient(new Uri(endpoint), new DefaultAzureCredential());
    }
    
    public Task<VoiceLiveSession> CreateSessionAsync(string model) =>
        _client.StartSessionAsync(model);
}
```

### 12.3 ❌ INCORRECT: Creating client per session
```csharp
// WRONG - wasteful to create client for each session
public async Task<VoiceLiveSession> CreateSession(string model)
{
    var client = new VoiceLiveClient(new Uri(endpoint), new DefaultAzureCredential());
    return await client.StartSessionAsync(model);
}
```

---

## 13. Audio Format Configuration

### 13.1 ✅ CORRECT: Configure Audio Formats
```csharp
VoiceLiveSessionOptions options = new()
{
    InputAudioFormat = InputAudioFormat.Pcm16,  // 16kHz PCM
    OutputAudioFormat = OutputAudioFormat.Pcm16  // 16kHz PCM
};
```

### 13.2 ✅ CORRECT: Alternative Audio Formats
```csharp
// 24kHz PCM audio
VoiceLiveSessionOptions options = new()
{
    InputAudioFormat = InputAudioFormat.Pcm24,
    OutputAudioFormat = OutputAudioFormat.Pcm24
};
```
