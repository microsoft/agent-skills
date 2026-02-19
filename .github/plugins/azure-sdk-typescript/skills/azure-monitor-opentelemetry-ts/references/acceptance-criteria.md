# Azure Monitor OpenTelemetry SDK Acceptance Criteria (TypeScript)

**SDK**: `@azure/monitor-opentelemetry`, `@azure/monitor-opentelemetry-exporter`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/monitor
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Auto-Instrumentation Imports

#### ✅ CORRECT: useAzureMonitor Import
```typescript
import { useAzureMonitor, shutdownAzureMonitor } from "@azure/monitor-opentelemetry";
```

#### ✅ CORRECT: With Options Type
```typescript
import { useAzureMonitor, AzureMonitorOpenTelemetryOptions } from "@azure/monitor-opentelemetry";
```

### 1.2 Exporter Imports

#### ✅ CORRECT: Exporter Imports
```typescript
import { AzureMonitorTraceExporter } from "@azure/monitor-opentelemetry-exporter";
import { AzureMonitorMetricExporter } from "@azure/monitor-opentelemetry-exporter";
import { AzureMonitorLogExporter } from "@azure/monitor-opentelemetry-exporter";
```

### 1.3 OpenTelemetry API Imports

#### ✅ CORRECT: OpenTelemetry Imports
```typescript
import { trace } from "@opentelemetry/api";
import { metrics } from "@opentelemetry/api";
import { logs } from "@opentelemetry/api-logs";
```

### 1.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong package name
```typescript
// WRONG - package is @azure/monitor-opentelemetry
import { useAzureMonitor } from "@azure/opentelemetry";
import { useAzureMonitor } from "azure-monitor-opentelemetry";
```

---

## 2. Initialization Patterns

### 2.1 ✅ CORRECT: Basic Auto-Instrumentation
```typescript
import { useAzureMonitor } from "@azure/monitor-opentelemetry";

useAzureMonitor({
  azureMonitorExporterOptions: {
    connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
  }
});

// Import application AFTER useAzureMonitor
import express from "express";
const app = express();
```

### 2.2 ✅ CORRECT: Full Configuration
```typescript
import { useAzureMonitor, AzureMonitorOpenTelemetryOptions } from "@azure/monitor-opentelemetry";
import { resourceFromAttributes } from "@opentelemetry/resources";

const options: AzureMonitorOpenTelemetryOptions = {
  azureMonitorExporterOptions: {
    connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING,
    storageDirectory: "/path/to/offline/storage",
    disableOfflineStorage: false
  },
  samplingRatio: 1.0,
  enableLiveMetrics: true,
  enableStandardMetrics: true,
  enablePerformanceCounters: true,
  instrumentationOptions: {
    azureSdk: { enabled: true },
    http: { enabled: true },
    mongoDb: { enabled: true },
    mySql: { enabled: true },
    postgreSql: { enabled: true },
    redis: { enabled: true },
    bunyan: { enabled: false },
    winston: { enabled: false }
  },
  resource: resourceFromAttributes({ "service.name": "my-service" })
};

useAzureMonitor(options);
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing app before useAzureMonitor
```typescript
// WRONG - useAzureMonitor must be called BEFORE importing other modules
import express from "express";
import { useAzureMonitor } from "@azure/monitor-opentelemetry";

useAzureMonitor({...});  // Too late!
```

#### ❌ INCORRECT: Hardcoded connection string
```typescript
// WRONG - hardcoded connection string
useAzureMonitor({
  azureMonitorExporterOptions: {
    connectionString: "InstrumentationKey=12345;IngestionEndpoint=https://..."
  }
});
```

---

## 3. Custom Traces Patterns

### 3.1 ✅ CORRECT: Creating Custom Spans
```typescript
import { trace } from "@opentelemetry/api";

const tracer = trace.getTracer("my-tracer");

const span = tracer.startSpan("doWork");
try {
  span.setAttribute("component", "worker");
  span.setAttribute("operation.id", "42");
  span.addEvent("processing started");
  
  // Your work here
  
} catch (error) {
  span.recordException(error as Error);
  span.setStatus({ code: 2, message: (error as Error).message });
} finally {
  span.end();
}
```

### 3.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not ending span
```typescript
// WRONG - span must be ended
const span = tracer.startSpan("doWork");
span.setAttribute("key", "value");
// Missing span.end()
```

---

## 4. Custom Metrics Patterns

### 4.1 ✅ CORRECT: Creating Custom Metrics
```typescript
import { metrics } from "@opentelemetry/api";

const meter = metrics.getMeter("my-meter");

// Counter
const counter = meter.createCounter("requests_total");
counter.add(1, { route: "/api/users", method: "GET" });

// Histogram
const histogram = meter.createHistogram("request_duration_ms");
histogram.record(150, { route: "/api/users" });

// Observable Gauge
const gauge = meter.createObservableGauge("active_connections");
gauge.addCallback((result) => {
  result.observe(getActiveConnections(), { pool: "main" });
});
```

---

## 5. Manual Exporter Setup Patterns

### 5.1 ✅ CORRECT: Trace Exporter Setup
```typescript
import { AzureMonitorTraceExporter } from "@azure/monitor-opentelemetry-exporter";
import { NodeTracerProvider, BatchSpanProcessor } from "@opentelemetry/sdk-trace-node";

const exporter = new AzureMonitorTraceExporter({
  connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
});

const provider = new NodeTracerProvider({
  spanProcessors: [new BatchSpanProcessor(exporter)]
});

provider.register();
```

### 5.2 ✅ CORRECT: Metric Exporter Setup
```typescript
import { AzureMonitorMetricExporter } from "@azure/monitor-opentelemetry-exporter";
import { PeriodicExportingMetricReader, MeterProvider } from "@opentelemetry/sdk-metrics";
import { metrics } from "@opentelemetry/api";

const exporter = new AzureMonitorMetricExporter({
  connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
});

const meterProvider = new MeterProvider({
  readers: [new PeriodicExportingMetricReader({ exporter })]
});

metrics.setGlobalMeterProvider(meterProvider);
```

### 5.3 ✅ CORRECT: Log Exporter Setup
```typescript
import { AzureMonitorLogExporter } from "@azure/monitor-opentelemetry-exporter";
import { BatchLogRecordProcessor, LoggerProvider } from "@opentelemetry/sdk-logs";
import { logs } from "@opentelemetry/api-logs";

const exporter = new AzureMonitorLogExporter({
  connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
});

const loggerProvider = new LoggerProvider();
loggerProvider.addLogRecordProcessor(new BatchLogRecordProcessor(exporter));

logs.setGlobalLoggerProvider(loggerProvider);
```

---

## 6. Custom Span Processor Patterns

### 6.1 ✅ CORRECT: Custom Span Processor
```typescript
import { SpanProcessor, ReadableSpan } from "@opentelemetry/sdk-trace-base";
import { Span, Context, SpanKind, TraceFlags } from "@opentelemetry/api";
import { useAzureMonitor } from "@azure/monitor-opentelemetry";

class FilteringSpanProcessor implements SpanProcessor {
  forceFlush(): Promise<void> { return Promise.resolve(); }
  shutdown(): Promise<void> { return Promise.resolve(); }
  onStart(span: Span, context: Context): void {}
  
  onEnd(span: ReadableSpan): void {
    span.attributes["CustomDimension"] = "value";
    
    if (span.kind === SpanKind.INTERNAL) {
      span.spanContext().traceFlags = TraceFlags.NONE;
    }
  }
}

useAzureMonitor({
  spanProcessors: [new FilteringSpanProcessor()]
});
```

---

## 7. ESM Support Patterns

### 7.1 ✅ CORRECT: ESM Loader Usage
```bash
node --import @azure/monitor-opentelemetry/loader ./dist/index.js
```

### 7.2 ✅ CORRECT: Package.json Script
```json
{
  "scripts": {
    "start": "node --import @azure/monitor-opentelemetry/loader ./dist/index.js"
  }
}
```

---

## 8. Sampling Patterns

### 8.1 ✅ CORRECT: Sampling Configuration
```typescript
import { ApplicationInsightsSampler } from "@azure/monitor-opentelemetry-exporter";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";

const sampler = new ApplicationInsightsSampler(0.75);  // 75% sampling

const provider = new NodeTracerProvider({ sampler });
```

### 8.2 ✅ CORRECT: Sampling via useAzureMonitor
```typescript
useAzureMonitor({
  azureMonitorExporterOptions: {
    connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
  },
  samplingRatio: 0.5  // 50% of traces
});
```

---

## 9. Shutdown Patterns

### 9.1 ✅ CORRECT: Graceful Shutdown
```typescript
import { useAzureMonitor, shutdownAzureMonitor } from "@azure/monitor-opentelemetry";

useAzureMonitor({
  azureMonitorExporterOptions: {
    connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
  }
});

process.on("SIGTERM", async () => {
  await shutdownAzureMonitor();
  process.exit(0);
});
```

### 9.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not flushing on shutdown
```typescript
// WRONG - should call shutdownAzureMonitor to flush telemetry
process.on("SIGTERM", () => {
  process.exit(0);  // Telemetry may be lost
});
```

---

## 10. Environment Variables

### 10.1 ✅ CORRECT: Required Variables
```typescript
const connectionString = process.env.APPLICATIONINSIGHTS_CONNECTION_STRING!;
```

### 10.2 ❌ INCORRECT: Hardcoded values
```typescript
// WRONG - hardcoded connection string
const connectionString = "InstrumentationKey=abc123;IngestionEndpoint=https://...";
```
