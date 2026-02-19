# Azure AI Translation SDK Acceptance Criteria (TypeScript)

**SDK**: `@azure-rest/ai-translation-text`, `@azure-rest/ai-translation-document`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/translation
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Text Translation Client Imports

#### ✅ CORRECT: TextTranslationClient Import
```typescript
import TextTranslationClient, { TranslatorCredential, isUnexpected } from "@azure-rest/ai-translation-text";
```

#### ✅ CORRECT: Document Translation Client Import
```typescript
import DocumentTranslationClient from "@azure-rest/ai-translation-document";
import { DefaultAzureCredential } from "@azure/identity";
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong package name
```typescript
// WRONG - package is @azure-rest/ai-translation-text, not @azure/ai-translation
import TextTranslationClient from "@azure/ai-translation";

// WRONG - using class-based imports (this is a REST client)
import { TextTranslationClient } from "@azure-rest/ai-translation-text";
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: API Key + Region Credential
```typescript
import TextTranslationClient, { TranslatorCredential } from "@azure-rest/ai-translation-text";

const credential: TranslatorCredential = {
  key: process.env.TRANSLATOR_SUBSCRIPTION_KEY!,
  region: process.env.TRANSLATOR_REGION!,
};
const client = TextTranslationClient(process.env.TRANSLATOR_ENDPOINT!, credential);
```

### 2.2 ✅ CORRECT: Just Credential (Global Endpoint)
```typescript
import TextTranslationClient, { TranslatorCredential } from "@azure-rest/ai-translation-text";

const credential: TranslatorCredential = {
  key: process.env.TRANSLATOR_SUBSCRIPTION_KEY!,
  region: process.env.TRANSLATOR_REGION!,
};
const client = TextTranslationClient(credential);
```

### 2.3 ✅ CORRECT: Document Translation with DefaultAzureCredential
```typescript
import DocumentTranslationClient from "@azure-rest/ai-translation-document";
import { DefaultAzureCredential } from "@azure/identity";

const client = DocumentTranslationClient(
  process.env.DOCUMENT_TRANSLATION_ENDPOINT!,
  new DefaultAzureCredential()
);
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing 'new' for REST client (it's a function)
```typescript
// WRONG - TextTranslationClient is a function, not a class
const client = new TextTranslationClient(endpoint, credential);
```

#### ❌ INCORRECT: Hardcoded credentials
```typescript
// WRONG - hardcoded API key
const credential: TranslatorCredential = {
  key: "my-api-key-12345",
  region: "westus",
};
```

---

## 3. Text Translation Patterns

### 3.1 ✅ CORRECT: Basic Translation
```typescript
import TextTranslationClient, { isUnexpected } from "@azure-rest/ai-translation-text";

const response = await client.path("/translate").post({
  body: {
    inputs: [
      {
        text: "Hello, how are you?",
        targets: [
          { language: "es" },
          { language: "fr" },
        ],
      },
    ],
  },
});

if (isUnexpected(response)) {
  throw response.body.error;
}

for (const result of response.body.value) {
  for (const translation of result.translations) {
    console.log(`${translation.language}: ${translation.text}`);
  }
}
```

### 3.2 ✅ CORRECT: Translation with Source Language
```typescript
const response = await client.path("/translate").post({
  body: {
    inputs: [
      {
        text: "Hello world",
        language: "en",
        targets: [{ language: "de" }],
      },
    ],
  },
});
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not checking isUnexpected
```typescript
// WRONG - must check for errors
const response = await client.path("/translate").post({...});
console.log(response.body.value);  // May fail if error
```

#### ❌ INCORRECT: Wrong request structure
```typescript
// WRONG - inputs is array, not object
const response = await client.path("/translate").post({
  body: {
    text: "Hello",
    to: ["es"],
  },
});
```

---

## 4. Language Detection Patterns

### 4.1 ✅ CORRECT: Detect Language
```typescript
const response = await client.path("/detect").post({
  body: { inputs: [{ text: "Bonjour le monde" }] },
});

if (!isUnexpected(response)) {
  for (const result of response.body.value) {
    console.log(`Language: ${result.language}, Score: ${result.score}`);
  }
}
```

---

## 5. Transliteration Patterns

### 5.1 ✅ CORRECT: Transliterate Text
```typescript
const response = await client.path("/transliterate").post({
  body: { inputs: [{ text: "这是个测试" }] },
  queryParameters: {
    language: "zh-Hans",
    fromScript: "Hans",
    toScript: "Latn",
  },
});

if (!isUnexpected(response)) {
  for (const t of response.body.value) {
    console.log(`${t.script}: ${t.text}`);
  }
}
```

---

## 6. Document Translation Patterns

### 6.1 ✅ CORRECT: Single Document Translation
```typescript
import DocumentTranslationClient from "@azure-rest/ai-translation-document";
import { writeFile } from "node:fs/promises";

const response = await client.path("/document:translate").post({
  queryParameters: {
    targetLanguage: "es",
    sourceLanguage: "en",
  },
  contentType: "multipart/form-data",
  body: [
    {
      name: "document",
      body: "Hello, this is a test document.",
      filename: "test.txt",
      contentType: "text/plain",
    },
  ],
}).asNodeStream();

if (response.status === "200") {
  await writeFile("translated.txt", response.body);
}
```

### 6.2 ✅ CORRECT: Batch Document Translation
```typescript
const response = await client.path("/document/batches").post({
  body: {
    inputs: [
      {
        source: { sourceUrl: sourceSasUrl },
        targets: [
          { targetUrl: targetSasUrl, language: "fr" },
        ],
      },
    ],
  },
});

const operationId = new URL(response.headers["operation-location"])
  .pathname.split("/").pop();
```

### 6.3 ✅ CORRECT: Get Translation Status
```typescript
import { isUnexpected, paginate } from "@azure-rest/ai-translation-document";

const statusResponse = await client.path("/document/batches/{id}", operationId).get();

if (!isUnexpected(statusResponse)) {
  const status = statusResponse.body;
  console.log(`Status: ${status.status}`);
  console.log(`Total: ${status.summary.total}`);
}
```

---

## 7. Get Supported Languages

### 7.1 ✅ CORRECT: List Languages
```typescript
const response = await client.path("/languages").get();

if (!isUnexpected(response)) {
  for (const [code, lang] of Object.entries(response.body.translation || {})) {
    console.log(`${code}: ${lang.name} (${lang.nativeName})`);
  }
}
```

---

## 8. Environment Variables

### 8.1 ✅ CORRECT: Required Variables
```typescript
const endpoint = process.env.TRANSLATOR_ENDPOINT!;
const key = process.env.TRANSLATOR_SUBSCRIPTION_KEY!;
const region = process.env.TRANSLATOR_REGION!;
```

### 8.2 ❌ INCORRECT: Hardcoded values
```typescript
// WRONG - hardcoded endpoint
const client = TextTranslationClient("https://api.cognitive.microsofttranslator.com", credential);
```

---

## 9. Error Handling Patterns

### 9.1 ✅ CORRECT: Check isUnexpected
```typescript
const response = await client.path("/translate").post({...});

if (isUnexpected(response)) {
  console.error("Error:", response.body.error);
  throw new Error(response.body.error.message);
}
```

### 9.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Ignoring error handling
```typescript
// WRONG - no error check
const response = await client.path("/translate").post({...});
const translations = response.body.value;  // May throw if error
```
