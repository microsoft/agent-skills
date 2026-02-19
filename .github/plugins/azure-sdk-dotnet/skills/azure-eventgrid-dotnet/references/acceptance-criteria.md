# Azure Event Grid SDK Acceptance Criteria (.NET)

**SDK**: `Azure.Messaging.EventGrid`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/eventgrid/Azure.Messaging.EventGrid
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Using Statements

### 1.1 ✅ CORRECT: Core Event Grid Imports
```csharp
using Azure.Messaging.EventGrid;
using Azure.Messaging.EventGrid.SystemEvents;
using Azure.Messaging;
```

### 1.2 ✅ CORRECT: For Namespaces (Pull Delivery)
```csharp
using Azure.Messaging.EventGrid.Namespaces;
```

### 1.3 ✅ CORRECT: With Identity
```csharp
using Azure.Identity;
using Azure.Messaging.EventGrid;
```

### 1.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong namespace
```csharp
// WRONG - Azure.Messaging.EventGrid not Microsoft.Azure.EventGrid
using Microsoft.Azure.EventGrid;
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: API Key Authentication
```csharp
using Azure;
using Azure.Messaging.EventGrid;

EventGridPublisherClient client = new(
    new Uri("https://mytopic.eastus-1.eventgrid.azure.net/api/events"),
    new AzureKeyCredential(Environment.GetEnvironmentVariable("EVENT_GRID_TOPIC_KEY")));
```

### 2.2 ✅ CORRECT: DefaultAzureCredential (Recommended)
```csharp
using Azure.Identity;
using Azure.Messaging.EventGrid;

EventGridPublisherClient client = new(
    new Uri("https://mytopic.eastus-1.eventgrid.azure.net/api/events"),
    new DefaultAzureCredential());
```

### 2.3 ✅ CORRECT: SAS Token Authentication
```csharp
string sasToken = EventGridPublisherClient.BuildSharedAccessSignature(
    new Uri(topicEndpoint),
    DateTimeOffset.UtcNow.AddHours(1),
    new AzureKeyCredential(topicKey));

var sasCredential = new AzureSasCredential(sasToken);
EventGridPublisherClient client = new(
    new Uri(topicEndpoint),
    sasCredential);
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded API key
```csharp
// WRONG - never hardcode API keys
EventGridPublisherClient client = new(
    new Uri(endpoint),
    new AzureKeyCredential("my-secret-key-12345"));
```

---

## 3. Client Hierarchy

### 3.1 Push Delivery (Topics/Domains)
```csharp
// EventGridPublisherClient for sending to topics and domains
EventGridPublisherClient client = new(endpoint, credential);
await client.SendEventAsync(eventGridEvent);
await client.SendEventsAsync(cloudEvents);
```

### 3.2 Pull Delivery (Namespaces)
```csharp
// EventGridSenderClient for sending to namespace topics
EventGridSenderClient senderClient = new(endpoint, topicName, credential);
await senderClient.SendAsync(cloudEvent);

// EventGridReceiverClient for receiving from subscriptions
EventGridReceiverClient receiverClient = new(endpoint, topicName, subscriptionName, credential);
var result = await receiverClient.ReceiveAsync(maxEvents: 10);
```

---

## 4. Publishing EventGridEvents

### 4.1 ✅ CORRECT: Single EventGridEvent
```csharp
EventGridPublisherClient client = new(
    new Uri(topicEndpoint),
    new AzureKeyCredential(topicKey));

EventGridEvent egEvent = new(
    subject: "orders/12345",
    eventType: "Order.Created",
    dataVersion: "1.0",
    data: new { OrderId = "12345", Amount = 99.99 });

await client.SendEventAsync(egEvent);
```

### 4.2 ✅ CORRECT: Batch of EventGridEvents
```csharp
List<EventGridEvent> events = new()
{
    new EventGridEvent(
        subject: "orders/12345",
        eventType: "Order.Created",
        dataVersion: "1.0",
        data: new OrderData { OrderId = "12345", Amount = 99.99 }),
    new EventGridEvent(
        subject: "orders/12346",
        eventType: "Order.Created",
        dataVersion: "1.0",
        data: new OrderData { OrderId = "12346", Amount = 149.99 })
};

await client.SendEventsAsync(events);
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing required EventGridEvent properties
```csharp
// WRONG - EventGridEvent requires subject, eventType, dataVersion, and data
EventGridEvent egEvent = new("Order.Created", new { OrderId = "123" });
```

---

## 5. Publishing CloudEvents

### 5.1 ✅ CORRECT: Single CloudEvent
```csharp
CloudEvent cloudEvent = new(
    source: "/orders/system",
    type: "Order.Created",
    data: new { OrderId = "12345", Amount = 99.99 });

cloudEvent.Subject = "orders/12345";
cloudEvent.Id = Guid.NewGuid().ToString();
cloudEvent.Time = DateTimeOffset.UtcNow;

await client.SendEventAsync(cloudEvent);
```

### 5.2 ✅ CORRECT: Batch of CloudEvents
```csharp
List<CloudEvent> cloudEvents = new()
{
    new CloudEvent("/orders", "Order.Created", new { OrderId = "1" }),
    new CloudEvent("/orders", "Order.Updated", new { OrderId = "2" })
};

await client.SendEventsAsync(cloudEvents);
```

---

## 6. Publishing to Event Grid Domain

### 6.1 ✅ CORRECT: Domain Events with Topic Routing
```csharp
List<EventGridEvent> events = new()
{
    new EventGridEvent(
        subject: "orders/12345",
        eventType: "Order.Created",
        dataVersion: "1.0",
        data: new { OrderId = "12345" })
    {
        Topic = "orders-topic"  // Domain topic name
    },
    new EventGridEvent(
        subject: "inventory/item-1",
        eventType: "Inventory.Updated",
        dataVersion: "1.0",
        data: new { ItemId = "item-1" })
    {
        Topic = "inventory-topic"
    }
};

await client.SendEventsAsync(events);
```

---

## 7. Pull Delivery (Namespaces)

### 7.1 ✅ CORRECT: Send to Namespace Topic
```csharp
using Azure;
using Azure.Messaging;
using Azure.Messaging.EventGrid.Namespaces;

var senderClient = new EventGridSenderClient(
    new Uri(namespaceEndpoint),
    topicName,
    new AzureKeyCredential(topicKey));

CloudEvent cloudEvent = new("employee_source", "Employee.Created", 
    new { Name = "John", Age = 30 });
await senderClient.SendAsync(cloudEvent);
```

### 7.2 ✅ CORRECT: Receive and Process Events
```csharp
var receiverClient = new EventGridReceiverClient(
    new Uri(namespaceEndpoint),
    topicName,
    subscriptionName,
    new AzureKeyCredential(topicKey));

// Receive events
ReceiveResult result = await receiverClient.ReceiveAsync(maxEvents: 10);

List<string> lockTokensToAck = new();
List<string> lockTokensToRelease = new();

foreach (ReceiveDetails detail in result.Details)
{
    CloudEvent cloudEvent = detail.Event;
    string lockToken = detail.BrokerProperties.LockToken;
    
    try
    {
        // Process the event
        Console.WriteLine($"Event: {cloudEvent.Type}, Data: {cloudEvent.Data}");
        lockTokensToAck.Add(lockToken);
    }
    catch (Exception)
    {
        // Release for retry
        lockTokensToRelease.Add(lockToken);
    }
}

// Acknowledge successfully processed events
if (lockTokensToAck.Any())
{
    await receiverClient.AcknowledgeAsync(lockTokensToAck);
}

// Release events for retry
if (lockTokensToRelease.Any())
{
    await receiverClient.ReleaseAsync(lockTokensToRelease);
}
```

### 7.3 ✅ CORRECT: Reject Events (Dead Letter)
```csharp
// Reject events that cannot be processed
await receiverClient.RejectAsync(new[] { lockToken });
```

---

## 8. Consuming Events (Azure Functions)

### 8.1 ✅ CORRECT: EventGridEvent Trigger
```csharp
using Azure.Messaging.EventGrid;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.EventGrid;

public static class EventGridFunction
{
    [FunctionName("ProcessEventGridEvent")]
    public static void Run(
        [EventGridTrigger] EventGridEvent eventGridEvent,
        ILogger log)
    {
        log.LogInformation($"Event Type: {eventGridEvent.EventType}");
        log.LogInformation($"Subject: {eventGridEvent.Subject}");
        log.LogInformation($"Data: {eventGridEvent.Data}");
    }
}
```

### 8.2 ✅ CORRECT: CloudEvent Trigger (Isolated Worker)
```csharp
using Azure.Messaging;
using Microsoft.Azure.Functions.Worker;

public class CloudEventFunction
{
    [Function("ProcessCloudEvent")]
    public void Run(
        [EventGridTrigger] CloudEvent cloudEvent,
        FunctionContext context)
    {
        var logger = context.GetLogger("ProcessCloudEvent");
        logger.LogInformation($"Event Type: {cloudEvent.Type}");
        logger.LogInformation($"Source: {cloudEvent.Source}");
        logger.LogInformation($"Data: {cloudEvent.Data}");
    }
}
```

---

## 9. Parsing Events

### 9.1 ✅ CORRECT: Parse EventGridEvent
```csharp
string json = "..."; // Event Grid webhook payload
EventGridEvent[] events = EventGridEvent.ParseMany(BinaryData.FromString(json));

foreach (EventGridEvent egEvent in events)
{
    if (egEvent.TryGetSystemEventData(out object systemEvent))
    {
        // Handle system event
        switch (systemEvent)
        {
            case StorageBlobCreatedEventData blobCreated:
                Console.WriteLine($"Blob created: {blobCreated.Url}");
                break;
        }
    }
    else
    {
        // Handle custom event
        var customData = egEvent.Data.ToObjectFromJson<MyCustomData>();
    }
}
```

### 9.2 ✅ CORRECT: Parse CloudEvent
```csharp
CloudEvent[] cloudEvents = CloudEvent.ParseMany(BinaryData.FromString(json));

foreach (CloudEvent cloudEvent in cloudEvents)
{
    var data = cloudEvent.Data.ToObjectFromJson<MyEventData>();
    Console.WriteLine($"Type: {cloudEvent.Type}, Data: {data}");
}
```

---

## 10. System Events

### 10.1 ✅ CORRECT: Handling System Events
```csharp
using Azure.Messaging.EventGrid.SystemEvents;

// Common system event types
StorageBlobCreatedEventData blobCreated;
StorageBlobDeletedEventData blobDeleted;
ResourceWriteSuccessEventData resourceCreated;
ContainerRegistryImagePushedEventData imagePushed;
IotHubDeviceCreatedEventData deviceCreated;
```

---

## 11. Error Handling

### 11.1 ✅ CORRECT: Handling Request Failures
```csharp
using Azure;

try
{
    await client.SendEventAsync(cloudEvent);
}
catch (RequestFailedException ex) when (ex.Status == 401)
{
    Console.WriteLine("Authentication failed - check credentials");
}
catch (RequestFailedException ex) when (ex.Status == 403)
{
    Console.WriteLine("Authorization failed - check RBAC permissions");
}
catch (RequestFailedException ex) when (ex.Status == 413)
{
    Console.WriteLine("Payload too large - max 1MB per event, 1MB total batch");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Event Grid error: {ex.Status} - {ex.Message}");
}
```

### 11.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Generic exception handling
```csharp
// WRONG - use specific RequestFailedException
try
{
    await client.SendEventAsync(cloudEvent);
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);
}
```

---

## 12. Failover Pattern

### 12.1 ✅ CORRECT: Region Failover
```csharp
try
{
    var primaryClient = new EventGridPublisherClient(primaryUri, credential);
    await primaryClient.SendEventsAsync(events);
}
catch (RequestFailedException)
{
    // Failover to secondary region
    var secondaryClient = new EventGridPublisherClient(secondaryUri, credential);
    await secondaryClient.SendEventsAsync(events);
}
```

---

## 13. Event Schemas Comparison

| Feature | EventGridEvent | CloudEvent |
|---------|----------------|------------|
| Standard | Azure-specific | CNCF standard |
| Required fields | subject, eventType, dataVersion, data | source, type |
| Extensibility | Limited | Extension attributes |
| Interoperability | Azure only | Cross-platform |

---

## 14. Best Practices

1. **Use CloudEvents** — Prefer CloudEvents for new implementations (industry standard)
2. **Batch events** — Send multiple events in one call for efficiency
3. **Use Entra ID** — Prefer managed identity over access keys
4. **Idempotent handlers** — Events may be delivered more than once
5. **Set event TTL** — Configure time-to-live for namespace events
6. **Handle partial failures** — Acknowledge/release events individually
7. **Use dead-letter** — Configure dead-letter for failed events
8. **Validate schemas** — Validate event data before processing

---

## Key Types Reference

| Type | Purpose |
|------|---------|
| `EventGridPublisherClient` | Publish to topics/domains |
| `EventGridSenderClient` | Send to namespace topics |
| `EventGridReceiverClient` | Receive from namespace subscriptions |
| `EventGridEvent` | Event Grid native schema |
| `CloudEvent` | CloudEvents 1.0 schema |
| `ReceiveResult` | Pull delivery response |
| `ReceiveDetails` | Event with broker properties |
| `BrokerProperties` | Lock token, delivery count |
