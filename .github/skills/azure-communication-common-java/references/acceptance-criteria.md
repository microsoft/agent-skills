# Azure Communication Common SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-communication-common`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/communication/azure-communication-common
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Credential Imports

#### ✅ CORRECT: Token Credential
```java
import com.azure.communication.common.CommunicationTokenCredential;
import com.azure.communication.common.CommunicationTokenRefreshOptions;
```

### 1.2 Identifier Imports

#### ✅ CORRECT: Communication Identifiers
```java
import com.azure.communication.common.CommunicationIdentifier;
import com.azure.communication.common.CommunicationUserIdentifier;
import com.azure.communication.common.PhoneNumberIdentifier;
import com.azure.communication.common.MicrosoftTeamsUserIdentifier;
import com.azure.communication.common.UnknownIdentifier;
import com.azure.communication.common.CommunicationCloudEnvironment;
```

---

## 2. Token Credential Patterns

### 2.1 ✅ CORRECT: Static Token
```java
String userToken = System.getenv("AZURE_COMMUNICATION_USER_TOKEN");
CommunicationTokenCredential credential = new CommunicationTokenCredential(userToken);
```

### 2.2 ✅ CORRECT: Proactive Token Refresh
```java
import java.util.concurrent.Callable;

Callable<String> tokenRefresher = () -> {
    return fetchNewTokenFromServer();
};

CommunicationTokenRefreshOptions refreshOptions = new CommunicationTokenRefreshOptions(tokenRefresher)
    .setRefreshProactively(true)
    .setInitialToken(currentToken);

CommunicationTokenCredential credential = new CommunicationTokenCredential(refreshOptions);
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded token
```java
// WRONG - hardcoded token
CommunicationTokenCredential credential = new CommunicationTokenCredential("eyJ...");
```

---

## 3. Identifier Patterns

### 3.1 ✅ CORRECT: CommunicationUserIdentifier
```java
CommunicationUserIdentifier user = new CommunicationUserIdentifier("8:acs:resource-id_user-id");
String rawId = user.getId();
```

### 3.2 ✅ CORRECT: PhoneNumberIdentifier
```java
PhoneNumberIdentifier phone = new PhoneNumberIdentifier("+14255551234");
String phoneNumber = phone.getPhoneNumber();
```

### 3.3 ✅ CORRECT: MicrosoftTeamsUserIdentifier
```java
MicrosoftTeamsUserIdentifier teamsUser = new MicrosoftTeamsUserIdentifier("<teams-user-id>")
    .setCloudEnvironment(CommunicationCloudEnvironment.PUBLIC);
```

### 3.4 ✅ CORRECT: Type Checking Identifiers
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
    }
}
```

---

## 4. Token Management

### 4.1 ✅ CORRECT: Get Token
```java
import com.azure.core.credential.AccessToken;

AccessToken accessToken = credential.getToken();
System.out.println("Token expires: " + accessToken.getExpiresAt());
```

### 4.2 ✅ CORRECT: Dispose Credential
```java
credential.close();

// Or use try-with-resources
try (CommunicationTokenCredential cred = new CommunicationTokenCredential(options)) {
    // Use credential
}
```

---

## 5. Cloud Environments

### 5.1 ✅ CORRECT: Setting Cloud Environment
```java
import com.azure.communication.common.CommunicationCloudEnvironment;

CommunicationCloudEnvironment publicCloud = CommunicationCloudEnvironment.PUBLIC;
CommunicationCloudEnvironment govCloud = CommunicationCloudEnvironment.GCCH;
CommunicationCloudEnvironment dodCloud = CommunicationCloudEnvironment.DOD;

MicrosoftTeamsUserIdentifier teamsUser = new MicrosoftTeamsUserIdentifier("<user-id>")
    .setCloudEnvironment(CommunicationCloudEnvironment.GCCH);
```

---

## 6. Best Practices Checklist

- [ ] Use `setRefreshProactively(true)` for long-lived clients
- [ ] Use environment variables for tokens
- [ ] Never log or expose full tokens
- [ ] Dispose of credentials when no longer needed
- [ ] Handle token refresh failures gracefully
- [ ] Use specific identifier types, not raw strings
