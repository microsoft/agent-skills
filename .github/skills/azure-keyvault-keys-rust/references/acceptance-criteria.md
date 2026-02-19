# Azure Key Vault Keys SDK for Rust Acceptance Criteria

**Crate**: `azure_security_keyvault_keys`
**Repository**: https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/keyvault/azure_security_keyvault_keys
**Purpose**: Skill testing acceptance criteria for validating generated Rust code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Client and Model Imports
```rust
use azure_security_keyvault_keys::KeyClient;
use azure_security_keyvault_keys::models::{CreateKeyParameters, KeyType, CurveName};
use azure_security_keyvault_keys::ResourceExt;
use azure_identity::DeveloperToolsCredential;
```

---

## 2. Client Creation

### 2.1 ✅ CORRECT: KeyClient with Entra ID
```rust
use azure_identity::DeveloperToolsCredential;
use azure_security_keyvault_keys::KeyClient;

let credential = DeveloperToolsCredential::new(None)?;
let client = KeyClient::new(
    "https://<vault-name>.vault.azure.net/",
    credential.clone(),
    None,
)?;
```

---

## 3. Key Operations

### 3.1 ✅ CORRECT: Get Key
```rust
let key = client
    .get_key("key-name", None)
    .await?
    .into_model()?;

println!("Key ID: {:?}", key.key.as_ref().map(|k| &k.kid));
```

### 3.2 ✅ CORRECT: Create RSA Key
```rust
use azure_security_keyvault_keys::models::{CreateKeyParameters, KeyType};

let params = CreateKeyParameters {
    kty: KeyType::Rsa,
    key_size: Some(2048),
    ..Default::default()
};

let key = client
    .create_key("key-name", params.try_into()?, None)
    .await?
    .into_model()?;
```

### 3.3 ✅ CORRECT: Create EC Key
```rust
use azure_security_keyvault_keys::models::{CreateKeyParameters, KeyType, CurveName};

let params = CreateKeyParameters {
    kty: KeyType::Ec,
    curve: Some(CurveName::P256),
    ..Default::default()
};

let key = client
    .create_key("ec-key", params.try_into()?, None)
    .await?
    .into_model()?;
```

### 3.4 ✅ CORRECT: List Keys with Paging
```rust
use azure_security_keyvault_keys::ResourceExt;
use futures::TryStreamExt;

let mut pager = client.list_key_properties(None)?.into_stream();
while let Some(key) = pager.try_next().await? {
    let name = key.resource_id()?.name;
    println!("Key: {}", name);
}
```

### 3.5 ✅ CORRECT: Delete Key
```rust
client.delete_key("key-name", None).await?;
```

### 3.6 ✅ CORRECT: Backup Key
```rust
let backup = client.backup_key("key-name", None).await?;
```

### 3.7 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using into_model
```rust
// WRONG - must call into_model() to get the key
let key = client.get_key("name", None).await?;
```

---

## 4. Key Types

### 4.1 ✅ CORRECT: Supported Key Types
```rust
use azure_security_keyvault_keys::models::KeyType;

KeyType::Rsa      // RSA keys
KeyType::RsaHsm   // HSM-protected RSA keys
KeyType::Ec       // Elliptic curve keys
KeyType::EcHsm    // HSM-protected EC keys
```

### 4.2 ✅ CORRECT: Curve Names for EC Keys
```rust
use azure_security_keyvault_keys::models::CurveName;

CurveName::P256   // NIST P-256
CurveName::P384   // NIST P-384
CurveName::P521   // NIST P-521
```

---

## 5. Best Practices

### 5.1 ✅ CORRECT: Use into_model for responses
```rust
let key = response.into_model()?;
```

### 5.2 ✅ CORRECT: Use ResourceExt for extracting names
```rust
use azure_security_keyvault_keys::ResourceExt;

let name = key.resource_id()?.name;
```

### 5.3 ✅ CORRECT: Use HSM keys for sensitive workloads
```rust
let params = CreateKeyParameters {
    kty: KeyType::RsaHsm,  // Hardware-protected
    key_size: Some(2048),
    ..Default::default()
};
```
