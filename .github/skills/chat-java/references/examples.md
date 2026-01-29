# Azure Communication Chat SDK for Java - Examples

Comprehensive code examples for the Azure Communication Chat SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Creating Chat Threads](#creating-chat-threads)
- [Sending Messages](#sending-messages)
- [Listing Messages](#listing-messages)
- [Adding and Removing Participants](#adding-and-removing-participants)
- [Updating Thread Topic](#updating-thread-topic)
- [Typing Notifications](#typing-notifications)
- [Read Receipts](#read-receipts)
- [Async Client Patterns](#async-client-patterns)
- [Error Handling](#error-handling)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-chat</artifactId>
    <version>1.6.4</version>
</dependency>

<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-common</artifactId>
    <version>1.3.8</version>
</dependency>
```

Using Azure SDK BOM:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-sdk-bom</artifactId>
            <version>{bom_version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-communication-chat</artifactId>
    </dependency>
</dependencies>
```

## Client Creation

### Synchronous ChatClient

```java
import com.azure.communication.chat.ChatClient;
import com.azure.communication.chat.ChatClientBuilder;
import com.azure.communication.common.CommunicationTokenCredential;

String endpoint = "https://<RESOURCE_NAME>.communication.azure.com";
String userAccessToken = "<USER_ACCESS_TOKEN>";

CommunicationTokenCredential credential = new CommunicationTokenCredential(userAccessToken);

ChatClient chatClient = new ChatClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildClient();
```

### Asynchronous ChatAsyncClient

```java
import com.azure.communication.chat.ChatAsyncClient;
import com.azure.communication.chat.ChatClientBuilder;

ChatAsyncClient chatAsyncClient = new ChatClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildAsyncClient();
```

### Get ChatThreadClient

```java
import com.azure.communication.chat.ChatThreadClient;

String chatThreadId = "19:abc123...@thread.v2";
ChatThreadClient chatThreadClient = chatClient.getChatThreadClient(chatThreadId);
```

## Creating Chat Threads

```java
import com.azure.communication.chat.models.ChatParticipant;
import com.azure.communication.chat.models.CreateChatThreadOptions;
import com.azure.communication.chat.models.CreateChatThreadResult;
import com.azure.communication.common.CommunicationUserIdentifier;

String userId1 = "<USER_Id1>";
ChatParticipant firstParticipant = new ChatParticipant()
    .setCommunicationIdentifier(new CommunicationUserIdentifier(userId1))
    .setDisplayName("Display Name 1");

String userId2 = "<USER_Id2>";
ChatParticipant secondParticipant = new ChatParticipant()
    .setCommunicationIdentifier(new CommunicationUserIdentifier(userId2))
    .setDisplayName("Display Name 2");

CreateChatThreadOptions createOptions = new CreateChatThreadOptions("Topic")
    .addParticipant(firstParticipant)
    .addParticipant(secondParticipant);

CreateChatThreadResult result = chatClient.createChatThread(createOptions);
String chatThreadId = result.getChatThread().getId();

// Get thread client
ChatThreadClient chatThreadClient = chatClient.getChatThreadClient(chatThreadId);
```

### Using setParticipants

```java
import java.util.ArrayList;
import java.util.List;

List<ChatParticipant> participants = new ArrayList<>();
participants.add(firstParticipant);
participants.add(secondParticipant);

CreateChatThreadOptions createOptions = new CreateChatThreadOptions("Topic")
    .setParticipants(participants);

CreateChatThreadResult result = chatClient.createChatThread(createOptions);
```

## Sending Messages

### Send Text Message

```java
import com.azure.communication.chat.models.ChatMessageType;
import com.azure.communication.chat.models.SendChatMessageOptions;
import com.azure.communication.chat.models.SendChatMessageResult;

SendChatMessageOptions sendOptions = new SendChatMessageOptions()
    .setContent("Message content")
    .setType(ChatMessageType.TEXT)
    .setSenderDisplayName("Sender Display Name");

SendChatMessageResult sendResult = chatThreadClient.sendMessage(sendOptions);
String chatMessageId = sendResult.getId();
```

### Send Message with Metadata

```java
import java.util.HashMap;
import java.util.Map;

Map<String, String> metadata = new HashMap<>();
metadata.put("hasAttachment", "true");
metadata.put("attachmentUrl", "https://contoso.com/files/attachment.docx");

SendChatMessageOptions sendOptions = new SendChatMessageOptions()
    .setType(ChatMessageType.TEXT)
    .setContent("Please take a look at the attachment")
    .setSenderDisplayName("Sender")
    .setMetadata(metadata);

SendChatMessageResult sendResult = chatThreadClient.sendMessage(sendOptions);
```

## Listing Messages

### List All Messages

```java
import com.azure.communication.chat.models.ChatMessage;

chatThreadClient.listMessages().forEach(message -> {
    System.out.printf("Message id: %s%n", message.getId());
    System.out.printf("Content: %s%n", message.getContent().getMessage());
});
```

### List with Pagination

```java
import com.azure.core.http.rest.PagedIterable;

PagedIterable<ChatMessage> messages = chatThreadClient.listMessages();
messages.iterableByPage().forEach(page -> {
    System.out.printf("Status: %d%n", page.getStatusCode());
    page.getElements().forEach(message ->
        System.out.printf("Message: %s%n", message.getId()));
});
```

### Get Specific Message

```java
ChatMessage message = chatThreadClient.getMessage(chatMessageId);
System.out.printf("Content: %s%n", message.getContent().getMessage());
```

### Update Message

```java
import com.azure.communication.chat.models.UpdateChatMessageOptions;

UpdateChatMessageOptions updateOptions = new UpdateChatMessageOptions()
    .setContent("Updated message content");

chatThreadClient.updateMessage(chatMessageId, updateOptions);
```

### Delete Message

```java
chatThreadClient.deleteMessage(chatMessageId);
```

### Check Message Status

```java
chatThreadClient.listMessages().forEach(message -> {
    // Check if deleted
    if (message.getDeletedOn() != null) {
        System.out.println("Deleted at: " + message.getDeletedOn());
    }
    
    // Check if edited
    if (message.getEditedOn() != null) {
        System.out.println("Edited at: " + message.getEditedOn());
    }
    
    // Message type
    System.out.println("Type: " + message.getType());
});
```

## Adding and Removing Participants

### Add Participants

```java
import java.util.ArrayList;
import java.util.List;

List<ChatParticipant> participants = new ArrayList<>();

ChatParticipant newParticipant = new ChatParticipant()
    .setCommunicationIdentifier(new CommunicationUserIdentifier("<USER_Id3>"))
    .setDisplayName("Display Name 3");

participants.add(newParticipant);

chatThreadClient.addParticipants(participants);
```

### Add Participant with History Sharing

```java
import java.time.OffsetDateTime;

ChatParticipant newParticipant = new ChatParticipant()
    .setCommunicationIdentifier(new CommunicationUserIdentifier("<USER_ID>"))
    .setDisplayName("New Participant")
    .setShareHistoryTime(OffsetDateTime.MIN);  // Share from beginning

List<ChatParticipant> participants = new ArrayList<>();
participants.add(newParticipant);
chatThreadClient.addParticipants(participants);
```

### Remove Participant

```java
CommunicationUserIdentifier user = new CommunicationUserIdentifier("<USER_ID>");
chatThreadClient.removeParticipant(user);
```

### List Participants

```java
import com.azure.communication.chat.models.ChatParticipant;

chatThreadClient.listParticipants().forEach(participant -> {
    System.out.println("Participant: " + participant.getDisplayName());
});
```

## Updating Thread Topic

```java
chatThreadClient.updateTopic("New Topic");
```

## Typing Notifications

### Send Typing Notification

```java
chatThreadClient.sendTypingNotification();
```

### Send with Options

```java
import com.azure.communication.chat.models.TypingNotificationOptions;

TypingNotificationOptions options = new TypingNotificationOptions()
    .setSenderDisplayName("Sender Name");

chatThreadClient.sendTypingNotificationWithResponse(options, null);
```

## Read Receipts

### Send Read Receipt

```java
chatThreadClient.sendReadReceipt(chatMessageId);
```

### List Read Receipts

```java
import com.azure.communication.chat.models.ChatMessageReadReceipt;

chatThreadClient.listReadReceipts().forEach(receipt -> {
    System.out.printf("Message ID: %s, Read by: %s at %s%n",
        receipt.getChatMessageId(),
        receipt.getSenderCommunicationIdentifier().getRawId(),
        receipt.getReadOn());
});
```

## Async Client Patterns

### Create Thread Async

```java
chatAsyncClient.createChatThread(createOptions)
    .subscribe(
        result -> System.out.println("Thread ID: " + result.getChatThread().getId()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### Send Message Async

```java
ChatThreadAsyncClient asyncThreadClient = chatAsyncClient.getChatThreadClient(chatThreadId);

asyncThreadClient.sendMessage(sendOptions)
    .subscribe(
        result -> System.out.println("Message ID: " + result.getId()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### List Messages Async

```java
asyncThreadClient.listMessages()
    .subscribe(
        message -> System.out.println("Message: " + message.getId()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### Chain Operations Async

```java
chatAsyncClient.createChatThread(createOptions)
    .flatMap(result -> {
        String threadId = result.getChatThread().getId();
        return chatAsyncClient.getChatThreadClient(threadId).sendMessage(sendOptions);
    })
    .subscribe(
        sendResult -> System.out.println("Message sent: " + sendResult.getId()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

## Error Handling

### Sync Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    chatThreadClient.sendMessage(sendOptions);
} catch (HttpResponseException e) {
    System.err.println("HTTP Status: " + e.getResponse().getStatusCode());
    System.err.println("Error: " + e.getMessage());
} catch (Exception e) {
    System.err.println("Unexpected error: " + e.getMessage());
}
```

### Async Error Handling

```java
asyncThreadClient.sendMessage(sendOptions)
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

### Common Error Scenarios

| Status Code | Cause |
|-------------|-------|
| 401 | Invalid or expired token |
| 403 | User not in thread |
| 404 | Thread or message not found |
| 429 | Rate limited |
