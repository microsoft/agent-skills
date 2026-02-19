# Azure Monitor Query SDK for Java - Examples

Comprehensive code examples for the Azure Monitor Query SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Querying Log Analytics](#querying-log-analytics)
- [Querying Metrics](#querying-metrics)
- [Batch Queries](#batch-queries)
- [Handling Query Results](#handling-query-results)
- [Time Ranges](#time-ranges)
- [Async Client Patterns](#async-client-patterns)
- [Error Handling](#error-handling)

## Maven Dependency

```xml
<!-- Using Azure SDK BOM (recommended) -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-sdk-bom</artifactId>
            <version>{bom_version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-monitor-query</artifactId>
    </dependency>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-identity</artifactId>
    </dependency>
</dependencies>

<!-- Or direct dependencies -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-query</artifactId>
    <version>1.5.9</version>
</dependency>
```

## Client Creation

### LogsQueryClient

```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.monitor.query.LogsQueryClient;
import com.azure.monitor.query.LogsQueryClientBuilder;

LogsQueryClient logsQueryClient = new LogsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### MetricsQueryClient

```java
import com.azure.monitor.query.MetricsQueryClient;
import com.azure.monitor.query.MetricsQueryClientBuilder;

MetricsQueryClient metricsQueryClient = new MetricsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### For Sovereign Clouds

```java
LogsQueryClient logsQueryClient = new LogsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint("https://api.loganalytics.azure.cn/v1")
    .buildClient();
```

## Querying Log Analytics

### Query Workspace

```java
import com.azure.monitor.query.models.LogsQueryResult;
import com.azure.monitor.query.models.LogsTableRow;
import com.azure.monitor.query.models.QueryTimeInterval;
import java.time.Duration;

LogsQueryResult result = logsQueryClient.queryWorkspace(
    "{workspace-id}",
    "AzureActivity | top 10 by TimeGenerated",
    new QueryTimeInterval(Duration.ofDays(2))
);

for (LogsTableRow row : result.getTable().getRows()) {
    System.out.println(
        row.getColumnValue("OperationName") + " " + 
        row.getColumnValue("ResourceGroup")
    );
}
```

### Query by Resource ID

```java
LogsQueryResult result = logsQueryClient.queryResource(
    "{resource-id}",  // Full Azure resource ID
    "AzureActivity | top 10 by TimeGenerated",
    new QueryTimeInterval(Duration.ofDays(2))
);
```

### Query with Options

```java
import com.azure.monitor.query.models.LogsQueryOptions;

LogsQueryResult result = logsQueryClient.queryWorkspace(
    "{workspace-id}",
    "AzureActivity | top 10 by TimeGenerated",
    new QueryTimeInterval(Duration.ofDays(2)),
    new LogsQueryOptions()
        .setServerTimeout(Duration.ofMinutes(2))
        .setIncludeStatistics(true)
        .setIncludeVisualization(true)
);
```

## Querying Metrics

### Basic Metrics Query

```java
import com.azure.monitor.query.models.MetricResult;
import com.azure.monitor.query.models.MetricValue;
import com.azure.monitor.query.models.MetricsQueryResult;
import com.azure.monitor.query.models.TimeSeriesElement;
import java.util.Arrays;

MetricsQueryResult result = metricsQueryClient.queryResource(
    "{resource-uri}",
    Arrays.asList("SuccessfulCalls", "TotalCalls")
);

for (MetricResult metric : result.getMetrics()) {
    System.out.println("Metric: " + metric.getMetricName());
    for (TimeSeriesElement ts : metric.getTimeSeries()) {
        System.out.println("Dimensions: " + ts.getMetadata());
        for (MetricValue value : ts.getValues()) {
            System.out.println(value.getTimeStamp() + ": " + value.getTotal());
        }
    }
}
```

### With Aggregations and Granularity

```java
import com.azure.core.http.rest.Response;
import com.azure.core.util.Context;
import com.azure.monitor.query.models.AggregationType;
import com.azure.monitor.query.models.MetricsQueryOptions;

Response<MetricsQueryResult> response = metricsQueryClient.queryResourceWithResponse(
    "{resource-id}",
    Arrays.asList("SuccessfulCalls", "TotalCalls"),
    new MetricsQueryOptions()
        .setGranularity(Duration.ofHours(1))
        .setAggregations(Arrays.asList(
            AggregationType.AVERAGE, 
            AggregationType.COUNT
        )),
    Context.NONE
);

MetricsQueryResult result = response.getValue();
```

## Batch Queries

```java
import com.azure.monitor.query.models.LogsBatchQuery;
import com.azure.monitor.query.models.LogsBatchQueryResult;
import com.azure.monitor.query.models.LogsBatchQueryResultCollection;
import com.azure.monitor.query.models.LogsQueryResultStatus;

LogsBatchQuery batchQuery = new LogsBatchQuery();
String q1 = batchQuery.addWorkspaceQuery("{workspace-id}", "{query-1}", 
    new QueryTimeInterval(Duration.ofDays(2)));
String q2 = batchQuery.addWorkspaceQuery("{workspace-id}", "{query-2}", 
    new QueryTimeInterval(Duration.ofDays(30)));
String q3 = batchQuery.addWorkspaceQuery("{workspace-id}", "{query-3}", 
    new QueryTimeInterval(Duration.ofDays(10)));

LogsBatchQueryResultCollection results = logsQueryClient
    .queryBatchWithResponse(batchQuery, Context.NONE).getValue();

// Process query 1 - iterate rows
LogsBatchQueryResult result1 = results.getResult(q1);
for (LogsTableRow row : result1.getTable().getRows()) {
    System.out.println(row.getColumnValue("OperationName"));
}

// Process query 2 - map to model
List<CustomModel> models = results.getResult(q2, CustomModel.class);

// Check query 3 for failures
LogsBatchQueryResult result3 = results.getResult(q3);
if (result3.getQueryResultStatus() == LogsQueryResultStatus.FAILURE) {
    System.out.println("Error: " + result3.getError().getMessage());
}
```

## Handling Query Results

### Response Structure

```
LogsQueryResult
├── statistics
├── visualization
├── error
└── tables (List<LogsTable>)
    └── LogsTable
        ├── name
        ├── columns (List<LogsTableColumn>)
        │   ├── name
        │   └── type
        └── rows (List<LogsTableRow>)
            └── LogsTableRow
                └── getColumnValue(name)
```

### Iterate Tables and Rows

```java
import com.azure.monitor.query.models.LogsTable;
import com.azure.monitor.query.models.LogsTableColumn;
import com.azure.monitor.query.models.LogsTableRow;

LogsQueryResult result = logsQueryClient.queryWorkspace(...);
LogsTable table = result.getTable();

// Print columns
System.out.println("Columns:");
for (LogsTableColumn col : table.getColumns()) {
    System.out.println("  " + col.getName() + " (" + col.getType() + ")");
}

// Print rows
System.out.println("Rows:");
for (LogsTableRow row : table.getRows()) {
    Object operationName = row.getColumnValue("OperationName");
    Object resourceGroup = row.getColumnValue("ResourceGroup");
    System.out.println(operationName + " - " + resourceGroup);
}
```

### Map to Custom Model

```java
// Define model
public class CustomLogModel {
    private String resourceGroup;
    private String operationName;

    public String getResourceGroup() { return resourceGroup; }
    public String getOperationName() { return operationName; }
}

// Query and map
List<CustomLogModel> models = logsQueryClient.queryWorkspace(
    "{workspace-id}",
    "{kusto-query}",
    new QueryTimeInterval(Duration.ofDays(2)),
    CustomLogModel.class
);

for (CustomLogModel model : models) {
    System.out.println(model.getOperationName());
}
```

## Time Ranges

### Using Duration

```java
QueryTimeInterval last2Days = new QueryTimeInterval(Duration.ofDays(2));
QueryTimeInterval last1Hour = new QueryTimeInterval(Duration.ofHours(1));
QueryTimeInterval last30Min = new QueryTimeInterval(Duration.ofMinutes(30));
```

### Predefined Constants

```java
QueryTimeInterval lastHour = QueryTimeInterval.LAST_1_HOUR;
QueryTimeInterval last7Days = QueryTimeInterval.LAST_7_DAYS;
```

### Absolute Time Range

```java
import java.time.OffsetDateTime;

OffsetDateTime start = OffsetDateTime.now().minusDays(7);
OffsetDateTime end = OffsetDateTime.now();
QueryTimeInterval absolute = new QueryTimeInterval(start, end);
```

## Async Client Patterns

### Create Async Clients

```java
import com.azure.monitor.query.LogsQueryAsyncClient;
import com.azure.monitor.query.MetricsQueryAsyncClient;

LogsQueryAsyncClient asyncLogsClient = new LogsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();

MetricsQueryAsyncClient asyncMetricsClient = new MetricsQueryClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();
```

### Async Logs Query

```java
asyncLogsClient.queryWorkspace(
    "{workspace-id}",
    "AzureActivity | top 10 by TimeGenerated",
    new QueryTimeInterval(Duration.ofDays(2))
)
.subscribe(
    result -> {
        for (LogsTableRow row : result.getTable().getRows()) {
            System.out.println(row.getColumnValue("OperationName"));
        }
    },
    error -> System.err.println("Error: " + error.getMessage())
);
```

### Async Metrics Query

```java
asyncMetricsClient.queryResource(
    "{resource-id}",
    Arrays.asList("SuccessfulCalls")
)
.subscribe(
    result -> {
        for (MetricResult metric : result.getMetrics()) {
            System.out.println("Metric: " + metric.getMetricName());
        }
    },
    error -> System.err.println("Error: " + error.getMessage())
);
```

## Error Handling

### Sync Error Handling

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.monitor.query.models.LogsQueryResultStatus;

try {
    LogsQueryResult result = logsQueryClient.queryWorkspace(...);
    
    // Check for partial errors
    if (result.getQueryResultStatus() == LogsQueryResultStatus.PARTIAL_FAILURE) {
        System.out.println("Warning: " + result.getError().getMessage());
    }
} catch (HttpResponseException e) {
    System.err.println("HTTP error: " + e.getResponse().getStatusCode());
    System.err.println("Message: " + e.getMessage());
} catch (Exception e) {
    System.err.println("Error: " + e.getMessage());
}
```

### Async Error Handling

```java
asyncLogsClient.queryWorkspace(...)
    .subscribe(
        result -> {
            if (result.getQueryResultStatus() == LogsQueryResultStatus.FAILURE) {
                System.err.println("Query failed: " + result.getError().getMessage());
            } else {
                // Process results
            }
        },
        error -> {
            if (error instanceof HttpResponseException) {
                HttpResponseException httpError = (HttpResponseException) error;
                System.err.println("HTTP: " + httpError.getResponse().getStatusCode());
            } else {
                System.err.println("Error: " + error.getMessage());
            }
        }
    );
```
