# Azure Identity SDK for Rust Acceptance Criteria

**Crate**: `azure_identity`
**Repository**: https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/identity/azure_identity
**Purpose**: Skill testing acceptance criteria for validating generated Rust code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Credential Imports
```rust
use azure_identity::DeveloperToolsCredential;
use azure_identity::ManagedIdentityCredential;
use azure_identity::ClientSecretCredential;
use azure_identity::AzureCliCredential;
use azure_identity::AzureDeveloperCliCredential;
use azure_identity::WorkloadIdentityCredential;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: DefaultAzureCredential (doesn't exist in Rust SDK)
```rust
// WRONG - use DeveloperToolsCredential instead
use azure_identity::DefaultAzureCredential;
```

---

## 2. DeveloperToolsCredential

### 2.1 ✅ CORRECT: Basic DeveloperToolsCredential
```rust
use azure_identity::DeveloperToolsCredential;

let credential = DeveloperToolsCredential::new(None)?;
```

### 2.2 ✅ CORRECT: Using with SecretClient
```rust
use azure_identity::DeveloperToolsCredential;
use azure_security_keyvault_secrets::SecretClient;

let credential = DeveloperToolsCredential::new(None)?;
let client = SecretClient::new(
    "https://my-vault.vault.azure.net/",
    credential.clone(),
    None,
)?;
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```rust
// WRONG - never hardcode credentials
let secret = "my-secret-value";
```

---

## 3. ManagedIdentityCredential

### 3.1 ✅ CORRECT: System-assigned Managed Identity
```rust
use azure_identity::ManagedIdentityCredential;

let credential = ManagedIdentityCredential::new(None)?;
```

### 3.2 ✅ CORRECT: User-assigned Managed Identity
```rust
use azure_identity::{ManagedIdentityCredential, ManagedIdentityCredentialOptions};

let options = ManagedIdentityCredentialOptions {
    client_id: Some("<user-assigned-mi-client-id>".into()),
    ..Default::default()
};
let credential = ManagedIdentityCredential::new(Some(options))?;
```

---

## 4. ClientSecretCredential

### 4.1 ✅ CORRECT: Service Principal Authentication
```rust
use azure_identity::ClientSecretCredential;

let credential = ClientSecretCredential::new(
    "<tenant-id>".into(),
    "<client-id>".into(),
    "<client-secret>".into(),
    None,
)?;
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded secrets in code
```rust
// WRONG - use environment variables instead
let credential = ClientSecretCredential::new(
    "12345-tenant".into(),
    "abcde-client".into(),
    "actual-secret-here".into(),
    None,
)?;
```

---

## 5. Best Practices

### 5.1 ✅ CORRECT: Clone credentials for multiple clients
```rust
let credential = DeveloperToolsCredential::new(None)?;
let client1 = SecretClient::new(url, credential.clone(), None)?;
let client2 = KeyClient::new(url, credential.clone(), None)?;
```

### 5.2 ✅ CORRECT: Use environment variables
```rust
use std::env;

let tenant_id = env::var("AZURE_TENANT_ID")?;
let client_id = env::var("AZURE_CLIENT_ID")?;
let client_secret = env::var("AZURE_CLIENT_SECRET")?;
```
