# Azure Storage Blob SDK for TypeScript Acceptance Criteria

**SDK**: `@azure/storage-blob`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/storage/storage-blob
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: ESM Imports

```typescript
import { 
  BlobServiceClient,
  ContainerClient,
  BlobClient,
  BlockBlobClient,
} from "@azure/storage-blob";
```

### 1.2 ✅ CORRECT: Type Imports

```typescript
import type { 
  BlobDownloadResponseParsed,
  BlobUploadCommonResponse,
  ContainerCreateResponse,
  BlobItem,
  ContainerItem,
  RestError,
} from "@azure/storage-blob";
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: CommonJS require

```typescript
// WRONG - Use ESM imports
const { BlobServiceClient } = require("@azure/storage-blob");
```

---

## 2. Authentication

### 2.1 ✅ CORRECT: DefaultAzureCredential (Recommended)

```typescript
import { BlobServiceClient } from "@azure/storage-blob";
import { DefaultAzureCredential } from "@azure/identity";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const client = new BlobServiceClient(
  `https://${accountName}.blob.core.windows.net`,
  new DefaultAzureCredential()
);
```

### 2.2 ✅ CORRECT: Connection String

```typescript
import { BlobServiceClient } from "@azure/storage-blob";

const client = BlobServiceClient.fromConnectionString(
  process.env.AZURE_STORAGE_CONNECTION_STRING!
);
```

### 2.3 ✅ CORRECT: StorageSharedKeyCredential (Node.js only)

```typescript
import { BlobServiceClient, StorageSharedKeyCredential } from "@azure/storage-blob";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY!;

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);
const client = new BlobServiceClient(
  `https://${accountName}.blob.core.windows.net`,
  sharedKeyCredential
);
```

### 2.4 ✅ CORRECT: SAS Token

```typescript
import { BlobServiceClient } from "@azure/storage-blob";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const sasToken = process.env.AZURE_STORAGE_SAS_TOKEN!; // starts with "?"

const client = new BlobServiceClient(
  `https://${accountName}.blob.core.windows.net${sasToken}`
);
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials

```typescript
// WRONG - Never hardcode credentials
const client = new BlobServiceClient(
  "https://myaccount.blob.core.windows.net",
  new StorageSharedKeyCredential("myaccount", "mySecretKey==")  // SECURITY RISK
);
```

---

## 3. Container Operations

### 3.1 ✅ CORRECT: Create Container

```typescript
const containerClient = client.getContainerClient("my-container");
await containerClient.create();

// Or create if not exists (idempotent)
await containerClient.createIfNotExists();
```

### 3.2 ✅ CORRECT: List Containers

```typescript
for await (const container of client.listContainers()) {
  console.log(container.name);
}

// With prefix filter
for await (const container of client.listContainers({ prefix: "logs-" })) {
  console.log(container.name);
}
```

### 3.3 ✅ CORRECT: Delete Container

```typescript
await containerClient.delete();

// Or delete if exists (idempotent)
await containerClient.deleteIfExists();
```

---

## 4. Blob Upload Operations

### 4.1 ✅ CORRECT: Upload String or Buffer

```typescript
const containerClient = client.getContainerClient("my-container");
const blockBlobClient = containerClient.getBlockBlobClient("my-file.txt");

// Upload string
await blockBlobClient.upload("Hello, World!", 13);

// Upload Buffer
const buffer = Buffer.from("Hello, World!");
await blockBlobClient.upload(buffer, buffer.length);
```

### 4.2 ✅ CORRECT: Upload from File (Node.js only)

```typescript
const blockBlobClient = containerClient.getBlockBlobClient("uploaded-file.txt");
await blockBlobClient.uploadFile("/path/to/local/file.txt");
```

### 4.3 ✅ CORRECT: Upload from Stream (Node.js only)

```typescript
import * as fs from "fs";

const blockBlobClient = containerClient.getBlockBlobClient("streamed-file.txt");
const readStream = fs.createReadStream("/path/to/local/file.txt");

await blockBlobClient.uploadStream(readStream, 4 * 1024 * 1024, 5, {
  onProgress: (progress) => console.log(`Uploaded ${progress.loadedBytes} bytes`),
});
```

### 4.4 ✅ CORRECT: Upload Data (Browser & Node.js)

```typescript
const blockBlobClient = containerClient.getBlockBlobClient("data.txt");

// From ArrayBuffer, Blob, or Buffer
await blockBlobClient.uploadData(myData);
```

---

## 5. Blob Download Operations

### 5.1 ✅ CORRECT: Download to Buffer (Node.js)

```typescript
const blobClient = containerClient.getBlobClient("my-file.txt");
const buffer = await blobClient.downloadToBuffer();
console.log(buffer.toString());
```

### 5.2 ✅ CORRECT: Download to File (Node.js)

```typescript
const blockBlobClient = containerClient.getBlockBlobClient("my-file.txt");
await blockBlobClient.downloadToFile("/path/to/local/destination.txt");
```

### 5.3 ✅ CORRECT: Download and Read Stream

```typescript
const blobClient = containerClient.getBlobClient("my-file.txt");
const downloadResponse = await blobClient.download();

// Node.js
const chunks: Buffer[] = [];
for await (const chunk of downloadResponse.readableStreamBody!) {
  chunks.push(Buffer.from(chunk));
}
const content = Buffer.concat(chunks).toString("utf-8");
```

---

## 6. List Blobs

### 6.1 ✅ CORRECT: List Blobs Flat

```typescript
for await (const blob of containerClient.listBlobsFlat()) {
  console.log(blob.name, blob.properties.contentLength);
}

// With prefix
for await (const blob of containerClient.listBlobsFlat({ prefix: "logs/" })) {
  console.log(blob.name);
}
```

### 6.2 ✅ CORRECT: List Blobs by Hierarchy

```typescript
for await (const item of containerClient.listBlobsByHierarchy("/")) {
  if (item.kind === "prefix") {
    console.log(`Directory: ${item.name}`);
  } else {
    console.log(`Blob: ${item.name}`);
  }
}
```

---

## 7. Blob Operations

### 7.1 ✅ CORRECT: Delete Blob

```typescript
const blobClient = containerClient.getBlobClient("my-file.txt");
await blobClient.delete();

// Delete if exists (idempotent)
await blobClient.deleteIfExists();

// Delete with snapshots
await blobClient.delete({ deleteSnapshots: "include" });
```

### 7.2 ✅ CORRECT: Copy Blob

```typescript
const sourceBlobClient = containerClient.getBlobClient("source.txt");
const destBlobClient = containerClient.getBlobClient("destination.txt");

const copyPoller = await destBlobClient.beginCopyFromURL(sourceBlobClient.url);
await copyPoller.pollUntilDone();
```

---

## 8. Blob Properties and Metadata

### 8.1 ✅ CORRECT: Get Properties

```typescript
const blobClient = containerClient.getBlobClient("my-file.txt");
const properties = await blobClient.getProperties();

console.log("Content-Type:", properties.contentType);
console.log("Content-Length:", properties.contentLength);
console.log("Last Modified:", properties.lastModified);
console.log("ETag:", properties.etag);
```

### 8.2 ✅ CORRECT: Set Metadata

```typescript
await blobClient.setMetadata({
  author: "John Doe",
  category: "documents",
});
```

### 8.3 ✅ CORRECT: Set HTTP Headers

```typescript
await blobClient.setHTTPHeaders({
  blobContentType: "text/plain",
  blobCacheControl: "max-age=3600",
  blobContentDisposition: "attachment; filename=download.txt",
});
```

---

## 9. SAS Token Generation (Node.js only)

### 9.1 ✅ CORRECT: Generate Blob SAS

```typescript
import {
  BlobSASPermissions,
  generateBlobSASQueryParameters,
  StorageSharedKeyCredential,
} from "@azure/storage-blob";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY!;

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);

const sasToken = generateBlobSASQueryParameters(
  {
    containerName: "my-container",
    blobName: "my-file.txt",
    permissions: BlobSASPermissions.parse("r"), // read only
    startsOn: new Date(),
    expiresOn: new Date(Date.now() + 3600 * 1000), // 1 hour
  },
  sharedKeyCredential
).toString();

const sasUrl = `https://${accountName}.blob.core.windows.net/my-container/my-file.txt?${sasToken}`;
```

### 9.2 ✅ CORRECT: Generate Container SAS

```typescript
import { ContainerSASPermissions, generateBlobSASQueryParameters } from "@azure/storage-blob";

const sasToken = generateBlobSASQueryParameters(
  {
    containerName: "my-container",
    permissions: ContainerSASPermissions.parse("racwdl"), // read, add, create, write, delete, list
    expiresOn: new Date(Date.now() + 24 * 3600 * 1000), // 24 hours
  },
  sharedKeyCredential
).toString();
```

---

## 10. Blob Types

### 10.1 ✅ CORRECT: Block Blob (Default)

```typescript
const blockBlobClient = containerClient.getBlockBlobClient("document.pdf");
await blockBlobClient.uploadFile("/path/to/document.pdf");
```

### 10.2 ✅ CORRECT: Append Blob

```typescript
const appendBlobClient = containerClient.getAppendBlobClient("app.log");

// Create the append blob
await appendBlobClient.create();

// Append data
await appendBlobClient.appendBlock("Log entry 1\n", 12);
await appendBlobClient.appendBlock("Log entry 2\n", 12);
```

### 10.3 ✅ CORRECT: Page Blob

```typescript
const pageBlobClient = containerClient.getPageBlobClient("disk.vhd");

// Create 512-byte aligned page blob
await pageBlobClient.create(1024 * 1024); // 1MB

// Write pages (must be 512-byte aligned)
const buffer = Buffer.alloc(512);
await pageBlobClient.uploadPages(buffer, 0, 512);
```

---

## 11. Error Handling

### 11.1 ✅ CORRECT: Handle Storage Errors

```typescript
import { RestError } from "@azure/storage-blob";

try {
  await containerClient.create();
} catch (error) {
  if (error instanceof RestError) {
    switch (error.statusCode) {
      case 404:
        console.log("Container not found");
        break;
      case 409:
        console.log("Container already exists");
        break;
      case 403:
        console.log("Access denied");
        break;
      default:
        console.error(`Storage error ${error.statusCode}: ${error.message}`);
    }
  }
  throw error;
}
```

---

## 12. Best Practices

1. **Use DefaultAzureCredential** — Prefer AAD over connection strings/keys
2. **Use streaming for large files** — `uploadStream`/`downloadToFile` for files > 256MB
3. **Set appropriate content types** — Use `setHTTPHeaders` for correct MIME types
4. **Use SAS tokens for client access** — Generate short-lived tokens for browser uploads
5. **Handle errors gracefully** — Check `RestError.statusCode` for specific handling
6. **Use `*IfNotExists` methods** — For idempotent container/blob creation
7. **Close clients** — Not required but good practice in long-running apps

---

## 13. Platform Differences

| Feature | Node.js | Browser |
|---------|---------|---------|
| `StorageSharedKeyCredential` | ✅ | ❌ |
| `uploadFile()` | ✅ | ❌ |
| `uploadStream()` | ✅ | ❌ |
| `downloadToFile()` | ✅ | ❌ |
| `downloadToBuffer()` | ✅ | ❌ |
| `uploadData()` | ✅ | ✅ |
| SAS generation | ✅ | ❌ |
| DefaultAzureCredential | ✅ | ❌ |
| Anonymous/SAS access | ✅ | ✅ |
