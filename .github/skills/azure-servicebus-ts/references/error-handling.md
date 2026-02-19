# Error Handling and Reliability

Comprehensive error handling patterns for @azure/service-bus.

## ServiceBusError

All Service Bus errors extend `ServiceBusError` with a `code` property:

```typescript
import { ServiceBusError } from "@azure/service-bus";

try {
  await sender.sendMessages(message);
} catch (error) {
  if (error instanceof ServiceBusError) {
    console.log(`Code: ${error.code}`);
    console.log(`Message: ${error.message}`);
    console.log(`Retryable: ${error.retryable}`);
    
    handleServiceBusError(error);
  }
}
```

## Error Codes Reference

| Code | Description | Retryable | Action |
|------|-------------|-----------|--------|
| `GeneralError` | Unspecified error | Maybe | Log and investigate |
| `MessagingEntityNotFound` | Queue/topic/subscription doesn't exist | No | Check entity name, create entity |
| `MessageLockLost` | Lock expired before settlement | No | Message will be redelivered |
| `MessageNotFound` | Message no longer available | No | Already processed or expired |
| `MessageSizeExceeded` | Message too large (>256KB standard, >100MB premium) | No | Reduce message size or use claim check |
| `MessagingEntityAlreadyExists` | Entity already exists | No | Use existing entity |
| `MessagingEntityDisabled` | Entity is disabled | No | Enable entity in portal |
| `QuotaExceeded` | Namespace quota exceeded | No | Delete messages, upgrade tier |
| `ServiceBusy` | Service temporarily overloaded | Yes | Retry with backoff |
| `ServiceTimeout` | Operation timed out | Yes | Retry with backoff |
| `ServiceCommunicationProblem` | Network/connection issue | Yes | Retry with backoff |
| `SessionCannotBeLocked` | Session locked by another receiver | Yes | Retry or use different session |
| `SessionLockLost` | Session lock expired | No | Re-accept session |
| `UnauthorizedAccess` | Authentication/authorization failed | No | Check credentials/permissions |

## Error Handling by Code

```typescript
function handleServiceBusError(error: ServiceBusError): void {
  switch (error.code) {
    case "MessagingEntityNotFound":
      console.error(`Entity not found: ${error.message}`);
      // Create entity or fix configuration
      break;
      
    case "MessageLockLost":
      console.warn("Message lock lost - will be redelivered");
      // No action needed, message returns to queue
      break;
      
    case "MessageSizeExceeded":
      console.error("Message too large - use claim check pattern");
      // Store payload in blob, send reference
      break;
      
    case "QuotaExceeded":
      console.error("Quota exceeded - namespace is full");
      // Alert ops team, consider cleanup or upgrade
      break;
      
    case "ServiceBusy":
    case "ServiceTimeout":
    case "ServiceCommunicationProblem":
      if (error.retryable) {
        console.warn(`Transient error: ${error.code} - will retry`);
        // SDK handles retry automatically
      }
      break;
      
    case "SessionCannotBeLocked":
      console.warn("Session busy - trying another session");
      // Use acceptNextSession() instead
      break;
      
    case "SessionLockLost":
      console.warn("Session lock lost - re-accepting session");
      // Re-accept the session
      break;
      
    case "UnauthorizedAccess":
      console.error("Authorization failed - check credentials");
      // Verify RBAC roles or connection string
      break;
      
    default:
      console.error(`Unexpected error: ${error.code} - ${error.message}`);
  }
}
```

## ProcessErrorArgs in Subscribe

When using `receiver.subscribe()`, errors are delivered via `processError`:

```typescript
import { ProcessErrorArgs } from "@azure/service-bus";

receiver.subscribe({
  processMessage: async (message) => {
    // Process message
  },
  processError: async (args: ProcessErrorArgs) => {
    console.error(`Error source: ${args.errorSource}`);
    console.error(`Entity path: ${args.entityPath}`);
    console.error(`Namespace: ${args.fullyQualifiedNamespace}`);
    
    if (args.error instanceof ServiceBusError) {
      console.error(`Code: ${args.error.code}`);
      console.error(`Retryable: ${args.error.retryable}`);
    }
    
    // Error sources:
    // - "receive" - Error receiving messages
    // - "processMessageCallback" - Error in your processMessage handler
    // - "renewLock" - Error renewing message lock
    // - "complete" / "abandon" / "deadLetter" - Settlement errors
    
    switch (args.errorSource) {
      case "receive":
        console.log("Connection issue - SDK will reconnect");
        break;
      case "processMessageCallback":
        console.log("Bug in message handler - fix code");
        break;
      case "renewLock":
        console.log("Lock renewal failed - message may be redelivered");
        break;
    }
  },
});
```

## Dead Letter Queue Handling

Messages that can't be processed go to the dead letter queue (DLQ):

```typescript
// Create DLQ receiver
const dlqReceiver = client.createReceiver("my-queue", {
  subQueueType: "deadLetter",
});

// Process dead letters
const deadLetters = await dlqReceiver.receiveMessages(10);

for (const message of deadLetters) {
  console.log(`Dead letter reason: ${message.deadLetterReason}`);
  console.log(`Error description: ${message.deadLetterErrorDescription}`);
  console.log(`Original body: ${JSON.stringify(message.body)}`);
  console.log(`Delivery count: ${message.deliveryCount}`);
  console.log(`Enqueued time: ${message.enqueuedTimeUtc}`);
  
  // Analyze and fix the issue
  if (canReprocess(message)) {
    // Resend to main queue
    const sender = client.createSender("my-queue");
    await sender.sendMessages({ body: message.body });
    await sender.close();
  }
  
  // Remove from DLQ
  await dlqReceiver.completeMessage(message);
}

await dlqReceiver.close();
```

### DLQ for Topics

```typescript
// DLQ receiver for topic subscription
const dlqReceiver = client.createReceiver(
  "my-topic",
  "my-subscription",
  { subQueueType: "deadLetter" }
);
```

### Automatic Dead Lettering

Messages are automatically dead-lettered when:
- `deliveryCount` exceeds `maxDeliveryCount` (default: 10)
- Message TTL expires (if `deadLetteringOnMessageExpiration` is enabled)
- Subscription filter evaluation fails

## Graceful Shutdown

Always close resources in the correct order:

```typescript
const client = new ServiceBusClient(namespace, credential);
const sender = client.createSender("my-queue");
const receiver = client.createReceiver("my-queue");

// Subscribe to messages
const subscription = receiver.subscribe({
  processMessage: async (msg) => { /* ... */ },
  processError: async (args) => { /* ... */ },
});

// Graceful shutdown handler
async function shutdown(): Promise<void> {
  console.log("Shutting down...");
  
  // 1. Stop receiving new messages
  await subscription.close();
  
  // 2. Close receiver (waits for in-flight messages)
  await receiver.close();
  
  // 3. Close sender (waits for pending sends)
  await sender.close();
  
  // 4. Close client last
  await client.close();
  
  console.log("Shutdown complete");
}

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
```

## Lock Renewal

### Automatic Lock Renewal (Subscribe)

```typescript
// subscribe() automatically renews locks
receiver.subscribe({
  processMessage: async (message) => {
    // Lock is auto-renewed while processing
    await longRunningOperation(message.body);
  },
  processError: async (args) => { /* ... */ },
}, {
  // Max time to auto-renew (default: 5 minutes)
  maxAutoLockRenewalDurationInMs: 10 * 60 * 1000, // 10 minutes
});
```

### Manual Lock Renewal (receiveMessages)

```typescript
const [message] = await receiver.receiveMessages(1);

// For long processing, manually renew lock
const renewalInterval = setInterval(async () => {
  try {
    await receiver.renewMessageLock(message);
    console.log("Lock renewed");
  } catch (error) {
    console.error("Lock renewal failed:", error);
    clearInterval(renewalInterval);
  }
}, 30000); // Renew every 30 seconds

try {
  await longRunningOperation(message.body);
  await receiver.completeMessage(message);
} finally {
  clearInterval(renewalInterval);
}
```

### Session Lock Renewal

```typescript
const sessionReceiver = await client.acceptSession("my-queue", "session-123");

// Auto-renewal for sessions
const sessionReceiver = await client.acceptSession("my-queue", "session-123", {
  maxAutoLockRenewalDurationInMs: 10 * 60 * 1000,
});

// Manual renewal
await sessionReceiver.renewSessionLock();
```

## Connection Recovery

The SDK automatically handles connection recovery:

```typescript
// SDK reconnects automatically on transient failures
// No manual reconnection code needed

receiver.subscribe({
  processMessage: async (message) => {
    // Processing continues after reconnection
  },
  processError: async (args) => {
    if (args.errorSource === "receive") {
      // Connection issue - SDK is reconnecting
      console.log("Connection lost, SDK reconnecting...");
    }
  },
});
```

## Retry Configuration

Configure retry behavior at client level:

```typescript
import { ServiceBusClient } from "@azure/service-bus";

const client = new ServiceBusClient(namespace, credential, {
  retryOptions: {
    maxRetries: 3,
    retryDelayInMs: 1000,
    maxRetryDelayInMs: 30000,
    mode: "Exponential", // or "Fixed"
  },
});
```

## Idempotent Processing

Design for at-least-once delivery:

```typescript
receiver.subscribe({
  processMessage: async (message) => {
    const messageId = message.messageId;
    
    // Check if already processed (use database, Redis, etc.)
    if (await isAlreadyProcessed(messageId)) {
      console.log(`Duplicate message: ${messageId}`);
      return; // Message will be completed
    }
    
    // Process message
    await processOrder(message.body);
    
    // Mark as processed
    await markAsProcessed(messageId);
  },
  processError: async (args) => { /* ... */ },
});
```

## Poison Message Handling

Handle messages that repeatedly fail:

```typescript
receiver.subscribe({
  processMessage: async (message) => {
    // Check delivery count
    if (message.deliveryCount > 5) {
      console.warn(`Message ${message.messageId} failed ${message.deliveryCount} times`);
      
      // Dead letter with reason
      await receiver.deadLetterMessage(message, {
        deadLetterReason: "MaxRetriesExceeded",
        deadLetterErrorDescription: `Failed after ${message.deliveryCount} attempts`,
      });
      return;
    }
    
    try {
      await processMessage(message.body);
    } catch (error) {
      // Abandon to retry
      await receiver.abandonMessage(message, {
        propertiesToModify: {
          lastError: error.message,
          lastAttempt: new Date().toISOString(),
        },
      });
    }
  },
  processError: async (args) => { /* ... */ },
}, {
  autoCompleteMessages: false, // Manual settlement
});
```

## Best Practices Summary

1. **Always handle errors** - Implement `processError` callback
2. **Use peek-lock mode** - Ensures at-least-once delivery
3. **Design for idempotency** - Messages may be delivered multiple times
4. **Monitor dead letter queues** - Set up alerts for DLQ messages
5. **Configure appropriate lock duration** - Match to processing time
6. **Use auto-lock renewal** - For long-running operations
7. **Graceful shutdown** - Close resources in correct order
8. **Log error codes** - Helps diagnose issues
9. **Set maxDeliveryCount** - Prevent infinite retry loops
10. **Handle poison messages** - Dead letter after max retries
