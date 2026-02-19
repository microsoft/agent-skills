# Azure Monitor OpenTelemetry Exporter Java - Migration Guide

> **⚠️ DEPRECATION NOTICE**: This package (`azure-monitor-opentelemetry-exporter`) is deprecated.
>
> **Migrate to `azure-monitor-opentelemetry-autoconfigure`** for automatic instrumentation and simplified configuration.

## Migration Overview

| Old Package | New Package |
|-------------|-------------|
| `azure-monitor-opentelemetry-exporter` | `azure-monitor-opentelemetry-autoconfigure` |

## Maven Dependency

### Remove (Deprecated)

```xml
<!-- REMOVE THIS -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-opentelemetry-exporter</artifactId>
    <version>1.0.0-beta.x</version>
</dependency>
```

### Add (Recommended)

```xml
<!-- ADD THIS -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-opentelemetry-autoconfigure</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Environment Variables

```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/
```

## Basic Setup with Autoconfigure

### Using Environment Variable (Simplest)

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

### With Explicit Connection String

```java
String connectionString = System.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING");

AutoConfiguredOpenTelemetrySdkBuilder sdkBuilder = AutoConfiguredOpenTelemetrySdk.builder();
AzureMonitorExporter.customize(sdkBuilder, connectionString);
OpenTelemetry openTelemetry = sdkBuilder.build().getOpenTelemetrySdk();
```

## Creating Traces

```java
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.context.Scope;

// Get tracer
Tracer tracer = openTelemetry.getTracer("com.example.myapp");

// Create span
Span span = tracer.spanBuilder("processOrder").startSpan();

try (Scope scope = span.makeCurrent()) {
    // Your application logic
    span.setAttribute("order.id", "12345");
    span.setAttribute("customer.tier", "premium");
    
    processOrder();
} catch (Throwable t) {
    span.recordException(t);
    throw t;
} finally {
    span.end();
}
```

## Creating Metrics

```java
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.metrics.LongCounter;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.common.AttributeKey;

Meter meter = openTelemetry.getMeter("com.example.myapp");

// Counter
LongCounter requestCounter = meter.counterBuilder("http.requests")
    .setDescription("Total HTTP requests")
    .setUnit("requests")
    .build();

requestCounter.add(1, Attributes.of(
    AttributeKey.stringKey("http.method"), "GET",
    AttributeKey.longKey("http.status_code"), 200L
));
```

## Custom Span Processor

```java
import io.opentelemetry.sdk.trace.SpanProcessor;
import io.opentelemetry.sdk.trace.ReadWriteSpan;
import io.opentelemetry.sdk.trace.ReadableSpan;
import io.opentelemetry.context.Context;

SpanProcessor customProcessor = new SpanProcessor() {
    @Override
    public void onStart(Context context, ReadWriteSpan span) {
        span.setAttribute("custom.attribute", "value");
    }

    @Override
    public boolean isStartRequired() { return true; }

    @Override
    public void onEnd(ReadableSpan span) { }

    @Override
    public boolean isEndRequired() { return false; }
};

AutoConfiguredOpenTelemetrySdkBuilder sdkBuilder = AutoConfiguredOpenTelemetrySdk.builder();
AzureMonitorExporter.customize(sdkBuilder);

sdkBuilder.addTracerProviderCustomizer(
    (sdkTracerProviderBuilder, configProperties) -> 
        sdkTracerProviderBuilder.addSpanProcessor(customProcessor)
);

OpenTelemetry openTelemetry = sdkBuilder.build().getOpenTelemetrySdk();
```

## Why Migrate?

The `azure-monitor-opentelemetry-autoconfigure` package provides:

1. **Automatic instrumentation** — Common libraries instrumented automatically
2. **Simplified configuration** — Less boilerplate code
3. **Better integration** — Native OpenTelemetry SDK integration
4. **Active maintenance** — Ongoing updates and improvements
5. **Production ready** — GA (Generally Available) status

## Migration Steps Summary

1. Update Maven/Gradle dependency
2. Replace manual exporter setup with `AzureMonitorExporter.customize()`
3. Use `AutoConfiguredOpenTelemetrySdk.builder()` for SDK initialization
4. Remove manual span processor registration (unless custom processors needed)
5. Set `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

## Reference Links

| Resource | URL |
|----------|-----|
| Migration Guide | https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/MIGRATION.md |
| Autoconfigure Package | https://central.sonatype.com/artifact/com.azure/azure-monitor-opentelemetry-autoconfigure |
| OpenTelemetry Java | https://opentelemetry.io/docs/languages/java/ |
| Application Insights | https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview |
