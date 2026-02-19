# Azure Cosmos DB SDK Acceptance Criteria

**SDK**: `azure-cosmos`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `5c5d6eb014da472e71937aceddbf2f19fdb9aa40`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Client
```python
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Client
```python
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential
```

#### ✅ CORRECT: Exceptions (Optional)
```python
from azure.cosmos import exceptions
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module for identity
```python
# WRONG - DefaultAzureCredential is in azure.identity
from azure.cosmos import DefaultAzureCredential
```

#### ❌ INCORRECT: Wrong module for PartitionKey
```python
# WRONG - PartitionKey is not in azure.cosmos.aio
from azure.cosmos.aio import PartitionKey
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: DefaultAzureCredential (AAD)
```python
import os
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = CosmosClient(
    url=os.environ["ACCOUNT_URI"],
    credential=credential,
)
```

### 2.2 ✅ CORRECT: Connection String
```python
import os
from azure.cosmos import CosmosClient

client = CosmosClient.from_connection_string(
    conn_str=os.environ["AZURE_COSMOS_CONNECTIONSTRING"],
)
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Passing connection string as URL
```python
# WRONG - conn string is not the account URL
client = CosmosClient(
    url=os.environ["AZURE_COSMOS_CONNECTIONSTRING"],
    credential=os.environ["ACCOUNT_KEY"],
)
```

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - do not hardcode secrets
client = CosmosClient(
    url="https://my-account.documents.azure.com:443/",
    credential="<account-key>",
)
```

---

## 3. CosmosClient Creation Patterns

### 3.1 ✅ CORRECT: Constructor Parameters
```python
from azure.cosmos import CosmosClient

client = CosmosClient(url=account_url, credential=credential)
```

### 3.2 ✅ CORRECT: From Connection String
```python
from azure.cosmos import CosmosClient

client = CosmosClient.from_connection_string(conn_str=connection_string)
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter name
```python
# WRONG - CosmosClient expects url, not endpoint
client = CosmosClient(endpoint=account_url, credential=credential)
```

---

## 4. Database and Container Operations

### 4.1 ✅ CORRECT: Create Database and Container
```python
from azure.cosmos import PartitionKey

database = client.create_database_if_not_exists(id="mydb")
container = database.create_container_if_not_exists(
    id="mycontainer",
    partition_key=PartitionKey(path="/category"),
)
```

### 4.2 ✅ CORRECT: Get Existing Database and Container
```python
database = client.get_database_client("mydb")
container = database.get_container_client("mycontainer")
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing PartitionKey
```python
# WRONG - partition_key is required
container = database.create_container_if_not_exists(
    id="mycontainer",
)
```

#### ❌ INCORRECT: Partition key not wrapped with PartitionKey
```python
# WRONG - partition_key must be a PartitionKey
container = database.create_container_if_not_exists(
    id="mycontainer",
    partition_key="/category",
)
```

---

## 5. Document CRUD Operations

### 5.1 ✅ CORRECT: Create Item
```python
item = {"id": "item-1", "category": "electronics", "name": "Laptop"}
container.create_item(body=item)
```

### 5.2 ✅ CORRECT: Read Item (Point Read)
```python
item = container.read_item(item="item-1", partition_key="electronics")
```

### 5.3 ✅ CORRECT: Replace Item
```python
item["price"] = 899.0
container.replace_item(item=item["id"], body=item)
```

### 5.4 ✅ CORRECT: Upsert Item
```python
container.upsert_item(body=item)
```

### 5.5 ✅ CORRECT: Delete Item
```python
container.delete_item(item="item-1", partition_key="electronics")
```

### 5.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing partition key on point read
```python
# WRONG - partition_key is required for point reads
container.read_item(item="item-1")
```

#### ❌ INCORRECT: Missing partition key on delete
```python
# WRONG - partition_key is required for deletes
container.delete_item(item="item-1")
```

#### ❌ INCORRECT: Wrong parameter name for read_item
```python
# WRONG - parameter name is item, not item_id
container.read_item(item_id="item-1", partition_key="electronics")
```

---

## 6. Query Patterns

### 6.1 ✅ CORRECT: Parameterized Query (Single Partition)
```python
query = "SELECT * FROM c WHERE c.category = @category"
items = container.query_items(
    query=query,
    parameters=[{"name": "@category", "value": "electronics"}],
    partition_key="electronics",
)
```

### 6.2 ✅ CORRECT: Cross-Partition Query
```python
query = "SELECT * FROM c WHERE c.price < @max_price"
items = container.query_items(
    query=query,
    parameters=[{"name": "@max_price", "value": 500}],
    enable_cross_partition_query=True,
)
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing partition key or cross-partition flag
```python
# WRONG - must provide partition_key or enable_cross_partition_query
items = container.query_items(
    query="SELECT * FROM c",
)
```

---

## 7. Partition Key Patterns

### 7.1 ✅ CORRECT: Single Partition Key
```python
from azure.cosmos import PartitionKey

PartitionKey(path="/category")
```

### 7.2 ✅ CORRECT: Hierarchical Partition Key (Preview)
```python
from azure.cosmos import PartitionKey

PartitionKey(path=["/tenant_id", "/user_id"], kind="MultiHash")
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing leading slash
```python
# WRONG - partition key paths must start with '/'
PartitionKey(path="category")
```

---

## 8. Environment Variables

### Required Variables
```bash
ACCOUNT_URI=https://<account>.documents.azure.com:443/
ACCOUNT_KEY=<primary-key>
```

### Optional Variables
```bash
AZURE_COSMOS_CONNECTIONSTRING=AccountEndpoint=https://<account>.documents.azure.com:443/;AccountKey=<key>;
```

---

## 9. Test Scenarios Checklist

### Basic Operations
- [ ] Client creation using DefaultAzureCredential
- [ ] Client creation using connection string
- [ ] Database and container creation with PartitionKey
- [ ] Container retrieval and item CRUD

### Queries
- [ ] Parameterized query with partition key
- [ ] Cross-partition query with enable_cross_partition_query

### Async
- [ ] Async client with async/await and context manager
