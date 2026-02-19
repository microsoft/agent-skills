# Queues vs Topics Patterns

Detailed patterns for Azure Service Bus queues and topics with @azure/service-bus.

## Queue Patterns (Point-to-Point)

Queues deliver each message to exactly one consumer. Use for work distribution.

### Basic Queue Sender

```typescript
import { ServiceBusClient, ServiceBusMessage } from "@azure/service-bus";
import { DefaultAzureCredential } from "@azure/identity";

const client = new ServiceBusClient(
  process.env.SERVICEBUS_NAMESPACE!,
  new DefaultAzureCredential()
);

const sender = client.createSender("order-queue");

// Send single message
const message: ServiceBusMessage = {
  body: { orderId: "12345", amount: 99.99 },
  contentType: "application/json",
  messageId: "unique-id-12345",
  correlationId: "request-abc",
  applicationProperties: {
    priority: "high",
    source: "web-app",
  },
};

await sender.sendMessages(message);
await sender.close();
```

### Batch Sending (Recommended for Multiple Messages)

```typescript
const sender = client.createSender("order-queue");

// Create batch with size limits
const batch = await sender.createMessageBatch();

const orders = [
  { orderId: "001", amount: 50 },
  { orderId: "002", amount: 75 },
  { orderId: "003", amount: 100 },
];

for (const order of orders) {
  const added = batch.tryAddMessage({ body: order });
  if (!added) {
    // Batch is full - send current batch and create new one
    await sender.sendMessages(batch);
    const newBatch = await sender.createMessageBatch();
    newBatch.tryAddMessage({ body: order });
  }
}

// Send remaining messages
if (batch.count > 0) {
  await sender.sendMessages(batch);
}

await sender.close();
```

### Queue Receiver (Pull Model)

```typescript
const receiver = client.createReceiver("order-queue", {
  receiveMode: "peekLock", // Default - message locked until settled
});

// Receive batch of messages
const messages = await receiver.receiveMessages(10, {
  maxWaitTimeInMs: 5000,
});

for (const message of messages) {
  try {
    const order = message.body;
    console.log(`Processing order: ${order.orderId}`);
    
    // Process successfully - remove from queue
    await receiver.completeMessage(message);
  } catch (error) {
    // Processing failed - return to queue for retry
    await receiver.abandonMessage(message);
  }
}

await receiver.close();
```

### Queue Subscriber (Push Model - Event-Driven)

```typescript
const receiver = client.createReceiver("order-queue");

const subscription = receiver.subscribe({
  processMessage: async (message) => {
    console.log(`Received: ${JSON.stringify(message.body)}`);
    // Message auto-completed on success when using subscribe()
  },
  processError: async (args) => {
    console.error(`Error source: ${args.errorSource}`);
    console.error(`Error: ${args.error.message}`);
    
    if (args.error.code === "MessageLockLost") {
      console.log("Message lock expired - will be redelivered");
    }
  },
}, {
  autoCompleteMessages: true, // Default
  maxConcurrentCalls: 5,
});

// Graceful shutdown
process.on("SIGTERM", async () => {
  await subscription.close();
  await receiver.close();
  await client.close();
});
```

## Topic Patterns (Publish-Subscribe)

Topics deliver messages to multiple subscriptions. Use for fan-out scenarios.

### Topic Publisher

```typescript
// Sending to a topic is identical to sending to a queue
const sender = client.createSender("order-events");

await sender.sendMessages({
  body: { event: "order.created", orderId: "12345" },
  applicationProperties: {
    eventType: "order.created",
    region: "us-west",
  },
  subject: "orders/created", // Can be used for filtering
});

await sender.close();
```

### Subscription Receiver

```typescript
// Receive from a specific subscription
const receiver = client.createReceiver(
  "order-events",      // Topic name
  "billing-service"    // Subscription name
);

const messages = await receiver.receiveMessages(10);

for (const message of messages) {
  console.log(`Billing received: ${message.body.event}`);
  await receiver.completeMessage(message);
}
```

### Multiple Subscriptions (Fan-Out)

```typescript
// Each subscription gets a copy of every message
// Create receivers for different services

const billingReceiver = client.createReceiver("order-events", "billing");
const inventoryReceiver = client.createReceiver("order-events", "inventory");
const notificationReceiver = client.createReceiver("order-events", "notifications");

// Each processes independently
billingReceiver.subscribe({
  processMessage: async (msg) => {
    await processBilling(msg.body);
  },
  processError: async (args) => console.error(args.error),
});

inventoryReceiver.subscribe({
  processMessage: async (msg) => {
    await updateInventory(msg.body);
  },
  processError: async (args) => console.error(args.error),
});
```

## Session-Enabled Queues (Ordered Processing)

Sessions guarantee FIFO ordering within a session and enable stateful processing.

### Send Session Messages

```typescript
const sender = client.createSender("workflow-queue");

// All messages with same sessionId processed in order by same receiver
await sender.sendMessages([
  { body: { step: 1, action: "validate" }, sessionId: "order-123" },
  { body: { step: 2, action: "charge" }, sessionId: "order-123" },
  { body: { step: 3, action: "fulfill" }, sessionId: "order-123" },
]);
```

### Accept Specific Session

```typescript
// Lock a specific session
const sessionReceiver = await client.acceptSession(
  "workflow-queue",
  "order-123"
);

// Process all messages for this session in order
const messages = await sessionReceiver.receiveMessages(10);

for (const message of messages) {
  console.log(`Step ${message.body.step}: ${message.body.action}`);
  await sessionReceiver.completeMessage(message);
}

await sessionReceiver.close();
```

### Accept Next Available Session

```typescript
// Accept any available session (load balancing)
const sessionReceiver = await client.acceptNextSession("workflow-queue", {
  maxAutoLockRenewalDurationInMs: 300000, // 5 minutes
});

console.log(`Processing session: ${sessionReceiver.sessionId}`);

// Get/set session state for checkpointing
const state = await sessionReceiver.getSessionState();
if (state) {
  const checkpoint = JSON.parse(state.toString());
  console.log(`Resuming from step: ${checkpoint.lastStep}`);
}

// Process messages...

// Save checkpoint
await sessionReceiver.setSessionState(
  Buffer.from(JSON.stringify({ lastStep: 3, status: "complete" }))
);

await sessionReceiver.close();
```

## Receive Modes

### Peek-Lock (Default - At-Least-Once)

```typescript
const receiver = client.createReceiver("my-queue", {
  receiveMode: "peekLock",
});

const [message] = await receiver.receiveMessages(1);

// Message is locked - other receivers can't see it
// You MUST settle the message:

await receiver.completeMessage(message);   // Success - remove from queue
await receiver.abandonMessage(message);    // Failure - return to queue
await receiver.deferMessage(message);      // Defer - retrieve by sequence number
await receiver.deadLetterMessage(message); // Move to DLQ
```

### Receive-and-Delete (At-Most-Once)

```typescript
const receiver = client.createReceiver("my-queue", {
  receiveMode: "receiveAndDelete",
});

const [message] = await receiver.receiveMessages(1);

// Message is immediately deleted - no settlement needed
// If processing fails, message is lost
console.log(`Received and deleted: ${message.body}`);
```

## Message Settlement Actions

```typescript
const receiver = client.createReceiver("my-queue");
const [message] = await receiver.receiveMessages(1);

// COMPLETE: Processing succeeded, remove message
await receiver.completeMessage(message);

// ABANDON: Processing failed, return to queue for retry
// Increments deliveryCount
await receiver.abandonMessage(message, {
  propertiesToModify: { retryReason: "timeout" },
});

// DEFER: Can't process now, retrieve later by sequence number
await receiver.deferMessage(message);
// Later: await receiver.receiveDeferredMessages([message.sequenceNumber!]);

// DEAD LETTER: Poison message, move to DLQ
await receiver.deadLetterMessage(message, {
  deadLetterReason: "ValidationFailed",
  deadLetterErrorDescription: "Missing required field: customerId",
});
```

## Scheduled Messages

```typescript
const sender = client.createSender("my-queue");

// Schedule for future delivery
const scheduledTime = new Date(Date.now() + 60 * 60 * 1000); // 1 hour from now

const sequenceNumbers = await sender.scheduleMessages(
  [
    { body: "Reminder: Complete your order" },
    { body: "Your cart is waiting" },
  ],
  scheduledTime
);

console.log(`Scheduled messages: ${sequenceNumbers}`);

// Cancel scheduled messages if needed
await sender.cancelScheduledMessages(sequenceNumbers);
```

## Peek Messages (Non-Destructive)

```typescript
const receiver = client.createReceiver("my-queue");

// Peek without removing or locking
const peekedMessages = await receiver.peekMessages(10);

for (const msg of peekedMessages) {
  console.log(`Peeked: ${msg.body}`);
  console.log(`Sequence: ${msg.sequenceNumber}`);
  console.log(`Enqueued: ${msg.enqueuedTimeUtc}`);
}

// Peek from specific sequence number
const moreMessages = await receiver.peekMessages(10, {
  fromSequenceNumber: 100n,
});
```

## When to Use Queues vs Topics

| Scenario | Use |
|----------|-----|
| Work distribution (one consumer per message) | Queue |
| Fan-out (multiple consumers per message) | Topic |
| Competing consumers (load balancing) | Queue |
| Event broadcasting | Topic |
| Request-reply pattern | Queue with reply-to |
| Ordered processing | Session-enabled Queue |
| Filtered delivery | Topic with subscription filters |
