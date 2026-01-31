# Azure Event Grid Acceptance Criteria

**SDK**: `com.azure:azure-messaging-eventgrid`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/eventgrid/azure-messaging-eventgrid
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Full qualified client imports
```java
import com.azure.messaging.eventgrid.EventGridPublisherClient;
import com.azure.messaging.eventgrid.EventGridPublisherClientBuilder;
import com.azure.messaging.eventgrid.EventGridPublisherAsyncClient;
```

#### ❌ INCORRECT: Wrong package imports
```java
import com.azure.eventgrid.EventGridPublisherClient;
```

### 1.2 Event Type Imports
#### ✅ CORRECT: EventGridEvent and CloudEvent
```java
import com.azure.messaging.eventgrid.EventGridEvent;
import com.azure.core.models.CloudEvent;
import com.azure.core.models.CloudEventDataFormat;
```

### 1.3 Credential Imports
#### ✅ CORRECT: Authentication credentials
```java
import com.azure.core.credential.AzureKeyCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
```

---

## 2. Client Creation Patterns

### 2.1 EventGridEvent Publisher
#### ✅ CORRECT: With API Key
```java
EventGridPublisherClient<EventGridEvent> client = new EventGridPublisherClientBuilder()
    .endpoint("<topic-endpoint>")
    .credential(new AzureKeyCredential("<access-key>"))
    .buildEventGridEventPublisherClient();
```

### 2.2 CloudEvent Publisher
#### ✅ CORRECT: CloudEvent client
```java
EventGridPublisherClient<CloudEvent> cloudClient = new EventGridPublisherClientBuilder()
    .endpoint("<topic-endpoint>")
    .credential(new AzureKeyCredential("<access-key>"))
    .buildCloudEventPublisherClient();
```

### 2.3 With DefaultAzureCredential
#### ✅ CORRECT: Entra ID authentication
```java
EventGridPublisherClient<EventGridEvent> client = new EventGridPublisherClientBuilder()
    .endpoint("<topic-endpoint>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildEventGridEventPublisherClient();
```

### 2.4 Async Client
#### ✅ CORRECT: Async publisher
```java
EventGridPublisherAsyncClient<EventGridEvent> asyncClient = new EventGridPublisherClientBuilder()
    .endpoint("<topic-endpoint>")
    .credential(new AzureKeyCredential("<access-key>"))
    .buildEventGridEventPublisherAsyncClient();
```

#### ❌ INCORRECT: Missing endpoint or credential
```java
EventGridPublisherClient<EventGridEvent> client = new EventGridPublisherClientBuilder()
    .buildEventGridEventPublisherClient();
```

---

## 3. Publishing EventGridEvent

### 3.1 Single Event
#### ✅ CORRECT: Full event creation
```java
EventGridEvent event = new EventGridEvent(
    "resource/path",           // subject
    "MyApp.Events.OrderCreated", // eventType
    BinaryData.fromObject(new OrderData("order-123", 99.99)), // data
    "1.0"                      // dataVersion
);

client.sendEvent(event);
```

#### ❌ INCORRECT: Missing required fields
```java
EventGridEvent event = new EventGridEvent(
    null,        // Missing subject
    "type",
    BinaryData.fromString("data"),
    "1.0"
);
```

### 3.2 Multiple Events
#### ✅ CORRECT: Batch publish
```java
List<EventGridEvent> events = Arrays.asList(
    new EventGridEvent("orders/1", "Order.Created", 
        BinaryData.fromObject(order1), "1.0"),
    new EventGridEvent("orders/2", "Order.Created", 
        BinaryData.fromObject(order2), "1.0")
);

client.sendEvents(events);
```

---

## 4. Publishing CloudEvent

### 4.1 Single CloudEvent
#### ✅ CORRECT: Full CloudEvent
```java
CloudEvent cloudEvent = new CloudEvent(
    "/myapp/orders",           // source
    "order.created",           // type
    BinaryData.fromObject(orderData), // data
    CloudEventDataFormat.JSON  // dataFormat
);
cloudEvent.setSubject("orders/12345");
cloudEvent.setId(UUID.randomUUID().toString());

cloudClient.sendEvent(cloudEvent);
```

### 4.2 CloudEvent Batch
#### ✅ CORRECT: Multiple CloudEvents
```java
List<CloudEvent> cloudEvents = Arrays.asList(
    new CloudEvent("/app", "event.type1", BinaryData.fromString("data1"), CloudEventDataFormat.JSON),
    new CloudEvent("/app", "event.type2", BinaryData.fromString("data2"), CloudEventDataFormat.JSON)
);

cloudClient.sendEvents(cloudEvents);
```

---

## 5. Async Publishing

### 5.1 Single Event Async
#### ✅ CORRECT: Reactive publish
```java
asyncClient.sendEvent(event)
    .subscribe(
        unused -> System.out.println("Event sent successfully"),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### 5.2 Batch Async with Block
#### ✅ CORRECT: Batch with error handling
```java
asyncClient.sendEvents(events)
    .doOnSuccess(unused -> System.out.println("All events sent"))
    .doOnError(error -> System.err.println("Failed: " + error))
    .block();
```

---

## 6. Custom Event Data

### 6.1 Data Class Definition
#### ✅ CORRECT: POJO for event data
```java
public class OrderData {
    private String orderId;
    private double amount;
    private String customerId;
    
    public OrderData(String orderId, double amount) {
        this.orderId = orderId;
        this.amount = amount;
    }
    
    // Getters and setters
}
```

### 6.2 Using Data Class
#### ✅ CORRECT: BinaryData.fromObject
```java
OrderData order = new OrderData("ORD-123", 150.00);
EventGridEvent event = new EventGridEvent(
    "orders/" + order.getOrderId(),
    "MyApp.Order.Created",
    BinaryData.fromObject(order),
    "1.0"
);
```

---

## 7. Receiving Events

### 7.1 Parse EventGridEvent
#### ✅ CORRECT: From JSON string
```java
String jsonPayload = "[{\"id\": \"...\", ...}]";
List<EventGridEvent> events = EventGridEvent.fromString(jsonPayload);

for (EventGridEvent event : events) {
    System.out.println("Event Type: " + event.getEventType());
    System.out.println("Subject: " + event.getSubject());
    System.out.println("Event Time: " + event.getEventTime());
    
    BinaryData data = event.getData();
    OrderData orderData = data.toObject(OrderData.class);
}
```

### 7.2 Parse CloudEvent
#### ✅ CORRECT: CloudEvent parsing
```java
String cloudEventJson = "[{\"specversion\": \"1.0\", ...}]";
List<CloudEvent> cloudEvents = CloudEvent.fromString(cloudEventJson);

for (CloudEvent event : cloudEvents) {
    System.out.println("Type: " + event.getType());
    System.out.println("Source: " + event.getSource());
    System.out.println("ID: " + event.getId());
    
    MyEventData data = event.getData().toObject(MyEventData.class);
}
```

### 7.3 Handle System Events
#### ✅ CORRECT: Azure system events
```java
import com.azure.messaging.eventgrid.systemevents.*;

for (EventGridEvent event : events) {
    if (event.getEventType().equals("Microsoft.Storage.BlobCreated")) {
        StorageBlobCreatedEventData blobData = 
            event.getData().toObject(StorageBlobCreatedEventData.class);
        System.out.println("Blob URL: " + blobData.getUrl());
    }
}
```

---

## 8. Event Grid Namespaces (Pull Model)

### 8.1 Receive from Namespace
#### ✅ CORRECT: Pull delivery
```java
import com.azure.messaging.eventgrid.namespaces.EventGridReceiverClient;
import com.azure.messaging.eventgrid.namespaces.EventGridReceiverClientBuilder;
import com.azure.messaging.eventgrid.namespaces.models.*;

EventGridReceiverClient receiverClient = new EventGridReceiverClientBuilder()
    .endpoint("<namespace-endpoint>")
    .credential(new AzureKeyCredential("<key>"))
    .topicName("my-topic")
    .subscriptionName("my-subscription")
    .buildClient();

ReceiveResult result = receiverClient.receive(10, Duration.ofSeconds(30));

for (ReceiveDetails detail : result.getValue()) {
    CloudEvent event = detail.getEvent();
    System.out.println("Event: " + event.getType());
    
    receiverClient.acknowledge(Arrays.asList(detail.getBrokerProperties().getLockToken()));
}
```

### 8.2 Reject or Release Events
#### ✅ CORRECT: Event disposition
```java
// Reject (don't retry)
receiverClient.reject(Arrays.asList(lockToken));

// Release (retry later)
receiverClient.release(Arrays.asList(lockToken));

// Release with delay
receiverClient.release(Arrays.asList(lockToken), 
    new ReleaseOptions().setDelay(ReleaseDelay.BY_60_SECONDS));
```

---

## 9. Error Handling

### 9.1 HTTP Response Exception
#### ✅ CORRECT: Specific error handling
```java
try {
    client.sendEvent(event);
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

#### ❌ INCORRECT: Catching generic exception
```java
try {
    client.sendEvent(event);
} catch (Exception e) {
    // Too broad
}
```

---

## 10. Required Dependencies

### 10.1 Maven Configuration
#### ✅ CORRECT: Current version
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-messaging-eventgrid</artifactId>
    <version>4.27.0</version>
</dependency>
```

---

## 11. Environment Variables

### 11.1 Required Variables
```bash
EVENT_GRID_TOPIC_ENDPOINT=https://<topic-name>.<region>.eventgrid.azure.net/api/events
EVENT_GRID_ACCESS_KEY=<your-access-key>
```

---

## 12. Best Practices

### 12.1 Event Publishing
- Batch events when possible for efficiency
- Include unique event IDs for deduplication
- Keep events under 1MB (64KB for basic tier)

### 12.2 Event Data
- Use strongly-typed event data classes
- Use `BinaryData.fromObject()` for automatic serialization
- Validate event schema before publishing

### 12.3 Event Handling
- Handle unknown event types gracefully
- Implement idempotent event handlers
- Consider dead-letter for persistent failures

### 12.4 Event Types
| Type | Description |
|------|-------------|
| `EventGridEvent` | Azure Event Grid native schema |
| `CloudEvent` | CNCF CloudEvents 1.0 specification |
| `BinaryData` | Custom schema events |
