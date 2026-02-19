# Acceptance Criteria: azure-keyvault-secrets-ts

## Overview

This document defines the acceptance criteria for code generated using the `@azure/keyvault-secrets` SDK for TypeScript/JavaScript.

**Package:** `@azure/keyvault-secrets`  
**Repository:** https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/keyvault/keyvault-secrets

---

## 1. Import Statements

### ✅ MUST

```typescript
// ESM imports
import { SecretClient } from "@azure/keyvault-secrets";
import { DefaultAzureCredential } from "@azure/identity";
```

### ❌ MUST NOT

```typescript
// CommonJS require (deprecated pattern)
const { SecretClient } = require("@azure/keyvault-secrets");

// Old SDK imports
import { KeyVaultClient } from "azure-keyvault";
```

---

## 2. Client Instantiation

### ✅ MUST

```typescript
// Use DefaultAzureCredential for production
const credential = new DefaultAzureCredential();
const vaultName = "<YOUR KEYVAULT NAME>";
const url = `https://${vaultName}.vault.azure.net`;

const client = new SecretClient(url, credential);
```

### ❌ MUST NOT

```typescript
// Hardcoded credentials
const client = new SecretClient(url, "hardcoded-key");

// Missing credential parameter
const client = new SecretClient(url);
```

---

## 3. Secret Operations

### Set Secret

```typescript
// ✅ Correct - set a secret value
const secret = await client.setSecret("MySecretName", "MySecretValue");

// ✅ Correct - with options
const secret = await client.setSecret("MySecretName", "MySecretValue", {
  enabled: true,
  expiresOn: new Date("2025-12-31"),
  contentType: "application/json",
  tags: { environment: "production" },
});
```

### Get Secret

```typescript
// ✅ Correct - get latest version
const secret = await client.getSecret("MySecretName");
console.log(secret.value);

// ✅ Correct - get specific version
const specificSecret = await client.getSecret("MySecretName", {
  version: secret.properties.version!,
});
```

### Update Secret Properties

```typescript
// ✅ Correct - update properties (not value)
await client.updateSecretProperties("MySecretName", secret.properties.version!, {
  enabled: false,
});

// ❌ Incorrect - trying to update value this way
await client.updateSecretProperties("MySecretName", version, {
  value: "new-value", // This won't work - use setSecret instead
});
```

### Delete Secret

```typescript
// ✅ Correct - use poller pattern
const poller = await client.beginDeleteSecret("MySecretName");
await poller.pollUntilDone();

// ✅ Correct - get result immediately
const deletedSecret = poller.getResult();

// ❌ Incorrect - no such method exists
await client.deleteSecret("MySecretName");
```

### Purge Deleted Secret

```typescript
// ✅ Correct - purge after delete completes
await client.purgeDeletedSecret("MySecretName");
```

### Recover Deleted Secret

```typescript
// ✅ Correct - use poller pattern
const recoverPoller = await client.beginRecoverDeletedSecret("MySecretName");
await recoverPoller.pollUntilDone();
```

---

## 4. List Operations

### List Secrets

```typescript
// ✅ Correct - async iteration (properties only, not values)
for await (const secretProperties of client.listPropertiesOfSecrets()) {
  console.log(secretProperties.name);
}

// ✅ Correct - paginated
for await (const page of client.listPropertiesOfSecrets().byPage()) {
  for (const secretProperties of page) {
    console.log(secretProperties.name);
  }
}
```

### List Deleted Secrets

```typescript
// ✅ Correct
for await (const deletedSecret of client.listDeletedSecrets()) {
  console.log(deletedSecret.name);
}
```

### List Secret Versions

```typescript
// ✅ Correct
for await (const versionProperties of client.listPropertiesOfSecretVersions("MySecretName")) {
  console.log(versionProperties.version);
}
```

---

## 5. Backup and Restore

### Backup

```typescript
// ✅ Correct
const backupResult = await client.backupSecret("MySecretName");
// Store backupResult (Uint8Array) securely
```

### Restore

```typescript
// ✅ Correct
const restoredSecret = await client.restoreSecretBackup(backupData);
```

---

## 6. Error Handling

### ✅ MUST

```typescript
import { RestError } from "@azure/core-rest-pipeline";

try {
  const secret = await client.getSecret("NonExistent");
} catch (error) {
  if (error instanceof RestError && error.statusCode === 404) {
    console.log("Secret not found");
  } else {
    throw error;
  }
}
```

### ❌ MUST NOT

```typescript
// Empty catch blocks
try {
  await client.getSecret("secret");
} catch (error) {
  // silently ignore
}

// Generic exception handling without specific checks
try {
  await client.getSecret("secret");
} catch (error) {
  console.log("Error");
}
```

---

## 7. Environment Variables

### ✅ MUST

```typescript
const vaultName = process.env.AZURE_KEYVAULT_NAME;
const url = `https://${vaultName}.vault.azure.net`;

// Or use full URL
const url = process.env.KEY_VAULT_URL;
```

### ❌ MUST NOT

```typescript
// Hardcoded vault URLs
const url = "https://my-vault.vault.azure.net";

// Hardcoded secret values
const secret = await client.setSecret("key", "hardcoded-secret-value");
```

---

## 8. Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| `await client.deleteSecret()` | `await client.beginDeleteSecret()` with poller |
| `require("@azure/keyvault-secrets")` | `import { SecretClient } from "@azure/keyvault-secrets"` |
| Hardcoded credentials | Use `DefaultAzureCredential` |
| `new KeyVaultClient()` | `new SecretClient()` |
| Sync operations | All operations are async - use `await` |
| Ignoring poller results | Always await `pollUntilDone()` for LRO |
| `listSecrets()` | `listPropertiesOfSecrets()` |
| `listSecretVersions()` | `listPropertiesOfSecretVersions()` |

---

## 9. Type Imports

```typescript
import {
  SecretClient,
  KeyVaultSecret,
  SecretProperties,
  DeletedSecret,
  SetSecretOptions,
  GetSecretOptions,
} from "@azure/keyvault-secrets";
```

---

## 10. Important Notes

1. **Secret values are not returned in list operations** - Use `getSecret()` to retrieve values
2. **Properties vs Values** - `listPropertiesOfSecrets()` returns metadata only
3. **Browser not supported** - This SDK is Node.js only due to Key Vault service limitations
4. **Soft-delete** - Deleted secrets are retained and must be purged for permanent deletion

---

## References

- [Official SDK README](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/keyvault/keyvault-secrets)
- [API Reference](https://learn.microsoft.com/javascript/api/@azure/keyvault-secrets)
- [Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/keyvault/keyvault-secrets/samples)
