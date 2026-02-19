# Azure AI VoiceLive SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-voicelive`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-voicelive
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Client Builder and Clients
```java
import com.azure.ai.voicelive.VoiceLiveAsyncClient;
import com.azure.ai.voicelive.VoiceLiveClientBuilder;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Session and Configuration Models
```java
import com.azure.ai.voicelive.models.VoiceLiveSessionOptions;
import com.azure.ai.voicelive.models.ServerVadTurnDetection;
import com.azure.ai.voicelive.models.AudioInputTranscriptionOptions;
import com.azure.ai.voicelive.models.AudioInputTranscriptionOptionsModel;
import com.azure.ai.voicelive.models.InputAudioFormat;
import com.azure.ai.voicelive.models.OutputAudioFormat;
import com.azure.ai.voicelive.models.InteractionModality;
import com.azure.ai.voicelive.models.AudioNoiseReduction;
import com.azure.ai.voicelive.models.AudioEchoCancellation;
```

#### ✅ CORRECT: Voice Models
```java
import com.azure.ai.voicelive.models.OpenAIVoice;
import com.azure.ai.voicelive.models.OpenAIVoiceName;
import com.azure.ai.voicelive.models.AzureStandardVoice;
import com.azure.ai.voicelive.models.AzureCustomVoice;
import com.azure.ai.voicelive.models.AzurePersonalVoice;
```

#### ✅ CORRECT: Event Models
```java
import com.azure.ai.voicelive.models.ServerEventType;
import com.azure.ai.voicelive.models.ClientEventSessionUpdate;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```java
// WRONG - Using sync client (only async is available)
import com.azure.ai.voicelive.VoiceLiveClient;

// WRONG - Models not in models package
import com.azure.ai.voicelive.VoiceLiveSessionOptions;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with AzureKeyCredential
```java
String endpoint = System.getenv("AZURE_VOICELIVE_ENDPOINT");
String key = System.getenv("AZURE_VOICELIVE_API_KEY");

VoiceLiveAsyncClient client = new VoiceLiveClientBuilder()
    .endpoint(endpoint)
    .credential(new AzureKeyCredential(key))
    .buildAsyncClient();
```

### 2.2 ✅ CORRECT: Builder with DefaultAzureCredential
```java
VoiceLiveAsyncClient client = new VoiceLiveClientBuilder()
    .endpoint(System.getenv("AZURE_VOICELIVE_ENDPOINT"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded endpoint URL
```java
.endpoint("https://myresource.openai.azure.com")
```

#### ❌ INCORRECT: Hardcoded API key
```java
.credential(new AzureKeyCredential("hardcoded-key"))
```

#### ❌ INCORRECT: Using sync client method
```java
.buildClient();
```

#### ❌ INCORRECT: Sync client class (does not exist)
```java
VoiceLiveClient client = new VoiceLiveClientBuilder()
```

---

## 3. Session Management Patterns

### 3.1 ✅ CORRECT: Start Session
```java
import reactor.core.publisher.Mono;

client.startSession("gpt-4o-realtime-preview")
    .flatMap(session -> {
        System.out.println("Session started");
        
        session.receiveEvents()
            .subscribe(
                event -> System.out.println("Event: " + event.getType()),
                error -> System.err.println("Error: " + error.getMessage())
            );
        
        return Mono.just(session);
    })
    .block();
```

### 3.2 ✅ CORRECT: Configure Session Options
```java
import java.util.Arrays;

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
    .setInputAudioTranscription(transcription)
    .setTurnDetection(turnDetection);

ClientEventSessionUpdate updateEvent = new ClientEventSessionUpdate(options);
session.sendEvent(updateEvent).subscribe();
```

### 3.3 ✅ CORRECT: Send Audio Input
```java
byte[] audioData = readAudioChunk();  // PCM16 audio data
session.sendInputAudio(BinaryData.fromBytes(audioData)).subscribe();
```

---

## 4. Event Handling Patterns

### 4.1 ✅ CORRECT: Handle Events
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
        // Handle audio response
    } else if (ServerEventType.RESPONSE_DONE.equals(eventType)) {
        System.out.println("Response complete");
    } else if (ServerEventType.ERROR.equals(eventType)) {
        System.err.println("Error occurred");
    }
});
```

---

## 5. Voice Configuration

### 5.1 ✅ CORRECT: OpenAI Voices
```java
// Available: ALLOY, ASH, BALLAD, CORAL, ECHO, SAGE, SHIMMER, VERSE
VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
    .setVoice(BinaryData.fromObject(new OpenAIVoice(OpenAIVoiceName.ALLOY)));
```

### 5.2 ✅ CORRECT: Azure Voices
```java
// Azure Standard Voice
options.setVoice(BinaryData.fromObject(new AzureStandardVoice("en-US-JennyNeural")));

// Azure Custom Voice
options.setVoice(BinaryData.fromObject(new AzureCustomVoice("myVoice", "endpointId")));
```

---

## 6. Error Handling

### 6.1 ✅ CORRECT: Error Handling with Reactive Patterns
```java
session.receiveEvents()
    .doOnError(error -> System.err.println("Connection error: " + error.getMessage()))
    .onErrorResume(error -> {
        // Attempt reconnection or cleanup
        return Flux.empty();
    })
    .subscribe();
```

---

## 7. Audio Requirements

- **Sample Rate**: 24kHz (24000 Hz)
- **Bit Depth**: 16-bit PCM
- **Channels**: Mono (1 channel)
- **Format**: Signed PCM, little-endian

---

## 8. Best Practices Checklist

- [ ] Use `DefaultAzureCredentialBuilder` for production authentication
- [ ] Use environment variables for endpoint and API key configuration
- [ ] Use only async client (VoiceLiveAsyncClient)
- [ ] Configure turn detection for natural conversation flow
- [ ] Enable noise reduction for better speech recognition
- [ ] Handle interruptions with `setInterruptResponse(true)`
- [ ] Use Whisper transcription for input audio
- [ ] Close sessions properly when conversation ends
- [ ] Use reactive patterns for event handling
