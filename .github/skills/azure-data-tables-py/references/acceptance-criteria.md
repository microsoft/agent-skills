# Azure Data Tables SDK Acceptance Criteria

**SDK**: `azure-data-tables`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Clients
```python
from azure.data.tables import TableServiceClient, TableClient, UpdateMode, TableTransactionError
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Clients
```python
from azure.data.tables.aio import TableServiceClient, TableClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module paths
```python
# WRONG - module does not exist
from azure.data.table import TableClient

# WRONG - legacy Cosmos Table SDK
from azure.cosmosdb.table import TableService

# WRONG - models are not in this module
from azure.data.tables.models import TableClient
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: DefaultAzureCredential with endpoint
```python
import os
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

service_client = TableServiceClient(
    endpoint=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
    credential=credential,
)
```

### 2.2 ✅ CORRECT: Connection string (Alternative)
```python
import os
from azure.data.tables import TableServiceClient

service_client = TableServiceClient.from_connection_string(
    conn_str=os.environ["AZURE_STORAGE_CONNECTION_STRING"],
)
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - hardcoded account key/connection string
service_client = TableServiceClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=..."
)
```

#### ❌ INCORRECT: Wrong parameter name
```python
# WRONG - TableServiceClient uses `endpoint`, not `url`
service_client = TableServiceClient(url=endpoint, credential=credential)
```

---

## 3. TableServiceClient Patterns

### 3.1 ✅ CORRECT: Table management
```python
table_name = "orders"

service_client.create_table_if_not_exists(table_name)

table_client = service_client.get_table_client(table_name)

for table in service_client.list_tables():
    print(table.name)
```

### 3.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong method name
```python
# WRONG - method does not exist
service_client.create_table_if_missing("orders")
```

---

## 4. TableClient Patterns

### 4.1 ✅ CORRECT: Create TableClient
```python
table_client = TableClient(
    endpoint=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
    table_name="orders",
    credential=DefaultAzureCredential(),
)
```

### 4.2 ✅ CORRECT: Entity CRUD operations
```python
entity = {
    "PartitionKey": "sales",
    "RowKey": "order-001",
    "product": "Widget",
    "quantity": 2,
}

table_client.create_entity(entity=entity)

table_client.upsert_entity(entity=entity, mode=UpdateMode.MERGE)

fetched = table_client.get_entity(
    partition_key="sales",
    row_key="order-001",
)

table_client.update_entity(
    entity={"PartitionKey": "sales", "RowKey": "order-001", "quantity": 3},
    mode=UpdateMode.REPLACE,
)

table_client.delete_entity(partition_key="sales", row_key="order-001")
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing required keys
```python
# WRONG - PartitionKey/RowKey required for entity operations
table_client.create_entity(entity={"product": "Widget"})
```

#### ❌ INCORRECT: Wrong key casing
```python
# WRONG - must be PartitionKey/RowKey, not snake_case
table_client.upsert_entity(entity={"partition_key": "sales", "row_key": "1"})
```

---

## 5. Entity CRUD Patterns

### 5.1 ✅ CORRECT: Query entities with filter
```python
entities = table_client.query_entities(
    query_filter="PartitionKey eq 'sales'"
)

for entity in entities:
    print(entity)
```

### 5.2 ✅ CORRECT: Parameterized query
```python
entities = table_client.query_entities(
    query_filter="PartitionKey eq @pk and quantity gt @min_qty",
    parameters={"pk": "sales", "min_qty": 1},
)
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong filter parameter name
```python
# WRONG - use query_filter, not filter
entities = table_client.query_entities(filter="PartitionKey eq 'sales'")
```

---

## 6. Batch Operations

### 6.1 ✅ CORRECT: submit_transaction
```python
operations = [
    ("create", {"PartitionKey": "batch", "RowKey": "1", "value": 1}),
    ("upsert", {"PartitionKey": "batch", "RowKey": "2", "value": 2}),
]

try:
    table_client.submit_transaction(operations)
except TableTransactionError as exc:
    print(f"Transaction failed: {exc}")
```

### 6.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong method name
```python
# WRONG - method does not exist
table_client.submit_batch(operations)
```

---

## 7. PartitionKey/RowKey Requirements

### 7.1 ✅ CORRECT: Explicit PartitionKey/RowKey
```python
entity = {
    "PartitionKey": "inventory",
    "RowKey": "sku-1001",
    "name": "Keyboard",
}
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing RowKey
```python
# WRONG - RowKey required
entity = {"PartitionKey": "inventory", "name": "Keyboard"}
```
