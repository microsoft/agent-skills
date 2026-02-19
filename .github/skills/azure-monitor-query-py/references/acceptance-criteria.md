# Azure Monitor Query SDK Acceptance Criteria

**SDK**: `azure-monitor-query`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Sync Client Imports
```python
from azure.monitor.query import LogsQueryClient, MetricsQueryClient
from azure.identity import DefaultAzureCredential
```

### 1.2 ✅ CORRECT: Async Client Imports
```python
from azure.monitor.query.aio import LogsQueryClient, MetricsQueryClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.3 ✅ CORRECT: Supporting Types
```python
from azure.monitor.query import LogsBatchQuery, LogsQueryStatus, MetricAggregationType
from datetime import datetime, timedelta, timezone
```

### 1.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong modules or non-existent classes
```python
# WRONG - Metrics client for this skill is MetricsQueryClient
from azure.monitor.querymetrics import MetricsClient

# WRONG - Async client class names are not suffixed with Async
from azure.monitor.query import LogsQueryClientAsync

# WRONG - Mixing async client with sync credential
from azure.monitor.query.aio import LogsQueryClient
from azure.identity import DefaultAzureCredential
```

---

## 2. LogsQueryClient Usage

### 2.1 ✅ CORRECT: Query Workspace with Relative Timespan
```python
from datetime import timedelta

client = LogsQueryClient(DefaultAzureCredential())

response = client.query_workspace(
    workspace_id=os.environ["AZURE_LOG_ANALYTICS_WORKSPACE_ID"],
    query="AppRequests | take 10",
    timespan=timedelta(hours=1),
)

for table in response.tables:
    for row in table.rows:
        print(row)
```

### 2.2 ✅ CORRECT: Batch Query
```python
from datetime import timedelta
from azure.monitor.query import LogsBatchQuery

queries = [
    LogsBatchQuery(
        workspace_id=os.environ["AZURE_LOG_ANALYTICS_WORKSPACE_ID"],
        query="AppRequests | take 5",
        timespan=timedelta(hours=1),
    ),
    LogsBatchQuery(
        workspace_id=os.environ["AZURE_LOG_ANALYTICS_WORKSPACE_ID"],
        query="AppExceptions | take 5",
        timespan=timedelta(hours=1),
    ),
]

responses = client.query_batch(queries)
```

### 2.3 ✅ CORRECT: Handle Partial Results
```python
from azure.monitor.query import LogsQueryStatus
from datetime import timedelta

response = client.query_workspace(
    workspace_id=workspace_id,
    query="AppRequests | take 10",
    timespan=timedelta(hours=24),
)

if response.status == LogsQueryStatus.PARTIAL:
    print(f"Partial results: {response.partial_error}")
elif response.status == LogsQueryStatus.FAILURE:
    print(f"Query failed: {response.partial_error}")
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Invalid timespan type
```python
# WRONG - timespan must be timedelta or (start_datetime, end_datetime)
client.query_workspace(
    workspace_id=workspace_id,
    query="AppRequests | take 10",
    timespan="1h",
)
```

---

## 3. MetricsQueryClient Usage

### 3.1 ✅ CORRECT: Query Resource Metrics
```python
from datetime import timedelta

metrics_client = MetricsQueryClient(DefaultAzureCredential())

response = metrics_client.query_resource(
    resource_uri=os.environ["AZURE_METRICS_RESOURCE_URI"],
    metric_names=["Percentage CPU", "Network In Total"],
    timespan=timedelta(hours=1),
    granularity=timedelta(minutes=5),
)

for metric in response.metrics:
    for time_series in metric.timeseries:
        for data in time_series.data:
            print(data.timestamp, data.average)
```

### 3.2 ✅ CORRECT: Aggregations and Dimension Filters
```python
from datetime import timedelta
from azure.monitor.query import MetricAggregationType

response = metrics_client.query_resource(
    resource_uri=resource_uri,
    metric_names=["Requests"],
    timespan=timedelta(hours=1),
    aggregations=[
        MetricAggregationType.AVERAGE,
        MetricAggregationType.MAXIMUM,
        MetricAggregationType.MINIMUM,
        MetricAggregationType.COUNT,
    ],
    filter="ApiName eq 'GetBlob'",
)
```

### 3.3 ✅ CORRECT: List Definitions and Namespaces
```python
definitions = metrics_client.list_metric_definitions(resource_uri)
namespaces = metrics_client.list_metric_namespaces(resource_uri)
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Metrics client used for logs
```python
# WRONG - Logs queries use LogsQueryClient.query_workspace
metrics_client.query_workspace(
    workspace_id=workspace_id,
    query="AppRequests | take 10",
    timespan=timedelta(hours=1),
)
```

---

## 4. Kusto Query Patterns

### 4.1 ✅ CORRECT: Kusto Query String with Pipes
```python
query = """
AppRequests
| where TimeGenerated > ago(1h)
| summarize count() by ResultCode
| order by count_ desc
"""
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: SQL-like syntax (not Kusto)
```python
# WRONG - Kusto does not use SELECT/FROM syntax
query = "SELECT * FROM AppRequests"
```

---

## 5. Timespan Usage

### 5.1 ✅ CORRECT: Relative Timespan
```python
from datetime import timedelta

timespan = timedelta(hours=1)
```

### 5.2 ✅ CORRECT: Absolute Time Range
```python
from datetime import datetime, timezone

timespan = (
    datetime(2024, 1, 1, tzinfo=timezone.utc),
    datetime(2024, 1, 2, tzinfo=timezone.utc),
)
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Naive datetime
```python
# WRONG - datetimes should include timezone information
timespan = (datetime(2024, 1, 1), datetime(2024, 1, 2))
```

---

## 6. Async Variants

### 6.1 ✅ CORRECT: Async Logs Query
```python
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.query.aio import LogsQueryClient
from datetime import timedelta

async def query_logs() -> None:
    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)

    response = await client.query_workspace(
        workspace_id=workspace_id,
        query="AppRequests | take 10",
        timespan=timedelta(hours=1),
    )

    await client.close()
    await credential.close()
```

### 6.2 ✅ CORRECT: Async Metrics Query
```python
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.query.aio import MetricsQueryClient
from datetime import timedelta

async def query_metrics() -> None:
    credential = DefaultAzureCredential()
    client = MetricsQueryClient(credential)

    response = await client.query_resource(
        resource_uri=resource_uri,
        metric_names=["Requests"],
        timespan=timedelta(hours=1),
    )

    await client.close()
    await credential.close()
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing await on async call
```python
# WRONG - query_workspace is async in aio client and must be awaited
response = client.query_workspace(workspace_id=workspace_id, query=query, timespan=timedelta(hours=1))
```
