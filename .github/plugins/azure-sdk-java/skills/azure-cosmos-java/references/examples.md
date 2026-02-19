# Azure Cosmos DB Java SDK - Examples

Comprehensive code examples for the Azure Cosmos DB SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Database Operations](#database-operations)
- [Container Operations](#container-operations)
- [CRUD Operations (Sync)](#crud-operations-sync)
- [CRUD Operations (Async)](#crud-operations-async)
- [SQL Queries](#sql-queries)

---

## Maven Dependency

```xml
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
        <artifactId>azure-cosmos</artifactId>
    </dependency>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-identity</artifactId>
    </dependency>
</dependencies>
```

---

## Client Creation

### Synchronous Client (CosmosClient)

```java
import com.azure.cosmos.ConsistencyLevel;
import com.azure.cosmos.CosmosClient;
import com.azure.cosmos.CosmosClientBuilder;
import java.util.Arrays;

// Basic client with key authentication
CosmosClient cosmosClient = new CosmosClientBuilder()
    .endpoint("<YOUR ENDPOINT HERE>")
    .key("<YOUR KEY HERE>")
    .buildClient();

// Client with full configuration
CosmosClient cosmosClient = new CosmosClientBuilder()
    .endpoint(serviceEndpoint)
    .key(key)
    .preferredRegions(Arrays.asList("West US", "East US"))
    .consistencyLevel(ConsistencyLevel.SESSION)
    .contentResponseOnWriteEnabled(true)
    .connectionSharingAcrossClientsEnabled(true)
    .userAgentSuffix("my-application-client")
    .buildClient();
```

### Asynchronous Client (CosmosAsyncClient)

```java
import com.azure.cosmos.CosmosAsyncClient;
import java.util.ArrayList;

ArrayList<String> preferredRegions = new ArrayList<>();
preferredRegions.add("West US");

CosmosAsyncClient cosmosAsyncClient = new CosmosClientBuilder()
    .endpoint(serviceEndpoint)
    .key(masterKey)
    .preferredRegions(preferredRegions)
    .consistencyLevel(ConsistencyLevel.SESSION)
    .contentResponseOnWriteEnabled(true)
    .buildAsyncClient();
```

### Client with DefaultAzureCredential (Recommended)

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

CosmosClient cosmosClient = new CosmosClientBuilder()
    .endpoint(serviceEndpoint)
    .credential(new DefaultAzureCredentialBuilder().build())
    .preferredRegions(Arrays.asList("West US"))
    .consistencyLevel(ConsistencyLevel.SESSION)
    .contentResponseOnWriteEnabled(true)
    .buildClient();
```

---

## Database Operations

```java
import com.azure.cosmos.CosmosDatabase;
import com.azure.cosmos.models.CosmosDatabaseResponse;
import com.azure.cosmos.models.CosmosDatabaseRequestOptions;

// Create database if not exists
CosmosDatabaseResponse databaseResponse = cosmosClient.createDatabaseIfNotExists("AzureSampleFamilyDB");
CosmosDatabase database = cosmosClient.getDatabase(databaseResponse.getProperties().getId());

// Get existing database reference
CosmosDatabase database = cosmosClient.getDatabase("AzureSampleFamilyDB");

// Delete database
CosmosDatabaseResponse deleteResponse = database.delete(new CosmosDatabaseRequestOptions());
System.out.println("Status code for database delete: " + deleteResponse.getStatusCode());
```

---

## Container Operations

```java
import com.azure.cosmos.CosmosContainer;
import com.azure.cosmos.models.CosmosContainerProperties;
import com.azure.cosmos.models.CosmosContainerResponse;
import com.azure.cosmos.models.ThroughputProperties;

// Create container with partition key and throughput
CosmosContainerProperties containerProperties = 
    new CosmosContainerProperties("FamilyContainer", "/lastName");

// Manual throughput (400 RU/s)
ThroughputProperties throughputProperties = ThroughputProperties.createManualThroughput(400);

CosmosContainerResponse containerResponse = database.createContainerIfNotExists(
    containerProperties, 
    throughputProperties
);

CosmosContainer container = database.getContainer(containerResponse.getProperties().getId());

// Get existing container reference
CosmosContainer container = database.getContainer("FamilyContainer");

// Delete container
container.delete();
```

---

## CRUD Operations (Sync)

```java
import com.azure.cosmos.CosmosContainer;
import com.azure.cosmos.CosmosException;
import com.azure.cosmos.models.CosmosItemRequestOptions;
import com.azure.cosmos.models.CosmosItemResponse;
import com.azure.cosmos.models.PartitionKey;
import java.time.Duration;

// ============ CREATE ============
Family family = new Family();
family.setId("AndersenFamily");
family.setLastName("Andersen");
family.setRegistered(true);

CosmosItemRequestOptions options = new CosmosItemRequestOptions();
CosmosItemResponse<Family> createResponse = container.createItem(
    family, 
    new PartitionKey(family.getLastName()), 
    options
);

System.out.printf("Created item with request charge of %.2f within duration %s%n",
    createResponse.getRequestCharge(), 
    createResponse.getDuration());

// ============ READ (Point Read) ============
try {
    CosmosItemResponse<Family> readResponse = container.readItem(
        "AndersenFamily",                    // id
        new PartitionKey("Andersen"),        // partition key
        Family.class
    );
    
    Family readFamily = readResponse.getItem();
    double requestCharge = readResponse.getRequestCharge();
    Duration requestLatency = readResponse.getDuration();
    
    System.out.printf("Read item id=%s with charge=%.2f, latency=%s%n",
        readFamily.getId(), requestCharge, requestLatency);
        
} catch (CosmosException e) {
    System.err.printf("Read failed with status code %d: %s%n", 
        e.getStatusCode(), e.getMessage());
}

// ============ UPDATE (Replace) ============
family.setDistrict("NewDistrict");
CosmosItemResponse<Family> replaceResponse = container.replaceItem(
    family,
    family.getId(),
    new PartitionKey(family.getLastName()),
    new CosmosItemRequestOptions()
);

System.out.printf("Replaced item id=%s, district=%s, charge=%.2f%n",
    replaceResponse.getItem().getId(),
    replaceResponse.getItem().getDistrict(),
    replaceResponse.getRequestCharge());

// ============ UPSERT (Create or Replace) ============
family.setRegistered(false);
CosmosItemResponse<Family> upsertResponse = container.upsertItem(family);

System.out.printf("Upserted item with charge=%.2f within duration %s%n",
    upsertResponse.getRequestCharge(), 
    upsertResponse.getDuration());

// ============ DELETE ============
container.deleteItem(
    family.getId(),
    new PartitionKey(family.getLastName()),
    new CosmosItemRequestOptions()
);
```

---

## CRUD Operations (Async)

```java
import com.azure.cosmos.CosmosAsyncContainer;
import reactor.core.publisher.Mono;
import reactor.core.publisher.Flux;

// ============ CREATE (Async) ============
Mono<CosmosItemResponse<Family>> createMono = cosmosAsyncContainer.createItem(family);

createMono.subscribe(response -> {
    System.out.printf("Created item with request charge of %.2f%n", 
        response.getRequestCharge());
});

// ============ CHAINED CRUD OPERATIONS ============
cosmosAsyncContainer.createItem(new Family("carla.davis@outlook.com", "Carla Davis"))
    .flatMap(response -> {
        System.out.println("Created item: " + response.getItem().getId());
        // Read that item
        return cosmosAsyncContainer.readItem(
            response.getItem().getId(),
            new PartitionKey(response.getItem().getLastName()), 
            Family.class
        );
    })
    .flatMap(response -> {
        System.out.println("Read item: " + response.getItem().getId());
        // Replace that item
        Family p = response.getItem();
        p.setDistrict("SFO");
        return cosmosAsyncContainer.replaceItem(
            p, 
            response.getItem().getId(),
            new PartitionKey(response.getItem().getLastName())
        );
    })
    .flatMap(response -> {
        // Delete that item
        return cosmosAsyncContainer.deleteItem(
            response.getItem().getId(),
            new PartitionKey(response.getItem().getLastName())
        );
    })
    .block(); // Block only for demo - avoid in production

// ============ BATCH CREATE (Async) ============
Flux<Family> familiesToCreate = Flux.just(family1, family2, family3, family4);

double totalCharge = familiesToCreate
    .flatMap(family -> cosmosAsyncContainer.createItem(family))
    .flatMap(itemResponse -> {
        System.out.printf("Created item ID: %s with charge %.2f%n",
            itemResponse.getItem().getId(),
            itemResponse.getRequestCharge());
        return Mono.just(itemResponse.getRequestCharge());
    })
    .reduce(0.0, Double::sum)
    .block();

System.out.printf("Total request charge: %.2f%n", totalCharge);
```

---

## SQL Queries

### Basic Queries

```java
import com.azure.cosmos.models.CosmosQueryRequestOptions;
import com.azure.cosmos.util.CosmosPagedIterable;

CosmosQueryRequestOptions queryOptions = new CosmosQueryRequestOptions();
queryOptions.setQueryMetricsEnabled(true);

// Query all documents
CosmosPagedIterable<Family> families = container.queryItems(
    "SELECT * FROM c", 
    queryOptions, 
    Family.class
);

for (Family family : families) {
    System.out.println("Family: " + family.getId());
}

// Query with WHERE clause
String query = "SELECT * FROM Family WHERE Family.lastName IN ('Andersen', 'Wakefield', 'Johnson')";
CosmosPagedIterable<Family> filteredFamilies = container.queryItems(
    query, 
    queryOptions, 
    Family.class
);
```

### Parameterized Queries (Recommended)

```java
import com.azure.cosmos.models.SqlParameter;
import com.azure.cosmos.models.SqlQuerySpec;
import java.util.ArrayList;

// Single parameter
ArrayList<SqlParameter> paramList = new ArrayList<>();
paramList.add(new SqlParameter("@id", "AndersenFamily"));

SqlQuerySpec querySpec = new SqlQuerySpec(
    "SELECT * FROM Families f WHERE (f.id = @id)",
    paramList
);

CosmosPagedIterable<Family> families = container.queryItems(
    querySpec, 
    new CosmosQueryRequestOptions(), 
    Family.class
);

// Multiple parameters
paramList = new ArrayList<>();
paramList.add(new SqlParameter("@id", "AndersenFamily"));
paramList.add(new SqlParameter("@city", "Seattle"));

querySpec = new SqlQuerySpec(
    "SELECT * FROM Families f WHERE f.id = @id AND f.Address.City = @city",
    paramList
);

CosmosPagedIterable<Family> result = container.queryItems(
    querySpec, 
    new CosmosQueryRequestOptions(), 
    Family.class
);
```

### Queries with Paging

```java
import com.azure.cosmos.models.FeedResponse;

String query = "SELECT * FROM Families";
int pageSize = 100;
String continuationToken = null;
double totalRequestCharge = 0.0;

do {
    CosmosQueryRequestOptions queryOptions = new CosmosQueryRequestOptions();
    
    Iterable<FeedResponse<Family>> feedResponseIterator = container
        .queryItems(query, queryOptions, Family.class)
        .iterableByPage(continuationToken, pageSize);

    for (FeedResponse<Family> page : feedResponseIterator) {
        System.out.printf("Page with %d items, charge: %.2f%n", 
            page.getResults().size(),
            page.getRequestCharge());
        
        totalRequestCharge += page.getRequestCharge();
        
        // Process items in this page
        for (Family family : page.getResults()) {
            System.out.println("  - " + family.getId());
        }
        
        // Get continuation token for next page
        continuationToken = page.getContinuationToken();
    }
} while (continuationToken != null);

System.out.printf("Total request charge: %.2f%n", totalRequestCharge);
```
