# Checkpointing Reference

Persistent checkpointing with BlobCheckpointStore for Azure Event Hubs consumer applications.

## Overview

Checkpointing tracks the last successfully processed event position per partition. This enables:
- **Resumption** — Continue from where you left off after restart
- **Load balancing** — Distribute partitions across multiple consumers
- **Exactly-once processing** — When combined with idempotent downstream operations

## Installation

```bash
npm install @azure/event-hubs @azure/eventhubs-checkpointstore-blob @azure/storage-blob @azure/identity
```

## Key Interfaces

```typescript
import { CheckpointStore, Checkpoint, PartitionOwnership } from "@azure/event-hubs";

// CheckpointStore interface (implemented by BlobCheckpointStore)
interface CheckpointStore {
  listCheckpoints(
    fullyQualifiedNamespace: string,
    eventHubName: string,
    consumerGroup: string
  ): Promise<Checkpoint[]>;

  updateCheckpoint(checkpoint: Checkpoint): Promise<void>;

  listOwnership(
    fullyQualifiedNamespace: string,
    eventHubName: string,
    consumerGroup: string
  ): Promise<PartitionOwnership[]>;

  claimOwnership(
    partitionOwnership: PartitionOwnership[]
  ): Promise<PartitionOwnership[]>;
}

// Checkpoint structure
interface Checkpoint {
  fullyQualifiedNamespace: string;
  eventHubName: string;
  consumerGroup: string;
  partitionId: string;
  sequenceNumber: number;
  offset: string;
}

// Partition ownership (for load balancing)
interface PartitionOwnership {
  fullyQualifiedNamespace: string;
  eventHubName: string;
  consumerGroup: string;
  partitionId: string;
  ownerId: string;
  lastModifiedTimeInMs?: number;
  etag?: string;
}
```

## Basic Checkpointing Setup

```typescript
import { EventHubConsumerClient } from "@azure/event-hubs";
import { ContainerClient } from "@azure/storage-blob";
import { BlobCheckpointStore } from "@azure/eventhubs-checkpointstore-blob";
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();

// Storage for checkpoints
const storageAccountName = process.env.STORAGE_ACCOUNT_NAME!;
const containerName = "eventhub-checkpoints";

const containerClient = new ContainerClient(
  `https://${storageAccountName}.blob.core.windows.net/${containerName}`,
  credential
);

// Ensure container exists
await containerClient.createIfNotExists();

// Create checkpoint store
const checkpointStore = new BlobCheckpointStore(containerClient);

// Create consumer with checkpoint store
const consumerClient = new EventHubConsumerClient(
  "$Default",
  "my-namespace.servicebus.windows.net",
  "my-event-hub",
  credential,
  checkpointStore  // Pass checkpoint store here
);

const subscription = consumerClient.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      await processEvent(event);
    }
    
    // Checkpoint after successful processing
    if (events.length > 0) {
      await context.updateCheckpoint(events[events.length - 1]);
    }
  },
  processError: async (err, context) => {
    console.error(`Error: ${err.message}`);
  }
});
```

## Connection String Authentication

```typescript
import { EventHubConsumerClient } from "@azure/event-hubs";
import { ContainerClient } from "@azure/storage-blob";
import { BlobCheckpointStore } from "@azure/eventhubs-checkpointstore-blob";

// Storage connection string
const storageConnectionString = process.env.STORAGE_CONNECTION_STRING!;
const containerName = "checkpoints";

const containerClient = new ContainerClient(
  storageConnectionString,
  containerName
);

await containerClient.createIfNotExists();

const checkpointStore = new BlobCheckpointStore(containerClient);

// Event Hub connection string
const eventHubConnectionString = process.env.EVENTHUB_CONNECTION_STRING!;
const eventHubName = process.env.EVENTHUB_NAME!;

const consumerClient = new EventHubConsumerClient(
  "$Default",
  eventHubConnectionString,
  eventHubName,
  checkpointStore
);
```

## Checkpointing Strategies

### Checkpoint Every Batch (Default)

```typescript
const subscription = consumerClient.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      await processEvent(event);
    }
    
    // Checkpoint after every batch
    if (events.length > 0) {
      await context.updateCheckpoint(events[events.length - 1]);
    }
  },
  processError: async (err, context) => {
    console.error(err);
  }
});
```

### Checkpoint Every N Events

```typescript
let processedCount = 0;
const checkpointInterval = 100;

const subscription = consumerClient.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      await processEvent(event);
      processedCount++;
      
      // Checkpoint every N events
      if (processedCount % checkpointInterval === 0) {
        await context.updateCheckpoint(event);
        console.log(`Checkpointed at ${event.sequenceNumber}`);
      }
    }
  },
  processError: async (err, context) => {
    console.error(err);
  }
});
```

### Checkpoint on Time Interval

```typescript
let lastCheckpointTime = Date.now();
let lastEvent: ReceivedEventData | null = null;
const checkpointIntervalMs = 30000; // 30 seconds

const subscription = consumerClient.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      await processEvent(event);
      lastEvent = event;
    }
    
    // Checkpoint based on time
    const now = Date.now();
    if (lastEvent && (now - lastCheckpointTime) >= checkpointIntervalMs) {
      await context.updateCheckpoint(lastEvent);
      lastCheckpointTime = now;
      console.log(`Time-based checkpoint at ${lastEvent.sequenceNumber}`);
    }
  },
  processError: async (err, context) => {
    console.error(err);
  }
});
```

### Checkpoint Only on Success

```typescript
const subscription = consumerClient.subscribe({
  processEvents: async (events, context) => {
    const results = await Promise.allSettled(
      events.map(event => processEvent(event))
    );
    
    // Find last successfully processed event
    let lastSuccessIndex = -1;
    for (let i = results.length - 1; i >= 0; i--) {
      if (results[i].status === "fulfilled") {
        lastSuccessIndex = i;
        break;
      }
    }
    
    // Only checkpoint up to last success
    if (lastSuccessIndex >= 0) {
      await context.updateCheckpoint(events[lastSuccessIndex]);
    }
    
    // Log failures
    const failures = results.filter(r => r.status === "rejected");
    if (failures.length > 0) {
      console.error(`${failures.length} events failed processing`);
    }
  },
  processError: async (err, context) => {
    console.error(err);
  }
});
```

## Load Balancing Across Consumers

Multiple consumers with the same consumer group automatically balance partitions:

```typescript
// Consumer Instance 1
const consumer1 = new EventHubConsumerClient(
  "my-consumer-group",
  namespace,
  eventHubName,
  credential,
  checkpointStore
);

// Consumer Instance 2 (separate process)
const consumer2 = new EventHubConsumerClient(
  "my-consumer-group",  // Same consumer group
  namespace,
  eventHubName,
  credential,
  checkpointStore       // Same checkpoint store
);

// Both subscribe - partitions automatically distributed
consumer1.subscribe({ /* handlers */ });
consumer2.subscribe({ /* handlers */ });
```

## Checkpoint Store Blob Structure

The BlobCheckpointStore creates blobs in this structure:

```
<container>/
├── <namespace>/<eventhub>/<consumergroup>/checkpoint/
│   ├── 0    (checkpoint for partition 0)
│   ├── 1    (checkpoint for partition 1)
│   └── ...
└── <namespace>/<eventhub>/<consumergroup>/ownership/
    ├── 0    (ownership for partition 0)
    ├── 1    (ownership for partition 1)
    └── ...
```

## Inspecting Checkpoints

```typescript
import { BlobCheckpointStore } from "@azure/eventhubs-checkpointstore-blob";

const checkpointStore = new BlobCheckpointStore(containerClient);

// List all checkpoints
const checkpoints = await checkpointStore.listCheckpoints(
  "my-namespace.servicebus.windows.net",
  "my-event-hub",
  "$Default"
);

for (const cp of checkpoints) {
  console.log(`Partition ${cp.partitionId}:`);
  console.log(`  Sequence: ${cp.sequenceNumber}`);
  console.log(`  Offset: ${cp.offset}`);
}

// List partition ownership
const ownerships = await checkpointStore.listOwnership(
  "my-namespace.servicebus.windows.net",
  "my-event-hub",
  "$Default"
);

for (const own of ownerships) {
  console.log(`Partition ${own.partitionId}: owned by ${own.ownerId}`);
}
```

## Error Handling

```typescript
const subscription = consumerClient.subscribe({
  processEvents: async (events, context) => {
    try {
      for (const event of events) {
        await processEvent(event);
      }
      
      if (events.length > 0) {
        await context.updateCheckpoint(events[events.length - 1]);
      }
    } catch (processingError) {
      // Don't checkpoint on error - events will be reprocessed
      console.error("Processing failed:", processingError);
      // Optionally: send to dead letter, alert, etc.
    }
  },
  
  processError: async (err, context) => {
    // SDK-level errors (connection, auth, etc.)
    console.error(`SDK error on partition ${context.partitionId}:`, err.message);
    
    // The SDK handles reconnection automatically
    // Consider alerting for persistent errors
  }
});
```

## Graceful Shutdown with Final Checkpoint

```typescript
let lastProcessedEvent: Map<string, ReceivedEventData> = new Map();

const subscription = consumerClient.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      await processEvent(event);
      lastProcessedEvent.set(context.partitionId, event);
    }
    
    // Regular checkpointing
    if (events.length > 0) {
      await context.updateCheckpoint(events[events.length - 1]);
    }
  },
  processError: async (err, context) => {
    console.error(err);
  }
});

// Graceful shutdown
process.on("SIGTERM", async () => {
  console.log("Shutting down gracefully...");
  
  // Close subscription (stops receiving)
  await subscription.close();
  
  // Close consumer client
  await consumerClient.close();
  
  console.log("Shutdown complete");
  process.exit(0);
});
```

## Best Practices

1. **Checkpoint after processing** — Never before, to avoid data loss
2. **Balance checkpoint frequency** — Too often = high storage costs; too rare = more reprocessing on restart
3. **Use same checkpoint store** — All consumers in a group must share the same store
4. **Create container before use** — Call `createIfNotExists()` on startup
5. **Handle checkpoint failures** — Log and alert if `updateCheckpoint` fails repeatedly
6. **Use consumer groups** — Separate groups for different processing pipelines
7. **Design for reprocessing** — Make downstream operations idempotent

## Checkpoint Frequency Trade-offs

| Frequency | Pros | Cons |
|-----------|------|------|
| Every event | Minimal reprocessing | High storage I/O |
| Every batch | Good balance | Some reprocessing possible |
| Time-based | Predictable I/O | Variable reprocessing |
| Every N events | Controlled I/O | May miss some on crash |

## See Also

- [Event Processing Reference](./event-processing.md)
- [Azure Blob Storage](https://learn.microsoft.com/azure/storage/blobs/)
- [Event Hubs Consumer Groups](https://learn.microsoft.com/azure/event-hubs/event-hubs-features#consumer-groups)
