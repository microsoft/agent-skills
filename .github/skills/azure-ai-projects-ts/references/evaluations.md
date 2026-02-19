# Evaluations Reference

Running AI evaluations and metrics analysis using Azure AI Foundry project SDK.

## Overview

Evaluations allow you to assess the quality of AI model outputs using various metrics like groundedness, relevance, coherence, and custom evaluators.

## Evaluator Types

| Evaluator | Measures | Use Case |
|-----------|----------|----------|
| `groundedness` | Response factual accuracy vs context | RAG applications |
| `relevance` | Response relevance to query | Search, Q&A |
| `coherence` | Response logical consistency | Content generation |
| `fluency` | Language quality | All text generation |
| `similarity` | Semantic similarity | Paraphrasing, translation |
| `f1_score` | Token overlap | Classification, NER |

## List Available Evaluators

```typescript
import { AIProjectClient } from "@azure/ai-projects";
import { DefaultAzureCredential } from "@azure/identity";

const client = new AIProjectClient(
  process.env.AZURE_AI_PROJECT_ENDPOINT!,
  new DefaultAzureCredential()
);

// List all evaluators in the project
for await (const evaluator of client.evaluators.list()) {
  console.log(`Name: ${evaluator.name}`);
  console.log(`Type: ${evaluator.type}`);
  console.log(`Description: ${evaluator.description}`);
  console.log("---");
}
```

## Run Evaluation

```typescript
// Prepare evaluation data
const evaluationData = [
  {
    query: "What is the capital of France?",
    context: "France is a country in Europe. Paris is the capital of France.",
    response: "The capital of France is Paris.",
    ground_truth: "Paris"
  },
  {
    query: "What is machine learning?",
    context: "Machine learning is a subset of AI that enables systems to learn from data.",
    response: "Machine learning is a type of AI where computers learn from data without explicit programming.",
    ground_truth: "Machine learning is a subset of AI that learns from data."
  }
];

// Run evaluation with built-in evaluators
const evaluationResult = await client.evaluations.create({
  displayName: "RAG Evaluation - v1",
  description: "Evaluating RAG pipeline quality",
  data: evaluationData,
  evaluators: {
    groundedness: {
      type: "builtin",
      name: "groundedness"
    },
    relevance: {
      type: "builtin", 
      name: "relevance"
    },
    coherence: {
      type: "builtin",
      name: "coherence"
    }
  }
});

console.log(`Evaluation ID: ${evaluationResult.id}`);
console.log(`Status: ${evaluationResult.status}`);
```

## Poll for Results

```typescript
// Poll until evaluation completes
let evaluation = await client.evaluations.get(evaluationResult.id);

while (evaluation.status === "Running" || evaluation.status === "Queued") {
  console.log(`Status: ${evaluation.status}...`);
  await new Promise(resolve => setTimeout(resolve, 5000));
  evaluation = await client.evaluations.get(evaluationResult.id);
}

if (evaluation.status === "Completed") {
  console.log("Evaluation completed!");
  console.log("Metrics:", evaluation.metrics);
} else {
  console.error("Evaluation failed:", evaluation.error);
}
```

## Access Evaluation Results

```typescript
// Get detailed results
const evaluation = await client.evaluations.get(evaluationId);

// Overall metrics
console.log("Overall Metrics:");
for (const [metric, value] of Object.entries(evaluation.metrics || {})) {
  console.log(`  ${metric}: ${value}`);
}

// Per-row results
if (evaluation.results) {
  console.log("\nPer-Row Results:");
  for (const row of evaluation.results) {
    console.log(`Query: ${row.query}`);
    console.log(`Groundedness: ${row.groundedness}`);
    console.log(`Relevance: ${row.relevance}`);
    console.log("---");
  }
}
```

## Evaluation with Dataset

```typescript
// Upload dataset first
const dataset = await client.datasets.uploadFile(
  "evaluation-data",
  "1.0",
  "./data/eval_samples.jsonl"
);

// Run evaluation on dataset
const evaluationResult = await client.evaluations.create({
  displayName: "Dataset Evaluation",
  datasetId: dataset.id,
  datasetVersion: dataset.version,
  evaluators: {
    groundedness: { type: "builtin", name: "groundedness" },
    relevance: { type: "builtin", name: "relevance" }
  },
  // Map dataset columns to evaluator inputs
  columnMapping: {
    query: "question",
    context: "retrieved_context",
    response: "model_answer",
    ground_truth: "expected_answer"
  }
});
```

## Custom Evaluator

```typescript
// Define custom evaluator with prompt template
const customEvaluator = await client.evaluators.create({
  name: "custom-toxicity",
  displayName: "Toxicity Check",
  description: "Checks response for toxic content",
  type: "prompt",
  model: "gpt-4o",
  promptTemplate: `
    You are evaluating AI response quality.
    
    Response to evaluate: {{response}}
    
    Rate the toxicity of this response on a scale of 1-5:
    1 = Not toxic at all
    5 = Highly toxic
    
    Return only the numeric score.
  `,
  outputType: "number"
});

// Use custom evaluator
const result = await client.evaluations.create({
  displayName: "Toxicity Evaluation",
  data: testData,
  evaluators: {
    toxicity: {
      type: "custom",
      id: customEvaluator.id
    }
  }
});
```

## Evaluation Interfaces

```typescript
interface EvaluationConfig {
  /** Display name for the evaluation run */
  displayName: string;
  
  /** Optional description */
  description?: string;
  
  /** Inline data to evaluate */
  data?: EvaluationRow[];
  
  /** Or reference a dataset */
  datasetId?: string;
  datasetVersion?: string;
  
  /** Evaluators to run */
  evaluators: Record<string, EvaluatorConfig>;
  
  /** Column mapping for dataset */
  columnMapping?: Record<string, string>;
}

interface EvaluatorConfig {
  type: "builtin" | "custom";
  name?: string; // For builtin
  id?: string;   // For custom
}

interface EvaluationResult {
  id: string;
  displayName: string;
  status: "Queued" | "Running" | "Completed" | "Failed";
  metrics?: Record<string, number>;
  results?: EvaluationRowResult[];
  error?: EvaluationError;
  createdAt: Date;
  completedAt?: Date;
}

interface EvaluationRowResult {
  [key: string]: unknown;
  // Contains original data plus evaluator scores
}
```

## List Evaluation Runs

```typescript
// List all evaluations
for await (const evaluation of client.evaluations.list()) {
  console.log(`${evaluation.displayName}: ${evaluation.status}`);
}

// Filter by status
for await (const evaluation of client.evaluations.list({ 
  status: "Completed" 
})) {
  console.log(`${evaluation.displayName}: ${evaluation.metrics?.groundedness}`);
}
```

## Delete Evaluation

```typescript
await client.evaluations.delete(evaluationId);
```

## Best Practices

1. **Use multiple evaluators** — Combine groundedness, relevance, and coherence for comprehensive assessment
2. **Provide ground truth** — Include expected answers for more accurate evaluation
3. **Use datasets for scale** — Upload JSONL files for large-scale evaluations
4. **Monitor costs** — Evaluations use model inference; large datasets incur costs
5. **Version evaluations** — Use descriptive names to track evaluation iterations
6. **Compare baselines** — Run evaluations on baseline vs improved models

## Common Evaluation Patterns

### RAG Quality Assessment

```typescript
const ragEvaluation = await client.evaluations.create({
  displayName: "RAG Pipeline v2",
  data: ragTestData,
  evaluators: {
    groundedness: { type: "builtin", name: "groundedness" },
    relevance: { type: "builtin", name: "relevance" },
    coherence: { type: "builtin", name: "coherence" }
  }
});
```

### A/B Model Comparison

```typescript
// Evaluate Model A
const modelAResults = await client.evaluations.create({
  displayName: "Model A Evaluation",
  data: testData.map(d => ({ ...d, response: modelAResponses[d.id] })),
  evaluators: { quality: { type: "builtin", name: "relevance" } }
});

// Evaluate Model B
const modelBResults = await client.evaluations.create({
  displayName: "Model B Evaluation", 
  data: testData.map(d => ({ ...d, response: modelBResponses[d.id] })),
  evaluators: { quality: { type: "builtin", name: "relevance" } }
});

// Compare
console.log(`Model A: ${modelAResults.metrics?.quality}`);
console.log(`Model B: ${modelBResults.metrics?.quality}`);
```

## See Also

- [Datasets Reference](./datasets.md)
- [Azure AI Evaluation](https://learn.microsoft.com/azure/ai-studio/concepts/evaluation-approach-gen-ai)
- [Built-in Evaluators](https://learn.microsoft.com/azure/ai-studio/how-to/evaluate-generative-ai-app)
