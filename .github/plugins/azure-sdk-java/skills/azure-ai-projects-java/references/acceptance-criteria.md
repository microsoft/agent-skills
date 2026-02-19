# Azure AI Projects SDK for Java Acceptance Criteria

**SDK**: `com.azure:azure-ai-projects`
**Repository**: https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-projects
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Builder and Clients

#### ✅ CORRECT: Sync Clients
```java
import com.azure.ai.projects.AIProjectClientBuilder;
import com.azure.ai.projects.ConnectionsClient;
import com.azure.ai.projects.DatasetsClient;
import com.azure.ai.projects.DeploymentsClient;
import com.azure.ai.projects.IndexesClient;
import com.azure.ai.projects.EvaluationsClient;
import com.azure.ai.projects.EvaluatorsClient;
import com.azure.ai.projects.SchedulesClient;
import com.azure.ai.projects.InsightsClient;
import com.azure.ai.projects.RedTeamsClient;
```

#### ✅ CORRECT: Async Clients
```java
import com.azure.ai.projects.ConnectionsAsyncClient;
import com.azure.ai.projects.DatasetsAsyncClient;
import com.azure.ai.projects.DeploymentsAsyncClient;
import com.azure.ai.projects.IndexesAsyncClient;
import com.azure.ai.projects.EvaluationsAsyncClient;
```

#### ✅ CORRECT: Authentication
```java
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

### 1.2 Model Imports

#### ✅ CORRECT: Connection Models
```java
import com.azure.ai.projects.models.Connection;
import com.azure.ai.projects.models.ConnectionType;
```

#### ✅ CORRECT: Dataset Models
```java
import com.azure.ai.projects.models.DatasetVersion;
import com.azure.ai.projects.models.FileDatasetVersion;
```

#### ✅ CORRECT: Deployment Models
```java
import com.azure.ai.projects.models.Deployment;
```

#### ✅ CORRECT: Index Models
```java
import com.azure.ai.projects.models.Index;
import com.azure.ai.projects.models.AzureAISearchIndex;
```

#### ✅ CORRECT: Pagination
```java
import com.azure.core.http.rest.PagedIterable;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong import paths
```java
// WRONG - AIProjectClient doesn't exist (use AIProjectClientBuilder)
import com.azure.ai.projects.AIProjectClient;

// WRONG - Models in wrong location
import com.azure.ai.projects.Connection;
import com.azure.ai.projects.Dataset;

// WRONG - Using non-existent classes
import com.azure.ai.projects.ProjectClient;
import com.azure.ai.projects.models.AIProject;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Builder Pattern with DefaultAzureCredential
```java
String endpoint = System.getenv("PROJECT_ENDPOINT");

AIProjectClientBuilder builder = new AIProjectClientBuilder()
    .endpoint(endpoint)
    .credential(new DefaultAzureCredentialBuilder().build());

ConnectionsClient connectionsClient = builder.buildConnectionsClient();
DatasetsClient datasetsClient = builder.buildDatasetsClient();
DeploymentsClient deploymentsClient = builder.buildDeploymentsClient();
IndexesClient indexesClient = builder.buildIndexesClient();
EvaluationsClient evaluationsClient = builder.buildEvaluationsClient();
```

### 2.2 ✅ CORRECT: Building Async Clients
```java
ConnectionsAsyncClient connectionsAsyncClient = builder.buildConnectionsAsyncClient();
DatasetsAsyncClient datasetsAsyncClient = builder.buildDatasetsAsyncClient();
DeploymentsAsyncClient deploymentsAsyncClient = builder.buildDeploymentsAsyncClient();
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using wrong builder methods
```java
// WRONG - buildClient() doesn't exist, use specific sub-client methods
AIProjectClientBuilder builder = new AIProjectClientBuilder();
var client = builder.buildClient();

// WRONG - Hardcoded endpoint
AIProjectClientBuilder builder = new AIProjectClientBuilder()
    .endpoint("https://myresource.services.ai.azure.com/api/projects/myproject")
    .credential(credential);
```

---

## 3. Connection Operations

### 3.1 ✅ CORRECT: List All Connections
```java
PagedIterable<Connection> connections = connectionsClient.listConnections();
for (Connection connection : connections) {
    System.out.println("Name: " + connection.getName());
    System.out.println("Type: " + connection.getType());
    System.out.println("Credential Type: " + connection.getCredentials().getType());
}
```

### 3.2 ✅ CORRECT: List Connections with Filter
```java
// Filter by type
Iterable<Connection> azureOpenAIConnections = 
    connectionsClient.listConnections(ConnectionType.AZURE_OPEN_AI, null);

// Filter by default connections
Iterable<Connection> defaultConnections = 
    connectionsClient.listConnections(null, true);
```

### 3.3 ✅ CORRECT: Get Connection
```java
// Without credentials
Connection connection = connectionsClient.getConnection("my-connection");

// With credentials
Connection connectionWithCreds = connectionsClient.getConnectionWithCredentials("my-connection");
System.out.println("Credentials: " + connectionWithCreds.getCredentials().getType());
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using wrong method names
```java
// WRONG - method is listConnections, not list
connectionsClient.list();

// WRONG - connection_name parameter name
connectionsClient.getConnection(connectionName: "my-connection");

// WRONG - Using string for connection type
connectionsClient.listConnections("AzureOpenAI", null);  // Should use enum
```

---

## 4. Deployment Operations

### 4.1 ✅ CORRECT: List Deployments
```java
PagedIterable<Deployment> deployments = deploymentsClient.list();
for (Deployment deployment : deployments) {
    System.out.println("Name: " + deployment.getName());
    System.out.println("Type: " + deployment.getType().getValue());
}
```

### 4.2 ✅ CORRECT: Get Deployment
```java
Deployment deployment = deploymentsClient.get("gpt-4o");
System.out.println("Name: " + deployment.getName());
System.out.println("Type: " + deployment.getType().getValue());
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong method names
```java
// WRONG - method is list, not listDeployments
deploymentsClient.listDeployments();

// WRONG - method is get, not getDeployment
deploymentsClient.getDeployment("gpt-4o");
```

---

## 5. Dataset Operations

### 5.1 ✅ CORRECT: Create Dataset with File Upload
```java
import java.nio.file.Path;

String datasetName = "my-dataset";
String datasetVersion = "1.0";
Path filePath = Path.of("data/product_info.md");

FileDatasetVersion createdDataset = datasetsClient.createDatasetWithFile(
    datasetName,
    datasetVersion,
    filePath
);

System.out.println("Created dataset: " + createdDataset.getId());
```

### 5.2 ✅ CORRECT: Create or Update Dataset with URI
```java
FileDatasetVersion fileDataset = new FileDatasetVersion()
    .setDataUri("https://example.com/data.txt")
    .setDescription("Sample dataset");

FileDatasetVersion created = (FileDatasetVersion) datasetsClient.createOrUpdateVersion(
    datasetName,
    datasetVersion,
    fileDataset
);
```

### 5.3 ✅ CORRECT: List Datasets
```java
// List latest versions of all datasets
datasetsClient.listLatest().forEach(dataset -> {
    System.out.println("Name: " + dataset.getName());
    System.out.println("Version: " + dataset.getVersion());
});

// List all versions of a specific dataset
datasetsClient.listVersions("my-dataset").forEach(version -> {
    System.out.println("Version: " + version.getVersion());
});
```

### 5.4 ✅ CORRECT: Get and Delete Dataset
```java
DatasetVersion dataset = datasetsClient.getDatasetVersion("my-dataset", "1.0");
System.out.println("Type: " + dataset.getType());

datasetsClient.deleteVersion("my-dataset", "1.0");
```

### 5.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong method names
```java
// WRONG - method is listLatest, not listDatasets
datasetsClient.listDatasets();

// WRONG - method is getDatasetVersion, not get
datasetsClient.get("my-dataset", "1.0");

// WRONG - missing version parameter
datasetsClient.getDatasetVersion("my-dataset");
```

---

## 6. Index Operations

### 6.1 ✅ CORRECT: List Indexes
```java
indexesClient.listLatest().forEach(index -> {
    System.out.println("Index name: " + index.getName());
    System.out.println("Version: " + index.getVersion());
    System.out.println("Description: " + index.getDescription());
});
```

### 6.2 ✅ CORRECT: Create or Update Index
```java
String searchConnectionName = System.getenv("AI_SEARCH_CONNECTION_NAME");
String searchIndexName = System.getenv("AI_SEARCH_INDEX_NAME");

Index index = indexesClient.createOrUpdate(
    "my-index",
    "1.0",
    new AzureAISearchIndex()
        .setConnectionName(searchConnectionName)
        .setIndexName(searchIndexName)
);

System.out.println("Created index: " + index.getName());
```

### 6.3 ✅ CORRECT: Get Index
```java
Index index = indexesClient.get("my-index", "1.0");
System.out.println("Index: " + index.getName());
```

### 6.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using wrong methods
```java
// WRONG - method is listLatest, not list
indexesClient.list();

// WRONG - missing version parameter
indexesClient.get("my-index");

// WRONG - Using wrong index type
indexesClient.createOrUpdate("name", "1.0", new Index());  // Should use AzureAISearchIndex
```

---

## 7. Evaluations

### 7.1 ✅ CORRECT: Access OpenAI Evaluations
```java
import com.openai.services.EvalService;

EvalService evalService = evaluationsClient.getOpenAIClient();
// Use OpenAI evaluation APIs directly
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong evaluation patterns
```java
// WRONG - evaluations aren't directly on the client
evaluationsClient.create(...);

// WRONG - must use getOpenAIClient() first
evaluationsClient.evals.create(...);
```

---

## 8. Async Client Usage

### 8.1 ✅ CORRECT: Async Connections
```java
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

ConnectionsAsyncClient asyncClient = builder.buildConnectionsAsyncClient();

Flux<Connection> connections = asyncClient.listConnections();
connections.subscribe(conn -> System.out.println("Connection: " + conn.getName()));

Mono<Connection> connection = asyncClient.getConnection("my-connection");
connection.subscribe(conn -> System.out.println("Got: " + conn.getName()));
```

### 8.2 ✅ CORRECT: Async Datasets
```java
DatasetsAsyncClient asyncClient = builder.buildDatasetsAsyncClient();

asyncClient.listLatest()
    .doOnNext(dataset -> System.out.println("Dataset: " + dataset.getName()))
    .blockLast();
```

### 8.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Blocking on async without subscribe
```java
// WRONG - must subscribe or block
asyncClient.listConnections();  // Result is ignored

// WRONG - mixing sync/async patterns
for (Connection conn : asyncClient.listConnections()) {  // Won't work with Flux
    System.out.println(conn.getName());
}
```

---

## 9. Error Handling

### 9.1 ✅ CORRECT: Exception Handling
```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    Index index = indexesClient.get("my-index", "1.0");
} catch (ResourceNotFoundException e) {
    System.err.println("Index not found: " + e.getMessage());
} catch (HttpResponseException e) {
    System.err.println("HTTP Error: " + e.getResponse().getStatusCode());
    System.err.println("Message: " + e.getMessage());
}
```

### 9.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Empty catch blocks
```java
// WRONG - swallowing exceptions
try {
    indexesClient.get("my-index", "1.0");
} catch (Exception e) {
    // Do nothing
}
```

---

## 10. Best Practices Checklist

- [ ] Use `DefaultAzureCredentialBuilder` for production authentication
- [ ] Use environment variables for endpoint and connection names
- [ ] Reuse `AIProjectClientBuilder` to create multiple sub-clients efficiently
- [ ] Handle pagination when listing resources with `PagedIterable`
- [ ] Check connection types before accessing credentials
- [ ] Use async clients for high-concurrency scenarios
- [ ] Use `ResourceNotFoundException` for missing resources
- [ ] Clean up datasets and indexes when no longer needed
