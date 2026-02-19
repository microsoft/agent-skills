# Azure Cosmos DB Java SDK Acceptance Criteria

**SDK**: `com.azure:azure-cosmos`
**Repository**: https://github.com/Azure/azure-sdk-for-java
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Client Builder Patterns

### ✅ CORRECT: CosmosClient with DefaultAzureCredential

```java
import com.azure.cosmos.CosmosClient;
import com.azure.cosmos.CosmosClientBuilder;
import com.azure.cosmos.ConsistencyLevel;
import com.azure.identity.DefaultAzureCredentialBuilder;
import java.util.Arrays;

CosmosClient cosmosClient = new CosmosClientBuilder()
    .endpoint(System.getenv("COSMOS_ENDPOINT"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .consistencyLevel(ConsistencyLevel.SESSION)
    .contentResponseOnWriteEnabled(true)
    .preferredRegions(Arrays.asList("West US", "East US"))
    .buildClient();
```

### ✅ CORRECT: CosmosAsyncClient for High-Throughput

```java
import com.azure.cosmos.CosmosAsyncClient;

CosmosAsyncClient asyncClient = new CosmosClientBuilder()
    .endpoint(System.getenv("COSMOS_ENDPOINT"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .consistencyLevel(ConsistencyLevel.SESSION)
    .contentResponseOnWriteEnabled(true)
    .buildAsyncClient();
```

### ❌ INCORRECT: Hardcoded Credentials

```java
// WRONG - hardcoded endpoint and key
CosmosClient client = new CosmosClientBuilder()
    .endpoint("https://myaccount.documents.azure.com:443/")
    .key("mySecretKey123...")
    .buildClient();
```

### ❌ INCORRECT: Missing Content Response Configuration

```java
// WRONG - missing contentResponseOnWriteEnabled for read-after-write scenarios
CosmosClient client = new CosmosClientBuilder()
    .endpoint(endpoint)
    .key(key)
    .buildClient();  // Missing .contentResponseOnWriteEnabled(true)
```

---

## 2. CRUD Operations with PartitionKey

### ✅ CORRECT: Create Item with PartitionKey

```java
import com.azure.cosmos.CosmosContainer;
import com.azure.cosmos.models.CosmosItemRequestOptions;
import com.azure.cosmos.models.CosmosItemResponse;
import com.azure.cosmos.models.PartitionKey;

CosmosContainer container = cosmosClient
    .getDatabase("myDatabase")
    .getContainer("myContainer");

User user = new User("user-123", "John Doe", "john@example.com");

CosmosItemResponse<User> response = container.createItem(
    user,
    new PartitionKey(user.getId()),
    new CosmosItemRequestOptions()
);

System.out.printf("Created item with request charge: %.2f%n", response.getRequestCharge());
```

### ✅ CORRECT: Read Item (Point Read)

```java
try {
    CosmosItemResponse<User> response = container.readItem(
        "user-123",
        new PartitionKey("user-123"),
        User.class
    );
    User user = response.getItem();
    System.out.printf("Read item with charge: %.2f RU%n", response.getRequestCharge());
} catch (CosmosException e) {
    if (e.getStatusCode() == 404) {
        System.out.println("Item not found");
    }
}
```

### ✅ CORRECT: Upsert (Create or Replace)

```java
CosmosItemResponse<User> response = container.upsertItem(user);
System.out.printf("Upserted with charge: %.2f%n", response.getRequestCharge());
```

### ❌ INCORRECT: Missing PartitionKey in Read

```java
// WRONG - readItem requires partition key
CosmosItemResponse<User> response = container.readItem("user-123", User.class);
```

### ❌ INCORRECT: Using Query Instead of Point Read

```java
// WRONG - inefficient; use readItem for single-document lookups
String query = "SELECT * FROM c WHERE c.id = 'user-123'";
container.queryItems(query, new CosmosQueryRequestOptions(), User.class);
```

---

## 3. Parameterized Queries

### ✅ CORRECT: SqlQuerySpec with Parameters

```java
import com.azure.cosmos.models.SqlParameter;
import com.azure.cosmos.models.SqlQuerySpec;
import com.azure.cosmos.models.CosmosQueryRequestOptions;
import com.azure.cosmos.util.CosmosPagedIterable;
import java.util.Arrays;

SqlQuerySpec querySpec = new SqlQuerySpec(
    "SELECT * FROM c WHERE c.status = @status AND c.category = @category",
    Arrays.asList(
        new SqlParameter("@status", "active"),
        new SqlParameter("@category", "electronics")
    )
);

CosmosPagedIterable<Product> results = container.queryItems(
    querySpec,
    new CosmosQueryRequestOptions(),
    Product.class
);

results.forEach(product -> System.out.println(product.getName()));
```

### ❌ INCORRECT: String Concatenation in Query

```java
// WRONG - SQL injection vulnerability
String status = userInput;
String query = "SELECT * FROM c WHERE c.status = '" + status + "'";
container.queryItems(query, options, Product.class);
```

### ❌ INCORRECT: String.format in Query

```java
// WRONG - still vulnerable to injection
String query = String.format("SELECT * FROM c WHERE c.id = '%s'", userId);
```

---

## 4. Async Patterns with Reactor

### ✅ CORRECT: Chained Async Operations

```java
import reactor.core.publisher.Mono;

cosmosAsyncContainer.createItem(user)
    .flatMap(response -> {
        System.out.println("Created: " + response.getItem().getId());
        return cosmosAsyncContainer.readItem(
            response.getItem().getId(),
            new PartitionKey(response.getItem().getId()),
            User.class
        );
    })
    .flatMap(response -> {
        User u = response.getItem();
        u.setEmail("updated@example.com");
        return cosmosAsyncContainer.replaceItem(
            u,
            u.getId(),
            new PartitionKey(u.getId())
        );
    })
    .subscribe(
        response -> System.out.println("Updated: " + response.getItem().getId()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### ✅ CORRECT: Batch Create with Flux

```java
import reactor.core.publisher.Flux;

Flux<User> usersToCreate = Flux.just(user1, user2, user3);

double totalCharge = usersToCreate
    .flatMap(user -> cosmosAsyncContainer.createItem(user))
    .map(response -> {
        System.out.printf("Created %s with %.2f RU%n",
            response.getItem().getId(),
            response.getRequestCharge());
        return response.getRequestCharge();
    })
    .reduce(0.0, Double::sum)
    .block();

System.out.printf("Total RU: %.2f%n", totalCharge);
```

### ❌ INCORRECT: Blocking in Production Code

```java
// WRONG - blocks reactive stream, defeats async purpose
CosmosItemResponse<User> response = cosmosAsyncContainer.createItem(user).block();
// Use sync client if blocking is needed
```

---

## 5. Query with Paging

### ✅ CORRECT: Paging with Continuation Token

```java
import com.azure.cosmos.models.FeedResponse;

String continuationToken = null;
int pageSize = 100;

do {
    CosmosQueryRequestOptions options = new CosmosQueryRequestOptions();

    Iterable<FeedResponse<User>> feedResponses = container
        .queryItems("SELECT * FROM c", options, User.class)
        .iterableByPage(continuationToken, pageSize);

    for (FeedResponse<User> page : feedResponses) {
        System.out.printf("Page with %d items, charge: %.2f%n",
            page.getResults().size(),
            page.getRequestCharge());

        for (User user : page.getResults()) {
            System.out.println("  - " + user.getId());
        }

        continuationToken = page.getContinuationToken();
    }
} while (continuationToken != null);
```

### ❌ INCORRECT: Loading All Results into Memory

```java
// WRONG - loads all results, memory issues for large datasets
List<User> allUsers = new ArrayList<>();
container.queryItems("SELECT * FROM c", options, User.class)
    .forEach(allUsers::add);  // OOM risk
```

---

## 6. Error Handling

### ✅ CORRECT: Handling CosmosException

```java
import com.azure.cosmos.CosmosException;

try {
    container.createItem(item, new PartitionKey(item.getId()), options);
} catch (CosmosException e) {
    int statusCode = e.getStatusCode();
    double requestCharge = e.getRequestCharge();

    switch (statusCode) {
        case 409:
            System.err.println("Conflict: Item already exists");
            break;
        case 429:
            System.err.printf("Rate limited. Retry after: %s%n",
                e.getRetryAfterDuration());
            break;
        case 404:
            System.err.println("Not found");
            break;
        default:
            System.err.printf("Error %d: %s (charge: %.2f)%n",
                statusCode, e.getMessage(), requestCharge);
    }
}
```

### ❌ INCORRECT: Catching Generic Exception

```java
// WRONG - loses status code information
try {
    container.createItem(item);
} catch (Exception e) {
    System.out.println("Error: " + e.getMessage());
}
```

---

## 7. Client Lifecycle Management

### ✅ CORRECT: Singleton Client with Cleanup

```java
public class CosmosService implements AutoCloseable {
    private final CosmosClient cosmosClient;
    private final CosmosContainer container;

    public CosmosService() {
        this.cosmosClient = new CosmosClientBuilder()
            .endpoint(System.getenv("COSMOS_ENDPOINT"))
            .credential(new DefaultAzureCredentialBuilder().build())
            .consistencyLevel(ConsistencyLevel.SESSION)
            .buildClient();

        this.container = cosmosClient
            .getDatabase("myDatabase")
            .getContainer("myContainer");
    }

    public User getUser(String id) {
        return container.readItem(id, new PartitionKey(id), User.class).getItem();
    }

    @Override
    public void close() {
        if (cosmosClient != null) {
            cosmosClient.close();
        }
    }
}
```

### ❌ INCORRECT: Creating Client Per Request

```java
// WRONG - creates new client for each request, connection overhead
public User getUser(String id) {
    CosmosClient client = new CosmosClientBuilder()
        .endpoint(endpoint)
        .key(key)
        .buildClient();
    return client.getDatabase("db").getContainer("c")
        .readItem(id, new PartitionKey(id), User.class).getItem();
    // Missing close(), connection leak
}
```

---

## 8. Database and Container Creation

### ✅ CORRECT: Create If Not Exists

```java
import com.azure.cosmos.CosmosDatabase;
import com.azure.cosmos.models.CosmosDatabaseResponse;
import com.azure.cosmos.models.CosmosContainerProperties;
import com.azure.cosmos.models.ThroughputProperties;

// Create database
CosmosDatabaseResponse dbResponse = cosmosClient.createDatabaseIfNotExists("myDatabase");
CosmosDatabase database = cosmosClient.getDatabase(dbResponse.getProperties().getId());

// Create container with partition key and throughput
CosmosContainerProperties containerProps =
    new CosmosContainerProperties("myContainer", "/partitionKey");

ThroughputProperties throughput = ThroughputProperties.createManualThroughput(400);

database.createContainerIfNotExists(containerProps, throughput);
```

### ❌ INCORRECT: Hardcoded Throughput in Production

```java
// WRONG - should use autoscale or configure via infrastructure
ThroughputProperties.createManualThroughput(10000);  // Expensive!
```
