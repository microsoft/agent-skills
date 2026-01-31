# Azure AI Anomaly Detector SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-anomalydetector`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/anomalydetector/azure-ai-anomalydetector
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Azure SDK Client Imports
```java
import com.azure.ai.anomalydetector.AnomalyDetectorClientBuilder;
import com.azure.ai.anomalydetector.MultivariateClient;
import com.azure.ai.anomalydetector.UnivariateClient;
import com.azure.core.credential.AzureKeyCredential;
```

#### ❌ INCORRECT: Non-existent or Wrong Package
```java
import com.azure.anomalydetector.AnomalyDetectorClient;  // Wrong package path
import azure.ai.anomalydetector.Client;  // Wrong root package
```

### 1.2 Model Imports
#### ✅ CORRECT: Model Classes from Models Package
```java
import com.azure.ai.anomalydetector.models.TimeSeriesPoint;
import com.azure.ai.anomalydetector.models.UnivariateDetectionOptions;
import com.azure.ai.anomalydetector.models.UnivariateEntireDetectionResult;
import com.azure.ai.anomalydetector.models.TimeGranularity;
```

#### ❌ INCORRECT: Wrong Model Package
```java
import com.azure.ai.anomalydetector.TimeSeriesPoint;  // Missing models subpackage
```

---

## 2. Client Creation Patterns

### 2.1 Multivariate Client
#### ✅ CORRECT: Using AnomalyDetectorClientBuilder
```java
MultivariateClient multivariateClient = new AnomalyDetectorClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildMultivariateClient();
```

#### ❌ INCORRECT: Direct Instantiation
```java
MultivariateClient client = new MultivariateClient(endpoint, key);
```

### 2.2 Univariate Client
#### ✅ CORRECT: Using AnomalyDetectorClientBuilder
```java
UnivariateClient univariateClient = new AnomalyDetectorClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildUnivariateClient();
```

### 2.3 DefaultAzureCredential
#### ✅ CORRECT: Using DefaultAzureCredentialBuilder
```java
import com.azure.identity.DefaultAzureCredentialBuilder;

MultivariateClient client = new AnomalyDetectorClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildMultivariateClient();
```

#### ❌ INCORRECT: Direct DefaultAzureCredential
```java
MultivariateClient client = new AnomalyDetectorClientBuilder()
    .credential(new DefaultAzureCredential())  // Must use builder
    .endpoint(endpoint)
    .buildMultivariateClient();
```

---

## 3. Univariate Detection Patterns

### 3.1 Batch Detection
#### ✅ CORRECT: UnivariateDetectionOptions with Series
```java
List<TimeSeriesPoint> series = List.of(
    new TimeSeriesPoint(OffsetDateTime.parse("2023-01-01T00:00:00Z"), 1.0),
    new TimeSeriesPoint(OffsetDateTime.parse("2023-01-02T00:00:00Z"), 2.5)
);

UnivariateDetectionOptions options = new UnivariateDetectionOptions(series)
    .setGranularity(TimeGranularity.DAILY)
    .setSensitivity(95);

UnivariateEntireDetectionResult result = univariateClient.detectUnivariateEntireSeries(options);
```

#### ❌ INCORRECT: Wrong Method Name or Parameters
```java
univariateClient.detectEntireSeries(series);  // Wrong method name
univariateClient.detectUnivariateEntireSeries(series);  // Missing options wrapper
```

### 3.2 Last Point Detection
#### ✅ CORRECT: Streaming Detection
```java
UnivariateLastDetectionResult result = univariateClient.detectUnivariateLastPoint(options);

if (result.isAnomaly()) {
    System.out.println("Anomaly detected!");
}
```

### 3.3 Change Point Detection
#### ✅ CORRECT: Using UnivariateChangePointDetectionOptions
```java
UnivariateChangePointDetectionOptions changeOptions = 
    new UnivariateChangePointDetectionOptions(series, TimeGranularity.DAILY);

UnivariateChangePointDetectionResult result = 
    univariateClient.detectUnivariateChangePoint(changeOptions);
```

---

## 4. Multivariate Detection Patterns

### 4.1 Model Training
#### ✅ CORRECT: ModelInfo Configuration
```java
ModelInfo modelInfo = new ModelInfo()
    .setDataSource("https://storage.blob.core.windows.net/container/data.zip?sasToken")
    .setStartTime(OffsetDateTime.parse("2023-01-01T00:00:00Z"))
    .setEndTime(OffsetDateTime.parse("2023-06-01T00:00:00Z"))
    .setSlidingWindow(200)
    .setDisplayName("MyModel");

AnomalyDetectionModel trainedModel = multivariateClient.trainMultivariateModel(modelInfo);
```

### 4.2 Batch Inference
#### ✅ CORRECT: MultivariateBatchDetectionOptions
```java
MultivariateBatchDetectionOptions options = new MultivariateBatchDetectionOptions()
    .setDataSource("https://storage.blob.core.windows.net/data.zip?sas")
    .setStartTime(OffsetDateTime.parse("2023-07-01T00:00:00Z"))
    .setEndTime(OffsetDateTime.parse("2023-07-31T00:00:00Z"))
    .setTopContributorCount(10);

MultivariateDetectionResult result = 
    multivariateClient.detectMultivariateBatchAnomaly(modelId, options);
```

### 4.3 Last Point Detection (Multivariate)
#### ✅ CORRECT: MultivariateLastDetectionOptions
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

## 5. Model Management Patterns

### 5.1 List Models
#### ✅ CORRECT: PagedIterable
```java
PagedIterable<AnomalyDetectionModel> models = multivariateClient.listMultivariateModels();
for (AnomalyDetectionModel model : models) {
    System.out.println("Model: " + model.getModelId());
}
```

### 5.2 Delete Model
#### ✅ CORRECT: Delete by Model ID
```java
multivariateClient.deleteMultivariateModel(modelId);
```

---

## 6. Error Handling

### 6.1 HttpResponseException
#### ✅ CORRECT: Azure SDK Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    univariateClient.detectUnivariateEntireSeries(options);
} catch (HttpResponseException e) {
    System.out.println("Status code: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

#### ❌ INCORRECT: Generic Exception Only
```java
try {
    univariateClient.detectUnivariateEntireSeries(options);
} catch (Exception e) {
    // Missing specific HttpResponseException handling
}
```

---

## 7. Environment Configuration

### 7.1 Environment Variables
#### ✅ CORRECT: Reading from Environment
```java
String endpoint = System.getenv("AZURE_ANOMALY_DETECTOR_ENDPOINT");
String key = System.getenv("AZURE_ANOMALY_DETECTOR_API_KEY");
```

#### ❌ INCORRECT: Hardcoded Credentials
```java
String endpoint = "https://myresource.cognitiveservices.azure.com/";
String key = "abc123secretkey";  // Never hardcode credentials
```

---

## 8. Data Requirements

### 8.1 Minimum Data Points
- Univariate detection requires at least 12 data points
- More data points improve accuracy

### 8.2 Granularity Alignment
- `TimeGranularity` must match actual data frequency
- Available: YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, PER_MINUTE, PER_SECOND, MICROSECOND, NONE

### 8.3 Sensitivity Values
- Range: 0-99
- Higher values detect more anomalies
- Typical: 95 for strict detection
