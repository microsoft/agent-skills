# Acceptance Criteria: azure-ai-document-intelligence-ts

## Overview

This document defines the acceptance criteria for code generated using the `@azure-rest/ai-document-intelligence` SDK for TypeScript/JavaScript.

**Package:** `@azure-rest/ai-document-intelligence`  
**Repository:** https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/documentintelligence/ai-document-intelligence-rest

> **Note:** This is a REST client library. Form Recognizer has been rebranded to Document Intelligence.

---

## 1. Import Statements

### ✅ MUST

```typescript
// ESM imports - REST client pattern
import DocumentIntelligence, {
  isUnexpected,
  getLongRunningPoller,
  AnalyzeOperationOutput,
  parseResultIdFromResponse,
} from "@azure-rest/ai-document-intelligence";
import { DefaultAzureCredential } from "@azure/identity";
```

### ❌ MUST NOT

```typescript
// CommonJS require
const DocumentIntelligence = require("@azure-rest/ai-document-intelligence");

// Old Form Recognizer SDK
import { DocumentAnalysisClient } from "@azure/ai-form-recognizer";

// Using new keyword (REST clients are factory functions)
const client = new DocumentIntelligence(endpoint, credential);
```

---

## 2. Client Instantiation

### ✅ MUST

```typescript
// With DefaultAzureCredential (recommended)
const endpoint = process.env.DOCUMENT_INTELLIGENCE_ENDPOINT!;
const client = DocumentIntelligence(endpoint, new DefaultAzureCredential());

// With API key
const client = DocumentIntelligence(endpoint, {
  key: process.env.DOCUMENT_INTELLIGENCE_API_KEY!,
});
```

### Sovereign Clouds

```typescript
import { KnownDocumentIntelligenceAudience } from "@azure-rest/ai-document-intelligence";

const client = DocumentIntelligence(endpoint, new DefaultAzureCredential(), {
  credentials: {
    scopes: [KnownDocumentIntelligenceAudience.AzureGovernment],
  },
});
```

### ❌ MUST NOT

```typescript
// Using new keyword
const client = new DocumentIntelligence(endpoint, credential);

// Hardcoded credentials
const client = DocumentIntelligence(endpoint, { key: "hardcoded-key" });
```

---

## 3. Analyze Documents

### Analyze with URL

```typescript
// ✅ Correct - using urlSource
const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-layout")
  .post({
    contentType: "application/json",
    body: {
      urlSource: "https://example.com/document.pdf",
    },
  });

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const poller = getLongRunningPoller(client, initialResponse);
const result = (await poller.pollUntilDone()).body as AnalyzeOperationOutput;
```

### Analyze with Base64

```typescript
import { readFile } from "node:fs/promises";

// ✅ Correct - using base64Source
const base64Source = await readFile("./document.pdf", { encoding: "base64" });

const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-invoice")
  .post({
    contentType: "application/json",
    body: {
      base64Source,
    },
  });

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const poller = getLongRunningPoller(client, initialResponse);
const result = (await poller.pollUntilDone()).body as AnalyzeOperationOutput;
```

### Available Prebuilt Models

| Model ID | Description |
|----------|-------------|
| `prebuilt-layout` | Extract text, tables, and structure |
| `prebuilt-read` | OCR with high accuracy |
| `prebuilt-invoice` | Extract invoice fields |
| `prebuilt-receipt` | Extract receipt fields |
| `prebuilt-idDocument` | Extract ID document fields |
| `prebuilt-tax.us.w2` | Extract W-2 form fields |
| `prebuilt-healthInsuranceCard.us` | Extract health insurance card fields |

---

## 4. Query Parameters

### Locale

```typescript
// ✅ Correct
const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-layout")
  .post({
    contentType: "application/json",
    body: { urlSource: "..." },
    queryParameters: { locale: "en-US" },
  });
```

### Markdown Output Format

```typescript
// ✅ Correct - get markdown output
const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-layout")
  .post({
    contentType: "application/json",
    body: { urlSource: "..." },
    queryParameters: { outputContentFormat: "markdown" },
  });
```

### Query Fields

```typescript
// ✅ Correct - extract specific fields
const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-layout")
  .post({
    contentType: "application/json",
    body: { urlSource: "..." },
    queryParameters: {
      features: ["queryFields"],
      queryFields: ["CustomerName", "InvoiceTotal"],
    },
  });
```

### Output Options (PDF, Figures)

```typescript
// ✅ Correct - request PDF and figures output
const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-layout")
  .post({
    contentType: "application/json",
    body: { base64Source },
    queryParameters: { output: ["pdf", "figures"] },
  });
```

---

## 5. Long-Running Operations

### Using getLongRunningPoller

```typescript
// ✅ Correct
const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-invoice")
  .post({...});

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const poller = getLongRunningPoller(client, initialResponse);
const result = (await poller.pollUntilDone()).body as AnalyzeOperationOutput;

// Access results
console.log(result.analyzeResult?.content);
for (const document of result.analyzeResult?.documents || []) {
  console.log("Document type:", document.docType);
  for (const [name, field] of Object.entries(document.fields || {})) {
    console.log(`${name}: ${field.valueString || field.value}`);
  }
}
```

---

## 6. Get Output Artifacts

### Get PDF Output

```typescript
import { streamToUint8Array } from "@azure-rest/ai-document-intelligence";
import { writeFile } from "node:fs/promises";

// ✅ Correct
const resultId = parseResultIdFromResponse(initialResponse);

const output = await client
  .path(
    "/documentModels/{modelId}/analyzeResults/{resultId}/pdf",
    "prebuilt-read",
    resultId
  )
  .get()
  .asNodeStream();

if (output.status !== "200" || !output.body) {
  throw new Error("Failed to get PDF");
}

const pdfData = await streamToUint8Array(output.body);
await writeFile("./output.pdf", pdfData);
```

### Get Figure Image

```typescript
// ✅ Correct
const figures = result.analyzeResult?.figures;
const figureId = figures?.[0].id;

const output = await client
  .path(
    "/documentModels/{modelId}/analyzeResults/{resultId}/figures/{figureId}",
    "prebuilt-layout",
    resultId,
    figureId
  )
  .get()
  .asNodeStream();

const imageData = await streamToUint8Array(output.body);
await writeFile(`./figure-${figureId}.png`, imageData);
```

---

## 7. Batch Analysis

```typescript
// ✅ Correct
const initialResponse = await client
  .path("/documentModels/{modelId}:analyzeBatch", "prebuilt-layout")
  .post({
    contentType: "application/json",
    body: {
      azureBlobSource: {
        containerUrl: process.env.BLOB_CONTAINER_SAS_URL,
      },
      resultContainerUrl: process.env.RESULT_CONTAINER_SAS_URL,
      resultPrefix: "results/",
    },
  });

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const resultId = parseResultIdFromResponse(initialResponse);
console.log("Batch job started, result ID:", resultId);
```

---

## 8. Custom Models

### Build Custom Model (Document Classifier)

```typescript
// ✅ Correct
const initialResponse = await client.path("/documentClassifiers:build").post({
  body: {
    classifierId: "my-classifier",
    description: "Document classifier",
    docTypes: {
      invoice: {
        azureBlobSource: {
          containerUrl: process.env.INVOICE_TRAINING_DATA_SAS_URL,
        },
      },
      receipt: {
        azureBlobSource: {
          containerUrl: process.env.RECEIPT_TRAINING_DATA_SAS_URL,
        },
      },
    },
  },
});

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const poller = getLongRunningPoller(client, initialResponse);
const classifier = await poller.pollUntilDone();
```

---

## 9. List and Get Models

### List Models

```typescript
import { paginate } from "@azure-rest/ai-document-intelligence";

// ✅ Correct
const response = await client.path("/documentModels").get();

if (isUnexpected(response)) {
  throw response.body.error;
}

for await (const model of paginate(client, response)) {
  console.log("Model ID:", model.modelId);
}
```

### Get Service Info

```typescript
// ✅ Correct
const response = await client.path("/info").get();

if (isUnexpected(response)) {
  throw response.body.error;
}

console.log("Custom document models limit:", response.body.customDocumentModels.limit);
```

---

## 10. Error Handling

### ✅ MUST use isUnexpected

```typescript
import DocumentIntelligence, { isUnexpected } from "@azure-rest/ai-document-intelligence";

const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-layout")
  .post({...});

if (isUnexpected(initialResponse)) {
  // Handle error
  console.error("Error:", initialResponse.body.error);
  throw initialResponse.body.error;
}

// Safe to proceed
const poller = getLongRunningPoller(client, initialResponse);
```

---

## 11. Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| `new DocumentIntelligence()` | `DocumentIntelligence()` (factory function) |
| Ignoring `isUnexpected()` | Always check with `isUnexpected()` |
| `@azure/ai-form-recognizer` | `@azure-rest/ai-document-intelligence` |
| Direct result access | Use `getLongRunningPoller()` for analyze operations |
| Missing poller await | Always await `pollUntilDone()` |

---

## 12. Type Imports

```typescript
import DocumentIntelligence, {
  isUnexpected,
  getLongRunningPoller,
  parseResultIdFromResponse,
  streamToUint8Array,
  paginate,
  AnalyzeOperationOutput,
  DocumentClassifierBuildOperationDetailsOutput,
  KnownDocumentIntelligenceAudience,
} from "@azure-rest/ai-document-intelligence";
```

---

## References

- [Official SDK README](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/documentintelligence/ai-document-intelligence-rest)
- [Migration Guide from Form Recognizer](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/documentintelligence/ai-document-intelligence-rest/MIGRATION-FR_v4-DI_v1.md)
- [API Reference](https://learn.microsoft.com/javascript/api/@azure-rest/ai-document-intelligence)
- [Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/documentintelligence/ai-document-intelligence-rest/samples)
