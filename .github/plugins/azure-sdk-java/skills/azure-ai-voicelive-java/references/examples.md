# Azure AI VoiceLive Java SDK - Examples

Comprehensive code examples for the Azure AI VoiceLive SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Session Management](#session-management)
- [Session Configuration](#session-configuration)
- [Audio Streaming](#audio-streaming)
- [Event Handling](#event-handling)
- [Voice Configuration](#voice-configuration)
- [Function Calling](#function-calling)
- [Error Handling](#error-handling)
- [Complete Application Example](#complete-application-example)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-voicelive</artifactId>
    <version>1.0.0-beta.2</version>
</dependency>

<!-- For DefaultAzureCredential -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.14.2</version>
</dependency>

<!-- Reactor for reactive streams -->
<dependency>
    <groupId>io.projectreactor</groupId>
    <artifactId>reactor-core</artifactId>
    <version>3.6.0</version>
</dependency>
```

## Client Creation

### With API Key

```java
import com.azure.ai.voicelive.VoiceLiveAsyncClient;
import com.azure.ai.voicelive.VoiceLiveClientBuilder;
import com.azure.core.credential.AzureKeyCredential;

String endpoint = System.getenv("AZURE_VOICELIVE_ENDPOINT");
String key = System.getenv("AZURE_VOICELIVE_API_KEY");

VoiceLiveAsyncClient client = new VoiceLiveClientBuilder()
    .endpoint(endpoint)
    .credential(new AzureKeyCredential(key))
    .buildAsyncClient();
```

### With DefaultAzureCredential (Recommended)

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

VoiceLiveAsyncClient client = new VoiceLiveClientBuilder()
    .endpoint(System.getenv("AZURE_VOICELIVE_ENDPOINT"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

## Session Management

### Start Session

```java
import com.azure.ai.voicelive.VoiceLiveSessionAsyncClient;
import reactor.core.publisher.Mono;

String modelDeployment = "gpt-4o-realtime-preview";

client.startSession(modelDeployment)
    .flatMap(session -> {
        System.out.println("Session started successfully");
        
        // Subscribe to events
        session.receiveEvents()
            .subscribe(
                event -> handleEvent(event),
                error -> System.err.println("Error: " + error.getMessage()),
                () -> System.out.println("Session ended")
            );
        
        return Mono.just(session);
    })
    .subscribe();
```

### Basic Session Flow

```java
client.startSession("gpt-4o-realtime-preview")
    .flatMap(session -> {
        // 1. Configure session
        return configureSession(session)
            .then(Mono.just(session));
    })
    .flatMap(session -> {
        // 2. Start receiving events
        session.receiveEvents()
            .subscribe(event -> processEvent(event));
        
        // 3. Send audio
        return sendAudioStream(session);
    })
    .subscribe(
        result -> System.out.println("Audio sent"),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

## Session Configuration

### Configure with Turn Detection

```java
import com.azure.ai.voicelive.models.*;
import com.azure.core.util.BinaryData;
import java.util.Arrays;

// Server-side Voice Activity Detection (VAD)
ServerVadTurnDetection turnDetection = new ServerVadTurnDetection()
    .setThreshold(0.5)                    // Sensitivity (0.0-1.0)
    .setPrefixPaddingMs(300)              // Audio to keep before speech
    .setSilenceDurationMs(500)            // Silence to end turn
    .setInterruptResponse(true)           // Allow user interruptions
    .setAutoTruncate(true)
    .setCreateResponse(true);

// Input transcription
AudioInputTranscriptionOptions transcription = new AudioInputTranscriptionOptions(
    AudioInputTranscriptionOptionsModel.WHISPER_1);

// Session options
VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
    .setInstructions("You are a helpful AI voice assistant. Be concise and friendly.")
    .setVoice(BinaryData.fromObject(new OpenAIVoice(OpenAIVoiceName.ALLOY)))
    .setModalities(Arrays.asList(InteractionModality.TEXT, InteractionModality.AUDIO))
    .setInputAudioFormat(InputAudioFormat.PCM16)
    .setOutputAudioFormat(OutputAudioFormat.PCM16)
    .setInputAudioSamplingRate(24000)
    .setInputAudioNoiseReduction(new AudioNoiseReduction(AudioNoiseReductionType.NEAR_FIELD))
    .setInputAudioEchoCancellation(new AudioEchoCancellation())
    .setInputAudioTranscription(transcription)
    .setTurnDetection(turnDetection);

// Send configuration
ClientEventSessionUpdate updateEvent = new ClientEventSessionUpdate(options);
session.sendEvent(updateEvent).subscribe();
```

### Configure for Text-Only Response

```java
VoiceLiveSessionOptions textOnlyOptions = new VoiceLiveSessionOptions()
    .setInstructions("You are a helpful assistant.")
    .setModalities(Arrays.asList(InteractionModality.TEXT))  // Text only
    .setInputAudioFormat(InputAudioFormat.PCM16)
    .setInputAudioSamplingRate(24000)
    .setTurnDetection(new ServerVadTurnDetection()
        .setCreateResponse(true));

session.sendEvent(new ClientEventSessionUpdate(textOnlyOptions)).subscribe();
```

## Audio Streaming

### Audio Requirements

- **Sample Rate**: 24kHz (24000 Hz)
- **Bit Depth**: 16-bit PCM
- **Channels**: Mono (1 channel)
- **Format**: Signed PCM, little-endian

### Send Audio Input

```java
import com.azure.core.util.BinaryData;

// Read audio from microphone or file (PCM16 format)
byte[] audioData = readAudioChunk();  // Your audio data

// Send audio to session
session.sendInputAudio(BinaryData.fromBytes(audioData))
    .subscribe(
        () -> System.out.println("Audio sent"),
        error -> System.err.println("Error sending audio: " + error.getMessage())
    );
```

### Stream Audio from Microphone

```java
import javax.sound.sampled.*;
import java.util.concurrent.atomic.AtomicBoolean;

public void streamFromMicrophone(VoiceLiveSessionAsyncClient session) {
    AtomicBoolean recording = new AtomicBoolean(true);
    
    // Audio format: 24kHz, 16-bit, mono, signed, little-endian
    AudioFormat format = new AudioFormat(24000, 16, 1, true, false);
    
    try {
        DataLine.Info info = new DataLine.Info(TargetDataLine.class, format);
        TargetDataLine microphone = (TargetDataLine) AudioSystem.getLine(info);
        microphone.open(format);
        microphone.start();
        
        // Stream in chunks
        byte[] buffer = new byte[4800];  // 100ms of audio at 24kHz
        
        Thread audioThread = new Thread(() -> {
            while (recording.get()) {
                int bytesRead = microphone.read(buffer, 0, buffer.length);
                if (bytesRead > 0) {
                    byte[] audioChunk = new byte[bytesRead];
                    System.arraycopy(buffer, 0, audioChunk, 0, bytesRead);
                    
                    session.sendInputAudio(BinaryData.fromBytes(audioChunk))
                        .subscribe();
                }
            }
            microphone.close();
        });
        
        audioThread.start();
        
        // Stop after some time or user action
        Thread.sleep(30000);
        recording.set(false);
        
    } catch (Exception e) {
        System.err.println("Error streaming audio: " + e.getMessage());
    }
}
```

### Commit Audio Buffer

Signal end of user input:

```java
session.sendEvent(new ClientEventInputAudioBufferCommit())
    .subscribe();
```

### Clear Audio Buffer

Cancel current input:

```java
session.sendEvent(new ClientEventInputAudioBufferClear())
    .subscribe();
```

## Event Handling

### Handle All Event Types

```java
import com.azure.ai.voicelive.models.*;

private void handleEvent(ServerEvent event) {
    ServerEventType eventType = event.getType();
    
    switch (eventType) {
        case SESSION_CREATED:
            handleSessionCreated((SessionCreatedEvent) event);
            break;
            
        case SESSION_UPDATED:
            System.out.println("Session configuration updated");
            break;
            
        case INPUT_AUDIO_BUFFER_SPEECH_STARTED:
            System.out.println("User started speaking");
            break;
            
        case INPUT_AUDIO_BUFFER_SPEECH_STOPPED:
            System.out.println("User stopped speaking");
            break;
            
        case INPUT_AUDIO_BUFFER_COMMITTED:
            System.out.println("Audio buffer committed");
            break;
            
        case CONVERSATION_ITEM_CREATED:
            handleConversationItemCreated(event);
            break;
            
        case RESPONSE_CREATED:
            System.out.println("Response generation started");
            break;
            
        case RESPONSE_AUDIO_DELTA:
            handleAudioDelta(event);
            break;
            
        case RESPONSE_AUDIO_TRANSCRIPT_DELTA:
            handleTranscriptDelta(event);
            break;
            
        case RESPONSE_TEXT_DELTA:
            handleTextDelta(event);
            break;
            
        case RESPONSE_DONE:
            System.out.println("Response complete");
            break;
            
        case ERROR:
            handleError(event);
            break;
            
        default:
            System.out.println("Event: " + eventType);
    }
}

private void handleSessionCreated(SessionCreatedEvent event) {
    System.out.println("Session created: " + event.getSession().getId());
}

private void handleAudioDelta(ServerEvent event) {
    if (event instanceof ResponseAudioDeltaEvent) {
        ResponseAudioDeltaEvent audioEvent = (ResponseAudioDeltaEvent) event;
        byte[] audioData = audioEvent.getDelta();
        
        // Play audio through speakers
        playAudio(audioData);
    }
}

private void handleTranscriptDelta(ServerEvent event) {
    if (event instanceof ResponseAudioTranscriptDeltaEvent) {
        ResponseAudioTranscriptDeltaEvent transcriptEvent = (ResponseAudioTranscriptDeltaEvent) event;
        System.out.print(transcriptEvent.getDelta());  // Print as it arrives
    }
}

private void handleTextDelta(ServerEvent event) {
    if (event instanceof ResponseTextDeltaEvent) {
        ResponseTextDeltaEvent textEvent = (ResponseTextDeltaEvent) event;
        System.out.print(textEvent.getDelta());
    }
}

private void handleError(ServerEvent event) {
    if (event instanceof ErrorEvent) {
        ErrorEvent errorEvent = (ErrorEvent) event;
        System.err.println("Error: " + errorEvent.getError().getMessage());
    }
}
```

### Play Audio Response

```java
import javax.sound.sampled.*;

private SourceDataLine speakerLine;

private void initializeSpeaker() throws LineUnavailableException {
    AudioFormat format = new AudioFormat(24000, 16, 1, true, false);
    DataLine.Info info = new DataLine.Info(SourceDataLine.class, format);
    speakerLine = (SourceDataLine) AudioSystem.getLine(info);
    speakerLine.open(format);
    speakerLine.start();
}

private void playAudio(byte[] audioData) {
    if (speakerLine != null) {
        speakerLine.write(audioData, 0, audioData.length);
    }
}

private void closeSpeaker() {
    if (speakerLine != null) {
        speakerLine.drain();
        speakerLine.close();
    }
}
```

## Voice Configuration

### OpenAI Voices

```java
// Available voices: ALLOY, ASH, BALLAD, CORAL, ECHO, SAGE, SHIMMER, VERSE
VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
    .setVoice(BinaryData.fromObject(new OpenAIVoice(OpenAIVoiceName.ALLOY)));

// Other voices
// OpenAIVoiceName.ASH      - Warm, friendly
// OpenAIVoiceName.BALLAD   - Expressive, dramatic
// OpenAIVoiceName.CORAL    - Clear, professional
// OpenAIVoiceName.ECHO     - Soft, calming
// OpenAIVoiceName.SAGE     - Wise, measured
// OpenAIVoiceName.SHIMMER  - Bright, energetic
// OpenAIVoiceName.VERSE    - Neutral, versatile
```

### Azure Neural Voices

```java
// Azure Standard Voice
AzureStandardVoice standardVoice = new AzureStandardVoice("en-US-JennyNeural");
options.setVoice(BinaryData.fromObject(standardVoice));

// Azure Custom Voice
AzureCustomVoice customVoice = new AzureCustomVoice("myCustomVoice", "endpointId");
options.setVoice(BinaryData.fromObject(customVoice));

// Azure Personal Voice
AzurePersonalVoice personalVoice = new AzurePersonalVoice(
    "speakerProfileId", 
    PersonalVoiceModels.PHOENIX_LATEST_NEURAL
);
options.setVoice(BinaryData.fromObject(personalVoice));
```

## Function Calling

### Define Functions

```java
import java.util.Map;

// Define function schema
Map<String, Object> weatherParams = Map.of(
    "type", "object",
    "properties", Map.of(
        "location", Map.of(
            "type", "string",
            "description", "City name, e.g., San Francisco"
        ),
        "unit", Map.of(
            "type", "string",
            "enum", new String[]{"celsius", "fahrenheit"},
            "description", "Temperature unit"
        )
    ),
    "required", new String[]{"location"}
);

VoiceLiveFunctionDefinition weatherFunction = new VoiceLiveFunctionDefinition("get_weather")
    .setDescription("Get current weather for a location")
    .setParameters(BinaryData.fromObject(weatherParams));

// Add to session options
VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
    .setInstructions("You are a helpful assistant with access to weather information.")
    .setTools(Arrays.asList(weatherFunction));
```

### Handle Function Calls

```java
private void handleFunctionCall(ServerEvent event) {
    if (event instanceof ResponseFunctionCallArgumentsDoneEvent) {
        ResponseFunctionCallArgumentsDoneEvent funcEvent = 
            (ResponseFunctionCallArgumentsDoneEvent) event;
        
        String functionName = funcEvent.getName();
        String arguments = funcEvent.getArguments();
        String callId = funcEvent.getCallId();
        
        System.out.println("Function call: " + functionName);
        System.out.println("Arguments: " + arguments);
        
        // Execute function and get result
        String result = executeFunction(functionName, arguments);
        
        // Send result back
        ConversationItemFunctionCallOutput output = new ConversationItemFunctionCallOutput(
            callId,
            result
        );
        
        session.sendEvent(new ClientEventConversationItemCreate(output))
            .then(session.sendEvent(new ClientEventResponseCreate()))
            .subscribe();
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

## Error Handling

### Handle Connection Errors

```java
session.receiveEvents()
    .doOnError(error -> {
        System.err.println("Connection error: " + error.getMessage());
        
        if (error instanceof java.net.SocketException) {
            System.err.println("Network disconnected - attempting reconnect");
            reconnect();
        }
    })
    .onErrorResume(error -> {
        // Log and continue or terminate
        return Flux.empty();
    })
    .subscribe(event -> handleEvent(event));
```

### Handle API Errors

```java
private void handleError(ServerEvent event) {
    if (event instanceof ErrorEvent) {
        ErrorEvent errorEvent = (ErrorEvent) event;
        ErrorDetails error = errorEvent.getError();
        
        System.err.println("Error type: " + error.getType());
        System.err.println("Error message: " + error.getMessage());
        System.err.println("Error code: " + error.getCode());
        
        // Handle specific errors
        String errorType = error.getType();
        if ("invalid_request_error".equals(errorType)) {
            System.err.println("Invalid request - check parameters");
        } else if ("rate_limit_error".equals(errorType)) {
            System.err.println("Rate limited - slow down requests");
        } else if ("server_error".equals(errorType)) {
            System.err.println("Server error - retry later");
        }
    }
}
```

## Complete Application Example

```java
import com.azure.ai.voicelive.VoiceLiveAsyncClient;
import com.azure.ai.voicelive.VoiceLiveClientBuilder;
import com.azure.ai.voicelive.VoiceLiveSessionAsyncClient;
import com.azure.ai.voicelive.models.*;
import com.azure.core.util.BinaryData;
import com.azure.identity.DefaultAzureCredentialBuilder;
import reactor.core.Disposable;

import javax.sound.sampled.*;
import java.util.Arrays;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicBoolean;

public class VoiceAssistant {
    
    private final VoiceLiveAsyncClient client;
    private VoiceLiveSessionAsyncClient session;
    private SourceDataLine speakerLine;
    private TargetDataLine microphoneLine;
    private AtomicBoolean running = new AtomicBoolean(false);
    private CountDownLatch sessionLatch;
    
    public VoiceAssistant() {
        this.client = new VoiceLiveClientBuilder()
            .endpoint(System.getenv("AZURE_VOICELIVE_ENDPOINT"))
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildAsyncClient();
    }
    
    public void start() throws Exception {
        sessionLatch = new CountDownLatch(1);
        running.set(true);
        
        // Initialize audio
        initializeAudio();
        
        // Start session
        client.startSession("gpt-4o-realtime-preview")
            .doOnNext(s -> {
                this.session = s;
                System.out.println("Session started");
            })
            .flatMap(this::configureSession)
            .subscribe(
                session -> {
                    // Start receiving events
                    session.receiveEvents()
                        .subscribe(
                            this::handleEvent,
                            error -> {
                                System.err.println("Error: " + error.getMessage());
                                stop();
                            },
                            () -> {
                                System.out.println("Session ended");
                                sessionLatch.countDown();
                            }
                        );
                    
                    // Start microphone streaming
                    startMicrophoneStream();
                },
                error -> {
                    System.err.println("Failed to start session: " + error.getMessage());
                    sessionLatch.countDown();
                }
            );
        
        System.out.println("Voice assistant started. Speak into the microphone...");
        System.out.println("Press Enter to stop.");
        
        // Wait for user to press Enter
        System.in.read();
        stop();
        
        sessionLatch.await();
    }
    
    private reactor.core.publisher.Mono<VoiceLiveSessionAsyncClient> configureSession(
            VoiceLiveSessionAsyncClient session) {
        
        ServerVadTurnDetection turnDetection = new ServerVadTurnDetection()
            .setThreshold(0.5)
            .setPrefixPaddingMs(300)
            .setSilenceDurationMs(500)
            .setInterruptResponse(true)
            .setAutoTruncate(true)
            .setCreateResponse(true);
        
        VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
            .setInstructions("You are a helpful voice assistant. Keep responses concise.")
            .setVoice(BinaryData.fromObject(new OpenAIVoice(OpenAIVoiceName.ALLOY)))
            .setModalities(Arrays.asList(InteractionModality.TEXT, InteractionModality.AUDIO))
            .setInputAudioFormat(InputAudioFormat.PCM16)
            .setOutputAudioFormat(OutputAudioFormat.PCM16)
            .setInputAudioSamplingRate(24000)
            .setInputAudioTranscription(new AudioInputTranscriptionOptions(
                AudioInputTranscriptionOptionsModel.WHISPER_1))
            .setTurnDetection(turnDetection);
        
        return session.sendEvent(new ClientEventSessionUpdate(options))
            .thenReturn(session);
    }
    
    private void initializeAudio() throws LineUnavailableException {
        AudioFormat format = new AudioFormat(24000, 16, 1, true, false);
        
        // Speaker
        DataLine.Info speakerInfo = new DataLine.Info(SourceDataLine.class, format);
        speakerLine = (SourceDataLine) AudioSystem.getLine(speakerInfo);
        speakerLine.open(format);
        speakerLine.start();
        
        // Microphone
        DataLine.Info micInfo = new DataLine.Info(TargetDataLine.class, format);
        microphoneLine = (TargetDataLine) AudioSystem.getLine(micInfo);
        microphoneLine.open(format);
        microphoneLine.start();
    }
    
    private void startMicrophoneStream() {
        Thread micThread = new Thread(() -> {
            byte[] buffer = new byte[4800];  // 100ms chunks
            
            while (running.get()) {
                int bytesRead = microphoneLine.read(buffer, 0, buffer.length);
                if (bytesRead > 0 && session != null) {
                    byte[] chunk = new byte[bytesRead];
                    System.arraycopy(buffer, 0, chunk, 0, bytesRead);
                    session.sendInputAudio(BinaryData.fromBytes(chunk)).subscribe();
                }
            }
        });
        micThread.setDaemon(true);
        micThread.start();
    }
    
    private void handleEvent(ServerEvent event) {
        switch (event.getType()) {
            case INPUT_AUDIO_BUFFER_SPEECH_STARTED:
                System.out.println("\n[You are speaking...]");
                break;
                
            case INPUT_AUDIO_BUFFER_SPEECH_STOPPED:
                System.out.println("[Processing...]");
                break;
                
            case RESPONSE_AUDIO_DELTA:
                if (event instanceof ResponseAudioDeltaEvent) {
                    byte[] audio = ((ResponseAudioDeltaEvent) event).getDelta();
                    speakerLine.write(audio, 0, audio.length);
                }
                break;
                
            case RESPONSE_AUDIO_TRANSCRIPT_DELTA:
                if (event instanceof ResponseAudioTranscriptDeltaEvent) {
                    System.out.print(((ResponseAudioTranscriptDeltaEvent) event).getDelta());
                }
                break;
                
            case RESPONSE_DONE:
                System.out.println("\n");
                break;
                
            case ERROR:
                if (event instanceof ErrorEvent) {
                    System.err.println("Error: " + ((ErrorEvent) event).getError().getMessage());
                }
                break;
                
            default:
                // Ignore other events
                break;
        }
    }
    
    public void stop() {
        running.set(false);
        
        if (microphoneLine != null) {
            microphoneLine.stop();
            microphoneLine.close();
        }
        
        if (speakerLine != null) {
            speakerLine.drain();
            speakerLine.stop();
            speakerLine.close();
        }
        
        System.out.println("Voice assistant stopped");
    }
    
    public static void main(String[] args) {
        try {
            VoiceAssistant assistant = new VoiceAssistant();
            assistant.start();
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
```

## Environment Variables

```bash
AZURE_VOICELIVE_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_VOICELIVE_API_KEY=<your-api-key>

# For DefaultAzureCredential
AZURE_CLIENT_ID=<service-principal-client-id>
AZURE_CLIENT_SECRET=<service-principal-secret>
AZURE_TENANT_ID=<tenant-id>
```

## Best Practices

1. **Use async client** — VoiceLive requires reactive patterns for real-time streaming
2. **Configure turn detection** — Tune VAD settings for natural conversation flow
3. **Enable noise reduction** — Use `AudioNoiseReduction` for better speech recognition
4. **Handle interruptions** — Set `setInterruptResponse(true)` for natural conversations
5. **Use Whisper transcription** — Enable for input audio transcription
6. **Close sessions properly** — Clean up resources when conversation ends
7. **Buffer audio appropriately** — Send audio in ~100ms chunks for optimal latency
8. **Implement error recovery** — Handle connection drops with reconnection logic
