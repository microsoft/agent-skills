# Azure Communication CallingServer (Legacy) Acceptance Criteria

**SDK**: `com.azure:azure-communication-callingserver` (DEPRECATED)
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/communication
**Purpose**: Skill testing acceptance criteria for validating migration guidance and legacy code maintenance

---

## ⚠️ DEPRECATION NOTICE

This SDK is **deprecated**. New projects should use `azure-communication-callautomation` instead.

---

## 1. Migration Guidance

### 1.1 Package Migration
#### ✅ CORRECT: Recommend migration to Call Automation
```xml
<!-- NEW (recommended) -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-callautomation</artifactId>
    <version>1.6.0</version>
</dependency>
```

#### ❌ INCORRECT: Recommending deprecated package for new projects
```xml
<!-- OLD (deprecated) - Do not use for new projects -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-callingserver</artifactId>
    <version>1.0.0-beta.5</version>
</dependency>
```

---

## 2. Legacy Import Patterns (For Maintenance Only)

### 2.1 Legacy Client Imports
#### ⚠️ LEGACY: Only for existing codebases
```java
import com.azure.communication.callingserver.CallingServerClient;
import com.azure.communication.callingserver.CallingServerClientBuilder;
```

#### ✅ MIGRATION: New client imports
```java
import com.azure.communication.callautomation.CallAutomationClient;
import com.azure.communication.callautomation.CallAutomationClientBuilder;
```

---

## 3. Class Name Changes Reference

### 3.1 Client Class Mapping
| CallingServer (Old) | Call Automation (New) |
|---------------------|----------------------|
| `CallingServerClient` | `CallAutomationClient` |
| `CallingServerClientBuilder` | `CallAutomationClientBuilder` |
| `CallConnection` | `CallConnection` (same) |
| `ServerCall` | Removed - use `CallConnection` |

---

## 4. Legacy Client Creation (For Reference Only)

### 4.1 Legacy Pattern
#### ⚠️ LEGACY: CallingServerClient creation
```java
CallingServerClient client = new CallingServerClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();
```

#### ✅ MIGRATION: CallAutomationClient creation
```java
CallAutomationClient client = new CallAutomationClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();
```

---

## 5. Legacy Recording Operations

### 5.1 Legacy Recording Start
#### ⚠️ LEGACY: Old recording pattern
```java
StartRecordingOptions options = new StartRecordingOptions(serverCallId)
    .setRecordingStateCallbackUri(callbackUri);

StartCallRecordingResult result = client.startRecording(options);
String recordingId = result.getRecordingId();
```

#### ✅ MIGRATION: New recording pattern
```java
CallRecording callRecording = client.getCallRecording();

StartRecordingOptions recordingOptions = new StartRecordingOptions(
    new ServerCallLocator("<server-call-id>"))
    .setRecordingChannel(RecordingChannel.MIXED)
    .setRecordingContent(RecordingContent.AUDIO_VIDEO)
    .setRecordingFormat(RecordingFormat.MP4);

RecordingStateResult recordingResult = callRecording.start(recordingOptions);
```

---

## 6. Migration Recommendations

### 6.1 When to Migrate
- All new projects should use `azure-communication-callautomation`
- Existing projects should plan migration during next major update cycle
- Legacy code maintenance is acceptable but avoid expanding usage

### 6.2 Migration Steps
1. Update Maven dependency to `azure-communication-callautomation`
2. Replace `CallingServerClient` with `CallAutomationClient`
3. Update import statements from `callingserver` to `callautomation`
4. Replace `ServerCall` usage with `CallConnection`
5. Update recording API calls to use new patterns
6. Test all call flows thoroughly after migration

---

## 7. Error Handling in Legacy Code

### 7.1 Exception Handling
#### ⚠️ LEGACY: Legacy exception handling
```java
try {
    client.startRecording(options);
} catch (CallingServerErrorException e) {
    System.out.println("Error: " + e.getMessage());
}
```

#### ✅ MIGRATION: Modern exception handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    callRecording.start(options);
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

---

## 8. Skill Response Requirements

### 8.1 For Legacy Code Questions
- Always include deprecation warning
- Provide migration guidance
- Show both legacy and modern patterns

### 8.2 For New Development Questions
- Never recommend CallingServer SDK
- Always redirect to CallAutomation SDK
- Reference `azure-communication-callautomation-java` skill
