# Azure Web PubSub SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-messaging-webpubsub`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/webpubsub/azure-messaging-webpubsub
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Service Clients
```java
import com.azure.messaging.webpubsub.WebPubSubServiceClient;
import com.azure.messaging.webpubsub.WebPubSubServiceClientBuilder;
import com.azure.messaging.webpubsub.WebPubSubServiceAsyncClient;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Web PubSub Models
```java
import com.azure.messaging.webpubsub.models.WebPubSubContentType;
import com.azure.messaging.webpubsub.models.GetClientAccessTokenOptions;
import com.azure.messaging.webpubsub.models.WebPubSubClientAccessToken;
import com.azure.messaging.webpubsub.models.WebPubSubPermission;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with Connection String
```java
String connectionString = System.getenv("WEB_PUBSUB_CONNECTION_STRING");

WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .connectionString(connectionString)
    .hub("chat")
    .buildClient();
```

### 2.2 ✅ CORRECT: Builder with DefaultAzureCredential
```java
String endpoint = System.getenv("WEB_PUBSUB_ENDPOINT");

WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .hub("chat")
    .buildClient();
```

---

## 3. Send Messages

### 3.1 ✅ CORRECT: Send to All
```java
client.sendToAll("Hello everyone!", WebPubSubContentType.TEXT_PLAIN);
```

### 3.2 ✅ CORRECT: Send JSON to All
```java
String jsonMessage = "{\"type\": \"notification\", \"message\": \"Update\"}";
client.sendToAll(jsonMessage, WebPubSubContentType.APPLICATION_JSON);
```

### 3.3 ✅ CORRECT: Send to Group
```java
client.sendToGroup("developers", "Hello devs!", WebPubSubContentType.TEXT_PLAIN);
```

### 3.4 ✅ CORRECT: Send to User
```java
client.sendToUser("userId123", "Private message", WebPubSubContentType.TEXT_PLAIN);
```

---

## 4. Group Management

### 4.1 ✅ CORRECT: Add/Remove Connection to Group
```java
client.addConnectionToGroup("premium-users", "connectionId123");
client.removeConnectionFromGroup("premium-users", "connectionId123");
```

### 4.2 ✅ CORRECT: Add/Remove User to Group
```java
client.addUserToGroup("admin-group", "userId456");
client.removeUserFromGroup("admin-group", "userId456");
```

---

## 5. Client Access Token

### 5.1 ✅ CORRECT: Generate Token
```java
WebPubSubClientAccessToken token = client.getClientAccessToken(
    new GetClientAccessTokenOptions()
        .setUserId("user123")
        .addRole("webpubsub.sendToGroup")
        .addGroup("announcements"));

System.out.println("URL: " + token.getUrl());
```

---

## 6. Connection Management

### 6.1 ✅ CORRECT: Check and Close Connections
```java
boolean connected = client.connectionExists("connectionId123");
client.closeConnection("connectionId123");
client.closeUserConnections("userId456");
```

---

## 7. Error Handling

### 7.1 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.sendToConnection("invalid-id", "test", WebPubSubContentType.TEXT_PLAIN);
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
}
```

---

## 8. Best Practices Checklist

- [ ] Use environment variables for connection configuration
- [ ] Organize connections into groups for targeted messaging
- [ ] Associate connections with user IDs
- [ ] Set appropriate token expiration for security
- [ ] Grant minimal required permissions via roles
