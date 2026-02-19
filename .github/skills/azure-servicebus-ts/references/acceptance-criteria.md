# Azure Service Bus SDK for TypeScript Acceptance Criteria

**SDK**: `@azure/service-bus`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/servicebus/service-bus
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: ESM Imports

```typescript
import { 
  ServiceBusClient,
  ServiceBusSender,
  ServiceBusReceiver,
  ServiceBusSessionReceiver,
} from "@azure/service-bus";
```

### 1.2 ✅ CORRECT: Type Imports

```typescript
import type { 
  ServiceBusMessage,
  ServiceBusReceivedMessage,
  ProcessMessageCallback,
  ProcessErrorCallback,
} from "@azure/service-bus";
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: CommonJS require

```typescript
// WRONG - Use ESM imports
const { ServiceBusClient } = require("@azure/service-bus");
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Recommended)

```typescript
import { ServiceBusClient } from "@azure/service-bus";
import { DefaultAzureCredential } from "@azure/identity";

const fullyQualifiedNamespace = process.env.SERVICEBUS_NAMESPACE!; // <namespace>.servicebus.windows.net
const client = new ServiceBusClient(fullyQualifiedNamespace, new DefaultAzureCredential());
```

### 2.2 ✅ CORRECT: Connection String

```typescript
import { ServiceBusClient } from "@azure/service-bus";

const client = new ServiceBusClient(process.env.SERVICEBUS_CONNECTION_STRING!);
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded connection string

```typescript
// WRONG - Never hardcode connection strings
const client = new ServiceBusClient(
  "Endpoint=sb://myns.servicebus.windows.net/;SharedAccessKeyName=key;SharedAccessKey=secret"
);
```

---

## 3. Sending Messages

### 3.1 ✅ CORRECT: Send Single Message

```typescript
const sender = client.createSender("my-queue");

await sender.sendMessages({
  body: { orderId: "12345", amount: 99.99 },
  contentType: "application/json",
});

await sender.close();
```

### 3.2 ✅ CORRECT: Send Multiple Messages as Batch

```typescript
const sender = client.createSender("my-queue");

const batch = await sender.createMessageBatch();
batch.tryAddMessage({ body: "Message 1" });
batch.tryAddMessage({ body: "Message 2" });
batch.tryAddMessage({ body: "Message 3" });

await sender.sendMessages(batch);
await sender.close();
```

### 3.3 ✅ CORRECT: Handle Batch Full

```typescript
const sender = client.createSender("my-queue");
const messages = [/* many messages */];

let batch = await sender.createMessageBatch();

for (const msg of messages) {
  if (!batch.tryAddMessage({ body: msg })) {
    // Batch is full, send and create new
    await sender.sendMessages(batch);
    batch = await sender.createMessageBatch();
    
    if (!batch.tryAddMessage({ body: msg })) {
      throw new Error("Message too large for batch");
    }
  }
}

// Send remaining messages
await sender.sendMessages(batch);
await sender.close();
```

### 3.4 ✅ CORRECT: Send to Topic

```typescript
const topicSender = client.createSender("my-topic");

await topicSender.sendMessages({
  body: { event: "order.created", data: { orderId: "123" } },
  applicationProperties: { eventType: "order.created" },
});

await topicSender.close();
```

### 3.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not closing sender

```typescript
// WRONG - Always close the sender
const sender = client.createSender("my-queue");
await sender.sendMessages({ body: "Hello" });
// Missing: await sender.close();
```

---

## 4. Receiving Messages

### 4.1 ✅ CORRECT: Receive Messages (Pull Model)

```typescript
const receiver = client.createReceiver("my-queue");

const messages = await receiver.receiveMessages(10, { maxWaitTimeInMs: 5000 });

for (const message of messages) {
  console.log(`Received: ${message.body}`);
  await receiver.completeMessage(message);
}

await receiver.close();
```

### 4.2 ✅ CORRECT: Subscribe to Messages (Push Model)

```typescript
const receiver = client.createReceiver("my-queue");

const subscription = receiver.subscribe({
  processMessage: async (message) => {
    console.log(`Processing: ${message.body}`);
    // Message auto-completed on success in default mode
  },
  processError: async (args) => {
    console.error(`Error: ${args.error}`);
    console.error(`Entity path: ${args.entityPath}`);
  },
});

// Stop after some time
setTimeout(async () => {
  await subscription.close();
  await receiver.close();
}, 60000);
```

### 4.3 ✅ CORRECT: Receive from Subscription

```typescript
const subscriptionReceiver = client.createReceiver("my-topic", "my-subscription");

const messages = await subscriptionReceiver.receiveMessages(10);
for (const message of messages) {
  console.log(`Received: ${message.body}`);
  await subscriptionReceiver.completeMessage(message);
}

await subscriptionReceiver.close();
```

### 4.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not handling processError

```typescript
// WRONG - Always implement processError
receiver.subscribe({
  processMessage: async (message) => { /* ... */ },
  // Missing processError handler!
});
```

---

## 5. Message Settlement

### 5.1 ✅ CORRECT: Complete Message (Remove from Queue)

```typescript
const receiver = client.createReceiver("my-queue");
const messages = await receiver.receiveMessages(1);

if (messages.length > 0) {
  await receiver.completeMessage(messages[0]);
}
```

### 5.2 ✅ CORRECT: Abandon Message (Return to Queue)

```typescript
await receiver.abandonMessage(message, {
  propertiesToModify: {
    retryCount: (message.applicationProperties?.retryCount ?? 0) + 1,
  },
});
```

### 5.3 ✅ CORRECT: Defer Message (For Later Processing)

```typescript
await receiver.deferMessage(message);

// Later, receive deferred message by sequence number
const deferredMessage = await receiver.receiveDeferredMessages(message.sequenceNumber!);
await receiver.completeMessage(deferredMessage[0]);
```

### 5.4 ✅ CORRECT: Dead Letter Message

```typescript
await receiver.deadLetterMessage(message, {
  deadLetterReason: "Validation failed",
  deadLetterErrorDescription: "Missing required field: orderId",
});
```

---

## 6. Dead Letter Queue

### 6.1 ✅ CORRECT: Receive from Dead Letter Queue

```typescript
// Queue dead letter
const dlqReceiver = client.createReceiver("my-queue", { subQueueType: "deadLetter" });

// Subscription dead letter
const dlqSubscriptionReceiver = client.createReceiver("my-topic", "my-subscription", {
  subQueueType: "deadLetter",
});

const dlqMessages = await dlqReceiver.receiveMessages(10);
for (const msg of dlqMessages) {
  console.log(`DLQ Reason: ${msg.deadLetterReason}`);
  console.log(`DLQ Description: ${msg.deadLetterErrorDescription}`);
  // Process or resubmit
  await dlqReceiver.completeMessage(msg);
}

await dlqReceiver.close();
```

---

## 7. Sessions

### 7.1 ✅ CORRECT: Send Session Message

```typescript
const sender = client.createSender("session-queue");

await sender.sendMessages({
  body: { step: 1, data: "First step" },
  sessionId: "workflow-123",
});

await sender.close();
```

### 7.2 ✅ CORRECT: Accept Specific Session

```typescript
const sessionReceiver = await client.acceptSession("session-queue", "workflow-123");

const messages = await sessionReceiver.receiveMessages(10);
for (const message of messages) {
  console.log(`Session ${sessionReceiver.sessionId}: ${message.body}`);
  await sessionReceiver.completeMessage(message);
}

await sessionReceiver.close();
```

### 7.3 ✅ CORRECT: Accept Next Available Session

```typescript
const sessionReceiver = await client.acceptNextSession("session-queue");

console.log(`Accepted session: ${sessionReceiver.sessionId}`);

const messages = await sessionReceiver.receiveMessages(10);
for (const message of messages) {
  await sessionReceiver.completeMessage(message);
}

await sessionReceiver.close();
```

### 7.4 ✅ CORRECT: Session State

```typescript
const sessionReceiver = await client.acceptSession("session-queue", "workflow-123");

// Get session state
const state = await sessionReceiver.getSessionState();
console.log(`Current state: ${state?.toString()}`);

// Set session state
await sessionReceiver.setSessionState(
  Buffer.from(JSON.stringify({ progress: 50, lastStep: "validation" }))
);

await sessionReceiver.close();
```

---

## 8. Scheduled Messages

### 8.1 ✅ CORRECT: Schedule Message for Future Delivery

```typescript
const sender = client.createSender("my-queue");

const scheduledTime = new Date(Date.now() + 60000); // 1 minute from now
const sequenceNumber = await sender.scheduleMessages(
  { body: "Delayed message" },
  scheduledTime
);

console.log(`Scheduled message sequence: ${sequenceNumber}`);
await sender.close();
```

### 8.2 ✅ CORRECT: Cancel Scheduled Message

```typescript
const sender = client.createSender("my-queue");

const scheduledTime = new Date(Date.now() + 60000);
const sequenceNumber = await sender.scheduleMessages(
  { body: "Message to cancel" },
  scheduledTime
);

// Cancel before delivery
await sender.cancelScheduledMessages(sequenceNumber);
await sender.close();
```

---

## 9. Peek Messages

### 9.1 ✅ CORRECT: Peek Without Removing

```typescript
const receiver = client.createReceiver("my-queue");

const peekedMessages = await receiver.peekMessages(10);
for (const msg of peekedMessages) {
  console.log(`Peeked: ${msg.body}`);
  // Messages are not removed from queue
}

await receiver.close();
```

---

## 10. Receive Modes

### 10.1 ✅ CORRECT: Peek-Lock Mode (Default)

```typescript
// Default mode - message locked until completed/abandoned
const receiver = client.createReceiver("my-queue", { receiveMode: "peekLock" });

const messages = await receiver.receiveMessages(1);
if (messages.length > 0) {
  // Must explicitly settle the message
  await receiver.completeMessage(messages[0]);   // Remove
  // or
  await receiver.abandonMessage(messages[0]);    // Return to queue
  // or
  await receiver.deferMessage(messages[0]);      // Defer
  // or  
  await receiver.deadLetterMessage(messages[0]); // Move to DLQ
}
```

### 10.2 ✅ CORRECT: Receive-and-Delete Mode

```typescript
// Message removed immediately upon receipt - no settlement needed
const receiver = client.createReceiver("my-queue", { receiveMode: "receiveAndDelete" });

const messages = await receiver.receiveMessages(10);
for (const message of messages) {
  console.log(`Received and deleted: ${message.body}`);
  // No need to complete - message already removed
}
```

---

## 11. Error Handling

### 11.1 ✅ CORRECT: Handle Errors in Subscribe

```typescript
const receiver = client.createReceiver("my-queue");

receiver.subscribe({
  processMessage: async (message) => {
    try {
      await processBusinessLogic(message);
    } catch (error) {
      console.error("Business logic failed:", error);
      throw error; // Re-throw to trigger abandonment
    }
  },
  processError: async (args) => {
    console.error(`Error source: ${args.errorSource}`);
    console.error(`Entity path: ${args.entityPath}`);
    console.error(`Namespace: ${args.fullyQualifiedNamespace}`);
    console.error(`Error: ${args.error}`);
  },
});
```

---

## 12. Best Practices

1. **Use Entra ID auth** — Avoid connection strings in production
2. **Reuse clients** — Create `ServiceBusClient` once, share across senders/receivers
3. **Close resources** — Always close senders/receivers when done
4. **Handle errors** — Implement `processError` callback for subscription receivers
5. **Use sessions for ordering** — When message order matters within a group
6. **Configure dead-letter** — Always handle DLQ messages
7. **Batch sends** — Use `createMessageBatch()` for multiple messages
8. **Use peek-lock** — Default mode allows for reliable processing with settlement
