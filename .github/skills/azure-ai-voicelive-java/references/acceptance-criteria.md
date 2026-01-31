# Azure AI VoiceLive SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-voicelive`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-voicelive
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Azure SDK Client Imports
```java
import com.azure.ai.voicelive.VoiceLiveAsyncClient;
import com.azure.ai.voicelive.VoiceLiveClientBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

#### ❌ INCORRECT: Non-existent or Wrong Package
```java
import com.azure.voicelive.VoiceLiveClient;  // Wrong package path
import azure.ai.voicelive.Client;  // Wrong root package
```

### 1.2 Model Imports
#### ✅ CORRECT: Model Classes from Models Package
```java
import com.azure.ai.voicelive.models.VoiceLiveSessionOptions;
import com.azure.ai.voicelive.models.ServerVadTurnDetection;
import com.azure.ai.voicelive.models.AudioInputTranscriptionOptions;
import com.azure.ai.voicelive.models.OpenAIVoice;
import com.azure.ai.voicelive.models.OpenAIVoiceName;
import com.azure.ai.voicelive.models.InteractionModality;
```

#### ❌ INCORRECT: Wrong Model Package
```java
import com.azure.ai.voicelive.VoiceLiveSessionOptions;  // Missing models subpackage
```

---

## 2. Client Creation Patterns

### 2.1 Async Client with API Key
#### ✅ CORRECT: Using VoiceLiveClientBuilder
```java
VoiceLiveAsyncClient client = new VoiceLiveClientBuilder()
    .endpoint(System.getenv("AZURE_VOICELIVE_ENDPOINT"))
    .credential(new AzureKeyCredential(System.getenv("AZURE_VOICELIVE_API_KEY")))
    .buildAsyncClient();
```

#### ❌ INCORRECT: Direct Instantiation or Sync Client
```java
VoiceLiveClient client = new VoiceLiveClient(endpoint, key);  // No sync client
VoiceLiveAsyncClient client = new VoiceLiveAsyncClient(endpoint);  // Direct instantiation
```

### 2.2 DefaultAzureCredential (Recommended)
#### ✅ CORRECT: Using DefaultAzureCredentialBuilder
```java
import com.azure.identity.DefaultAzureCredentialBuilder;

VoiceLiveAsyncClient client = new VoiceLiveClientBuilder()
    .endpoint(System.getenv("AZURE_VOICELIVE_ENDPOINT"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

#### ❌ INCORRECT: Direct DefaultAzureCredential
```java
VoiceLiveAsyncClient client = new VoiceLiveClientBuilder()
    .credential(new DefaultAzureCredential())  // Must use builder
    .buildAsyncClient();
```

---

## 3. Session Management Patterns

### 3.1 Start Session
#### ✅ CORRECT: Reactive Session Start
```java
import reactor.core.publisher.Mono;

client.startSession("gpt-4o-realtime-preview")
    .flatMap(session -> {
        System.out.println("Session started");
        
        // Subscribe to events
        session.receiveEvents()
            .subscribe(
                event -> System.out.println("Event: " + event.getType()),
                error -> System.err.println("Error: " + error.getMessage())
            );
        
        return Mono.just(session);
    })
    .block();
```

#### ❌ INCORRECT: Non-reactive Approach
```java
VoiceLiveSession session = client.startSession("model");  // No sync method
```

### 3.2 Configure Session Options
#### ✅ CORRECT: Full Session Configuration
```java
ServerVadTurnDetection turnDetection = new ServerVadTurnDetection()
    .setThreshold(0.5)
    .setPrefixPaddingMs(300)
    .setSilenceDurationMs(500)
    .setInterruptResponse(true)
    .setAutoTruncate(true)
    .setCreateResponse(true);

AudioInputTranscriptionOptions transcription = new AudioInputTranscriptionOptions(
    AudioInputTranscriptionOptionsModel.WHISPER_1);

VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
    .setInstructions("You are a helpful AI voice assistant.")
    .setVoice(BinaryData.fromObject(new OpenAIVoice(OpenAIVoiceName.ALLOY)))
    .setModalities(Arrays.asList(InteractionModality.TEXT, InteractionModality.AUDIO))
    .setInputAudioFormat(InputAudioFormat.PCM16)
    .setOutputAudioFormat(OutputAudioFormat.PCM16)
    .setInputAudioSamplingRate(24000)
    .setInputAudioNoiseReduction(new AudioNoiseReduction(AudioNoiseReductionType.NEAR_FIELD))
    .setInputAudioEchoCancellation(new AudioEchoCancellation())
    .setInputAudioTranscription(transcription)
    .setTurnDetection(turnDetection);

ClientEventSessionUpdate updateEvent = new ClientEventSessionUpdate(options);
session.sendEvent(updateEvent).subscribe();
```

---

## 4. Audio Requirements

### 4.1 Audio Format Specifications
| Requirement | Value |
|-------------|-------|
| Sample Rate | 24kHz (24000 Hz) |
| Bit Depth | 16-bit PCM |
| Channels | Mono (1 channel) |
| Format | Signed PCM, little-endian |

### 4.2 Send Audio Input
#### ✅ CORRECT: BinaryData for Audio
```java
byte[] audioData = readAudioChunk(); // Your PCM16 audio data
session.sendInputAudio(BinaryData.fromBytes(audioData)).subscribe();
```

#### ❌ INCORRECT: Wrong Audio Format
```java
session.sendInputAudio(audioData);  // Must wrap in BinaryData
session.sendAudio(audioBytes);  // Wrong method name
```

---

## 5. Event Handling Patterns

### 5.1 Receive Events
#### ✅ CORRECT: Reactive Event Subscription
```java
session.receiveEvents().subscribe(event -> {
    ServerEventType eventType = event.getType();
    
    if (ServerEventType.SESSION_CREATED.equals(eventType)) {
        System.out.println("Session created");
    } else if (ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED.equals(eventType)) {
        System.out.println("User started speaking");
    } else if (ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED.equals(eventType)) {
        System.out.println("User stopped speaking");
    } else if (ServerEventType.RESPONSE_AUDIO_DELTA.equals(eventType)) {
        if (event instanceof SessionUpdateResponseAudioDelta) {
            SessionUpdateResponseAudioDelta audioEvent = (SessionUpdateResponseAudioDelta) event;
            playAudioChunk(audioEvent.getDelta());
        }
    } else if (ServerEventType.RESPONSE_DONE.equals(eventType)) {
        System.out.println("Response complete");
    } else if (ServerEventType.ERROR.equals(eventType)) {
        if (event instanceof SessionUpdateError) {
            SessionUpdateError errorEvent = (SessionUpdateError) event;
            System.err.println("Error: " + errorEvent.getError().getMessage());
        }
    }
});
```

### 5.2 Key Event Types
| Event Type | Description |
|------------|-------------|
| `SESSION_CREATED` | Session successfully established |
| `INPUT_AUDIO_BUFFER_SPEECH_STARTED` | User started speaking |
| `INPUT_AUDIO_BUFFER_SPEECH_STOPPED` | User stopped speaking |
| `RESPONSE_AUDIO_DELTA` | Audio response chunk received |
| `RESPONSE_DONE` | Response completed |
| `ERROR` | Error occurred |

---

## 6. Voice Configuration Patterns

### 6.1 OpenAI Voices
#### ✅ CORRECT: OpenAI Voice Selection
```java
// Available: ALLOY, ASH, BALLAD, CORAL, ECHO, SAGE, SHIMMER, VERSE
VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
    .setVoice(BinaryData.fromObject(new OpenAIVoice(OpenAIVoiceName.ALLOY)));
```

### 6.2 Azure Voices
#### ✅ CORRECT: Azure Standard Voice
```java
options.setVoice(BinaryData.fromObject(new AzureStandardVoice("en-US-JennyNeural")));
```

#### ✅ CORRECT: Azure Custom Voice
```java
options.setVoice(BinaryData.fromObject(new AzureCustomVoice("myVoice", "endpointId")));
```

#### ✅ CORRECT: Azure Personal Voice
```java
options.setVoice(BinaryData.fromObject(
    new AzurePersonalVoice("speakerProfileId", PersonalVoiceModels.PHOENIX_LATEST_NEURAL)));
```

---

## 7. Function Calling Patterns

### 7.1 Define Functions
#### ✅ CORRECT: VoiceLiveFunctionDefinition
```java
VoiceLiveFunctionDefinition weatherFunction = new VoiceLiveFunctionDefinition("get_weather")
    .setDescription("Get current weather for a location")
    .setParameters(BinaryData.fromObject(parametersSchema));

VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
    .setTools(Arrays.asList(weatherFunction))
    .setInstructions("You have access to weather information.");
```

---

## 8. Error Handling

### 8.1 Reactive Error Handling
#### ✅ CORRECT: doOnError and onErrorResume
```java
session.receiveEvents()
    .doOnError(error -> System.err.println("Connection error: " + error.getMessage()))
    .onErrorResume(error -> {
        // Attempt reconnection or cleanup
        return Flux.empty();
    })
    .subscribe();
```

#### ❌ INCORRECT: Try-catch for Reactive Streams
```java
try {
    session.receiveEvents().subscribe();  // Won't catch async errors
} catch (Exception e) {
    // This won't catch reactive stream errors
}
```

---

## 9. Environment Configuration

### 9.1 Environment Variables
#### ✅ CORRECT: Reading from Environment
```java
String endpoint = System.getenv("AZURE_VOICELIVE_ENDPOINT");
String key = System.getenv("AZURE_VOICELIVE_API_KEY");
```

#### ❌ INCORRECT: Hardcoded Credentials
```java
String endpoint = "https://myresource.openai.azure.com/";
String key = "abc123secretkey";  // Never hardcode credentials
```

---

## 10. Best Practices

### 10.1 Async-Only SDK
- VoiceLive requires reactive patterns (no sync client)
- Use Project Reactor types (Mono, Flux)

### 10.2 Turn Detection
- Configure turn detection for natural conversation flow
- Adjust threshold for sensitivity (0.0-1.0)
- Set appropriate silence duration

### 10.3 Audio Processing
- Enable noise reduction for better speech recognition
- Use echo cancellation when needed
- Enable Whisper transcription for input audio

### 10.4 Interruptions
- Enable `setInterruptResponse(true)` for natural conversation
- Handle speech start/stop events appropriately

### 10.5 Session Lifecycle
- Close sessions properly when conversation ends
- Handle reconnection on errors