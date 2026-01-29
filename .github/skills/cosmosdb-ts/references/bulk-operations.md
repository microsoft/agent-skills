# Bulk Operations Reference

High-throughput bulk operations for Azure Cosmos DB using the @azure/cosmos TypeScript SDK.

## Overview

Bulk operations enable efficient batch processing of Create, Upsert, Read, Replace, Delete, and Patch operations with automatic batching and retry handling.

## BulkOperationType Enum

```typescript
import { BulkOperationType } from "@azure/cosmos";

enum BulkOperationType {
  Create = "Create",
  Upsert = "Upsert",
  Read = "Read",
  Replace = "Replace",
  Delete = "Delete",
  Patch = "Patch"
}
```

## OperationInput Interface

```typescript
import { OperationInput, PatchOperation } from "@azure/cosmos";

// Base operation types
interface CreateOperationInput {
  operationType: BulkOperationType.Create;
  resourceBody: Record<string, unknown>;
  partitionKey?: PartitionKey;
}

interface UpsertOperationInput {
  operationType: BulkOperationType.Upsert;
  resourceBody: Record<string, unknown>;
  partitionKey?: PartitionKey;
}

interface ReadOperationInput {
  operationType: BulkOperationType.Read;
  id: string;
  partitionKey: PartitionKey;
}

interface ReplaceOperationInput {
  operationType: BulkOperationType.Replace;
  id: string;
  resourceBody: Record<string, unknown>;
  partitionKey?: PartitionKey;
}

interface DeleteOperationInput {
  operationType: BulkOperationType.Delete;
  id: string;
  partitionKey: PartitionKey;
}

interface PatchOperationInput {
  operationType: BulkOperationType.Patch;
  id: string;
  partitionKey: PartitionKey;
  resourceBody: {
    operations: PatchOperation[];
    condition?: string;
  };
}

type OperationInput = 
  | CreateOperationInput
  | UpsertOperationInput
  | ReadOperationInput
  | ReplaceOperationInput
  | DeleteOperationInput
  | PatchOperationInput;
```

## Basic Bulk Operations

```typescript
import { 
  CosmosClient, 
  BulkOperationType, 
  OperationInput,
  BulkOperationResponse 
} from "@azure/cosmos";

const client = new CosmosClient({ endpoint, key });
const container = client.database("mydb").container("mycontainer");

// Mixed bulk operations
const operations: OperationInput[] = [
  // Create
  {
    operationType: BulkOperationType.Create,
    resourceBody: { 
      id: "item-1", 
      partitionKey: "category-a", 
      name: "Item 1",
      price: 10.99
    }
  },
  // Upsert
  {
    operationType: BulkOperationType.Upsert,
    resourceBody: { 
      id: "item-2", 
      partitionKey: "category-a", 
      name: "Item 2",
      price: 20.99
    }
  },
  // Read
  {
    operationType: BulkOperationType.Read,
    id: "item-3",
    partitionKey: "category-b"
  },
  // Replace
  {
    operationType: BulkOperationType.Replace,
    id: "item-4",
    partitionKey: "category-b",
    resourceBody: { 
      id: "item-4", 
      partitionKey: "category-b", 
      name: "Updated Item 4",
      price: 15.99
    }
  },
  // Delete
  {
    operationType: BulkOperationType.Delete,
    id: "item-5",
    partitionKey: "category-c"
  }
];

const response: BulkOperationResponse = await container.items.bulk(operations);

// Process results
response.forEach((result, index) => {
  if (result.statusCode >= 200 && result.statusCode < 300) {
    console.log(`Operation ${index} succeeded: ${result.statusCode}`);
    if (result.resourceBody) {
      console.log(`  Resource: ${JSON.stringify(result.resourceBody)}`);
    }
  } else {
    console.error(`Operation ${index} failed: ${result.statusCode}`);
  }
});
```

## Bulk Create Pattern

```typescript
interface Product {
  id: string;
  partitionKey: string;
  name: string;
  price: number;
}

async function bulkCreate(
  container: Container,
  items: Product[]
): Promise<{ succeeded: number; failed: number }> {
  const operations: OperationInput[] = items.map(item => ({
    operationType: BulkOperationType.Create,
    resourceBody: item
  }));

  const response = await container.items.bulk(operations);

  let succeeded = 0;
  let failed = 0;

  response.forEach((result, index) => {
    if (result.statusCode === 201) {
      succeeded++;
    } else {
      failed++;
      console.error(`Failed to create item ${items[index].id}: ${result.statusCode}`);
    }
  });

  return { succeeded, failed };
}

// Usage
const products: Product[] = [
  { id: "p1", partitionKey: "electronics", name: "Laptop", price: 999 },
  { id: "p2", partitionKey: "electronics", name: "Phone", price: 599 },
  { id: "p3", partitionKey: "clothing", name: "Shirt", price: 29 },
];

const result = await bulkCreate(container, products);
console.log(`Created: ${result.succeeded}, Failed: ${result.failed}`);
```

## Bulk Upsert Pattern

```typescript
async function bulkUpsert<T extends { id: string }>(
  container: Container,
  items: T[]
): Promise<BulkOperationResponse> {
  const operations: OperationInput[] = items.map(item => ({
    operationType: BulkOperationType.Upsert,
    resourceBody: item as Record<string, unknown>
  }));

  return container.items.bulk(operations);
}

// Usage - creates if not exists, updates if exists
const updates = [
  { id: "p1", partitionKey: "electronics", name: "Laptop Pro", price: 1299 },
  { id: "p4", partitionKey: "electronics", name: "Tablet", price: 399 },
];

await bulkUpsert(container, updates);
```

## Bulk Delete Pattern

```typescript
interface DeleteItem {
  id: string;
  partitionKey: string;
}

async function bulkDelete(
  container: Container,
  items: DeleteItem[]
): Promise<{ deleted: number; notFound: number; errors: number }> {
  const operations: OperationInput[] = items.map(item => ({
    operationType: BulkOperationType.Delete,
    id: item.id,
    partitionKey: item.partitionKey
  }));

  const response = await container.items.bulk(operations);

  let deleted = 0;
  let notFound = 0;
  let errors = 0;

  response.forEach((result) => {
    if (result.statusCode === 204) {
      deleted++;
    } else if (result.statusCode === 404) {
      notFound++;
    } else {
      errors++;
    }
  });

  return { deleted, notFound, errors };
}

// Usage
const toDelete: DeleteItem[] = [
  { id: "p1", partitionKey: "electronics" },
  { id: "p2", partitionKey: "electronics" },
];

const deleteResult = await bulkDelete(container, toDelete);
console.log(`Deleted: ${deleteResult.deleted}, Not found: ${deleteResult.notFound}`);
```

## Bulk Patch Pattern

```typescript
import { PatchOperation } from "@azure/cosmos";

interface PatchItem {
  id: string;
  partitionKey: string;
  operations: PatchOperation[];
}

async function bulkPatch(
  container: Container,
  items: PatchItem[]
): Promise<BulkOperationResponse> {
  const operations: OperationInput[] = items.map(item => ({
    operationType: BulkOperationType.Patch,
    id: item.id,
    partitionKey: item.partitionKey,
    resourceBody: {
      operations: item.operations
    }
  }));

  return container.items.bulk(operations);
}

// Usage - partial updates
const patches: PatchItem[] = [
  {
    id: "p1",
    partitionKey: "electronics",
    operations: [
      { op: "replace", path: "/price", value: 899 },
      { op: "add", path: "/onSale", value: true }
    ]
  },
  {
    id: "p2",
    partitionKey: "electronics",
    operations: [
      { op: "incr", path: "/viewCount", value: 1 }
    ]
  }
];

await bulkPatch(container, patches);
```

## Chunked Bulk Operations

For very large datasets, process in chunks to manage memory and handle rate limiting:

```typescript
async function bulkOperationsChunked<T extends Record<string, unknown>>(
  container: Container,
  items: T[],
  operationType: BulkOperationType.Create | BulkOperationType.Upsert,
  chunkSize: number = 100
): Promise<{ succeeded: number; failed: number }> {
  let succeeded = 0;
  let failed = 0;

  // Process in chunks
  for (let i = 0; i < items.length; i += chunkSize) {
    const chunk = items.slice(i, i + chunkSize);
    
    const operations: OperationInput[] = chunk.map(item => ({
      operationType,
      resourceBody: item
    }));

    const response = await container.items.bulk(operations);

    response.forEach(result => {
      if (result.statusCode >= 200 && result.statusCode < 300) {
        succeeded++;
      } else {
        failed++;
      }
    });

    console.log(`Processed ${Math.min(i + chunkSize, items.length)}/${items.length}`);
  }

  return { succeeded, failed };
}

// Usage
const largeDataset = generateItems(10000);
const result = await bulkOperationsChunked(container, largeDataset, BulkOperationType.Create, 100);
```

## Bulk Operation Response

```typescript
interface BulkOperationResponse extends Array<OperationResponse> {}

interface OperationResponse {
  /** HTTP status code */
  statusCode: number;
  
  /** Request charge (RUs) for this operation */
  requestCharge: number;
  
  /** ETag of the resource (for successful operations) */
  eTag?: string;
  
  /** Resource body (for read/create/upsert/replace) */
  resourceBody?: Record<string, unknown>;
}

// Common status codes
// 200 - Read successful
// 201 - Create successful
// 204 - Delete successful
// 400 - Bad request
// 404 - Not found
// 409 - Conflict (duplicate id on create)
// 412 - Precondition failed
// 429 - Rate limited
```

## Error Handling

```typescript
async function bulkWithRetry(
  container: Container,
  operations: OperationInput[],
  maxRetries: number = 3
): Promise<BulkOperationResponse> {
  let response = await container.items.bulk(operations);
  let retryCount = 0;

  while (retryCount < maxRetries) {
    const failedOps: OperationInput[] = [];
    const failedIndices: number[] = [];

    response.forEach((result, index) => {
      if (result.statusCode === 429) {
        // Rate limited - retry these
        failedOps.push(operations[index]);
        failedIndices.push(index);
      }
    });

    if (failedOps.length === 0) {
      break; // All succeeded
    }

    console.log(`Retrying ${failedOps.length} rate-limited operations...`);
    
    // Exponential backoff
    await new Promise(resolve => 
      setTimeout(resolve, Math.pow(2, retryCount) * 1000)
    );

    const retryResponse = await container.items.bulk(failedOps);
    
    // Update original response with retry results
    retryResponse.forEach((result, i) => {
      response[failedIndices[i]] = result;
    });

    retryCount++;
  }

  return response;
}
```

## Best Practices

1. **Batch by partition key** — Operations in the same partition are more efficient
2. **Use appropriate chunk sizes** — 100-500 items per batch is typical
3. **Handle 429 errors** — Implement retry with exponential backoff
4. **Monitor RU consumption** — Check `requestCharge` in responses
5. **Use Upsert for idempotency** — Safer than Create for retry scenarios
6. **Validate before bulk** — Check data before submitting large batches
7. **Process results** — Always check individual operation status codes

## Performance Considerations

| Factor | Recommendation |
|--------|----------------|
| Chunk size | 100-500 items per batch |
| Partition distribution | Spread across partitions for parallelism |
| Operation type | Upsert is safer than Create for retries |
| Error handling | Implement retry logic for 429s |
| Memory | Stream large datasets, don't load all into memory |

## See Also

- [Query Patterns Reference](./query-patterns.md)
- [Cosmos DB Bulk Execution](https://learn.microsoft.com/azure/cosmos-db/nosql/tutorial-dotnet-bulk-import)
- [Request Units (RUs)](https://learn.microsoft.com/azure/cosmos-db/request-units)
