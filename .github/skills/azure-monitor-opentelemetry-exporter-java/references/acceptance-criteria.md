# Azure Monitor OpenTelemetry Exporter for Java Acceptance Criteria

**SDK**: `com.azure:azure-monitor-opentelemetry-exporter` (Deprecated)
**Recommended**: `com.azure:azure-monitor-opentelemetry-autoconfigure`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Azure Monitor Exporter Imports
#### ✅ CORRECT: AzureMonitorExporter Import
```java
import com.azure.monitor.opentelemetry.exporter.AzureMonitorExporter;
```
#### ❌ INCORRECT: Wrong Package or Class Names
```java
import com.azure.monitor.opentelemetry.AzureMonitorExporter;  // Wrong package
import com.azure.monitor.exporter.AzureMonitorExporter;  // Wrong package
```

### 1.2 OpenTelemetry SDK Imports
#### ✅ CORRECT: OpenTelemetry Autoconfigure Imports
```java
import io.opentelemetry.sdk.autoconfigure.AutoConfiguredOpenTelemetrySdk;
import io.opentelemetry.sdk.autoconfigure.AutoConfiguredOpenTelemetrySdkBuilder;
import io.opentelemetry.api.OpenTelemetry;
```
#### ❌ INCORRECT: Deprecated or Wrong SDK Imports
```java
import io.opentelemetry.OpenTelemetry;  // Old import path
import io.opentelemetry.sdk.OpenTelemetrySdk;  // Not for autoconfigure
```

### 1.3 Tracing Imports
#### ✅ CORRECT: Tracer and Span Imports
```java
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.context.Scope;
```
#### ❌ INCORRECT: Wrong Span Import
```java
import io.opentelemetry.trace.Span;  // Old package
import io.opentelemetry.sdk.trace.Span;  // SDK internal, not API
```

### 1.4 Metrics Imports
#### ✅ CORRECT: Meter and Instrument Imports
```java
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.metrics.LongCounter;
import io.opentelemetry.api.metrics.LongHistogram;
```

### 1.5 Attributes Imports
#### ✅ CORRECT: AttributeKey and Attributes
```java
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
```

---

## 2. SDK Initialization Patterns

### 2.1 Autoconfigure with Environment Variable
#### ✅ CORRECT: Using AzureMonitorExporter.customize()
```java
AutoConfiguredOpenTelemetrySdkBuilder sdkBuilder = AutoConfiguredOpenTelemetrySdk.builder();
AzureMonitorExporter.customize(sdkBuilder);
OpenTelemetry openTelemetry = sdkBuilder.build().getOpenTelemetrySdk();
```
#### ❌ INCORRECT: Direct Exporter Instantiation (Deprecated Pattern)
```java
// Don't use deprecated manual exporter setup
AzureMonitorTraceExporter exporter = new AzureMonitorExporterBuilder()
    .connectionString(connectionString)
    .buildTraceExporter();
```

### 2.2 Explicit Connection String
#### ✅ CORRECT: Passing Connection String to customize()
```java
AutoConfiguredOpenTelemetrySdkBuilder sdkBuilder = AutoConfiguredOpenTelemetrySdk.builder();
AzureMonitorExporter.customize(sdkBuilder, "{connection-string}");
OpenTelemetry openTelemetry = sdkBuilder.build().getOpenTelemetrySdk();
```
#### ❌ INCORRECT: Wrong Method Signature
```java
AzureMonitorExporter.configure(sdkBuilder, connectionString);  // Wrong method name
AzureMonitorExporter.customize(connectionString);  // Missing builder
```

---

## 3. Tracer Operations

### 3.1 Getting a Tracer
#### ✅ CORRECT: Tracer from OpenTelemetry Instance
```java
Tracer tracer = openTelemetry.getTracer("com.example.myapp");
```
#### ❌ INCORRECT: Global Tracer Access (Not Recommended)
```java
Tracer tracer = GlobalOpenTelemetry.getTracer("myapp");  // Avoid global access
```

### 3.2 Creating Spans
#### ✅ CORRECT: Span with try-with-resources for Scope
```java
Span span = tracer.spanBuilder("myOperation").startSpan();

try (Scope scope = span.makeCurrent()) {
    doWork();
} catch (Throwable t) {
    span.recordException(t);
    throw t;
} finally {
    span.end();
}
```
#### ❌ INCORRECT: Missing Scope or End
```java
Span span = tracer.spanBuilder("myOperation").startSpan();
doWork();  // No scope, no end - span never completes

Span span = tracer.spanBuilder("myOperation").startSpan();
doWork();
span.end();  // Missing scope - context not propagated
```

### 3.3 Span with Attributes at Start
#### ✅ CORRECT: Setting Attributes on Builder
```java
Span span = tracer.spanBuilder("processOrder")
    .setAttribute("order.id", "12345")
    .setAttribute("customer.tier", "premium")
    .startSpan();
```

### 3.4 Adding Attributes During Execution
#### ✅ CORRECT: Dynamic Attributes
```java
try (Scope scope = span.makeCurrent()) {
    span.setAttribute("items.count", 3);
    span.setAttribute("total.amount", 99.99);
    processOrder();
} finally {
    span.end();
}
```

---

## 4. Nested Spans

### 4.1 Parent-Child Span Relationship
#### ✅ CORRECT: Automatic Context Propagation
```java
public void parentOperation() {
    Span parentSpan = tracer.spanBuilder("parentOperation").startSpan();
    try (Scope scope = parentSpan.makeCurrent()) {
        childOperation();  // Child automatically links to parent
    } finally {
        parentSpan.end();
    }
}

public void childOperation() {
    Span childSpan = tracer.spanBuilder("childOperation").startSpan();
    try (Scope scope = childSpan.makeCurrent()) {
        // Child work
    } finally {
        childSpan.end();
    }
}
```
#### ❌ INCORRECT: Manual Parent Setting (Unnecessary)
```java
Span childSpan = tracer.spanBuilder("childOperation")
    .setParent(Context.current().with(parentSpan))  // Unnecessary if scope is active
    .startSpan();
```

---

## 5. Exception Recording

### 5.1 Recording Exceptions on Spans
#### ✅ CORRECT: Record and Set Error Status
```java
Span span = tracer.spanBuilder("riskyOperation").startSpan();
try (Scope scope = span.makeCurrent()) {
    performRiskyWork();
} catch (Exception e) {
    span.recordException(e);
    span.setStatus(StatusCode.ERROR, e.getMessage());
    throw e;
} finally {
    span.end();
}
```
#### ❌ INCORRECT: Missing Exception Recording
```java
try (Scope scope = span.makeCurrent()) {
    performRiskyWork();
} catch (Exception e) {
    throw e;  // Exception not recorded on span
} finally {
    span.end();
}
```

---

## 6. Custom Span Processor

### 6.1 Implementing SpanProcessor
#### ✅ CORRECT: Custom Processor Implementation
```java
import io.opentelemetry.sdk.trace.SpanProcessor;
import io.opentelemetry.sdk.trace.ReadWriteSpan;
import io.opentelemetry.sdk.trace.ReadableSpan;
import io.opentelemetry.context.Context;

private static final AttributeKey<String> CUSTOM_ATTR = AttributeKey.stringKey("custom.attribute");

SpanProcessor customProcessor = new SpanProcessor() {
    @Override
    public void onStart(Context context, ReadWriteSpan span) {
        span.setAttribute(CUSTOM_ATTR, "customValue");
    }

    @Override
    public boolean isStartRequired() {
        return true;
    }

    @Override
    public void onEnd(ReadableSpan span) {
        // Post-processing
    }

    @Override
    public boolean isEndRequired() {
        return false;
    }
};
```

### 6.2 Registering Custom Processor
#### ✅ CORRECT: Using TracerProviderCustomizer
```java
AutoConfiguredOpenTelemetrySdkBuilder sdkBuilder = AutoConfiguredOpenTelemetrySdk.builder();
AzureMonitorExporter.customize(sdkBuilder);

sdkBuilder.addTracerProviderCustomizer(
    (sdkTracerProviderBuilder, configProperties) -> 
        sdkTracerProviderBuilder.addSpanProcessor(customProcessor)
);

OpenTelemetry openTelemetry = sdkBuilder.build().getOpenTelemetrySdk();
```
#### ❌ INCORRECT: Adding Processor After Build
```java
OpenTelemetry openTelemetry = sdkBuilder.build().getOpenTelemetrySdk();
// Cannot add processor after SDK is built
```

---

## 7. Metrics Operations

### 7.1 Creating a Meter
#### ✅ CORRECT: Meter from OpenTelemetry
```java
Meter meter = openTelemetry.getMeter("com.example.myapp");
```

### 7.2 Creating Counters
#### ✅ CORRECT: LongCounter with Description and Unit
```java
LongCounter requestCounter = meter.counterBuilder("http.requests")
    .setDescription("Total HTTP requests")
    .setUnit("requests")
    .build();

requestCounter.add(1, Attributes.of(
    AttributeKey.stringKey("http.method"), "GET",
    AttributeKey.longKey("http.status_code"), 200L
));
```
#### ❌ INCORRECT: Wrong Attribute Types
```java
requestCounter.add(1, Attributes.of(
    AttributeKey.stringKey("http.status_code"), "200"  // Should be long, not string
));
```

### 7.3 Creating Histograms
#### ✅ CORRECT: LongHistogram for Latency
```java
LongHistogram latencyHistogram = meter.histogramBuilder("http.latency")
    .setDescription("Request latency")
    .setUnit("ms")
    .ofLongs()
    .build();

latencyHistogram.record(150, Attributes.of(
    AttributeKey.stringKey("http.route"), "/api/users"
));
```
#### ❌ INCORRECT: Missing ofLongs() for Long Histogram
```java
// This creates a DoubleHistogram, not LongHistogram
var histogram = meter.histogramBuilder("latency").build();
```

---

## 8. Environment Configuration

### 8.1 Required Environment Variable
#### ✅ CORRECT: Connection String Environment Variable
```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/
```
#### ❌ INCORRECT: Wrong Variable Name
```bash
APPLICATION_INSIGHTS_CONNECTION_STRING=...  # Wrong name (underscores)
APPINSIGHTS_CONNECTIONSTRING=...  # Wrong name
```

---

## 9. Migration to Autoconfigure

### 9.1 Dependency Change
#### ✅ CORRECT: New Autoconfigure Dependency
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-opentelemetry-autoconfigure</artifactId>
    <version>LATEST</version>
</dependency>
```
#### ❌ INCORRECT: Using Deprecated Package
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-opentelemetry-exporter</artifactId>
    <version>1.0.0-beta.x</version>
</dependency>
```

---

## 10. Best Practices

### 10.1 Semantic Conventions
#### ✅ CORRECT: Using Standard Attribute Names
```java
span.setAttribute("http.method", "GET");
span.setAttribute("http.url", "https://api.example.com/users");
span.setAttribute("http.status_code", 200);
span.setAttribute("db.system", "postgresql");
span.setAttribute("db.statement", "SELECT * FROM users");
```
#### ❌ INCORRECT: Custom Non-Standard Names
```java
span.setAttribute("method", "GET");  // Should be http.method
span.setAttribute("url", "...");  // Should be http.url
span.setAttribute("statusCode", 200);  // Should be http.status_code
```

### 10.2 Always End Spans
#### ✅ CORRECT: Span End in Finally Block
```java
Span span = tracer.spanBuilder("operation").startSpan();
try (Scope scope = span.makeCurrent()) {
    doWork();
} finally {
    span.end();  // Always in finally
}
```
#### ❌ INCORRECT: Conditional Span End
```java
Span span = tracer.spanBuilder("operation").startSpan();
try {
    doWork();
    span.end();  // Won't execute on exception
} catch (Exception e) {
    // span.end() never called
}
```
