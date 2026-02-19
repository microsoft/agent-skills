# Telemetry & Observability for Node.js

Configure OpenTelemetry in JavaScript/TypeScript apps to report traces, metrics, and logs to the Aspire dashboard.

---

## How It Works

Aspire sets `OTEL_EXPORTER_OTLP_ENDPOINT` automatically for all orchestrated resources. Node.js apps use the OpenTelemetry SDK to export telemetry data to this endpoint. The Aspire dashboard receives and displays this data.

```
Node.js App → OpenTelemetry SDK → OTLP gRPC → Aspire Dashboard
```

---

## Setup

### 1. Install OpenTelemetry Packages

```bash
npm install @opentelemetry/api \
  @opentelemetry/sdk-node \
  @opentelemetry/auto-instrumentations-node \
  @opentelemetry/exporter-trace-otlp-grpc \
  @opentelemetry/exporter-metrics-otlp-grpc \
  @opentelemetry/sdk-metrics \
  @opentelemetry/resources \
  @opentelemetry/semantic-conventions
```

### 2. Create Telemetry Configuration

```javascript
// telemetry.js — MUST be imported before any other code
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-grpc');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { resourceFromAttributes } = require('@opentelemetry/resources');
const { ATTR_SERVICE_NAME } = require('@opentelemetry/semantic-conventions');

const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4317';

const sdk = new NodeSDK({
    resource: resourceFromAttributes({
        [ATTR_SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'my-node-app',
    }),
    traceExporter: new OTLPTraceExporter({ url: otlpEndpoint }),
    metricReader: new PeriodicExportingMetricReader({
        exporter: new OTLPMetricExporter({ url: otlpEndpoint }),
    }),
    instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

// Graceful shutdown
process.on('SIGTERM', () => sdk.shutdown());
```

### 3. Import First in Entry Point

```javascript
// server.js
require('./telemetry'); // MUST be the first import

const express = require('express');
const app = express();
// ... rest of application
```

### TypeScript Variant

```typescript
// telemetry.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-grpc';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-grpc';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
import { resourceFromAttributes } from '@opentelemetry/resources';
import { ATTR_SERVICE_NAME } from '@opentelemetry/semantic-conventions';

const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4317';

const sdk = new NodeSDK({
    resource: resourceFromAttributes({
        [ATTR_SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'my-node-app',
    }),
    traceExporter: new OTLPTraceExporter({ url: otlpEndpoint }),
    metricReader: new PeriodicExportingMetricReader({
        exporter: new OTLPMetricExporter({ url: otlpEndpoint }),
    }),
    instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

process.on('SIGTERM', () => sdk.shutdown());
```

```typescript
// server.ts — import telemetry first
import './telemetry';
import express from 'express';
// ... rest of application
```

---

## Aspire-Injected Environment Variables

Aspire automatically sets these OpenTelemetry env vars for orchestrated resources:

| Variable | Purpose | Example |
|----------|---------|---------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector URL | `http://localhost:4318` |
| `OTEL_SERVICE_NAME` | Service name in traces | `my-api` |
| `OTEL_RESOURCE_ATTRIBUTES` | Resource attributes | `service.instance.id=abc-123` |
| `OTEL_BSP_SCHEDULE_DELAY` | Batch span export interval (ms) | `1000` |
| `OTEL_BLRP_SCHEDULE_DELAY` | Batch log export interval (ms) | `1000` |
| `OTEL_METRIC_EXPORT_INTERVAL` | Metric export interval (ms) | `1000` |

These are set automatically — you don't need to configure them in the AppHost.

---

## Auto-Instrumentations

The `@opentelemetry/auto-instrumentations-node` package auto-instruments:

- **HTTP:** `http` and `https` modules
- **Express:** Route handling, middleware
- **pg:** PostgreSQL queries
- **redis:** Redis commands (ioredis, redis)
- **MongoDB:** Database operations
- **gRPC:** Client and server calls
- **fs:** File system operations
- **dns:** DNS lookups

### Selective instrumentation

```javascript
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

const sdk = new NodeSDK({
    instrumentations: [
        getNodeAutoInstrumentations({
            '@opentelemetry/instrumentation-fs': { enabled: false },
            '@opentelemetry/instrumentation-dns': { enabled: false },
        }),
    ],
});
```

---

## Custom Spans & Metrics

### Custom spans

```javascript
const { trace } = require('@opentelemetry/api');
const tracer = trace.getTracer('my-app');

async function processOrder(orderId) {
    return tracer.startActiveSpan('process-order', async (span) => {
        span.setAttribute('order.id', orderId);
        try {
            const result = await doWork(orderId);
            span.setStatus({ code: 1 }); // OK
            return result;
        } catch (error) {
            span.setStatus({ code: 2, message: error.message }); // ERROR
            span.recordException(error);
            throw error;
        } finally {
            span.end();
        }
    });
}
```

### Custom metrics

```javascript
const { metrics } = require('@opentelemetry/api');
const meter = metrics.getMeter('my-app');

const requestCounter = meter.createCounter('http.requests.total', {
    description: 'Total HTTP requests',
});

const requestDuration = meter.createHistogram('http.request.duration', {
    description: 'HTTP request duration in ms',
    unit: 'ms',
});

// In request handler
app.use((req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
        requestCounter.add(1, { method: req.method, path: req.path, status: res.statusCode });
        requestDuration.record(Date.now() - start, { method: req.method, path: req.path });
    });
    next();
});
```

---

## Health Checks

Expose a health endpoint for Aspire to monitor:

```javascript
app.get('/health', (req, res) => {
    // Check dependencies
    const healthy = checkDatabaseConnection() && checkRedisConnection();
    res.status(healthy ? 200 : 503).json({ status: healthy ? 'healthy' : 'unhealthy' });
});
```

Configure in AppHost:

```csharp
var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithHttpHealthCheck("/health");
```

The Aspire dashboard shows health status and can trigger restarts.
