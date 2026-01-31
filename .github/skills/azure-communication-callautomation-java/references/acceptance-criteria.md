# Azure Communication Call Automation Acceptance Criteria

**SDK**: `com.azure:azure-communication-callautomation`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/communication/azure-communication-callautomation
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Full qualified client imports
```java
import com.azure.communication.callautomation.CallAutomationClient;
import com.azure.communication.callautomation.CallAutomationClientBuilder;
import com.azure.communication.callautomation.CallAutomationEventParser;
import com.azure.communication.callautomation.CallConnection;
import com.azure.communication.callautomation.CallMedia;
import com.azure.communication.callautomation.CallRecording;
```

#### ❌ INCORRECT: Using deprecated CallingServer imports
```java
import com.azure.communication.callingserver.CallingServerClient;
import com.azure.communication.callingserver.CallingServerClientBuilder;
```

### 1.2 Model Imports
#### ✅ CORRECT: Models from callautomation.models package
```java
import com.azure.communication.callautomation.models.*;
import com.azure.communication.callautomation.models.events.*;
```

#### ❌ INCORRECT: Models from wrong package
```java
import com.azure.communication.calling.models.*;
```

### 1.3 Identity Imports
#### ✅ CORRECT: Common identity types
```java
import com.azure.communication.common.CommunicationUserIdentifier;
import com.azure.communication.common.PhoneNumberIdentifier;
import com.azure.identity.DefaultAzureCredentialBuilder;
```

---

## 2. Client Creation Patterns

### 2.1 With DefaultAzureCredential
#### ✅ CORRECT: Using credential builder
```java
CallAutomationClient client = new CallAutomationClientBuilder()
    .endpoint("https://<resource>.communication.azure.com")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

#### ❌ INCORRECT: Missing endpoint or credential
```java
CallAutomationClient client = new CallAutomationClientBuilder()
    .buildClient();
```

### 2.2 With Connection String
#### ✅ CORRECT: Full connection string
```java
CallAutomationClient client = new CallAutomationClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();
```

#### ❌ INCORRECT: Using both connection string and endpoint
```java
CallAutomationClient client = new CallAutomationClientBuilder()
    .connectionString("<connection-string>")
    .endpoint("https://...")
    .buildClient();
```

---

## 3. Outbound Call Patterns

### 3.1 Create Call with Options
#### ✅ CORRECT: Full CreateCallOptions setup
```java
PhoneNumberIdentifier target = new PhoneNumberIdentifier("+14255551234");
PhoneNumberIdentifier caller = new PhoneNumberIdentifier("+14255550100");

CreateCallOptions options = new CreateCallOptions(
    new CommunicationUserIdentifier("<user-id>"),
    List.of(target))
    .setSourceCallerId(caller)
    .setCallbackUrl("https://your-app.com/api/callbacks");

CreateCallResult result = client.createCall(options);
```

#### ❌ INCORRECT: Missing callback URL
```java
CreateCallOptions options = new CreateCallOptions(
    new CommunicationUserIdentifier("<user-id>"),
    List.of(target));
// Missing setCallbackUrl
```

---

## 4. Answer Call Patterns

### 4.1 Answer Incoming Call
#### ✅ CORRECT: With context and callback URL
```java
AnswerCallOptions options = new AnswerCallOptions(
    incomingCallContext,
    "https://your-app.com/api/callbacks");

AnswerCallResult result = client.answerCall(options);
CallConnection callConnection = result.getCallConnection();
```

#### ❌ INCORRECT: Missing callback URL parameter
```java
AnswerCallOptions options = new AnswerCallOptions(incomingCallContext);
```

---

## 5. Media Operations

### 5.1 Play Text-to-Speech
#### ✅ CORRECT: TextSource with voice configuration
```java
CallMedia callMedia = callConnection.getCallMedia();

TextSource textSource = new TextSource()
    .setText("Welcome to Contoso.")
    .setVoiceName("en-US-JennyNeural");

PlayOptions playOptions = new PlayOptions(
    List.of(textSource),
    List.of(new CommunicationUserIdentifier("<target-user>")));

callMedia.play(playOptions);
```

#### ❌ INCORRECT: Using play without PlayOptions
```java
callMedia.play(textSource);
```

### 5.2 DTMF Recognition
#### ✅ CORRECT: Full recognition options
```java
CallMediaRecognizeDtmfOptions recognizeOptions = new CallMediaRecognizeDtmfOptions(
    new CommunicationUserIdentifier("<target-user>"),
    5)
    .setInterToneTimeout(Duration.ofSeconds(5))
    .setStopTones(List.of(DtmfTone.POUND))
    .setInitialSilenceTimeout(Duration.ofSeconds(15))
    .setPlayPrompt(new TextSource().setText("Enter your PIN."));

callMedia.startRecognizing(recognizeOptions);
```

---

## 6. Recording Operations

### 6.1 Start Recording
#### ✅ CORRECT: With recording options
```java
CallRecording callRecording = client.getCallRecording();

StartRecordingOptions recordingOptions = new StartRecordingOptions(
    new ServerCallLocator("<server-call-id>"))
    .setRecordingChannel(RecordingChannel.MIXED)
    .setRecordingContent(RecordingContent.AUDIO_VIDEO)
    .setRecordingFormat(RecordingFormat.MP4);

RecordingStateResult recordingResult = callRecording.start(recordingOptions);
```

#### ❌ INCORRECT: Using deprecated method
```java
callRecording.startRecording(serverCallId);
```

### 6.2 Recording Lifecycle
#### ✅ CORRECT: Proper pause/resume/stop flow
```java
callRecording.pause(recordingId);
callRecording.resume(recordingId);
callRecording.stop(recordingId);
```

---

## 7. Event Handling

### 7.1 Parse Webhook Events
#### ✅ CORRECT: Using CallAutomationEventParser
```java
List<CallAutomationEventBase> events = CallAutomationEventParser.parseEvents(requestBody);

for (CallAutomationEventBase event : events) {
    if (event instanceof CallConnected) {
        CallConnected connected = (CallConnected) event;
        System.out.println("Call connected: " + connected.getCallConnectionId());
    } else if (event instanceof RecognizeCompleted) {
        RecognizeCompleted recognized = (RecognizeCompleted) event;
        DtmfResult dtmfResult = (DtmfResult) recognized.getRecognizeResult();
    }
}
```

#### ❌ INCORRECT: Manual JSON parsing without type safety
```java
JsonObject json = JsonParser.parseString(requestBody).getAsJsonObject();
String eventType = json.get("type").getAsString();
```

---

## 8. Error Handling

### 8.1 HTTP Response Exception
#### ✅ CORRECT: Proper exception handling
```java
try {
    client.answerCall(options);
} catch (HttpResponseException e) {
    if (e.getResponse().getStatusCode() == 404) {
        System.out.println("Call not found or already ended");
    } else if (e.getResponse().getStatusCode() == 400) {
        System.out.println("Invalid request: " + e.getMessage());
    }
}
```

#### ❌ INCORRECT: Catching generic Exception
```java
try {
    client.answerCall(options);
} catch (Exception e) {
    System.out.println("Error");
}
```

---

## 9. Call Connection Operations

### 9.1 Add Participant
#### ✅ CORRECT: With options
```java
CommunicationUserIdentifier participant = new CommunicationUserIdentifier("<user-id>");
AddParticipantOptions addOptions = new AddParticipantOptions(participant)
    .setInvitationTimeout(Duration.ofSeconds(30));

AddParticipantResult result = callConnection.addParticipant(addOptions);
```

### 9.2 Hang Up
#### ✅ CORRECT: Specifying forEveryone flag
```java
callConnection.hangUp(true);  // Hang up for all participants
callConnection.hangUp(false); // Hang up only this leg
```

---

## 10. Required Dependencies

### 10.1 Maven Configuration
#### ✅ CORRECT: Current version
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-callautomation</artifactId>
    <version>1.6.0</version>
</dependency>
```

#### ❌ INCORRECT: Using deprecated package
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-callingserver</artifactId>
    <version>1.0.0-beta.5</version>
</dependency>
```
