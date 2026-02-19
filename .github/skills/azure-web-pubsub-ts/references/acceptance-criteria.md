# Azure Web PubSub SDK Acceptance Criteria (TypeScript)

**SDK**: `@azure/web-pubsub`, `@azure/web-pubsub-client`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/web-pubsub
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Server-Side Imports

#### ✅ CORRECT: WebPubSubServiceClient Import
```typescript
import { WebPubSubServiceClient, AzureKeyCredential } from "@azure/web-pubsub";
import { DefaultAzureCredential } from "@azure/identity";
```

### 1.2 Client-Side Imports

#### ✅ CORRECT: WebPubSubClient Import
```typescript
import { WebPubSubClient } from "@azure/web-pubsub-client";
```

### 1.3 Express Middleware Imports

#### ✅ CORRECT: Express Handler Import
```typescript
import { WebPubSubEventHandler } from "@azure/web-pubsub-express";
```

### 1.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong package name
```typescript
// WRONG - package is @azure/web-pubsub
import { WebPubSubServiceClient } from "@azure/webpubsub";
import { WebPubSubClient } from "@azure/web-pubsub";  // WRONG - client is separate package
```

---

## 2. Server-Side Authentication Patterns

### 2.1 ✅ CORRECT: Connection String
```typescript
import { WebPubSubServiceClient } from "@azure/web-pubsub";

const client = new WebPubSubServiceClient(
  process.env.WEBPUBSUB_CONNECTION_STRING!,
  "chat"  // hub name
);
```

### 2.2 ✅ CORRECT: DefaultAzureCredential (Recommended)
```typescript
import { WebPubSubServiceClient } from "@azure/web-pubsub";
import { DefaultAzureCredential } from "@azure/identity";

const client = new WebPubSubServiceClient(
  process.env.WEBPUBSUB_ENDPOINT!,
  new DefaultAzureCredential(),
  "chat"
);
```

### 2.3 ✅ CORRECT: AzureKeyCredential
```typescript
import { WebPubSubServiceClient, AzureKeyCredential } from "@azure/web-pubsub";

const client = new WebPubSubServiceClient(
  process.env.WEBPUBSUB_ENDPOINT!,
  new AzureKeyCredential(process.env.WEBPUBSUB_KEY!),
  "chat"
);
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```typescript
// WRONG - hardcoded access key
const client = new WebPubSubServiceClient(
  "Endpoint=https://myresource.webpubsub.azure.com;AccessKey=secret123;Version=1.0;",
  "chat"
);
```

---

## 3. Client Access Token Patterns

### 3.1 ✅ CORRECT: Basic Token Generation
```typescript
const token = await client.getClientAccessToken();
console.log(token.url);  // wss://...?access_token=...
```

### 3.2 ✅ CORRECT: Token with User ID
```typescript
const userToken = await client.getClientAccessToken({
  userId: "user123",
});
```

### 3.3 ✅ CORRECT: Token with Permissions
```typescript
const permToken = await client.getClientAccessToken({
  userId: "user123",
  roles: [
    "webpubsub.joinLeaveGroup",
    "webpubsub.sendToGroup",
    "webpubsub.sendToGroup.chat-room",
  ],
  groups: ["chat-room"],
  expirationTimeInMinutes: 60,
});
```

---

## 4. Message Sending Patterns

### 4.1 ✅ CORRECT: Broadcast to All
```typescript
await client.sendToAll({ message: "Hello everyone!" });
await client.sendToAll("Plain text", { contentType: "text/plain" });
```

### 4.2 ✅ CORRECT: Send to User
```typescript
await client.sendToUser("user123", { message: "Hello!" });
```

### 4.3 ✅ CORRECT: Send to Connection
```typescript
await client.sendToConnection("connectionId", { data: "Direct message" });
```

### 4.4 ✅ CORRECT: Send with Filter
```typescript
await client.sendToAll({ message: "Filtered" }, {
  filter: "userId ne 'admin'",
});
```

---

## 5. Group Management Patterns

### 5.1 ✅ CORRECT: Group Operations
```typescript
const group = client.group("chat-room");

// Add user/connection to group
await group.addUser("user123");
await group.addConnection("connectionId");

// Remove from group
await group.removeUser("user123");

// Send to group
await group.sendToAll({ message: "Group message" });

// Close all connections in group
await group.closeAllConnections({ reason: "Maintenance" });
```

---

## 6. Connection Management Patterns

### 6.1 ✅ CORRECT: Check Existence
```typescript
const userExists = await client.userExists("user123");
const connExists = await client.connectionExists("connectionId");
```

### 6.2 ✅ CORRECT: Close Connections
```typescript
await client.closeConnection("connectionId", { reason: "Kicked" });
await client.closeUserConnections("user123");
await client.closeAllConnections();
```

### 6.3 ✅ CORRECT: Manage Permissions
```typescript
await client.grantPermission("connectionId", "sendToGroup", { targetName: "chat" });
await client.revokePermission("connectionId", "sendToGroup", { targetName: "chat" });
```

---

## 7. Client-Side Patterns

### 7.1 ✅ CORRECT: Connect with URL
```typescript
import { WebPubSubClient } from "@azure/web-pubsub-client";

const client = new WebPubSubClient("<client-access-url>");
```

### 7.2 ✅ CORRECT: Connect with Negotiate Endpoint
```typescript
import { WebPubSubClient } from "@azure/web-pubsub-client";

const client = new WebPubSubClient({
  getClientAccessUrl: async () => {
    const response = await fetch("/negotiate");
    const { url } = await response.json();
    return url;
  },
});
```

### 7.3 ✅ CORRECT: Register Handlers Before Start
```typescript
client.on("connected", (e) => {
  console.log(`Connected: ${e.connectionId}`);
});

client.on("group-message", (e) => {
  console.log(`${e.message.group}: ${e.message.data}`);
});

await client.start();
```

### 7.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Starting before registering handlers
```typescript
// WRONG - handlers registered after start
await client.start();
client.on("connected", (e) => {
  console.log(`Connected: ${e.connectionId}`);
});
```

---

## 8. Client-Side Message Patterns

### 8.1 ✅ CORRECT: Join Group and Send
```typescript
await client.joinGroup("chat-room");

await client.sendToGroup("chat-room", "Hello!", "text");
await client.sendToGroup("chat-room", { type: "message", content: "Hi" }, "json");
```

### 8.2 ✅ CORRECT: Send with Options
```typescript
await client.sendToGroup("chat-room", "Hello", "text", {
  noEcho: true,
  fireAndForget: true,
});
```

### 8.3 ✅ CORRECT: Send Event to Server
```typescript
await client.sendEvent("userAction", { action: "typing" }, "json");
```

---

## 9. Client-Side Event Handlers

### 9.1 ✅ CORRECT: All Event Handlers
```typescript
client.on("connected", (e) => {
  console.log(`Connected: ${e.connectionId}, User: ${e.userId}`);
});

client.on("disconnected", (e) => {
  console.log(`Disconnected: ${e.message}`);
});

client.on("stopped", () => {
  console.log("Client stopped");
});

client.on("group-message", (e) => {
  console.log(`[${e.message.group}] ${e.message.fromUserId}: ${e.message.data}`);
});

client.on("server-message", (e) => {
  console.log(`Server: ${e.message.data}`);
});

client.on("rejoin-group-failed", (e) => {
  console.log(`Failed to rejoin ${e.group}: ${e.error}`);
});
```

---

## 10. Express Event Handler Patterns

### 10.1 ✅ CORRECT: Full Event Handler
```typescript
import express from "express";
import { WebPubSubEventHandler } from "@azure/web-pubsub-express";

const app = express();

const handler = new WebPubSubEventHandler("chat", {
  path: "/api/webpubsub/hubs/chat/",
  
  handleConnect: (req, res) => {
    if (!req.claims?.sub) {
      res.fail(401, "Authentication required");
      return;
    }
    res.success({
      userId: req.claims.sub[0],
      groups: ["general"],
      roles: ["webpubsub.sendToGroup"],
    });
  },
  
  handleUserEvent: (req, res) => {
    console.log(`Event from ${req.context.userId}:`, req.data);
    res.success(`Received: ${req.data}`, "text");
  },
  
  onConnected: (req) => {
    console.log(`Client connected: ${req.context.connectionId}`);
  },
  
  onDisconnected: (req) => {
    console.log(`Client disconnected: ${req.context.connectionId}`);
  },
});

app.use(handler.getMiddleware());
```

---

## 11. Negotiate Endpoint Patterns

### 11.1 ✅ CORRECT: Negotiate Endpoint
```typescript
app.get("/negotiate", async (req, res) => {
  const token = await serviceClient.getClientAccessToken({
    userId: req.user?.id,
  });
  res.json({ url: token.url });
});
```

---

## 12. Environment Variables

### 12.1 ✅ CORRECT: Required Variables
```typescript
const connectionString = process.env.WEBPUBSUB_CONNECTION_STRING!;
const endpoint = process.env.WEBPUBSUB_ENDPOINT!;
```

### 12.2 ❌ INCORRECT: Hardcoded values
```typescript
// WRONG - hardcoded endpoint
const client = new WebPubSubServiceClient(
  "https://myresource.webpubsub.azure.com",
  new DefaultAzureCredential(),
  "chat"
);
```
