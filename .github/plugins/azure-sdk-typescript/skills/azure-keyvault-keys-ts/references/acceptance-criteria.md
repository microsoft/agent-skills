# Acceptance Criteria: azure-keyvault-keys-ts

## Overview

This document defines the acceptance criteria for code generated using the `@azure/keyvault-keys` SDK for TypeScript/JavaScript.

**Package:** `@azure/keyvault-keys`  
**Repository:** https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/keyvault/keyvault-keys

---

## 1. Import Statements

### ✅ MUST

```typescript
// ESM imports
import { KeyClient, CryptographyClient } from "@azure/keyvault-keys";
import { DefaultAzureCredential } from "@azure/identity";
```

### ❌ MUST NOT

```typescript
// CommonJS require (deprecated pattern)
const { KeyClient } = require("@azure/keyvault-keys");

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

const client = new KeyClient(url, credential);
```

### ✅ MAY (for testing only)

```typescript
import { AzureKeyCredential } from "@azure/core-auth";

// API key only for specific scenarios, prefer DefaultAzureCredential
const client = new KeyClient(url, new AzureKeyCredential("<api-key>"));
```

### ❌ MUST NOT

```typescript
// Hardcoded credentials
const client = new KeyClient(url, "hardcoded-key");

// Missing credential parameter
const client = new KeyClient(url);
```

---

## 3. Key Operations

### Create Key

```typescript
// ✅ Correct - specify key type
const key = await client.createKey("MyKeyName", "RSA");

// ✅ Correct - RSA with options
const rsaKey = await client.createRsaKey("MyRsaKey", { keySize: 2048 });

// ✅ Correct - EC key
const ecKey = await client.createEcKey("MyEcKey", { curve: "P-256" });

// ❌ Incorrect - missing key type
const key = await client.createKey("MyKeyName");
```

### Get Key

```typescript
// ✅ Correct - get latest version
const key = await client.getKey("MyKeyName");

// ✅ Correct - get specific version
const specificKey = await client.getKey("MyKeyName", { version: "abc123" });
```

### Update Key Properties

```typescript
// ✅ Correct - update properties
await client.updateKeyProperties("MyKeyName", latestKey.properties.version, {
  enabled: false,
});
```

### Delete Key

```typescript
// ✅ Correct - use poller pattern
const poller = await client.beginDeleteKey("MyKeyName");
await poller.pollUntilDone();

// ✅ Correct - get result immediately
const deletedKey = poller.getResult();

// ❌ Incorrect - no such method exists
await client.deleteKey("MyKeyName");
```

### Purge Deleted Key

```typescript
// ✅ Correct - purge after delete completes
await client.purgeDeletedKey("MyKeyName");
```

### Recover Deleted Key

```typescript
// ✅ Correct - use poller pattern
const recoverPoller = await client.beginRecoverDeletedKey("MyKeyName");
await recoverPoller.pollUntilDone();
```

---

## 4. Key Rotation

### Manual Rotation

```typescript
// ✅ Correct
const rotatedKey = await client.rotateKey("MyKeyName");
```

### Rotation Policy

```typescript
// ✅ Correct - set rotation policy
await client.updateKeyRotationPolicy("MyKeyName", {
  lifetimeActions: [
    {
      action: "Rotate",
      timeBeforeExpiry: "P30D",
    },
  ],
  expiresIn: "P90D",
});

// ✅ Correct - get rotation policy
const policy = await client.getKeyRotationPolicy("MyKeyName");
```

---

## 5. List Operations

### List Keys

```typescript
// ✅ Correct - async iteration
for await (const keyProperties of client.listPropertiesOfKeys()) {
  console.log(keyProperties.name);
}

// ✅ Correct - paginated
for await (const page of client.listPropertiesOfKeys().byPage()) {
  for (const keyProperties of page) {
    console.log(keyProperties.name);
  }
}
```

### List Deleted Keys

```typescript
// ✅ Correct
for await (const deletedKey of client.listDeletedKeys()) {
  console.log(deletedKey.name);
}
```

### List Key Versions

```typescript
// ✅ Correct
for await (const versionProperties of client.listPropertiesOfKeyVersions("MyKeyName")) {
  console.log(versionProperties.version);
}
```

---

## 6. Cryptography Operations

### Create CryptographyClient

```typescript
// ✅ Correct - from key object
const cryptoClient = new CryptographyClient(key, credential);

// ✅ Correct - from key ID
const cryptoClient = new CryptographyClient(key.id!, credential);

// ✅ Correct - from URL
const cryptoClient = new CryptographyClient(
  `https://${vaultName}.vault.azure.net/keys/MyKey`,
  credential
);
```

### Encrypt/Decrypt

```typescript
// ✅ Correct - object parameter style
const encryptResult = await cryptoClient.encrypt({
  algorithm: "RSA1_5",
  plaintext: Buffer.from("My Message"),
});

const decryptResult = await cryptoClient.decrypt({
  algorithm: "RSA1_5",
  ciphertext: encryptResult.result,
});

// ❌ Incorrect - positional arguments (old API)
const result = await cryptoClient.encrypt("RSA1_5", Buffer.from("data"));
```

### Sign/Verify

```typescript
import { createHash } from "node:crypto";

// ✅ Correct - sign a digest
const hash = createHash("sha256").update("My Message").digest();
const signResult = await cryptoClient.sign("RS256", hash);

// ✅ Correct - verify signature
const verifyResult = await cryptoClient.verify("RS256", hash, signResult.result);
console.log(verifyResult.result); // boolean
```

### Sign/Verify Data

```typescript
// ✅ Correct - sign data directly
const signResult = await cryptoClient.signData("RS256", Buffer.from("My Message"));

// ✅ Correct - verify data directly
const verifyResult = await cryptoClient.verifyData("RS256", Buffer.from("My Message"), signResult.result);
```

### Wrap/Unwrap Key

```typescript
// ✅ Correct
const wrapResult = await cryptoClient.wrapKey("RSA-OAEP", Buffer.from("My Key"));
const unwrapResult = await cryptoClient.unwrapKey("RSA-OAEP", wrapResult.result);
```

---

## 7. Error Handling

### ✅ MUST

```typescript
import { RestError } from "@azure/core-rest-pipeline";

try {
  const key = await client.getKey("NonExistent");
} catch (error) {
  if (error instanceof RestError && error.statusCode === 404) {
    console.log("Key not found");
  } else {
    throw error;
  }
}
```

### ❌ MUST NOT

```typescript
// Empty catch blocks
try {
  await client.getKey("key");
} catch (error) {
  // silently ignore
}

// Generic exception handling without specific checks
try {
  await client.getKey("key");
} catch (error) {
  console.log("Error");
}
```

---

## 8. Environment Variables

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
```

---

## 9. Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| `await client.deleteKey()` | `await client.beginDeleteKey()` with poller |
| `require("@azure/keyvault-keys")` | `import { KeyClient } from "@azure/keyvault-keys"` |
| Hardcoded credentials | Use `DefaultAzureCredential` |
| `new KeyVaultClient()` | `new KeyClient()` |
| Sync operations | All operations are async - use `await` |
| Ignoring poller results | Always await `pollUntilDone()` for LRO |

---

## 10. Type Imports

```typescript
import {
  KeyClient,
  KeyVaultKey,
  KeyProperties,
  DeletedKey,
  CryptographyClient,
  JsonWebKey,
  CreateKeyOptions,
  CreateRsaKeyOptions,
  CreateEcKeyOptions,
  KeyRotationPolicy,
} from "@azure/keyvault-keys";
```

---

## References

- [Official SDK README](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/keyvault/keyvault-keys)
- [API Reference](https://learn.microsoft.com/javascript/api/@azure/keyvault-keys)
- [Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/keyvault/keyvault-keys/samples)
