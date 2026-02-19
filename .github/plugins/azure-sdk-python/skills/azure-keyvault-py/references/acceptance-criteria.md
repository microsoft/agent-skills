# Azure Key Vault SDK Acceptance Criteria

**SDK**: `azure-keyvault-secrets`, `azure-keyvault-keys`, `azure-keyvault-certificates`
**Repository**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Sync Client Imports
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.keyvault.keys import KeyClient
from azure.keyvault.certificates import CertificateClient, CertificatePolicy
```

### 1.2 ✅ CORRECT: Async Client Imports
```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient
from azure.keyvault.keys.aio import KeyClient
from azure.keyvault.certificates.aio import CertificateClient
```

### 1.3 ✅ CORRECT: Cryptography Imports
```python
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm, SignatureAlgorithm
```

### 1.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module paths or legacy clients
```python
# WRONG - legacy SDK
from azure.keyvault import KeyVaultClient

# WRONG - async client should be imported from .aio
from azure.keyvault.secrets import SecretClient as AsyncSecretClient

# WRONG - crypto client is not in azure.keyvault.keys
from azure.keyvault.keys import CryptographyClient
```

---

## 2. SecretClient

### 2.1 ✅ CORRECT: Client Creation
```python
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

vault_url = os.environ["AZURE_KEYVAULT_URL"]
credential = DefaultAzureCredential()

client = SecretClient(vault_url=vault_url, credential=credential)
```

### 2.2 ✅ CORRECT: Set and Get Secret
```python
secret = client.set_secret("database-password", "super-secret-value")
latest = client.get_secret("database-password")
print(latest.value)
```

### 2.3 ✅ CORRECT: List Secret Properties and Versions
```python
for secret_props in client.list_properties_of_secrets():
    print(secret_props.name)

for version_props in client.list_properties_of_secret_versions("database-password"):
    print(version_props.version)
```

### 2.4 ✅ CORRECT: Delete, Purge, Recover
```python
poller = client.begin_delete_secret("database-password")
deleted = poller.result()

client.purge_deleted_secret("database-password")
client.begin_recover_deleted_secret("database-password").result()
```

### 2.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter name
```python
# WRONG - SecretClient expects vault_url
client = SecretClient(url="https://vault.vault.azure.net/", credential=credential)
```

---

## 3. KeyClient

### 3.1 ✅ CORRECT: Client Creation
```python
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

vault_url = os.environ["AZURE_KEYVAULT_URL"]
credential = DefaultAzureCredential()

client = KeyClient(vault_url=vault_url, credential=credential)
```

### 3.2 ✅ CORRECT: Create RSA and EC Keys
```python
rsa_key = client.create_rsa_key("rsa-key", size=2048)
ec_key = client.create_ec_key("ec-key", curve="P-256")
```

### 3.3 ✅ CORRECT: Get and List Keys
```python
key = client.get_key("rsa-key")
print(key.name)

for key_props in client.list_properties_of_keys():
    print(key_props.name)
```

### 3.4 ✅ CORRECT: Delete Key
```python
poller = client.begin_delete_key("rsa-key")
deleted = poller.result()
print(deleted.name)
```

### 3.5 ✅ CORRECT: Cryptography Operations
```python
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm, SignatureAlgorithm
import hashlib

key = client.get_key("rsa-key")
crypto_client = CryptographyClient(key, credential=credential)

encrypted = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep, b"hello")
decrypted = crypto_client.decrypt(EncryptionAlgorithm.rsa_oaep, encrypted.ciphertext)

digest = hashlib.sha256(b"data").digest()
signature = crypto_client.sign(SignatureAlgorithm.rs256, digest).signature
verified = crypto_client.verify(SignatureAlgorithm.rs256, digest, signature)
print(verified.is_valid)
```

### 3.6 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong client class for keys
```python
# WRONG - keys are managed by KeyClient
from azure.keyvault.secrets import SecretClient
client = SecretClient(vault_url=vault_url, credential=credential)
client.create_rsa_key("rsa-key", size=2048)
```

---

## 4. CertificateClient

### 4.1 ✅ CORRECT: Client Creation
```python
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificatePolicy

vault_url = os.environ["AZURE_KEYVAULT_URL"]
credential = DefaultAzureCredential()

client = CertificateClient(vault_url=vault_url, credential=credential)
policy = CertificatePolicy.get_default()
```

### 4.2 ✅ CORRECT: Create and Get Certificate
```python
poller = client.begin_create_certificate("my-cert", policy=policy)
certificate = poller.result()

latest = client.get_certificate("my-cert")
print(latest.name)
```

### 4.3 ✅ CORRECT: List Certificates
```python
for cert_props in client.list_properties_of_certificates():
    print(cert_props.name)
```

### 4.4 ✅ CORRECT: Delete Certificate
```python
poller = client.begin_delete_certificate("my-cert")
deleted = poller.result()
print(deleted.name)
```

### 4.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using create_certificate on sync client
```python
# WRONG - sync client uses begin_create_certificate
client.create_certificate("my-cert", policy=policy)
```

---

## 5. CRUD Operations

### 5.1 ✅ CORRECT: Secret, Key, Certificate CRUD
```python
# Secret CRUD
secret = secret_client.set_secret("app-secret", "value")
secret = secret_client.get_secret("app-secret")
secret_client.begin_delete_secret("app-secret").result()

# Key CRUD
key = key_client.create_rsa_key("app-key", size=2048)
key = key_client.get_key("app-key")
key_client.begin_delete_key("app-key").result()

# Certificate CRUD
cert = cert_client.begin_create_certificate("app-cert", policy=policy).result()
cert = cert_client.get_certificate("app-cert")
cert_client.begin_delete_certificate("app-cert").result()
```

---

## 6. Async Variants

### 6.1 ✅ CORRECT: Async SecretClient Usage
```python
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

async def main():
    vault_url = os.environ["AZURE_KEYVAULT_URL"]
    credential = DefaultAzureCredential()

    async with SecretClient(vault_url=vault_url, credential=credential) as client:
        secret = await client.get_secret("my-secret")
        print(secret.value)

if __name__ == "__main__":
    asyncio.run(main())
```

### 6.2 ✅ CORRECT: Async KeyClient and CertificateClient Listing
```python
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient
from azure.keyvault.certificates.aio import CertificateClient

async def main():
    vault_url = os.environ["AZURE_KEYVAULT_URL"]
    credential = DefaultAzureCredential()

    async with KeyClient(vault_url=vault_url, credential=credential) as key_client:
        async for key_props in key_client.list_properties_of_keys():
            print(key_props.name)

    async with CertificateClient(vault_url=vault_url, credential=credential) as cert_client:
        async for cert_props in cert_client.list_properties_of_certificates():
            print(cert_props.name)

if __name__ == "__main__":
    asyncio.run(main())
```

### 6.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Sync credential with async client or missing async for
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient

credential = DefaultAzureCredential()  # WRONG - should be azure.identity.aio
client = KeyClient(vault_url=vault_url, credential=credential)

for item in client.list_properties_of_keys():  # WRONG - async iterator
    print(item.name)
```
