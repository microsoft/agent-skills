# Azure Storage Blob Java SDK Acceptance Criteria

**SDK**: `com.azure:azure-storage-blob`
**Repository**: https://github.com/Azure/azure-sdk-for-java
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Client Builder Patterns

### ✅ CORRECT: BlobServiceClient with DefaultAzureCredential

```java
import com.azure.storage.blob.BlobServiceClient;
import com.azure.storage.blob.BlobServiceClientBuilder;
import com.azure.identity.DefaultAzureCredentialBuilder;

BlobServiceClient serviceClient = new BlobServiceClientBuilder()
    .endpoint(System.getenv("AZURE_STORAGE_ACCOUNT_URL"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

### ✅ CORRECT: BlobContainerClient Direct Construction

```java
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobContainerClientBuilder;

BlobContainerClient containerClient = new BlobContainerClientBuilder()
    .endpoint(System.getenv("AZURE_STORAGE_ACCOUNT_URL"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .containerName("mycontainer")
    .buildClient();
```

### ✅ CORRECT: BlobClient for Specific Blob

```java
import com.azure.storage.blob.BlobClient;
import com.azure.storage.blob.BlobClientBuilder;

BlobClient blobClient = new BlobClientBuilder()
    .endpoint(System.getenv("AZURE_STORAGE_ACCOUNT_URL"))
    .credential(new DefaultAzureCredentialBuilder().build())
    .containerName("mycontainer")
    .blobName("folder/myfile.txt")
    .buildClient();
```

### ❌ INCORRECT: Hardcoded Connection String

```java
// WRONG - hardcoded connection string
BlobServiceClient client = new BlobServiceClientBuilder()
    .connectionString("DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=...")
    .buildClient();
```

### ❌ INCORRECT: Missing Container/Blob Name

```java
// WRONG - incomplete client configuration
BlobClient blobClient = new BlobClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildClient();  // Missing containerName and blobName
```

---

## 2. Container Operations

### ✅ CORRECT: Create Container If Not Exists

```java
// Create container if not exists
BlobContainerClient container = serviceClient.createBlobContainerIfNotExists("mycontainer");

// Or from existing container client
containerClient.createIfNotExists();
```

### ✅ CORRECT: List Containers

```java
serviceClient.listBlobContainers().forEach(container -> {
    System.out.printf("Container: %s, Last Modified: %s%n",
        container.getName(),
        container.getProperties().getLastModified());
});
```

### ❌ INCORRECT: Not Handling Already Exists

```java
// WRONG - throws exception if container exists
serviceClient.createBlobContainer("mycontainer");
// Use createBlobContainerIfNotExists instead
```

---

## 3. Upload Operations

### ✅ CORRECT: Upload with BinaryData

```java
import com.azure.core.util.BinaryData;

String content = "Hello, Azure Blob Storage!";
blobClient.upload(BinaryData.fromString(content), true);  // true = overwrite
```

### ✅ CORRECT: Upload from File

```java
blobClient.uploadFromFile("path/to/local/file.txt", true);  // true = overwrite
```

### ✅ CORRECT: Upload from InputStream

```java
import com.azure.storage.blob.specialized.BlockBlobClient;

BlockBlobClient blockBlobClient = blobClient.getBlockBlobClient();

try (InputStream inputStream = new FileInputStream("largefile.bin")) {
    long fileSize = new File("largefile.bin").length();
    blockBlobClient.upload(inputStream, fileSize, true);
}
```

### ✅ CORRECT: Upload with Options (Headers, Metadata)

```java
import com.azure.storage.blob.models.BlobHttpHeaders;
import com.azure.storage.blob.options.BlobParallelUploadOptions;
import com.azure.core.util.Context;
import java.util.Map;

BlobHttpHeaders headers = new BlobHttpHeaders()
    .setContentType("application/json")
    .setCacheControl("max-age=3600");

Map<String, String> metadata = Map.of(
    "author", "john",
    "version", "1.0"
);

try (InputStream stream = new FileInputStream("data.json")) {
    BlobParallelUploadOptions options = new BlobParallelUploadOptions(stream)
        .setHeaders(headers)
        .setMetadata(metadata);

    blobClient.uploadWithResponse(options, null, Context.NONE);
}
```

### ✅ CORRECT: Upload Only If Not Exists

```java
import com.azure.storage.blob.models.BlobRequestConditions;

BlobParallelUploadOptions options = new BlobParallelUploadOptions(inputStream, length)
    .setRequestConditions(new BlobRequestConditions().setIfNoneMatch("*"));

try {
    blobClient.uploadWithResponse(options, null, Context.NONE);
} catch (BlobStorageException e) {
    if (e.getStatusCode() == 409) {
        System.out.println("Blob already exists");
    }
}
```

### ❌ INCORRECT: Missing Overwrite Flag

```java
// WRONG - fails silently or throws if blob exists
blobClient.upload(BinaryData.fromString(content));  // Missing overwrite flag
```

---

## 4. Download Operations

### ✅ CORRECT: Download to BinaryData

```java
BinaryData content = blobClient.downloadContent();
String text = content.toString();
System.out.println("Content: " + text);
```

### ✅ CORRECT: Download to File

```java
blobClient.downloadToFile("path/to/downloaded/file.txt");
```

### ✅ CORRECT: Download to OutputStream

```java
try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream()) {
    blobClient.downloadStream(outputStream);
    byte[] data = outputStream.toByteArray();
    System.out.println("Downloaded " + data.length + " bytes");
}
```

### ✅ CORRECT: Download with BlobInputStream

```java
import com.azure.storage.blob.specialized.BlobInputStream;

try (BlobInputStream blobIS = blobClient.openInputStream()) {
    byte[] buffer = new byte[4096];
    int bytesRead;
    while ((bytesRead = blobIS.read(buffer)) != -1) {
        // Process buffer
        processChunk(buffer, bytesRead);
    }
}
```

### ❌ INCORRECT: Not Handling Missing Blob

```java
// WRONG - no error handling for missing blob
String content = blobClient.downloadContent().toString();
// Should catch BlobStorageException with status 404
```

---

## 5. List Blobs

### ✅ CORRECT: List All Blobs

```java
import com.azure.storage.blob.models.BlobItem;

for (BlobItem blobItem : containerClient.listBlobs()) {
    System.out.printf("Blob: %s, Size: %d%n",
        blobItem.getName(),
        blobItem.getProperties().getContentLength());
}
```

### ✅ CORRECT: List with Prefix (Virtual Directory)

```java
import com.azure.storage.blob.models.ListBlobsOptions;

ListBlobsOptions options = new ListBlobsOptions()
    .setPrefix("folder/subfolder/");

for (BlobItem blobItem : containerClient.listBlobs(options, null)) {
    System.out.println("Blob: " + blobItem.getName());
}
```

### ✅ CORRECT: List by Hierarchy (Directories)

```java
import com.azure.storage.blob.models.BlobListDetails;

String delimiter = "/";
ListBlobsOptions options = new ListBlobsOptions()
    .setPrefix("data/")
    .setDetails(new BlobListDetails().setRetrieveMetadata(true));

for (BlobItem item : containerClient.listBlobsByHierarchy(delimiter, options, null)) {
    if (item.isPrefix() != null && item.isPrefix()) {
        System.out.println("Directory: " + item.getName());
    } else {
        System.out.println("Blob: " + item.getName());
    }
}
```

---

## 6. Delete Operations

### ✅ CORRECT: Delete If Exists

```java
boolean deleted = blobClient.deleteIfExists();
System.out.println("Blob deleted: " + deleted);
```

### ✅ CORRECT: Delete with Snapshots

```java
import com.azure.storage.blob.models.DeleteSnapshotsOptionType;
import com.azure.core.util.Context;

blobClient.deleteWithResponse(
    DeleteSnapshotsOptionType.INCLUDE,  // Delete blob and snapshots
    null,                                // No conditions
    null,                                // No timeout
    Context.NONE
);
```

### ❌ INCORRECT: Not Handling Missing Blob

```java
// WRONG - throws exception if blob doesn't exist
blobClient.delete();
// Use deleteIfExists() instead
```

---

## 7. SAS Token Generation

### ✅ CORRECT: Generate Blob-Level SAS

```java
import com.azure.storage.blob.sas.*;
import java.time.OffsetDateTime;

BlobSasPermission permissions = new BlobSasPermission()
    .setReadPermission(true)
    .setWritePermission(false);

OffsetDateTime expiry = OffsetDateTime.now().plusDays(1);

BlobServiceSasSignatureValues sasValues = new BlobServiceSasSignatureValues(expiry, permissions);
String sasToken = blobClient.generateSas(sasValues);

System.out.println("SAS URL: " + blobClient.getBlobUrl() + "?" + sasToken);
```

### ✅ CORRECT: Generate Container-Level SAS

```java
import com.azure.storage.blob.sas.BlobContainerSasPermission;

BlobContainerSasPermission containerPermissions = new BlobContainerSasPermission()
    .setReadPermission(true)
    .setListPermission(true)
    .setWritePermission(false);

BlobServiceSasSignatureValues sasValues = new BlobServiceSasSignatureValues(
    OffsetDateTime.now().plusHours(4),
    containerPermissions
);

String sasToken = containerClient.generateSas(sasValues);
```

### ❌ INCORRECT: Overly Permissive SAS

```java
// WRONG - too many permissions, long expiry
BlobSasPermission permissions = new BlobSasPermission()
    .setReadPermission(true)
    .setWritePermission(true)
    .setDeletePermission(true)
    .setCreatePermission(true);

OffsetDateTime expiry = OffsetDateTime.now().plusYears(1);  // Too long!
```

---

## 8. Blob Properties and Metadata

### ✅ CORRECT: Get and Set Properties

```java
import com.azure.storage.blob.models.BlobProperties;

// Get properties
BlobProperties properties = blobClient.getProperties();
System.out.printf("Size: %d bytes, Content-Type: %s, Last Modified: %s%n",
    properties.getBlobSize(),
    properties.getContentType(),
    properties.getLastModified());

// Set metadata
Map<String, String> metadata = Map.of(
    "processed", "true",
    "version", "2.0"
);
blobClient.setMetadata(metadata);

// Set HTTP headers
BlobHttpHeaders headers = new BlobHttpHeaders()
    .setContentType("application/octet-stream")
    .setCacheControl("max-age=86400");
blobClient.setHttpHeaders(headers);
```

---

## 9. Blob Leasing

### ✅ CORRECT: Acquire and Release Lease

```java
import com.azure.storage.blob.specialized.BlobLeaseClient;
import com.azure.storage.blob.specialized.BlobLeaseClientBuilder;

BlobLeaseClient leaseClient = new BlobLeaseClientBuilder()
    .blobClient(blobClient)
    .buildClient();

// Acquire lease (60 seconds, or -1 for infinite)
String leaseId = leaseClient.acquireLease(60);
System.out.println("Lease acquired: " + leaseId);

try {
    // Perform operations with lease
    blobClient.upload(BinaryData.fromString("Updated content"), true);
} finally {
    // Release lease
    leaseClient.releaseLease();
}
```

---

## 10. Copy Operations

### ✅ CORRECT: Copy from URL

```java
import com.azure.storage.blob.models.BlobCopyInfo;
import com.azure.core.util.polling.SyncPoller;

// Async copy (for large blobs or cross-account)
SyncPoller<BlobCopyInfo, Void> poller = blobClient.beginCopy(
    sourceBlobUrl,
    Duration.ofSeconds(1)
);
poller.waitForCompletion();

// Sync copy from URL (same account, small blobs)
blobClient.copyFromUrl(sourceBlobUrl);
```

---

## 11. Error Handling

### ✅ CORRECT: Handle BlobStorageException

```java
import com.azure.storage.blob.models.BlobStorageException;

try {
    blobClient.downloadContent();
} catch (BlobStorageException e) {
    int statusCode = e.getStatusCode();
    String errorCode = e.getErrorCode().toString();

    switch (statusCode) {
        case 404:
            System.err.println("Blob not found: " + blobClient.getBlobName());
            break;
        case 409:
            System.err.println("Conflict: " + errorCode);
            break;
        case 403:
            System.err.println("Access denied: " + errorCode);
            break;
        default:
            System.err.printf("Error %d: %s%n", statusCode, e.getMessage());
    }
}
```

### ❌ INCORRECT: Generic Exception Handling

```java
// WRONG - loses error details
try {
    blobClient.upload(data);
} catch (Exception e) {
    System.out.println("Error: " + e.getMessage());
}
```

---

## 12. Upload via OutputStream

### ✅ CORRECT: BlobOutputStream for Streaming

```java
import com.azure.storage.blob.specialized.BlobOutputStream;

try (BlobOutputStream blobOS = blobClient.getBlockBlobClient().getBlobOutputStream(true)) {
    blobOS.write("Streaming data...".getBytes());
    blobOS.write("More data...".getBytes());
}
```
