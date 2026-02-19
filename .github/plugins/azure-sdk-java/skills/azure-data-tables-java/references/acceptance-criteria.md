# Azure Data Tables Java SDK Acceptance Criteria

**SDK**: `com.azure:azure-data-tables`
**Repository**: https://github.com/Azure/azure-sdk-for-java
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Client Builder Patterns

### ✅ CORRECT: TableServiceClient with DefaultAzureCredential

```java
import com.azure.data.tables.TableServiceClient;
import com.azure.data.tables.TableServiceClientBuilder;
import com.azure.identity.DefaultAzureCredentialBuilder;

TableServiceClient serviceClient = new TableServiceClientBuilder()
    .endpoint(System.getenv("AZURE_TABLES_ENDPOINT"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### ✅ CORRECT: TableClient Direct Construction

```java
import com.azure.data.tables.TableClient;
import com.azure.data.tables.TableClientBuilder;

TableClient tableClient = new TableClientBuilder()
    .endpoint(System.getenv("AZURE_TABLES_ENDPOINT"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .tableName("mytable")
    .buildClient();
```

### ✅ CORRECT: With AzureNamedKeyCredential

```java
import com.azure.core.credential.AzureNamedKeyCredential;

AzureNamedKeyCredential credential = new AzureNamedKeyCredential(
    System.getenv("AZURE_STORAGE_ACCOUNT_NAME"),
    System.getenv("AZURE_STORAGE_ACCOUNT_KEY")
);

TableServiceClient serviceClient = new TableServiceClientBuilder()
    .endpoint(System.getenv("AZURE_TABLES_ENDPOINT"))
    .credential(credential)
    .buildClient();
```

### ❌ INCORRECT: Hardcoded Connection String

```java
// WRONG - hardcoded connection string
TableServiceClient client = new TableServiceClientBuilder()
    .connectionString("DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=...")
    .buildClient();
```

### ❌ INCORRECT: Missing Table Name

```java
// WRONG - TableClient requires table name
TableClient tableClient = new TableClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildClient();  // Missing .tableName()
```

---

## 2. Table Operations

### ✅ CORRECT: Create Table If Not Exists

```java
// Create table if not exists (returns TableClient)
TableClient tableClient = serviceClient.createTableIfNotExists("mytable");

// Or from service client
serviceClient.createTableIfNotExists("products");
```

### ✅ CORRECT: Get Table Client from Service

```java
TableClient tableClient = serviceClient.getTableClient("mytable");
```

### ✅ CORRECT: List Tables

```java
import com.azure.data.tables.models.TableItem;
import com.azure.data.tables.models.ListTablesOptions;

// List all tables
for (TableItem table : serviceClient.listTables()) {
    System.out.println("Table: " + table.getName());
}

// List with filter
ListTablesOptions options = new ListTablesOptions()
    .setFilter("TableName ge 'a' and TableName lt 'b'");

for (TableItem table : serviceClient.listTables(options, null, null)) {
    System.out.println("Table: " + table.getName());
}
```

### ❌ INCORRECT: Not Using CreateIfNotExists

```java
// WRONG - throws exception if table exists
serviceClient.createTable("mytable");
// Use createTableIfNotExists instead
```

---

## 3. Entity Operations

### ✅ CORRECT: Create Entity with TableEntity

```java
import com.azure.data.tables.models.TableEntity;

TableEntity entity = new TableEntity("electronics", "laptop-001")
    .addProperty("Name", "Gaming Laptop")
    .addProperty("Price", 1299.99)
    .addProperty("Quantity", 50)
    .addProperty("InStock", true);

tableClient.createEntity(entity);
```

### ✅ CORRECT: Get Entity

```java
TableEntity entity = tableClient.getEntity("electronics", "laptop-001");

String name = (String) entity.getProperty("Name");
Double price = (Double) entity.getProperty("Price");
Integer quantity = (Integer) entity.getProperty("Quantity");

System.out.printf("Product: %s, Price: %.2f, Qty: %d%n", name, price, quantity);
```

### ✅ CORRECT: Update Entity (Merge vs Replace)

```java
import com.azure.data.tables.models.TableEntityUpdateMode;

// Merge - updates only specified properties, keeps others
TableEntity mergeEntity = new TableEntity("electronics", "laptop-001")
    .addProperty("Price", 1199.99);  // Only update price
tableClient.updateEntity(mergeEntity, TableEntityUpdateMode.MERGE);

// Replace - replaces entire entity
TableEntity replaceEntity = new TableEntity("electronics", "laptop-001")
    .addProperty("Name", "Updated Laptop")
    .addProperty("Price", 1199.99)
    .addProperty("Quantity", 45)
    .addProperty("InStock", true);
tableClient.updateEntity(replaceEntity, TableEntityUpdateMode.REPLACE);
```

### ✅ CORRECT: Upsert Entity

```java
// Insert or update (merge mode)
tableClient.upsertEntity(entity, TableEntityUpdateMode.MERGE);

// Insert or replace
tableClient.upsertEntity(entity, TableEntityUpdateMode.REPLACE);
```

### ✅ CORRECT: Delete Entity

```java
tableClient.deleteEntity("electronics", "laptop-001");
```

### ❌ INCORRECT: Missing Partition Key or Row Key

```java
// WRONG - TableEntity requires both partition key and row key
TableEntity entity = new TableEntity("partitionKey", null);
// Both keys are required
```

---

## 4. Query Operations

### ✅ CORRECT: List Entities with Filter

```java
import com.azure.data.tables.models.ListEntitiesOptions;

// Filter by partition key
ListEntitiesOptions options = new ListEntitiesOptions()
    .setFilter("PartitionKey eq 'electronics'");

for (TableEntity entity : tableClient.listEntities(options, null, null)) {
    System.out.printf("%s: %s%n",
        entity.getRowKey(),
        entity.getProperty("Name"));
}
```

### ✅ CORRECT: Complex OData Filters

```java
// Multiple conditions
ListEntitiesOptions options = new ListEntitiesOptions()
    .setFilter("PartitionKey eq 'electronics' and Price gt 500");

// Range queries
options.setFilter("Quantity ge 10 and Quantity le 100");

// String comparison
options.setFilter("Name ge 'A' and Name lt 'N'");
```

### ✅ CORRECT: Select Specific Properties

```java
ListEntitiesOptions options = new ListEntitiesOptions()
    .setFilter("PartitionKey eq 'electronics'")
    .setSelect("Name", "Price");  // Only return these properties

for (TableEntity entity : tableClient.listEntities(options, null, null)) {
    // Only Name and Price are populated
    System.out.printf("%s: %.2f%n",
        entity.getProperty("Name"),
        entity.getProperty("Price"));
}
```

### ✅ CORRECT: Top N Results

```java
ListEntitiesOptions options = new ListEntitiesOptions()
    .setFilter("PartitionKey eq 'electronics'")
    .setTop(10);  // Return only 10 results

for (TableEntity entity : tableClient.listEntities(options, null, null)) {
    System.out.println(entity.getRowKey());
}
```

### ❌ INCORRECT: Missing Partition Key Filter (Performance)

```java
// WRONG - full table scan without partition key filter
ListEntitiesOptions options = new ListEntitiesOptions()
    .setFilter("Price gt 100");  // Should include PartitionKey for performance
```

---

## 5. Batch/Transaction Operations

### ✅ CORRECT: Batch with Same Partition Key

```java
import com.azure.data.tables.models.TableTransactionAction;
import com.azure.data.tables.models.TableTransactionActionType;
import java.util.Arrays;
import java.util.List;

// All entities MUST have same partition key
List<TableTransactionAction> actions = Arrays.asList(
    new TableTransactionAction(
        TableTransactionActionType.CREATE,
        new TableEntity("electronics", "item-001")
            .addProperty("Name", "Item 1")
            .addProperty("Price", 29.99)),
    new TableTransactionAction(
        TableTransactionActionType.CREATE,
        new TableEntity("electronics", "item-002")
            .addProperty("Name", "Item 2")
            .addProperty("Price", 49.99)),
    new TableTransactionAction(
        TableTransactionActionType.UPSERT_MERGE,
        new TableEntity("electronics", "item-003")
            .addProperty("Name", "Item 3")
            .addProperty("Price", 19.99))
);

tableClient.submitTransaction(actions);
```

### ❌ INCORRECT: Different Partition Keys in Batch

```java
// WRONG - all entities in a transaction must have same partition key
List<TableTransactionAction> actions = Arrays.asList(
    new TableTransactionAction(
        TableTransactionActionType.CREATE,
        new TableEntity("electronics", "item-001")),  // partition: electronics
    new TableTransactionAction(
        TableTransactionActionType.CREATE,
        new TableEntity("clothing", "item-002"))      // partition: clothing - WRONG!
);
```

### ❌ INCORRECT: More Than 100 Operations

```java
// WRONG - batch limit is 100 operations
List<TableTransactionAction> actions = new ArrayList<>();
for (int i = 0; i < 150; i++) {  // Too many!
    actions.add(new TableTransactionAction(...));
}
tableClient.submitTransaction(actions);  // Will fail
```

---

## 6. Typed Entities

### ✅ CORRECT: Custom Entity Class

```java
import com.azure.data.tables.models.TableEntity;
import java.time.OffsetDateTime;

public class Product {
    private String partitionKey;
    private String rowKey;
    private OffsetDateTime timestamp;
    private String eTag;
    private String name;
    private double price;
    private int quantity;
    private boolean inStock;

    // Required: default constructor
    public Product() {}

    public Product(String category, String productId) {
        this.partitionKey = category;
        this.rowKey = productId;
    }

    // Getters and setters for all fields
    public String getPartitionKey() { return partitionKey; }
    public void setPartitionKey(String partitionKey) { this.partitionKey = partitionKey; }

    public String getRowKey() { return rowKey; }
    public void setRowKey(String rowKey) { this.rowKey = rowKey; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }

    public boolean isInStock() { return inStock; }
    public void setInStock(boolean inStock) { this.inStock = inStock; }
}
```

### ✅ CORRECT: Using Typed Entity

```java
Product product = new Product("electronics", "laptop-001");
product.setName("Gaming Laptop");
product.setPrice(1299.99);
product.setQuantity(50);
product.setInStock(true);

// Create using typed entity (convert to TableEntity)
TableEntity entity = new TableEntity(product.getPartitionKey(), product.getRowKey())
    .addProperty("Name", product.getName())
    .addProperty("Price", product.getPrice())
    .addProperty("Quantity", product.getQuantity())
    .addProperty("InStock", product.isInStock());

tableClient.createEntity(entity);
```

---

## 7. Error Handling

### ✅ CORRECT: Handle TableServiceException

```java
import com.azure.data.tables.models.TableServiceException;

try {
    tableClient.createEntity(entity);
} catch (TableServiceException e) {
    int statusCode = e.getResponse().getStatusCode();

    switch (statusCode) {
        case 409:
            System.err.println("Entity already exists");
            break;
        case 404:
            System.err.println("Table not found");
            break;
        default:
            System.err.printf("Error %d: %s%n", statusCode, e.getMessage());
    }
}
```

### ❌ INCORRECT: Generic Exception Handling

```java
// WRONG - loses status code information
try {
    tableClient.createEntity(entity);
} catch (Exception e) {
    System.out.println("Error: " + e.getMessage());
}
```

---

## 8. Partition Key Design

### ✅ CORRECT: Good Partition Key Choices

```java
// Category-based partitioning for products
new TableEntity("electronics", "laptop-001")
new TableEntity("electronics", "phone-001")
new TableEntity("clothing", "shirt-001")

// Tenant-based partitioning for multi-tenant apps
new TableEntity("tenant-" + tenantId, "user-" + oderId)

// Date-based partitioning for logs
new TableEntity("2024-01", "log-001")
new TableEntity("2024-01", "log-002")
```

### ❌ INCORRECT: Hot Partition

```java
// WRONG - all data in single partition causes hotspots
new TableEntity("all-data", "item-001")
new TableEntity("all-data", "item-002")
new TableEntity("all-data", "item-003")
// Use varied partition keys for distribution
```

### ❌ INCORRECT: Too Many Partitions

```java
// WRONG - using unique ID as partition key fragments data
new TableEntity(UUID.randomUUID().toString(), "data")
// Makes range queries impossible
```

---

## 9. Environment Configuration

### ✅ CORRECT: Environment Variables

```bash
# Azure Storage Tables
AZURE_TABLES_ENDPOINT=https://<account>.table.core.windows.net
AZURE_STORAGE_ACCOUNT_NAME=<account-name>
AZURE_STORAGE_ACCOUNT_KEY=<account-key>

# Azure Cosmos DB Table API
COSMOS_TABLE_ENDPOINT=https://<account>.table.cosmosdb.azure.com
```

---

## 10. Connection String vs Endpoint

### ✅ CORRECT: Use Endpoint with Credential

```java
// Preferred - explicit endpoint and credential
TableServiceClient client = new TableServiceClientBuilder()
    .endpoint(System.getenv("AZURE_TABLES_ENDPOINT"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### ✅ CORRECT: Connection String from Environment

```java
// Acceptable - connection string from environment
TableServiceClient client = new TableServiceClientBuilder()
    .connectionString(System.getenv("AZURE_TABLES_CONNECTION_STRING"))
    .buildClient();
```