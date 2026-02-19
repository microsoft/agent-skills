# Azure Monitor OpenTelemetry Exporter for Java Acceptance Criteria

**SDK**: `com.azure:azure-monitor-opentelemetry-exporter` (DEPRECATED)
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## ⚠️ DEPRECATION NOTICE

**This package is deprecated.** Migrate to `azure-monitor-opentelemetry-autoconfigure`.

---

## 1. Recommended: Use Autoconfigure

### 1.1 ✅ CORRECT: Use Autoconfigure Package
```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-opentelemetry-autoconfigure</artifactId>
    <version>LATEST</version>
</dependency>
```

### 1.2 ✅ CORRECT: Setup with Autoconfigure
```java
import io.opentelemetry.sdk.autoconfigure.AutoConfiguredOpenTelemetrySdk;
import io.opentelemetry.sdk.autoconfigure.AutoConfiguredOpenTelemetrySdkBuilder;
import io.opentelemetry.api.OpenTelemetry;
import com.azure.monitor.opentelemetry.exporter.AzureMonitorExporter;

// Connection string from APPLICATIONINSIGHTS_CONNECTION_STRING env var
AutoConfiguredOpenTelemetrySdkBuilder sdkBuilder = AutoConfiguredOpenTelemetrySdk.builder();
AzureMonitorExporter.customize(sdkBuilder);
OpenTelemetry openTelemetry = sdkBuilder.build().getOpenTelemetrySdk();
```

---

## 2. Creating Spans

### 2.1 ✅ CORRECT: Basic Span
```java
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.context.Scope;

Tracer tracer = openTelemetry.getTracer("com.example.myapp");

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

### 2.2 ✅ CORRECT: Span with Attributes
```java
Span span = tracer.spanBuilder("processOrder")
    .setAttribute("order.id", "12345")
    .setAttribute("customer.tier", "premium")
    .startSpan();
```

---

## 3. Recording Exceptions

### 3.1 ✅ CORRECT: Record Exception on Span
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

---

## 4. Best Practices Checklist

- [ ] Use `azure-monitor-opentelemetry-autoconfigure` instead of this package
- [ ] Set APPLICATIONINSIGHTS_CONNECTION_STRING environment variable
- [ ] Use meaningful span names
- [ ] Add relevant attributes for debugging
- [ ] Always record exceptions on spans
- [ ] End spans in finally block
- [ ] Use try-with-resources for Scope management
