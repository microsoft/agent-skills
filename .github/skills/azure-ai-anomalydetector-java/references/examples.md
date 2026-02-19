# Azure AI Anomaly Detector Java SDK - Examples

Comprehensive code examples for the Azure AI Anomaly Detector SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Univariate Detection](#univariate-detection)
- [Univariate Streaming Detection](#univariate-streaming-detection)
- [Change Point Detection](#change-point-detection)
- [Multivariate Model Training](#multivariate-model-training)
- [Multivariate Batch Inference](#multivariate-batch-inference)
- [Multivariate Last Point Detection](#multivariate-last-point-detection)
- [Model Management](#model-management)
- [Error Handling](#error-handling)
- [Complete Application Example](#complete-application-example)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-anomalydetector</artifactId>
    <version>3.0.0-beta.6</version>
</dependency>

<!-- For DefaultAzureCredential -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.14.2</version>
</dependency>
```

## Client Creation

### With API Key

```java
import com.azure.ai.anomalydetector.AnomalyDetectorClientBuilder;
import com.azure.ai.anomalydetector.MultivariateClient;
import com.azure.ai.anomalydetector.UnivariateClient;
import com.azure.core.credential.AzureKeyCredential;

String endpoint = System.getenv("AZURE_ANOMALY_DETECTOR_ENDPOINT");
String key = System.getenv("AZURE_ANOMALY_DETECTOR_API_KEY");

// Univariate client for single variable analysis
UnivariateClient univariateClient = new AnomalyDetectorClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildUnivariateClient();

// Multivariate client for multiple correlated signals
MultivariateClient multivariateClient = new AnomalyDetectorClientBuilder()
    .credential(new AzureKeyCredential(key))
    .endpoint(endpoint)
    .buildMultivariateClient();
```

### With DefaultAzureCredential (Recommended)

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

UnivariateClient univariateClient = new AnomalyDetectorClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildUnivariateClient();

MultivariateClient multivariateClient = new AnomalyDetectorClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildMultivariateClient();
```

### Async Clients

```java
import com.azure.ai.anomalydetector.UnivariateAsyncClient;
import com.azure.ai.anomalydetector.MultivariateAsyncClient;

UnivariateAsyncClient univariateAsyncClient = new AnomalyDetectorClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildUnivariateAsyncClient();

MultivariateAsyncClient multivariateAsyncClient = new AnomalyDetectorClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint(endpoint)
    .buildMultivariateAsyncClient();
```

## Univariate Detection

### Batch Detection (Entire Series)

Detect anomalies across an entire time series at once.

```java
import com.azure.ai.anomalydetector.models.*;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;

// Prepare time series data (minimum 12 points required)
List<TimeSeriesPoint> series = new ArrayList<>();
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-01T00:00:00Z"), 826.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-02T00:00:00Z"), 799.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-03T00:00:00Z"), 890.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-04T00:00:00Z"), 900.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-05T00:00:00Z"), 961.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-06T00:00:00Z"), 935.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-07T00:00:00Z"), 894.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-08T00:00:00Z"), 855.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-09T00:00:00Z"), 809.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-10T00:00:00Z"), 810.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-11T00:00:00Z"), 766.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-12T00:00:00Z"), 805.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-13T00:00:00Z"), 821.0));
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-14T00:00:00Z"), 2000.0)); // Anomaly!
series.add(new TimeSeriesPoint(OffsetDateTime.parse("2023-01-15T00:00:00Z"), 888.0));

// Configure detection options
UnivariateDetectionOptions options = new UnivariateDetectionOptions(series)
    .setGranularity(TimeGranularity.DAILY)
    .setSensitivity(95);  // Higher = more sensitive (0-99)

// Detect anomalies
UnivariateEntireDetectionResult result = univariateClient.detectUnivariateEntireSeries(options);

// Process results
System.out.println("=== Anomaly Detection Results ===");
System.out.println("Period: " + result.getPeriod());

for (int i = 0; i < result.getIsAnomaly().size(); i++) {
    if (result.getIsAnomaly().get(i)) {
        TimeSeriesPoint point = series.get(i);
        System.out.printf("ANOMALY at %s: value=%.2f, expected=%.2f, upper=%.2f, lower=%.2f%n",
            point.getTimestamp(),
            point.getValue(),
            result.getExpectedValues().get(i),
            result.getUpperMargins().get(i),
            result.getLowerMargins().get(i));
    }
}

// Check positive/negative anomalies
for (int i = 0; i < result.getIsPositiveAnomaly().size(); i++) {
    if (result.getIsPositiveAnomaly().get(i)) {
        System.out.printf("Positive anomaly (spike) at index %d%n", i);
    }
    if (result.getIsNegativeAnomaly().get(i)) {
        System.out.printf("Negative anomaly (dip) at index %d%n", i);
    }
}
```

### Custom Period and Sensitivity

```java
UnivariateDetectionOptions options = new UnivariateDetectionOptions(series)
    .setGranularity(TimeGranularity.HOURLY)
    .setCustomInterval(4)           // Custom interval for non-standard granularity
    .setSensitivity(85)             // Lower sensitivity = fewer anomalies
    .setImputeMode(ImputeMode.AUTO) // Handle missing values
    .setImputeFixedValue(0.0);      // Fixed value for imputation (if FIXED mode)

UnivariateEntireDetectionResult result = univariateClient.detectUnivariateEntireSeries(options);
```

## Univariate Streaming Detection

### Last Point Detection (Real-time)

Detect if the most recent data point is an anomaly.

```java
// Add your latest data point to the series
series.add(new TimeSeriesPoint(OffsetDateTime.now(), 1500.0));

UnivariateDetectionOptions options = new UnivariateDetectionOptions(series)
    .setGranularity(TimeGranularity.DAILY)
    .setSensitivity(95);

UnivariateLastDetectionResult result = univariateClient.detectUnivariateLastPoint(options);

System.out.println("=== Last Point Detection ===");
System.out.println("Is Anomaly: " + result.isAnomaly());
System.out.println("Is Positive Anomaly: " + result.isPositiveAnomaly());
System.out.println("Is Negative Anomaly: " + result.isNegativeAnomaly());
System.out.printf("Expected Value: %.2f%n", result.getExpectedValue());
System.out.printf("Upper Margin: %.2f%n", result.getUpperMargin());
System.out.printf("Lower Margin: %.2f%n", result.getLowerMargin());
System.out.println("Severity: " + result.getSeverity());

if (result.isAnomaly()) {
    System.out.println("⚠️ ALERT: Anomaly detected in latest data point!");
}
```

### Streaming Detection Pattern

```java
public class StreamingAnomalyDetector {
    
    private final UnivariateClient client;
    private final List<TimeSeriesPoint> buffer;
    private final int windowSize;
    
    public StreamingAnomalyDetector(UnivariateClient client, int windowSize) {
        this.client = client;
        this.buffer = new ArrayList<>();
        this.windowSize = windowSize;
    }
    
    public boolean processDataPoint(OffsetDateTime timestamp, double value) {
        // Add new point
        buffer.add(new TimeSeriesPoint(timestamp, value));
        
        // Keep window size manageable
        if (buffer.size() > windowSize) {
            buffer.remove(0);
        }
        
        // Need minimum 12 points for detection
        if (buffer.size() < 12) {
            return false;
        }
        
        // Detect anomaly
        UnivariateDetectionOptions options = new UnivariateDetectionOptions(buffer)
            .setGranularity(TimeGranularity.MINUTELY)
            .setSensitivity(90);
        
        UnivariateLastDetectionResult result = client.detectUnivariateLastPoint(options);
        
        return result.isAnomaly();
    }
}
```

## Change Point Detection

Detect trend changes in time series data.

```java
UnivariateChangePointDetectionOptions changeOptions = 
    new UnivariateChangePointDetectionOptions(series, TimeGranularity.DAILY);

UnivariateChangePointDetectionResult result = 
    univariateClient.detectUnivariateChangePoint(changeOptions);

System.out.println("=== Change Point Detection ===");
System.out.println("Period: " + result.getPeriod());

int changePointCount = 0;
for (int i = 0; i < result.getIsChangePoint().size(); i++) {
    if (result.getIsChangePoint().get(i)) {
        changePointCount++;
        TimeSeriesPoint point = series.get(i);
        System.out.printf("Change point at %s (confidence: %.2f)%n",
            point.getTimestamp(),
            result.getConfidenceScores().get(i));
    }
}
System.out.printf("Total change points detected: %d%n", changePointCount);
```

## Multivariate Model Training

Train a model on multiple correlated variables.

### Prepare Training Data

Data must be in a ZIP file in Azure Blob Storage with CSV files for each variable:

```
training-data.zip
├── variable1.csv
├── variable2.csv
└── variable3.csv
```

Each CSV format:
```csv
timestamp,value
2023-01-01T00:00:00Z,100.5
2023-01-01T01:00:00Z,102.3
...
```

### Train Model

```java
import com.azure.ai.anomalydetector.models.*;
import java.time.OffsetDateTime;

String blobSasUrl = "https://storage.blob.core.windows.net/container/training-data.zip?sasToken";

ModelInfo modelInfo = new ModelInfo()
    .setDataSource(blobSasUrl)
    .setStartTime(OffsetDateTime.parse("2023-01-01T00:00:00Z"))
    .setEndTime(OffsetDateTime.parse("2023-06-01T00:00:00Z"))
    .setSlidingWindow(200)  // Window size for pattern detection
    .setAlignPolicy(new AlignPolicy()
        .setAlignMode(AlignMode.OUTER)
        .setFillNAMethod(FillNAMethod.LINEAR))
    .setDisplayName("MyMultivariateModel");

// Start training (long-running operation)
AnomalyDetectionModel trainedModel = multivariateClient.trainMultivariateModel(modelInfo);

String modelId = trainedModel.getModelId();
System.out.println("Model ID: " + modelId);

// Poll for training completion
AnomalyDetectionModel model;
do {
    Thread.sleep(10000); // Wait 10 seconds
    model = multivariateClient.getMultivariateModel(modelId);
    System.out.println("Training status: " + model.getModelInfo().getStatus());
} while (model.getModelInfo().getStatus() == ModelStatus.CREATED 
      || model.getModelInfo().getStatus() == ModelStatus.RUNNING);

if (model.getModelInfo().getStatus() == ModelStatus.READY) {
    System.out.println("Model trained successfully!");
    System.out.println("Variables used: " + model.getModelInfo().getVariableStates().size());
} else {
    System.err.println("Training failed: " + model.getModelInfo().getErrors());
}
```

## Multivariate Batch Inference

Detect anomalies across multiple variables at once.

```java
String inferenceDataUrl = "https://storage.blob.core.windows.net/container/inference-data.zip?sasToken";

MultivariateBatchDetectionOptions detectionOptions = new MultivariateBatchDetectionOptions()
    .setDataSource(inferenceDataUrl)
    .setStartTime(OffsetDateTime.parse("2023-07-01T00:00:00Z"))
    .setEndTime(OffsetDateTime.parse("2023-07-31T00:00:00Z"))
    .setTopContributorCount(10);  // Top contributing variables to show

// Start batch detection
MultivariateDetectionResult detectionResult = 
    multivariateClient.detectMultivariateBatchAnomaly(modelId, detectionOptions);

String resultId = detectionResult.getResultId();
System.out.println("Detection started, result ID: " + resultId);

// Poll for results
MultivariateDetectionResult result;
do {
    Thread.sleep(5000);
    result = multivariateClient.getBatchDetectionResult(resultId);
    System.out.println("Detection status: " + result.getSummary().getStatus());
} while (result.getSummary().getStatus() == MultivariateBatchDetectionStatus.CREATED
      || result.getSummary().getStatus() == MultivariateBatchDetectionStatus.RUNNING);

// Process results
if (result.getSummary().getStatus() == MultivariateBatchDetectionStatus.READY) {
    System.out.println("=== Multivariate Anomaly Detection Results ===");
    
    int anomalyCount = 0;
    for (AnomalyState state : result.getResults()) {
        if (state.getValue().isAnomaly()) {
            anomalyCount++;
            System.out.printf("Anomaly at %s, severity: %.4f%n",
                state.getTimestamp(),
                state.getValue().getSeverity());
            
            // Show contributing variables
            if (state.getValue().getInterpretation() != null) {
                System.out.println("  Contributing variables:");
                for (AnomalyInterpretation interp : state.getValue().getInterpretation()) {
                    System.out.printf("    - %s: %.4f%n",
                        interp.getVariable(),
                        interp.getContributionScore());
                }
            }
        }
    }
    System.out.printf("Total anomalies detected: %d%n", anomalyCount);
}
```

## Multivariate Last Point Detection

Real-time detection for multivariate data.

```java
import java.util.Arrays;

// Prepare latest data point for each variable
List<VariableValues> variables = Arrays.asList(
    new VariableValues("temperature", 
        Arrays.asList("2023-07-15T12:00:00Z"), 
        Arrays.asList(85.5f)),
    new VariableValues("pressure", 
        Arrays.asList("2023-07-15T12:00:00Z"), 
        Arrays.asList(1013.2f)),
    new VariableValues("humidity", 
        Arrays.asList("2023-07-15T12:00:00Z"), 
        Arrays.asList(65.0f))
);

MultivariateLastDetectionOptions lastOptions = new MultivariateLastDetectionOptions()
    .setVariables(variables)
    .setTopContributorCount(5);

MultivariateLastDetectionResult lastResult = 
    multivariateClient.detectMultivariateLastAnomaly(modelId, lastOptions);

System.out.println("=== Multivariate Last Point Detection ===");
System.out.println("Is Anomaly: " + lastResult.getValue().isAnomaly());
System.out.printf("Severity: %.4f%n", lastResult.getValue().getSeverity());
System.out.printf("Score: %.4f%n", lastResult.getValue().getScore());

if (lastResult.getValue().isAnomaly()) {
    System.out.println("Contributing variables:");
    for (AnomalyInterpretation interp : lastResult.getValue().getInterpretation()) {
        System.out.printf("  - %s: contribution=%.4f, value=%.2f, expected=%.2f%n",
            interp.getVariable(),
            interp.getContributionScore(),
            interp.getCorrelationChanges().getChangedValues().get(0),
            interp.getCorrelationChanges().getExpectedValues().get(0));
    }
}
```

## Model Management

### List Models

```java
import com.azure.core.http.rest.PagedIterable;

PagedIterable<AnomalyDetectionModel> models = multivariateClient.listMultivariateModels();

System.out.println("=== Available Models ===");
for (AnomalyDetectionModel m : models) {
    System.out.printf("Model: %s, Status: %s, Created: %s%n",
        m.getModelId(),
        m.getModelInfo().getStatus(),
        m.getCreatedTime());
}
```

### Get Model Details

```java
AnomalyDetectionModel model = multivariateClient.getMultivariateModel(modelId);

System.out.println("=== Model Details ===");
System.out.println("Model ID: " + model.getModelId());
System.out.println("Display Name: " + model.getModelInfo().getDisplayName());
System.out.println("Status: " + model.getModelInfo().getStatus());
System.out.println("Created: " + model.getCreatedTime());
System.out.println("Last Updated: " + model.getLastUpdatedTime());
System.out.println("Sliding Window: " + model.getModelInfo().getSlidingWindow());

// Variable states
System.out.println("Variables:");
for (VariableState vs : model.getModelInfo().getVariableStates()) {
    System.out.printf("  - %s: effective=%d, missing=%.2f%%%n",
        vs.getVariable(),
        vs.getEffectiveCount(),
        vs.getMissingRatio() * 100);
}
```

### Delete Model

```java
multivariateClient.deleteMultivariateModel(modelId);
System.out.println("Model deleted: " + modelId);
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    UnivariateDetectionOptions options = new UnivariateDetectionOptions(series)
        .setGranularity(TimeGranularity.DAILY);
    
    univariateClient.detectUnivariateEntireSeries(options);
    
} catch (HttpResponseException e) {
    int statusCode = e.getResponse().getStatusCode();
    System.err.println("HTTP Status: " + statusCode);
    System.err.println("Error: " + e.getMessage());
    
    switch (statusCode) {
        case 400:
            System.err.println("Bad request - check data format and minimum points (12 required)");
            break;
        case 401:
            System.err.println("Unauthorized - check API key");
            break;
        case 404:
            System.err.println("Model not found");
            break;
        case 429:
            System.err.println("Rate limited - implement retry with backoff");
            break;
        default:
            System.err.println("Unexpected error");
    }
} catch (Exception e) {
    System.err.println("Unexpected error: " + e.getMessage());
}
```

## Complete Application Example

```java
import com.azure.ai.anomalydetector.AnomalyDetectorClientBuilder;
import com.azure.ai.anomalydetector.UnivariateClient;
import com.azure.ai.anomalydetector.models.*;
import com.azure.identity.DefaultAzureCredentialBuilder;

import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class MetricsAnomalyDetector {
    
    private final UnivariateClient client;
    private final int sensitivity;
    
    public MetricsAnomalyDetector(int sensitivity) {
        this.client = new AnomalyDetectorClientBuilder()
            .endpoint(System.getenv("AZURE_ANOMALY_DETECTOR_ENDPOINT"))
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildUnivariateClient();
        this.sensitivity = sensitivity;
    }
    
    public List<AnomalyResult> detectAnomalies(List<MetricDataPoint> metrics) {
        // Convert to time series points
        List<TimeSeriesPoint> series = new ArrayList<>();
        for (MetricDataPoint metric : metrics) {
            series.add(new TimeSeriesPoint(metric.timestamp, metric.value));
        }
        
        // Detect anomalies
        UnivariateDetectionOptions options = new UnivariateDetectionOptions(series)
            .setGranularity(TimeGranularity.MINUTELY)
            .setSensitivity(sensitivity);
        
        UnivariateEntireDetectionResult result = client.detectUnivariateEntireSeries(options);
        
        // Build results
        List<AnomalyResult> anomalies = new ArrayList<>();
        for (int i = 0; i < result.getIsAnomaly().size(); i++) {
            if (result.getIsAnomaly().get(i)) {
                anomalies.add(new AnomalyResult(
                    metrics.get(i).timestamp,
                    metrics.get(i).value,
                    result.getExpectedValues().get(i),
                    result.getUpperMargins().get(i),
                    result.getLowerMargins().get(i),
                    result.getIsPositiveAnomaly().get(i) ? "SPIKE" : "DIP"
                ));
            }
        }
        
        return anomalies;
    }
    
    public boolean isLatestPointAnomaly(List<MetricDataPoint> metrics) {
        List<TimeSeriesPoint> series = new ArrayList<>();
        for (MetricDataPoint metric : metrics) {
            series.add(new TimeSeriesPoint(metric.timestamp, metric.value));
        }
        
        UnivariateDetectionOptions options = new UnivariateDetectionOptions(series)
            .setGranularity(TimeGranularity.MINUTELY)
            .setSensitivity(sensitivity);
        
        UnivariateLastDetectionResult result = client.detectUnivariateLastPoint(options);
        return result.isAnomaly();
    }
    
    // Data classes
    public static class MetricDataPoint {
        public final OffsetDateTime timestamp;
        public final double value;
        
        public MetricDataPoint(OffsetDateTime timestamp, double value) {
            this.timestamp = timestamp;
            this.value = value;
        }
    }
    
    public static class AnomalyResult {
        public final OffsetDateTime timestamp;
        public final double actualValue;
        public final double expectedValue;
        public final double upperBound;
        public final double lowerBound;
        public final String type;
        
        public AnomalyResult(OffsetDateTime timestamp, double actualValue, 
                           double expectedValue, double upperBound, 
                           double lowerBound, String type) {
            this.timestamp = timestamp;
            this.actualValue = actualValue;
            this.expectedValue = expectedValue;
            this.upperBound = upperBound;
            this.lowerBound = lowerBound;
            this.type = type;
        }
        
        @Override
        public String toString() {
            return String.format("[%s] %s: actual=%.2f, expected=%.2f (bounds: %.2f - %.2f)",
                timestamp, type, actualValue, expectedValue, lowerBound, upperBound);
        }
    }
    
    public static void main(String[] args) {
        MetricsAnomalyDetector detector = new MetricsAnomalyDetector(90);
        
        // Generate sample data with an anomaly
        List<MetricDataPoint> metrics = new ArrayList<>();
        OffsetDateTime baseTime = OffsetDateTime.now().minusHours(1);
        Random random = new Random();
        
        for (int i = 0; i < 60; i++) {
            double value = 100 + random.nextGaussian() * 5;
            
            // Inject anomaly at minute 45
            if (i == 45) {
                value = 200;
            }
            
            metrics.add(new MetricDataPoint(
                baseTime.plus(i, ChronoUnit.MINUTES),
                value
            ));
        }
        
        // Detect anomalies
        List<AnomalyResult> anomalies = detector.detectAnomalies(metrics);
        
        System.out.println("=== Detected Anomalies ===");
        for (AnomalyResult anomaly : anomalies) {
            System.out.println(anomaly);
        }
        
        // Check latest point
        boolean isLatestAnomaly = detector.isLatestPointAnomaly(metrics);
        System.out.println("\nLatest point is anomaly: " + isLatestAnomaly);
    }
}
```

## Environment Variables

```bash
AZURE_ANOMALY_DETECTOR_ENDPOINT=https://<resource>.cognitiveservices.azure.com/
AZURE_ANOMALY_DETECTOR_API_KEY=<your-api-key>

# For DefaultAzureCredential
AZURE_CLIENT_ID=<service-principal-client-id>
AZURE_CLIENT_SECRET=<service-principal-secret>
AZURE_TENANT_ID=<tenant-id>
```

## Best Practices

1. **Minimum data points** — Univariate requires at least 12 points; more data improves accuracy
2. **Match granularity** — Set `TimeGranularity` to match your actual data frequency
3. **Tune sensitivity** — Higher values (0-99) detect more anomalies; tune based on use case
4. **Multivariate training** — Use 200-1000 sliding window based on pattern complexity
5. **Handle missing data** — Use `ImputeMode` to handle gaps in time series
6. **Use streaming for real-time** — `detectUnivariateLastPoint` for continuous monitoring
7. **Check contributing variables** — For multivariate, analyze which variables caused the anomaly
8. **Implement retry logic** — Handle rate limiting with exponential backoff
