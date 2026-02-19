# Azure Storage Blob Java SDK - Examples

Comprehensive code examples for the Azure Storage Blob SDK for Java.

## Table of Contents

- [Maven Dependency](#maven-dependency)
- [Client Creation](#client-creation)
- [Container Operations](#container-operations)
- [Upload Blobs](#upload-blobs)
- [Download Blobs](#download-blobs)
- [List Blobs](#list-blobs)
- [SAS Token Generation](#sas-token-generation)
- [Error Handling](#error-handling)

---

## Maven Dependency

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-storage-blob</artifactId>
    <version>12.33.0</version>
</dependency>
```

Or use the BOM:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-sdk-bom</artifactId>
            <version>{bom_version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-storage-blob</artifactId>
    </dependency>
</dependencies>
```

---

## Client Creation

### Using Shared Key Credential

```java
import com.azure.storage.blob.BlobServiceClient;
import com.azure.storage.blob.BlobServiceClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;

StorageSharedKeyCredential credential = new StorageSharedKeyCredential(accountName, accountKey);

String endpoint = String.format("https://%s.blob.core.windows.net", accountName);
BlobServiceClient blobServiceClient = new BlobServiceClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildClient();
```

### Using SAS Token

```java
// Separate endpoint and SAS token
BlobServiceClient blobServiceClient = new BlobServiceClientBuilder()
    .endpoint("<your-storage-account-url>")
    .sasToken("<your-sasToken>")
    .buildClient();

// Combined URL with SAS token
BlobServiceClient blobServiceClient = new BlobServiceClientBuilder()
    .endpoint("<your-storage-account-url>" + "?" + "<your-sasToken>")
    .buildClient();
```

### Using DefaultAzureCredential (Recommended)

```java
import com.azure.identity.DefaultAzureCredentialBuilder;

BlobServiceClient blobServiceClient = new BlobServiceClientBuilder()
    .endpoint("<your-storage-account-url>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

---

## Container Operations

### Create BlobContainerClient

```java
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobContainerClientBuilder;

// From BlobServiceClient
BlobContainerClient containerClient = blobServiceClient.getBlobContainerClient("mycontainer");

// From builder with SAS token
BlobContainerClient containerClient = new BlobContainerClientBuilder()
    .endpoint("<your-storage-account-url>")
    .sasToken("<your-sasToken>")
    .containerName("mycontainer")
    .buildClient();
```

### Create Container

```java
import java.util.Collections;
import java.util.Map;

// Simple create
containerClient.create();

// Create with metadata
Map<String, String> metadata = Collections.singletonMap("mykey", "myvalue");
containerClient.createWithResponse(metadata, null, null, Context.NONE);

// Create from service client
blobServiceClient.createBlobContainer("mycontainer");
```

### List and Delete Containers

```java
// List all containers
blobServiceClient.listBlobContainers().forEach(containerItem -> {
    System.out.println("Container name: " + containerItem.getName());
});

// Delete container
containerClient.delete();
```

---

## Upload Blobs

### Upload BinaryData

```java
import com.azure.core.util.BinaryData;
import com.azure.storage.blob.BlobClient;

BlobClient blobClient = containerClient.getBlobClient("myblob");
String dataSample = "samples";
blobClient.upload(BinaryData.fromString(dataSample));
```

### Upload from InputStream

```java
import com.azure.storage.blob.specialized.BlockBlobClient;
import java.io.ByteArrayInputStream;

BlockBlobClient blockBlobClient = containerClient.getBlobClient("myblockblob").getBlockBlobClient();
String dataSample = "samples";
try (ByteArrayInputStream dataStream = new ByteArrayInputStream(dataSample.getBytes())) {
    blockBlobClient.upload(dataStream, dataSample.length());
}
```

### Upload from File

```java
BlobClient blobClient = containerClient.getBlobClient("myblockblob");
blobClient.uploadFromFile("local-file.jpg");
```

### Upload with Overwrite Control

```java
// Upload without overwrite (fails if blob exists)
blobClient.upload(BinaryData.fromString("data"), false);

// Upload with overwrite enabled
blobClient.upload(BinaryData.fromString("data"), true);

// Upload with access conditions (fail if blob exists)
import com.azure.storage.blob.models.BlobRequestConditions;
import com.azure.storage.blob.options.BlobParallelUploadOptions;

BlobParallelUploadOptions options = new BlobParallelUploadOptions(dataStream, dataSample.length());
options.setRequestConditions(new BlobRequestConditions().setIfNoneMatch("*"));
blobClient.uploadWithResponse(options, null, Context.NONE);
```

### Upload with Metadata and Headers

```java
import com.azure.storage.blob.models.BlobHttpHeaders;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

Map<String, String> metadata = Collections.singletonMap("myblobmetadata", "sample");
BlobHttpHeaders headers = new BlobHttpHeaders()
    .setContentDisposition("attachment")
    .setContentType("text/html; charset=utf-8");

String data = "Hello world!";
byte[] md5 = MessageDigest.getInstance("MD5").digest(data.getBytes(StandardCharsets.UTF_8));

try (InputStream dataStream = new ByteArrayInputStream(data.getBytes(StandardCharsets.UTF_8))) {
    blockBlobClient.uploadWithResponse(
        dataStream, 
        data.length(), 
        headers, 
        metadata, 
        null,  // tier
        md5,   // content MD5
        null,  // request conditions
        null,  // timeout
        null   // context
    );
}
```

---

## Download Blobs

### Download to BinaryData

```java
BinaryData content = blobClient.downloadContent();
String text = content.toString();
```

### Download to OutputStream

```java
import java.io.ByteArrayOutputStream;

try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream()) {
    blobClient.downloadStream(outputStream);
    byte[] data = outputStream.toByteArray();
}
```

### Download to File

```java
blobClient.downloadToFile("downloaded-file.jpg");
```

### Download via InputStream

```java
import com.azure.storage.blob.specialized.BlobInputStream;

try (BlobInputStream blobIS = blobClient.openInputStream()) {
    int data = blobIS.read();
    // Process data...
}
```

---

## List Blobs

### Simple Listing

```java
import com.azure.storage.blob.models.BlobItem;

for (BlobItem blobItem : containerClient.listBlobs()) {
    System.out.println("Blob name: " + blobItem.getName());
}
```

### List and Create Clients

```java
for (BlobItem blobItem : containerClient.listBlobs()) {
    BlobClient blobClient;
    if (blobItem.getSnapshot() != null) {
        blobClient = containerClient.getBlobClient(blobItem.getName(), blobItem.getSnapshot());
    } else {
        blobClient = containerClient.getBlobClient(blobItem.getName());
    }
    System.out.println("Blob URI: " + blobClient.getBlobUrl());
}
```

---

## SAS Token Generation

```java
import com.azure.storage.blob.sas.*;
import com.azure.storage.common.sas.*;
import java.time.OffsetDateTime;

// Generate Account SAS
OffsetDateTime expiryTime = OffsetDateTime.now().plusDays(1);
AccountSasPermission accountSasPermission = new AccountSasPermission().setReadPermission(true);
AccountSasService services = new AccountSasService().setBlobAccess(true);
AccountSasResourceType resourceTypes = new AccountSasResourceType().setObject(true);

AccountSasSignatureValues accountSasValues = new AccountSasSignatureValues(
    expiryTime, accountSasPermission, services, resourceTypes);
String sasToken = blobServiceClient.generateAccountSas(accountSasValues);

// Generate Container SAS
BlobContainerSasPermission containerSasPermission = new BlobContainerSasPermission().setCreatePermission(true);
BlobServiceSasSignatureValues serviceSasValues = new BlobServiceSasSignatureValues(expiryTime, containerSasPermission);
String containerSas = containerClient.generateSas(serviceSasValues);

// Generate Blob SAS
BlobSasPermission blobSasPermission = new BlobSasPermission().setReadPermission(true);
BlobServiceSasSignatureValues blobSasValues = new BlobServiceSasSignatureValues(expiryTime, blobSasPermission);
String blobSas = blobClient.generateSas(blobSasValues);
```

---

## Error Handling

```java
import com.azure.storage.blob.models.BlobErrorCode;
import com.azure.storage.blob.models.BlobStorageException;

try {
    containerClient.create();
} catch (BlobStorageException e) {
    if (e.getErrorCode() == BlobErrorCode.CONTAINER_ALREADY_EXISTS) {
        System.out.println("Container already exists: " + containerClient.getBlobContainerUrl());
    } else if (e.getErrorCode() == BlobErrorCode.CONTAINER_BEING_DELETED) {
        System.out.println("Container is being deleted: " + e.getServiceMessage());
    } else if (e.getErrorCode() == BlobErrorCode.RESOURCE_NOT_FOUND) {
        System.out.println("Resource not found, status: " + e.getStatusCode());
    } else {
        throw e;
    }
}
```

---

## Complete Working Example

```java
import com.azure.storage.blob.*;
import com.azure.storage.blob.specialized.BlockBlobClient;
import com.azure.storage.common.StorageSharedKeyCredential;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

public class BasicExample {

    public static void main(String[] args) throws IOException {
        String accountName = System.getenv("AZURE_STORAGE_ACCOUNT_NAME");
        String accountKey = System.getenv("AZURE_STORAGE_ACCOUNT_KEY");

        StorageSharedKeyCredential credential = new StorageSharedKeyCredential(accountName, accountKey);
        String endpoint = String.format(Locale.ROOT, "https://%s.blob.core.windows.net", accountName);

        BlobServiceClient storageClient = new BlobServiceClientBuilder()
            .endpoint(endpoint)
            .credential(credential)
            .buildClient();

        // Create container (names must be lowercase)
        BlobContainerClient containerClient = storageClient
            .getBlobContainerClient("myjavacontainer" + System.currentTimeMillis());
        containerClient.create();

        // Create blob client
        BlockBlobClient blobClient = containerClient
            .getBlobClient("HelloWorld.txt")
            .getBlockBlobClient();

        // Upload data
        String data = "Hello world!";
        try (InputStream dataStream = new ByteArrayInputStream(data.getBytes(StandardCharsets.UTF_8))) {
            blobClient.upload(dataStream, data.length());
        }

        // Download data
        int dataSize = (int) blobClient.getProperties().getBlobSize();
        try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream(dataSize)) {
            blobClient.downloadStream(outputStream);
            String downloaded = new String(outputStream.toByteArray(), StandardCharsets.UTF_8);
            System.out.println("Downloaded: " + downloaded);
        }

        // List blobs
        containerClient.listBlobs().forEach(blobItem -> 
            System.out.println("Blob: " + blobItem.getName()));

        // Cleanup
        blobClient.delete();
        containerClient.delete();
    }
}
```
