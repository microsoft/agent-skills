# Azure Event Hubs SDK for TypeScript Acceptance Criteria

**SDK**: `@azure/event-hubs`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/eventhub/event-hubs
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: ESM Imports

```typescript
import { 
  EventHubProducerClient, 
  EventHubConsumerClient,
  earliestEventPosition,
  latestEventPosition,
} from "@azure/event-hubs";
```

### 1.2 ✅ CORRECT: Type Imports

```typescript
import type { 
  EventData,
  ReceivedEventData,
  PartitionContext,
  Subscription,
  SubscriptionEventHandlers,
  CreateBatchOptions,
  EventPosition,
} from "@azure/event-hubs";
```

### 1.3 ✅ CORRECT: Checkpoint Store Import

```typescript
import { BlobCheckpointStore } from "@azure/eventhubs-checkpointstore-blob";
import { ContainerClient } from "@azure/storage-blob";
```

### 1.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: CommonJS require

```typescript
// WRONG - Use ESM imports
const { EventHubProducerClient } = require("@azure/event-hubs");
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Recommended)

```typescript
import { EventHubProducerClient, EventHubConsumerClient } from "@azure/event-hubs";
import { DefaultAzureCredential } from "@azure/identity";

const fullyQualifiedNamespace = process.env.EVENTHUB_NAMESPACE!; // <namespace>.servicebus.windows.net
const eventHubName = process.env.EVENTHUB_NAME!;
const credential = new DefaultAzureCredential();

// Producer
const producer = new EventHubProducerClient(
  fullyQualifiedNamespace, 
  eventHubName, 
  credential
);

// Consumer
const consumer = new EventHubConsumerClient(
  "$Default",  // Consumer group
  fullyQualifiedNamespace,
  eventHubName,
  credential
);
```

### 2.2 ✅ CORRECT: Connection String

```typescript
import { EventHubProducerClient, EventHubConsumerClient } from "@azure/event-hubs";

const connectionString = process.env.EVENTHUB_CONNECTION_STRING!;
const eventHubName = process.env.EVENTHUB_NAME!;

const producer = new EventHubProducerClient(connectionString, eventHubName);
const consumer = new EventHubConsumerClient("$Default", connectionString, eventHubName);
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded connection string

```typescript
// WRONG - Never hardcode connection strings
const producer = new EventHubProducerClient(
  "Endpoint=sb://myns.servicebus.windows.net/;SharedAccessKeyName=key;SharedAccessKey=secret",
  "my-hub"
);
```

---

## 3. Sending Events

### 3.1 ✅ CORRECT: Create Batch and Send

```typescript
const producer = new EventHubProducerClient(namespace, eventHubName, credential);

const batch = await producer.createBatch();
batch.tryAdd({ body: { temperature: 72.5, deviceId: "sensor-1" } });
batch.tryAdd({ body: { temperature: 68.2, deviceId: "sensor-2" } });

await producer.sendBatch(batch);
await producer.close();
```

### 3.2 ✅ CORRECT: Send to Specific Partition

```typescript
// By partition ID
const batch = await producer.createBatch({ partitionId: "0" });
batch.tryAdd({ body: "Event for partition 0" });
await producer.sendBatch(batch);

// By partition key (consistent hashing)
const batch2 = await producer.createBatch({ partitionKey: "device-123" });
batch2.tryAdd({ body: "Event with partition key" });
await producer.sendBatch(batch2);
```

### 3.3 ✅ CORRECT: Send with Event Properties

```typescript
const batch = await producer.createBatch();
batch.tryAdd({
  body: { data: "payload" },
  properties: {
    eventType: "telemetry",
    deviceId: "sensor-1",
  },
  contentType: "application/json",
  correlationId: "request-123",
});
await producer.sendBatch(batch);
```

### 3.4 ✅ CORRECT: Handle Batch Full

```typescript
const events = [/* many events */];
let batch = await producer.createBatch();

for (const event of events) {
  if (!batch.tryAdd({ body: event })) {
    // Batch is full, send it and create a new one
    await producer.sendBatch(batch);
    batch = await producer.createBatch();
    
    if (!batch.tryAdd({ body: event })) {
      throw new Error("Event too large for a batch");
    }
  }
}

// Send remaining events
if (batch.count > 0) {
  await producer.sendBatch(batch);
}
```

### 3.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using batches

```typescript
// WRONG - Always use createBatch for efficient sending
await producer.sendBatch([{ body: "event1" }, { body: "event2" }]);
```

#### ❌ INCORRECT: Not closing producer

```typescript
// WRONG - Always close the producer
const producer = new EventHubProducerClient(namespace, eventHubName, credential);
await producer.sendBatch(batch);
// Missing: await producer.close();
```

---

## 4. Receiving Events

### 4.1 ✅ CORRECT: Simple Subscribe

```typescript
const consumer = new EventHubConsumerClient("$Default", namespace, eventHubName, credential);

const subscription = consumer.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      console.log(`Partition: ${context.partitionId}, Body: ${JSON.stringify(event.body)}`);
    }
  },
  processError: async (err, context) => {
    console.error(`Error on partition ${context.partitionId}: ${err.message}`);
  },
});

// Stop after some time
setTimeout(async () => {
  await subscription.close();
  await consumer.close();
}, 60000);
```

### 4.2 ✅ CORRECT: Subscribe with Checkpointing (Production)

```typescript
import { EventHubConsumerClient } from "@azure/event-hubs";
import { ContainerClient } from "@azure/storage-blob";
import { BlobCheckpointStore } from "@azure/eventhubs-checkpointstore-blob";
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();
const storageAccount = process.env.STORAGE_ACCOUNT_NAME!;
const containerName = process.env.STORAGE_CONTAINER_NAME!;

const containerClient = new ContainerClient(
  `https://${storageAccount}.blob.core.windows.net/${containerName}`,
  credential
);

const checkpointStore = new BlobCheckpointStore(containerClient);

const consumer = new EventHubConsumerClient(
  "$Default",
  process.env.EVENTHUB_NAMESPACE!,
  process.env.EVENTHUB_NAME!,
  credential,
  checkpointStore
);

const subscription = consumer.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      console.log(`Processing: ${JSON.stringify(event.body)}`);
    }
    // Checkpoint after processing batch
    if (events.length > 0) {
      await context.updateCheckpoint(events[events.length - 1]);
    }
  },
  processError: async (err, context) => {
    console.error(`Error: ${err.message}`);
  },
});
```

### 4.3 ✅ CORRECT: Subscribe from Specific Position

```typescript
import { earliestEventPosition, latestEventPosition } from "@azure/event-hubs";

const subscription = consumer.subscribe(
  {
    processEvents: async (events, context) => { /* ... */ },
    processError: async (err, context) => { /* ... */ },
  },
  {
    startPosition: {
      // Start from beginning
      "0": earliestEventPosition,
      // Start from end (new events only)
      "1": latestEventPosition,
      // Start from specific offset
      "2": { offset: "12345" },
      // Start from specific time
      "3": { enqueuedOn: new Date("2024-01-01") },
    },
  }
);
```

### 4.4 ✅ CORRECT: Subscribe to Specific Partition

```typescript
const partitionIds = await consumer.getPartitionIds();

const subscription = consumer.subscribe(
  partitionIds[0],  // Subscribe to first partition only
  {
    processEvents: async (events, context) => { /* ... */ },
    processError: async (err, context) => { /* ... */ },
  }
);
```

### 4.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not handling processError

```typescript
// WRONG - Always implement processError
const subscription = consumer.subscribe({
  processEvents: async (events, context) => { /* ... */ },
  // Missing processError handler!
});
```

#### ❌ INCORRECT: Checkpointing on error

```typescript
// WRONG - Don't checkpoint when processing fails
const subscription = consumer.subscribe({
  processEvents: async (events, context) => {
    try {
      for (const event of events) {
        await processEvent(event);
      }
    } catch (error) {
      console.error(error);
    }
    // WRONG - Checkpointing even when processing failed
    await context.updateCheckpoint(events[events.length - 1]);
  },
});
```

---

## 5. Batch Processing Options

### 5.1 ✅ CORRECT: Configure Batch Size and Wait Time

```typescript
const subscription = consumer.subscribe(
  {
    processEvents: async (events, context) => { /* ... */ },
    processError: async (err, context) => { /* ... */ },
  },
  {
    maxBatchSize: 100,           // Max events per batch
    maxWaitTimeInSeconds: 30,    // Max wait for batch
  }
);
```

---

## 6. Event Hub Properties

### 6.1 ✅ CORRECT: Get Hub and Partition Info

```typescript
// Get hub info
const hubProperties = await producer.getEventHubProperties();
console.log(`Partitions: ${hubProperties.partitionIds}`);

// Get partition info
const partitionProperties = await producer.getPartitionProperties("0");
console.log(`Last sequence: ${partitionProperties.lastEnqueuedSequenceNumber}`);
console.log(`Last enqueued: ${partitionProperties.lastEnqueuedOnUtc}`);
```

---

## 7. Error Handling

### 7.1 ✅ CORRECT: Handle Errors Gracefully

```typescript
consumer.subscribe({
  processEvents: async (events, context) => {
    try {
      for (const event of events) {
        await processEvent(event);
      }
      // Only checkpoint on success
      if (events.length > 0) {
        await context.updateCheckpoint(events[events.length - 1]);
      }
    } catch (error) {
      // Don't checkpoint on error - events will be reprocessed
      console.error("Processing failed:", error);
    }
  },
  processError: async (err, context) => {
    if (err.name === "MessagingError") {
      // Transient error - SDK will retry
      console.warn("Transient error:", err.message);
    } else {
      // Fatal error
      console.error("Fatal error:", err);
    }
  },
});
```

---

## 8. Accessing Event Properties

### 8.1 ✅ CORRECT: Access Event Metadata

```typescript
consumer.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      console.log(`Body: ${JSON.stringify(event.body)}`);
      console.log(`Properties: ${JSON.stringify(event.properties)}`);
      console.log(`Sequence: ${event.sequenceNumber}`);
      console.log(`Enqueued: ${event.enqueuedTimeUtc}`);
      console.log(`Offset: ${event.offset}`);
      console.log(`Partition: ${context.partitionId}`);
    }
  },
  processError: async (err, context) => { /* ... */ },
});
```

---

## 9. Best Practices

1. **Use checkpointing** — Always checkpoint in production for exactly-once processing
2. **Batch sends** — Use `createBatch()` for efficient sending
3. **Partition keys** — Use partition keys to ensure ordering for related events
4. **Consumer groups** — Use separate consumer groups for different processing pipelines
5. **Handle errors gracefully** — Don't checkpoint on processing failures
6. **Close clients** — Always close producer/consumer when done
7. **Monitor lag** — Track `lastEnqueuedSequenceNumber` vs processed sequence
