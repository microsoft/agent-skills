# Azure Monitor OpenTelemetry Distro for Python Acceptance Criteria

**SDK**: `azure-monitor-opentelemetry`
**Repository**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Imports

### 1.1 ✅ Correct: Core Setup
```python
from azure.monitor.opentelemetry import configure_azure_monitor
```

### 1.2 ✅ Correct: Custom Spans & Metrics
```python
from opentelemetry import trace, metrics
```

### 1.3 ✅ Correct: Resource for Cloud Role Name
```python
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
```

### 1.4 ❌ Incorrect: Importing from exporter package
```python
# WRONG - exporter package is different SDK
from azure.monitor.opentelemetry.exporter import configure_azure_monitor
```

### 1.5 ❌ Incorrect: Non-existent class import
```python
# WRONG - no AzureMonitorTraceExporter in this package
from azure.monitor.opentelemetry import AzureMonitorTraceExporter
```

---

## 2. configure_azure_monitor Usage

### 2.1 ✅ Correct: One-line setup
```python
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()
```

### 2.2 ✅ Correct: Explicit configuration options
```python
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    sampling_ratio=0.1,
    enable_live_metrics=True,
)
```

### 2.3 ❌ Incorrect: Wrong parameter name
```python
# WRONG - parameter is connection_string
configure_azure_monitor(connectionString="InstrumentationKey=...")
```

---

## 3. Connection String Setup

### 3.1 ✅ Correct: Environment variable
```python
import os
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
)
```

### 3.2 ✅ Correct: Full connection string literal
```python
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string="InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/",
)
```

### 3.3 ❌ Incorrect: Instrumentation key only
```python
# WRONG - connection string must include IngestionEndpoint
configure_azure_monitor(connection_string="InstrumentationKey=xxx")
```

---

## 4. Auto-Instrumentation

### 4.1 ✅ Correct: Flask auto-instrumentation
```python
from flask import Flask
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"
```

### 4.2 ✅ Correct: FastAPI auto-instrumentation
```python
from fastapi import FastAPI
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### 4.3 ✅ Correct: Limit instrumentations
```python
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    instrumentations=["flask", "requests"],
)
```

### 4.4 ❌ Incorrect: Wrong instrumentations type
```python
# WRONG - instrumentations must be a list
configure_azure_monitor(instrumentations="flask")
```

---

## 5. Custom Spans, Metrics, and Logs

### 5.1 ✅ Correct: Custom span
```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

configure_azure_monitor()

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("my-operation") as span:
    span.set_attribute("custom.attribute", "value")
```

### 5.2 ✅ Correct: Custom metric
```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import metrics

configure_azure_monitor()

meter = metrics.get_meter(__name__)
counter = meter.create_counter("my_counter")

counter.add(1, {"dimension": "value"})
```

### 5.3 ✅ Correct: Custom logs
```python
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("This will appear in Application Insights")
logger.error("Errors are captured too", exc_info=True)
```

### 5.4 ❌ Incorrect: Using OpenCensus API
```python
# WRONG - use OpenTelemetry APIs instead of OpenCensus
from opencensus.trace.tracer import Tracer
```
