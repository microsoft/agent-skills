# Azure Monitor Ingestion SDK Acceptance Criteria

**SDK**: `azure-monitor-ingestion`
**Repository**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-ingestion
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Client
```python
from azure.monitor.ingestion import LogsIngestionClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Client
```python
from azure.monitor.ingestion.aio import LogsIngestionClient
from azure.identity.aio import DefaultAzureCredential
```

#### ✅ CORRECT: HttpResponseError Handling
```python
from azure.core.exceptions import HttpResponseError
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module path
```python
# WRONG - LogsIngestionClient is not under .models
from azure.monitor.ingestion.models import LogsIngestionClient
```

#### ❌ INCORRECT: Mixing sync/async credentials
```python
# WRONG - using sync credential with async client
from azure.monitor.ingestion.aio import LogsIngestionClient
from azure.identity import DefaultAzureCredential

client = LogsIngestionClient(endpoint, DefaultAzureCredential())
```

---

## 2. LogsIngestionClient Creation Patterns

### 2.1 ✅ CORRECT: Sync Client Creation
```python
import os
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient

endpoint = os.environ["AZURE_DCE_ENDPOINT"]
credential = DefaultAzureCredential()

client = LogsIngestionClient(endpoint=endpoint, credential=credential)
```

### 2.2 ✅ CORRECT: Async Client with Context Manager
```python
import os
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.ingestion.aio import LogsIngestionClient

endpoint = os.environ["AZURE_DCE_ENDPOINT"]

async with LogsIngestionClient(endpoint=endpoint, credential=DefaultAzureCredential()) as client:
    await client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
```

### 2.3 ✅ CORRECT: Sovereign Cloud Scopes
```python
from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient

credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
client = LogsIngestionClient(
    endpoint="https://example.ingest.monitor.azure.us",
    credential=credential,
    credential_scopes=["https://monitor.azure.us/.default"],
)
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter name
```python
# WRONG - parameter is 'endpoint'
client = LogsIngestionClient(data_collection_endpoint=endpoint, credential=credential)
```

#### ❌ INCORRECT: Missing credential
```python
# WRONG - credential is required
client = LogsIngestionClient(endpoint=endpoint)
```

---

## 3. Data Collection Rules (DCR)

### 3.1 ✅ CORRECT: DCR Rule ID and Stream Name
```python
import os

rule_id = os.environ["AZURE_DCR_RULE_ID"]
stream_name = os.environ["AZURE_DCR_STREAM_NAME"]

client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
```

### 3.2 ✅ CORRECT: Alternate Environment Names
```python
import os

rule_id = os.environ["LOGS_DCR_RULE_ID"]
stream_name = os.environ["LOGS_DCR_STREAM_NAME"]

client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using workspace ID instead of DCR rule ID
```python
# WRONG - rule_id must be a DCR immutable ID
rule_id = os.environ["LOG_ANALYTICS_WORKSPACE_ID"]
client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
```

---

## 4. Data Collection Endpoints (DCE)

### 4.1 ✅ CORRECT: DCE Endpoint Format
```python
import os

endpoint = os.environ["AZURE_DCE_ENDPOINT"]
client = LogsIngestionClient(endpoint=endpoint, credential=DefaultAzureCredential())
```

### 4.2 ✅ CORRECT: Public Azure Ingestion URL
```python
endpoint = "https://my-dce.westus2.ingest.monitor.azure.com"
client = LogsIngestionClient(endpoint=endpoint, credential=DefaultAzureCredential())
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using legacy ODS ingestion endpoint
```python
# WRONG - legacy Data Collector API endpoint
endpoint = "https://workspace-id.ods.opinsights.azure.com"
client = LogsIngestionClient(endpoint=endpoint, credential=DefaultAzureCredential())
```

---

## 5. Uploading Custom Logs

### 5.1 ✅ CORRECT: Basic Upload
```python
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient

client = LogsIngestionClient(
    endpoint=os.environ["AZURE_DCE_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

logs = [
    {"TimeGenerated": "2024-01-15T10:00:00Z", "Computer": "server1", "Message": "Started"},
    {"TimeGenerated": "2024-01-15T10:01:00Z", "Computer": "server2", "Message": "Processed"},
]

client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
```

### 5.2 ✅ CORRECT: Upload with Error Handling
```python
from azure.core.exceptions import HttpResponseError

try:
    client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
except HttpResponseError as exc:
    print(f"Upload failed: {exc}")
```

### 5.3 ✅ CORRECT: Upload with Custom Error Callback
```python
failed_logs = []

def on_error(error):
    failed_logs.extend(error.failed_logs)

client.upload(
    rule_id=rule_id,
    stream_name=stream_name,
    logs=logs,
    on_error=on_error,
)
```

### 5.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Passing a JSON string directly
```python
# WRONG - logs must be a list of dicts
logs = '[{"TimeGenerated": "2024-01-15T10:00:00Z"}]'
client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
```

#### ❌ INCORRECT: Missing rule_id or stream_name
```python
# WRONG - both rule_id and stream_name are required
client.upload(logs=logs)
```
