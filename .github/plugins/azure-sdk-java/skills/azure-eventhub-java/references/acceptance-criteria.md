# Azure Event Hubs Java SDK Acceptance Criteria

**SDK**: `com.azure:azure-messaging-eventhubs`
**Repository**: https://github.com/Azure/azure-sdk-for-java
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Client Builder Patterns

### ✅ CORRECT: EventHubProducerClient with DefaultAzureCredential

```java
import com.azure.messaging.eventhubs.EventHubProducerClient;
import com.azure.messaging.eventhubs.EventHubClientBuilder;
import com.azure.identity.DefaultAzureCredentialBuilder;

EventHubProducerClient producer = new EventHubClientBuilder()
    .fullyQualifiedNamespace(System.getenv("EVENT_HUBS_NAMESPACE"))
    .eventHubName(System.getenv("EVENT_HUB_NAME"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildProducerClient();
```

### ✅ CORRECT: EventHubConsumerClient with Consumer Group

```java
import com.azure.messaging.eventhubs.EventHubConsumerClient;

EventHubConsumerClient consumer = new EventHubClientBuilder()
    .fullyQualifiedNamespace(System.getenv("EVENT_HUBS_NAMESPACE"))
    .eventHubName(System.getenv("EVENT_HUB_NAME"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .consumerGroup(EventHubClientBuilder.DEFAULT_CONSUMER_GROUP_NAME)
    .buildConsumerClient();
```

### ✅ CORRECT: Async Clients for High Throughput

```java
import com.azure.messaging.eventhubs.EventHubProducerAsyncClient;
import com.azure.messaging.eventhubs.EventHubConsumerAsyncClient;

EventHubProducerAsyncClient asyncProducer = new EventHubClientBuilder()
    .fullyQualifiedNamespace(namespace)
    .eventHubName(eventHubName)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncProducerClient();

EventHubConsumerAsyncClient asyncConsumer = new EventHubClientBuilder()
    .fullyQualifiedNamespace(namespace)
    .eventHubName(eventHubName)
    .credential(new DefaultAzureCredentialBuilder().build())
    .consumerGroup("$Default")
    .buildAsyncConsumerClient();
```

### ❌ INCORRECT: Hardcoded Connection String

```java
// WRONG - hardcoded connection string
EventHubProducerClient producer = new EventHubClientBuilder()
    .connectionString("Endpoint=sb://mynamespace.servicebus.windows.net/;SharedAccessKeyName=...")
    .eventHubName("myeventhub")
    .buildProducerClient();
```

### ❌ INCORRECT: Missing Consumer Group

```java
// WRONG - consumer requires consumer group
EventHubConsumerClient consumer = new EventHubClientBuilder()
    .connectionString(connectionString)
    .buildConsumerClient();  // Missing .consumerGroup()
```

---

## 2. Sending Events

### ✅ CORRECT: Batch Sending with EventDataBatch

```java
import com.azure.messaging.eventhubs.EventData;
import com.azure.messaging.eventhubs.EventDataBatch;

EventDataBatch batch = producer.createBatch();

for (int i = 0; i < events.size(); i++) {
    EventData event = new EventData(events.get(i));
    if (!batch.tryAdd(event)) {
        // Batch is full, send and create new batch
        producer.send(batch);
        batch = producer.createBatch();
        if (!batch.tryAdd(event)) {
            throw new IllegalArgumentException("Event too large for batch");
        }
    }
}

// Send remaining events
if (batch.getCount() > 0) {
    producer.send(batch);
}
```

### ✅ CORRECT: Send with Partition Key

```java
import com.azure.messaging.eventhubs.models.CreateBatchOptions;

CreateBatchOptions options = new CreateBatchOptions()
    .setPartitionKey("customer-" + customerId);

EventDataBatch batch = producer.createBatch(options);
batch.tryAdd(new EventData("Order created for customer " + customerId));
producer.send(batch);
```

### ✅ CORRECT: Event with Properties

```java
EventData event = new EventData("Order created");
event.getProperties().put("orderId", "ORD-123");
event.getProperties().put("customerId", "CUST-456");
event.getProperties().put("timestamp", Instant.now().toString());

producer.send(Collections.singletonList(event));
```

### ❌ INCORRECT: Sending Unbatched in Loop

```java
// WRONG - inefficient, creates overhead per event
for (String data : eventDataList) {
    producer.send(Collections.singletonList(new EventData(data)));
}
```

### ❌ INCORRECT: Ignoring tryAdd Return Value

```java
// WRONG - ignores batch size limits
EventDataBatch batch = producer.createBatch();
for (EventData event : events) {
    batch.tryAdd(event);  // May silently fail if batch is full
}
producer.send(batch);
```

---

## 3. EventProcessorClient (Production Pattern)

### ✅ CORRECT: EventProcessorClient with BlobCheckpointStore

```java
import com.azure.messaging.eventhubs.EventProcessorClient;
import com.azure.messaging.eventhubs.EventProcessorClientBuilder;
import com.azure.messaging.eventhubs.checkpointstore.blob.BlobCheckpointStore;
import com.azure.storage.blob.BlobContainerAsyncClient;
import com.azure.storage.blob.BlobContainerClientBuilder;

// Create checkpoint store
BlobContainerAsyncClient blobClient = new BlobContainerClientBuilder()
    .connectionString(System.getenv("STORAGE_CONNECTION_STRING"))
    .containerName("checkpoints")
    .buildAsyncClient();

// Create processor
EventProcessorClient processor = new EventProcessorClientBuilder()
    .fullyQualifiedNamespace(System.getenv("EVENT_HUBS_NAMESPACE"))
    .eventHubName(System.getenv("EVENT_HUB_NAME"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .consumerGroup("$Default")
    .checkpointStore(new BlobCheckpointStore(blobClient))
    .processEvent(eventContext -> {
        EventData event = eventContext.getEventData();
        System.out.printf("Processing: %s from partition %s%n",
            event.getBodyAsString(),
            eventContext.getPartitionContext().getPartitionId());

        // Checkpoint after successful processing
        eventContext.updateCheckpoint();
    })
    .processError(errorContext -> {
        System.err.printf("Error on partition %s: %s%n",
            errorContext.getPartitionContext().getPartitionId(),
            errorContext.getThrowable().getMessage());
    })
    .buildEventProcessorClient();

// Start processing
processor.start();

// Graceful shutdown
Runtime.getRuntime().addShutdownHook(new Thread(processor::stop));
```

### ✅ CORRECT: Batch Event Processing

```java
EventProcessorClient processor = new EventProcessorClientBuilder()
    .fullyQualifiedNamespace(namespace)
    .eventHubName(eventHubName)
    .credential(new DefaultAzureCredentialBuilder().build())
    .consumerGroup("$Default")
    .checkpointStore(new BlobCheckpointStore(blobClient))
    .processEventBatch(eventBatchContext -> {
        List<EventData> events = eventBatchContext.getEvents();
        System.out.printf("Processing batch of %d events%n", events.size());

        for (EventData event : events) {
            processEvent(event);
        }

        // Checkpoint after batch
        eventBatchContext.updateCheckpoint();
    }, 100)  // maxBatchSize
    .processError(errorContext -> {
        System.err.println("Error: " + errorContext.getThrowable().getMessage());
    })
    .buildEventProcessorClient();
```

### ❌ INCORRECT: No Checkpointing

```java
// WRONG - events will be reprocessed on restart
.processEvent(eventContext -> {
    processEvent(eventContext.getEventData());
    // Missing eventContext.updateCheckpoint();
})
```

### ❌ INCORRECT: Using ConsumerClient for Production

```java
// WRONG - ConsumerClient doesn't support load balancing or checkpointing
EventHubConsumerClient consumer = new EventHubClientBuilder()
    .connectionString(connectionString)
    .consumerGroup("$Default")
    .buildConsumerClient();

// Use EventProcessorClient for production workloads
```

---

## 4. Receiving Events

### ✅ CORRECT: Receive from Partition with EventPosition

```java
import com.azure.messaging.eventhubs.models.EventPosition;
import com.azure.messaging.eventhubs.models.PartitionEvent;
import java.time.Duration;

Iterable<PartitionEvent> events = consumer.receiveFromPartition(
    "0",                           // partitionId
    100,                           // maxEvents
    EventPosition.earliest(),      // from beginning
    Duration.ofSeconds(30)         // timeout
);

for (PartitionEvent partitionEvent : events) {
    EventData event = partitionEvent.getData();
    System.out.printf("Sequence: %d, Offset: %s, Body: %s%n",
        event.getSequenceNumber(),
        event.getOffset(),
        event.getBodyAsString());
}
```

### ✅ CORRECT: Event Position Options

```java
// From beginning of partition
EventPosition.earliest()

// From end (new events only)
EventPosition.latest()

// From specific offset
EventPosition.fromOffset(12345L)

// From sequence number
EventPosition.fromSequenceNumber(100L)

// From specific time
EventPosition.fromEnqueuedTime(Instant.now().minus(Duration.ofHours(1)))
```

### ❌ INCORRECT: Hardcoded Partition ID

```java
// WRONG - partition count may change
consumer.receiveFromPartition("0", 100, EventPosition.latest(), timeout);
// Use EventProcessorClient for automatic partition assignment
```

---

## 5. Async Receiving

### ✅ CORRECT: Async Consumer with Flux

```java
import com.azure.messaging.eventhubs.models.EventPosition;

asyncConsumer.receiveFromPartition("0", EventPosition.latest())
    .subscribe(
        partitionEvent -> {
            EventData event = partitionEvent.getData();
            System.out.printf("Received: %s%n", event.getBodyAsString());
        },
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Completed")
    );
```

### ✅ CORRECT: Async Producer Send

```java
asyncProducer.createBatch()
    .flatMap(batch -> {
        batch.tryAdd(new EventData("Event 1"));
        batch.tryAdd(new EventData("Event 2"));
        return asyncProducer.send(batch);
    })
    .subscribe(
        unused -> System.out.println("Batch sent successfully"),
        error -> System.err.println("Send failed: " + error.getMessage())
    );
```

---

## 6. Error Handling

### ✅ CORRECT: Process Error Handler

```java
import com.azure.messaging.eventhubs.models.ErrorContext;
import com.azure.core.amqp.exception.AmqpException;

.processError(errorContext -> {
    Throwable error = errorContext.getThrowable();
    String partitionId = errorContext.getPartitionContext().getPartitionId();

    if (error instanceof AmqpException) {
        AmqpException amqpError = (AmqpException) error;
        if (amqpError.isTransient()) {
            System.out.printf("Transient error on partition %s, will retry%n", partitionId);
            return;
        }
    }

    System.err.printf("Error on partition %s: %s%n", partitionId, error.getMessage());
    // Log to monitoring system
})
```

### ❌ INCORRECT: Empty Error Handler

```java
// WRONG - silently ignores errors
.processError(errorContext -> {})
```

---

## 7. Resource Cleanup

### ✅ CORRECT: Try-with-Resources

```java
try (EventHubProducerClient producer = new EventHubClientBuilder()
        .fullyQualifiedNamespace(namespace)
        .eventHubName(eventHubName)
        .credential(new DefaultAzureCredentialBuilder().build())
        .buildProducerClient()) {

    EventDataBatch batch = producer.createBatch();
    batch.tryAdd(new EventData("Test event"));
    producer.send(batch);
}
```

### ✅ CORRECT: Explicit Close in Finally

```java
EventHubProducerClient producer = null;
try {
    producer = new EventHubClientBuilder()
        .fullyQualifiedNamespace(namespace)
        .eventHubName(eventHubName)
        .credential(new DefaultAzureCredentialBuilder().build())
        .buildProducerClient();

    producer.send(batch);
} finally {
    if (producer != null) {
        producer.close();
    }
}
```

### ❌ INCORRECT: Missing Close

```java
// WRONG - connection leak
EventHubProducerClient producer = new EventHubClientBuilder()
    .connectionString(connectionString)
    .buildProducerClient();
producer.send(batch);
// Missing producer.close()
```

---

## 8. Event Hub Properties

### ✅ CORRECT: Get Hub and Partition Info

```java
import com.azure.messaging.eventhubs.EventHubProperties;
import com.azure.messaging.eventhubs.PartitionProperties;

// Get hub properties
EventHubProperties hubProps = producer.getEventHubProperties();
System.out.printf("Hub: %s, Partitions: %s%n",
    hubProps.getName(),
    hubProps.getPartitionIds());

// Get partition properties
for (String partitionId : hubProps.getPartitionIds()) {
    PartitionProperties partitionProps = producer.getPartitionProperties(partitionId);
    System.out.printf("Partition %s: begin=%d, end=%d%n",
        partitionId,
        partitionProps.getBeginningSequenceNumber(),
        partitionProps.getLastEnqueuedSequenceNumber());
}
```
