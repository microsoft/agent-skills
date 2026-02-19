# Azure Monitor Query SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-monitor-query`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/monitor/azure-monitor-query
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## ⚠️ DEPRECATION NOTICE

This package is deprecated in favor of:
- `azure-monitor-query-logs` for Log Analytics queries
- `azure-monitor-query-metrics` for metrics queries

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Query Clients
```java
import com.azure.monitor.query.LogsQueryClient;
import com.azure.monitor.query.LogsQueryClientBuilder;
import com.azure.monitor.query.LogsQueryAsyncClient;
import com.azure.monitor.query.MetricsQueryClient;
import com.azure.monitor.query.MetricsQueryClientBuilder;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
```

### 1.2 Model Imports

#### ✅ CORRECT: Query Models
```java
import com.azure.monitor.query.models.LogsQueryResult;
import com.azure.monitor.query.models.LogsTableRow;
import com.azure.monitor.query.models.QueryTimeInterval;
import com.azure.monitor.query.models.MetricsQueryResult;
import com.azure.monitor.query.models.MetricResult;
import com.azure.monitor.query.models.LogsBatchQuery;
import com.azure.monitor.query.models.LogsQueryOptions;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: LogsQueryClient
```java
LogsQueryClient logsClient = new LogsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.2 ✅ CORRECT: MetricsQueryClient
```java
MetricsQueryClient metricsClient = new MetricsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

---

## 3. Logs Query Operations

### 3.1 ✅ CORRECT: Basic Query
```java
String workspaceId = System.getenv("LOG_ANALYTICS_WORKSPACE_ID");

LogsQueryResult result = logsClient.queryWorkspace(
    workspaceId,
    "AzureActivity | summarize count() by ResourceGroup | top 10 by count_",
    new QueryTimeInterval(Duration.ofDays(7))
);

for (LogsTableRow row : result.getTable().getRows()) {
    System.out.println(row.getColumnValue("ResourceGroup"));
}
```

### 3.2 ✅ CORRECT: Query with Model Mapping
```java
List<ActivityLog> logs = logsClient.queryWorkspace(
    workspaceId,
    "AzureActivity | project ResourceGroup, OperationName | take 100",
    new QueryTimeInterval(Duration.ofDays(2)),
    ActivityLog.class
);
```

### 3.3 ✅ CORRECT: Batch Query
```java
LogsBatchQuery batchQuery = new LogsBatchQuery();
String q1 = batchQuery.addWorkspaceQuery(workspaceId, "AzureActivity | count", new QueryTimeInterval(Duration.ofDays(1)));
String q2 = batchQuery.addWorkspaceQuery(workspaceId, "Heartbeat | count", new QueryTimeInterval(Duration.ofDays(1)));

LogsBatchQueryResultCollection results = logsClient
    .queryBatchWithResponse(batchQuery, Context.NONE)
    .getValue();

LogsBatchQueryResult result1 = results.getResult(q1);
```

---

## 4. Metrics Query Operations

### 4.1 ✅ CORRECT: Basic Metrics Query
```java
String resourceId = System.getenv("AZURE_RESOURCE_ID");

MetricsQueryResult result = metricsClient.queryResource(
    resourceId,
    Arrays.asList("SuccessfulCalls", "TotalCalls")
);

for (MetricResult metric : result.getMetrics()) {
    System.out.println("Metric: " + metric.getMetricName());
}
```

---

## 5. Error Handling

### 5.1 ✅ CORRECT: Check Query Status
```java
import com.azure.monitor.query.models.LogsQueryResultStatus;

LogsQueryResult result = logsClient.queryWorkspace(workspaceId, query, timeInterval);

if (result.getStatus() == LogsQueryResultStatus.PARTIAL_FAILURE) {
    System.err.println("Partial failure: " + result.getError().getMessage());
}
```

### 5.2 ✅ CORRECT: HTTP Exception Handling
```java
import com.azure.core.exception.HttpResponseException;

try {
    logsClient.queryWorkspace(workspaceId, query, timeInterval);
} catch (HttpResponseException e) {
    System.err.println("Query failed: " + e.getMessage());
}
```

---

## 6. Best Practices Checklist

- [ ] Use batch queries to combine multiple queries
- [ ] Set appropriate timeouts for long queries
- [ ] Limit result size with `top` or `take`
- [ ] Use `project` to select only needed columns
- [ ] Handle PARTIAL_FAILURE results gracefully
- [ ] Plan migration to `azure-monitor-query-logs` and `azure-monitor-query-metrics`
