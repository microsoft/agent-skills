# Azure Storage Blob SDK Acceptance Criteria

**SDK**: `azure-storage-blob`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `e7b5fa81aa188011fb4323382d1a32b32f54d55b`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Clients
```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
```

#### ✅ CORRECT: Async Clients
```python
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient, ContainerClient, BlobClient
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing credential from wrong module
```python
# WRONG - DefaultAzureCredential is in azure.identity
from azure.storage.blob import DefaultAzureCredential
```

#### ❌ INCORRECT: Mixing sync/async imports
```python
# WRONG - async client with sync credential
from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: DefaultAzureCredential with account URL
```python
import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

account_url = os.environ["AZURE_STORAGE_ACCOUNT_URL"]
credential = DefaultAzureCredential()

blob_service_client = BlobServiceClient(account_url, credential=credential)
```

### 2.2 ❌ INCORRECT: Hardcoded secrets or connection strings in code
```python
# WRONG - hardcoded connection string
blob_service_client = BlobServiceClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=..."
)
```

---

## 3. BlobServiceClient Patterns

### 3.1 ✅ CORRECT: Create container and get clients
```python
container_client = blob_service_client.get_container_client("sample-container")
container_client.create_container()

blob_client = blob_service_client.get_blob_client(
    container="sample-container",
    blob="sample.txt",
)
```

### 3.2 ❌ INCORRECT: Calling container operations on BlobServiceClient
```python
# WRONG - list_blobs is not a BlobServiceClient method
for blob in blob_service_client.list_blobs():
    print(blob.name)
```

---

## 4. ContainerClient Patterns

### 4.1 ✅ CORRECT: Upload via ContainerClient
```python
container_client = blob_service_client.get_container_client("sample-container")

with open("./local-file.txt", "rb") as data:
    container_client.upload_blob(name="sample.txt", data=data, overwrite=True)
```

### 4.2 ✅ CORRECT: List blobs
```python
for blob in container_client.list_blobs(name_starts_with="logs/"):
    print(blob.name)
```

### 4.3 ❌ INCORRECT: Using BlobClient-only APIs on ContainerClient
```python
# WRONG - download_blob is on BlobClient, not ContainerClient
container_client.download_blob("sample.txt")
```

---

## 5. BlobClient Patterns

### 5.1 ✅ CORRECT: Upload and download with BlobClient
```python
blob_client = blob_service_client.get_blob_client(
    container="sample-container",
    blob="sample.txt",
)

blob_client.upload_blob(b"hello", overwrite=True)

download_stream = blob_client.download_blob()
content = download_stream.readall()
```

### 5.2 ✅ CORRECT: Read into a stream
```python
import io

stream = io.BytesIO()
num_bytes = blob_client.download_blob().readinto(stream)
```

### 5.3 ❌ INCORRECT: Calling upload on wrong object
```python
# WRONG - upload_blob does not exist on BlobServiceClient
blob_service_client.upload_blob(data=b"hello")
```

---

## 6. Upload/Download Patterns

### 6.1 ✅ CORRECT: Upload from file with overwrite
```python
with open("./local-file.txt", "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
```

### 6.2 ✅ CORRECT: Download to local file
```python
with open("./downloaded.txt", "wb") as file:
    download_stream = blob_client.download_blob()
    file.write(download_stream.readall())
```

### 6.3 ❌ INCORRECT: Using async methods without await
```python
# WRONG - download_blob returns awaitable in async clients
download_stream = blob_client.download_blob()
data = download_stream.readall()
```

---

## 7. List Blobs Patterns

### 7.1 ✅ CORRECT: List blobs with prefix
```python
for blob in container_client.list_blobs(name_starts_with="logs/"):
    print(blob.name)
```

### 7.2 ✅ CORRECT: Walk blobs with delimiter
```python
for item in container_client.walk_blobs(delimiter="/"):
    if item.get("prefix"):
        print(f"Directory: {item['prefix']}")
    else:
        print(f"Blob: {item.name}")
```

### 7.3 ❌ INCORRECT: Listing blobs from BlobServiceClient
```python
# WRONG - list_blobs is a ContainerClient method
blob_service_client.list_blobs()
```

---

## 8. Async Variants

### 8.1 ✅ CORRECT: Async client and operations
```python
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

async def main():
    account_url = os.environ["AZURE_STORAGE_ACCOUNT_URL"]
    credential = DefaultAzureCredential()

    async with BlobServiceClient(account_url, credential=credential) as client:
        blob_client = client.get_blob_client("sample-container", "sample.txt")
        await blob_client.upload_blob(b"hello", overwrite=True)

        stream = await blob_client.download_blob()
        data = await stream.readall()
        print(data)

if __name__ == "__main__":
    asyncio.run(main())
```

### 8.2 ✅ CORRECT: Async list blobs
```python
async for blob in container_client.list_blobs():
    print(blob.name)
```

### 8.3 ❌ INCORRECT: Missing async context manager
```python
# WRONG - async client should use async with
client = BlobServiceClient(account_url, credential=credential)
blob_client = client.get_blob_client("sample-container", "sample.txt")
await blob_client.upload_blob(b"hello")
```
