# Azure Communication Chat SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-communication-chat`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/communication/azure-communication-chat
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Client and Builder
```java
import com.azure.communication.chat.ChatClient;
import com.azure.communication.chat.ChatClientBuilder;
import com.azure.communication.chat.ChatAsyncClient;
import com.azure.communication.chat.ChatThreadClient;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.communication.common.CommunicationTokenCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Chat Models
```java
import com.azure.communication.chat.models.ChatParticipant;
import com.azure.communication.chat.models.ChatMessage;
import com.azure.communication.chat.models.ChatMessageType;
import com.azure.communication.chat.models.ChatThreadProperties;
import com.azure.communication.chat.models.CreateChatThreadOptions;
import com.azure.communication.chat.models.CreateChatThreadResult;
import com.azure.communication.chat.models.SendChatMessageOptions;
import com.azure.communication.chat.models.SendChatMessageResult;
import com.azure.communication.chat.models.ChatMessageReadReceipt;
```

#### ✅ CORRECT: Communication Identifiers
```java
import com.azure.communication.common.CommunicationUserIdentifier;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```java
// WRONG - Models not in main package
import com.azure.communication.chat.ChatParticipant;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with CommunicationTokenCredential
```java
String endpoint = System.getenv("AZURE_COMMUNICATION_ENDPOINT");
String userAccessToken = System.getenv("AZURE_COMMUNICATION_USER_TOKEN");

CommunicationTokenCredential credential = new CommunicationTokenCredential(userAccessToken);

ChatClient chatClient = new ChatClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildClient();
```

### 2.2 ✅ CORRECT: Async Client
```java
ChatAsyncClient chatAsyncClient = new ChatClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildAsyncClient();
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```java
// WRONG - hardcoded values
ChatClient chatClient = new ChatClientBuilder()
    .endpoint("https://myresource.communication.azure.com")
    .credential(new CommunicationTokenCredential("hardcoded-token"))
    .buildClient();
```

---

## 3. Chat Thread Operations

### 3.1 ✅ CORRECT: Create Chat Thread
```java
List<ChatParticipant> participants = new ArrayList<>();

ChatParticipant participant1 = new ChatParticipant()
    .setCommunicationIdentifier(new CommunicationUserIdentifier("<user-id-1>"))
    .setDisplayName("Alice");

participants.add(participant1);

CreateChatThreadOptions options = new CreateChatThreadOptions("Project Discussion")
    .setParticipants(participants);

CreateChatThreadResult result = chatClient.createChatThread(options);
String threadId = result.getChatThread().getId();

ChatThreadClient threadClient = chatClient.getChatThreadClient(threadId);
```

### 3.2 ✅ CORRECT: Delete Chat Thread
```java
chatClient.deleteChatThread(threadId);
```

---

## 4. Message Operations

### 4.1 ✅ CORRECT: Send Message
```java
SendChatMessageOptions messageOptions = new SendChatMessageOptions()
    .setContent("Hello, team!")
    .setSenderDisplayName("Alice")
    .setType(ChatMessageType.TEXT);

SendChatMessageResult sendResult = threadClient.sendMessage(messageOptions);
String messageId = sendResult.getId();
```

### 4.2 ✅ CORRECT: List Messages
```java
PagedIterable<ChatMessage> messages = threadClient.listMessages();

for (ChatMessage message : messages) {
    System.out.println("Content: " + message.getContent().getMessage());
    System.out.println("Sender: " + message.getSenderDisplayName());
}
```

### 4.3 ✅ CORRECT: Update and Delete Messages
```java
threadClient.updateMessage(messageId, new UpdateChatMessageOptions()
    .setContent("Updated content"));

threadClient.deleteMessage(messageId);
```

---

## 5. Participant Operations

### 5.1 ✅ CORRECT: Add Participants
```java
List<ChatParticipant> newParticipants = new ArrayList<>();
newParticipants.add(new ChatParticipant()
    .setCommunicationIdentifier(new CommunicationUserIdentifier("<new-user-id>"))
    .setDisplayName("Charlie"));

threadClient.addParticipants(newParticipants);
```

### 5.2 ✅ CORRECT: Remove Participant
```java
CommunicationUserIdentifier userToRemove = new CommunicationUserIdentifier("<user-id>");
threadClient.removeParticipant(userToRemove);
```

---

## 6. Read Receipts

### 6.1 ✅ CORRECT: Send Read Receipt
```java
threadClient.sendReadReceipt(messageId);
```

### 6.2 ✅ CORRECT: List Read Receipts
```java
PagedIterable<ChatMessageReadReceipt> receipts = threadClient.listReadReceipts();

for (ChatMessageReadReceipt receipt : receipts) {
    System.out.println("Message ID: " + receipt.getChatMessageId());
    System.out.println("Read at: " + receipt.getReadOn());
}
```

---

## 7. Typing Notifications

### 7.1 ✅ CORRECT: Send Typing Notification
```java
threadClient.sendTypingNotification();
```

---

## 8. Error Handling

### 8.1 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    threadClient.sendMessage(messageOptions);
} catch (HttpResponseException e) {
    switch (e.getResponse().getStatusCode()) {
        case 401:
            System.out.println("Unauthorized - check token");
            break;
        case 403:
            System.out.println("Forbidden - user not in thread");
            break;
        case 404:
            System.out.println("Thread not found");
            break;
        default:
            System.out.println("Error: " + e.getMessage());
    }
}
```

---

## 9. Best Practices Checklist

- [ ] Use `CommunicationTokenCredential` for user authentication
- [ ] Use environment variables for tokens and endpoints
- [ ] Implement token refresh for long-lived clients
- [ ] Use pagination for listing messages in large threads
- [ ] Send read receipts only when messages are actually viewed
- [ ] Handle token expiration gracefully
