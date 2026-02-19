# Azure Identity SDK Acceptance Criteria

**SDK**: `azure-identity`
**Repository**: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: Sync Credential Imports
```python
from azure.identity import (
    DefaultAzureCredential,
    ManagedIdentityCredential,
    ClientSecretCredential,
    InteractiveBrowserCredential,
    ChainedTokenCredential,
    TokenCachePersistenceOptions,
    AzureCliCredential,
)
```

### 1.2 ✅ CORRECT: Async Credential Imports
```python
from azure.identity.aio import (
    DefaultAzureCredential,
    ManagedIdentityCredential,
    ClientSecretCredential,
    InteractiveBrowserCredential,
    ChainedTokenCredential,
)
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module paths or missing .aio
```python
# WRONG - async credentials must be imported from azure.identity.aio
from azure.identity import DefaultAzureCredential

# WRONG - token cache options are not in azure.identity.aio
from azure.identity.aio import TokenCachePersistenceOptions
```

---

## 2. DefaultAzureCredential

### 2.1 ✅ CORRECT: Basic DefaultAzureCredential
```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default")
print(token.expires_on)
```

### 2.2 ✅ CORRECT: Customize DefaultAzureCredential
```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential(
    exclude_environment_credential=True,
    exclude_shared_token_cache_credential=True,
    exclude_interactive_browser_credential=False,
    managed_identity_client_id="<user-assigned-mi-client-id>",
)
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded access token usage
```python
# WRONG - never hardcode access tokens
token = "eyJ0eXAiOiJKV1QiLCJhbGci..."
```

---

## 3. ManagedIdentityCredential

### 3.1 ✅ CORRECT: System-assigned Managed Identity
```python
from azure.identity import ManagedIdentityCredential

credential = ManagedIdentityCredential()
```

### 3.2 ✅ CORRECT: User-assigned Managed Identity
```python
from azure.identity import ManagedIdentityCredential

credential = ManagedIdentityCredential(client_id="<user-assigned-mi-client-id>")
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Passing tenant_id to ManagedIdentityCredential
```python
# WRONG - ManagedIdentityCredential doesn't accept tenant_id
credential = ManagedIdentityCredential(tenant_id="<tenant-id>")
```

---

## 4. ClientSecretCredential

### 4.1 ✅ CORRECT: Client Secret Auth
```python
import os
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"],
)
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded secrets
```python
# WRONG - never hardcode secrets
credential = ClientSecretCredential(
    tenant_id="tenant-id",
    client_id="client-id",
    client_secret="super-secret",
)
```

---

## 5. InteractiveBrowserCredential

### 5.1 ✅ CORRECT: Interactive Browser Auth
```python
from azure.identity import InteractiveBrowserCredential

credential = InteractiveBrowserCredential()
token = credential.get_token("https://management.azure.com/.default")
print(token.token)
```

### 5.2 ✅ CORRECT: Custom tenant and client ID
```python
from azure.identity import InteractiveBrowserCredential

credential = InteractiveBrowserCredential(
    tenant_id="<tenant-id>",
    client_id="<client-id>",
)
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using InteractiveBrowserCredential in async without .aio
```python
# WRONG - async code must use azure.identity.aio
from azure.identity import InteractiveBrowserCredential

credential = InteractiveBrowserCredential()
```

---

## 6. ChainedTokenCredential

### 6.1 ✅ CORRECT: Custom Credential Chain
```python
from azure.identity import ChainedTokenCredential, ManagedIdentityCredential, AzureCliCredential

credential = ChainedTokenCredential(
    ManagedIdentityCredential(client_id="<user-assigned-mi-client-id>"),
    AzureCliCredential(),
)
```

### 6.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Passing strings instead of credential instances
```python
# WRONG - ChainedTokenCredential expects credential instances
credential = ChainedTokenCredential(
    "ManagedIdentityCredential",
    "AzureCliCredential",
)
```

---

## 7. Token Caching

### 7.1 ✅ CORRECT: Enable persistent token cache
```python
from azure.identity import DefaultAzureCredential, TokenCachePersistenceOptions

cache_options = TokenCachePersistenceOptions(
    name="azure_identity_cache",
    allow_unencrypted_storage=True,
)

credential = DefaultAzureCredential(cache_persistence_options=cache_options)
```

### 7.2 ✅ CORRECT: In-memory token caching (default)
```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
```

### 7.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Rolling your own disk cache for access tokens
```python
# WRONG - don't persist raw tokens yourself
with open("token.txt", "w") as handle:
    handle.write("<raw-token>")
```
