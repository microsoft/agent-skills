# Azure Communication Call Automation SDK for Java - Examples

Comprehensive code examples for the Azure Communication Call Automation SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Creating Outbound Calls](#creating-outbound-calls)
- [Answering Inbound Calls](#answering-inbound-calls)
- [Playing Audio/TTS](#playing-audiotts)
- [Recognizing DTMF Tones](#recognizing-dtmf-tones)
- [Recording Calls](#recording-calls)
- [Transfer Calls](#transfer-calls)
- [Add/Remove Participants](#addremove-participants)
- [Handling Call Events](#handling-call-events)
- [Async Client Patterns](#async-client-patterns)
- [Error Handling](#error-handling)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-callautomation</artifactId>
    <version>1.5.2</version>
</dependency>
```

## Client Creation

### Sync Client

```java
import com.azure.communication.callautomation.CallAutomationClient;
import com.azure.communication.callautomation.CallAutomationClientBuilder;

CallAutomationClient callAutomationClient = new CallAutomationClientBuilder()
    .connectionString("<Azure Communication Services connection string>")
    .buildClient();
```

### Async Client

```java
import com.azure.communication.callautomation.CallAutomationAsyncClient;

CallAutomationAsyncClient asyncClient = new CallAutomationClientBuilder()
    .connectionString("<acsConnectionString>")
    .buildAsyncClient();
```

## Creating Outbound Calls

### Single PSTN Call

```java
import com.azure.communication.callautomation.models.*;
import com.azure.communication.common.PhoneNumberIdentifier;
import com.azure.core.util.Context;

String callbackUri = "https://<myendpoint>/Events";
PhoneNumberIdentifier callerIdNumber = new PhoneNumberIdentifier("+18001234567");
PhoneNumberIdentifier target = new PhoneNumberIdentifier("+16471234567");

CallInvite callInvite = new CallInvite(target, callerIdNumber);
CreateCallOptions createCallOptions = new CreateCallOptions(callInvite, callbackUri);

// Optional: Add AI capabilities
CallIntelligenceOptions callIntelligenceOptions = new CallIntelligenceOptions()
    .setCognitiveServicesEndpoint("https://your-cognitive-services.cognitiveservices.azure.com/");
createCallOptions.setCallIntelligenceOptions(callIntelligenceOptions);

Response<CreateCallResult> result = callAutomationClient.createCallWithResponse(
    createCallOptions, 
    Context.NONE
);
String callConnectionId = result.getValue().getCallConnectionProperties().getCallConnectionId();
```

### Group Call

```java
import com.azure.communication.common.CommunicationUserIdentifier;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

List<CommunicationIdentifier> targets = new ArrayList<>(Arrays.asList(
    new PhoneNumberIdentifier("+16471234567"),
    new CommunicationUserIdentifier("<user_id>")
));

CreateGroupCallOptions groupCallOptions = new CreateGroupCallOptions(targets, callbackUri);
groupCallOptions.setSourceCallIdNumber(callerIdNumber);

Response<CreateCallResult> response = callAutomationClient.createGroupCallWithResponse(
    groupCallOptions, 
    Context.NONE
);
```

## Answering Inbound Calls

### Basic Answer

```java
import com.azure.communication.callautomation.models.*;

String incomingCallContext = "<IncomingCallContext_From_IncomingCall_Event>";
String callbackUri = "https://<myendpoint>/Events";

AnswerCallOptions answerCallOptions = new AnswerCallOptions(incomingCallContext, callbackUri);
Response<AnswerCallResult> response = callAutomationClient.answerCallWithResponse(
    answerCallOptions, 
    Context.NONE
);
```

### Answer with AI Capabilities

```java
CallIntelligenceOptions callIntelligenceOptions = new CallIntelligenceOptions()
    .setCognitiveServicesEndpoint("https://cognitive-services.cognitiveservices.azure.com/");

AnswerCallOptions answerCallOptions = new AnswerCallOptions(incomingCallContext, callbackUri)
    .setCallIntelligenceOptions(callIntelligenceOptions);

Response<AnswerCallResult> response = callAutomationClient.answerCallWithResponse(
    answerCallOptions, 
    Context.NONE
);
```

### Answer with Transcription

```java
TranscriptionOptions transcriptionOptions = new TranscriptionOptions(
    "wss://your-websocket-url",
    TranscriptionTransport.WEBSOCKET,
    "en-US",
    false,
    "your-endpoint-id"
);

AnswerCallOptions answerCallOptions = new AnswerCallOptions(incomingCallContext, callbackUri)
    .setCallIntelligenceOptions(callIntelligenceOptions)
    .setTranscriptionOptions(transcriptionOptions);
```

## Playing Audio/TTS

### Play Text-to-Speech to All

```java
import com.azure.communication.callautomation.CallConnection;

String textToPlay = "Welcome to Contoso. How can I help you today?";

TextSource textSource = new TextSource()
    .setText(textToPlay)
    .setVoiceName("en-US-NancyNeural");

CallConnection callConnection = callAutomationClient.getCallConnection(callConnectionId);
callConnection.getCallMedia().playToAll(textSource);
```

### Play Audio File to Participant

```java
import java.util.Arrays;

CommunicationIdentifier targetParticipant = new PhoneNumberIdentifier("+16471234567");

FileSource playSource = new FileSource()
    .setUrl("https://storage.blob.core.windows.net/audio/welcome.wav")
    .setPlaySourceCacheId("<playSourceId>");  // Optional: cache for repeated playback

var playTo = Arrays.asList(targetParticipant);
PlayOptions playOptions = new PlayOptions(playSource, playTo);

callAutomationClient.getCallConnection(callConnectionId)
    .getCallMedia()
    .playWithResponse(playOptions, Context.NONE);
```

### Play with SSML

```java
String ssmlText = "<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" xml:lang=\"en-US\">" +
    "<voice name=\"en-US-JennyNeural\">Hello, welcome to our service!</voice></speak>";

SsmlSource ssmlSource = new SsmlSource()
    .setSsmlText(ssmlText);

callConnection.getCallMedia().playToAll(ssmlSource);
```

## Recognizing DTMF Tones

### DTMF Recognition

```java
import java.time.Duration;
import java.util.Arrays;

CommunicationIdentifier targetParticipant = new PhoneNumberIdentifier("+16471234567");
int maxTonesToCollect = 3;

TextSource playSource = new TextSource()
    .setText("Please enter 3 digits.")
    .setVoiceName("en-US-ElizabethNeural");

CallMediaRecognizeDtmfOptions recognizeOptions = new CallMediaRecognizeDtmfOptions(
    targetParticipant, 
    maxTonesToCollect
)
    .setInitialSilenceTimeout(Duration.ofSeconds(30))
    .setPlayPrompt(playSource)
    .setInterToneTimeout(Duration.ofSeconds(5))
    .setInterruptPrompt(true)
    .setStopTones(Arrays.asList(DtmfTone.POUND));

callAutomationClient.getCallConnection(callConnectionId)
    .getCallMedia()
    .startRecognizingWithResponse(recognizeOptions, Context.NONE);
```

### Speech or DTMF Recognition

```java
CallMediaRecognizeSpeechOrDtmfOptions recognizeOptions = 
    new CallMediaRecognizeSpeechOrDtmfOptions(
        targetParticipant, 
        maxTonesToCollect, 
        Duration.ofMillis(1000)
    )
    .setPlayPrompt(playSource)
    .setInitialSilenceTimeout(Duration.ofSeconds(30))
    .setInterruptPrompt(true)
    .setOperationContext("OpenQuestionSpeechOrDtmf");

callAutomationClient.getCallConnection(callConnectionId)
    .getCallMedia()
    .startRecognizingWithResponse(recognizeOptions, Context.NONE);
```

### Choice Recognition

```java
import java.util.List;

List<RecognitionChoice> choices = Arrays.asList(
    new RecognitionChoice()
        .setLabel("Confirm")
        .setPhrases(Arrays.asList("Confirm", "Yes", "One"))
        .setTone(DtmfTone.ONE),
    new RecognitionChoice()
        .setLabel("Cancel")
        .setPhrases(Arrays.asList("Cancel", "No", "Two"))
        .setTone(DtmfTone.TWO)
);

TextSource playSource = new TextSource()
    .setText("Say Confirm or press 1 to confirm, or say Cancel or press 2 to cancel.")
    .setVoiceName("en-US-ElizabethNeural");

CallMediaRecognizeChoiceOptions recognizeOptions = new CallMediaRecognizeChoiceOptions(
    targetParticipant, 
    choices
)
    .setInterruptPrompt(true)
    .setInitialSilenceTimeout(Duration.ofSeconds(30))
    .setPlayPrompt(playSource)
    .setOperationContext("AppointmentReminderMenu");

callAutomationClient.getCallConnection(callConnectionId)
    .getCallMedia()
    .startRecognizingWithResponse(recognizeOptions, Context.NONE);
```

### Send DTMF Tones

```java
List<DtmfTone> tones = Arrays.asList(
    DtmfTone.ONE, 
    DtmfTone.TWO, 
    DtmfTone.THREE, 
    DtmfTone.POUND
);

SendDtmfTonesOptions options = new SendDtmfTonesOptions(
    tones, 
    new PhoneNumberIdentifier(targetPhoneNumber)
);
options.setOperationContext("dtmfs-to-ivr");

callAutomationClient.getCallConnection(callConnectionId)
    .getCallMedia()
    .sendDtmfTonesWithResponse(options, Context.NONE);
```

## Recording Calls

### Start Recording

```java
import com.azure.communication.callautomation.CallRecording;

CallRecording callRecording = callAutomationClient.getCallRecording();

StartRecordingOptions startRecordingOptions = new StartRecordingOptions(
    new ServerCallLocator(serverCallId)
)
    .setRecordingContent(RecordingContent.AUDIO_VIDEO)
    .setRecordingChannel(RecordingChannel.MIXED)
    .setRecordingFormat(RecordingFormat.MP4);

Response<RecordingStateResult> response = callRecording.startWithResponse(
    startRecordingOptions, 
    Context.NONE
);

String recordingId = response.getValue().getRecordingId();
```

### Pause/Resume Recording

```java
// Pause
callRecording.pause(recordingId);

// Resume
callRecording.resume(recordingId);
```

### Stop Recording

```java
callRecording.stop(recordingId);
```

### Download Recording

```java
callRecording.downloadToWithResponse(
    recordingUrl,
    Paths.get("recording.mp4"),
    null,  // HttpRange (optional)
    Context.NONE
);
```

## Transfer Calls

### Blind Transfer

```java
CommunicationIdentifier transferDestination = new PhoneNumberIdentifier("+16471234567");

TransferCallToParticipantOptions transferOptions = new TransferCallToParticipantOptions(
    transferDestination
);

Response<TransferCallResult> response = callAutomationClient
    .getCallConnection(callConnectionId)
    .transferCallToParticipantWithResponse(transferOptions, Context.NONE);
```

### Transfer with Announcement

```java
TextSource transferee Prompt = new TextSource()
    .setText("Please hold while we transfer your call.")
    .setVoiceName("en-US-NancyNeural");

TransferCallToParticipantOptions transferOptions = new TransferCallToParticipantOptions(
    transferDestination
)
    .setSourceCallerIdNumber(new PhoneNumberIdentifier("+18001234567"))
    .setTransfereeGreeting(transfereePrompt);

callAutomationClient.getCallConnection(callConnectionId)
    .transferCallToParticipantWithResponse(transferOptions, Context.NONE);
```

## Add/Remove Participants

### Add Participant

```java
CommunicationIdentifier participant = new PhoneNumberIdentifier("+16471234567");
PhoneNumberIdentifier callerId = new PhoneNumberIdentifier("+18001234567");

AddParticipantOptions addOptions = new AddParticipantOptions(
    new CallInvite(participant, callerId)
);

Response<AddParticipantResult> response = callAutomationClient
    .getCallConnection(callConnectionId)
    .addParticipantWithResponse(addOptions, Context.NONE);
```

### Remove Participant

```java
CommunicationIdentifier participant = new PhoneNumberIdentifier("+16471234567");

callAutomationClient.getCallConnection(callConnectionId)
    .removeParticipant(participant);
```

### List Participants

```java
ListParticipantsResult participants = callAutomationClient
    .getCallConnection(callConnectionId)
    .listParticipants();

participants.getValues().forEach(p -> 
    System.out.println("Participant: " + p.getIdentifier().getRawId()));
```

## Handling Call Events

### Event Grid Webhook Handler (Spring Boot)

```java
import com.azure.communication.callautomation.CallAutomationEventParser;
import com.azure.communication.callautomation.models.events.*;
import org.springframework.web.bind.annotation.*;

@RestController
public class CallbackController {

    @PostMapping("/Events")
    public ResponseEntity<String> handleCallEvents(@RequestBody String requestBody) {
        List<CallAutomationEventBase> events = CallAutomationEventParser.parseEvents(requestBody);
        
        for (CallAutomationEventBase event : events) {
            String callConnectionId = event.getCallConnectionId();
            
            if (event instanceof CallConnected) {
                handleCallConnected((CallConnected) event);
            } else if (event instanceof RecognizeCompleted) {
                handleRecognizeCompleted((RecognizeCompleted) event);
            } else if (event instanceof RecognizeFailed) {
                handleRecognizeFailed((RecognizeFailed) event);
            } else if (event instanceof PlayCompleted) {
                handlePlayCompleted((PlayCompleted) event);
            } else if (event instanceof CallDisconnected) {
                handleCallDisconnected((CallDisconnected) event);
            }
        }
        
        return ResponseEntity.ok("");
    }
    
    private void handleCallConnected(CallConnected event) {
        System.out.println("Call connected: " + event.getCallConnectionId());
    }
    
    private void handleRecognizeCompleted(RecognizeCompleted event) {
        CollectTonesResult result = (CollectTonesResult) event.getRecognizeResult();
        String tones = result.getTones().stream()
            .map(DtmfTone::toString)
            .collect(Collectors.joining());
        System.out.println("DTMF tones received: " + tones);
    }
    
    private void handleRecognizeFailed(RecognizeFailed event) {
        System.out.println("Recognition failed: " + event.getResultInformation().getMessage());
    }
    
    private void handlePlayCompleted(PlayCompleted event) {
        System.out.println("Play completed: " + event.getOperationContext());
    }
    
    private void handleCallDisconnected(CallDisconnected event) {
        System.out.println("Call disconnected: " + event.getCallConnectionId());
    }
}
```

## Async Client Patterns

### Create Call Async

```java
asyncClient.createCall(callInvite, callbackUri)
    .subscribe(
        result -> System.out.println("Call ID: " + 
            result.getCallConnectionProperties().getCallConnectionId()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### Play Audio Async

```java
asyncClient.getCallConnectionAsync(callConnectionId)
    .getCallMediaAsync()
    .playToAll(textSource)
    .subscribe(
        unused -> System.out.println("Play started"),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### Recognize Async

```java
asyncClient.getCallConnectionAsync(callConnectionId)
    .getCallMediaAsync()
    .startRecognizingWithResponse(recognizeOptions)
    .subscribe(
        response -> System.out.println("Recognition started"),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

## Error Handling

### Sync Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    Response<CreateCallResult> result = callAutomationClient.createCallWithResponse(
        createCallOptions, 
        Context.NONE
    );
} catch (HttpResponseException e) {
    System.err.println("HTTP Status: " + e.getResponse().getStatusCode());
    System.err.println("Error: " + e.getMessage());
} catch (Exception e) {
    System.err.println("Unexpected error: " + e.getMessage());
}
```

### Async Error Handling

```java
asyncClient.createCall(callInvite, callbackUri)
    .subscribe(
        result -> System.out.println("Success"),
        error -> {
            if (error instanceof HttpResponseException) {
                HttpResponseException httpError = (HttpResponseException) error;
                System.err.println("HTTP error: " + httpError.getResponse().getStatusCode());
            } else {
                System.err.println("Error: " + error.getMessage());
            }
        }
    );
```

### Common Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid request |
| 401 | Authentication failed |
| 403 | Not authorized |
| 404 | Call/resource not found |
| 429 | Rate limited |
| 500 | Server error |
