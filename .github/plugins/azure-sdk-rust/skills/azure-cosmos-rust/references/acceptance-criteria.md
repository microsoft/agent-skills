# Azure Cosmos DB SDK for Rust Acceptance Criteria

**Crate**: `azure_data_cosmos`
**Repository**: https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/cosmos/azure_data_cosmos
**Purpose**: Skill testing acceptance criteria for validating generated Rust code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Client Imports
```rust
use azure_data_cosmos::CosmosClient;
use azure_data_cosmos::models::PatchDocument;
use azure_identity::DeveloperToolsCredential;
```

### 1.2 ✅ CORRECT: Serde for Item Serialization
```rust
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct Item {
    pub id: String,
    pub partition_key: String,
    pub value: String,
}
```

---

## 2. Client Creation

### 2.1 ✅ CORRECT: Entra ID Authentication
```rust
use azure_identity::DeveloperToolsCredential;
use azure_data_cosmos::CosmosClient;

let credential = DeveloperToolsCredential::new(None)?;
let client = CosmosClient::new(
    "https://<account>.documents.azure.com:443/",
    credential.clone(),
    None,
)?;
```

### 2.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded connection string
```rust
// WRONG - use environment variables
let endpoint = "https://myaccount.documents.azure.com:443/";
let key = "actual-primary-key-here";
```

---

## 3. Client Hierarchy

### 3.1 ✅ CORRECT: Get Database and Container Clients
```rust
let database = client.database_client("myDatabase");
let container = database.container_client("myContainer");
```

---

## 4. CRUD Operations

### 4.1 ✅ CORRECT: Create Item
```rust
let item = Item {
    id: "1".into(),
    partition_key: "partition1".into(),
    value: "hello".into(),
};

container.create_item("partition1", item, None).await?;
```

### 4.2 ✅ CORRECT: Read Item with into_model
```rust
let response = container.read_item("partition1", "1", None).await?;
let item: Item = response.into_model()?;
```

### 4.3 ✅ CORRECT: Replace Item
```rust
let mut item: Item = container
    .read_item("partition1", "1", None)
    .await?
    .into_model()?;

item.value = "updated".into();

container.replace_item("partition1", "1", item, None).await?;
```

### 4.4 ✅ CORRECT: Patch Item
```rust
use azure_data_cosmos::models::PatchDocument;

let patch = PatchDocument::default()
    .with_add("/newField", "newValue")?
    .with_remove("/oldField")?;

container.patch_item("partition1", "1", patch, None).await?;
```

### 4.5 ✅ CORRECT: Delete Item
```rust
container.delete_item("partition1", "1", None).await?;
```

### 4.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing partition key
```rust
// WRONG - partition key is required
container.read_item("1", None).await?;
```

---

## 5. Best Practices

### 5.1 ✅ CORRECT: Always specify partition key
```rust
// Partition key is required for point operations
container.read_item("partition1", "item-id", None).await?;
```

### 5.2 ✅ CORRECT: Use into_model for deserialization
```rust
let item: Item = response.into_model()?;
```
