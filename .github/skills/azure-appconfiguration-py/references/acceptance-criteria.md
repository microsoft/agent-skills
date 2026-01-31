# Azure App Configuration Acceptance Criteria

**SDK**: `azure-appconfiguration`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Sync Client via Connection String
```python
from azure.appconfiguration import AzureAppConfigurationClient

client = AzureAppConfigurationClient.from_connection_string(
    os.environ["AZURE_APPCONFIGURATION_CONNECTION_STRING"]
)
```

#### ✅ CORRECT: Sync Client via Entra ID
```python
from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential

client = AzureAppConfigurationClient(
    base_url=os.environ["AZURE_APPCONFIGURATION_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

#### ✅ CORRECT: Async Client via Entra ID
```python
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.identity.aio import DefaultAzureCredential

client = AzureAppConfigurationClient(
    base_url=os.environ["AZURE_APPCONFIGURATION_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

### 1.2 Model Imports

#### ✅ CORRECT: Configuration Setting
```python
from azure.appconfiguration import ConfigurationSetting

setting = ConfigurationSetting(
    key="app:message",
    value="Hello, World!",
    label="production"
)
```

#### ✅ CORRECT: Snapshot Models
```python
from azure.appconfiguration import (
    ConfigurationSnapshot,
    ConfigurationSettingFilter
)

snapshot = ConfigurationSnapshot(
    name="v1-snapshot",
    filters=[ConfigurationSettingFilter(key="app:*")]
)
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong module path
```python
# WRONG - ConfigurationSetting is not in this module
from azure.appconfiguration.models import ConfigurationSetting

# WRONG - Client should not be imported from models
from azure.appconfiguration.models import AzureAppConfigurationClient
```

**Instead:** Import directly from `azure.appconfiguration` for both `ConfigurationSetting` and `AzureAppConfigurationClient`. The models submodule does not expose these classes publicly.

#### ❌ INCORRECT: Using async with sync imports
```python
# WRONG - mixing sync and async
from azure.appconfiguration import AzureAppConfigurationClient  # Sync
from azure.identity.aio import DefaultAzureCredential  # Async
```

**Instead:** Use async modules from `azure.appconfiguration.aio` and `azure.identity.aio` when working with async code. Sync and async credential types are not compatible.

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Connection String
```python
from azure.appconfiguration import AzureAppConfigurationClient

client = AzureAppConfigurationClient.from_connection_string(
    os.environ["AZURE_APPCONFIGURATION_CONNECTION_STRING"]
)

setting = client.get_configuration_setting(key="app:message")
print(setting.value)
```

### 2.2 ✅ CORRECT: Entra ID Authentication
```python
from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential

client = AzureAppConfigurationClient(
    base_url=os.environ["AZURE_APPCONFIGURATION_ENDPOINT"],
    credential=DefaultAzureCredential()
)

setting = client.get_configuration_setting(key="app:message")
```

### 2.3 ✅ CORRECT: Context Manager
```python
from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential

with AzureAppConfigurationClient(
    base_url=endpoint,
    credential=DefaultAzureCredential()
) as client:
    setting = client.get_configuration_setting(key="app:message")
    print(setting.value)
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - never hardcode credentials
client = AzureAppConfigurationClient(
    base_url="https://mystore.azconfig.io",
    credential="mykey"  # WRONG
)
```

**Instead:** Use `DefaultAzureCredential()` and environment variables. Hardcoded credentials are a security vulnerability and should never be used in production code. Load endpoint and credentials from environment variables or secure configuration systems.

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - parameter is 'base_url', not 'endpoint'
client = AzureAppConfigurationClient(endpoint=endpoint, credential=cred)
```

**Instead:** The correct parameter name is `base_url`, not `endpoint`. Use `base_url` to specify the Azure App Configuration endpoint URL.

#### ❌ INCORRECT: Not using context manager
```python
# WRONG - should use context manager for cleanup
client = AzureAppConfigurationClient(base_url=endpoint, credential=cred)
setting = client.get_configuration_setting(key="app:message")
# Missing: client.close() or using 'with' statement
```

**Instead:** Always use a context manager (`with` statement) when creating clients. This ensures proper resource cleanup and connection handling automatically, even if an exception occurs.

---

## 3. Configuration Settings Patterns

### 3.1 ✅ CORRECT: Get Setting
```python
setting = client.get_configuration_setting(key="app:settings:message")
print(f"Key: {setting.key}, Value: {setting.value}")
```

### 3.2 ✅ CORRECT: Get Setting with Label
```python
# Labels enable environment-specific values
setting = client.get_configuration_setting(
    key="app:settings:message",
    label="production"
)
```

### 3.3 ✅ CORRECT: Set Setting
```python
from azure.appconfiguration import ConfigurationSetting

setting = ConfigurationSetting(
    key="app:settings:message",
    value="Hello, World!",
    label="development",
    content_type="text/plain",
    tags={"environment": "dev"}
)

client.set_configuration_setting(setting)
```

### 3.4 ✅ CORRECT: Delete Setting
```python
client.delete_configuration_setting(
    key="app:settings:message",
    label="development"
)
```

### 3.5 ✅ CORRECT: List All Settings
```python
settings = client.list_configuration_settings()
for setting in settings:
    print(f"{setting.key} [{setting.label}] = {setting.value}")
```

### 3.6 ✅ CORRECT: List with Filters
```python
# Filter by key prefix
settings = client.list_configuration_settings(key_filter="app:settings:*")

# Filter by label
settings = client.list_configuration_settings(label_filter="production")

# Combine filters
settings = client.list_configuration_settings(
    key_filter="app:*",
    label_filter="production"
)
```

### 3.7 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong parameter names
```python
# WRONG - parameters are 'key_filter' and 'label_filter'
settings = client.list_configuration_settings(key="app:*", label="prod")
```

**Instead:** Use the correct parameter names `key_filter` and `label_filter` when filtering configuration settings in a list operation.

#### ❌ INCORRECT: Setting without required fields
```python
# WRONG - must have key and value
setting = ConfigurationSetting(label="prod")
```

**Instead:** `ConfigurationSetting` requires both `key` and `value` fields. The `label` parameter is optional and used for environment-specific configurations.

---

## 4. Feature Flag Patterns

### 4.1 ✅ CORRECT: Set Feature Flag
```python
from azure.appconfiguration import ConfigurationSetting
import json

feature_flag = ConfigurationSetting(
    key=".appconfig.featureflag/beta-feature",
    value=json.dumps({
        "id": "beta-feature",
        "enabled": True,
        "conditions": {
            "client_filters": []
        }
    }),
    content_type="application/vnd.microsoft.appconfig.ff+json;charset=utf-8"
)

client.set_configuration_setting(feature_flag)
```

### 4.2 ✅ CORRECT: Get Feature Flag
```python
setting = client.get_configuration_setting(
    key=".appconfig.featureflag/beta-feature"
)
flag_data = json.loads(setting.value)
print(f"Feature enabled: {flag_data['enabled']}")
```

### 4.3 ✅ CORRECT: List Feature Flags
```python
flags = client.list_configuration_settings(
    key_filter=".appconfig.featureflag/*"
)

for flag in flags:
    data = json.loads(flag.value)
    status = "enabled" if data.get("enabled") else "disabled"
    print(f"{data['id']}: {status}")
```

### 4.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong content type
```python
# WRONG - content type must be specific for feature flags
feature_flag = ConfigurationSetting(
    key=".appconfig.featureflag/beta-feature",
    value=json.dumps({"id": "beta-feature", "enabled": True}),
    content_type="application/json"  # WRONG format
)
```

**Instead:** Feature flags must use the specific content type `"application/vnd.microsoft.appconfig.ff+json;charset=utf-8"`. This tells the Azure App Configuration service to recognize and handle this setting as a feature flag, enabling proper feature management capabilities.

#### ❌ INCORRECT: Not using json.dumps for feature flag value
```python
# WRONG - value must be JSON string
feature_flag = ConfigurationSetting(
    key=".appconfig.featureflag/beta-feature",
    value={"id": "beta-feature", "enabled": True},  # Should be string
)
```

**Instead:** The `value` parameter must be a JSON string, not a Python dict. Use `json.dumps()` to serialize the dictionary to a JSON string before passing it to `ConfigurationSetting`.

---

## 5. Read-Only Settings Patterns

### 5.1 ✅ CORRECT: Make Setting Read-Only
```python
# Make setting read-only to prevent accidental changes
client.set_read_only(
    configuration_setting=setting,
    read_only=True
)
```

### 5.2 ✅ CORRECT: Remove Read-Only
```python
# Remove read-only to allow modifications
client.set_read_only(
    configuration_setting=setting,
    read_only=False
)
```

---

## 6. Snapshot Patterns

### 6.1 ✅ CORRECT: Create Snapshot
```python
from azure.appconfiguration import ConfigurationSnapshot, ConfigurationSettingFilter

snapshot = ConfigurationSnapshot(
    name="v1-snapshot",
    filters=[
        ConfigurationSettingFilter(key="app:*", label="production")
    ]
)

created = client.begin_create_snapshot(
    name="v1-snapshot",
    snapshot=snapshot
).result()
```

### 6.2 ✅ CORRECT: List Snapshot Settings
```python
settings = client.list_configuration_settings(
    snapshot_name="v1-snapshot"
)

for setting in settings:
    print(f"{setting.key} = {setting.value}")
```

### 6.3 ✅ CORRECT: List Snapshots
```python
snapshots = client.list_snapshots()
for snapshot in snapshots:
    print(f"Snapshot: {snapshot.name}, Status: {snapshot.status}")
```

---

## 7. Async Client Patterns

### 7.1 ✅ CORRECT: Full Async Example
```python
import asyncio
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.identity.aio import DefaultAzureCredential

async def main():
    credential = DefaultAzureCredential()
    
    async with AzureAppConfigurationClient(
        base_url=os.environ["AZURE_APPCONFIGURATION_ENDPOINT"],
        credential=credential
    ) as client:
        setting = await client.get_configuration_setting(key="app:message")
        print(setting.value)
        
        # Async iteration
        async for setting in await client.list_configuration_settings():
            print(f"{setting.key} = {setting.value}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing await
```python
# WRONG - missing await for async operations
async def bad_example():
    setting = client.get_configuration_setting(key="app:message")  # Missing await
    return setting
```

**Instead:** All async method calls must be preceded by the `await` keyword. Without `await`, the coroutine object is returned instead of the actual result, causing type errors and logic failures.

#### ❌ INCORRECT: Wrong credential type
```python
# WRONG - using sync credential with async client
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential  # Should be from .aio
```

**Instead:** When using async clients, always import credentials from `azure.identity.aio`. Sync credentials are not compatible with async clients and will cause runtime errors.

---

## 8. Environment Variables

### Required Variables
```bash
# For connection string auth
AZURE_APPCONFIGURATION_CONNECTION_STRING=Endpoint=https://<name>.azconfig.io;Id=...;Secret=...

# For Entra ID auth
AZURE_APPCONFIGURATION_ENDPOINT=https://<name>.azconfig.io
```

---

## 9. Best Practices Checklist

### ✅ Do
- [ ] Use `DefaultAzureCredential` for production (not connection strings)
- [ ] Use context managers (`with` statement) for client cleanup
- [ ] Use labels for environment separation (dev, staging, prod)
- [ ] Use key prefixes for logical grouping (app:database:*, app:cache:*)
- [ ] Make production settings read-only to prevent accidental changes
- [ ] Use snapshots before deployments for rollback capability
- [ ] Use async client when building async applications
- [ ] Properly format feature flag keys (`.appconfig.featureflag/*`)

### ❌ Don't
- [ ] Don't hardcode credentials or endpoints
- [ ] Don't use sync client in async code
- [ ] Don't forget `await` in async methods
- [ ] Don't mix sync and async credentials
- [ ] Don't use wrong parameter names (endpoint vs base_url)
- [ ] Don't forget context manager for resource cleanup
- [ ] Don't use wrong content type for feature flags
- [ ] Don't pass dict instead of JSON string for feature flags

---

## 10. Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: 'ConfigurationSetting' object has no attribute 'content'` | Accessing wrong attribute | Use `setting.value`, not `setting.content` |
| `TypeError: unsupported operand type(s)` | Trying to parse non-JSON value | Use `json.loads()` only on feature flags |
| `Missing credentials` | No auth configured | Use `DefaultAzureCredential()` or connection string |
| `Connection refused` | Wrong endpoint | Check `AZURE_APPCONFIGURATION_ENDPOINT` format |
| `Feature flag not found` | Wrong key format | Use `.appconfig.featureflag/name` prefix |
| `Async operation not awaited` | Missing await | Add `await` to async method calls |
| `Wrong credential type` | Using sync with async | Import from `azure.identity.aio` for async |
