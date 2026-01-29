# @azure/storage-blob - Streaming Patterns

Reference documentation for upload/download streaming in the Azure Blob Storage TypeScript SDK.

**Source**: [Azure SDK for JS - storage-blob](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/storage/storage-blob)

---

## Installation

```bash
npm install @azure/storage-blob @azure/identity
```

---

## Client Setup

```typescript
import {
  BlobServiceClient,
  ContainerClient,
  BlockBlobClient,
} from "@azure/storage-blob";
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();
const accountUrl = `https://${process.env["STORAGE_ACCOUNT_NAME"]}.blob.core.windows.net`;

const blobServiceClient = new BlobServiceClient(accountUrl, credential);
const containerClient = blobServiceClient.getContainerClient("my-container");
const blobClient = containerClient.getBlockBlobClient("my-blob.txt");
```

---

## Download Streaming

### Download to Buffer

```typescript
const downloadResponse = await blobClient.download(0);
const downloaded = await streamToBuffer(downloadResponse.readableStreamBody!);

async function streamToBuffer(readableStream: NodeJS.ReadableStream): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    readableStream.on("data", (data) => chunks.push(Buffer.from(data)));
    readableStream.on("end", () => resolve(Buffer.concat(chunks)));
    readableStream.on("error", reject);
  });
}
```

### Download to File (Node.js)

```typescript
import fs from "node:fs";
import { pipeline } from "node:stream/promises";

const downloadResponse = await blobClient.download(0);
await pipeline(
  downloadResponse.readableStreamBody!,
  fs.createWriteStream("./local-file.txt")
);
```

### Download with Range

```typescript
// Download bytes 100-199 (100 bytes total)
const downloadResponse = await blobClient.download(100, 100);
```

### Download with Progress

```typescript
const downloadResponse = await blobClient.download(0, undefined, {
  onProgress: (progress) => {
    console.log(`Downloaded ${progress.loadedBytes} bytes`);
  },
});
```

---

## Upload Streaming

### Upload from Buffer

```typescript
const content = Buffer.from("Hello, World!");
await blobClient.upload(content, content.length);
```

### Upload from Stream (Node.js)

```typescript
import fs from "node:fs";

const fileStream = fs.createReadStream("./large-file.zip");
const fileSize = fs.statSync("./large-file.zip").size;

await blobClient.uploadStream(fileStream, fileSize, 4, {
  onProgress: (progress) => {
    const percent = ((progress.loadedBytes / fileSize) * 100).toFixed(2);
    console.log(`Upload progress: ${percent}%`);
  },
});
```

### Upload with Options

```typescript
await blobClient.uploadStream(fileStream, fileSize, 4, {
  // Number of concurrent upload operations
  concurrency: 4,
  
  // Size of each block (4MB default, max 4000MB)
  bufferSize: 4 * 1024 * 1024,
  
  // Progress tracking
  onProgress: (progress) => {
    console.log(`Uploaded: ${progress.loadedBytes} bytes`);
  },
  
  // HTTP headers
  blobHTTPHeaders: {
    blobContentType: "application/zip",
    blobContentEncoding: "gzip",
  },
  
  // Custom metadata
  metadata: {
    uploadedBy: "my-app",
    version: "1.0",
  },
  
  // Access tier
  tier: "Cool",
});
```

---

## Block Upload (Large Files)

For large files, use staged block uploads for better control:

```typescript
import { BlockBlobClient, BlockBlobStageBlockOptions } from "@azure/storage-blob";
import { v4 as uuidv4 } from "uuid";

async function uploadLargeFile(
  blobClient: BlockBlobClient,
  filePath: string,
  blockSize = 4 * 1024 * 1024 // 4MB blocks
) {
  const fileHandle = await fs.promises.open(filePath, "r");
  const fileStats = await fileHandle.stat();
  const fileSize = fileStats.size;
  
  const blockIds: string[] = [];
  let offset = 0;
  let blockIndex = 0;
  
  try {
    while (offset < fileSize) {
      const chunkSize = Math.min(blockSize, fileSize - offset);
      const buffer = Buffer.alloc(chunkSize);
      
      await fileHandle.read(buffer, 0, chunkSize, offset);
      
      // Generate block ID (must be base64 encoded, same length)
      const blockId = Buffer.from(
        blockIndex.toString().padStart(6, "0")
      ).toString("base64");
      
      // Stage the block
      await blobClient.stageBlock(blockId, buffer, buffer.length);
      
      blockIds.push(blockId);
      offset += chunkSize;
      blockIndex++;
      
      console.log(`Staged block ${blockIndex}, offset: ${offset}/${fileSize}`);
    }
    
    // Commit all blocks
    await blobClient.commitBlockList(blockIds, {
      blobHTTPHeaders: {
        blobContentType: "application/octet-stream",
      },
    });
    
    console.log("Upload complete!");
  } finally {
    await fileHandle.close();
  }
}
```

---

## Parallel Upload/Download

### Parallel Download to File

```typescript
import { BlobClient } from "@azure/storage-blob";

// Downloads in parallel chunks automatically
await blobClient.downloadToFile("./local-file.zip", 0, undefined, {
  // Chunk size for parallel download
  blockSize: 4 * 1024 * 1024,
  
  // Number of parallel downloads
  concurrency: 4,
  
  onProgress: (progress) => {
    console.log(`Downloaded: ${progress.loadedBytes} bytes`);
  },
});
```

### Parallel Upload from File

```typescript
// Uploads in parallel chunks automatically
await blobClient.uploadFile("./large-file.zip", {
  // Chunk size
  blockSize: 4 * 1024 * 1024,
  
  // Parallel uploads
  concurrency: 4,
  
  onProgress: (progress) => {
    console.log(`Uploaded: ${progress.loadedBytes} bytes`);
  },
  
  blobHTTPHeaders: {
    blobContentType: "application/zip",
  },
});
```

---

## Browser Upload

For browser environments, use `uploadBrowserData`:

```typescript
// From File input
const fileInput = document.getElementById("file") as HTMLInputElement;
const file = fileInput.files![0];

await blobClient.uploadBrowserData(file, {
  onProgress: (progress) => {
    const percent = ((progress.loadedBytes / file.size) * 100).toFixed(2);
    document.getElementById("progress")!.textContent = `${percent}%`;
  },
  blobHTTPHeaders: {
    blobContentType: file.type,
  },
});

// From ArrayBuffer
const arrayBuffer = await file.arrayBuffer();
await blobClient.uploadBrowserData(arrayBuffer);

// From Blob
const blob = new Blob(["Hello, World!"], { type: "text/plain" });
await blobClient.uploadBrowserData(blob);
```

---

## Abort Operations

Cancel long-running uploads/downloads:

```typescript
const abortController = new AbortController();

// Set up abort after 30 seconds
setTimeout(() => abortController.abort(), 30000);

try {
  await blobClient.uploadFile("./large-file.zip", {
    abortSignal: abortController.signal,
    onProgress: (progress) => {
      console.log(`Progress: ${progress.loadedBytes}`);
    },
  });
} catch (error) {
  if (error.name === "AbortError") {
    console.log("Upload was cancelled");
  } else {
    throw error;
  }
}

// Manual abort
document.getElementById("cancel")?.addEventListener("click", () => {
  abortController.abort();
});
```

---

## Copy Operations

### Copy from URL

```typescript
const sourceUrl = "https://source-account.blob.core.windows.net/container/blob";

// Start async copy
const copyPoller = await blobClient.beginCopyFromURL(sourceUrl);

// Wait for completion
const result = await copyPoller.pollUntilDone();
console.log(`Copy completed: ${result.copyStatus}`);

// Or copy synchronously (for small blobs)
await blobClient.syncCopyFromURL(sourceUrl);
```

### Copy with Progress

```typescript
const copyPoller = await blobClient.beginCopyFromURL(sourceUrl, {
  onProgress: (state) => {
    if (state.copyProgress) {
      const [copied, total] = state.copyProgress.split("/").map(Number);
      console.log(`Copied: ${copied}/${total} bytes`);
    }
  },
});
```

---

## Complete Example

```typescript
import {
  BlobServiceClient,
  ContainerClient,
  BlockBlobClient,
} from "@azure/storage-blob";
import { DefaultAzureCredential } from "@azure/identity";
import fs from "node:fs";
import { pipeline } from "node:stream/promises";

async function uploadAndDownload() {
  const credential = new DefaultAzureCredential();
  const blobServiceClient = new BlobServiceClient(
    `https://${process.env["STORAGE_ACCOUNT_NAME"]}.blob.core.windows.net`,
    credential
  );

  const containerClient = blobServiceClient.getContainerClient("demo");
  await containerClient.createIfNotExists();

  const blobClient = containerClient.getBlockBlobClient("test-file.txt");

  // Upload with progress
  console.log("Uploading...");
  const uploadData = Buffer.from("Hello, Azure Blob Storage!");
  await blobClient.upload(uploadData, uploadData.length, {
    onProgress: (progress) => {
      console.log(`Upload progress: ${progress.loadedBytes} bytes`);
    },
  });
  console.log("Upload complete!");

  // Download with progress
  console.log("Downloading...");
  const downloadResponse = await blobClient.download(0, undefined, {
    onProgress: (progress) => {
      console.log(`Download progress: ${progress.loadedBytes} bytes`);
    },
  });

  // Stream to file
  await pipeline(
    downloadResponse.readableStreamBody!,
    fs.createWriteStream("./downloaded-file.txt")
  );
  console.log("Download complete!");

  // Get blob properties
  const properties = await blobClient.getProperties();
  console.log(`Blob size: ${properties.contentLength} bytes`);
  console.log(`Content type: ${properties.contentType}`);
  console.log(`Last modified: ${properties.lastModified}`);

  // Cleanup
  await blobClient.delete();
  console.log("Blob deleted");
}

uploadAndDownload().catch(console.error);
```

---

## Best Practices

1. **Use parallel operations** - `uploadFile`/`downloadToFile` automatically parallelize
2. **Set appropriate block sizes** - 4-8MB for most scenarios, larger for huge files
3. **Implement progress tracking** - Use `onProgress` for user feedback
4. **Handle abort signals** - Allow users to cancel long operations
5. **Set content types** - Always set `blobContentType` for proper browser handling
6. **Use streams for large files** - Avoid loading entire files into memory
7. **Implement retry logic** - SDK has built-in retries, configure as needed

---

## See Also

- [SAS Token Patterns](./sas-tokens.md) - Generate secure access tokens
- [Official Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/storage/storage-blob/samples)
