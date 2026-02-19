# Azure Key Vault Certificates SDK for Rust Acceptance Criteria

**Crate**: `azure_security_keyvault_certificates`
**Repository**: https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/keyvault/azure_security_keyvault_certificates
**Purpose**: Skill testing acceptance criteria for validating generated Rust code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Client and Model Imports
```rust
use azure_security_keyvault_certificates::CertificateClient;
use azure_security_keyvault_certificates::models::{
    CreateCertificateParameters, CertificatePolicy,
    IssuerParameters, X509CertificateProperties,
    ImportCertificateParameters,
};
use azure_security_keyvault_certificates::ResourceExt;
use azure_core::base64;
use azure_identity::DeveloperToolsCredential;
```

---

## 2. Client Creation

### 2.1 ✅ CORRECT: CertificateClient with Entra ID
```rust
use azure_identity::DeveloperToolsCredential;
use azure_security_keyvault_certificates::CertificateClient;

let credential = DeveloperToolsCredential::new(None)?;
let client = CertificateClient::new(
    "https://<vault-name>.vault.azure.net/",
    credential.clone(),
    None,
)?;
```

---

## 3. Certificate Operations

### 3.1 ✅ CORRECT: Get Certificate
```rust
use azure_core::base64;

let certificate = client
    .get_certificate("certificate-name", None)
    .await?
    .into_model()?;

println!(
    "Thumbprint: {:?}",
    certificate.x509_thumbprint.map(base64::encode_url_safe)
);
```

### 3.2 ✅ CORRECT: Create Self-Signed Certificate
```rust
use azure_security_keyvault_certificates::models::{
    CreateCertificateParameters, CertificatePolicy,
    IssuerParameters, X509CertificateProperties,
};

let policy = CertificatePolicy {
    issuer_parameters: Some(IssuerParameters {
        name: Some("Self".into()),
        ..Default::default()
    }),
    x509_certificate_properties: Some(X509CertificateProperties {
        subject: Some("CN=example.com".into()),
        ..Default::default()
    }),
    ..Default::default()
};

let params = CreateCertificateParameters {
    certificate_policy: Some(policy),
    ..Default::default()
};

let operation = client
    .create_certificate("cert-name", params.try_into()?, None)
    .await?;
```

### 3.3 ✅ CORRECT: Import Certificate
```rust
use azure_security_keyvault_certificates::models::ImportCertificateParameters;

let params = ImportCertificateParameters {
    base64_encoded_certificate: Some(base64_cert_data),
    password: Some("optional-password".into()),
    ..Default::default()
};

let certificate = client
    .import_certificate("cert-name", params.try_into()?, None)
    .await?
    .into_model()?;
```

### 3.4 ✅ CORRECT: List Certificates with Paging
```rust
use azure_security_keyvault_certificates::ResourceExt;
use futures::TryStreamExt;

let mut pager = client.list_certificate_properties(None)?.into_stream();
while let Some(cert) = pager.try_next().await? {
    let name = cert.resource_id()?.name;
    println!("Certificate: {}", name);
}
```

### 3.5 ✅ CORRECT: Delete Certificate
```rust
client.delete_certificate("certificate-name", None).await?;
```

### 3.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Not using into_model
```rust
// WRONG - must call into_model() to get the certificate
let cert = client.get_certificate("name", None).await?;
```

---

## 4. Certificate Policy

### 4.1 ✅ CORRECT: Self-Signed Issuer
```rust
let issuer = IssuerParameters {
    name: Some("Self".into()),
    ..Default::default()
};
```

### 4.2 ✅ CORRECT: X509 Properties
```rust
let x509_props = X509CertificateProperties {
    subject: Some("CN=example.com".into()),
    ..Default::default()
};
```

---

## 5. Best Practices

### 5.1 ✅ CORRECT: Use into_model for responses
```rust
let certificate = response.into_model()?;
```

### 5.2 ✅ CORRECT: Use ResourceExt for extracting names
```rust
use azure_security_keyvault_certificates::ResourceExt;

let name = cert.resource_id()?.name;
```

### 5.3 ✅ CORRECT: Use base64 for thumbprint display
```rust
use azure_core::base64;

certificate.x509_thumbprint.map(base64::encode_url_safe)
```
