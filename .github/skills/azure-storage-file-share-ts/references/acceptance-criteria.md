# Azure Storage File Share SDK Acceptance Criteria (TypeScript)

**SDK**: `@azure/storage-file-share`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/storage/storage-file-share
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Core Client Imports
```typescript
import { ShareServiceClient, ShareClient, ShareDirectoryClient, ShareFileClient } from "@azure/storage-file-share";
```

#### ✅ CORRECT: With Authentication
```typescript
import { ShareServiceClient, StorageSharedKeyCredential } from "@azure/storage-file-share";
import { DefaultAzureCredential } from "@azure/identity";
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong package name
```typescript
// WRONG - package is @azure/storage-file-share
import { ShareServiceClient } from "@azure/storage-file";
import { ShareServiceClient } from "azure-storage";
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: Connection String
```typescript
import { ShareServiceClient } from "@azure/storage-file-share";

const client = ShareServiceClient.fromConnectionString(
  process.env.AZURE_STORAGE_CONNECTION_STRING!
);
```

### 2.2 ✅ CORRECT: StorageSharedKeyCredential
```typescript
import { ShareServiceClient, StorageSharedKeyCredential } from "@azure/storage-file-share";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY!;

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);
const client = new ShareServiceClient(
  `https://${accountName}.file.core.windows.net`,
  sharedKeyCredential
);
```

### 2.3 ✅ CORRECT: DefaultAzureCredential
```typescript
import { ShareServiceClient } from "@azure/storage-file-share";
import { DefaultAzureCredential } from "@azure/identity";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const client = new ShareServiceClient(
  `https://${accountName}.file.core.windows.net`,
  new DefaultAzureCredential()
);
```

### 2.4 ✅ CORRECT: SAS Token
```typescript
import { ShareServiceClient } from "@azure/storage-file-share";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const sasToken = process.env.AZURE_STORAGE_SAS_TOKEN!;

const client = new ShareServiceClient(
  `https://${accountName}.file.core.windows.net${sasToken}`
);
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```typescript
// WRONG - hardcoded account key
const sharedKeyCredential = new StorageSharedKeyCredential(
  "myaccount",
  "myaccountkey12345"
);
```

---

## 3. Share Operations Patterns

### 3.1 ✅ CORRECT: Create Share
```typescript
const shareClient = client.getShareClient("my-share");
await shareClient.create();

// Create with quota
await shareClient.create({ quota: 100 });
```

### 3.2 ✅ CORRECT: List Shares
```typescript
for await (const share of client.listShares()) {
  console.log(share.name, share.properties.quota);
}

// With prefix filter
for await (const share of client.listShares({ prefix: "logs-" })) {
  console.log(share.name);
}
```

### 3.3 ✅ CORRECT: Delete Share
```typescript
await shareClient.delete();

// Delete if exists
await shareClient.deleteIfExists();
```

### 3.4 ✅ CORRECT: Get Share Properties
```typescript
const properties = await shareClient.getProperties();
console.log("Quota:", properties.quota, "GB");
console.log("Last Modified:", properties.lastModified);
```

---

## 4. Directory Operations Patterns

### 4.1 ✅ CORRECT: Create Directory
```typescript
const directoryClient = shareClient.getDirectoryClient("my-directory");
await directoryClient.create();

// Create nested directory
const nestedDir = shareClient.getDirectoryClient("parent/child/grandchild");
await nestedDir.create();
```

### 4.2 ✅ CORRECT: List Files and Directories
```typescript
const directoryClient = shareClient.getDirectoryClient("my-directory");

for await (const item of directoryClient.listFilesAndDirectories()) {
  if (item.kind === "directory") {
    console.log(`[DIR] ${item.name}`);
  } else {
    console.log(`[FILE] ${item.name} (${item.properties.contentLength} bytes)`);
  }
}
```

### 4.3 ✅ CORRECT: Check Directory Exists
```typescript
const exists = await directoryClient.exists();
if (!exists) {
  await directoryClient.create();
}
```

---

## 5. File Operations Patterns

### 5.1 ✅ CORRECT: Upload File Content
```typescript
const fileClient = shareClient
  .getDirectoryClient("my-directory")
  .getFileClient("my-file.txt");

const content = "Hello, World!";
await fileClient.create(content.length);
await fileClient.uploadRange(content, 0, content.length);
```

### 5.2 ✅ CORRECT: Upload from Local File (Node.js)
```typescript
import * as fs from "fs";

const fileClient = shareClient.rootDirectoryClient.getFileClient("uploaded.txt");
const localFilePath = "/path/to/local/file.txt";
const fileSize = fs.statSync(localFilePath).size;

await fileClient.create(fileSize);
await fileClient.uploadFile(localFilePath);
```

### 5.3 ✅ CORRECT: Download File
```typescript
const fileClient = shareClient
  .getDirectoryClient("my-directory")
  .getFileClient("my-file.txt");

const downloadResponse = await fileClient.download();

const chunks: Buffer[] = [];
for await (const chunk of downloadResponse.readableStreamBody!) {
  chunks.push(Buffer.from(chunk));
}
const content = Buffer.concat(chunks).toString("utf-8");
```

### 5.4 ✅ CORRECT: Download to File (Node.js)
```typescript
const fileClient = shareClient.rootDirectoryClient.getFileClient("my-file.txt");
await fileClient.downloadToFile("/path/to/local/destination.txt");
```

### 5.5 ✅ CORRECT: Download to Buffer (Node.js)
```typescript
const fileClient = shareClient.rootDirectoryClient.getFileClient("my-file.txt");
const buffer = await fileClient.downloadToBuffer();
console.log(buffer.toString());
```

### 5.6 ✅ CORRECT: Delete File
```typescript
const fileClient = shareClient.rootDirectoryClient.getFileClient("my-file.txt");
await fileClient.delete();

// Delete if exists
await fileClient.deleteIfExists();
```

### 5.7 ✅ CORRECT: Copy File
```typescript
const sourceUrl = "https://account.file.core.windows.net/share/source.txt";
const destFileClient = shareClient.rootDirectoryClient.getFileClient("destination.txt");

const copyPoller = await destFileClient.startCopyFromURL(sourceUrl);
await copyPoller.pollUntilDone();
```

---

## 6. File Properties & Metadata Patterns

### 6.1 ✅ CORRECT: Get File Properties
```typescript
const fileClient = shareClient.rootDirectoryClient.getFileClient("my-file.txt");
const properties = await fileClient.getProperties();

console.log("Content-Length:", properties.contentLength);
console.log("Content-Type:", properties.contentType);
console.log("Last Modified:", properties.lastModified);
```

### 6.2 ✅ CORRECT: Set Metadata
```typescript
await fileClient.setMetadata({
  author: "John Doe",
  category: "documents",
});
```

### 6.3 ✅ CORRECT: Set HTTP Headers
```typescript
await fileClient.setHttpHeaders({
  fileContentType: "text/plain",
  fileCacheControl: "max-age=3600",
  fileContentDisposition: "attachment; filename=download.txt",
});
```

---

## 7. SAS Token Generation Patterns

### 7.1 ✅ CORRECT: Generate File SAS
```typescript
import {
  generateFileSASQueryParameters,
  FileSASPermissions,
  StorageSharedKeyCredential,
} from "@azure/storage-file-share";

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);

const sasToken = generateFileSASQueryParameters(
  {
    shareName: "my-share",
    filePath: "my-directory/my-file.txt",
    permissions: FileSASPermissions.parse("r"),
    expiresOn: new Date(Date.now() + 3600 * 1000),
  },
  sharedKeyCredential
).toString();

const sasUrl = `https://${accountName}.file.core.windows.net/my-share/my-directory/my-file.txt?${sasToken}`;
```

---

## 8. Snapshot Operations Patterns

### 8.1 ✅ CORRECT: Create Snapshot
```typescript
const snapshotResponse = await shareClient.createSnapshot();
console.log("Snapshot:", snapshotResponse.snapshot);
```

### 8.2 ✅ CORRECT: Access Snapshot
```typescript
const snapshotShareClient = shareClient.withSnapshot(snapshotResponse.snapshot!);
const snapshotFileClient = snapshotShareClient.rootDirectoryClient.getFileClient("file.txt");
const content = await snapshotFileClient.downloadToBuffer();
```

---

## 9. Error Handling Patterns

### 9.1 ✅ CORRECT: Handle RestError
```typescript
import { RestError } from "@azure/storage-file-share";

try {
  await shareClient.create();
} catch (error) {
  if (error instanceof RestError) {
    switch (error.statusCode) {
      case 404:
        console.log("Share not found");
        break;
      case 409:
        console.log("Share already exists");
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

## 10. Environment Variables

### 10.1 ✅ CORRECT: Required Variables
```typescript
const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY!;
const connectionString = process.env.AZURE_STORAGE_CONNECTION_STRING!;
```

### 10.2 ❌ INCORRECT: Hardcoded values
```typescript
// WRONG - hardcoded account
const client = new ShareServiceClient(
  "https://myaccount.file.core.windows.net",
  sharedKeyCredential
);
```
