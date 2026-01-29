# Azure AI Projects Java SDK - Examples

Comprehensive code examples for the Azure AI Projects SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Working with Connections](#working-with-connections)
- [Working with Deployments](#working-with-deployments)
- [Working with Datasets](#working-with-datasets)
- [Async Clients](#async-clients)

---

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-projects</artifactId>
    <version>1.0.0-beta.1</version>
</dependency>

<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.15.3</version>
</dependency>
```

---

## Client Creation

### Creating AIProjectClient and Sub-Clients

```java
import com.azure.ai.projects.*;
import com.azure.core.util.Configuration;
import com.azure.identity.DefaultAzureCredentialBuilder;

public class ClientInitializationSample {

    public static void main(String[] args) {
        // Create the builder with endpoint and credentials
        AIProjectClientBuilder builder = new AIProjectClientBuilder()
            .endpoint(Configuration.getGlobalConfiguration().get("AZURE_AI_PROJECTS_ENDPOINT"))
            .credential(new DefaultAzureCredentialBuilder().build());

        // Build specific sub-clients as needed
        ConnectionsClient connectionsClient = builder.buildConnectionsClient();
        DatasetsClient datasetsClient = builder.buildDatasetsClient();
        DeploymentsClient deploymentsClient = builder.buildDeploymentsClient();
        EvaluationRulesClient evaluationRulesClient = builder.buildEvaluationRulesClient();
        EvaluationsClient evaluationsClient = builder.buildEvaluationsClient();
        EvaluationTaxonomiesClient evaluationTaxonomiesClient = builder.buildEvaluationTaxonomiesClient();
        EvaluatorsClient evaluatorsClient = builder.buildEvaluatorsClient();
        IndexesClient indexesClient = builder.buildIndexesClient();
        InsightsClient insightsClient = builder.buildInsightsClient();
        RedTeamsClient redTeamsClient = builder.buildRedTeamsClient();
        SchedulesClient schedulesClient = builder.buildSchedulesClient();
        
        // For async clients, use the async builder methods
        ConnectionsAsyncClient connectionsAsyncClient = builder.buildConnectionsAsyncClient();
        DatasetsAsyncClient datasetsAsyncClient = builder.buildDatasetsAsyncClient();
        DeploymentsAsyncClient deploymentsAsyncClient = builder.buildDeploymentsAsyncClient();
    }
}
```

---

## Working with Connections

### List Connections

```java
import com.azure.ai.projects.models.Connection;
import com.azure.ai.projects.models.ConnectionType;
import com.azure.core.http.rest.PagedIterable;

public class ConnectionsSample {

    private static ConnectionsClient connectionsClient;

    public static void listConnections() {
        PagedIterable<Connection> connections = connectionsClient.listConnections();
        for (Connection connection : connections) {
            System.out.println("Connection name: " + connection.getName());
            System.out.println("Connection type: " + connection.getType());
            System.out.println("Connection credential type: " + connection.getCredentials().getType());
            System.out.println("-------------------------------------------------");
        }
    }

    public static void getConnectionWithoutCredentials() {
        String connectionName = "my-connection";
        Connection connection = connectionsClient.getConnection(connectionName);
        System.out.printf("Connection name: %s%n", connection.getName());
    }

    public static void getConnectionWithCredentials() {
        String connectionName = "my-connection";
        Connection connection = connectionsClient.getConnectionWithCredentials(connectionName);
        System.out.printf("Connection name: %s%n", connection.getName());
        System.out.printf("Connection credentials: %s%n", connection.getCredentials().getType());
    }

    // Filter connections by type
    public static void listConnectionsWithFilters() {
        // List only Azure OpenAI connections
        Iterable<Connection> azureOpenAIConnections = 
            connectionsClient.listConnections(ConnectionType.AZURE_OPEN_AI, null);
        
        azureOpenAIConnections.forEach(connection -> {
            System.out.println("Azure OpenAI Connection: " + connection.getName());
        });

        // List only default connections
        Iterable<Connection> defaultConnections = connectionsClient.listConnections(null, true);
        defaultConnections.forEach(connection -> {
            System.out.println("Default Connection: " + connection.getName());
        });
    }
}
```

---

## Working with Deployments

### List and Get Deployments

```java
import com.azure.ai.projects.models.Deployment;
import com.azure.core.http.rest.PagedIterable;

public class DeploymentsSample {

    private static DeploymentsClient deploymentsClient;

    public static void listDeployments() {
        PagedIterable<Deployment> deployments = deploymentsClient.list();
        for (Deployment deployment : deployments) {
            System.out.printf("Deployment name: %s%n", deployment.getName());
        }
    }

    public static void getDeployment() {
        String deploymentName = "gpt-4o";
        Deployment deployment = deploymentsClient.get(deploymentName);

        System.out.printf("Deployment name: %s%n", deployment.getName());
        System.out.printf("Deployment type: %s%n", deployment.getType().getValue());
    }
}
```

---

## Working with Datasets

### Create Dataset with File Upload

```java
import com.azure.ai.projects.models.DatasetVersion;
import com.azure.ai.projects.models.FileDatasetVersion;

import java.nio.file.Path;

public class DatasetsSample {

    private static DatasetsClient datasetsClient;

    // Create a dataset by uploading a file
    public static void createDatasetWithFile() {
        String datasetName = "my-dataset";
        String datasetVersionString = "1.0";

        Path filePath = Path.of("product_info.md");

        FileDatasetVersion createdDatasetVersion = datasetsClient.createDatasetWithFile(
            datasetName, 
            datasetVersionString, 
            filePath
        );

        System.out.println("Created dataset version: " + createdDatasetVersion.getId());
    }

    // List all datasets (latest versions)
    public static void listDatasets() {
        System.out.println("Listing all datasets (latest versions):");
        datasetsClient.listLatest().forEach(dataset -> {
            System.out.println("\nDataset name: " + dataset.getName());
            System.out.println("Dataset Id: " + dataset.getId());
            System.out.println("Dataset version: " + dataset.getVersion());
            System.out.println("Dataset type: " + dataset.getType());
            if (dataset.getDescription() != null) {
                System.out.println("Description: " + dataset.getDescription());
            }
        });
    }

    // List all versions of a specific dataset
    public static void listDatasetVersions() {
        String datasetName = "my-dataset";

        System.out.println("Listing all versions of dataset: " + datasetName);
        datasetsClient.listVersions(datasetName).forEach(version -> {
            System.out.println("\nDataset name: " + version.getName());
            System.out.println("Dataset version: " + version.getVersion());
            System.out.println("Dataset type: " + version.getType());
            if (version.getDataUri() != null) {
                System.out.println("Data URI: " + version.getDataUri());
            }
        });
    }

    // Get a specific dataset version
    public static void getDataset() {
        String datasetName = "my-dataset";
        String datasetVersion = "1.0";

        DatasetVersion dataset = datasetsClient.getDatasetVersion(datasetName, datasetVersion);

        System.out.println("Retrieved dataset:");
        System.out.println("Name: " + dataset.getName());
        System.out.println("Version: " + dataset.getVersion());
        System.out.println("Type: " + dataset.getType());
    }

    // Create or update a dataset with a data URI
    public static void createOrUpdateDataset() {
        String datasetName = "my-dataset";
        String datasetVersion = "1.0";
        String dataUri = "https://example.com/data.txt";

        // Create a new FileDatasetVersion with provided dataUri
        FileDatasetVersion fileDataset = new FileDatasetVersion()
            .setDataUri(dataUri)
            .setDescription("Sample dataset created via SDK");

        // Create or update the dataset
        FileDatasetVersion createdDataset = (FileDatasetVersion) datasetsClient.createOrUpdateVersion(
            datasetName, 
            datasetVersion, 
            fileDataset
        );

        System.out.println("Created/Updated dataset:");
        System.out.println("Name: " + createdDataset.getName());
        System.out.println("Version: " + createdDataset.getVersion());
        System.out.println("Data URI: " + createdDataset.getDataUri());
    }

    // Delete a dataset version
    public static void deleteDataset() {
        String datasetName = "my-dataset";
        String datasetVersion = "1.0";

        datasetsClient.deleteVersion(datasetName, datasetVersion);
        System.out.println("Dataset version deleted successfully");
    }
}
```

---

## Async Clients

### List Connections (Async)

```java
import com.azure.ai.projects.models.Connection;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

public class ConnectionsAsyncSample {

    private static ConnectionsAsyncClient connectionsAsyncClient;

    public static Flux<Connection> listConnections() {
        return connectionsAsyncClient.listConnections()
            .doOnNext(connection -> System.out.printf("Connection name: %s%n", connection.getName()));
    }

    public static Mono<Connection> getConnectionWithoutCredentials() {
        String connectionName = "my-connection";
        return connectionsAsyncClient.getConnection(connectionName)
            .doOnNext(connection -> System.out.printf("Connection name: %s%n", connection.getName()));
    }

    public static Mono<Connection> getConnectionWithCredentials() {
        String connectionName = "my-connection";
        return connectionsAsyncClient.getConnectionWithCredentials(connectionName)
            .doOnNext(connection -> {
                System.out.printf("Connection name: %s%n", connection.getName());
                System.out.printf("Connection credentials: %s%n", connection.getCredentials().getType());
            });
    }

    public static void main(String[] args) {
        // Using block() to wait for the async operations to complete in the sample
        listConnections().blockLast();
        getConnectionWithoutCredentials().block();
        getConnectionWithCredentials().block();
    }
}
```

### Datasets (Async)

```java
import com.azure.ai.projects.models.DatasetVersion;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

public class DatasetsAsyncSample {

    private static DatasetsAsyncClient datasetsAsyncClient;

    public static Flux<DatasetVersion> listLatestDatasets() {
        return datasetsAsyncClient.listLatest()
            .doOnNext(dataset -> {
                System.out.println("Dataset: " + dataset.getName());
                System.out.println("Version: " + dataset.getVersion());
            });
    }

    public static Mono<DatasetVersion> getDataset(String name, String version) {
        return datasetsAsyncClient.getDatasetVersion(name, version)
            .doOnNext(dataset -> {
                System.out.println("Retrieved: " + dataset.getName());
            });
    }

    public static void main(String[] args) {
        listLatestDatasets().blockLast();
        getDataset("my-dataset", "1.0").block();
    }
}
```
