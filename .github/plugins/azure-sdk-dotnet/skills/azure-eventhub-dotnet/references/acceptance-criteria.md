# Azure Event Hubs SDK Acceptance Criteria (.NET)

**SDK**: `Azure.Messaging.EventHubs`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/eventhub
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Using Statements

### 1.1 ✅ CORRECT: Core Event Hubs Imports
```csharp
using Azure.Messaging.EventHubs;
using Azure.Messaging.EventHubs.Producer;
using Azure.Messaging.EventHubs.Consumer;
using Azure.Messaging.EventHubs.Processor;
```

### 1.2 ✅ CORRECT: With Identity and Storage (for checkpointing)
```csharp
using Azure.Identity;
using Azure.Messaging.EventHubs;
using Azure.Messaging.EventHubs.Processor;
using Azure.Storage.Blobs;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong namespace
```csharp
// WRONG - Azure.Messaging.EventHubs not Microsoft.Azure.EventHubs
using Microsoft.Azure.EventHubs;
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Preferred)
```csharp
using Azure.Identity;
using Azure.Messaging.EventHubs.Producer;

var credential = new DefaultAzureCredential();
var fullyQualifiedNamespace = Environment.GetEnvironmentVariable("EVENTHUB_FULLY_QUALIFIED_NAMESPACE");
var eventHubName = Environment.GetEnvironmentVariable("EVENTHUB_NAME");

var producer = new EventHubProducerClient(
    fullyQualifiedNamespace,
    eventHubName,
    credential);
```

### 2.2 ✅ CORRECT: Connection String
```csharp
using Azure.Messaging.EventHubs.Producer;

string connectionString = Environment.GetEnvironmentVariable("EVENTHUB_CONNECTION_STRING");
await using var producer = new EventHubProducerClient(connectionString);
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded connection string
```csharp
// WRONG - never hardcode connection strings
await using var producer = new EventHubProducerClient(
    "Endpoint=sb://mynamespace.servicebus.windows.net/;SharedAccessKeyName=...");
```

---

## 3. Client Types

### 3.1 Client Selection Guide
| Client | Purpose | When to Use |
|--------|---------|-------------|
| `EventHubProducerClient` | Send events immediately in batches | Real-time sending, full control |
| `EventHubBufferedProducerClient` | Automatic batching with background sending | High-volume, fire-and-forget |
| `EventHubConsumerClient` | Simple event reading | **Prototyping only** |
| `EventProcessorClient` | Production event processing | **Always use for receiving** |

### 3.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using EventHubConsumerClient in production
```csharp
// WRONG - use EventProcessorClient for production receiving
var consumer = new EventHubConsumerClient(consumerGroup, connectionString);
await foreach (var partitionEvent in consumer.ReadEventsAsync())
{
    // No checkpointing, no partition ownership management
}
```

---

## 4. Sending Events

### 4.1 ✅ CORRECT: Send Events with Batching
```csharp
await using var producer = new EventHubProducerClient(
    fullyQualifiedNamespace,
    eventHubName,
    new DefaultAzureCredential());

// Create a batch (respects size limits automatically)
using EventDataBatch batch = await producer.CreateBatchAsync();

var events = new[]
{
    new EventData(BinaryData.FromString("{\"id\": 1, \"message\": \"Hello\"}")),
    new EventData(BinaryData.FromString("{\"id\": 2, \"message\": \"World\"}"))
};

foreach (var eventData in events)
{
    if (!batch.TryAdd(eventData))
    {
        // Batch is full - send it and create a new one
        await producer.SendAsync(batch);
        batch = await producer.CreateBatchAsync();
        
        if (!batch.TryAdd(eventData))
        {
            throw new Exception("Event too large for empty batch");
        }
    }
}

// Send remaining events
if (batch.Count > 0)
{
    await producer.SendAsync(batch);
}
```

### 4.2 ✅ CORRECT: Buffered Producer (High Volume)
```csharp
using Azure.Messaging.EventHubs.Producer;

var options = new EventHubBufferedProducerClientOptions
{
    MaximumWaitTime = TimeSpan.FromSeconds(1)
};

await using var producer = new EventHubBufferedProducerClient(
    fullyQualifiedNamespace,
    eventHubName,
    new DefaultAzureCredential(),
    options);

// Handle send success/failure
producer.SendEventBatchSucceededAsync += args =>
{
    Console.WriteLine($"Batch sent: {args.EventBatch.Count} events");
    return Task.CompletedTask;
};

producer.SendEventBatchFailedAsync += args =>
{
    Console.WriteLine($"Batch failed: {args.Exception.Message}");
    return Task.CompletedTask;
};

// Enqueue events (sent automatically in background)
for (int i = 0; i < 1000; i++)
{
    await producer.EnqueueEventAsync(new EventData($"Event {i}"));
}

// Flush remaining events before disposing
await producer.FlushAsync();
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using batch for multiple events
```csharp
// WRONG - inefficient, sends each event individually
foreach (var eventData in events)
{
    await producer.SendAsync(new[] { eventData });
}
```

---

## 5. Receiving Events (Production)

### 5.1 ✅ CORRECT: EventProcessorClient with Checkpointing
```csharp
using Azure.Identity;
using Azure.Messaging.EventHubs;
using Azure.Messaging.EventHubs.Consumer;
using Azure.Messaging.EventHubs.Processor;
using Azure.Storage.Blobs;

// Blob container for checkpointing
var blobClient = new BlobContainerClient(
    Environment.GetEnvironmentVariable("BLOB_STORAGE_CONNECTION_STRING"),
    Environment.GetEnvironmentVariable("BLOB_CONTAINER_NAME"));

await blobClient.CreateIfNotExistsAsync();

// Create processor
var processor = new EventProcessorClient(
    blobClient,
    EventHubConsumerClient.DefaultConsumerGroup,
    fullyQualifiedNamespace,
    eventHubName,
    new DefaultAzureCredential());

// Handle events
processor.ProcessEventAsync += async args =>
{
    Console.WriteLine($"Partition: {args.Partition.PartitionId}");
    Console.WriteLine($"Data: {args.Data.EventBody}");
    
    // Checkpoint after processing
    await args.UpdateCheckpointAsync();
};

// Handle errors
processor.ProcessErrorAsync += args =>
{
    Console.WriteLine($"Error: {args.Exception.Message}");
    Console.WriteLine($"Partition: {args.PartitionId}");
    return Task.CompletedTask;
};

// Start processing
await processor.StartProcessingAsync();

// Run until cancelled
await Task.Delay(Timeout.Infinite, cancellationToken);

// Stop gracefully
await processor.StopProcessingAsync();
```

### 5.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not handling ProcessErrorAsync
```csharp
// WRONG - always register error handler
processor.ProcessEventAsync += async args =>
{
    await args.UpdateCheckpointAsync();
};
// Missing: processor.ProcessErrorAsync += ...
await processor.StartProcessingAsync();
```

---

## 6. Partition Operations

### 6.1 ✅ CORRECT: Get Partition IDs
```csharp
string[] partitionIds = await producer.GetPartitionIdsAsync();
```

### 6.2 ✅ CORRECT: Send to Specific Partition (Use Sparingly)
```csharp
var options = new SendEventOptions
{
    PartitionId = "0"
};
await producer.SendAsync(events, options);
```

### 6.3 ✅ CORRECT: Use Partition Key (Recommended)
```csharp
var batchOptions = new CreateBatchOptions
{
    PartitionKey = "customer-123"  // Events with same key go to same partition
};
using var batch = await producer.CreateBatchAsync(batchOptions);
```

### 6.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Mixing PartitionId and PartitionKey
```csharp
// WRONG - cannot use both
var batchOptions = new CreateBatchOptions
{
    PartitionId = "0",
    PartitionKey = "customer-123"  // Will throw
};
```

---

## 7. EventPosition Options

### 7.1 ✅ CORRECT: Starting Position Options
```csharp
// Start from beginning
EventPosition.Earliest

// Start from end (new events only)
EventPosition.Latest

// Start from specific offset
EventPosition.FromOffset(12345)

// Start from specific sequence number
EventPosition.FromSequenceNumber(100)

// Start from specific time
EventPosition.FromEnqueuedTime(DateTimeOffset.UtcNow.AddHours(-1))
```

---

## 8. Checkpointing Strategies

### 8.1 ✅ CORRECT: Checkpoint Every N Events
```csharp
private int _eventCount = 0;

processor.ProcessEventAsync += async args =>
{
    // Process event...
    
    _eventCount++;
    if (_eventCount >= 100)
    {
        await args.UpdateCheckpointAsync();
        _eventCount = 0;
    }
};
```

### 8.2 ✅ CORRECT: Checkpoint After Each Event (Low Volume)
```csharp
processor.ProcessEventAsync += async args =>
{
    // Process event...
    await args.UpdateCheckpointAsync();
};
```

### 8.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Never checkpointing
```csharp
// WRONG - will reprocess all events on restart
processor.ProcessEventAsync += async args =>
{
    Console.WriteLine(args.Data.EventBody);
    // Missing: await args.UpdateCheckpointAsync();
};
```

---

## 9. ASP.NET Core Integration

### 9.1 ✅ CORRECT: Dependency Injection
```csharp
using Azure.Identity;
using Azure.Messaging.EventHubs.Producer;
using Microsoft.Extensions.Azure;

builder.Services.AddAzureClients(clientBuilder =>
{
    clientBuilder.AddEventHubProducerClient(
        builder.Configuration["EventHub:FullyQualifiedNamespace"],
        builder.Configuration["EventHub:Name"]);
    
    clientBuilder.UseCredential(new DefaultAzureCredential());
});

// Inject in controller/service
public class EventService
{
    private readonly EventHubProducerClient _producer;
    
    public EventService(EventHubProducerClient producer)
    {
        _producer = producer;
    }
    
    public async Task SendAsync(string message)
    {
        using var batch = await _producer.CreateBatchAsync();
        batch.TryAdd(new EventData(message));
        await _producer.SendAsync(batch);
    }
}
```

---

## 10. Error Handling

### 10.1 ✅ CORRECT: Handling Event Hubs Exceptions
```csharp
using Azure.Messaging.EventHubs;

try
{
    await producer.SendAsync(batch);
}
catch (EventHubsException ex) when (ex.Reason == EventHubsException.FailureReason.ServiceBusy)
{
    // Retry with backoff
    await Task.Delay(TimeSpan.FromSeconds(5));
}
catch (EventHubsException ex) when (ex.IsTransient)
{
    // Transient error - safe to retry
    Console.WriteLine($"Transient error: {ex.Message}");
}
catch (EventHubsException ex)
{
    // Non-transient error
    Console.WriteLine($"Error: {ex.Reason} - {ex.Message}");
}
```

### 10.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Generic exception handling
```csharp
// WRONG - use specific EventHubsException
try
{
    await producer.SendAsync(batch);
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);
}
```

---

## 11. Resource Management

### 11.1 ✅ CORRECT: Proper Disposal Pattern
```csharp
await using var producer = new EventHubProducerClient(
    fullyQualifiedNamespace,
    eventHubName,
    new DefaultAzureCredential());

// Use producer...
// Automatically disposed at end of scope
```

### 11.2 ✅ CORRECT: Singleton Pattern (Thread-Safe)
```csharp
// Clients are thread-safe and should be reused
public class EventHubService : IAsyncDisposable
{
    private readonly EventHubProducerClient _producer;
    
    public EventHubService(string fullyQualifiedNamespace, string eventHubName)
    {
        _producer = new EventHubProducerClient(
            fullyQualifiedNamespace,
            eventHubName,
            new DefaultAzureCredential());
    }
    
    public async Task SendAsync(string message)
    {
        using var batch = await _producer.CreateBatchAsync();
        batch.TryAdd(new EventData(message));
        await _producer.SendAsync(batch);
    }
    
    public async ValueTask DisposeAsync()
    {
        await _producer.DisposeAsync();
    }
}
```

---

## Key Types Reference

| Type | Purpose |
|------|---------|
| `EventHubProducerClient` | Send events to Event Hubs |
| `EventHubBufferedProducerClient` | Automatic batching producer |
| `EventHubConsumerClient` | Simple consumer (not for production) |
| `EventProcessorClient` | Production event processing with checkpointing |
| `EventData` | Event to send |
| `EventDataBatch` | Batch of events |
| `PartitionReceiver` | Low-level partition reading |
| `BlobContainerClient` | For checkpoint storage |

---

## Required RBAC Roles

| Operation | Required Role |
|-----------|---------------|
| Sending | `Azure Event Hubs Data Sender` |
| Receiving | `Azure Event Hubs Data Receiver` |
| Both | `Azure Event Hubs Data Owner` |
