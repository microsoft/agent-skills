# @azure/search-documents - Semantic Ranking Patterns

Reference documentation for semantic search and ranking in the Azure AI Search TypeScript SDK.

**Source**: [Azure SDK for JS - search-documents](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/search/search-documents)

---

## Installation

```bash
npm install @azure/search-documents @azure/identity
```

---

## SemanticSearchOptions Interface

```typescript
interface SemanticSearchOptions {
  /** Name of the semantic configuration to use */
  configurationName?: string;
  
  /** Error handling mode: "partial" or "fail" */
  errorMode?: SemanticErrorMode;
  
  /** Max wait time for semantic processing (ms) */
  maxWaitInMilliseconds?: number;
  
  /** Extract answers from documents */
  answers?: QueryAnswer;
  
  /** Extract captions with highlighting */
  captions?: QueryCaption;
  
  /** AI-generated query rewrites */
  queryRewrites?: QueryRewrites;
  
  /** Separate query for semantic reranking */
  semanticQuery?: string;
  
  /** Fields for semantic search */
  semanticFields?: string[];
  
  /** Enable debug info */
  debugMode?: QueryDebugMode;
}
```

---

## Basic Semantic Search

Enable semantic ranking with `queryType: "semantic"`:

```typescript
import { SearchClient } from "@azure/search-documents";
import { DefaultAzureCredential } from "@azure/identity";

interface Article {
  id: string;
  title: string;
  content: string;
  category: string;
}

const client = new SearchClient<Article>(
  process.env["AZURE_SEARCH_ENDPOINT"]!,
  "articles",
  new DefaultAzureCredential()
);

const results = await client.search("what causes climate change", {
  queryType: "semantic",
  semanticSearchOptions: {
    configurationName: "my-semantic-config",
  },
  select: ["id", "title", "content"],
  top: 10,
});

for await (const result of results.results) {
  console.log(`${result.document.title}`);
  console.log(`Reranker Score: ${result.rerankerScore}`);
}
```

---

## Extractive Captions

Extract representative passages with keyword highlighting:

```typescript
const results = await client.search("renewable energy benefits", {
  queryType: "semantic",
  semanticSearchOptions: {
    configurationName: "my-semantic-config",
    captions: {
      captionType: "extractive",
      highlight: true,
    },
  },
});

for await (const result of results.results) {
  console.log(`Title: ${result.document.title}`);
  
  // Access captions
  result.captions?.forEach((caption) => {
    console.log(`Caption: ${caption.text}`);
    console.log(`Highlighted: ${caption.highlights}`); // With <em> tags
  });
}
```

### Caption Options

```typescript
interface QueryCaption {
  /** Caption type: "extractive" | "none" */
  captionType: QueryCaptionType;
  
  /** Include highlighting with <em> tags */
  highlight?: boolean;
}
```

---

## Extractive Answers

Extract direct answers for Q&A-style queries:

```typescript
const results = await client.search("what is the speed of light", {
  queryType: "semantic",
  semanticSearchOptions: {
    configurationName: "science-config",
    answers: {
      answerType: "extractive",
      count: 3,           // Number of answers to extract
      threshold: 0.7,     // Minimum confidence threshold
    },
  },
});

// Access answers at the result set level
if (results.answers && results.answers.length > 0) {
  console.log("Top Answers:");
  results.answers.forEach((answer, i) => {
    console.log(`${i + 1}. ${answer.text}`);
    console.log(`   Highlights: ${answer.highlights}`);
    console.log(`   Score: ${answer.score}`);
    console.log(`   Document: ${answer.key}`);
  });
}
```

### Answer Options

```typescript
interface QueryAnswer {
  /** Answer type: "extractive" | "none" */
  answerType: QueryAnswerType;
  
  /** Number of answers to return (1-10) */
  count?: number;
  
  /** Minimum confidence threshold (0-1) */
  threshold?: number;
}
```

---

## Query Rewrites

Enable AI-generated query rewrites for better recall:

```typescript
const results = await client.search("ML algorithms", {
  queryType: "semantic",
  semanticSearchOptions: {
    configurationName: "tech-config",
    queryRewrites: {
      rewritesType: "generative",
      count: 3, // Number of rewrites to generate
    },
  },
});

// Access generated rewrites
if (results.queryRewrites && results.queryRewrites.length > 0) {
  console.log("Query Rewrites:");
  results.queryRewrites.forEach((rewrite) => {
    console.log(`- ${rewrite}`);
  });
}
```

---

## Semantic + Hybrid Search

Combine semantic ranking with vector search for best results:

```typescript
const results = await client.search("climate change solutions", {
  // Enable semantic reranking
  queryType: "semantic",
  semanticSearchOptions: {
    configurationName: "articles-semantic",
    captions: { captionType: "extractive", highlight: true },
    answers: { answerType: "extractive", count: 3 },
  },
  
  // Add vector search
  vectorSearchOptions: {
    queries: [
      {
        kind: "text",
        text: "climate change solutions",
        kNearestNeighborsCount: 50,
        fields: ["contentVector"],
      },
    ],
  },
  
  // Keyword search fields
  searchFields: ["title", "content"],
  
  top: 10,
  select: ["id", "title", "content", "category"],
});

// Results are:
// 1. Retrieved via hybrid (keyword + vector)
// 2. Reranked by semantic model
// 3. Enriched with captions and answers
```

---

## Semantic Query Override

Use different queries for retrieval vs. semantic reranking:

```typescript
const results = await client.search("ML", {
  // "ML" used for keyword matching
  queryType: "semantic",
  semanticSearchOptions: {
    configurationName: "tech-config",
    // Full question used for semantic reranking
    semanticQuery: "What are the best machine learning algorithms for classification?",
    captions: { captionType: "extractive" },
  },
});
```

---

## Debug Mode

Get detailed information about semantic processing:

```typescript
const results = await client.search("quantum computing applications", {
  queryType: "semantic",
  semanticSearchOptions: {
    configurationName: "science-config",
    debugMode: "semantic", // "disabled" | "speller" | "semantic" | "all"
  },
});

for await (const result of results.results) {
  // Access debug info per document
  console.log(`Document: ${result.document.title}`);
  console.log(`Debug Info:`, result.documentDebugInfo);
}
```

---

## Error Handling

Control behavior when semantic processing fails:

```typescript
const results = await client.search("complex query here", {
  queryType: "semantic",
  semanticSearchOptions: {
    configurationName: "my-config",
    
    // "partial" - Return results without semantic enrichment on failure
    // "fail" - Return error if semantic processing fails
    errorMode: "partial",
    
    // Timeout for semantic processing
    maxWaitInMilliseconds: 5000,
  },
});
```

---

## Index Semantic Configuration

Define semantic configuration in your index:

```typescript
import { SearchIndexClient, SearchIndex } from "@azure/search-documents";

const indexClient = new SearchIndexClient(endpoint, credential);

const index: SearchIndex = {
  name: "articles",
  fields: [
    { name: "id", type: "Edm.String", key: true },
    { name: "title", type: "Edm.String", searchable: true },
    { name: "content", type: "Edm.String", searchable: true },
    { name: "summary", type: "Edm.String", searchable: true },
    { name: "category", type: "Edm.String", filterable: true },
  ],
  semanticSearch: {
    configurations: [
      {
        name: "articles-semantic",
        prioritizedFields: {
          // Title field (highest priority for reranking)
          titleField: {
            fieldName: "title",
          },
          // Content fields (used for caption/answer extraction)
          contentFields: [
            { fieldName: "content" },
            { fieldName: "summary" },
          ],
          // Keyword fields (boost exact matches)
          keywordsFields: [
            { fieldName: "category" },
          ],
        },
      },
    ],
    defaultConfiguration: "articles-semantic",
  },
};

await indexClient.createOrUpdateIndex(index);
```

---

## Complete Example

```typescript
import { SearchClient } from "@azure/search-documents";
import { DefaultAzureCredential } from "@azure/identity";

interface Document {
  id: string;
  title: string;
  content: string;
  contentVector: number[];
  category: string;
}

async function semanticHybridSearch(query: string) {
  const client = new SearchClient<Document>(
    process.env["AZURE_SEARCH_ENDPOINT"]!,
    "knowledge-base",
    new DefaultAzureCredential()
  );

  const results = await client.search(query, {
    queryType: "semantic",
    semanticSearchOptions: {
      configurationName: "default-semantic",
      captions: { captionType: "extractive", highlight: true },
      answers: { answerType: "extractive", count: 3, threshold: 0.7 },
    },
    vectorSearchOptions: {
      queries: [
        {
          kind: "text",
          text: query,
          kNearestNeighborsCount: 50,
          fields: ["contentVector"],
        },
      ],
    },
    searchFields: ["title", "content"],
    top: 10,
    select: ["id", "title", "content", "category"],
  });

  // Process answers first (highest quality extracts)
  const response: {
    answers: Array<{ text: string; score: number; documentId: string }>;
    results: Array<{
      document: Document;
      score: number;
      rerankerScore: number;
      captions: string[];
    }>;
  } = {
    answers: [],
    results: [],
  };

  // Extract answers
  if (results.answers) {
    response.answers = results.answers.map((a) => ({
      text: a.highlights || a.text || "",
      score: a.score ?? 0,
      documentId: a.key || "",
    }));
  }

  // Extract results with captions
  for await (const result of results.results) {
    response.results.push({
      document: result.document,
      score: result.score ?? 0,
      rerankerScore: result.rerankerScore ?? 0,
      captions: result.captions?.map((c) => c.highlights || c.text || "") ?? [],
    });
  }

  return response;
}

// Usage
const response = await semanticHybridSearch("how does photosynthesis work");

console.log("=== Direct Answers ===");
response.answers.forEach((a, i) => {
  console.log(`${i + 1}. ${a.text} (score: ${a.score})`);
});

console.log("\n=== Search Results ===");
response.results.forEach((r, i) => {
  console.log(`${i + 1}. ${r.document.title}`);
  console.log(`   Reranker Score: ${r.rerankerScore}`);
  console.log(`   Caption: ${r.captions[0] || "N/A"}`);
});
```

---

## Best Practices

1. **Use extractive answers** - For Q&A scenarios, answers provide direct responses
2. **Enable captions** - They provide relevant snippets without returning full content
3. **Combine with hybrid search** - Semantic + vector + keyword yields best results
4. **Set appropriate thresholds** - Filter low-confidence answers
5. **Configure semantic fields** - Prioritize title > content > keywords
6. **Use partial error mode** - Gracefully degrade when semantic processing fails
7. **Monitor latency** - Semantic processing adds ~100-300ms latency

---

## See Also

- [Vector Search Patterns](./vector-search.md) - Combine with vector search
- [Official Documentation](https://learn.microsoft.com/azure/search/semantic-search-overview)
