# Azure Web PubSub Java SDK - Examples

Comprehensive code examples for the Azure Web PubSub SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Send Messages](#send-messages)
- [Group Management](#group-management)
- [Connection Management](#connection-management)
- [Client Access Tokens](#client-access-tokens)
- [Permissions](#permissions)
- [Async Operations](#async-operations)
- [Complete Application Example](#complete-application-example)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-messaging-webpubsub</artifactId>
    <version>1.5.0</version>
</dependency>
```

## Client Creation

### With Connection String

```java
import com.azure.messaging.webpubsub.WebPubSubServiceClient;
import com.azure.messaging.webpubsub.WebPubSubServiceClientBuilder;

WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .connectionString(System.getenv("WEB_PUBSUB_CONNECTION_STRING"))
    .hub("chat")
    .buildClient();
```

### With DefaultAzureCredential

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(System.getenv("WEB_PUBSUB_ENDPOINT"))
    .hub("chat")
    .buildClient();
```

### With Access Key

```java
import com.azure.core.credential.AzureKeyCredential;

WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .credential(new AzureKeyCredential("<access-key>"))
    .endpoint("<endpoint>")
    .hub("chat")
    .buildClient();
```

### Async Client

```java
import com.azure.messaging.webpubsub.WebPubSubServiceAsyncClient;

WebPubSubServiceAsyncClient asyncClient = new WebPubSubServiceClientBuilder()
    .connectionString(connectionString)
    .hub("chat")
    .buildAsyncClient();
```

## Send Messages

### Send to All Connections

```java
import com.azure.messaging.webpubsub.models.WebPubSubContentType;

// Send text message
client.sendToAll("Hello everyone!", WebPubSubContentType.TEXT_PLAIN);

// Send JSON
String jsonMessage = "{\"type\": \"notification\", \"message\": \"New update!\"}";
client.sendToAll(jsonMessage, WebPubSubContentType.APPLICATION_JSON);
```

### Send to All with Filter

```java
import com.azure.core.http.rest.RequestOptions;
import com.azure.core.util.BinaryData;

BinaryData message = BinaryData.fromString("Hello filtered users!");

// Filter by userId
client.sendToAllWithResponse(
    message,
    WebPubSubContentType.TEXT_PLAIN,
    message.getLength(),
    new RequestOptions().addQueryParam("filter", "userId ne 'user1'"));

// Filter by groups
client.sendToAllWithResponse(
    message,
    WebPubSubContentType.TEXT_PLAIN,
    message.getLength(),
    new RequestOptions().addQueryParam("filter", "'GroupA' in groups and not('GroupB' in groups)"));
```

### Send to Group

```java
client.sendToGroup("developers", "Hello developers!", WebPubSubContentType.TEXT_PLAIN);

String json = "{\"event\": \"update\", \"version\": \"2.0\"}";
client.sendToGroup("subscribers", json, WebPubSubContentType.APPLICATION_JSON);
```

### Send to User

```java
client.sendToUser("user123", "Personal message", WebPubSubContentType.TEXT_PLAIN);
```

### Send to Connection

```java
client.sendToConnection("connectionId123", "Direct message", WebPubSubContentType.TEXT_PLAIN);
```

## Group Management

### Add/Remove Connections

```java
// Add connection to group
client.addConnectionToGroup("premium-users", "connectionId123");

// Remove connection from group
client.removeConnectionFromGroup("premium-users", "connectionId123");
```

### Add/Remove Users

```java
// Add user to group (all their connections)
client.addUserToGroup("admin-group", "userId456");

// Remove user from group
client.removeUserFromGroup("admin-group", "userId456");

// Check if user is in group
boolean exists = client.userExistsInGroup("admin-group", "userId456");
```

## Connection Management

### Check Connection/User Status

```java
// Check if connection exists
boolean connected = client.connectionExists("connectionId123");

// Check if user exists (has any connections)
boolean userOnline = client.userExists("userId456");
```

### Close Connections

```java
// Close a connection
client.closeConnection("connectionId123");

// Close with reason
client.closeConnection("connectionId123", "Session expired");

// Close all connections for a user
client.closeUserConnections("userId456");

// Close all connections in a group
client.closeGroupConnections("inactive-group");
```

## Client Access Tokens

### Generate Basic Token

```java
import com.azure.messaging.webpubsub.models.GetClientAccessTokenOptions;
import com.azure.messaging.webpubsub.models.WebPubSubClientAccessToken;

WebPubSubClientAccessToken token = client.getClientAccessToken(
    new GetClientAccessTokenOptions());
System.out.println("WebSocket URL: " + token.getUrl());
```

### Token with User ID

```java
WebPubSubClientAccessToken token = client.getClientAccessToken(
    new GetClientAccessTokenOptions().setUserId("user123"));
```

### Token with Roles

```java
WebPubSubClientAccessToken token = client.getClientAccessToken(
    new GetClientAccessTokenOptions()
        .setUserId("user123")
        .addRole("webpubsub.joinLeaveGroup")
        .addRole("webpubsub.sendToGroup"));
```

### Token with Initial Groups

```java
WebPubSubClientAccessToken token = client.getClientAccessToken(
    new GetClientAccessTokenOptions()
        .setUserId("user123")
        .addGroup("announcements")
        .addGroup("updates"));
```

### Token with Custom Expiration

```java
import java.time.Duration;

WebPubSubClientAccessToken token = client.getClientAccessToken(
    new GetClientAccessTokenOptions()
        .setUserId("user123")
        .setExpiresAfter(Duration.ofHours(2)));
```

## Permissions

### Grant/Revoke Permissions

```java
import com.azure.messaging.webpubsub.models.WebPubSubPermission;

// Grant permission
client.grantPermission(
    WebPubSubPermission.SEND_TO_GROUP,
    "connectionId123",
    new RequestOptions().addQueryParam("targetName", "chat-room"));

// Revoke permission
client.revokePermission(
    WebPubSubPermission.SEND_TO_GROUP,
    "connectionId123",
    new RequestOptions().addQueryParam("targetName", "chat-room"));

// Check permission
boolean hasPermission = client.checkPermission(
    WebPubSubPermission.SEND_TO_GROUP,
    "connectionId123",
    new RequestOptions().addQueryParam("targetName", "chat-room"));
```

## Async Operations

```java
WebPubSubServiceAsyncClient asyncClient = new WebPubSubServiceClientBuilder()
    .connectionString(connectionString)
    .hub("chat")
    .buildAsyncClient();

asyncClient.sendToAll("Async message!", WebPubSubContentType.TEXT_PLAIN)
    .subscribe(
        unused -> System.out.println("Message sent"),
        error -> System.err.println("Error: " + error.getMessage())
    );

asyncClient.sendToGroup("developers", "Group message", WebPubSubContentType.TEXT_PLAIN)
    .doOnSuccess(v -> System.out.println("Sent to group"))
    .doOnError(e -> System.err.println("Failed: " + e))
    .subscribe();
```

## Complete Application Example

### Real-Time Chat Service

```java
import com.azure.messaging.webpubsub.*;
import com.azure.messaging.webpubsub.models.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class ChatService {
    private final WebPubSubServiceClient client;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Map<String, Set<String>> userRooms = new ConcurrentHashMap<>();
    
    public ChatService(String connectionString) {
        this.client = new WebPubSubServiceClientBuilder()
            .connectionString(connectionString)
            .hub("chat")
            .buildClient();
    }
    
    public WebPubSubClientAccessToken connectUser(String userId, List<String> initialRooms) {
        GetClientAccessTokenOptions options = new GetClientAccessTokenOptions()
            .setUserId(userId)
            .addRole("webpubsub.joinLeaveGroup")
            .addRole("webpubsub.sendToGroup")
            .setExpiresAfter(Duration.ofHours(24));
        
        // Add initial rooms
        for (String room : initialRooms) {
            options.addGroup(room);
        }
        
        userRooms.put(userId, new HashSet<>(initialRooms));
        
        return client.getClientAccessToken(options);
    }
    
    public void joinRoom(String userId, String roomId) {
        client.addUserToGroup(roomId, userId);
        userRooms.computeIfAbsent(userId, k -> new HashSet<>()).add(roomId);
        
        broadcastToRoom(roomId, new ChatEvent("user_joined", userId, roomId, null));
    }
    
    public void leaveRoom(String userId, String roomId) {
        client.removeUserFromGroup(roomId, userId);
        
        Set<String> rooms = userRooms.get(userId);
        if (rooms != null) {
            rooms.remove(roomId);
        }
        
        broadcastToRoom(roomId, new ChatEvent("user_left", userId, roomId, null));
    }
    
    public void sendMessage(String userId, String roomId, String message) {
        ChatEvent event = new ChatEvent("message", userId, roomId, message);
        broadcastToRoom(roomId, event);
    }
    
    public void sendDirectMessage(String fromUserId, String toUserId, String message) {
        ChatEvent event = new ChatEvent("direct_message", fromUserId, null, message);
        try {
            String json = objectMapper.writeValueAsString(event);
            client.sendToUser(toUserId, json, WebPubSubContentType.APPLICATION_JSON);
        } catch (Exception e) {
            throw new RuntimeException("Failed to send direct message", e);
        }
    }
    
    public void broadcastSystemMessage(String message) {
        ChatEvent event = new ChatEvent("system", "system", null, message);
        try {
            String json = objectMapper.writeValueAsString(event);
            client.sendToAll(json, WebPubSubContentType.APPLICATION_JSON);
        } catch (Exception e) {
            throw new RuntimeException("Failed to broadcast", e);
        }
    }
    
    public boolean isUserOnline(String userId) {
        return client.userExists(userId);
    }
    
    public void disconnectUser(String userId) {
        client.closeUserConnections(userId);
        userRooms.remove(userId);
    }
    
    private void broadcastToRoom(String roomId, ChatEvent event) {
        try {
            String json = objectMapper.writeValueAsString(event);
            client.sendToGroup(roomId, json, WebPubSubContentType.APPLICATION_JSON);
        } catch (Exception e) {
            throw new RuntimeException("Failed to broadcast to room", e);
        }
    }
    
    static class ChatEvent {
        public String type;
        public String userId;
        public String roomId;
        public String message;
        public long timestamp;
        
        ChatEvent(String type, String userId, String roomId, String message) {
            this.type = type;
            this.userId = userId;
            this.roomId = roomId;
            this.message = message;
            this.timestamp = System.currentTimeMillis();
        }
    }
}
```

### Usage

```java
public class Main {
    public static void main(String[] args) {
        String connectionString = System.getenv("WEB_PUBSUB_CONNECTION_STRING");
        ChatService chatService = new ChatService(connectionString);
        
        // Connect a user
        WebPubSubClientAccessToken token = chatService.connectUser(
            "user1", 
            Arrays.asList("general", "support")
        );
        System.out.println("WebSocket URL: " + token.getUrl());
        
        // Send a message
        chatService.sendMessage("user1", "general", "Hello everyone!");
        
        // Send direct message
        chatService.sendDirectMessage("user1", "user2", "Hey, private message!");
        
        // Broadcast system message
        chatService.broadcastSystemMessage("Server maintenance in 10 minutes");
    }
}
```

## Environment Variables

```bash
WEB_PUBSUB_CONNECTION_STRING=Endpoint=https://<resource>.webpubsub.azure.com;AccessKey=...
WEB_PUBSUB_ENDPOINT=https://<resource>.webpubsub.azure.com
WEB_PUBSUB_ACCESS_KEY=<your-access-key>
```

## Client Roles Reference

| Role | Permission |
|------|------------|
| `webpubsub.joinLeaveGroup` | Join/leave any group |
| `webpubsub.sendToGroup` | Send to any group |
| `webpubsub.joinLeaveGroup.<group>` | Join/leave specific group |
| `webpubsub.sendToGroup.<group>` | Send to specific group |

## Best Practices

1. **Use Groups** - Organize connections into groups for targeted messaging
2. **User IDs** - Associate connections with user IDs for user-level messaging
3. **Token Expiration** - Set appropriate token expiration for security
4. **Roles** - Grant minimal required permissions via roles
5. **Hub Isolation** - Use separate hubs for different application features
6. **Connection Management** - Clean up inactive connections
7. **Error Handling** - Handle connection failures gracefully
