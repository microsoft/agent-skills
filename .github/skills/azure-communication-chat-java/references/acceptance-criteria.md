# Azure Communication Chat Acceptance Criteria

**SDK**: `com.azure:azure-communication-chat`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/communication/azure-communication-chat
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Full qualified client imports
```java
import com.azure.communication.chat.ChatClient;
import com.azure.communication.chat.ChatClientBuilder;
import com.azure.communication.chat.ChatThreadClient;
import com.azure.communication.chat.ChatAsyncClient;
```

#### ❌ INCORRECT: Wrong package imports
```java
import com.azure.communication.calling.ChatClient;
```

### 1.2 Model Imports
#### ✅ CORRECT: Models from chat.models package
```java
import com.azure.communication.chat.models.*;
```

### 1.3 Credential Imports
#### ✅ CORRECT: CommunicationTokenCredential
```java
import com.azure.communication.common.CommunicationTokenCredential;
import com.azure.communication.common.CommunicationUserIdentifier;
```

---

## 2. Client Creation Patterns

### 2.1 With CommunicationTokenCredential
#### ✅ CORRECT: Full client setup
```java
String endpoint = "https://<resource>.communication.azure.com";
String userAccessToken = "<user-access-token>";

CommunicationTokenCredential credential = new CommunicationTokenCredential(userAccessToken);

ChatClient chatClient = new ChatClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildClient();
```

#### ❌ INCORRECT: Using DefaultAzureCredential for ChatClient
```java
// ChatClient requires user token, not service principal
ChatClient chatClient = new ChatClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.2 Async Client
#### ✅ CORRECT: Async client creation
```java
ChatAsyncClient chatAsyncClient = new ChatClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildAsyncClient();
```

---

## 3. Chat Thread Operations

### 3.1 Create Thread
#### ✅ CORRECT: With participants and topic
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
```

#### ❌ INCORRECT: Missing topic
```java
CreateChatThreadOptions options = new CreateChatThreadOptions(null);
```

### 3.2 Get Thread Client
#### ✅ CORRECT: From ChatClient
```java
ChatThreadClient threadClient = chatClient.getChatThreadClient(threadId);
```

---

## 4. Message Operations

### 4.1 Send Message
#### ✅ CORRECT: With options
```java
SendChatMessageOptions messageOptions = new SendChatMessageOptions()
    .setContent("Hello, team!")
    .setSenderDisplayName("Alice")
    .setType(ChatMessageType.TEXT);

SendChatMessageResult sendResult = threadClient.sendMessage(messageOptions);
String messageId = sendResult.getId();
```

#### ❌ INCORRECT: Using deprecated methods
```java
threadClient.sendMessage("Hello");
```

### 4.2 List Messages
#### ✅ CORRECT: With PagedIterable
```java
PagedIterable<ChatMessage> messages = threadClient.listMessages();

for (ChatMessage message : messages) {
    System.out.println("ID: " + message.getId());
    System.out.println("Type: " + message.getType());
    System.out.println("Content: " + message.getContent().getMessage());
}
```

### 4.3 Update and Delete Messages
#### ✅ CORRECT: Update with options
```java
UpdateChatMessageOptions updateOptions = new UpdateChatMessageOptions()
    .setContent("Updated message content");

threadClient.updateMessage(messageId, updateOptions);

// Delete
threadClient.deleteMessage(messageId);
```

---

## 5. Participant Management

### 5.1 Add Participants
#### ✅ CORRECT: With share history time
```java
List<ChatParticipant> newParticipants = new ArrayList<>();
newParticipants.add(new ChatParticipant()
    .setCommunicationIdentifier(new CommunicationUserIdentifier("<new-user-id>"))
    .setDisplayName("Charlie")
    .setShareHistoryTime(OffsetDateTime.now().minusDays(7)));

threadClient.addParticipants(newParticipants);
```

### 5.2 Remove Participant
#### ✅ CORRECT: Using identifier
```java
CommunicationUserIdentifier userToRemove = new CommunicationUserIdentifier("<user-id>");
threadClient.removeParticipant(userToRemove);
```

### 5.3 List Participants
#### ✅ CORRECT: With type casting
```java
PagedIterable<ChatParticipant> participants = threadClient.listParticipants();

for (ChatParticipant participant : participants) {
    CommunicationUserIdentifier user = 
        (CommunicationUserIdentifier) participant.getCommunicationIdentifier();
    System.out.println("User: " + user.getId());
    System.out.println("Display Name: " + participant.getDisplayName());
}
```

---

## 6. Read Receipts

### 6.1 Send Read Receipt
#### ✅ CORRECT: Using message ID
```java
threadClient.sendReadReceipt(messageId);
```

### 6.2 List Read Receipts
#### ✅ CORRECT: Iterate receipts
```java
PagedIterable<ChatMessageReadReceipt> receipts = threadClient.listReadReceipts();

for (ChatMessageReadReceipt receipt : receipts) {
    System.out.println("Message ID: " + receipt.getChatMessageId());
    System.out.println("Read by: " + receipt.getSenderCommunicationIdentifier());
    System.out.println("Read at: " + receipt.getReadOn());
}
```

---

## 7. Typing Notifications

### 7.1 Send Typing Notification
#### ✅ CORRECT: With options
```java
TypingNotificationOptions typingOptions = new TypingNotificationOptions()
    .setSenderDisplayName("Alice");

threadClient.sendTypingNotificationWithResponse(typingOptions, Context.NONE);
```

#### ✅ CORRECT: Simple notification
```java
threadClient.sendTypingNotification();
```

---

## 8. Pagination

### 8.1 Paginate Messages
#### ✅ CORRECT: With options and page iteration
```java
int maxPageSize = 10;
ListChatMessagesOptions listOptions = new ListChatMessagesOptions()
    .setMaxPageSize(maxPageSize);

PagedIterable<ChatMessage> pagedMessages = threadClient.listMessages(listOptions);

pagedMessages.iterableByPage().forEach(page -> {
    System.out.println("Page status code: " + page.getStatusCode());
    page.getElements().forEach(msg -> 
        System.out.println("Message: " + msg.getContent().getMessage()));
});
```

---

## 9. Error Handling

### 9.1 HTTP Response Exception
#### ✅ CORRECT: Status code checking
```java
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

#### ❌ INCORRECT: Catching generic exception
```java
try {
    threadClient.sendMessage(messageOptions);
} catch (Exception e) {
    // Too broad
}
```

---

## 10. Message Types

### 10.1 Message Type Enum
#### ✅ CORRECT: Using ChatMessageType enum
```java
// User messages
ChatMessageType.TEXT
ChatMessageType.HTML

// System messages
ChatMessageType.TOPIC_UPDATED
ChatMessageType.PARTICIPANT_ADDED
ChatMessageType.PARTICIPANT_REMOVED
```

---

## 11. Required Dependencies

### 11.1 Maven Configuration
#### ✅ CORRECT: Current version
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-chat</artifactId>
    <version>1.6.0</version>
</dependency>
```

---

## 12. Best Practices

### 12.1 Token Management
- User tokens expire; implement refresh logic with `CommunicationTokenRefreshOptions`
- Never log or expose full tokens

### 12.2 Message Handling
- Filter system messages from user messages when displaying
- Use `maxPageSize` for large threads

### 12.3 Participant Management
- Set `shareHistoryTime` when adding participants to control message visibility
- Send read receipts only when messages are actually viewed
