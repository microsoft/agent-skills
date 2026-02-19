# Azure Blob Storage SDK for Rust Acceptance Criteria

**Crate**: `azure_storage_blob`
**Repository**: https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/storage/azure_storage_blob
**Purpose**: Skill testing acceptance criteria for validating generated Rust code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Client Imports
```rust
use azure_storage_blob::{BlobClient, BlobClientOptions};
use azure_storage_blob::BlobContainerClient;
use azure_storage_blob::BlobServiceClient;
use azure_core::http::RequestContent;
use azure_identity::DeveloperToolsCredential;
```

---

## 2. Client Creation

### 2.1 ✅ CORRECT: BlobClient with Entra ID
```rust
use azure_identity::DeveloperToolsCredential;
use azure_storage_blob::{BlobClient, BlobClientOptions};

let credential = DeveloperToolsCredential::new(None)?;
let blob_client = BlobClient::new(
    "https://<account>.blob.core.windows.net/",
    "container-name",
    "blob-name",
    Some(credential),
    Some(BlobClientOptions::default()),
)?;
```

### 2.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded account key
```rust
// WRONG - use Entra ID authentication
let account_key = "actual-key-here";
```

---

## 3. Blob Operations

### 3.1 ✅ CORRECT: Upload Blob
```rust
use azure_core::http::RequestContent;

let data = b"hello world";
blob_client
    .upload(
        RequestContent::from(data.to_vec()),
        false,  // overwrite
        u64::try_from(data.len())?,
        None,
    )
    .await?;
```

### 3.2 ✅ CORRECT: Download Blob
```rust
let response = blob_client.download(None).await?;
let content = response.into_body().collect_bytes().await?;
```

### 3.3 ✅ CORRECT: Get Blob Properties
```rust
let properties = blob_client.get_properties(None).await?;
```

### 3.4 ✅ CORRECT: Delete Blob
```rust
blob_client.delete(None).await?;
```

### 3.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing content length
```rust
// WRONG - content length is required
blob_client.upload(data, false, None).await?;
```

---

## 4. Container Operations

### 4.1 ✅ CORRECT: Create Container Client
```rust
use azure_storage_blob::BlobContainerClient;

let container_client = BlobContainerClient::new(
    "https://<account>.blob.core.windows.net/",
    "container-name",
    Some(credential),
    None,
)?;
```

### 4.2 ✅ CORRECT: Create Container
```rust
container_client.create(None).await?;
```

---

## 5. Best Practices

### 5.1 ✅ CORRECT: Use RequestContent for upload data
```rust
use azure_core::http::RequestContent;

let data = RequestContent::from(bytes.to_vec());
```

### 5.2 ✅ CORRECT: Specify content length
```rust
blob_client.upload(data, false, content_length, None).await?;
```
