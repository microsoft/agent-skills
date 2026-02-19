# Azure AI Anomaly Detector SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-anomalydetector`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/anomalydetector/azure-ai-anomalydetector
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Client Builder and Clients
```java
import com.azure.ai.anomalydetector.AnomalyDetectorClientBuilder;
import com.azure.ai.anomalydetector.MultivariateClient;
import com.azure.ai.anomalydetector.MultivariateAsyncClient;
import com.azure.ai.anomalydetector.UnivariateClient;
import com.azure.ai.anomalydetector.UnivariateAsyncClient;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Detection Models
```java
import com.azure.ai.anomalydetector.models.TimeSeriesPoint;
import com.azure.ai.anomalydetector.models.TimeGranularity;
import com.azure.ai.anomalydetector.models.UnivariateDetectionOptions;
import com.azure.ai.anomalydetector.models.UnivariateEntireDetectionResult;
import com.azure.ai.anomalydetector.models.UnivariateLastDetectionResult;
import com.azure.ai.anomalydetector.models.UnivariateChangePointDetectionOptions;
import com.azure.ai.anomalydetector.models.UnivariateChangePointDetectionResult;
```

#### ✅ CORRECT: Multivariate Models
```java
import com.azure.ai.anomalydetector.models.ModelInfo;
import com.azure.ai.anomalydetector.models.AnomalyDetectionModel;
import com.azure.ai.anomalydetector.models.MultivariateBatchDetectionOptions;
import com.azure.ai.anomalydetector.models.MultivariateDetectionResult;
import com.azure.ai.anomalydetector.models.MultivariateLastDetectionOptions;
import com.azure.ai.anomalydetector.models.MultivariateLastDetectionResult;
import com.azure.ai.anomalydetector.models.VariableValues;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```java
// WRONG - Using old package names
import com.azure.cognitiveservices.anomalydetector.AnomalyDetectorClient;

// WRONG - Models not in main package
import com.azure.ai.anomalydetector.TimeSeriesPoint;

// WRONG - Using non-existent classes
import com.azure.ai.anomalydetector.AnomalyDetectorClient;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder with API Key
```java
String endpoint = System.getenv("AZURE_ANOMALY_DETECTOR_ENDPOINT");
String key = System.getenv("AZURE_ANOMALY_DETECTOR_API_KEY");

UnivariateClient univariateClient = new AnomalyDetectorClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildUnivariateClient();

MultivariateClient multivariateClient = new AnomalyDetectorClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildMultivariateClient();
```

### 2.2 ✅ CORRECT: Builder with DefaultAzureCredential
```java
UnivariateClient client = new AnomalyDetectorClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildUnivariateClient();
```

### 2.3 ✅ CORRECT: Async Clients
```java
UnivariateAsyncClient asyncClient = new AnomalyDetectorClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildUnivariateAsyncClient();

MultivariateAsyncClient multivariateAsyncClient = new AnomalyDetectorClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildMultivariateAsyncClient();
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```java
// WRONG - hardcoded endpoint and key
UnivariateClient client = new AnomalyDetectorClientBuilder()
    .endpoint("https://myresource.cognitiveservices.azure.com")
    .credential(new AzureKeyCredential("hardcoded-key"))
    .buildUnivariateClient();
```

#### ❌ INCORRECT: Missing required parameters
```java
// WRONG - missing endpoint
UnivariateClient client = new AnomalyDetectorClientBuilder()
    .credential(new AzureKeyCredential(key))
    .buildUnivariateClient();
```

---

## 3. Univariate Detection Patterns

### 3.1 ✅ CORRECT: Batch Detection
```java
List<TimeSeriesPoint> series = List.of(
    new TimeSeriesPoint(OffsetDateTime.parse("2023-01-01T00:00:00Z"), 1.0),
    new TimeSeriesPoint(OffsetDateTime.parse("2023-01-02T00:00:00Z"), 2.5)
    // ... minimum 12 points required
);

UnivariateDetectionOptions options = new UnivariateDetectionOptions(series)
    .setGranularity(TimeGranularity.DAILY)
    .setSensitivity(95);

UnivariateEntireDetectionResult result = univariateClient.detectUnivariateEntireSeries(options);

for (int i = 0; i < result.getIsAnomaly().size(); i++) {
    if (result.getIsAnomaly().get(i)) {
        System.out.printf("Anomaly at index %d%n", i);
    }
}
```

### 3.2 ✅ CORRECT: Last Point Detection
```java
UnivariateLastDetectionResult result = univariateClient.detectUnivariateLastPoint(options);

if (result.isAnomaly()) {
    System.out.println("Latest point is an anomaly!");
}
```

### 3.3 ✅ CORRECT: Change Point Detection
```java
UnivariateChangePointDetectionOptions changeOptions = 
    new UnivariateChangePointDetectionOptions(series, TimeGranularity.DAILY);

UnivariateChangePointDetectionResult result = 
    univariateClient.detectUnivariateChangePoint(changeOptions);

for (int i = 0; i < result.getIsChangePoint().size(); i++) {
    if (result.getIsChangePoint().get(i)) {
        System.out.printf("Change point at index %d%n", i);
    }
}
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Insufficient data points
```java
// WRONG - less than 12 data points
List<TimeSeriesPoint> series = List.of(
    new TimeSeriesPoint(OffsetDateTime.now(), 1.0)
);
univariateClient.detectUnivariateEntireSeries(new UnivariateDetectionOptions(series));
```

---

## 4. Multivariate Detection Patterns

### 4.1 ✅ CORRECT: Train Model
```java
ModelInfo modelInfo = new ModelInfo()
    .setDataSource("https://storage.blob.core.windows.net/container/data.zip?sasToken")
    .setStartTime(OffsetDateTime.parse("2023-01-01T00:00:00Z"))
    .setEndTime(OffsetDateTime.parse("2023-06-01T00:00:00Z"))
    .setSlidingWindow(200)
    .setDisplayName("MyModel");

AnomalyDetectionModel model = multivariateClient.trainMultivariateModel(modelInfo);
String modelId = model.getModelId();
```

### 4.2 ✅ CORRECT: Batch Detection
```java
MultivariateBatchDetectionOptions detectionOptions = new MultivariateBatchDetectionOptions()
    .setDataSource("https://storage.blob.core.windows.net/container/inference.zip?sasToken")
    .setStartTime(OffsetDateTime.parse("2023-07-01T00:00:00Z"))
    .setEndTime(OffsetDateTime.parse("2023-07-31T00:00:00Z"))
    .setTopContributorCount(10);

MultivariateDetectionResult result = 
    multivariateClient.detectMultivariateBatchAnomaly(modelId, detectionOptions);
```

### 4.3 ✅ CORRECT: Last Point Detection
```java
MultivariateLastDetectionOptions lastOptions = new MultivariateLastDetectionOptions()
    .setVariables(List.of(
        new VariableValues("variable1", List.of("timestamp1"), List.of(1.0f)),
        new VariableValues("variable2", List.of("timestamp1"), List.of(2.5f))
    ))
    .setTopContributorCount(5);

MultivariateLastDetectionResult result = 
    multivariateClient.detectMultivariateLastAnomaly(modelId, lastOptions);
```

---

## 5. Error Handling

### 5.1 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    univariateClient.detectUnivariateEntireSeries(options);
} catch (HttpResponseException e) {
    System.err.println("HTTP Status: " + e.getResponse().getStatusCode());
    System.err.println("Error: " + e.getMessage());
}
```

### 5.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Empty catch blocks
```java
// WRONG - swallowing exceptions
try {
    univariateClient.detectUnivariateEntireSeries(options);
} catch (Exception e) {
    // Do nothing
}
```

---

## 6. Best Practices Checklist

- [ ] Use `DefaultAzureCredentialBuilder` for production authentication
- [ ] Use environment variables for endpoint and API key configuration
- [ ] Provide at least 12 data points for univariate detection
- [ ] Match `TimeGranularity` to actual data frequency
- [ ] Use async clients for high-concurrency scenarios
- [ ] Handle `HttpResponseException` appropriately
- [ ] Clean up multivariate models when no longer needed
