# Azure Data Tables SDK for Java - Examples

Comprehensive code examples for the Azure Data Tables SDK for Java.

## Table of Contents
- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Creating Tables](#creating-tables)
- [CRUD Operations on Entities](#crud-operations-on-entities)
- [Querying Entities](#querying-entities)
- [Batch/Transactional Operations](#batchtransactional-operations)
- [Async Client Patterns](#async-client-patterns)
- [Error Handling](#error-handling)

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-data-tables</artifactId>
    <version>12.6.0-beta.1</version>
</dependency>

<!-- For DefaultAzureCredential authentication -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.18.2</version>
</dependency>
```

## Client Creation

### TableServiceClient with DefaultAzureCredential

```java
import com.azure.core.credential.TokenCredential;
import com.azure.data.tables.TableServiceClient;
import com.azure.data.tables.TableServiceClientBuilder;
import com.azure.identity.DefaultAzureCredentialBuilder;

TokenCredential tokenCredential = new DefaultAzureCredentialBuilder().build();
TableServiceClient tableServiceClient = new TableServiceClientBuilder()
    .endpoint("<your-table-account-url>")
    .credential(tokenCredential)
    .buildClient();
```

### TableServiceClient with Connection String

```java
TableServiceClient tableServiceClient = new TableServiceClientBuilder()
    .connectionString("<your-connection-string>")
    .buildClient();
```

### TableServiceClient with Named Key Credential

```java
import com.azure.core.credential.AzureNamedKeyCredential;

AzureNamedKeyCredential credential = new AzureNamedKeyCredential(
    "<your-account-name>", 
    "<account-access-key>"
);
TableServiceClient tableServiceClient = new TableServiceClientBuilder()
    .endpoint("<your-table-account-url>")
    .credential(credential)
    .buildClient();
```

### TableServiceClient with SAS Token

```java
TableServiceClient tableServiceClient = new TableServiceClientBuilder()
    .endpoint("<your-table-account-url>")
    .sasToken("<sas-token-string>")
    .buildClient();
```

### TableClient (Direct Table Access)

```java
import com.azure.data.tables.TableClient;
import com.azure.data.tables.TableClientBuilder;

// Using endpoint and credential
TableClient tableClient = new TableClientBuilder()
    .endpoint("https://myaccount.table.core.windows.net/")
    .credential(new AzureNamedKeyCredential("name", "key"))
    .tableName("myTable")
    .buildClient();

// Using connection string
TableClient tableClient = new TableClientBuilder()
    .connectionString("<your-connection-string>")
    .tableName("myTable")
    .buildClient();
```

### Get TableClient from TableServiceClient

```java
TableClient tableClient = tableServiceClient.getTableClient("myTable");
System.out.printf("Table name: %s%n", tableClient.getTableName());
```

## Creating Tables

### Create Table

```java
import com.azure.data.tables.TableClient;

String tableName = "myTable";
TableClient tableClient = tableServiceClient.createTable(tableName);
System.out.printf("Created table: %s%n", tableClient.getTableName());
```

### Create Table If Not Exists (Idempotent)

```java
TableClient tableClient = tableServiceClient.createTableIfNotExists(tableName);
```

### Create with Response

```java
import com.azure.core.http.rest.Response;
import com.azure.core.util.Context;
import java.time.Duration;

Response<TableClient> response = tableServiceClient.createTableWithResponse(
    "myTable", 
    Duration.ofSeconds(5), 
    new Context("key1", "value1")
);
System.out.printf("Status: %d, Table: %s%n", 
    response.getStatusCode(), 
    response.getValue().getTableName());
```

### Delete Table

```java
tableServiceClient.deleteTable("myTable");
```

## CRUD Operations on Entities

### Create Entity

```java
import com.azure.data.tables.models.TableEntity;

String partitionKey = "OfficeSupplies";
String rowKey = "s001";

TableEntity entity = new TableEntity(partitionKey, rowKey)
    .addProperty("Product", "Marker Set")
    .addProperty("Price", 5.00)
    .addProperty("Quantity", 21)
    .addProperty("Type", "Pen");

tableClient.createEntity(entity);
System.out.printf("Created entity: %s/%s%n", partitionKey, rowKey);
```

### Create Entity with Response

```java
Response<Void> response = tableClient.createEntityWithResponse(
    entity, 
    Duration.ofSeconds(5), 
    new Context("key1", "value1")
);
System.out.printf("Status: %d%n", response.getStatusCode());
```

### Get Entity

```java
TableEntity retrievedEntity = tableClient.getEntity(partitionKey, rowKey);
System.out.printf("Retrieved: %s/%s%n", 
    retrievedEntity.getPartitionKey(), 
    retrievedEntity.getRowKey());

// Access properties
Object product = retrievedEntity.getProperty("Product");
Object price = retrievedEntity.getProperty("Price");
```

### Get Entity with Select

```java
import java.util.Arrays;
import java.util.List;

List<String> propertiesToSelect = Arrays.asList("Product", "Price");

Response<TableEntity> response = tableClient.getEntityWithResponse(
    partitionKey, 
    rowKey, 
    propertiesToSelect, 
    Duration.ofSeconds(5), 
    new Context("key1", "value1")
);

TableEntity entity = response.getValue();
entity.getProperties().forEach((key, value) ->
    System.out.printf("%s: %s%n", key, value));
```

### Update Entity (Merge)

```java
import com.azure.data.tables.models.TableEntityUpdateMode;

TableEntity entityForUpdate = new TableEntity(partitionKey, rowKey)
    .addProperty("Type", "Pen")
    .addProperty("Color", "Red");

// MERGE mode: merges with existing entity (default)
tableClient.updateEntity(entityForUpdate);

// Explicit MERGE
tableClient.updateEntity(entityForUpdate, TableEntityUpdateMode.MERGE);
```

### Update Entity (Replace)

```java
// REPLACE mode: replaces entire entity
tableClient.updateEntity(entityForUpdate, TableEntityUpdateMode.REPLACE);
```

### Update with ETag (Optimistic Concurrency)

```java
Response<Void> response = tableClient.updateEntityWithResponse(
    entityForUpdate, 
    TableEntityUpdateMode.REPLACE, 
    true,  // ifUnchanged - use ETag
    Duration.ofSeconds(5), 
    new Context("key1", "value1")
);
```

### Upsert Entity (Insert or Update)

```java
TableEntity entityForUpsert = new TableEntity(partitionKey, "s002")
    .addProperty("Type", "Marker")
    .addProperty("Color", "Blue");

// Insert if not exists, update if exists
tableClient.upsertEntity(entityForUpsert);
```

### Delete Entity

```java
// By keys
tableClient.deleteEntity(partitionKey, rowKey);

// By entity object
tableClient.deleteEntity(entity);

// With response
Response<Void> response = tableClient.deleteEntityWithResponse(
    entity, 
    true,  // ifUnchanged - use ETag
    Duration.ofSeconds(5), 
    new Context("key1", "value1")
);
```

## Querying Entities

### List All Entities

```java
import com.azure.core.http.rest.PagedIterable;

PagedIterable<TableEntity> entities = tableClient.listEntities();

entities.forEach(entity ->
    System.out.printf("Entity: %s/%s%n", 
        entity.getPartitionKey(), 
        entity.getRowKey()));
```

### List with Filter and Select

```java
import com.azure.data.tables.models.ListEntitiesOptions;
import java.util.Arrays;

List<String> propertiesToSelect = Arrays.asList("Product", "Price");

ListEntitiesOptions options = new ListEntitiesOptions()
    .setFilter(String.format("PartitionKey eq '%s'", partitionKey))
    .setSelect(propertiesToSelect);

for (TableEntity entity : tableClient.listEntities(options, null, null)) {
    System.out.printf("%s: %.2f%n", 
        entity.getProperty("Product"), 
        entity.getProperty("Price"));
}
```

### Advanced Query with Top

```java
ListEntitiesOptions options = new ListEntitiesOptions()
    .setTop(15)  // Limit results
    .setFilter("PartitionKey eq 'MyPartitionKey' and RowKey eq 'MyRowKey'")
    .setSelect(Arrays.asList("name", "lastname", "age"));

PagedIterable<TableEntity> entities = tableClient.listEntities(
    options,
    Duration.ofSeconds(5), 
    null
);

entities.forEach(entity -> {
    System.out.printf("Entity: %s/%s%n", 
        entity.getPartitionKey(), 
        entity.getRowKey());
    entity.getProperties().forEach((key, value) ->
        System.out.printf("  %s: %s%n", key, value));
});
```

### Filter Operators

```java
// Equals
"PartitionKey eq 'Sales'"

// Not equals
"PartitionKey ne 'Sales'"

// Greater than
"Price gt 10.0"

// Greater than or equal
"Quantity ge 100"

// Less than
"Price lt 50.0"

// Less than or equal
"Quantity le 10"

// And
"PartitionKey eq 'Sales' and Price gt 10.0"

// Or
"Type eq 'Pen' or Type eq 'Marker'"
```

### List Tables

```java
import com.azure.data.tables.models.ListTablesOptions;
import com.azure.data.tables.models.TableItem;

// List all tables
for (TableItem tableItem : tableServiceClient.listTables()) {
    System.out.println(tableItem.getName());
}

// List with filter
ListTablesOptions options = new ListTablesOptions()
    .setFilter(String.format("TableName eq '%s'", tableName));

for (TableItem tableItem : tableServiceClient.listTables(options, null, null)) {
    System.out.println(tableItem.getName());
}
```

## Batch/Transactional Operations

All entities in a transaction must have the same partition key.

```java
import com.azure.data.tables.models.TableTransactionAction;
import com.azure.data.tables.models.TableTransactionActionType;
import com.azure.data.tables.models.TableTransactionResult;

import java.util.ArrayList;
import java.util.List;

List<TableTransactionAction> transactionActions = new ArrayList<>();

String partitionKey = "markers";  // All entities MUST have same partition key

// CREATE action
TableEntity firstEntity = new TableEntity(partitionKey, "m001")
    .addProperty("Type", "Dry")
    .addProperty("Color", "Red");
transactionActions.add(new TableTransactionAction(
    TableTransactionActionType.CREATE, 
    firstEntity
));

// CREATE action
TableEntity secondEntity = new TableEntity(partitionKey, "m002")
    .addProperty("Type", "Wet")
    .addProperty("Color", "Blue");
transactionActions.add(new TableTransactionAction(
    TableTransactionActionType.CREATE, 
    secondEntity
));

// UPDATE_MERGE action
TableEntity entityToUpdate = new TableEntity(partitionKey, "m003")
    .addProperty("Brand", "Crayola")
    .addProperty("Color", "Blue");
transactionActions.add(new TableTransactionAction(
    TableTransactionActionType.UPDATE_MERGE, 
    entityToUpdate
));

// DELETE action
TableEntity entityToDelete = new TableEntity(partitionKey, "m004");
transactionActions.add(new TableTransactionAction(
    TableTransactionActionType.DELETE, 
    entityToDelete
));

// Submit transaction
TableTransactionResult result = tableClient.submitTransaction(transactionActions);

// Check results
System.out.println("Transaction status codes:");
result.getTransactionActionResponses().forEach(response ->
    System.out.printf("  %d%n", response.getStatusCode()));
```

### Transaction Action Types

```java
TableTransactionActionType.CREATE          // Insert new entity
TableTransactionActionType.UPDATE_MERGE    // Merge with existing entity
TableTransactionActionType.UPDATE_REPLACE  // Replace entire entity
TableTransactionActionType.UPSERT_MERGE    // Insert or merge
TableTransactionActionType.UPSERT_REPLACE  // Insert or replace
TableTransactionActionType.DELETE          // Delete entity
```

## Async Client Patterns

### Create Async Clients

```java
import com.azure.data.tables.TableServiceAsyncClient;
import com.azure.data.tables.TableAsyncClient;

TableServiceAsyncClient asyncServiceClient = new TableServiceClientBuilder()
    .connectionString("<connection-string>")
    .buildAsyncClient();

TableAsyncClient asyncTableClient = new TableClientBuilder()
    .connectionString("<connection-string>")
    .tableName("myTable")
    .buildAsyncClient();
```

### Create Entity Async

```java
TableEntity entity = new TableEntity("partitionKey", "rowKey")
    .addProperty("Name", "Async Entity");

asyncTableClient.createEntity(entity)
    .subscribe(
        unused -> System.out.println("Entity created"),
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Completed")
    );
```

### Query Entities Async

```java
asyncTableClient.listEntities()
    .subscribe(
        entity -> System.out.printf("Entity: %s/%s%n", 
            entity.getPartitionKey(), 
            entity.getRowKey()),
        error -> System.err.println("Error: " + error.getMessage())
    );
```

### Transaction Async

```java
asyncTableClient.submitTransaction(transactionActions)
    .subscribe(
        result -> {
            System.out.println("Transaction completed");
            result.getTransactionActionResponses().forEach(r ->
                System.out.printf("Status: %d%n", r.getStatusCode()));
        },
        error -> System.err.println("Transaction failed: " + error.getMessage())
    );
```

## Error Handling

### Sync Error Handling

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.data.tables.models.TableServiceException;

try {
    tableClient.createEntity(entity);
} catch (TableServiceException e) {
    System.err.println("Table service error: " + e.getMessage());
    System.err.println("Status code: " + e.getResponse().getStatusCode());
    System.err.println("Error code: " + e.getValue().getErrorCode());
} catch (HttpResponseException e) {
    System.err.println("HTTP error: " + e.getResponse().getStatusCode());
} catch (Exception e) {
    System.err.println("Unexpected error: " + e.getMessage());
}
```

### Transaction Error Handling

```java
import com.azure.data.tables.models.TableTransactionFailedException;

try {
    tableClient.submitTransaction(transactionActions);
} catch (TableTransactionFailedException e) {
    System.err.println("Transaction failed");
    System.err.println("Failed action index: " + e.getFailedTransactionActionIndex());
    System.err.println("Status code: " + e.getResponse().getStatusCode());
}
```

### Async Error Handling

```java
asyncTableClient.createEntity(entity)
    .subscribe(
        unused -> System.out.println("Success"),
        error -> {
            if (error instanceof TableServiceException) {
                TableServiceException tse = (TableServiceException) error;
                System.err.println("Error code: " + tse.getValue().getErrorCode());
            } else {
                System.err.println("Error: " + error.getMessage());
            }
        }
    );
```
