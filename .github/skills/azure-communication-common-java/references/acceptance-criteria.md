# Azure Communication Common Acceptance Criteria

**SDK**: `com.azure:azure-communication-common`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/communication/azure-communication-common
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Credential Imports
#### ✅ CORRECT: Full credential imports
```java
import com.azure.communication.common.CommunicationTokenCredential;
import com.azure.communication.common.CommunicationTokenRefreshOptions;
```

### 1.2 Identifier Imports
#### ✅ CORRECT: All identifier types
```java
import com.azure.communication.common.CommunicationUserIdentifier;
import com.azure.communication.common.PhoneNumberIdentifier;
import com.azure.communication.common.MicrosoftTeamsUserIdentifier;
import com.azure.communication.common.UnknownIdentifier;
import com.azure.communication.common.CommunicationIdentifier;
```

### 1.3 Cloud Environment Import
#### ✅ CORRECT: Cloud environment enum
```java
import com.azure.communication.common.CommunicationCloudEnvironment;
```

---

## 2. CommunicationTokenCredential Patterns

### 2.1 Static Token (Simple)
#### ✅ CORRECT: Direct token initialization
```java
String userToken = "<user-access-token>";
CommunicationTokenCredential credential = new CommunicationTokenCredential(userToken);
```

#### ❌ INCORRECT: Null token
```java
CommunicationTokenCredential credential = new CommunicationTokenCredential(null);
```

### 2.2 Proactive Token Refresh
#### ✅ CORRECT: With refresh callback and proactive refresh
```java
Callable<String> tokenRefresher = () -> {
    return fetchNewTokenFromServer();
};

CommunicationTokenRefreshOptions refreshOptions = new CommunicationTokenRefreshOptions(tokenRefresher)
    .setRefreshProactively(true)
    .setInitialToken(currentToken);

CommunicationTokenCredential credential = new CommunicationTokenCredential(refreshOptions);
```

#### ❌ INCORRECT: Missing proactive refresh for long-lived clients
```java
CommunicationTokenRefreshOptions refreshOptions = new CommunicationTokenRefreshOptions(tokenRefresher);
// Missing setRefreshProactively(true) for long-lived client
```

### 2.3 Async Token Refresh
#### ✅ CORRECT: CompletableFuture-based refresh
```java
Callable<String> asyncRefresher = () -> {
    CompletableFuture<String> future = fetchTokenAsync();
    return future.get();
};

CommunicationTokenRefreshOptions options = new CommunicationTokenRefreshOptions(asyncRefresher)
    .setRefreshProactively(true);

CommunicationTokenCredential credential = new CommunicationTokenCredential(options);
```

---

## 3. Identifier Patterns

### 3.1 CommunicationUserIdentifier
#### ✅ CORRECT: ACS user identifier
```java
CommunicationUserIdentifier user = new CommunicationUserIdentifier("8:acs:resource-id_user-id");
String rawId = user.getId();
```

#### ❌ INCORRECT: Invalid format
```java
CommunicationUserIdentifier user = new CommunicationUserIdentifier("invalid-id");
```

### 3.2 PhoneNumberIdentifier
#### ✅ CORRECT: E.164 format
```java
PhoneNumberIdentifier phone = new PhoneNumberIdentifier("+14255551234");
String phoneNumber = phone.getPhoneNumber();
String rawId = phone.getRawId();
```

#### ❌ INCORRECT: Non-E.164 format
```java
PhoneNumberIdentifier phone = new PhoneNumberIdentifier("4255551234");
```

### 3.3 MicrosoftTeamsUserIdentifier
#### ✅ CORRECT: With cloud environment
```java
MicrosoftTeamsUserIdentifier teamsUser = new MicrosoftTeamsUserIdentifier("<teams-user-id>")
    .setCloudEnvironment(CommunicationCloudEnvironment.PUBLIC);
```

#### ✅ CORRECT: Anonymous Teams user
```java
MicrosoftTeamsUserIdentifier anonymousTeamsUser = new MicrosoftTeamsUserIdentifier("<teams-user-id>")
    .setAnonymous(true);
```

### 3.4 UnknownIdentifier
#### ✅ CORRECT: For unknown types
```java
UnknownIdentifier unknown = new UnknownIdentifier("some-raw-id");
```

---

## 4. Identifier Type Checking

### 4.1 instanceof Pattern
#### ✅ CORRECT: Type-safe identifier handling
```java
public void processIdentifier(CommunicationIdentifier identifier) {
    if (identifier instanceof CommunicationUserIdentifier) {
        CommunicationUserIdentifier user = (CommunicationUserIdentifier) identifier;
        System.out.println("ACS User: " + user.getId());
        
    } else if (identifier instanceof PhoneNumberIdentifier) {
        PhoneNumberIdentifier phone = (PhoneNumberIdentifier) identifier;
        System.out.println("Phone: " + phone.getPhoneNumber());
        
    } else if (identifier instanceof MicrosoftTeamsUserIdentifier) {
        MicrosoftTeamsUserIdentifier teams = (MicrosoftTeamsUserIdentifier) identifier;
        System.out.println("Teams User: " + teams.getUserId());
        
    } else if (identifier instanceof UnknownIdentifier) {
        UnknownIdentifier unknown = (UnknownIdentifier) identifier;
        System.out.println("Unknown: " + unknown.getId());
    }
}
```

#### ❌ INCORRECT: Unchecked casting
```java
CommunicationUserIdentifier user = (CommunicationUserIdentifier) identifier;
// May throw ClassCastException
```

---

## 5. Entra ID Authentication

### 5.1 EntraCommunicationTokenCredentialOptions
#### ✅ CORRECT: Teams Phone Extensibility
```java
InteractiveBrowserCredential entraCredential = new InteractiveBrowserCredentialBuilder()
    .clientId("<your-client-id>")
    .tenantId("<your-tenant-id>")
    .redirectUrl("<your-redirect-uri>")
    .build();

String resourceEndpoint = "https://<resource>.communication.azure.com";
List<String> scopes = Arrays.asList(
    "https://auth.msft.communication.azure.com/TeamsExtension.ManageCalls"
);

EntraCommunicationTokenCredentialOptions entraOptions = 
    new EntraCommunicationTokenCredentialOptions(entraCredential, resourceEndpoint)
        .setScopes(scopes);

CommunicationTokenCredential credential = new CommunicationTokenCredential(entraOptions);
```

---

## 6. Token Access

### 6.1 Synchronous Token Access
#### ✅ CORRECT: Get token synchronously
```java
AccessToken accessToken = credential.getToken();
System.out.println("Token expires: " + accessToken.getExpiresAt());
```

### 6.2 Asynchronous Token Access
#### ✅ CORRECT: Reactive token access
```java
credential.getTokenAsync()
    .subscribe(token -> {
        System.out.println("Expires: " + token.getExpiresAt());
    });
```

---

## 7. Resource Cleanup

### 7.1 Close Credential
#### ✅ CORRECT: Explicit close
```java
credential.close();
```

#### ✅ CORRECT: Try-with-resources
```java
try (CommunicationTokenCredential cred = new CommunicationTokenCredential(options)) {
    chatClient.doSomething();
}
```

#### ❌ INCORRECT: Never closing credential
```java
CommunicationTokenCredential credential = new CommunicationTokenCredential(options);
// Use credential
// Missing close() - resource leak
```

---

## 8. Cloud Environments

### 8.1 Available Environments
#### ✅ CORRECT: Using environment constants
```java
CommunicationCloudEnvironment publicCloud = CommunicationCloudEnvironment.PUBLIC;
CommunicationCloudEnvironment govCloud = CommunicationCloudEnvironment.GCCH;
CommunicationCloudEnvironment dodCloud = CommunicationCloudEnvironment.DOD;

MicrosoftTeamsUserIdentifier teamsUser = new MicrosoftTeamsUserIdentifier("<user-id>")
    .setCloudEnvironment(CommunicationCloudEnvironment.GCCH);
```

---

## 9. Identifier Parsing

### 9.1 Parse Raw ID
#### ✅ CORRECT: Prefix-based parsing
```java
public CommunicationIdentifier parseIdentifier(String rawId) {
    if (rawId.startsWith("8:acs:")) {
        return new CommunicationUserIdentifier(rawId);
    } else if (rawId.startsWith("4:")) {
        String phone = rawId.substring(2);
        return new PhoneNumberIdentifier(phone);
    } else if (rawId.startsWith("8:orgid:")) {
        String teamsId = rawId.substring(8);
        return new MicrosoftTeamsUserIdentifier(teamsId);
    } else {
        return new UnknownIdentifier(rawId);
    }
}
```

---

## 10. Required Dependencies

### 10.1 Maven Configuration
#### ✅ CORRECT: Current version
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-common</artifactId>
    <version>1.4.0</version>
</dependency>
```

---

## 11. Best Practices

### 11.1 Token Security
- Never log or expose full tokens
- Use proactive refresh for long-lived clients
- Dispose of credentials when no longer needed

### 11.2 Identifier Handling
- Use specific identifier types, not raw strings
- Always check identifier type before casting
- Handle unknown identifiers gracefully
