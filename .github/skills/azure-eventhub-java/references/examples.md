# Azure Event Hubs Java SDK - Examples

Comprehensive code examples for the Azure Event Hubs SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [EventHubProducerClient](#eventhubproducerclient)
- [EventHubConsumerClient](#eventhubconsumerclient)
- [EventProcessorClient](#eventprocessorclient)
- [Checkpointing Patterns](#checkpointing-patterns)
- [Partition Handling](#partition-handling)

---

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-messaging-eventhubs</artifactId>
    <version>5.21.0</version>
</dependency>

<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.18.2</version>
</dependency>

<!-- For EventProcessorClient with blob checkpointing -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-messaging-eventhubs-checkpointstore-blob</artifactId>
    <version>1.21.0</version>
</dependency>
```

---

## EventHubProducerClient

### Basic Producer with Azure Identity

```java
import com.azure.messaging.eventhubs.*;
import com.azure.identity.DefaultAzureCredentialBuilder;

import java.util.Arrays;
import java.util.List;

import static java.nio.charset.StandardCharsets.UTF_8;

public class PublishEventsWithAzureIdentity {
    public static void main(String[] args) {
        List<EventData> telemetryEvents = Arrays.asList(
            new EventData("Roast beef".getBytes(UTF_8)),
            new EventData("Cheese".getBytes(UTF_8)),
            new EventData("Tofu".getBytes(UTF_8)),
            new EventData("Turkey".getBytes(UTF_8)));

        // Create a producer
        // "<<fully-qualified-namespace>>" = "{your-namespace}.servicebus.windows.net"
        EventHubProducerClient producer = new EventHubClientBuilder()
            .credential(
                "<<fully-qualified-namespace>>",
                "<<event-hub-name>>",
                new DefaultAzureCredentialBuilder().build())
            .buildProducerClient();

        // Create batch - Event Hubs auto-routes to available partitions
        EventDataBatch currentBatch = producer.createBatch();

        // Add events to batch, send when full
        for (EventData event : telemetryEvents) {
            if (currentBatch.tryAdd(event)) {
                continue;
            }

            // Batch is full - send and create new batch
            producer.send(currentBatch);
            currentBatch = producer.createBatch();

            if (!currentBatch.tryAdd(event)) {
                System.err.printf("Event is too large for an empty batch. Max size: %s.%n",
                    currentBatch.getMaxSizeInBytes());
            }
        }

        // Send remaining events
        producer.send(currentBatch);
        
        producer.close();
    }
}
```

### Producer with Connection String

```java
String connectionString = "Endpoint={endpoint};SharedAccessKeyName={sharedAccessKeyName};"
    + "SharedAccessKey={sharedAccessKey};EntityPath={eventHubName}";

EventHubProducerClient producer = new EventHubClientBuilder()
    .connectionString(connectionString)
    .buildProducerClient();
```

### Send to Specific Partition

```java
import com.azure.messaging.eventhubs.models.CreateBatchOptions;

// Route all events in batch to partition "0"
CreateBatchOptions options = new CreateBatchOptions().setPartitionId("0");
EventDataBatch batch = producer.createBatch(options);

batch.tryAdd(new EventData("Event for partition 0"));
producer.send(batch);
```

### Send with Partition Key (Hash-based Routing)

```java
import com.azure.messaging.eventhubs.models.SendOptions;

List<EventData> events = Arrays.asList(
    new EventData("Melbourne"), 
    new EventData("London"),
    new EventData("New York"));

// Events with same partition key go to same partition
SendOptions sendOptions = new SendOptions().setPartitionKey("cities");
producer.send(events, sendOptions);
```

---

## EventHubConsumerClient

### Synchronous Consumer

```java
import com.azure.core.util.IterableStream;
import com.azure.messaging.eventhubs.*;
import com.azure.messaging.eventhubs.models.EventPosition;
import com.azure.messaging.eventhubs.models.PartitionEvent;
import com.azure.identity.DefaultAzureCredentialBuilder;

import java.time.Duration;
import java.time.Instant;

EventHubConsumerClient consumer = new EventHubClientBuilder()
    .credential("<<fully-qualified-namespace>>", "<<event-hub-name>>",
        new DefaultAzureCredentialBuilder().build())
    .consumerGroup(EventHubClientBuilder.DEFAULT_CONSUMER_GROUP_NAME)
    .buildConsumerClient();

// Start from 12 hours ago
Instant twelveHoursAgo = Instant.now().minus(Duration.ofHours(12));
EventPosition startingPosition = EventPosition.fromEnqueuedTime(twelveHoursAgo);
String partitionId = "0";

// Receive up to 100 events or wait 30 seconds
IterableStream<PartitionEvent> events = consumer.receiveFromPartition(
    partitionId, 100, startingPosition, Duration.ofSeconds(30));

Long lastSequenceNumber = -1L;
for (PartitionEvent partitionEvent : events) {
    System.out.print("Event received: " + partitionEvent.getData().getSequenceNumber());
    lastSequenceNumber = partitionEvent.getData().getSequenceNumber();
}

// Continue from last processed event
if (lastSequenceNumber != -1L) {
    EventPosition nextPosition = EventPosition.fromSequenceNumber(lastSequenceNumber, false);
    IterableStream<PartitionEvent> nextEvents = consumer.receiveFromPartition(
        partitionId, 100, nextPosition, Duration.ofSeconds(30));
}

consumer.close();
```

### Asynchronous Consumer (Reactive)

```java
import com.azure.messaging.eventhubs.*;
import com.azure.messaging.eventhubs.models.PartitionContext;
import reactor.core.Disposable;

EventHubConsumerAsyncClient consumer = new EventHubClientBuilder()
    .credential("<<fully-qualified-namespace>>", "<<event-hub-name>>",
        new DefaultAzureCredentialBuilder().build())
    .consumerGroup(EventHubClientBuilder.DEFAULT_CONSUMER_GROUP_NAME)
    .buildAsyncConsumerClient();

String partitionId = "0";
EventPosition startingPosition = EventPosition.latest();

// Non-blocking - returns immediately
Disposable subscription = consumer.receiveFromPartition(partitionId, startingPosition)
    .subscribe(partitionEvent -> {
        PartitionContext partitionContext = partitionEvent.getPartitionContext();
        EventData event = partitionEvent.getData();

        System.out.printf("Received event from partition '%s'%n", partitionContext.getPartitionId());
        System.out.printf("Contents: '%s'%n", event.getBodyAsString());
    }, error -> {
        System.err.print("An error occurred: " + error);
    }, () -> {
        System.out.print("Stream has ended.");
    });

// When done receiving
subscription.dispose();
consumer.close();
```

---

## EventProcessorClient

### Basic EventProcessorClient with Checkpointing

```java
import com.azure.messaging.eventhubs.*;
import com.azure.messaging.eventhubs.checkpointstore.blob.BlobCheckpointStore;
import com.azure.messaging.eventhubs.models.ErrorContext;
import com.azure.messaging.eventhubs.models.EventContext;
import com.azure.storage.blob.BlobContainerAsyncClient;
import com.azure.storage.blob.BlobContainerClientBuilder;
import com.azure.identity.DefaultAzureCredentialBuilder;

import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

public class EventProcessorClientSample {
    public static void main(String[] args) throws Exception {
        
        // Event handler - processes each event and checkpoints
        Consumer<EventContext> processEvent = eventContext -> {
            System.out.printf("Processing event: partition=%s, sequence=%d%n",
                eventContext.getPartitionContext().getPartitionId(),
                eventContext.getEventData().getSequenceNumber());

            // Checkpoint after processing each event
            eventContext.updateCheckpoint();
        };

        // Error handler - logs errors, processor keeps running
        Consumer<ErrorContext> processError = errorContext -> {
            System.err.printf("Error while processing partition %s: %s%n", 
                errorContext.getPartitionContext().getPartitionId(),
                errorContext.getThrowable().getMessage());
        };

        // Create blob container client for checkpoint store
        BlobContainerAsyncClient blobContainerAsyncClient = new BlobContainerClientBuilder()
            .credential(new DefaultAzureCredentialBuilder().build())
            .endpoint("<storage-account-url>")
            .containerName("checkpoints")
            .buildAsyncClient();

        EventProcessorClient eventProcessorClient = new EventProcessorClientBuilder()
            .consumerGroup(EventHubClientBuilder.DEFAULT_CONSUMER_GROUP_NAME)
            .credential("<<fully-qualified-namespace>>", "<<event-hub-name>>",
                new DefaultAzureCredentialBuilder().build())
            .processEvent(processEvent)
            .processError(processError)
            .checkpointStore(new BlobCheckpointStore(blobContainerAsyncClient))
            .buildEventProcessorClient();
        
        System.out.println("Starting event processor");
        eventProcessorClient.start();

        // Processor runs in background - do other work
        Thread.sleep(TimeUnit.MINUTES.toMillis(1));

        System.out.println("Stopping event processor");
        eventProcessorClient.stop();
    }
}
```

---

## Checkpointing Patterns

### Batch Processing with Periodic Checkpointing

```java
import com.azure.messaging.eventhubs.*;
import com.azure.messaging.eventhubs.models.EventBatchContext;

import java.time.Duration;
import java.util.function.Consumer;

// Process 50 events in a batch OR wait up to 30 seconds
Consumer<EventBatchContext> processBatch = batchContext -> {
    if (batchContext.getEvents().isEmpty()) {
        return;
    }

    for (EventData event : batchContext.getEvents()) {
        System.out.printf("Processing event: partition=%s, sequence=%d%n",
            batchContext.getPartitionContext().getPartitionId(),
            event.getSequenceNumber());
    }

    // Checkpoint after processing entire batch
    batchContext.updateCheckpoint();
};

EventProcessorClient processor = new EventProcessorClientBuilder()
    .consumerGroup(EventHubClientBuilder.DEFAULT_CONSUMER_GROUP_NAME)
    .credential("<<fully-qualified-namespace>>", "<<event-hub-name>>",
        new DefaultAzureCredentialBuilder().build())
    .processEventBatch(processBatch, 50, Duration.ofSeconds(30))
    .processError(processError)
    .checkpointStore(new BlobCheckpointStore(blobContainerAsyncClient))
    .buildEventProcessorClient();

processor.start();
```

### Checkpoint After N Events

```java
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

// Track events per partition
Map<String, AtomicInteger> partitionCounters = new ConcurrentHashMap<>();
int checkpointAfterN = 100;

Consumer<EventContext> processEvent = eventContext -> {
    String partitionId = eventContext.getPartitionContext().getPartitionId();
    
    // Process event
    System.out.println("Event: " + eventContext.getEventData().getBodyAsString());
    
    // Increment counter for this partition
    AtomicInteger counter = partitionCounters.computeIfAbsent(
        partitionId, k -> new AtomicInteger(0));
    
    if (counter.incrementAndGet() >= checkpointAfterN) {
        eventContext.updateCheckpoint();
        counter.set(0);
        System.out.printf("Checkpointed partition %s%n", partitionId);
    }
};
```

---

## Partition Handling

### Get Partition Information

```java
EventHubProducerClient producer = new EventHubClientBuilder()
    .credential("<<namespace>>", "<<event-hub>>",
        new DefaultAzureCredentialBuilder().build())
    .buildProducerClient();

// Get Event Hub properties
EventHubProperties eventHubProperties = producer.getEventHubProperties();
System.out.println("Event Hub: " + eventHubProperties.getName());
System.out.println("Partitions: " + eventHubProperties.getPartitionIds());

// Get specific partition properties
for (String partitionId : eventHubProperties.getPartitionIds()) {
    PartitionProperties partitionProperties = producer.getPartitionProperties(partitionId);
    System.out.printf("Partition %s: begin=%d, end=%d%n",
        partitionId,
        partitionProperties.getBeginningSequenceNumber(),
        partitionProperties.getLastEnqueuedSequenceNumber());
}
```

### Event Position Options

```java
import com.azure.messaging.eventhubs.models.EventPosition;
import java.time.Instant;

// From beginning of partition
EventPosition fromStart = EventPosition.earliest();

// From end (new events only)
EventPosition fromEnd = EventPosition.latest();

// From specific sequence number (exclusive)
EventPosition fromSequence = EventPosition.fromSequenceNumber(12345L, false);

// From specific sequence number (inclusive)
EventPosition fromSequenceInclusive = EventPosition.fromSequenceNumber(12345L, true);

// From specific time
EventPosition fromTime = EventPosition.fromEnqueuedTime(Instant.now().minusSeconds(3600));

// From specific offset
EventPosition fromOffset = EventPosition.fromOffset(1000L);
```
