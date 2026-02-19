# Event Processing Reference

Receiving and processing events with Azure Event Hubs using the @azure/event-hubs TypeScript SDK.

## Overview

Event Hubs provides high-throughput event streaming. This reference covers the EventHubConsumerClient, subscription patterns, event handlers, and processing strategies.

## Key Interfaces

```typescript
import {
  EventHubConsumerClient,
  ReceivedEventData,
  PartitionContext,
  SubscriptionEventHandlers,
  SubscribeOptions,
  Subscription
} from "@azure/event-hubs";

// ReceivedEventData - structure of received events
interface ReceivedEventData {
  body: any;
  contentType?: string;
  correlationId?: string | number | Buffer;
  enqueuedTimeUtc: Date;
  messageId?: string | number | Buffer;
  offset: string;
  partitionKey: string | null;
  properties?: Record<string, any>;
  sequenceNumber: number;
  systemProperties?: Record<string, any>;
}

// PartitionContext - context for event handlers
interface PartitionContext {
  readonly consumerGroup: string;
  readonly eventHubName: string;
  readonly fullyQualifiedNamespace: string;
  readonly partitionId: string;
  readonly lastEnqueuedEventProperties?: LastEnqueuedEventProperties;
  updateCheckpoint(eventData: ReceivedEventData): Promise<void>;
}

// Handler types
type ProcessEventsHandler = (
  events: ReceivedEventData[],
  context: PartitionContext
) => Promise<void>;

type ProcessErrorHandler = (
  error: Error,
  context: PartitionContext
) => Promise<void>;

type ProcessInitializeHandler = (
  context: PartitionContext
) => Promise<void>;

type ProcessCloseHandler = (
  reason: CloseReason,
  context: PartitionContext
) => Promise<void>;
```

## Basic Subscribe Pattern

```typescript
import { EventHubConsumerClient, earliestEventPosition } from "@azure/event-hubs";
import { DefaultAzureCredential } from "@azure/identity";

const fullyQualifiedNamespace = "my-namespace.servicebus.windows.net";
const eventHubName = "my-event-hub";
const consumerGroup = "$Default";

const client = new EventHubConsumerClient(
  consumerGroup,
  fullyQualifiedNamespace,
  eventHubName,
  new DefaultAzureCredential()
);

const subscription = client.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      console.log(`Partition: ${context.partitionId}`);
      console.log(`Body: ${JSON.stringify(event.body)}`);
      console.log(`Sequence: ${event.sequenceNumber}`);
      console.log(`Enqueued: ${event.enqueuedTimeUtc}`);
    }
  },
  processError: async (err, context) => {
    console.error(`Error on partition ${context.partitionId}: ${err.message}`);
  }
}, {
  startPosition: earliestEventPosition
});

// Stop after some time
setTimeout(async () => {
  await subscription.close();
  await client.close();
}, 60000);
```

## Full Subscription with All Handlers

```typescript
import {
  EventHubConsumerClient,
  ReceivedEventData,
  PartitionContext,
  CloseReason,
  earliestEventPosition,
  latestEventPosition
} from "@azure/event-hubs";

const client = new EventHubConsumerClient(
  "$Default",
  connectionString,
  eventHubName
);

const subscription = client.subscribe({
  processInitialize: async (context: PartitionContext) => {
    console.log(`Started receiving from partition ${context.partitionId}`);
  },

  processEvents: async (events: ReceivedEventData[], context: PartitionContext) => {
    if (events.length === 0) {
      console.log(`No events received. Waiting...`);
      return;
    }

    console.log(`Received ${events.length} events from partition ${context.partitionId}`);
    
    for (const event of events) {
      // Process each event
      await processEvent(event, context);
    }

    // Checkpoint after processing batch
    const lastEvent = events[events.length - 1];
    await context.updateCheckpoint(lastEvent);
  },

  processError: async (err: Error, context: PartitionContext) => {
    console.error(`Error on partition ${context.partitionId}:`);
    console.error(err.message);
  },

  processClose: async (reason: CloseReason, context: PartitionContext) => {
    console.log(`Stopped receiving from partition ${context.partitionId}`);
    console.log(`Reason: ${reason}`);
  }
}, {
  startPosition: earliestEventPosition,
  maxBatchSize: 100,
  maxWaitTimeInSeconds: 30
});
```

## Subscribe to Specific Partition

```typescript
const client = new EventHubConsumerClient(
  "$Default",
  connectionString,
  eventHubName
);

// Get partition IDs
const partitionIds = await client.getPartitionIds();
console.log(`Partitions: ${partitionIds.join(", ")}`);

// Subscribe to specific partition
const subscription = client.subscribe(
  partitionIds[0], // First partition only
  {
    processEvents: async (events, context) => {
      console.log(`Partition ${context.partitionId}: ${events.length} events`);
    },
    processError: async (err, context) => {
      console.error(err);
    }
  },
  { startPosition: earliestEventPosition }
);
```

## Start Position Options

```typescript
import { 
  earliestEventPosition, 
  latestEventPosition,
  EventPosition 
} from "@azure/event-hubs";

// Start from beginning (all historical events)
const fromBeginning = { startPosition: earliestEventPosition };

// Start from end (new events only)
const fromEnd = { startPosition: latestEventPosition };

// Start from specific offset
const fromOffset: SubscribeOptions = {
  startPosition: { offset: "12345" }
};

// Start from specific sequence number
const fromSequence: SubscribeOptions = {
  startPosition: { sequenceNumber: 1000 }
};

// Start from specific time
const fromTime: SubscribeOptions = {
  startPosition: { enqueuedOn: new Date("2024-01-01T00:00:00Z") }
};

// Different positions per partition
const perPartition: SubscribeOptions = {
  startPosition: {
    "0": earliestEventPosition,
    "1": latestEventPosition,
    "2": { offset: "5000" }
  }
};
```

## SubscribeOptions Reference

```typescript
interface SubscribeOptions {
  /** Starting position for reading events */
  startPosition?: EventPosition | Record<string, EventPosition>;
  
  /** Max events per batch (default: varies) */
  maxBatchSize?: number;
  
  /** Max wait time in seconds for a batch */
  maxWaitTimeInSeconds?: number;
  
  /** Track last enqueued event info (for lag monitoring) */
  trackLastEnqueuedEventProperties?: boolean;
  
  /** Owner level for exclusive access */
  ownerLevel?: number;
}
```

## Event Processing Patterns

### Sequential Processing

```typescript
const subscription = client.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      await processEventSequentially(event);
    }
    await context.updateCheckpoint(events[events.length - 1]);
  },
  processError: async (err, context) => {
    console.error(err);
  }
});
```

### Parallel Processing within Batch

```typescript
const subscription = client.subscribe({
  processEvents: async (events, context) => {
    // Process events in parallel
    await Promise.all(
      events.map(event => processEventAsync(event))
    );
    
    // Checkpoint after all complete
    if (events.length > 0) {
      await context.updateCheckpoint(events[events.length - 1]);
    }
  },
  processError: async (err, context) => {
    console.error(err);
  }
});
```

### With Error Handling per Event

```typescript
const subscription = client.subscribe({
  processEvents: async (events, context) => {
    const results = await Promise.allSettled(
      events.map(event => processEvent(event))
    );
    
    const failures = results.filter(r => r.status === "rejected");
    if (failures.length > 0) {
      console.error(`${failures.length} events failed processing`);
      // Decide: checkpoint anyway or skip?
    }
    
    // Checkpoint even with some failures (at-least-once)
    if (events.length > 0) {
      await context.updateCheckpoint(events[events.length - 1]);
    }
  },
  processError: async (err, context) => {
    console.error(err);
  }
});
```

## Monitoring Consumer Lag

```typescript
const subscription = client.subscribe({
  processEvents: async (events, context) => {
    // Check lag if tracking enabled
    if (context.lastEnqueuedEventProperties) {
      const lastEnqueued = context.lastEnqueuedEventProperties.sequenceNumber;
      const lastProcessed = events.length > 0 
        ? events[events.length - 1].sequenceNumber 
        : 0;
      
      const lag = lastEnqueued - lastProcessed;
      console.log(`Partition ${context.partitionId} lag: ${lag} events`);
    }
    
    // Process events...
  },
  processError: async (err, context) => {
    console.error(err);
  }
}, {
  trackLastEnqueuedEventProperties: true
});
```

## Event Properties Access

```typescript
const subscription = client.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      // Standard properties
      console.log(`Body: ${event.body}`);
      console.log(`Partition Key: ${event.partitionKey}`);
      console.log(`Sequence Number: ${event.sequenceNumber}`);
      console.log(`Offset: ${event.offset}`);
      console.log(`Enqueued Time: ${event.enqueuedTimeUtc}`);
      
      // Custom properties (set by producer)
      if (event.properties) {
        console.log(`Event Type: ${event.properties.eventType}`);
        console.log(`Device ID: ${event.properties.deviceId}`);
      }
      
      // System properties
      if (event.systemProperties) {
        console.log(`System Props: ${JSON.stringify(event.systemProperties)}`);
      }
      
      // Content type
      if (event.contentType) {
        console.log(`Content Type: ${event.contentType}`);
      }
    }
  },
  processError: async (err, context) => {
    console.error(err);
  }
});
```

## Graceful Shutdown

```typescript
let subscription: Subscription;

async function start() {
  const client = new EventHubConsumerClient(
    "$Default",
    connectionString,
    eventHubName
  );

  subscription = client.subscribe({
    processEvents: async (events, context) => {
      // Process events...
    },
    processError: async (err, context) => {
      console.error(err);
    }
  });

  // Handle shutdown signals
  process.on("SIGINT", async () => {
    console.log("Shutting down...");
    await subscription.close();
    await client.close();
    process.exit(0);
  });

  process.on("SIGTERM", async () => {
    console.log("Shutting down...");
    await subscription.close();
    await client.close();
    process.exit(0);
  });
}

start().catch(console.error);
```

## Best Practices

1. **Always handle empty batches** — `processEvents` may receive empty arrays
2. **Checkpoint after processing** — Not before, to avoid data loss
3. **Use consumer groups** — Separate groups for different processing pipelines
4. **Monitor lag** — Enable `trackLastEnqueuedEventProperties`
5. **Handle errors gracefully** — Don't crash on individual event failures
6. **Close resources** — Always close subscription and client on shutdown
7. **Set appropriate batch size** — Balance throughput vs latency

## See Also

- [Checkpointing Reference](./checkpointing.md)
- [Azure Event Hubs Documentation](https://learn.microsoft.com/azure/event-hubs/)
- [Event Hubs Quotas](https://learn.microsoft.com/azure/event-hubs/event-hubs-quotas)
