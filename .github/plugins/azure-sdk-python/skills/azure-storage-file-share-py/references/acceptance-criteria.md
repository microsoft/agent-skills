# Azure Storage File Share SDK Acceptance Criteria

**SDK**: `azure-storage-file-share`
**Repository**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
**Commit**: `azure-storage-file-share_12.24.0`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Clients
```python
from azure.storage.fileshare import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient,
)
```

#### ✅ CORRECT: Async Clients
```python
from azure.storage.fileshare.aio import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient,
)
```

### 1.2 Credential Imports

#### ✅ CORRECT: DefaultAzureCredential
```python
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async DefaultAzureCredential
```python
from azure.identity.aio import DefaultAzureCredential
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module paths
```python
# WRONG - old package path
from azure.storage.file.share import ShareServiceClient

# WRONG - not in storage.fileshare
from azure.storage.file import ShareClient

# WRONG - blob client, not file shares
from azure.storage.blob import BlobServiceClient
```

---

## 2. Authentication Patterns

### 2.1 ✅ CORRECT: Connection String
```python
service = ShareServiceClient.from_connection_string(
    os.environ["AZURE_STORAGE_CONNECTION_STRING"]
)
```

### 2.2 ✅ CORRECT: Microsoft Entra ID
```python
service = ShareServiceClient(
    account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
    credential=DefaultAzureCredential(),
)
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded keys/URLs
```python
# WRONG - hardcoded account key
service = ShareServiceClient(
    account_url="https://myaccount.file.core.windows.net",
    credential="account-key",
)

# WRONG - hardcoded connection string
service = ShareServiceClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=..."
)
```

---

## 3. ShareServiceClient Patterns

### 3.1 ✅ CORRECT: Create/List/Delete Shares
```python
service = ShareServiceClient.from_connection_string(
    os.environ["AZURE_STORAGE_CONNECTION_STRING"]
)

service.create_share("my-share")
for share in service.list_shares():
    print(share.name)
service.delete_share("my-share")
```

### 3.2 ✅ CORRECT: Get Share Client
```python
share_client = service.get_share_client("my-share")
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using wrong client for service operations
```python
# WRONG - ShareClient cannot list all shares
share_client = ShareClient.from_connection_string(
    os.environ["AZURE_STORAGE_CONNECTION_STRING"],
    share_name="my-share",
)
shares = share_client.list_shares()  # Not supported on ShareClient
```

---

## 4. ShareClient Patterns

### 4.1 ✅ CORRECT: ShareClient Creation
```python
share_client = ShareClient.from_connection_string(
    conn_str=os.environ["AZURE_STORAGE_CONNECTION_STRING"],
    share_name="my-share",
)
```

### 4.2 ✅ CORRECT: Directory Operations
```python
share_client.create_directory("my-directory")
directory_client = share_client.get_directory_client("my-directory")
```

### 4.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter name
```python
# WRONG - parameter is share_name, not name
share_client = ShareClient.from_connection_string(
    conn_str=os.environ["AZURE_STORAGE_CONNECTION_STRING"],
    name="my-share",
)
```

---

## 5. ShareDirectoryClient Patterns

### 5.1 ✅ CORRECT: List Directories and Files
```python
directory_client = share_client.get_directory_client("my-directory")

for item in directory_client.list_directories_and_files():
    if item["is_directory"]:
        print(f"[DIR] {item['name']}")
    else:
        print(f"[FILE] {item['name']}")
```

### 5.2 ✅ CORRECT: Delete Directory
```python
share_client.delete_directory("my-directory")
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong listing method
```python
# WRONG - list_files is not on ShareDirectoryClient
directory_client.list_files()
```

---

## 6. ShareFileClient Patterns

### 6.1 ✅ CORRECT: Upload/Download File
```python
file_client = share_client.get_file_client("my-directory/file.txt")
file_client.upload_file("Hello, World!")

data = file_client.download_file().readall()
print(data)
```

### 6.2 ✅ CORRECT: Range Operations
```python
file_client.upload_range(data=b"content", offset=0, length=7)
chunk = file_client.download_file(offset=0, length=7).readall()
```

### 6.3 ✅ CORRECT: Delete File
```python
file_client.delete_file()
```

### 6.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Blob client methods
```python
# WRONG - upload_blob is for blob storage, not file shares
file_client.upload_blob(b"content")
```

---

## 7. SMB Operations (Mounted File Share)

### 7.1 ✅ CORRECT: Use Standard File I/O After SMB Mount
```python
import os

mounted_share_path = "/mnt/azure-share"
with open(os.path.join(mounted_share_path, "notes.txt"), "w") as handle:
    handle.write("hello")

with open(os.path.join(mounted_share_path, "notes.txt"), "r") as handle:
    print(handle.read())

print(os.listdir(mounted_share_path))
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Confusing SMB with SDK client usage
```python
# WRONG - SMB access does not use ShareServiceClient
service = ShareServiceClient.from_connection_string(conn_str)
with open("/mnt/azure-share/notes.txt", "r") as handle:
    print(handle.read())
```
