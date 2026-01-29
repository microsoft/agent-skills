# Azure Event Grid SDK for Java - Examples

Comprehensive code examples for the Azure Event Grid SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Publishing CloudEvents](#publishing-cloudevents)
- [Publishing EventGridEvents](#publishing-eventgridevents)
- [Publishing Custom Events](#publishing-custom-events)
- [Async Client Patterns](#async-client-patterns)
- [Batch Publishing](#batch-publishing)
- [Error Handling](#error-handling)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-messaging-eventgrid</artifactId>
    <version>4.32.0-beta.1</version>
</dependency>

<!-- For DefaultAzureCredential authentication -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.18.2</version>
</dependency>
```

## Client Creation

### Sync Client with DefaultAzureCredential

```java
import com.azure.core.models.CloudEvent;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.messaging.eventgrid.EventGridPublisherClient;
import com.azure.messaging.eventgrid.EventGridPublisherClientBuilder;

EventGridPublisherClient<CloudEvent> cloudEventClient = new EventGridPublisherClientBuilder()
    .endpoint("<endpoint of your event grid topic/domain that accepts CloudEvent schema>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildCloudEventPublisherClient();
```

### Async Client with DefaultAzureCredential

```java
import com.azure.messaging.eventgrid.EventGridPublisherAsyncClient;

EventGridPublisherAsyncClient<CloudEvent> cloudEventAsyncClient = new EventGridPublisherClientBuilder()
    .endpoint("<endpoint of your event grid topic/domain that accepts CloudEvent schema>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildCloudEventPublisherAsyncClient();
```

### Client with AzureKeyCredential

```java
import com.azure.core.credential.AzureKeyCredential;

EventGridPublisherClient<CloudEvent> client = new EventGridPublisherClientBuilder()
    .endpoint(System.getenv("AZURE_EVENTGRID_CLOUDEVENT_ENDPOINT"))
    .credential(new AzureKeyCredential(System.getenv("AZURE_EVENTGRID_CLOUDEVENT_KEY")))
    .buildCloudEventPublisherClient();
```

## Publishing CloudEvents

```java
import com.azure.core.credential.AzureKeyCredential;
import com.azure.core.models.CloudEvent;
import com.azure.core.models.CloudEventDataFormat;
import com.azure.core.util.BinaryData;
import com.azure.messaging.eventgrid.EventGridPublisherClient;
import com.azure.messaging.eventgrid.EventGridPublisherClientBuilder;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class PublishCloudEventsToTopic {
    public static void main(String[] args) {
        EventGridPublisherClient<CloudEvent> publisherClient = new EventGridPublisherClientBuilder()
            .endpoint(System.getenv("AZURE_EVENTGRID_CLOUDEVENT_ENDPOINT"))
            .credential(new AzureKeyCredential(System.getenv("AZURE_EVENTGRID_CLOUDEVENT_KEY")))
            .buildCloudEventPublisherClient();

        // CloudEvent with String data
        String str = "FirstName: John1, LastName:James";
        CloudEvent cloudEventStr = new CloudEvent("https://com.example.myapp", "User.Created.Text",
            BinaryData.fromObject(str), CloudEventDataFormat.JSON, "text/plain");

        // CloudEvent with Object data
        User newUser = new User("John2", "James");
        CloudEvent cloudEventModel = new CloudEvent("https://com.example.myapp", "User.Created.Object",
            BinaryData.fromObject(newUser), CloudEventDataFormat.JSON, "application/json");
        
        // CloudEvent with bytes data
        byte[] byteSample = "FirstName: John3, LastName: James".getBytes(StandardCharsets.UTF_8);
        CloudEvent cloudEventBytes = new CloudEvent("https://com.example.myapp", "User.Created.Binary",
            BinaryData.fromBytes(byteSample), CloudEventDataFormat.BYTES, "application/octet-stream");

        // CloudEvent with extension attributes
        CloudEvent cloudEventWithExtension = cloudEventBytes.addExtensionAttribute("extension", "value");

        // Send batch
        List<CloudEvent> events = new ArrayList<>();
        events.add(cloudEventStr);
        events.add(cloudEventModel);
        events.add(cloudEventBytes);
        events.add(cloudEventWithExtension);
        
        publisherClient.sendEvents(events);
    }
}
```

## Publishing EventGridEvents

```java
import com.azure.core.credential.AzureKeyCredential;
import com.azure.core.util.BinaryData;
import com.azure.messaging.eventgrid.EventGridEvent;
import com.azure.messaging.eventgrid.EventGridPublisherClient;
import com.azure.messaging.eventgrid.EventGridPublisherClientBuilder;

import java.util.ArrayList;
import java.util.List;

public class PublishEventGridEventsToTopic {
    public static void main(String[] args) {
        EventGridPublisherClient<EventGridEvent> publisherClient = new EventGridPublisherClientBuilder()
            .endpoint(System.getenv("AZURE_EVENTGRID_EVENT_ENDPOINT"))
            .credential(new AzureKeyCredential(System.getenv("AZURE_EVENTGRID_EVENT_KEY")))
            .buildEventGridEventPublisherClient();

        // EventGridEvent with String data
        String str = "FirstName: John1, LastName: James";
        EventGridEvent eventJson = new EventGridEvent(
            "com/example/MyApp",           // subject
            "User.Created.Text",           // eventType
            BinaryData.fromObject(str),    // data
            "0.1"                          // dataVersion
        );
        
        // EventGridEvent with Object data
        User newUser = new User("John2", "James");
        EventGridEvent eventModelClass = new EventGridEvent(
            "com/example/MyApp",
            "User.Created.Object",
            BinaryData.fromObject(newUser),
            "0.1"
        );

        List<EventGridEvent> events = new ArrayList<>();
        events.add(eventJson);
        events.add(eventModelClass);

        publisherClient.sendEvents(events);
    }
}
```

## Publishing Custom Events

```java
import com.azure.core.credential.AzureKeyCredential;
import com.azure.core.util.BinaryData;
import com.azure.messaging.eventgrid.EventGridPublisherClient;
import com.azure.messaging.eventgrid.EventGridPublisherClientBuilder;

import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.UUID;

public class PublishCustomEvents {
    public static void main(String[] args) {
        // Create custom event publisher client
        EventGridPublisherClient<BinaryData> customEventClient = new EventGridPublisherClientBuilder()
            .endpoint("<endpoint of your event grid topic/domain that accepts custom event schema>")
            .credential(new AzureKeyCredential("<key for the endpoint>"))
            .buildCustomEventPublisherClient();

        // Build custom event as a map
        List<BinaryData> events = new ArrayList<>();
        events.add(BinaryData.fromObject(new HashMap<String, String>() {
            {
                put("id", UUID.randomUUID().toString());
                put("time", OffsetDateTime.now().toString());
                put("subject", "Test");
                put("foo", "bar");
                put("type", "Microsoft.MockPublisher.TestEvent");
                put("data", "example data");
                put("dataVersion", "0.1");
            }
        }));
        
        customEventClient.sendEvents(events);
    }
}
```

## Async Client Patterns

### Async CloudEvent Publishing

```java
import com.azure.core.credential.AzureKeyCredential;
import com.azure.core.models.CloudEvent;
import com.azure.core.models.CloudEventDataFormat;
import com.azure.core.util.BinaryData;
import com.azure.messaging.eventgrid.EventGridPublisherAsyncClient;
import com.azure.messaging.eventgrid.EventGridPublisherClientBuilder;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class PublishCloudEventsAsynchronously {
    public static void main(String[] args) throws Exception {
        EventGridPublisherAsyncClient<CloudEvent> publisherClient = new EventGridPublisherClientBuilder()
            .endpoint(System.getenv("AZURE_EVENTGRID_CLOUDEVENT_ENDPOINT"))
            .credential(new AzureKeyCredential(System.getenv("AZURE_EVENTGRID_CLOUDEVENT_KEY")))
            .buildCloudEventPublisherAsyncClient();

        // Create CloudEvents
        User newUser = new User("John2", "James");
        CloudEvent cloudEventModel = new CloudEvent("https://com.example.myapp", "User.Created.Object",
            BinaryData.fromObject(newUser), CloudEventDataFormat.JSON, "application/json");

        byte[] byteSample = "FirstName: John3, LastName: James".getBytes(StandardCharsets.UTF_8);
        CloudEvent cloudEventBytes = new CloudEvent("https://com.example.myapp", "User.Created.Binary",
            BinaryData.fromBytes(byteSample), CloudEventDataFormat.BYTES, "application/octet-stream");

        List<CloudEvent> events = new ArrayList<>();
        events.add(cloudEventModel);
        events.add(cloudEventBytes);

        // Non-blocking send with subscribe()
        publisherClient.sendEvents(events)
            .subscribe(
                unused -> System.out.println("Events sent successfully"),
                error -> System.err.println("Error sending events: " + error.getMessage()),
                () -> System.out.println("Send operation completed")
            );

        // Keep application alive for async operation
        Thread.sleep(5000);
    }
}
```

### Async EventGridEvent Publishing

```java
import com.azure.core.credential.AzureKeyCredential;
import com.azure.core.util.BinaryData;
import com.azure.messaging.eventgrid.EventGridEvent;
import com.azure.messaging.eventgrid.EventGridPublisherAsyncClient;
import com.azure.messaging.eventgrid.EventGridPublisherClientBuilder;

import java.util.ArrayList;
import java.util.List;

public class PublishEventGridEventsAsynchronously {
    public static void main(String[] args) throws Exception {
        EventGridPublisherAsyncClient<EventGridEvent> publisherClient = new EventGridPublisherClientBuilder()
            .endpoint(System.getenv("AZURE_EVENTGRID_EVENT_ENDPOINT"))
            .credential(new AzureKeyCredential(System.getenv("AZURE_EVENTGRID_EVENT_KEY")))
            .buildEventGridEventPublisherAsyncClient();

        String str = "FirstName: John1, LastName: James";
        EventGridEvent eventJson = new EventGridEvent("com/example/MyApp", "User.Created.Text", 
            BinaryData.fromObject(str), "0.1");
        
        User newUser = new User("John2", "James");
        EventGridEvent eventModelClass = new EventGridEvent("com/example/MyApp", "User.Created.Object", 
            BinaryData.fromObject(newUser), "0.1");

        List<EventGridEvent> events = new ArrayList<>();
        events.add(eventJson);
        events.add(eventModelClass);

        // Non-blocking send
        publisherClient.sendEvents(events)
            .subscribe();

        Thread.sleep(5000);
    }
}
```

## Batch Publishing

All `sendEvents()` methods accept a `List` and publish as a batch:

```java
// CloudEvents batch
List<CloudEvent> cloudEvents = new ArrayList<>();
cloudEvents.add(event1);
cloudEvents.add(event2);
cloudEvents.add(event3);
publisherClient.sendEvents(cloudEvents);

// EventGridEvents batch
List<EventGridEvent> gridEvents = new ArrayList<>();
gridEvents.add(gridEvent1);
gridEvents.add(gridEvent2);
publisherClient.sendEvents(gridEvents);

// Custom events batch
List<BinaryData> customEvents = new ArrayList<>();
customEvents.add(BinaryData.fromObject(customEvent1));
customEvents.add(BinaryData.fromObject(customEvent2));
customEventClient.sendEvents(customEvents);
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.models.CloudEvent;
import com.azure.messaging.eventgrid.EventGridPublisherClient;

public class EventGridErrorHandling {
    public static void main(String[] args) {
        EventGridPublisherClient<CloudEvent> client = /* create client */;
        
        try {
            client.sendEvents(events);
        } catch (HttpResponseException e) {
            System.err.println("HTTP Status Code: " + e.getResponse().getStatusCode());
            System.err.println("Error Message: " + e.getMessage());
            
            // Handle specific status codes
            int statusCode = e.getResponse().getStatusCode();
            if (statusCode == 401 || statusCode == 403) {
                System.err.println("Authentication/Authorization error");
            } else if (statusCode == 404) {
                System.err.println("Topic/Domain not found");
            } else if (statusCode >= 500) {
                System.err.println("Server error - consider retry");
            }
        } catch (Exception e) {
            System.err.println("Unexpected error: " + e.getMessage());
        }
    }
}
```

### Async Error Handling

```java
publisherClient.sendEvents(events)
    .subscribe(
        unused -> System.out.println("Success"),
        error -> {
            if (error instanceof HttpResponseException) {
                HttpResponseException httpError = (HttpResponseException) error;
                System.err.println("HTTP error: " + httpError.getResponse().getStatusCode());
            } else {
                System.err.println("Error: " + error.getMessage());
            }
        },
        () -> System.out.println("Completed")
    );
```

## Helper Class

```java
public class User {
    private String firstName;
    private String lastName;

    public User(String firstName, String lastName) {
        this.firstName = firstName;
        this.lastName = lastName;
    }

    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }
    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }
}
```
