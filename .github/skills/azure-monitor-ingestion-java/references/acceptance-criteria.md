# Azure Monitor Ingestion SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-monitor-ingestion`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/monitor/azure-monitor-ingestion
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: LogsIngestionClient Imports
```java
import com.azure.monitor.ingestion.LogsIngestionClient;
import com.azure.monitor.ingestion.LogsIngestionClientBuilder;
import com.azure.monitor.ingestion.LogsIngestionAsyncClient;
```
#### ❌ INCORRECT: Wrong Package or Class Names
```java
import com.azure.monitor.LogsIngestionClient;  // Wrong package
import com.azure.monitor.ingestion.IngestionClient;  // Wrong class name
import com.azure.monitor.ingestion.MonitorIngestionClient;  // Wrong name
```

### 1.2 Model Imports
#### ✅ CORRECT: Options Import
```java
import com.azure.monitor.ingestion.models.LogsUploadOptions;
```
#### ❌ INCORRECT: Non-existent Classes
```java
import com.azure.monitor.ingestion.models.UploadOptions;  // Wrong name
import com.azure.monitor.ingestion.models.LogsIngestionOptions;  // Doesn't exist
```

### 1.3 Credential and Core Imports
#### ✅ CORRECT: Azure Identity and Context
```java
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.util.Context;
```
#### ❌ INCORRECT: Wrong Credential Import
```java
import com.azure.identity.DefaultCredential;  // Wrong class
```

---

## 2. Client Creation Patterns

### 2.1 Synchronous Client with DefaultAzureCredential
#### ✅ CORRECT: Using Endpoint and Credential
```java
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder().build();

LogsIngestionClient client = new LogsIngestionClientBuilder()
    .endpoint("<data-collection-endpoint>")
    .credential(credential)
    .buildClient();
```
#### ❌ INCORRECT: Missing Endpoint or Wrong Method
```java
LogsIngestionClient client = new LogsIngestionClientBuilder()
    .credential(credential)
    .buildClient();  // Missing endpoint

LogsIngestionClient client = new LogsIngestionClientBuilder()
    .dataCollectionEndpoint("<endpoint>")  // Wrong method name
    .credential(credential)
    .buildClient();
```

### 2.2 Asynchronous Client
#### ✅ CORRECT: Building Async Client
```java
LogsIngestionAsyncClient asyncClient = new LogsIngestionClientBuilder()
    .endpoint("<data-collection-endpoint>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```
#### ❌ INCORRECT: Wrong Build Method
```java
LogsIngestionAsyncClient asyncClient = new LogsIngestionClientBuilder()
    .endpoint("<endpoint>")
    .credential(credential)
    .buildClient();  // Returns sync client
```

---

## 3. Core Upload Operations

### 3.1 Basic Upload
#### ✅ CORRECT: Upload with Rule ID and Stream Name
```java
List<Object> logs = new ArrayList<>();
logs.add(new MyLogEntry("2024-01-15T10:30:00Z", "INFO", "Application started"));
logs.add(new MyLogEntry("2024-01-15T10:30:05Z", "DEBUG", "Processing request"));

client.upload("<data-collection-rule-id>", "<stream-name>", logs);
```
#### ❌ INCORRECT: Wrong Parameter Order or Types
```java
client.upload(logs, "<rule-id>", "<stream-name>");  // Wrong order
client.upload("<rule-id>", logs);  // Missing stream name
```

### 3.2 Upload with Concurrency Options
#### ✅ CORRECT: Using LogsUploadOptions
```java
List<Object> logs = getLargeLogs();

LogsUploadOptions options = new LogsUploadOptions()
    .setMaxConcurrency(3);

client.upload("<data-collection-rule-id>", "<stream-name>", logs, options, Context.NONE);
```
#### ❌ INCORRECT: Wrong Options Type or Missing Context
```java
client.upload("<rule-id>", "<stream-name>", logs, options);  // Missing Context
client.upload("<rule-id>", "<stream-name>", logs, 3, Context.NONE);  // Int instead of options
```

### 3.3 Upload with Error Consumer
#### ✅ CORRECT: Handling Partial Failures
```java
LogsUploadOptions options = new LogsUploadOptions()
    .setLogsUploadErrorConsumer(uploadError -> {
        System.err.println("Upload error: " + uploadError.getResponseException().getMessage());
        System.err.println("Failed logs count: " + uploadError.getFailedLogs().size());
    });

client.upload("<data-collection-rule-id>", "<stream-name>", logs, options, Context.NONE);
```
#### ❌ INCORRECT: Wrong Error Handler Signature
```java
LogsUploadOptions options = new LogsUploadOptions()
    .setErrorHandler(error -> { });  // Wrong method name

LogsUploadOptions options = new LogsUploadOptions()
    .setLogsUploadErrorConsumer((error, logs) -> { });  // Wrong signature
```

---

## 4. Async Upload Operations

### 4.1 Basic Async Upload
#### ✅ CORRECT: Reactive Upload Pattern
```java
List<Object> logs = getLogs();

asyncClient.upload("<data-collection-rule-id>", "<stream-name>", logs)
    .doOnSuccess(v -> System.out.println("Upload completed"))
    .doOnError(e -> System.err.println("Upload failed: " + e.getMessage()))
    .subscribe();
```
#### ❌ INCORRECT: Blocking on Async Client
```java
asyncClient.upload("<rule-id>", "<stream-name>", logs).block();  // Avoid blocking
```

### 4.2 Async Upload with Options
#### ✅ CORRECT: Using Options in Async
```java
LogsUploadOptions options = new LogsUploadOptions().setMaxConcurrency(5);

asyncClient.upload("<rule-id>", "<stream-name>", logs, options)
    .subscribe();
```

---

## 5. Log Entry Model

### 5.1 Custom Log Entry Class
#### ✅ CORRECT: POJO with Getters for Serialization
```java
public class MyLogEntry {
    private String timeGenerated;
    private String level;
    private String message;
    
    public MyLogEntry(String timeGenerated, String level, String message) {
        this.timeGenerated = timeGenerated;
        this.level = level;
        this.message = message;
    }
    
    // Getters required for JSON serialization
    public String getTimeGenerated() { return timeGenerated; }
    public String getLevel() { return level; }
    public String getMessage() { return message; }
}
```
#### ❌ INCORRECT: Missing Getters or Using Map Incorrectly
```java
public class MyLogEntry {
    public String timeGenerated;  // Public fields work but not recommended
    // Missing getters - may not serialize properly
}
```

### 5.2 Using Maps for Log Entries
#### ✅ CORRECT: Map-based Log Entry
```java
List<Object> logs = new ArrayList<>();
Map<String, Object> entry = new HashMap<>();
entry.put("TimeGenerated", "2024-01-15T10:30:00Z");
entry.put("Level", "INFO");
entry.put("Message", "Application started");
logs.add(entry);

client.upload(ruleId, streamName, logs);
```

---

## 6. Error Handling

### 6.1 HTTP Exception Handling
#### ✅ CORRECT: Catching HttpResponseException
```java
import com.azure.core.exception.HttpResponseException;

try {
    client.upload(ruleId, streamName, logs);
} catch (HttpResponseException e) {
    System.err.println("HTTP Status: " + e.getResponse().getStatusCode());
    System.err.println("Error: " + e.getMessage());
    
    if (e.getResponse().getStatusCode() == 403) {
        System.err.println("Check DCR permissions and managed identity");
    } else if (e.getResponse().getStatusCode() == 404) {
        System.err.println("Verify DCE endpoint and DCR ID");
    }
}
```
#### ❌ INCORRECT: Generic Exception Only
```java
try {
    client.upload(ruleId, streamName, logs);
} catch (Exception e) {
    System.out.println("Error occurred");  // No specific handling
}
```

### 6.2 Partial Failure Handling
#### ✅ CORRECT: Using Error Consumer for Partial Failures
```java
LogsUploadOptions options = new LogsUploadOptions()
    .setLogsUploadErrorConsumer(uploadError -> {
        // Log failed entries
        for (Object failedLog : uploadError.getFailedLogs()) {
            System.err.println("Failed to upload: " + failedLog);
        }
        
        // Option to throw and abort
        // throw uploadError.getResponseException();
    });
```

---

## 7. Environment Configuration

### 7.1 Required Environment Variables
#### ✅ CORRECT: Standard Variable Names
```java
String endpoint = System.getenv("DATA_COLLECTION_ENDPOINT");
String ruleId = System.getenv("DATA_COLLECTION_RULE_ID");
String streamName = System.getenv("STREAM_NAME");

LogsIngestionClient client = new LogsIngestionClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

---

## 8. Batch Processing Patterns

### 8.1 Batching Large Uploads
#### ✅ CORRECT: Using Concurrency for Large Collections
```java
List<Object> largeLogs = generateLargeLogs(10000);

LogsUploadOptions options = new LogsUploadOptions()
    .setMaxConcurrency(5)  // Process up to 5 batches concurrently
    .setLogsUploadErrorConsumer(error -> {
        System.err.println("Batch failed: " + error.getFailedLogs().size() + " logs");
    });

client.upload(ruleId, streamName, largeLogs, options, Context.NONE);
```
#### ❌ INCORRECT: Not Using Batching for Large Collections
```java
// Uploading one at a time - inefficient
for (Object log : largeLogs) {
    client.upload(ruleId, streamName, List.of(log));  // Don't do this
}
```

---

## 9. Data Collection Rule Concepts

### 9.1 Stream Name Format
#### ✅ CORRECT: Custom Table Stream Names
```java
// Custom tables use "Custom-" prefix
String customStream = "Custom-MyTable_CL";

// Built-in tables use their standard names
String syslogStream = "Microsoft-Syslog";
String securityStream = "Microsoft-SecurityEvent";

client.upload(ruleId, customStream, logs);
```
#### ❌ INCORRECT: Wrong Stream Name Format
```java
String stream = "MyTable_CL";  // Missing Custom- prefix for custom tables
String stream = "custom-MyTable";  // Wrong case and suffix
```

---

## 10. Client Reuse Patterns

### 10.1 Singleton Client Pattern
#### ✅ CORRECT: Reuse Client Instance
```java
public class LogIngestionService {
    private final LogsIngestionClient client;
    
    public LogIngestionService(String endpoint) {
        this.client = new LogsIngestionClientBuilder()
            .endpoint(endpoint)
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildClient();
    }
    
    public void uploadLogs(String ruleId, String stream, List<Object> logs) {
        client.upload(ruleId, stream, logs);
    }
}
```
#### ❌ INCORRECT: Creating New Client Per Request
```java
public void uploadLogs(List<Object> logs) {
    // Don't create client every time
    LogsIngestionClient client = new LogsIngestionClientBuilder()
        .endpoint(endpoint)
        .credential(new DefaultAzureCredentialBuilder().build())
        .buildClient();
    
    client.upload(ruleId, stream, logs);
}
```
