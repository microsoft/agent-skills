# Azure Cosmos DB SDK for TypeScript Acceptance Criteria

**SDK**: `@azure/cosmos`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/cosmosdb/cosmos
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: ESM Imports

```typescript
import { CosmosClient } from "@azure/cosmos";
import { 
  CosmosClient,
  Database,
  Container,
  SqlQuerySpec,
  PatchOperation,
  BulkOperationType,
  OperationInput,
} from "@azure/cosmos";
```

### 1.2 ✅ CORRECT: Type Imports

```typescript
import type { 
  ItemResponse,
  FeedResponse,
  ResourceResponse,
  ErrorResponse,
} from "@azure/cosmos";
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: CommonJS require

```typescript
// WRONG - Use ESM imports
const { CosmosClient } = require("@azure/cosmos");
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: AAD with DefaultAzureCredential (Recommended)

```typescript
import { CosmosClient } from "@azure/cosmos";
import { DefaultAzureCredential } from "@azure/identity";

const client = new CosmosClient({
  endpoint: process.env.COSMOS_ENDPOINT!,
  aadCredentials: new DefaultAzureCredential(),
});
```

### 2.2 ✅ CORRECT: Key-Based Authentication

```typescript
import { CosmosClient } from "@azure/cosmos";

const client = new CosmosClient({
  endpoint: process.env.COSMOS_ENDPOINT!,
  key: process.env.COSMOS_KEY!,
});
```

### 2.3 ✅ CORRECT: Connection String

```typescript
import { CosmosClient } from "@azure/cosmos";

const client = new CosmosClient(process.env.COSMOS_CONNECTION_STRING!);
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials

```typescript
// WRONG - Never hardcode credentials
const client = new CosmosClient({
  endpoint: "https://myaccount.documents.azure.com:443/",
  key: "mySecretKey123=="  // SECURITY RISK
});
```

#### ❌ INCORRECT: Using credential instead of aadCredentials

```typescript
// WRONG - Use aadCredentials, not credential
const client = new CosmosClient({
  endpoint: process.env.COSMOS_ENDPOINT!,
  credential: new DefaultAzureCredential(),  // WRONG property name
});
```

---

## 3. Database and Container Operations

### 3.1 ✅ CORRECT: Create Database and Container

```typescript
const { database } = await client.databases.createIfNotExists({
  id: "my-database",
});

const { container } = await database.containers.createIfNotExists({
  id: "my-container",
  partitionKey: { paths: ["/partitionKey"] },
});
```

### 3.2 ✅ CORRECT: Get Database and Container Reference

```typescript
const database = client.database("my-database");
const container = database.container("my-container");
```

---

## 4. Document CRUD Operations

### 4.1 ✅ CORRECT: Create Document

```typescript
interface Product {
  id: string;
  partitionKey: string;
  name: string;
  price: number;
}

const item: Product = {
  id: "product-1",
  partitionKey: "electronics",
  name: "Laptop",
  price: 999.99,
};

const { resource } = await container.items.create<Product>(item);
```

### 4.2 ✅ CORRECT: Read Document (with partition key)

```typescript
const { resource } = await container
  .item("product-1", "electronics")  // id, partitionKey
  .read<Product>();

if (resource) {
  console.log(resource.name);
}
```

### 4.3 ✅ CORRECT: Update Document (Replace)

```typescript
const { resource: existing } = await container
  .item("product-1", "electronics")
  .read<Product>();

if (existing) {
  existing.price = 899.99;
  const { resource: updated } = await container
    .item("product-1", "electronics")
    .replace<Product>(existing);
}
```

### 4.4 ✅ CORRECT: Upsert Document

```typescript
const item: Product = {
  id: "product-1",
  partitionKey: "electronics",
  name: "Laptop Pro",
  price: 1299.99,
};

const { resource } = await container.items.upsert<Product>(item);
```

### 4.5 ✅ CORRECT: Delete Document

```typescript
await container.item("product-1", "electronics").delete();
```

### 4.6 ✅ CORRECT: Patch Document (Partial Update)

```typescript
import { PatchOperation } from "@azure/cosmos";

const operations: PatchOperation[] = [
  { op: "replace", path: "/price", value: 799.99 },
  { op: "add", path: "/discount", value: true },
  { op: "remove", path: "/oldField" },
];

const { resource } = await container
  .item("product-1", "electronics")
  .patch<Product>(operations);
```

### 4.7 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Read without partition key

```typescript
// WRONG - Must provide partition key value
const { resource } = await container.item("product-1").read();
```

---

## 5. Queries

### 5.1 ✅ CORRECT: Simple Query

```typescript
const { resources } = await container.items
  .query<Product>("SELECT * FROM c WHERE c.price < 1000")
  .fetchAll();
```

### 5.2 ✅ CORRECT: Parameterized Query (Recommended)

```typescript
import { SqlQuerySpec } from "@azure/cosmos";

const querySpec: SqlQuerySpec = {
  query: "SELECT * FROM c WHERE c.partitionKey = @category AND c.price < @maxPrice",
  parameters: [
    { name: "@category", value: "electronics" },
    { name: "@maxPrice", value: 1000 },
  ],
};

const { resources } = await container.items
  .query<Product>(querySpec)
  .fetchAll();
```

### 5.3 ✅ CORRECT: Query with Pagination

```typescript
const queryIterator = container.items.query<Product>(querySpec, {
  maxItemCount: 10,
});

while (queryIterator.hasMoreResults()) {
  const { resources, continuationToken } = await queryIterator.fetchNext();
  console.log(`Page with ${resources?.length} items`);
}
```

### 5.4 ✅ CORRECT: Cross-Partition Query

```typescript
const { resources } = await container.items
  .query<Product>(
    "SELECT * FROM c WHERE c.price > 500",
    { enableCrossPartitionQuery: true }
  )
  .fetchAll();
```

### 5.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: String concatenation in queries

```typescript
// WRONG - SQL injection risk, use parameterized queries
const category = userInput;
const query = `SELECT * FROM c WHERE c.category = '${category}'`;
```

---

## 6. Bulk Operations

### 6.1 ✅ CORRECT: Execute Bulk Operations

```typescript
import { BulkOperationType, OperationInput } from "@azure/cosmos";

const operations: OperationInput[] = [
  {
    operationType: BulkOperationType.Create,
    resourceBody: { id: "1", partitionKey: "cat-a", name: "Item 1" },
  },
  {
    operationType: BulkOperationType.Upsert,
    resourceBody: { id: "2", partitionKey: "cat-a", name: "Item 2" },
  },
  {
    operationType: BulkOperationType.Delete,
    id: "5",
    partitionKey: "cat-c",
  },
];

const response = await container.items.executeBulkOperations(operations);

response.forEach((result, index) => {
  if (result.statusCode >= 200 && result.statusCode < 300) {
    console.log(`Operation ${index} succeeded`);
  } else {
    console.error(`Operation ${index} failed: ${result.statusCode}`);
  }
});
```

---

## 7. Partition Keys

### 7.1 ✅ CORRECT: Simple Partition Key

```typescript
const { container } = await database.containers.createIfNotExists({
  id: "products",
  partitionKey: { paths: ["/category"] },
});
```

### 7.2 ✅ CORRECT: Hierarchical Partition Key (MultiHash)

```typescript
import { PartitionKeyDefinitionVersion, PartitionKeyKind } from "@azure/cosmos";

const { container } = await database.containers.createIfNotExists({
  id: "orders",
  partitionKey: {
    paths: ["/tenantId", "/userId", "/sessionId"],
    version: PartitionKeyDefinitionVersion.V2,
    kind: PartitionKeyKind.MultiHash,
  },
});

// Operations require array of partition key values
const { resource } = await container
  .item("order-1", ["tenant-a", "user-123", "session-xyz"])
  .read();
```

---

## 8. Error Handling

### 8.1 ✅ CORRECT: Handle Cosmos Errors

```typescript
import { ErrorResponse } from "@azure/cosmos";

try {
  const { resource } = await container.item("missing", "pk").read();
} catch (error) {
  if (error instanceof ErrorResponse) {
    switch (error.code) {
      case 404:
        console.log("Document not found");
        break;
      case 409:
        console.log("Conflict - document already exists");
        break;
      case 412:
        console.log("Precondition failed (ETag mismatch)");
        break;
      case 429:
        console.log("Rate limited - retry after:", error.retryAfterInMs);
        break;
      default:
        console.error(`Cosmos error ${error.code}: ${error.message}`);
    }
  }
  throw error;
}
```

---

## 9. Optimistic Concurrency (ETags)

### 9.1 ✅ CORRECT: Use ETags for Concurrency Control

```typescript
const { resource, etag } = await container
  .item("product-1", "electronics")
  .read<Product>();

if (resource && etag) {
  resource.price = 899.99;
  
  try {
    await container.item("product-1", "electronics").replace(resource, {
      accessCondition: { type: "IfMatch", condition: etag },
    });
  } catch (error) {
    if (error instanceof ErrorResponse && error.code === 412) {
      console.log("Document was modified by another process");
    }
  }
}
```

---

## 10. Best Practices

### 10.1 ✅ CORRECT: Service Layer Pattern

```typescript
export class ProductService {
  private container: Container;

  constructor(client: CosmosClient) {
    this.container = client
      .database(process.env.COSMOS_DATABASE!)
      .container(process.env.COSMOS_CONTAINER!);
  }

  async getById(id: string, category: string): Promise<Product | null> {
    try {
      const { resource } = await this.container
        .item(id, category)
        .read<Product>();
      return resource ?? null;
    } catch (error) {
      if (error instanceof ErrorResponse && error.code === 404) {
        return null;
      }
      throw error;
    }
  }

  async create(product: Omit<Product, "id">): Promise<Product> {
    const item = { ...product, id: crypto.randomUUID() };
    const { resource } = await this.container.items.create<Product>(item);
    return resource!;
  }

  async findByCategory(category: string): Promise<Product[]> {
    const querySpec: SqlQuerySpec = {
      query: "SELECT * FROM c WHERE c.partitionKey = @category",
      parameters: [{ name: "@category", value: category }],
    };
    const { resources } = await this.container.items
      .query<Product>(querySpec)
      .fetchAll();
    return resources;
  }
}
```
