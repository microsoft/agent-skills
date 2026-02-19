# Acceptance Criteria: azure-search-documents-ts

## Overview

This document defines the acceptance criteria for code generated using the `@azure/search-documents` SDK for TypeScript/JavaScript.

**Package:** `@azure/search-documents`  
**Repository:** https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/search/search-documents

---

## 1. Import Statements

### ✅ MUST

```typescript
// ESM imports
import {
  SearchClient,
  SearchIndexClient,
  SearchIndexerClient,
  AzureKeyCredential,
} from "@azure/search-documents";
import { DefaultAzureCredential } from "@azure/identity";
```

### ❌ MUST NOT

```typescript
// CommonJS require
const { SearchClient } = require("@azure/search-documents");

// Old package names
import { SearchServiceClient } from "azure-search";
```

---

## 2. Client Instantiation

### SearchClient (for querying)

```typescript
// ✅ Correct - with DefaultAzureCredential
const credential = new DefaultAzureCredential();
const client = new SearchClient("<endpoint>", "<indexName>", credential);

// ✅ Correct - with API key
const client = new SearchClient(
  "<endpoint>",
  "<indexName>",
  new AzureKeyCredential("<apiKey>")
);
```

### SearchIndexClient (for index management)

```typescript
// ✅ Correct
const indexClient = new SearchIndexClient("<endpoint>", credential);
const indexClient = new SearchIndexClient("<endpoint>", new AzureKeyCredential("<apiKey>"));
```

### SearchIndexerClient (for indexers)

```typescript
// ✅ Correct
const indexerClient = new SearchIndexerClient("<endpoint>", credential);
```

### ❌ MUST NOT

```typescript
// Hardcoded credentials
const client = new SearchClient(endpoint, indexName, "api-key-string");

// Missing index name for SearchClient
const client = new SearchClient(endpoint, credential);
```

---

## 3. Search Operations

### Basic Search

```typescript
// ✅ Correct - async iteration
const results = await searchClient.search("wifi -luxury");
for await (const result of results.results) {
  console.log(result.document);
}

// ✅ Correct - with options
const results = await searchClient.search("wifi", {
  select: ["hotelId", "hotelName"],
  filter: "rating ge 4",
  orderBy: ["rating desc"],
  top: 10,
});
```

### Vector Search

```typescript
// ✅ Correct - vector query
const results = await searchClient.search("*", {
  vectorSearchOptions: {
    queries: [
      {
        kind: "vector",
        vector: queryVector,
        fields: ["descriptionVector"],
        kNearestNeighborsCount: 3,
      },
    ],
  },
});

// ❌ Incorrect - old vector syntax
const results = await searchClient.search("*", {
  vectors: [{ value: queryVector, fields: ["embedding"], k: 3 }],
});
```

### Hybrid Search (Text + Vector)

```typescript
// ✅ Correct - combine text and vector
const results = await searchClient.search("luxury hotel", {
  vectorSearchOptions: {
    queries: [
      {
        kind: "vector",
        vector: queryVector,
        fields: ["descriptionVector"],
        kNearestNeighborsCount: 50,
      },
    ],
  },
  select: ["hotelId", "hotelName", "description"],
  top: 10,
});
```

### Semantic Search

```typescript
// ✅ Correct
const results = await searchClient.search("best hotel for families", {
  queryType: "semantic",
  semanticSearchOptions: {
    configurationName: "semantic-config",
    captions: { captionType: "extractive" },
    answers: { answerType: "extractive", count: 3 },
  },
});

// Access semantic results
for await (const result of results.results) {
  console.log(result.rerankerScore);
  console.log(result.captions);
}
```

---

## 4. Index Operations

### Create Index

```typescript
// ✅ Correct - with typed fields
const index: SearchIndex = {
  name: "hotels",
  fields: [
    { name: "id", type: "Edm.String", key: true },
    { name: "name", type: "Edm.String", searchable: true },
    { name: "rating", type: "Edm.Double", filterable: true, sortable: true },
    {
      name: "embedding",
      type: "Collection(Edm.Single)",
      searchable: true,
      vectorSearchDimensions: 1536,
      vectorSearchProfileName: "vector-profile",
    },
  ],
  vectorSearch: {
    algorithms: [{ name: "hnsw-algorithm", kind: "hnsw" }],
    profiles: [
      { name: "vector-profile", algorithmConfigurationName: "hnsw-algorithm" },
    ],
  },
};

await indexClient.createIndex(index);

// ✅ Correct - create or update (idempotent)
await indexClient.createOrUpdateIndex(index);
```

### Semantic Configuration

```typescript
// ✅ Correct
const index: SearchIndex = {
  name: "hotels",
  fields: [...],
  semanticSearch: {
    configurations: [
      {
        name: "semantic-config",
        prioritizedFields: {
          titleField: { name: "name" },
          contentFields: [{ name: "description" }],
          keywordsFields: [{ name: "tags" }],
        },
      },
    ],
  },
};
```

---

## 5. Document Operations

### Upload Documents

```typescript
// ✅ Correct - batch upload
const result = await searchClient.uploadDocuments([
  { id: "1", name: "Hotel A", rating: 4.5 },
  { id: "2", name: "Hotel B", rating: 4.0 },
]);

for (const r of result.results) {
  console.log(`${r.key}: ${r.succeeded}`);
}
```

### Merge or Upload (Upsert)

```typescript
// ✅ Correct - idempotent upsert
const result = await searchClient.mergeOrUploadDocuments([
  { id: "1", name: "Updated Hotel A" },
]);
```

### Delete Documents

```typescript
// ✅ Correct
const result = await searchClient.deleteDocuments([
  { id: "1" },
  { id: "2" },
]);
```

### Get Document

```typescript
// ✅ Correct - retrieve by key
const document = await searchClient.getDocument("1");
```

---

## 6. Filtering and Facets

### Filter Syntax

```typescript
// ✅ Correct - OData filter
const results = await searchClient.search("*", {
  filter: "rating ge 4 and category eq 'luxury'",
});

// ✅ Correct - using odata helper
import { odata } from "@azure/search-documents";

const minRating = 4;
const results = await searchClient.search("*", {
  filter: odata`rating ge ${minRating}`,
});
```

### Facets

```typescript
// ✅ Correct
const results = await searchClient.search("*", {
  facets: ["category,count:10", "rating,interval:1"],
});

// Access facets
for (const [facetName, facetResults] of Object.entries(results.facets || {})) {
  for (const facet of facetResults) {
    console.log(`${facet.value}: ${facet.count}`);
  }
}
```

---

## 7. Autocomplete and Suggestions

### Suggester Definition

```typescript
// ✅ Correct - in index definition
const index: SearchIndex = {
  name: "hotels",
  fields: [...],
  suggesters: [
    { name: "sg", sourceFields: ["name", "description"] },
  ],
};
```

### Autocomplete

```typescript
// ✅ Correct
const autocomplete = await searchClient.autocomplete("lux", "sg", {
  mode: "twoTerms",
  top: 5,
});

for (const result of autocomplete.results) {
  console.log(result.text);
}
```

### Suggestions

```typescript
// ✅ Correct
const suggestions = await searchClient.suggest("lux", "sg", {
  select: ["name"],
  top: 5,
});

for (const result of suggestions.results) {
  console.log(result.document.name);
}
```

---

## 8. TypeScript Typing

### Typed Documents

```typescript
// ✅ Correct - generic type parameter
interface Hotel {
  id: string;
  name: string;
  rating: number;
  description?: string;
}

const searchClient = new SearchClient<Hotel>(endpoint, indexName, credential);

const results = await searchClient.search("luxury", {
  select: ["id", "name", "rating"], // Type-checked
});

for await (const result of results.results) {
  // result.document is typed as Hotel
  console.log(result.document.name);
}
```

### Select Fields Type Helper

```typescript
import { SelectFields } from "@azure/search-documents";

const select: SelectFields<Hotel>[] = ["id", "name"];
```

---

## 9. Error Handling

### ✅ MUST

```typescript
import { RestError } from "@azure/core-rest-pipeline";

try {
  const results = await searchClient.search("query");
} catch (error) {
  if (error instanceof RestError) {
    console.log(`Search error: ${error.statusCode} - ${error.message}`);
  } else {
    throw error;
  }
}
```

---

## 10. Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| `require("@azure/search-documents")` | `import { SearchClient } from "@azure/search-documents"` |
| Hardcoded credentials | Use `DefaultAzureCredential` or `AzureKeyCredential` |
| `vectors: [...]` (old syntax) | `vectorSearchOptions: { queries: [...] }` |
| Missing `for await` | Always use `for await` with search results |
| Sync iteration | All search operations are async |

---

## 11. Type Imports

```typescript
import {
  SearchClient,
  SearchIndexClient,
  SearchIndexerClient,
  SearchIndex,
  SearchField,
  SearchOptions,
  VectorSearch,
  SemanticSearch,
  AzureKeyCredential,
  odata,
  SelectFields,
} from "@azure/search-documents";
```

---

## References

- [Official SDK README](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/search/search-documents)
- [API Reference](https://learn.microsoft.com/javascript/api/@azure/search-documents)
- [Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/search/search-documents/samples)
