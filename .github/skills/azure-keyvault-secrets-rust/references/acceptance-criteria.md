# Azure Key Vault Secrets SDK for Rust Acceptance Criteria

**Crate**: `azure_security_keyvault_secrets`
**Repository**: https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/keyvault/azure_security_keyvault_secrets
**Purpose**: Skill testing acceptance criteria for validating generated Rust code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Client and Model Imports
```rust
use azure_security_keyvault_secrets::SecretClient;
use azure_security_keyvault_secrets::models::SetSecretParameters;
use azure_security_keyvault_secrets::models::UpdateSecretPropertiesParameters;
use azure_security_keyvault_secrets::ResourceExt;
use azure_identity::DeveloperToolsCredential;
```

---

## 2. Client Creation

### 2.1 ✅ CORRECT: SecretClient with Entra ID
```rust
use azure_identity::DeveloperToolsCredential;
use azure_security_keyvault_secrets::SecretClient;

let credential = DeveloperToolsCredential::new(None)?;
let client = SecretClient::new(
    "https://<vault-name>.vault.azure.net/",
    credential.clone(),
    None,
)?;
```

### 2.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded vault URL
```rust
// WRONG - use environment variables
let client = SecretClient::new(
    "https://my-actual-vault.vault.azure.net/",
    credential,
    None,
)?;
```

---

## 3. Secret Operations

### 3.1 ✅ CORRECT: Get Secret
```rust
let secret = client
    .get_secret("secret-name", None)
    .await?
    .into_model()?;

println!("Secret value: {:?}", secret.value);
```

### 3.2 ✅ CORRECT: Set Secret
```rust
use azure_security_keyvault_secrets::models::SetSecretParameters;

let params = SetSecretParameters {
    value: Some("secret-value".into()),
    ..Default::default()
};

let secret = client
    .set_secret("secret-name", params.try_into()?, None)
    .await?
    .into_model()?;
```

### 3.3 ✅ CORRECT: Update Secret Properties
```rust
use azure_security_keyvault_secrets::models::UpdateSecretPropertiesParameters;
use std::collections::HashMap;

let params = UpdateSecretPropertiesParameters {
    content_type: Some("text/plain".into()),
    tags: Some(HashMap::from([("env".into(), "prod".into())])),
    ..Default::default()
};

client
    .update_secret_properties("secret-name", params.try_into()?, None)
    .await?;
```

### 3.4 ✅ CORRECT: List Secrets with Paging
```rust
use azure_security_keyvault_secrets::ResourceExt;
use futures::TryStreamExt;

let mut pager = client.list_secret_properties(None)?.into_stream();
while let Some(secret) = pager.try_next().await? {
    let name = secret.resource_id()?.name;
    println!("Secret: {}", name);
}
```

### 3.5 ✅ CORRECT: Delete Secret
```rust
client.delete_secret("secret-name", None).await?;
```

### 3.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using into_model
```rust
// WRONG - must call into_model() to get the secret
let secret = client.get_secret("name", None).await?;
```

---

## 4. Best Practices

### 4.1 ✅ CORRECT: Use into_model for responses
```rust
let secret = response.into_model()?;
```

### 4.2 ✅ CORRECT: Use ResourceExt for extracting names
```rust
use azure_security_keyvault_secrets::ResourceExt;

let name = secret.resource_id()?.name;
```

### 4.3 ✅ CORRECT: Use try_into for parameters
```rust
let params = SetSecretParameters { ... };
client.set_secret("name", params.try_into()?, None).await?;
```
