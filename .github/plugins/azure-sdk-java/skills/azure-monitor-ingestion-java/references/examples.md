# Azure Monitor Ingestion SDK for Java - Examples

Comprehensive code examples for the Azure Monitor Ingestion SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Uploading Logs](#uploading-logs)
- [Batching with Concurrency](#batching-with-concurrency)
- [Error Handling](#error-handling)
- [Async Client Patterns](#async-client-patterns)

## Maven Dependency

```xml
<!-- Using Azure SDK BOM (recommended) -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-sdk-bom</artifactId>
            <version>1.2.29</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-monitor-ingestion</artifactId>
    </dependency>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-identity</artifactId>
    </dependency>
</dependencies>

<!-- Or direct dependencies -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-ingestion</artifactId>
    <version>1.2.14</version>
</dependency>
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.15.3</version>
</dependency>
```

## Client Creation

### Synchronous Client

```java
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.monitor.ingestion.LogsIngestionClient;
import com.azure.monitor.ingestion.LogsIngestionClientBuilder;

DefaultAzureCredential credential = new DefaultAzureCredentialBuilder().build();

LogsIngestionClient client = new LogsIngestionClientBuilder()
    .endpoint("<data-collection-endpoint>")  // e.g., "https://my-dce.eastus-1.ingest.monitor.azure.com"
    .credential(credential)
    .buildClient();
```

### Asynchronous Client

```java
import com.azure.monitor.ingestion.LogsIngestionAsyncClient;

LogsIngestionAsyncClient asyncClient = new LogsIngestionClientBuilder()
    .endpoint("<data-collection-endpoint>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

## Uploading Logs

### Basic Upload

```java
import com.azure.monitor.ingestion.LogsIngestionClient;
import com.azure.monitor.ingestion.models.LogsUploadException;
import java.time.OffsetDateTime;
import java.util.Arrays;
import java.util.List;

List<Object> logs = Arrays.asList(
    new Object() {
        OffsetDateTime time = OffsetDateTime.now();
        String computer = "Computer1";
        String message = "Application started";
        int level = 1;
    },
    new Object() {
        OffsetDateTime time = OffsetDateTime.now();
        String computer = "Computer2";
        String message = "Connection established";
        int level = 2;
    }
);

try {
    client.upload(
        "dcr-00000000000000000000000000000000",  // DCR immutable ID
        "Custom-MyTableRawData",                  // Stream name from DCR
        logs
    );
    System.out.println("Logs uploaded successfully");
} catch (LogsUploadException e) {
    System.out.println("Failed to upload logs");
    e.getLogsUploadErrors().forEach(error -> 
        System.out.println(error.getMessage()));
}
```

### Using POJO Classes

```java
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;

// Define log entry class
class CustomLogEntry {
    private OffsetDateTime timeGenerated;
    private String computer;
    private String message;
    private int severity;

    public CustomLogEntry(OffsetDateTime timeGenerated, String computer, 
                          String message, int severity) {
        this.timeGenerated = timeGenerated;
        this.computer = computer;
        this.message = message;
        this.severity = severity;
    }

    // Getters required for JSON serialization
    public OffsetDateTime getTimeGenerated() { return timeGenerated; }
    public String getComputer() { return computer; }
    public String getMessage() { return message; }
    public int getSeverity() { return severity; }
}

// Create and upload logs
List<Object> logs = new ArrayList<>();
logs.add(new CustomLogEntry(OffsetDateTime.now(), "Server1", "Started", 1));
logs.add(new CustomLogEntry(OffsetDateTime.now(), "Server2", "Connected", 2));

client.upload("<dcr-id>", "<stream-name>", logs);
```

## Batching with Concurrency

When uploading large collections, the SDK automatically splits them into batches:

```java
import com.azure.core.util.Context;
import com.azure.monitor.ingestion.models.LogsUploadOptions;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;

// Generate large batch
List<Object> logs = new ArrayList<>();
for (int i = 0; i < 100000; i++) {
    final int index = i;
    logs.add(new Object() {
        OffsetDateTime time = OffsetDateTime.now();
        String computer = "Computer" + (index % 10);
        String message = "Log entry " + index;
        int level = index % 5;
    });
}

// Configure concurrency
LogsUploadOptions options = new LogsUploadOptions()
    .setMaxConcurrency(3);  // Up to 3 concurrent batch uploads

client.upload("<dcr-id>", "<stream-name>", logs, options, Context.NONE);
```

## Error Handling

### Error Consumer for Partial Failures

```java
import com.azure.core.util.Context;
import com.azure.monitor.ingestion.models.LogsUploadOptions;

LogsUploadOptions options = new LogsUploadOptions()
    .setLogsUploadErrorConsumer(error -> {
        // Log error details
        System.out.println("Error: " + error.getResponseException().getMessage());
        System.out.println("Failed logs: " + error.getFailedLogs().size());
        
        // Access failed logs for retry
        error.getFailedLogs().forEach(log -> 
            System.out.println("Failed: " + log));

        // Option 1: Continue with remaining logs (default)
        // Just return

        // Option 2: Abort remaining uploads
        // throw error.getResponseException();
    });

client.upload("<dcr-id>", "<stream-name>", logs, options, Context.NONE);
```

### Catching LogsUploadException

```java
import com.azure.monitor.ingestion.models.LogsUploadException;

try {
    client.upload("<dcr-id>", "<stream-name>", logs);
    System.out.println("All logs uploaded");
} catch (LogsUploadException e) {
    System.out.println("Some logs failed");
    e.getLogsUploadErrors().forEach(error -> {
        System.out.println("Error: " + error.getMessage());
        System.out.println("Status: " + 
            error.getResponseException().getResponse().getStatusCode());
    });
}
```

## Async Client Patterns

### Basic Async Upload

```java
import java.util.concurrent.CountDownLatch;

CountDownLatch latch = new CountDownLatch(1);

asyncClient.upload("<dcr-id>", "<stream-name>", logs)
    .doOnSuccess(unused -> System.out.println("Uploaded successfully"))
    .doOnError(error -> System.err.println("Failed: " + error.getMessage()))
    .doFinally(signal -> latch.countDown())
    .subscribe();

latch.await();
```

### Async with Options

```java
import com.azure.monitor.ingestion.models.LogsUploadOptions;

LogsUploadOptions options = new LogsUploadOptions()
    .setMaxConcurrency(3)
    .setLogsUploadErrorConsumer(error -> {
        System.out.println("Partial failure: " + error.getFailedLogs().size());
    });

asyncClient.upload("<dcr-id>", "<stream-name>", logs, options)
    .subscribe(
        unused -> System.out.println("Success"),
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Completed")
    );
```

### Chaining Operations

```java
import reactor.core.publisher.Mono;

Mono.just(generateLogs())
    .flatMap(logs -> asyncClient.upload("<dcr-id>", "<stream-name>", logs))
    .doOnSuccess(unused -> System.out.println("Upload complete"))
    .doOnError(error -> System.err.println("Upload failed: " + error))
    .subscribe();
```
