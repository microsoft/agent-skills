# Azure Communication Call Automation SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-communication-callautomation`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/communication/azure-communication-callautomation
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Client and Builder
```java
import com.azure.communication.callautomation.CallAutomationClient;
import com.azure.communication.callautomation.CallAutomationClientBuilder;
import com.azure.communication.callautomation.CallConnection;
import com.azure.communication.callautomation.CallMedia;
import com.azure.communication.callautomation.CallRecording;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
```

### 1.2 Model Imports

#### ✅ CORRECT: Call Models
```java
import com.azure.communication.callautomation.models.CreateCallOptions;
import com.azure.communication.callautomation.models.CreateCallResult;
import com.azure.communication.callautomation.models.AnswerCallOptions;
import com.azure.communication.callautomation.models.AnswerCallResult;
import com.azure.communication.callautomation.models.CallConnectionProperties;
```

#### ✅ CORRECT: Media Models
```java
import com.azure.communication.callautomation.models.TextSource;
import com.azure.communication.callautomation.models.FileSource;
import com.azure.communication.callautomation.models.PlayOptions;
import com.azure.communication.callautomation.models.CallMediaRecognizeDtmfOptions;
import com.azure.communication.callautomation.models.CallMediaRecognizeSpeechOptions;
import com.azure.communication.callautomation.models.DtmfTone;
```

#### ✅ CORRECT: Recording Models
```java
import com.azure.communication.callautomation.models.StartRecordingOptions;
import com.azure.communication.callautomation.models.RecordingStateResult;
import com.azure.communication.callautomation.models.RecordingChannel;
import com.azure.communication.callautomation.models.RecordingContent;
import com.azure.communication.callautomation.models.RecordingFormat;
import com.azure.communication.callautomation.models.ServerCallLocator;
```

#### ✅ CORRECT: Communication Identifiers
```java
import com.azure.communication.common.CommunicationUserIdentifier;
import com.azure.communication.common.PhoneNumberIdentifier;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using deprecated CallingServer SDK
```java
// WRONG - deprecated SDK
import com.azure.communication.callingserver.CallingServerClient;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with DefaultAzureCredential
```java
String endpoint = System.getenv("AZURE_COMMUNICATION_ENDPOINT");

CallAutomationClient client = new CallAutomationClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.2 ✅ CORRECT: Builder with Connection String
```java
String connectionString = System.getenv("AZURE_COMMUNICATION_CONNECTION_STRING");

CallAutomationClient client = new CallAutomationClientBuilder()
    .connectionString(connectionString)
    .buildClient();
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded connection string
```java
// WRONG - hardcoded values
CallAutomationClient client = new CallAutomationClientBuilder()
    .connectionString("endpoint=https://...;accesskey=...")
    .buildClient();
```

---

## 3. Call Operations

### 3.1 ✅ CORRECT: Create Outbound Call
```java
PhoneNumberIdentifier target = new PhoneNumberIdentifier("+14255551234");
PhoneNumberIdentifier caller = new PhoneNumberIdentifier("+14255550100");

CreateCallOptions options = new CreateCallOptions(
    new CommunicationUserIdentifier("<user-id>"),
    List.of(target))
    .setSourceCallerId(caller)
    .setCallbackUrl("https://your-app.com/api/callbacks");

CreateCallResult result = client.createCall(options);
String callConnectionId = result.getCallConnectionProperties().getCallConnectionId();
```

### 3.2 ✅ CORRECT: Answer Incoming Call
```java
String incomingCallContext = "<incoming-call-context-from-event>";

AnswerCallOptions options = new AnswerCallOptions(
    incomingCallContext,
    "https://your-app.com/api/callbacks");

AnswerCallResult result = client.answerCall(options);
CallConnection callConnection = result.getCallConnection();
```

### 3.3 ✅ CORRECT: Hang Up Call
```java
CallConnection callConnection = client.getCallConnection(callConnectionId);
callConnection.hangUp(true);  // true = hang up for all participants
```

---

## 4. Media Operations

### 4.1 ✅ CORRECT: Play Text-to-Speech
```java
CallConnection callConnection = client.getCallConnection(callConnectionId);
CallMedia callMedia = callConnection.getCallMedia();

TextSource textSource = new TextSource()
    .setText("Welcome to Contoso. Press 1 for sales, 2 for support.")
    .setVoiceName("en-US-JennyNeural");

PlayOptions playOptions = new PlayOptions(
    List.of(textSource),
    List.of(new CommunicationUserIdentifier("<target-user>")));

callMedia.play(playOptions);
```

### 4.2 ✅ CORRECT: Recognize DTMF
```java
CallMediaRecognizeDtmfOptions recognizeOptions = new CallMediaRecognizeDtmfOptions(
    new CommunicationUserIdentifier("<target-user>"),
    5)  // Max tones
    .setInterToneTimeout(Duration.ofSeconds(5))
    .setStopTones(List.of(DtmfTone.POUND))
    .setInitialSilenceTimeout(Duration.ofSeconds(15))
    .setPlayPrompt(new TextSource().setText("Enter your account number followed by pound."));

callMedia.startRecognizing(recognizeOptions);
```

---

## 5. Recording Operations

### 5.1 ✅ CORRECT: Start Recording
```java
CallRecording callRecording = client.getCallRecording();

StartRecordingOptions recordingOptions = new StartRecordingOptions(
    new ServerCallLocator("<server-call-id>"))
    .setRecordingChannel(RecordingChannel.MIXED)
    .setRecordingContent(RecordingContent.AUDIO_VIDEO)
    .setRecordingFormat(RecordingFormat.MP4);

RecordingStateResult result = callRecording.start(recordingOptions);
String recordingId = result.getRecordingId();
```

### 5.2 ✅ CORRECT: Stop/Pause/Resume Recording
```java
callRecording.pause(recordingId);
callRecording.resume(recordingId);
callRecording.stop(recordingId);
```

---

## 6. Event Handling

### 6.1 ✅ CORRECT: Parse Webhook Events
```java
import com.azure.communication.callautomation.CallAutomationEventParser;
import com.azure.communication.callautomation.models.events.*;

List<CallAutomationEventBase> events = CallAutomationEventParser.parseEvents(requestBody);

for (CallAutomationEventBase event : events) {
    if (event instanceof CallConnected) {
        CallConnected connected = (CallConnected) event;
        System.out.println("Call connected: " + connected.getCallConnectionId());
    } else if (event instanceof RecognizeCompleted) {
        RecognizeCompleted recognized = (RecognizeCompleted) event;
        // Handle recognition result
    }
}
```

---

## 7. Error Handling

### 7.1 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.answerCall(options);
} catch (HttpResponseException e) {
    if (e.getResponse().getStatusCode() == 404) {
        System.out.println("Call not found or already ended");
    } else {
        System.out.println("Error: " + e.getMessage());
    }
}
```

---

## 8. Best Practices Checklist

- [ ] Use `DefaultAzureCredentialBuilder` or connection string for authentication
- [ ] Use environment variables for configuration
- [ ] Use secure HTTPS callback URLs
- [ ] Handle webhook events for call state changes
- [ ] Clean up recordings after downloading
- [ ] Handle `HttpResponseException` appropriately
