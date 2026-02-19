# @azure/search-documents - Vector Search Patterns

Reference documentation for vector search in the Azure AI Search TypeScript SDK.

**Source**: [Azure SDK for JS - search-documents](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/search/search-documents)

---

## Installation

```bash
npm install @azure/search-documents @azure/identity
```

---

## Client Setup

```typescript
import { SearchClient, SearchIndexClient } from "@azure/search-documents";
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();
const endpoint = process.env["AZURE_SEARCH_ENDPOINT"]!;

// For searching
const searchClient = new SearchClient<MyDocument>(
  endpoint,
  "my-index",
  credential
);

// For index management
const indexClient = new SearchIndexClient(endpoint, credential);
```

---

## VectorSearchOptions Interface

```typescript
interface VectorSearchOptions {
  /** Vector queries to execute */
  queries?: VectorQuery[];
  
  /** Filter mode for vector queries */
  filterMode?: VectorFilterMode; // "preFilter" | "postFilter"
}

type VectorQuery = 
  | VectorizedQuery      // Pre-computed vector
  | VectorizableTextQuery // Text to be vectorized
  | VectorizableImageUrlQuery
  | VectorizableImageBinaryQuery;
```

---

## Basic Vector Search

Search using a pre-computed embedding vector:

```typescript
import { SearchClient } from "@azure/search-documents";

interface Product {
  id: string;
  name: string;
  description: string;
  descriptionVector: number[];
}

const searchClient = new SearchClient<Product>(endpoint, "products", credential);

// Your embedding (e.g., from OpenAI, Azure OpenAI, etc.)
const queryVector = await getEmbedding("comfortable running shoes");

const results = await searchClient.search("*", {
  vectorSearchOptions: {
    queries: [
      {
        kind: "vector",
        vector: queryVector,
        kNearestNeighborsCount: 10,
        fields: ["descriptionVector"],
      },
    ],
  },
  select: ["id", "name", "description"],
});

for await (const result of results.results) {
  console.log(`${result.document.name} (score: ${result.score})`);
}
```

---

## Integrated Vectorization (Text)

Let Azure AI Search vectorize the query text automatically:

```typescript
const results = await searchClient.search("*", {
  vectorSearchOptions: {
    queries: [
      {
        kind: "text",
        text: "comfortable running shoes",
        kNearestNeighborsCount: 10,
        fields: ["descriptionVector"],
      },
    ],
  },
});
```

> **Note**: Requires a vectorizer configured on the index.

---

## Hybrid Search (Text + Vector)

Combine keyword search with vector search for better results:

```typescript
const results = await searchClient.search("running shoes", {
  // Keyword search component
  searchFields: ["name", "description"],
  
  // Vector search component
  vectorSearchOptions: {
    queries: [
      {
        kind: "text",
        text: "comfortable running shoes",
        kNearestNeighborsCount: 50,
        fields: ["descriptionVector"],
      },
    ],
  },
  
  // Return top 10 after RRF fusion
  top: 10,
  select: ["id", "name", "description"],
});
```

---

## Multi-Vector Search

Search across multiple vector fields simultaneously:

```typescript
const results = await searchClient.search("*", {
  vectorSearchOptions: {
    queries: [
      // Search title embeddings
      {
        kind: "text",
        text: "machine learning",
        kNearestNeighborsCount: 50,
        fields: ["titleVector"],
        weight: 2.0, // Boost title matches
      },
      // Search content embeddings
      {
        kind: "text",
        text: "machine learning",
        kNearestNeighborsCount: 50,
        fields: ["contentVector"],
        weight: 1.0,
      },
    ],
  },
  top: 10,
});
```

---

## Vector Filtering

### Pre-Filter (Default)

Apply filters before vector search - smaller search space, faster:

```typescript
const results = await searchClient.search("*", {
  filter: "category eq 'Electronics' and price lt 500",
  vectorSearchOptions: {
    filterMode: "preFilter", // Default
    queries: [
      {
        kind: "text",
        text: "wireless headphones",
        kNearestNeighborsCount: 10,
        fields: ["descriptionVector"],
      },
    ],
  },
});
```

### Post-Filter

Apply filters after vector search - ensures k results are found first:

```typescript
const results = await searchClient.search("*", {
  filter: "category eq 'Electronics'",
  vectorSearchOptions: {
    filterMode: "postFilter",
    queries: [
      {
        kind: "text",
        text: "wireless headphones",
        kNearestNeighborsCount: 50, // Get more, then filter
        fields: ["descriptionVector"],
      },
    ],
  },
  top: 10,
});
```

### Per-Query Filter Override

Apply different filters to different vector queries:

```typescript
const results = await searchClient.search("*", {
  filter: "inStock eq true", // Global filter
  vectorSearchOptions: {
    queries: [
      {
        kind: "text",
        text: "premium headphones",
        kNearestNeighborsCount: 20,
        fields: ["descriptionVector"],
        filterOverride: "category eq 'Audio' and price gt 200", // Override for this query
      },
    ],
  },
});
```

---

## Vector Thresholds

Set minimum similarity thresholds:

```typescript
const results = await searchClient.search("*", {
  vectorSearchOptions: {
    queries: [
      {
        kind: "text",
        text: "wireless headphones",
        kNearestNeighborsCount: 50,
        fields: ["descriptionVector"],
        threshold: {
          kind: "vectorSimilarity",
          value: 0.8, // Only results with similarity >= 0.8
        },
      },
    ],
  },
});
```

---

## Exhaustive Search

Force brute-force search instead of approximate (HNSW):

```typescript
const results = await searchClient.search("*", {
  vectorSearchOptions: {
    queries: [
      {
        kind: "text",
        text: "specific product query",
        kNearestNeighborsCount: 10,
        fields: ["descriptionVector"],
        exhaustive: true, // Slower but more accurate
      },
    ],
  },
});
```

---

## Index Configuration for Vector Search

Create an index with vector search capabilities:

```typescript
import { SearchIndexClient, SearchIndex } from "@azure/search-documents";

const indexClient = new SearchIndexClient(endpoint, credential);

const index: SearchIndex = {
  name: "products",
  fields: [
    { name: "id", type: "Edm.String", key: true },
    { name: "name", type: "Edm.String", searchable: true },
    { name: "description", type: "Edm.String", searchable: true },
    { name: "category", type: "Edm.String", filterable: true, facetable: true },
    { name: "price", type: "Edm.Double", filterable: true, sortable: true },
    {
      name: "descriptionVector",
      type: "Collection(Edm.Single)",
      searchable: true,
      vectorSearchDimensions: 1536,
      vectorSearchProfileName: "vector-profile",
    },
  ],
  vectorSearch: {
    algorithms: [
      {
        name: "hnsw-algorithm",
        kind: "hnsw",
        parameters: {
          m: 4,
          efConstruction: 400,
          efSearch: 500,
          metric: "cosine",
        },
      },
    ],
    profiles: [
      {
        name: "vector-profile",
        algorithmConfigurationName: "hnsw-algorithm",
        vectorizerName: "openai-vectorizer", // Optional: for integrated vectorization
      },
    ],
    vectorizers: [
      {
        name: "openai-vectorizer",
        kind: "azureOpenAI",
        azureOpenAIParameters: {
          resourceUri: process.env["AZURE_OPENAI_ENDPOINT"]!,
          deploymentId: "text-embedding-ada-002",
          modelName: "text-embedding-ada-002",
        },
      },
    ],
  },
};

await indexClient.createOrUpdateIndex(index);
```

---

## Complete Hybrid Search Example

```typescript
import { SearchClient } from "@azure/search-documents";
import { DefaultAzureCredential } from "@azure/identity";

interface Product {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number;
}

async function hybridSearch(query: string, category?: string) {
  const client = new SearchClient<Product>(
    process.env["AZURE_SEARCH_ENDPOINT"]!,
    "products",
    new DefaultAzureCredential()
  );

  const filter = category ? `category eq '${category}'` : undefined;

  const results = await client.search(query, {
    filter,
    searchFields: ["name", "description"],
    vectorSearchOptions: {
      queries: [
        {
          kind: "text",
          text: query,
          kNearestNeighborsCount: 50,
          fields: ["descriptionVector"],
        },
      ],
    },
    top: 10,
    select: ["id", "name", "description", "category", "price"],
  });

  const items: Array<{ document: Product; score: number }> = [];
  
  for await (const result of results.results) {
    items.push({
      document: result.document,
      score: result.score ?? 0,
    });
  }

  return items;
}

// Usage
const results = await hybridSearch("wireless noise canceling", "Electronics");
results.forEach((r) => {
  console.log(`${r.document.name}: $${r.document.price} (score: ${r.score})`);
});
```

---

## Best Practices

1. **Use hybrid search** - Combining keyword + vector typically outperforms either alone
2. **Tune kNearestNeighborsCount** - Higher values increase recall but slow down search
3. **Use pre-filtering** - When filter selectivity is high (filters out most documents)
4. **Use post-filtering** - When you need exactly k vector matches, then filter
5. **Set appropriate thresholds** - Filter out low-quality matches
6. **Weight vector queries** - Boost more relevant vector fields
7. **Monitor index metrics** - Track search latency and recall

---

## See Also

- [Semantic Ranking](./semantic-ranking.md) - Combine with semantic reranking
- [Official Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/search/search-documents/samples)
