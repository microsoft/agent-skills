# Azure Monitor OpenTelemetry Exporter Acceptance Criteria

**SDK**: `azure-monitor-opentelemetry-exporter`
**Repository**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Imports

### 1.1 ✅ CORRECT: Exporter Imports
```python
from azure.monitor.opentelemetry.exporter import (
    AzureMonitorTraceExporter,
    AzureMonitorMetricExporter,
    AzureMonitorLogExporter,
    ApplicationInsightsSampler,
)
```

### 1.2 ✅ CORRECT: OpenTelemetry SDK Imports
```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
```

### 1.3 ✅ CORRECT: Identity Import
```python
from azure.identity import DefaultAzureCredential
```

### 1.4 ❌ INCORRECT: Wrong Module Paths
```python
# WRONG - exporters are not in azure.monitor.opentelemetry
from azure.monitor.opentelemetry import AzureMonitorTraceExporter

# WRONG - legacy package path
from azure.opentelemetry.exporter.azuremonitor import AzureMonitorTraceExporter
```

---

## 2. AzureMonitorTraceExporter

### 2.1 ✅ CORRECT: Trace Exporter with Connection String
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

exporter = AzureMonitorTraceExporter(
    connection_string="InstrumentationKey=...;IngestionEndpoint=https://...",
)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("startup"):
    print("ready")
```

### 2.2 ✅ CORRECT: Trace Exporter with AAD Credential
```python
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

exporter = AzureMonitorTraceExporter(
    credential=DefaultAzureCredential(),
    connection_string="InstrumentationKey=...;IngestionEndpoint=https://...",
)
```

### 2.3 ❌ INCORRECT: Unsupported Constructor Parameters
```python
# WRONG - instrumentation_key is not a supported parameter
exporter = AzureMonitorTraceExporter(instrumentation_key="...")
```

---

## 3. AzureMonitorMetricExporter

### 3.1 ✅ CORRECT: Metric Exporter with Periodic Reader
```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

exporter = AzureMonitorMetricExporter(
    connection_string="InstrumentationKey=...;IngestionEndpoint=https://...",
)

reader = PeriodicExportingMetricReader(exporter, export_interval_millis=60000)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

meter = metrics.get_meter(__name__)
counter = meter.create_counter("requests_total")
counter.add(1, {"route": "/health"})
```

### 3.2 ❌ INCORRECT: Missing Metric Reader
```python
# WRONG - exporter must be used with PeriodicExportingMetricReader
metrics.set_meter_provider(MeterProvider())
```

---

## 4. AzureMonitorLogExporter

### 4.1 ✅ CORRECT: Log Exporter with LoggerProvider
```python
import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

exporter = AzureMonitorLogExporter(
    connection_string="InstrumentationKey=...;IngestionEndpoint=https://...",
)

logger_provider = LoggerProvider()
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
set_logger_provider(logger_provider)

handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("log payload")
```

### 4.2 ❌ INCORRECT: Attaching Handler to Root Logger
```python
# WRONG - use a named logger to avoid exporting SDK internal logs
logging.getLogger().addHandler(LoggingHandler())
```

---

## 5. TracerProvider Setup

### 5.1 ✅ CORRECT: TracerProvider with BatchSpanProcessor
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(AzureMonitorTraceExporter())
)
```

### 5.2 ✅ CORRECT: ApplicationInsightsSampler
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from azure.monitor.opentelemetry.exporter import ApplicationInsightsSampler

sampler = ApplicationInsightsSampler(sampling_ratio=0.1)
trace.set_tracer_provider(TracerProvider(sampler=sampler))
```

### 5.3 ❌ INCORRECT: Using SimpleSpanProcessor in Production
```python
# WRONG - prefer BatchSpanProcessor for production workloads
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))
```

---

## 6. Low-level OpenTelemetry Configuration

### 6.1 ✅ CORRECT: Manual SDK Configuration (Low-level)
```python
import os
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from azure.monitor.opentelemetry.exporter import (
    AzureMonitorTraceExporter,
    AzureMonitorMetricExporter,
    AzureMonitorLogExporter,
)

connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]

trace_exporter = AzureMonitorTraceExporter(connection_string=connection_string)
metric_exporter = AzureMonitorMetricExporter(connection_string=connection_string)
log_exporter = AzureMonitorLogExporter(connection_string=connection_string)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(trace_exporter))

reader = PeriodicExportingMetricReader(metric_exporter)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

logger_provider = LoggerProvider()
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
set_logger_provider(logger_provider)
logging.getLogger("app").addHandler(
    LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
)
```

### 6.2 ❌ INCORRECT: Using Distro API in Low-level Skill
```python
# WRONG - configure_azure_monitor belongs to azure-monitor-opentelemetry distro
from azure.monitor.opentelemetry import configure_azure_monitor
configure_azure_monitor()
```
