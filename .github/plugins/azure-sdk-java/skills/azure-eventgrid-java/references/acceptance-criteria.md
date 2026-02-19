# Azure Event Grid SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-messaging-eventgrid`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/eventgrid/azure-messaging-eventgrid
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Publisher Clients
```java
import com.azure.messaging.eventgrid.EventGridPublisherClient;
import com.azure.messaging.eventgrid.EventGridPublisherClientBuilder;
import com.azure.messaging.eventgrid.EventGridPublisherAsyncClient;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Event Models
```java
import com.azure.messaging.eventgrid.EventGridEvent;
import com.azure.core.models.CloudEvent;
import com.azure.core.models.CloudEventDataFormat;
import com.azure.core.util.BinaryData;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: EventGridEvent Publisher
```java
String endpoint = System.getenv("EVENT_GRID_TOPIC_ENDPOINT");
String key = System.getenv("EVENT_GRID_ACCESS_KEY");

EventGridPublisherClient<EventGridEvent> client = new EventGridPublisherClientBuilder()
    .endpoint(endpoint)
    .credential(new AzureKeyCredential(key))
    .buildEventGridEventPublisherClient();
```

### 2.2 ✅ CORRECT: CloudEvent Publisher
```java
EventGridPublisherClient<CloudEvent> cloudClient = new EventGridPublisherClientBuilder()
    .endpoint(endpoint)
    .credential(new AzureKeyCredential(key))
    .buildCloudEventPublisherClient();
```

### 2.3 ✅ CORRECT: With DefaultAzureCredential
```java
EventGridPublisherClient<EventGridEvent> client = new EventGridPublisherClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildEventGridEventPublisherClient();
```

---

## 3. Publish Events

### 3.1 ✅ CORRECT: Publish EventGridEvent
```java
EventGridEvent event = new EventGridEvent(
    "resource/path",
    "MyApp.Events.OrderCreated",
    BinaryData.fromObject(new OrderData("order-123", 99.99)),
    "1.0"
);

client.sendEvent(event);
```

### 3.2 ✅ CORRECT: Publish Multiple Events
```java
List<EventGridEvent> events = Arrays.asList(
    new EventGridEvent("orders/1", "Order.Created", BinaryData.fromObject(order1), "1.0"),
    new EventGridEvent("orders/2", "Order.Created", BinaryData.fromObject(order2), "1.0")
);

client.sendEvents(events);
```

### 3.3 ✅ CORRECT: Publish CloudEvent
```java
CloudEvent cloudEvent = new CloudEvent(
    "/myapp/orders",
    "order.created",
    BinaryData.fromObject(orderData),
    CloudEventDataFormat.JSON
);
cloudEvent.setSubject("orders/12345");

cloudClient.sendEvent(cloudEvent);
```

---

## 4. Parse Events

### 4.1 ✅ CORRECT: Parse EventGridEvent
```java
String jsonPayload = "[{\"id\": \"...\", ...}]";
List<EventGridEvent> events = EventGridEvent.fromString(jsonPayload);

for (EventGridEvent event : events) {
    System.out.println("Event Type: " + event.getEventType());
    OrderData data = event.getData().toObject(OrderData.class);
}
```

### 4.2 ✅ CORRECT: Parse CloudEvent
```java
List<CloudEvent> cloudEvents = CloudEvent.fromString(cloudEventJson);

for (CloudEvent event : cloudEvents) {
    System.out.println("Type: " + event.getType());
    MyEventData data = event.getData().toObject(MyEventData.class);
}
```

---

## 5. Error Handling

### 5.1 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.sendEvent(event);
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

---

## 6. Best Practices Checklist

- [ ] Use environment variables for endpoint and key
- [ ] Batch events when possible with `sendEvents`
- [ ] Include unique event IDs for deduplication
- [ ] Use strongly-typed event data classes
- [ ] Keep events under 1MB (64KB for basic tier)
