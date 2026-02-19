# Query Patterns Reference

Advanced query patterns for Azure Cosmos DB using the @azure/cosmos TypeScript SDK.

## Overview

Cosmos DB supports SQL-like queries with support for JSON documents. This reference covers parameterized queries, pagination, cross-partition queries, and advanced query patterns.

## SqlQuerySpec Interface

```typescript
import { SqlQuerySpec, SqlParameter } from "@azure/cosmos";

interface SqlQuerySpec {
  /** SQL query text */
  query: string;
  /** Array of parameters */
  parameters?: SqlParameter[];
}

interface SqlParameter {
  /** Parameter name (including @) */
  name: string;
  /** Parameter value */
  value: unknown;
}
```

## Parameterized Queries (Recommended)

Always use parameterized queries to prevent injection and improve plan caching.

```typescript
import { SqlQuerySpec, Container } from "@azure/cosmos";

interface Product {
  id: string;
  category: string;
  name: string;
  price: number;
  inStock: boolean;
}

// Single parameter
const querySpec: SqlQuerySpec = {
  query: "SELECT * FROM c WHERE c.category = @category",
  parameters: [
    { name: "@category", value: "electronics" }
  ]
};

const { resources } = await container.items
  .query<Product>(querySpec)
  .fetchAll();

// Multiple parameters
const rangeQuery: SqlQuerySpec = {
  query: `
    SELECT * FROM c 
    WHERE c.category = @category 
      AND c.price >= @minPrice 
      AND c.price <= @maxPrice
      AND c.inStock = @inStock
  `,
  parameters: [
    { name: "@category", value: "electronics" },
    { name: "@minPrice", value: 100 },
    { name: "@maxPrice", value: 1000 },
    { name: "@inStock", value: true }
  ]
};

const { resources: filtered } = await container.items
  .query<Product>(rangeQuery)
  .fetchAll();
```

## Pagination with Continuation Tokens

```typescript
import { FeedOptions } from "@azure/cosmos";

interface PagedResult<T> {
  items: T[];
  continuationToken?: string;
  hasMore: boolean;
}

async function queryWithPagination<T>(
  container: Container,
  querySpec: SqlQuerySpec,
  pageSize: number,
  continuationToken?: string
): Promise<PagedResult<T>> {
  const options: FeedOptions = {
    maxItemCount: pageSize,
    continuationToken
  };

  const queryIterator = container.items.query<T>(querySpec, options);
  const { resources, continuationToken: nextToken } = await queryIterator.fetchNext();

  return {
    items: resources || [],
    continuationToken: nextToken,
    hasMore: !!nextToken
  };
}

// Usage
let page = await queryWithPagination<Product>(
  container,
  { query: "SELECT * FROM c ORDER BY c.createdAt DESC" },
  10
);

console.log(`Page 1: ${page.items.length} items`);

while (page.hasMore) {
  page = await queryWithPagination<Product>(
    container,
    { query: "SELECT * FROM c ORDER BY c.createdAt DESC" },
    10,
    page.continuationToken
  );
  console.log(`Next page: ${page.items.length} items`);
}
```

## Async Iterator Pattern

```typescript
async function* queryAll<T>(
  container: Container,
  querySpec: SqlQuerySpec
): AsyncGenerator<T> {
  const queryIterator = container.items.query<T>(querySpec);
  
  while (queryIterator.hasMoreResults()) {
    const { resources } = await queryIterator.fetchNext();
    if (resources) {
      for (const item of resources) {
        yield item;
      }
    }
  }
}

// Usage
for await (const product of queryAll<Product>(container, querySpec)) {
  console.log(product.name);
}
```

## Cross-Partition Queries

```typescript
// Enable cross-partition query when partition key is not specified
const crossPartitionQuery: SqlQuerySpec = {
  query: "SELECT * FROM c WHERE c.price > @minPrice",
  parameters: [{ name: "@minPrice", value: 500 }]
};

const { resources } = await container.items
  .query<Product>(crossPartitionQuery, {
    enableCrossPartitionQuery: true
  })
  .fetchAll();

// Aggregate across partitions
const aggregateQuery: SqlQuerySpec = {
  query: "SELECT VALUE COUNT(1) FROM c WHERE c.category = @category",
  parameters: [{ name: "@category", value: "electronics" }]
};

const { resources: countResult } = await container.items
  .query<number>(aggregateQuery, { enableCrossPartitionQuery: true })
  .fetchAll();

console.log(`Total count: ${countResult[0]}`);
```

## Projection Queries

```typescript
// Select specific fields
const projectionQuery: SqlQuerySpec = {
  query: `
    SELECT c.id, c.name, c.price, c.category
    FROM c
    WHERE c.inStock = true
  `
};

interface ProductSummary {
  id: string;
  name: string;
  price: number;
  category: string;
}

const { resources } = await container.items
  .query<ProductSummary>(projectionQuery)
  .fetchAll();

// Computed properties
const computedQuery: SqlQuerySpec = {
  query: `
    SELECT 
      c.id,
      c.name,
      c.price,
      c.price * 0.9 AS discountedPrice,
      CONCAT(c.category, "-", c.id) AS sku
    FROM c
  `
};
```

## Array Queries (JOIN)

```typescript
interface Order {
  id: string;
  customerId: string;
  items: OrderItem[];
}

interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
}

// Query items within arrays
const arrayQuery: SqlQuerySpec = {
  query: `
    SELECT 
      o.id AS orderId,
      o.customerId,
      i.productId,
      i.quantity,
      i.price
    FROM orders o
    JOIN i IN o.items
    WHERE i.quantity > @minQuantity
  `,
  parameters: [{ name: "@minQuantity", value: 5 }]
};

// Check if array contains value
const containsQuery: SqlQuerySpec = {
  query: `
    SELECT * FROM c 
    WHERE ARRAY_CONTAINS(c.tags, @tag)
  `,
  parameters: [{ name: "@tag", value: "featured" }]
};
```

## Aggregate Functions

```typescript
// COUNT
const countQuery = { query: "SELECT VALUE COUNT(1) FROM c" };

// SUM, AVG, MIN, MAX
const statsQuery: SqlQuerySpec = {
  query: `
    SELECT 
      COUNT(1) AS totalProducts,
      SUM(c.price) AS totalValue,
      AVG(c.price) AS averagePrice,
      MIN(c.price) AS minPrice,
      MAX(c.price) AS maxPrice
    FROM c
    WHERE c.category = @category
  `,
  parameters: [{ name: "@category", value: "electronics" }]
};

interface ProductStats {
  totalProducts: number;
  totalValue: number;
  averagePrice: number;
  minPrice: number;
  maxPrice: number;
}

const { resources } = await container.items
  .query<ProductStats>(statsQuery, { enableCrossPartitionQuery: true })
  .fetchAll();
```

## ORDER BY and TOP

```typescript
// Order by with TOP
const topQuery: SqlQuerySpec = {
  query: `
    SELECT TOP 10 *
    FROM c
    WHERE c.category = @category
    ORDER BY c.price DESC
  `,
  parameters: [{ name: "@category", value: "electronics" }]
};

// Multiple ORDER BY
const multiOrderQuery: SqlQuerySpec = {
  query: `
    SELECT * FROM c
    ORDER BY c.category ASC, c.price DESC
  `
};

// OFFSET and LIMIT (alternative to continuation tokens)
const offsetQuery: SqlQuerySpec = {
  query: `
    SELECT * FROM c
    ORDER BY c.createdAt DESC
    OFFSET @offset LIMIT @limit
  `,
  parameters: [
    { name: "@offset", value: 20 },
    { name: "@limit", value: 10 }
  ]
};
```

## String Functions

```typescript
const stringQuery: SqlQuerySpec = {
  query: `
    SELECT * FROM c
    WHERE CONTAINS(c.name, @searchTerm, true)
      OR STARTSWITH(c.name, @prefix)
  `,
  parameters: [
    { name: "@searchTerm", value: "phone" },
    { name: "@prefix", value: "Smart" }
  ]
};

// Case-insensitive search with LOWER
const caseInsensitiveQuery: SqlQuerySpec = {
  query: `
    SELECT * FROM c
    WHERE LOWER(c.name) LIKE @pattern
  `,
  parameters: [{ name: "@pattern", value: "%laptop%" }]
};
```

## FeedOptions Reference

```typescript
interface FeedOptions {
  /** Max items per page */
  maxItemCount?: number;
  
  /** Continuation token from previous page */
  continuationToken?: string;
  
  /** Enable cross-partition queries */
  enableCrossPartitionQuery?: boolean;
  
  /** Max parallelism for cross-partition queries */
  maxDegreeOfParallelism?: number;
  
  /** Partition key for scoped queries */
  partitionKey?: PartitionKey;
  
  /** Enable scan in queries (avoid if possible) */
  enableScanInQuery?: boolean;
  
  /** Populate index metrics in response */
  populateIndexMetrics?: boolean;
}
```

## Query Performance Tips

1. **Always specify partition key** — Avoids expensive cross-partition queries
2. **Use parameterized queries** — Enables query plan caching
3. **Project only needed fields** — Reduces response size and RU consumption
4. **Avoid cross-partition aggregates** — Very expensive; consider materialized views
5. **Use continuation tokens** — More efficient than OFFSET/LIMIT
6. **Check index metrics** — Use `populateIndexMetrics: true` to diagnose slow queries

## See Also

- [Bulk Operations Reference](./bulk-operations.md)
- [Azure Cosmos DB SQL Reference](https://learn.microsoft.com/azure/cosmos-db/nosql/query/)
- [Query Performance Tips](https://learn.microsoft.com/azure/cosmos-db/nosql/query-metrics)
