# Azure Container Registry SDK Acceptance Criteria

**SDK**: `azure-containerregistry`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Package**: `azure-containerregistry`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Client
```python
from azure.containerregistry import ContainerRegistryClient
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Async Client
```python
from azure.containerregistry.aio import ContainerRegistryClient
from azure.identity.aio import DefaultAzureCredential
```

#### ✅ CORRECT: Anonymous Access (Public Registry)
```python
from azure.containerregistry import ContainerRegistryClient

client = ContainerRegistryClient(
    endpoint="https://mcr.microsoft.com",
    credential=None,
    audience="https://mcr.microsoft.com"
)
```

### 1.2 Model Imports

#### ✅ CORRECT: Repository Properties
```python
from azure.containerregistry import (
    RepositoryProperties,
    ArtifactManifestProperties,
)
```

#### ✅ CORRECT: Ordering Enums
```python
from azure.containerregistry import (
    ArtifactTagOrder,
    ArtifactManifestOrder,
)
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing from wrong module
```python
# WRONG - ContainerRegistryClient is in azure.containerregistry, not .models
from azure.containerregistry.models import ContainerRegistryClient

# WRONG - RepositoryProperties is in main module
from azure.containerregistry.models import RepositoryProperties
```

#### ❌ INCORRECT: Using old module names
```python
# WRONG - No such module
from azure.container_registry import ContainerRegistryClient

# WRONG - Typo in module name
from azure.container_registry_py import ContainerRegistryClient
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Sync Client with DefaultAzureCredential
```python
from azure.containerregistry import ContainerRegistryClient
from azure.identity import DefaultAzureCredential
import os

client = ContainerRegistryClient(
    endpoint=os.environ["AZURE_CONTAINERREGISTRY_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

### 2.2 ✅ CORRECT: Sync Client with Context Manager
```python
from azure.containerregistry import ContainerRegistryClient
from azure.identity import DefaultAzureCredential

with ContainerRegistryClient(
    endpoint=os.environ["AZURE_CONTAINERREGISTRY_ENDPOINT"],
    credential=DefaultAzureCredential()
) as client:
    for repo in client.list_repository_names():
        print(repo)
```

### 2.3 ✅ CORRECT: Async Client
```python
from azure.containerregistry.aio import ContainerRegistryClient
from azure.identity.aio import DefaultAzureCredential

async with ContainerRegistryClient(
    endpoint=os.environ["AZURE_CONTAINERREGISTRY_ENDPOINT"],
    credential=DefaultAzureCredential()
) as client:
    async for repo in client.list_repository_names():
        print(repo)
```

### 2.4 ✅ CORRECT: Anonymous Access
```python
from azure.containerregistry import ContainerRegistryClient

client = ContainerRegistryClient(
    endpoint="https://mcr.microsoft.com",
    credential=None,
    audience="https://mcr.microsoft.com"
)
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded endpoint
```python
# WRONG - endpoints should come from environment variables
client = ContainerRegistryClient(
    endpoint="https://myregistry.azurecr.io",
    credential=DefaultAzureCredential()
)
```

#### ❌ INCORRECT: Not using context manager
```python
# WRONG - no cleanup
client = ContainerRegistryClient(endpoint=endpoint, credential=credential)
for repo in client.list_repository_names():
     print(repo)
# Missing: client cleanup
```

Always use a context manager to ensure proper client cleanup. The client should be wrapped with `with` to automatically close resources.

#### ❌ INCORRECT: Mixing sync and async
```python
# WRONG - using sync client with async patterns
from azure.containerregistry import ContainerRegistryClient
async with ContainerRegistryClient(...) as client:  # Should be .aio version
    async for repo in client.list_repository_names():
        print(repo)
```

---

## 3. Repository Operations

### 3.1 ✅ CORRECT: List Repositories
```python
client = ContainerRegistryClient(endpoint=endpoint, credential=credential)

for repository in client.list_repository_names():
    print(repository)
```

### 3.2 ✅ CORRECT: Get Repository Properties
```python
properties = client.get_repository_properties("my-image")
print(f"Created: {properties.created_on}")
print(f"Modified: {properties.last_updated_on}")
print(f"Manifests: {properties.manifest_count}")
print(f"Tags: {properties.tag_count}")
```

### 3.3 ✅ CORRECT: Update Repository Properties
```python
from azure.containerregistry import RepositoryProperties

client.update_repository_properties(
    "my-image",
    properties=RepositoryProperties(
        can_delete=False,
        can_write=False
    )
)
```

### 3.4 ✅ CORRECT: Delete Repository
```python
client.delete_repository("my-image")
```

### 3.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong property attribute names
```python
# WRONG - should be can_delete, can_write
properties = RepositoryProperties(
     delete_enabled=False,
     write_enabled=False
)
```

Use the correct property names `can_delete` and `can_write` instead of `delete_enabled` and `write_enabled` when creating RepositoryProperties.

---

## 4. Tag Operations

### 4.1 ✅ CORRECT: List Tags
```python
for tag in client.list_tag_properties("my-image"):
    print(f"{tag.name}: {tag.created_on}")
```

### 4.2 ✅ CORRECT: List Tags with Ordering
```python
from azure.containerregistry import ArtifactTagOrder

for tag in client.list_tag_properties(
    "my-image",
    order_by=ArtifactTagOrder.LAST_UPDATED_ON_DESCENDING
):
    print(f"{tag.name}: {tag.last_updated_on}")
```

### 4.3 ✅ CORRECT: Get Tag Properties
```python
tag = client.get_tag_properties("my-image", "latest")
print(f"Digest: {tag.digest}")
print(f"Created: {tag.created_on}")
```

### 4.4 ✅ CORRECT: Delete Tag
```python
client.delete_tag("my-image", "old-tag")
```

---

## 5. Manifest Operations

### 5.1 ✅ CORRECT: List Manifests
```python
from azure.containerregistry import ArtifactManifestOrder

for manifest in client.list_manifest_properties(
    "my-image",
    order_by=ArtifactManifestOrder.LAST_UPDATED_ON_DESCENDING
):
    print(f"Digest: {manifest.digest}")
    print(f"Tags: {manifest.tags}")
    print(f"Size: {manifest.size_in_bytes}")
```

### 5.2 ✅ CORRECT: Get Manifest Properties
```python
manifest = client.get_manifest_properties("my-image", "latest")
print(f"Digest: {manifest.digest}")
print(f"Architecture: {manifest.architecture}")
print(f"OS: {manifest.operating_system}")
```

### 5.3 ✅ CORRECT: Update Manifest Properties
```python
from azure.containerregistry import ArtifactManifestProperties

client.update_manifest_properties(
    "my-image",
    "latest",
    properties=ArtifactManifestProperties(
        can_delete=False,
        can_write=False
    )
)
```

### 5.4 ✅ CORRECT: Delete Manifest by Digest
```python
client.delete_manifest("my-image", "sha256:abc123...")
```

### 5.5 ✅ CORRECT: Delete Manifest by Tag
```python
manifest = client.get_manifest_properties("my-image", "old-tag")
client.delete_manifest("my-image", manifest.digest)
```

### 5.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Deleting by tag directly
```python
# WRONG - should get digest first
client.delete_manifest("my-image", "old-tag")
```

The `delete_manifest()` method requires a digest, not a tag. You must first get the manifest properties to extract the digest using `get_manifest_properties()`, then pass the digest to `delete_manifest()`.

#### ❌ INCORRECT: Deleting tagged manifests without checking
```python
# WRONG - may delete tagged images unintentionally
for manifest in client.list_manifest_properties("my-image"):
     if manifest.last_updated_on < cutoff:
         client.delete_manifest("my-image", manifest.digest)  # Lost tags!
```

Always check `manifest.tags` to ensure the manifest is untagged before deleting. Tagged manifests should not be deleted unless you explicitly want to remove those tags.

---

## 6. Upload and Download Artifacts

### 6.1 ✅ CORRECT: Download Manifest
```python
manifest = client.download_manifest("my-image", "latest")
print(f"Media type: {manifest.media_type}")
print(f"Digest: {manifest.digest}")
```

### 6.2 ✅ CORRECT: Download Blob
```python
blob = client.download_blob("my-image", "sha256:abc123...")
with open("layer.tar.gz", "wb") as f:
    for chunk in blob:
        f.write(chunk)
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not handling streaming blob
```python
# WRONG - blob is a stream, not bytes directly
blob = client.download_blob("my-image", "sha256:abc123...")
with open("layer.tar.gz", "wb") as f:
     f.write(blob)  # Should iterate chunks
```

Blobs are returned as streams and must be iterated over in chunks. Use a `for` loop to read each chunk and write it to the file.

---

## 7. Async Patterns

### 7.1 ✅ CORRECT: Async Repository Listing
```python
from azure.containerregistry.aio import ContainerRegistryClient
from azure.identity.aio import DefaultAzureCredential

async def list_repos():
    credential = DefaultAzureCredential()
    async with ContainerRegistryClient(endpoint=endpoint, credential=credential) as client:
        async for repo in client.list_repository_names():
            print(repo)
        await credential.close()
```

### 7.2 ✅ CORRECT: Async Tag Listing
```python
async with ContainerRegistryClient(endpoint=endpoint, credential=credential) as client:
    async for tag in client.list_tag_properties("my-image"):
        print(f"{tag.name}: {tag.created_on}")
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing await for async operations
```python
# WRONG - missing async iteration
async def bad_example():
     async with ContainerRegistryClient(...) as client:
         repos = client.list_repository_names()  # No async iteration
         for repo in repos:  # Should use async for
             print(repo)
```

When using async client methods, you must use `async for` to iterate over results. Standard `for` loops will not work with async iterables.

#### ❌ INCORRECT: Using sync client with async patterns
```python
# WRONG - using sync client class with async context manager
from azure.containerregistry import ContainerRegistryClient  # Should be .aio

async with ContainerRegistryClient(endpoint=endpoint, credential=credential) as client:
    async for repo in client.list_repository_names():
        print(repo)
```

---

## 8. Common Cleanup Patterns

### 8.1 ✅ CORRECT: Clean Old Images
```python
from datetime import datetime, timedelta, timezone

cutoff = datetime.now(timezone.utc) - timedelta(days=30)

for manifest in client.list_manifest_properties("my-image"):
    if manifest.last_updated_on < cutoff and not manifest.tags:
        print(f"Deleting {manifest.digest}")
        client.delete_manifest("my-image", manifest.digest)
```

### 8.2 ✅ CORRECT: Lock Production Images
```python
from azure.containerregistry import ArtifactManifestProperties

# Prevent deletion of production images
client.update_manifest_properties(
    "my-image",
    "latest",
    properties=ArtifactManifestProperties(
        can_delete=False,
        can_write=False
    )
)
```

---

## 9. Environment Variables

### Required Variables
```bash
AZURE_CONTAINERREGISTRY_ENDPOINT=https://<registry-name>.azurecr.io
```

### Optional Variables
```bash
AZURE_CONTAINERREGISTRY_USERNAME=<username>
AZURE_CONTAINERREGISTRY_PASSWORD=<password>
```

---

## 10. Error Handling

### ✅ CORRECT: Proper Error Handling
```python
from azure.core.exceptions import ResourceNotFoundError

try:
    repo = client.get_repository_properties("nonexistent")
except ResourceNotFoundError:
    print("Repository not found")
```

### ❌ INCORRECT: Empty Exception Handlers
```python
# WRONG - suppresses all errors silently
try:
     client.delete_repository("my-image")
except:
     pass  # No error context
```

Always handle exceptions explicitly by catching specific exception types and either logging the error or re-raising it. Never use bare `except:` or empty exception handlers that silently suppress errors.

---

## 11. Client Operations Reference

| Operation | Description | Returns |
|-----------|-------------|---------|
| `list_repository_names()` | List all repositories | Iterator of strings |
| `get_repository_properties(name)` | Get repository metadata | RepositoryProperties |
| `update_repository_properties(name, properties)` | Update repository settings | RepositoryProperties |
| `delete_repository(name)` | Delete repository and all images | None |
| `list_tag_properties(repo)` | List tags in repository | Iterator of TagProperties |
| `get_tag_properties(repo, tag)` | Get tag metadata | TagProperties |
| `delete_tag(repo, tag)` | Delete specific tag | None |
| `list_manifest_properties(repo)` | List manifests in repository | Iterator of ManifestProperties |
| `get_manifest_properties(repo, tag)` | Get manifest metadata | ManifestProperties |
| `update_manifest_properties(repo, tag, properties)` | Update manifest settings | ManifestProperties |
| `delete_manifest(repo, digest)` | Delete manifest by digest | None |
| `download_manifest(repo, tag)` | Download manifest content | DownloadedManifest |
| `download_blob(repo, digest)` | Download layer blob | Iterator of bytes |

---

## 12. Test Scenarios Checklist

### Basic Operations
- [ ] Client creation with context manager
- [ ] List repositories
- [ ] Get repository properties
- [ ] Delete repository

### Tag Operations
- [ ] List tags with default order
- [ ] List tags with custom ordering (ascending/descending)
- [ ] Get tag properties
- [ ] Delete tag

### Manifest Operations
- [ ] List manifests with ordering
- [ ] Get manifest properties
- [ ] Update manifest properties (lock production)
- [ ] Delete manifest by digest
- [ ] Delete manifest safely (check tags first)

### Upload/Download
- [ ] Download manifest
- [ ] Download blob with chunk streaming

### Async
- [ ] Async list repositories
- [ ] Async list tags
- [ ] Async client with context manager

### Error Handling
- [ ] Proper exception handling
- [ ] Resource not found errors

### Cleanup
- [ ] Clean old untagged manifests
- [ ] Lock production images

---

## 13. Quick Reference: Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'azure.containerregistry'` | SDK not installed | `pip install azure-containerregistry` |
| `AuthenticationError` | Invalid credentials | Use `DefaultAzureCredential()` and set environment variables |
| `ResourceNotFoundError` | Repository/tag/manifest not found | Check repository/tag name before accessing |
| `OperationError: Cannot delete tagged manifest` | Deleting manifest with tags | Check `manifest.tags` before deleting |
| `PermissionError: Cannot write to read-only repository` | Repository locked with `can_write=False` | Use account with proper permissions |
| `TypeError: 'str' object is not iterable` | Not iterating over blob chunks | Use `for chunk in blob:` when downloading blobs |
| `AttributeError: 'ContainerRegistryClient' has no attribute 'X'` | Wrong method name | Check method names in API reference |

---

## 14. Best Practices

1. **Use DefaultAzureCredential** for authentication in production
2. **Use context managers** for proper client cleanup
3. **Delete by digest** not tag to avoid orphaned images
4. **Lock production images** with `can_delete=False` and `can_write=False`
5. **Clean up untagged manifests** regularly
6. **Check manifest.tags** before deleting to avoid losing tagged images
7. **Use async client** for high-throughput operations
8. **Order results by last_updated** to find recent/old images easily
9. **Handle ResourceNotFoundError** when accessing resources
10. **Use ArtifactTagOrder and ArtifactManifestOrder** for consistent sorting
