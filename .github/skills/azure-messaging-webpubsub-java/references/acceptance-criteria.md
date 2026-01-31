# Azure Web PubSub SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-messaging-webpubsub`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/webpubsub/azure-messaging-webpubsub
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Service Client Imports
```java
import com.azure.messaging.webpubsub.WebPubSubServiceClient;
import com.azure.messaging.webpubsub.WebPubSubServiceClientBuilder;
import com.azure.messaging.webpubsub.WebPubSubServiceAsyncClient;
```
#### ❌ INCORRECT: Wrong Package or Class Names
```java
import com.azure.webpubsub.WebPubSubClient;  // Wrong package
import com.azure.messaging.webpubsub.WebPubSubClient;  // Wrong class name
```

### 1.2 Model Imports
#### ✅ CORRECT: Content Type and Token Imports
```java
import com.azure.messaging.webpubsub.models.WebPubSubContentType;
import com.azure.messaging.webpubsub.models.GetClientAccessTokenOptions;
import com.azure.messaging.webpubsub.models.WebPubSubClientAccessToken;
import com.azure.messaging.webpubsub.models.WebPubSubPermission;
```
#### ❌ INCORRECT: Non-existent Model Classes
```java
import com.azure.messaging.webpubsub.models.MessageType;  // Does not exist
import com.azure.messaging.webpubsub.models.AccessToken;  // Wrong name
```

### 1.3 Credential Imports
#### ✅ CORRECT: Azure Identity and Key Credential
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureKeyCredential;
```
#### ❌ INCORRECT: Wrong Credential Classes
```java
import com.azure.identity.DefaultAzureCredential;  // Must use Builder
import com.azure.core.credential.KeyCredential;  // Wrong class
```

---

## 2. Client Creation Patterns

### 2.1 Connection String Authentication
#### ✅ CORRECT: Using Connection String with Hub
```java
WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .connectionString("<connection-string>")
    .hub("chat")
    .buildClient();
```
#### ❌ INCORRECT: Missing Hub or Wrong Method
```java
WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();  // Missing hub()

WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .connectionString("<connection-string>")
    .hubName("chat")  // Wrong method name
    .buildClient();
```

### 2.2 Access Key Authentication
#### ✅ CORRECT: Using AzureKeyCredential with Endpoint
```java
WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .credential(new AzureKeyCredential("<access-key>"))
    .endpoint("<endpoint>")
    .hub("chat")
    .buildClient();
```
#### ❌ INCORRECT: Missing Endpoint or Wrong Order
```java
WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .credential(new AzureKeyCredential("<access-key>"))
    .hub("chat")
    .buildClient();  // Missing endpoint
```

### 2.3 DefaultAzureCredential Authentication
#### ✅ CORRECT: Using DefaultAzureCredentialBuilder
```java
WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint("<endpoint>")
    .hub("chat")
    .buildClient();
```
#### ❌ INCORRECT: Wrong Credential Construction
```java
WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .credential(new DefaultAzureCredential())  // Must use builder
    .endpoint("<endpoint>")
    .hub("chat")
    .buildClient();
```

### 2.4 Async Client Creation
#### ✅ CORRECT: Building Async Client
```java
WebPubSubServiceAsyncClient asyncClient = new WebPubSubServiceClientBuilder()
    .connectionString("<connection-string>")
    .hub("chat")
    .buildAsyncClient();
```
#### ❌ INCORRECT: Wrong Build Method
```java
WebPubSubServiceAsyncClient asyncClient = new WebPubSubServiceClientBuilder()
    .connectionString("<connection-string>")
    .hub("chat")
    .buildClient();  // Returns sync client, not async
```

---

## 3. Core Operations

### 3.1 Send to All Connections
#### ✅ CORRECT: Using WebPubSubContentType
```java
client.sendToAll("Hello everyone!", WebPubSubContentType.TEXT_PLAIN);

String jsonMessage = "{\"type\": \"notification\"}";
client.sendToAll(jsonMessage, WebPubSubContentType.APPLICATION_JSON);
```
#### ❌ INCORRECT: Wrong Content Type or Missing Parameter
```java
client.sendToAll("Hello everyone!");  // Missing content type
client.sendToAll("Hello", "text/plain");  // String instead of enum
```

### 3.2 Send to Group
#### ✅ CORRECT: Group Messaging
```java
client.sendToGroup("developers", "Hello devs!", WebPubSubContentType.TEXT_PLAIN);
```
#### ❌ INCORRECT: Wrong Parameter Order
```java
client.sendToGroup("Hello devs!", "developers", WebPubSubContentType.TEXT_PLAIN);
```

### 3.3 Send to User
#### ✅ CORRECT: User Messaging
```java
client.sendToUser("userId123", "Private message", WebPubSubContentType.TEXT_PLAIN);
```

### 3.4 Send to Connection
#### ✅ CORRECT: Connection Messaging
```java
client.sendToConnection("connectionId123", "Direct message", WebPubSubContentType.TEXT_PLAIN);
```

---

## 4. Group Management

### 4.1 Add/Remove Connection to Group
#### ✅ CORRECT: Connection Group Operations
```java
client.addConnectionToGroup("premium-users", "connectionId123");
client.removeConnectionFromGroup("premium-users", "connectionId123");
```
#### ❌ INCORRECT: Wrong Parameter Order
```java
client.addConnectionToGroup("connectionId123", "premium-users");  // Reversed
```

### 4.2 Add/Remove User to Group
#### ✅ CORRECT: User Group Operations
```java
client.addUserToGroup("admin-group", "userId456");
client.removeUserFromGroup("admin-group", "userId456");
boolean exists = client.userExistsInGroup("admin-group", "userId456");
```

---

## 5. Connection Management

### 5.1 Connection Operations
#### ✅ CORRECT: Connection Checks and Closure
```java
boolean connected = client.connectionExists("connectionId123");
client.closeConnection("connectionId123");
client.closeConnection("connectionId123", "Session expired");  // With reason
```

### 5.2 User Connection Operations
#### ✅ CORRECT: User Existence and Closure
```java
boolean userOnline = client.userExists("userId456");
client.closeUserConnections("userId456");
client.closeGroupConnections("inactive-group");
```

---

## 6. Client Access Token Generation

### 6.1 Basic Token Generation
#### ✅ CORRECT: Using GetClientAccessTokenOptions
```java
WebPubSubClientAccessToken token = client.getClientAccessToken(
    new GetClientAccessTokenOptions());
String url = token.getUrl();
```
#### ❌ INCORRECT: Wrong Method or Missing Options
```java
String token = client.generateToken();  // Method doesn't exist
WebPubSubClientAccessToken token = client.getClientAccessToken();  // Missing options
```

### 6.2 Token with User and Roles
#### ✅ CORRECT: Configuring Token Options
```java
WebPubSubClientAccessToken token = client.getClientAccessToken(
    new GetClientAccessTokenOptions()
        .setUserId("user123")
        .addRole("webpubsub.joinLeaveGroup")
        .addRole("webpubsub.sendToGroup"));
```

### 6.3 Token with Groups and Expiration
#### ✅ CORRECT: Groups and Duration
```java
WebPubSubClientAccessToken token = client.getClientAccessToken(
    new GetClientAccessTokenOptions()
        .setUserId("user123")
        .addGroup("announcements")
        .setExpiresAfter(Duration.ofHours(2)));
```
#### ❌ INCORRECT: Wrong Duration Type
```java
new GetClientAccessTokenOptions()
    .setExpiresAfter(7200);  // Should be Duration, not int
```

---

## 7. Permission Management

### 7.1 Grant/Revoke Permissions
#### ✅ CORRECT: Using WebPubSubPermission Enum
```java
client.grantPermission(
    WebPubSubPermission.SEND_TO_GROUP,
    "connectionId123",
    new RequestOptions().addQueryParam("targetName", "chat-room"));

client.revokePermission(
    WebPubSubPermission.SEND_TO_GROUP,
    "connectionId123",
    new RequestOptions().addQueryParam("targetName", "chat-room"));
```
#### ❌ INCORRECT: String Instead of Enum
```java
client.grantPermission("sendToGroup", "connectionId123", options);  // String not enum
```

### 7.2 Check Permission
#### ✅ CORRECT: Permission Check
```java
boolean hasPermission = client.checkPermission(
    WebPubSubPermission.SEND_TO_GROUP,
    "connectionId123",
    new RequestOptions().addQueryParam("targetName", "chat-room"));
```

---

## 8. Async Operations

### 8.1 Async Send Operations
#### ✅ CORRECT: Reactive Patterns
```java
asyncClient.sendToAll("Async message!", WebPubSubContentType.TEXT_PLAIN)
    .subscribe(
        unused -> System.out.println("Message sent"),
        error -> System.err.println("Error: " + error.getMessage())
    );

asyncClient.sendToGroup("developers", "Group message", WebPubSubContentType.TEXT_PLAIN)
    .doOnSuccess(v -> System.out.println("Sent"))
    .doOnError(e -> System.err.println("Failed"))
    .subscribe();
```
#### ❌ INCORRECT: Blocking on Async Client
```java
asyncClient.sendToAll("message", WebPubSubContentType.TEXT_PLAIN).block();  // Avoid blocking
```

---

## 9. Error Handling

### 9.1 HTTP Exception Handling
#### ✅ CORRECT: Using HttpResponseException
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.sendToConnection("invalid-id", "test", WebPubSubContentType.TEXT_PLAIN);
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```
#### ❌ INCORRECT: Generic Exception Only
```java
try {
    client.sendToConnection("invalid-id", "test", WebPubSubContentType.TEXT_PLAIN);
} catch (Exception e) {
    // Missing specific error handling
}
```

---

## 10. Filter-Based Messaging

### 10.1 Send with OData Filter
#### ✅ CORRECT: Using RequestOptions with Filter
```java
BinaryData message = BinaryData.fromString("Filtered message");

client.sendToAllWithResponse(
    message,
    WebPubSubContentType.TEXT_PLAIN,
    message.getLength(),
    new RequestOptions().addQueryParam("filter", "userId ne 'user1'"));

client.sendToAllWithResponse(
    message,
    WebPubSubContentType.TEXT_PLAIN,
    message.getLength(),
    new RequestOptions().addQueryParam("filter", "'GroupA' in groups"));
```
#### ❌ INCORRECT: Filter as Direct Parameter
```java
client.sendToAll("message", WebPubSubContentType.TEXT_PLAIN, "userId ne 'user1'");  // Wrong API
```
