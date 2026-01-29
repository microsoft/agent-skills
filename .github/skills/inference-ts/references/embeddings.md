# Embeddings Reference

Text and image embeddings using @azure-rest/ai-inference SDK.

## Overview

The Azure AI Inference REST client provides embedding generation for:
- **Text embeddings** - Semantic representations of text for search, similarity, clustering
- **Image embeddings** - Visual representations for image search and similarity

## Core Types

```typescript
import ModelClient, {
  isUnexpected,
  EmbeddingsResultOutput,
  EmbeddingItem
} from "@azure-rest/ai-inference";
```

## Client Initialization

```typescript
import ModelClient from "@azure-rest/ai-inference";
import { DefaultAzureCredential } from "@azure/identity";
import { AzureKeyCredential } from "@azure/core-auth";

// With DefaultAzureCredential (recommended)
const client = ModelClient(
  process.env.AZURE_INFERENCE_ENDPOINT!,
  new DefaultAzureCredential()
);

// With API key
const clientWithKey = ModelClient(
  process.env.AZURE_INFERENCE_ENDPOINT!,
  new AzureKeyCredential(process.env.AZURE_INFERENCE_CREDENTIAL!)
);
```

## Text Embeddings

### Basic Text Embedding

```typescript
import ModelClient, { isUnexpected } from "@azure-rest/ai-inference";

const response = await client.path("/embeddings").post({
  body: {
    input: ["Hello, world!"]
  }
});

if (isUnexpected(response)) {
  throw new Error(response.body.error.message);
}

const embedding = response.body.data[0].embedding;
console.log(`Embedding dimension: ${embedding.length}`);
console.log(`First 5 values: ${embedding.slice(0, 5)}`);
```

### Multiple Text Inputs (Batch)

```typescript
const response = await client.path("/embeddings").post({
  body: {
    input: [
      "First document about machine learning",
      "Second document about web development",
      "Third document about cloud computing",
      "Fourth document about TypeScript"
    ]
  }
});

if (isUnexpected(response)) {
  throw response.body.error;
}

// Each input gets its own embedding at corresponding index
for (const item of response.body.data) {
  console.log(`Index ${item.index}: ${item.embedding.length} dimensions`);
}

// Access by index
const firstEmbedding = response.body.data[0].embedding;
const secondEmbedding = response.body.data[1].embedding;
```

### Request Parameters

```typescript
const response = await client.path("/embeddings").post({
  body: {
    input: ["Text to embed"],
    
    // Reduce dimensions (model-dependent)
    dimensions: 1024,
    
    // Output format
    encoding_format: "float",  // "float" | "base64"
    
    // Input type hint (model-dependent)
    input_type: "query",  // "query" | "document"
    
    // Model override (for multi-model endpoints)
    model: "text-embedding-3-small"
  }
});
```

### Input Types

| Type | Use Case |
|------|----------|
| `query` | Search queries (shorter, question-like text) |
| `document` | Documents to be indexed/searched |

```typescript
// For search: embed query with input_type "query"
const queryEmbedding = await client.path("/embeddings").post({
  body: {
    input: ["What is machine learning?"],
    input_type: "query"
  }
});

// For indexing: embed documents with input_type "document"
const docEmbeddings = await client.path("/embeddings").post({
  body: {
    input: [
      "Machine learning is a subset of artificial intelligence...",
      "Deep learning uses neural networks..."
    ],
    input_type: "document"
  }
});
```

### Encoding Formats

```typescript
// Float format (default) - array of numbers
const floatResponse = await client.path("/embeddings").post({
  body: {
    input: ["Hello"],
    encoding_format: "float"
  }
});
// embedding: [0.123, -0.456, 0.789, ...]

// Base64 format - compact binary representation
const base64Response = await client.path("/embeddings").post({
  body: {
    input: ["Hello"],
    encoding_format: "base64"
  }
});
// embedding: "SGVsbG8gV29ybGQ..." (base64 string of float32 array)

// Decode base64 to float array
function decodeBase64Embedding(base64: string): number[] {
  const buffer = Buffer.from(base64, "base64");
  const floats: number[] = [];
  for (let i = 0; i < buffer.length; i += 4) {
    floats.push(buffer.readFloatLE(i));
  }
  return floats;
}
```

## Image Embeddings

### Basic Image Embedding (URL)

```typescript
const response = await client.path("/images/embeddings").post({
  body: {
    input: [
      { image: "https://example.com/image.jpg" }
    ]
  }
});

if (isUnexpected(response)) {
  throw response.body.error;
}

const imageEmbedding = response.body.data[0].embedding;
console.log(`Image embedding: ${imageEmbedding.length} dimensions`);
```

### Image Embedding (Base64 Data URL)

```typescript
import { readFileSync } from "node:fs";
import { extname } from "node:path";

function imageToDataUrl(filePath: string): string {
  const buffer = readFileSync(filePath);
  const ext = extname(filePath).slice(1).toLowerCase();
  const mimeType = ext === "jpg" ? "jpeg" : ext;
  return `data:image/${mimeType};base64,${buffer.toString("base64")}`;
}

const response = await client.path("/images/embeddings").post({
  body: {
    input: [
      { image: imageToDataUrl("./photo.png") }
    ]
  }
});
```

### Multiple Image Embeddings

```typescript
const response = await client.path("/images/embeddings").post({
  body: {
    input: [
      { image: "https://example.com/cat.jpg" },
      { image: "https://example.com/dog.jpg" },
      { image: imageToDataUrl("./bird.png") }
    ]
  }
});

if (isUnexpected(response)) {
  throw response.body.error;
}

// Process each image embedding
for (const item of response.body.data) {
  console.log(`Image ${item.index}: ${item.embedding.length} dimensions`);
}
```

## Response Structure

```typescript
interface EmbeddingsResultOutput {
  data: Array<{
    index: number;           // Position in input array
    embedding: number[];     // Vector representation
    object: "embedding";
  }>;
  model: string;             // Model used
  object: "list";
  usage: {
    prompt_tokens: number;   // Input tokens consumed
    total_tokens: number;    // Total tokens used
  };
}
```

## Batch Processing

### Chunked Batch Processing

```typescript
async function embedInBatches(
  client: ReturnType<typeof ModelClient>,
  texts: string[],
  batchSize: number = 100
): Promise<number[][]> {
  const allEmbeddings: number[][] = [];
  
  for (let i = 0; i < texts.length; i += batchSize) {
    const batch = texts.slice(i, i + batchSize);
    
    const response = await client.path("/embeddings").post({
      body: { input: batch }
    });
    
    if (isUnexpected(response)) {
      throw new Error(`Batch ${i / batchSize} failed: ${response.body.error.message}`);
    }
    
    // Ensure correct order
    const sortedData = response.body.data.sort((a, b) => a.index - b.index);
    allEmbeddings.push(...sortedData.map(d => d.embedding));
    
    console.log(`Processed batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(texts.length / batchSize)}`);
  }
  
  return allEmbeddings;
}

// Usage
const documents = ["doc1", "doc2", ..., "doc1000"];
const embeddings = await embedInBatches(client, documents, 100);
```

### Parallel Batch Processing

```typescript
async function embedInParallel(
  client: ReturnType<typeof ModelClient>,
  texts: string[],
  batchSize: number = 100,
  concurrency: number = 3
): Promise<number[][]> {
  const batches: string[][] = [];
  for (let i = 0; i < texts.length; i += batchSize) {
    batches.push(texts.slice(i, i + batchSize));
  }
  
  const results: Map<number, number[][]> = new Map();
  
  // Process in parallel with concurrency limit
  for (let i = 0; i < batches.length; i += concurrency) {
    const batchPromises = batches
      .slice(i, i + concurrency)
      .map(async (batch, offset) => {
        const batchIndex = i + offset;
        const response = await client.path("/embeddings").post({
          body: { input: batch }
        });
        
        if (isUnexpected(response)) {
          throw new Error(`Batch ${batchIndex} failed`);
        }
        
        const sorted = response.body.data.sort((a, b) => a.index - b.index);
        results.set(batchIndex, sorted.map(d => d.embedding));
      });
    
    await Promise.all(batchPromises);
  }
  
  // Reassemble in order
  const allEmbeddings: number[][] = [];
  for (let i = 0; i < batches.length; i++) {
    allEmbeddings.push(...results.get(i)!);
  }
  
  return allEmbeddings;
}
```

## Vector Similarity

### Cosine Similarity

```typescript
function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) {
    throw new Error("Vectors must have same length");
  }
  
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// Usage
const similarity = cosineSimilarity(embedding1, embedding2);
console.log(`Similarity: ${similarity.toFixed(4)}`);  // 0-1, higher = more similar
```

### Dot Product (for Normalized Vectors)

```typescript
function dotProduct(a: number[], b: number[]): number {
  let sum = 0;
  for (let i = 0; i < a.length; i++) {
    sum += a[i] * b[i];
  }
  return sum;
}

// Normalize vector
function normalize(v: number[]): number[] {
  const magnitude = Math.sqrt(v.reduce((sum, x) => sum + x * x, 0));
  return v.map(x => x / magnitude);
}
```

### Euclidean Distance

```typescript
function euclideanDistance(a: number[], b: number[]): number {
  let sum = 0;
  for (let i = 0; i < a.length; i++) {
    sum += (a[i] - b[i]) ** 2;
  }
  return Math.sqrt(sum);
}
// Lower = more similar
```

## Semantic Search Pattern

```typescript
interface Document {
  id: string;
  text: string;
  embedding?: number[];
}

class SimpleVectorStore {
  private documents: Document[] = [];
  private client: ReturnType<typeof ModelClient>;
  
  constructor(client: ReturnType<typeof ModelClient>) {
    this.client = client;
  }
  
  async addDocuments(docs: Document[]): Promise<void> {
    const texts = docs.map(d => d.text);
    
    const response = await this.client.path("/embeddings").post({
      body: { input: texts, input_type: "document" }
    });
    
    if (isUnexpected(response)) {
      throw response.body.error;
    }
    
    for (const item of response.body.data) {
      docs[item.index].embedding = item.embedding;
    }
    
    this.documents.push(...docs);
  }
  
  async search(query: string, topK: number = 5): Promise<Array<Document & { score: number }>> {
    // Embed query
    const response = await this.client.path("/embeddings").post({
      body: { input: [query], input_type: "query" }
    });
    
    if (isUnexpected(response)) {
      throw response.body.error;
    }
    
    const queryEmbedding = response.body.data[0].embedding;
    
    // Calculate similarity scores
    const scored = this.documents.map(doc => ({
      ...doc,
      score: cosineSimilarity(queryEmbedding, doc.embedding!)
    }));
    
    // Return top K
    return scored
      .sort((a, b) => b.score - a.score)
      .slice(0, topK);
  }
}

// Usage
const store = new SimpleVectorStore(client);

await store.addDocuments([
  { id: "1", text: "TypeScript is a typed superset of JavaScript" },
  { id: "2", text: "Python is great for machine learning" },
  { id: "3", text: "JavaScript runs in web browsers" }
]);

const results = await store.search("What language is good for ML?");
// Returns doc 2 with highest score
```

## Error Handling

```typescript
import ModelClient, { isUnexpected } from "@azure-rest/ai-inference";

async function getEmbeddingSafe(text: string): Promise<number[] | null> {
  try {
    const response = await client.path("/embeddings").post({
      body: { input: [text] }
    });
    
    if (isUnexpected(response)) {
      console.error(`API Error: ${response.body.error.message}`);
      return null;
    }
    
    return response.body.data[0].embedding;
  } catch (error) {
    if (error instanceof Error) {
      console.error(`Network error: ${error.message}`);
    }
    return null;
  }
}
```

### Common Error Codes

| Status | Meaning |
|--------|---------|
| 400 | Invalid input (empty text, too long, invalid format) |
| 401 | Authentication failed |
| 403 | Access denied |
| 404 | Model/endpoint not found |
| 429 | Rate limited |
| 500 | Server error |

### Rate Limit Handling

```typescript
async function embedWithRetry(
  client: ReturnType<typeof ModelClient>,
  input: string[],
  maxRetries: number = 3
): Promise<number[][]> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await client.path("/embeddings").post({
      body: { input }
    });
    
    if (response.status === "429") {
      const retryAfter = parseInt(response.headers["retry-after"] || "5");
      console.log(`Rate limited, waiting ${retryAfter}s...`);
      await new Promise(r => setTimeout(r, retryAfter * 1000));
      continue;
    }
    
    if (isUnexpected(response)) {
      throw response.body.error;
    }
    
    return response.body.data
      .sort((a, b) => a.index - b.index)
      .map(d => d.embedding);
  }
  
  throw new Error("Max retries exceeded");
}
```

## Token Counting

```typescript
// Approximate token count (rough estimate)
function estimateTokens(text: string): number {
  // ~4 characters per token for English text
  return Math.ceil(text.length / 4);
}

// Check token usage from response
const response = await client.path("/embeddings").post({
  body: { input: texts }
});

if (!isUnexpected(response)) {
  console.log(`Tokens used: ${response.body.usage.total_tokens}`);
}
```

## Best Practices

1. **Batch inputs** - Send multiple texts per request (up to model limit, typically 100-2048)
2. **Use input_type** - "query" for searches, "document" for indexing (improves retrieval)
3. **Reduce dimensions** - Use `dimensions` parameter if model supports it for storage savings
4. **Handle rate limits** - Implement exponential backoff for 429 responses
5. **Normalize vectors** - Pre-normalize if using dot product similarity
6. **Cache embeddings** - Store embeddings to avoid recomputing for unchanged content
7. **Monitor usage** - Track token consumption via `usage` in responses
8. **Choose right model** - Smaller models (text-embedding-3-small) for cost, larger for quality

## Supported Models

| Model | Dimensions | Max Input | Best For |
|-------|------------|-----------|----------|
| text-embedding-3-small | 1536 | 8191 tokens | Cost-effective general use |
| text-embedding-3-large | 3072 | 8191 tokens | High-quality retrieval |
| text-embedding-ada-002 | 1536 | 8191 tokens | Legacy compatibility |

## See Also

- [chat-completions.md](./chat-completions.md) - Chat completions and streaming
