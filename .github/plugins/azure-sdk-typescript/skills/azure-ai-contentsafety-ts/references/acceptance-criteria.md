# Acceptance Criteria: azure-ai-contentsafety-ts

## Overview

This document defines the acceptance criteria for code generated using the `@azure-rest/ai-content-safety` SDK for TypeScript/JavaScript.

**Package:** `@azure-rest/ai-content-safety`  
**Repository:** https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/contentsafety/ai-content-safety-rest

> **Note:** This is a REST client library. Please refer to [REST client docs](https://github.com/Azure/azure-sdk-for-js/blob/main/documentation/rest-clients.md).

---

## 1. Import Statements

### ✅ MUST

```typescript
// ESM imports - REST client pattern
import ContentSafetyClient, { isUnexpected } from "@azure-rest/ai-content-safety";
import { AzureKeyCredential } from "@azure/core-auth";
import { DefaultAzureCredential } from "@azure/identity";
```

### ❌ MUST NOT

```typescript
// CommonJS require
const ContentSafetyClient = require("@azure-rest/ai-content-safety");

// Non-REST client patterns
import { ContentSafetyClient } from "@azure/ai-content-safety";
```

---

## 2. Client Instantiation

### ✅ MUST

```typescript
// With DefaultAzureCredential (recommended)
const endpoint = "https://<resource>.cognitiveservices.azure.com/";
const credential = new DefaultAzureCredential();
const client = ContentSafetyClient(endpoint, credential);

// With API key
const credential = new AzureKeyCredential("<api_key>");
const client = ContentSafetyClient(endpoint, credential);
```

### ❌ MUST NOT

```typescript
// Using new keyword (REST clients are factory functions)
const client = new ContentSafetyClient(endpoint, credential);

// Hardcoded credentials
const client = ContentSafetyClient(endpoint, "hardcoded-key");
```

---

## 3. Text Analysis

### Analyze Text

```typescript
// ✅ Correct - using path and post
const result = await client.path("/text:analyze").post({
  body: {
    text: "Sample text to analyze",
  },
});

if (isUnexpected(result)) {
  throw result;
}

for (const category of result.body.categoriesAnalysis) {
  console.log(`${category.category}: severity ${category.severity}`);
}
```

### Analyze Text with Options

```typescript
// ✅ Correct - with categories and output type
const result = await client.path("/text:analyze").post({
  body: {
    text: "Sample text to analyze",
    categories: ["Hate", "Violence", "Sexual", "SelfHarm"],
    outputType: "EightSeverityLevels", // or "FourSeverityLevels"
  },
});
```

### Analyze Text with Blocklists

```typescript
// ✅ Correct - with blocklist
const result = await client.path("/text:analyze").post({
  body: {
    text: "Sample text to check",
    blocklistNames: ["MyBlocklist"],
    haltOnBlocklistHit: false,
  },
});

// Check blocklist matches
if (result.body.blocklistsMatch) {
  for (const match of result.body.blocklistsMatch) {
    console.log(`Blocklist: ${match.blocklistName}, Item: ${match.blocklistItemText}`);
  }
}
```

---

## 4. Image Analysis

### Analyze Image from Base64

```typescript
import { readFileSync } from "node:fs";

// ✅ Correct - base64 content
const imageBuffer = readFileSync("./image.png");
const base64Image = imageBuffer.toString("base64");

const result = await client.path("/image:analyze").post({
  body: {
    image: { content: base64Image },
  },
});

if (isUnexpected(result)) {
  throw result;
}

for (const category of result.body.categoriesAnalysis) {
  console.log(`${category.category}: severity ${category.severity}`);
}
```

### Analyze Image from URL

```typescript
// ✅ Correct - URL reference
const result = await client.path("/image:analyze").post({
  body: {
    image: { blobUrl: "https://example.blob.core.windows.net/images/sample.png" },
  },
});
```

---

## 5. Blocklist Management

### Create or Update Blocklist

```typescript
// ✅ Correct - using patch with merge-patch content type
const result = await client
  .path("/text/blocklists/{blocklistName}", "MyBlocklist")
  .patch({
    contentType: "application/merge-patch+json",
    body: {
      description: "Custom blocklist for my application",
    },
  });

if (isUnexpected(result)) {
  throw result;
}

console.log("Blocklist created:", result.body.blocklistName);
```

### Add Block Items

```typescript
// ✅ Correct
const result = await client
  .path("/text/blocklists/{blocklistName}:addOrUpdateBlocklistItems", "MyBlocklist")
  .post({
    body: {
      blocklistItems: [
        { text: "badword1", description: "Profanity" },
        { text: "badword2", description: "Slur" },
      ],
    },
  });

if (isUnexpected(result)) {
  throw result;
}

for (const item of result.body.blocklistItems || []) {
  console.log(`Added: ${item.text} (ID: ${item.blocklistItemId})`);
}
```

### List Blocklists

```typescript
// ✅ Correct
const result = await client.path("/text/blocklists").get();

if (isUnexpected(result)) {
  throw result;
}

for (const blocklist of result.body.value || []) {
  console.log(`${blocklist.blocklistName}: ${blocklist.description}`);
}
```

### Get Blocklist

```typescript
// ✅ Correct
const result = await client
  .path("/text/blocklists/{blocklistName}", "MyBlocklist")
  .get();

if (isUnexpected(result)) {
  throw result;
}

console.log("Blocklist:", result.body.blocklistName);
```

### List Block Items

```typescript
// ✅ Correct
const result = await client
  .path("/text/blocklists/{blocklistName}/blocklistItems", "MyBlocklist")
  .get();

if (isUnexpected(result)) {
  throw result;
}

for (const item of result.body.value || []) {
  console.log(`${item.text} (ID: ${item.blocklistItemId})`);
}
```

### Remove Block Items

```typescript
// ✅ Correct
const result = await client
  .path("/text/blocklists/{blocklistName}:removeBlocklistItems", "MyBlocklist")
  .post({
    body: {
      blocklistItemIds: ["item-id-1", "item-id-2"],
    },
  });
```

### Delete Blocklist

```typescript
// ✅ Correct
const result = await client
  .path("/text/blocklists/{blocklistName}", "MyBlocklist")
  .delete();

if (isUnexpected(result)) {
  throw result;
}

console.log("Blocklist deleted");
```

---

## 6. Error Handling

### ✅ MUST use isUnexpected

```typescript
import ContentSafetyClient, { isUnexpected } from "@azure-rest/ai-content-safety";

const result = await client.path("/text:analyze").post({
  body: { text: "Sample text" },
});

if (isUnexpected(result)) {
  // result.body contains error information
  console.error("Error:", result.body);
  throw result;
}

// Safe to access result.body as success response
console.log(result.body.categoriesAnalysis);
```

### ❌ MUST NOT

```typescript
// Ignoring isUnexpected check
const result = await client.path("/text:analyze").post({...});
console.log(result.body.categoriesAnalysis); // May throw if error

// Empty catch blocks
try {
  await client.path("/text:analyze").post({...});
} catch (error) {
  // silently ignore
}
```

---

## 7. Response Categories

### Harm Categories

The SDK analyzes content for these categories:

| Category | Description |
|----------|-------------|
| `Hate` | Discriminatory content based on identity |
| `Sexual` | Sexual content |
| `Violence` | Violence-related content |
| `SelfHarm` | Self-harm related content |

### Severity Levels

```typescript
// Four severity levels (default)
// 0, 2, 4, 6

// Eight severity levels (when outputType: "EightSeverityLevels")
// 0, 1, 2, 3, 4, 5, 6, 7
```

---

## 8. Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| `new ContentSafetyClient()` | `ContentSafetyClient()` (factory function) |
| Ignoring `isUnexpected()` | Always check with `isUnexpected()` |
| `require("@azure-rest/ai-content-safety")` | `import ContentSafetyClient from "@azure-rest/ai-content-safety"` |
| Hardcoded API keys | Use `AzureKeyCredential` or `DefaultAzureCredential` |
| Direct property access on result | Check `isUnexpected()` first |

---

## 9. Type Imports

```typescript
import ContentSafetyClient, {
  isUnexpected,
  AnalyzeTextOptions,
  AnalyzeImageOptions,
  TextBlocklist,
  AddOrUpdateTextBlocklistItemsOptions,
} from "@azure-rest/ai-content-safety";

import { AzureKeyCredential } from "@azure/core-auth";
import { DefaultAzureCredential } from "@azure/identity";
```

---

## 10. REST Client Patterns

This SDK follows the Azure REST client pattern:

```typescript
// Path-based method calls
client.path("/text:analyze").post({ body: {...} })
client.path("/image:analyze").post({ body: {...} })
client.path("/text/blocklists/{blocklistName}", name).get()
client.path("/text/blocklists/{blocklistName}", name).patch({...})
client.path("/text/blocklists/{blocklistName}", name).delete()
```

---

## References

- [Official SDK README](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/contentsafety/ai-content-safety-rest)
- [REST Client Documentation](https://github.com/Azure/azure-sdk-for-js/blob/main/documentation/rest-clients.md)
- [API Reference](https://learn.microsoft.com/javascript/api/@azure-rest/ai-content-safety)
- [Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/contentsafety/ai-content-safety-rest/samples)
