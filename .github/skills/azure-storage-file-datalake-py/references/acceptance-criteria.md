# Azure Storage File Data Lake SDK Acceptance Criteria

**SDK**: `azure-storage-file-datalake`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Clients
```python
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    FileSystemClient,
    DataLakeDirectoryClient,
    DataLakeFileClient,
)
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Clients
```python
from azure.storage.filedatalake.aio import DataLakeServiceClient
from azure.identity.aio import DefaultAzureCredential
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing from Blob SDK
```python
# WRONG - Data Lake Gen2 uses filedatalake, not blob
from azure.storage.blob import BlobServiceClient
```

#### ❌ INCORRECT: Mixing sync and async imports
```python
# WRONG - async client with sync credential
from azure.storage.filedatalake.aio import DataLakeServiceClient
from azure.identity import DefaultAzureCredential
```

---

## 2. Authentication Patterns

### ✅ CORRECT: DefaultAzureCredential with DFS endpoint
```python
import os
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient

account_url = os.environ["AZURE_STORAGE_ACCOUNT_URL"]
credential = DefaultAzureCredential()

service_client = DataLakeServiceClient(
    account_url=account_url,
    credential=credential,
)
```

### ❌ INCORRECT: Hardcoded keys or connection strings
```python
# WRONG - avoid account keys/connection strings in skill guidance
service_client = DataLakeServiceClient(
    account_url="https://myaccount.dfs.core.windows.net",
    credential="<account-key>",
)

# WRONG - connection string auth is not recommended
service_client = DataLakeServiceClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
)
```

---

## 3. DataLakeServiceClient Patterns

### ✅ CORRECT: Create, list, and get file system client
```python
from azure.storage.filedatalake import DataLakeServiceClient

service_client = DataLakeServiceClient(
    account_url="https://<account>.dfs.core.windows.net",
    credential=credential,
)

file_system_client = service_client.create_file_system("myfilesystem")

for fs in service_client.list_file_systems():
    print(fs.name)

file_system_client = service_client.get_file_system_client("myfilesystem")
```

### ❌ INCORRECT: Using blob endpoint or wrong parameter
```python
# WRONG - blob endpoint is not for Data Lake Gen2 directory/file APIs
DataLakeServiceClient(
    account_url="https://<account>.blob.core.windows.net",
    credential=credential,
)

# WRONG - incorrect parameter name
DataLakeServiceClient(url="https://<account>.dfs.core.windows.net", credential=credential)
```

---

## 4. FileSystemClient Patterns

### ✅ CORRECT: Create directory, list paths, and get file client
```python
file_system_client = service_client.get_file_system_client("myfilesystem")

directory_client = file_system_client.create_directory("mydir")

for path in file_system_client.get_paths(path="mydir", recursive=True):
    print(path.name)

file_client = file_system_client.get_file_client("mydir/data.txt")
```

### ❌ INCORRECT: Using container/blob APIs
```python
# WRONG - Blob container clients are not Data Lake file systems
container_client = service_client.get_container_client("myfilesystem")
```

---

## 5. DirectoryClient Patterns

### ✅ CORRECT: Directory operations
```python
directory_client = file_system_client.get_directory_client("mydir")

subdir_client = directory_client.get_sub_directory_client("subdir")

directory_client.rename_directory(new_name="myfilesystem/mydir-renamed")

acl = directory_client.get_access_control()
print(acl["permissions"])
```

### ❌ INCORRECT: Missing file system in rename
```python
# WRONG - rename requires file system prefix in the new name
directory_client.rename_directory(new_name="mydir-renamed")
```

---

## 6. FileClient Patterns

### ✅ CORRECT: Upload, append, flush, download, delete
```python
file_client = file_system_client.get_file_client("mydir/data.txt")

file_client.upload_data(b"Hello", overwrite=True)

file_client.append_data(data=b"chunk1", offset=0, length=6)
file_client.append_data(data=b"chunk2", offset=6, length=6)
file_client.flush_data(12)

download = file_client.download_file()
contents = download.readall()

file_client.delete_file()
```

### ❌ INCORRECT: Blob APIs on DataLakeFileClient
```python
# WRONG - DataLakeFileClient does not use blob upload/download methods
file_client.upload_blob(b"data")
file_client.download_blob()
```

---

## 7. Hierarchical Operations

### ✅ CORRECT: Nested directories and recursive listing
```python
file_system_client.create_directory("path/to/nested/dir")

for path in file_system_client.get_paths(path="path", recursive=True):
    print(path.name)
```

### ❌ INCORRECT: Flat blob listing for hierarchical operations
```python
# WRONG - list_blobs is a blob API and ignores hierarchical directories
for blob in file_system_client.list_blobs():
    print(blob.name)
```
