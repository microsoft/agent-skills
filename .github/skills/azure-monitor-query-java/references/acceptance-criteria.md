# Azure Monitor Query SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-monitor-query`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/monitor/azure-monitor-query
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

> **Note**: This package is deprecated. Migrate to `azure-monitor-query-logs` and `azure-monitor-query-metrics`.

---

## 1. Correct Import Patterns

### 1.1 Logs Query Client Imports
#### ✅ CORRECT: LogsQueryClient and Builder
```java
import com.azure.monitor.query.LogsQueryClient;
import com.azure.monitor.query.LogsQueryClientBuilder;
import com.azure.monitor.query.LogsQueryAsyncClient;
```
#### ❌ INCORRECT: Wrong Package or Class Names
```java
import com.azure.monitor.LogsQueryClient;  // Wrong package
import com.azure.monitor.query.LogAnalyticsClient;  // Wrong class name
```

### 1.2 Metrics Query Client Imports
#### ✅ CORRECT: MetricsQueryClient and Builder
```java
import com.azure.monitor.query.MetricsQueryClient;
import com.azure.monitor.query.MetricsQueryClientBuilder;
import com.azure.monitor.query.MetricsQueryAsyncClient;
import com.azure.monitor.query.MetricsClient;
import com.azure.monitor.query.MetricsClientBuilder;
```
#### ❌ INCORRECT: Wrong Class Names
```java
import com.azure.monitor.query.MetricQueryClient;  // Wrong name (singular)
import com.azure.monitor.query.AzureMetricsClient;  // Wrong name
```

### 1.3 Model Imports
#### ✅ CORRECT: Query Result Models
```java
import com.azure.monitor.query.models.LogsQueryResult;
import com.azure.monitor.query.models.LogsTableRow;
import com.azure.monitor.query.models.QueryTimeInterval;
import com.azure.monitor.query.models.LogsBatchQuery;
import com.azure.monitor.query.models.LogsBatchQueryResult;
import com.azure.monitor.query.models.LogsBatchQueryResultCollection;
import com.azure.monitor.query.models.LogsQueryOptions;
import com.azure.monitor.query.models.LogsQueryResultStatus;
```

### 1.4 Metrics Model Imports
#### ✅ CORRECT: Metrics Result Models
```java
import com.azure.monitor.query.models.MetricsQueryResult;
import com.azure.monitor.query.models.MetricResult;
import com.azure.monitor.query.models.TimeSeriesElement;
import com.azure.monitor.query.models.MetricValue;
import com.azure.monitor.query.models.MetricsQueryOptions;
import com.azure.monitor.query.models.AggregationType;
```

---

## 2. Client Creation Patterns

### 2.1 LogsQueryClient (Sync)
#### ✅ CORRECT: Using DefaultAzureCredential
```java
import com.azure.identity.DefaultAzureCredentialBuilder;

LogsQueryClient logsClient = new LogsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```
#### ❌ INCORRECT: Missing Credential
```java
LogsQueryClient logsClient = new LogsQueryClientBuilder()
    .buildClient();  // Missing credential
```

### 2.2 LogsQueryAsyncClient
#### ✅ CORRECT: Building Async Client
```java
LogsQueryAsyncClient logsAsyncClient = new LogsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```
#### ❌ INCORRECT: Wrong Build Method
```java
LogsQueryAsyncClient logsAsyncClient = new LogsQueryClientBuilder()
    .credential(credential)
    .buildClient();  // Returns sync client
```

### 2.3 MetricsQueryClient
#### ✅ CORRECT: Metrics Client Creation
```java
MetricsQueryClient metricsClient = new MetricsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### 2.4 Sovereign Cloud Configuration
#### ✅ CORRECT: Custom Endpoint for Sovereign Clouds
```java
// Azure China Cloud - Logs
LogsQueryClient logsClient = new LogsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint("https://api.loganalytics.azure.cn/v1")
    .buildClient();

// Azure China Cloud - Metrics
MetricsQueryClient metricsClient = new MetricsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint("https://management.chinacloudapi.cn")
    .buildClient();
```
#### ❌ INCORRECT: Wrong Endpoint Format
```java
new LogsQueryClientBuilder()
    .endpoint("api.loganalytics.azure.cn")  // Missing https:// and path
    .buildClient();
```

---

## 3. Logs Query Operations

### 3.1 Basic Query
#### ✅ CORRECT: Query with Workspace ID and Time Interval
```java
import java.time.Duration;

LogsQueryResult result = logsClient.queryWorkspace(
    "{workspace-id}",
    "AzureActivity | summarize count() by ResourceGroup | top 10 by count_",
    new QueryTimeInterval(Duration.ofDays(7))
);

for (LogsTableRow row : result.getTable().getRows()) {
    System.out.println(row.getColumnValue("ResourceGroup") + ": " + row.getColumnValue("count_"));
}
```
#### ❌ INCORRECT: Wrong Parameter Order or Missing Time Interval
```java
logsClient.queryWorkspace(
    "AzureActivity | count",
    "{workspace-id}",  // Wrong order
    new QueryTimeInterval(Duration.ofDays(7))
);

logsClient.queryWorkspace("{workspace-id}", "query");  // Missing time interval
```

### 3.2 Query by Resource ID
#### ✅ CORRECT: Using queryResource Method
```java
LogsQueryResult result = logsClient.queryResource(
    "{resource-id}",
    "AzureMetrics | where TimeGenerated > ago(1h)",
    new QueryTimeInterval(Duration.ofDays(1))
);
```
#### ❌ INCORRECT: Using Wrong Method
```java
logsClient.queryWorkspace("{resource-id}", ...);  // Resource ID, not workspace
```

### 3.3 Map Results to Custom Model
#### ✅ CORRECT: Generic Query with Class Mapping
```java
public class ActivityLog {
    private String resourceGroup;
    private String operationName;
    
    public String getResourceGroup() { return resourceGroup; }
    public String getOperationName() { return operationName; }
}

List<ActivityLog> logs = logsClient.queryWorkspace(
    "{workspace-id}",
    "AzureActivity | project ResourceGroup, OperationName | take 100",
    new QueryTimeInterval(Duration.ofDays(2)),
    ActivityLog.class
);
```
#### ❌ INCORRECT: Wrong Column Names in Model
```java
public class ActivityLog {
    private String resource_group;  // Must match query column name exactly
}
```

---

## 4. Batch Query Operations

### 4.1 Creating Batch Query
#### ✅ CORRECT: Using LogsBatchQuery
```java
LogsBatchQuery batchQuery = new LogsBatchQuery();
String q1 = batchQuery.addWorkspaceQuery("{workspace-id}", "AzureActivity | count", new QueryTimeInterval(Duration.ofDays(1)));
String q2 = batchQuery.addWorkspaceQuery("{workspace-id}", "Heartbeat | count", new QueryTimeInterval(Duration.ofDays(1)));
String q3 = batchQuery.addWorkspaceQuery("{workspace-id}", "Perf | count", new QueryTimeInterval(Duration.ofDays(1)));

LogsBatchQueryResultCollection results = logsClient
    .queryBatchWithResponse(batchQuery, Context.NONE)
    .getValue();

LogsBatchQueryResult result1 = results.getResult(q1);
LogsBatchQueryResult result2 = results.getResult(q2);
LogsBatchQueryResult result3 = results.getResult(q3);
```
#### ❌ INCORRECT: Not Capturing Query IDs
```java
batchQuery.addWorkspaceQuery("{workspace-id}", "query1", interval);  // Lost query ID
batchQuery.addWorkspaceQuery("{workspace-id}", "query2", interval);

// Cannot retrieve results without IDs
```

### 4.2 Handling Batch Query Failures
#### ✅ CORRECT: Checking Query Result Status
```java
LogsBatchQueryResult result = results.getResult(queryId);

if (result.getQueryResultStatus() == LogsQueryResultStatus.FAILURE) {
    System.err.println("Query failed: " + result.getError().getMessage());
} else if (result.getQueryResultStatus() == LogsQueryResultStatus.PARTIAL_FAILURE) {
    System.err.println("Partial failure: " + result.getError().getMessage());
    // Still process available data
}
```

---

## 5. Query Options

### 5.1 Setting Server Timeout and Statistics
#### ✅ CORRECT: Using LogsQueryOptions
```java
import com.azure.core.http.rest.Response;

LogsQueryOptions options = new LogsQueryOptions()
    .setServerTimeout(Duration.ofMinutes(10))
    .setIncludeStatistics(true)
    .setIncludeVisualization(true);

Response<LogsQueryResult> response = logsClient.queryWorkspaceWithResponse(
    "{workspace-id}",
    "AzureActivity | summarize count() by bin(TimeGenerated, 1h)",
    new QueryTimeInterval(Duration.ofDays(7)),
    options,
    Context.NONE
);

LogsQueryResult result = response.getValue();
BinaryData statistics = result.getStatistics();
BinaryData visualization = result.getVisualization();
```
#### ❌ INCORRECT: Timeout as Integer
```java
new LogsQueryOptions().setServerTimeout(600);  // Should be Duration, not int
```

### 5.2 Query Multiple Workspaces
#### ✅ CORRECT: Using Additional Workspaces
```java
LogsQueryOptions options = new LogsQueryOptions()
    .setAdditionalWorkspaces(Arrays.asList("{workspace-id-2}", "{workspace-id-3}"));

Response<LogsQueryResult> response = logsClient.queryWorkspaceWithResponse(
    "{workspace-id-1}",
    "AzureActivity | summarize count() by TenantId",
    new QueryTimeInterval(Duration.ofDays(1)),
    options,
    Context.NONE
);
```

---

## 6. Metrics Query Operations

### 6.1 Basic Metrics Query
#### ✅ CORRECT: Query with Resource URI and Metric Names
```java
MetricsQueryResult result = metricsClient.queryResource(
    "{resource-uri}",
    Arrays.asList("SuccessfulCalls", "TotalCalls")
);

for (MetricResult metric : result.getMetrics()) {
    System.out.println("Metric: " + metric.getMetricName());
    for (TimeSeriesElement ts : metric.getTimeSeries()) {
        for (MetricValue value : ts.getValues()) {
            System.out.println(value.getTimeStamp() + ": " + value.getTotal());
        }
    }
}
```
#### ❌ INCORRECT: String Instead of List
```java
metricsClient.queryResource("{resource-uri}", "SuccessfulCalls");  // Should be List
```

### 6.2 Metrics with Aggregations
#### ✅ CORRECT: Using MetricsQueryOptions
```java
Response<MetricsQueryResult> response = metricsClient.queryResourceWithResponse(
    "{resource-id}",
    Arrays.asList("SuccessfulCalls", "TotalCalls"),
    new MetricsQueryOptions()
        .setGranularity(Duration.ofHours(1))
        .setAggregations(Arrays.asList(AggregationType.AVERAGE, AggregationType.COUNT)),
    Context.NONE
);
```
#### ❌ INCORRECT: String Aggregation Types
```java
new MetricsQueryOptions()
    .setAggregations(Arrays.asList("Average", "Count"));  // Should be AggregationType enum
```

### 6.3 Query Multiple Resources
#### ✅ CORRECT: Using MetricsClient for Batch Query
```java
MetricsClient metricsClient = new MetricsClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint("{endpoint}")
    .buildClient();

MetricsQueryResourcesResult result = metricsClient.queryResources(
    Arrays.asList("{resourceId1}", "{resourceId2}"),
    Arrays.asList("{metric1}", "{metric2}"),
    "{metricNamespace}"
);

for (MetricsQueryResult queryResult : result.getMetricsQueryResults()) {
    for (MetricResult metric : queryResult.getMetrics()) {
        System.out.println(metric.getMetricName());
    }
}
```

---

## 7. Response Processing

### 7.1 Processing Log Table Rows
#### ✅ CORRECT: Iterating Table Rows
```java
LogsQueryResult result = logsClient.queryWorkspace(workspaceId, query, interval);

for (LogsTableRow row : result.getTable().getRows()) {
    String resourceGroup = row.getColumnValue("ResourceGroup").toString();
    Long count = (Long) row.getColumnValue("count_");
    System.out.println(resourceGroup + ": " + count);
}
```
#### ❌ INCORRECT: Direct Index Access
```java
// Avoid using index-based access
Object value = row.getRow().get(0);  // Not type-safe
```

### 7.2 Processing Metrics Time Series
#### ✅ CORRECT: Navigating Metrics Hierarchy
```java
for (MetricResult metric : result.getMetrics()) {
    for (TimeSeriesElement ts : metric.getTimeSeries()) {
        System.out.println("Dimensions: " + ts.getMetadata());
        for (MetricValue value : ts.getValues()) {
            System.out.println("  " + value.getTimeStamp() + 
                ": avg=" + value.getAverage() + 
                ", total=" + value.getTotal());
        }
    }
}
```

---

## 8. Error Handling

### 8.1 HTTP Exception Handling
#### ✅ CORRECT: Catching HttpResponseException
```java
import com.azure.core.exception.HttpResponseException;

try {
    LogsQueryResult result = logsClient.queryWorkspace(workspaceId, query, timeInterval);
    
    if (result.getStatus() == LogsQueryResultStatus.PARTIAL_FAILURE) {
        System.err.println("Partial failure: " + result.getError().getMessage());
    }
} catch (HttpResponseException e) {
    System.err.println("Query failed: " + e.getMessage());
    System.err.println("Status: " + e.getResponse().getStatusCode());
}
```
#### ❌ INCORRECT: Not Checking Partial Failure
```java
LogsQueryResult result = logsClient.queryWorkspace(workspaceId, query, interval);
// Missing partial failure check - may have incomplete data
for (LogsTableRow row : result.getTable().getRows()) { ... }
```

---

## 9. Time Interval Patterns

### 9.1 Duration-Based Interval
#### ✅ CORRECT: QueryTimeInterval with Duration
```java
// Last 7 days
new QueryTimeInterval(Duration.ofDays(7))

// Last 24 hours
new QueryTimeInterval(Duration.ofHours(24))

// Last 30 minutes
new QueryTimeInterval(Duration.ofMinutes(30))
```

### 9.2 Explicit Time Range
#### ✅ CORRECT: Start and End Time
```java
OffsetDateTime start = OffsetDateTime.now().minusDays(7);
OffsetDateTime end = OffsetDateTime.now();

new QueryTimeInterval(start, end)
```
#### ❌ INCORRECT: Wrong Time Types
```java
new QueryTimeInterval(LocalDateTime.now().minusDays(7), LocalDateTime.now());  // Should be OffsetDateTime
```

---

## 10. Best Practices

### 10.1 Limit Result Size
#### ✅ CORRECT: Using top/take in Kusto Query
```java
String query = "AzureActivity | top 100 by TimeGenerated";
String query = "AzureActivity | take 1000";
String query = "AzureActivity | project ResourceGroup, OperationName | take 500";
```
#### ❌ INCORRECT: Unbounded Query
```java
String query = "AzureActivity";  // Returns all rows - may timeout or OOM
```

### 10.2 Handle Migration Notice
#### ✅ CORRECT: Plan for Migration
```java
// Note: azure-monitor-query is deprecated
// Migrate to:
// - azure-monitor-query-logs for Log Analytics
// - azure-monitor-query-metrics for Metrics
```
