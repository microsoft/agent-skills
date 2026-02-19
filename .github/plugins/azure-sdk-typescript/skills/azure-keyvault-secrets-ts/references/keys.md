# Keys Reference

Cryptographic key management and operations using @azure/keyvault-keys SDK.

## Overview

The Key Vault Keys SDK provides two main clients:
- **KeyClient** - CRUD operations for keys (create, get, list, rotate, delete)
- **CryptographyClient** - Cryptographic operations using keys (encrypt, decrypt, sign, verify, wrap, unwrap)

## Core Types

```typescript
import {
  KeyClient,
  CryptographyClient,
  KeyVaultKey,
  KeyProperties,
  DeletedKey,
  KeyRotationPolicy,
  KeyRotationPolicyProperties,
  KeyRotationLifetimeAction,
  CreateKeyOptions,
  CreateRsaKeyOptions,
  CreateEcKeyOptions,
  EncryptParameters,
  DecryptParameters,
  SignResult,
  VerifyResult,
  WrapResult,
  UnwrapResult,
  KnownEncryptionAlgorithms,
  KnownSignatureAlgorithms,
  KnownKeyTypes,
  KnownKeyCurveNames
} from "@azure/keyvault-keys";
```

## KeyClient Initialization

```typescript
import { KeyClient } from "@azure/keyvault-keys";
import { DefaultAzureCredential } from "@azure/identity";

const vaultUrl = `https://${process.env.AZURE_KEYVAULT_NAME}.vault.azure.net`;
const credential = new DefaultAzureCredential();

const keyClient = new KeyClient(vaultUrl, credential);
```

## Creating Keys

### RSA Keys

```typescript
// Basic RSA key (default 2048-bit)
const rsaKey = await keyClient.createRsaKey("my-rsa-key");

// RSA key with specific size
const rsaKey2048 = await keyClient.createRsaKey("my-rsa-2048", {
  keySize: 2048
});

const rsaKey4096 = await keyClient.createRsaKey("my-rsa-4096", {
  keySize: 4096
});

// RSA-HSM (Hardware Security Module backed)
const rsaHsmKey = await keyClient.createRsaKey("my-rsa-hsm", {
  keySize: 2048,
  hsm: true  // Requires Premium vault
});
```

### Elliptic Curve Keys

```typescript
// P-256 curve (default)
const ecKey = await keyClient.createEcKey("my-ec-key");

// Specific curves
const ecKeyP256 = await keyClient.createEcKey("my-ec-p256", {
  curve: "P-256"
});

const ecKeyP384 = await keyClient.createEcKey("my-ec-p384", {
  curve: "P-384"
});

const ecKeyP521 = await keyClient.createEcKey("my-ec-p521", {
  curve: "P-521"
});

// EC-HSM
const ecHsmKey = await keyClient.createEcKey("my-ec-hsm", {
  curve: "P-256",
  hsm: true
});
```

### Oct Keys (Symmetric)

```typescript
// Symmetric key for wrap/unwrap operations
const octKey = await keyClient.createOctKey("my-oct-key", {
  keySize: 256  // 128, 192, or 256 bits
});

// Oct-HSM
const octHsmKey = await keyClient.createOctKey("my-oct-hsm", {
  keySize: 256,
  hsm: true
});
```

### Generic Create with Options

```typescript
const key = await keyClient.createKey("my-key", "RSA", {
  keySize: 2048,
  enabled: true,
  expiresOn: new Date("2025-12-31"),
  notBefore: new Date("2024-01-01"),
  tags: {
    environment: "production",
    application: "my-app"
  },
  keyOps: ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"],
  exportable: false,
  releasePolicy: undefined  // For Managed HSM key release
});
```

## Key Operations

### Get Key

```typescript
// Get latest version
const key = await keyClient.getKey("my-key");
console.log(`Key: ${key.name}, Type: ${key.keyType}, ID: ${key.id}`);

// Get specific version
const keyVersion = await keyClient.getKey("my-key", {
  version: "abc123..."
});
```

### List Keys

```typescript
// List all keys (properties only, not key material)
for await (const keyProperties of keyClient.listPropertiesOfKeys()) {
  console.log(`Key: ${keyProperties.name}, Created: ${keyProperties.createdOn}`);
}

// List all versions of a key
for await (const version of keyClient.listPropertiesOfKeyVersions("my-key")) {
  console.log(`Version: ${version.version}, Enabled: ${version.enabled}`);
}

// List deleted keys (soft-delete enabled vaults)
for await (const deletedKey of keyClient.listDeletedKeys()) {
  console.log(`Deleted: ${deletedKey.name}, Scheduled purge: ${deletedKey.scheduledPurgeDate}`);
}
```

### Update Key Properties

```typescript
const updated = await keyClient.updateKeyProperties("my-key", {
  enabled: false,
  expiresOn: new Date("2026-12-31"),
  tags: { status: "deprecated" }
});

// Update specific version
const updatedVersion = await keyClient.updateKeyProperties("my-key", "version-id", {
  enabled: true
});
```

### Import Key

```typescript
import { JsonWebKey } from "@azure/keyvault-keys";

// Import existing key material
const jwk: JsonWebKey = {
  kty: "RSA",
  n: Buffer.from("...modulus..."),
  e: Buffer.from("...exponent..."),
  d: Buffer.from("...private exponent..."),  // Optional for public key
  // ... other RSA parameters
};

const importedKey = await keyClient.importKey("imported-key", jwk, {
  hardwareProtected: false  // true for HSM
});
```

## Key Rotation

### Manual Rotation

```typescript
// Creates new version, previous versions remain valid
const rotatedKey = await keyClient.rotateKey("my-key");
console.log(`New version: ${rotatedKey.properties.version}`);
```

### Rotation Policy

```typescript
// Get current policy
const policy = await keyClient.getKeyRotationPolicy("my-key");

// Update rotation policy
const updatedPolicy = await keyClient.updateKeyRotationPolicy("my-key", {
  expiresIn: "P90D",  // ISO 8601 duration - key expires 90 days after creation
  lifetimeActions: [
    {
      action: "Rotate",
      timeAfterCreate: "P30D"  // Auto-rotate 30 days after creation
    },
    {
      action: "Notify",
      timeBeforeExpiry: "P7D"  // Notify 7 days before expiry
    }
  ]
});

// Rotation policy with multiple actions
const complexPolicy = await keyClient.updateKeyRotationPolicy("my-key", {
  expiresIn: "P1Y",  // 1 year
  lifetimeActions: [
    { action: "Rotate", timeAfterCreate: "P90D" },  // Rotate every 90 days
    { action: "Notify", timeBeforeExpiry: "P30D" }  // Notify 30 days before expiry
  ]
});
```

### ISO 8601 Duration Format

| Duration | Meaning |
|----------|---------|
| `P30D` | 30 days |
| `P90D` | 90 days |
| `P1Y` | 1 year |
| `P6M` | 6 months |
| `P1Y6M` | 1 year 6 months |

## Key Deletion and Recovery

### Soft Delete (Default)

```typescript
// Begin delete (returns poller for long-running operation)
const deletePoller = await keyClient.beginDeleteKey("my-key");

// Wait for deletion to complete
const deletedKey = await deletePoller.pollUntilDone();
console.log(`Deleted: ${deletedKey.name}, Recovery ID: ${deletedKey.recoveryId}`);

// Get deleted key info
const deleted = await keyClient.getDeletedKey("my-key");

// Recover deleted key
const recoverPoller = await keyClient.beginRecoverDeletedKey("my-key");
const recoveredKey = await recoverPoller.pollUntilDone();

// Permanently delete (purge) - irreversible
await keyClient.purgeDeletedKey("my-key");
```

### Immediate Deletion (Non-blocking)

```typescript
// Start deletion without waiting
const poller = await keyClient.beginDeleteKey("my-key");

// Check status periodically
while (!poller.isDone()) {
  await poller.poll();
  console.log(`State: ${poller.getOperationState().status}`);
  await new Promise(resolve => setTimeout(resolve, 1000));
}
```

## CryptographyClient

### Initialization

```typescript
import { CryptographyClient } from "@azure/keyvault-keys";

// From KeyVaultKey object
const key = await keyClient.getKey("my-key");
const cryptoClient = new CryptographyClient(key, credential);

// From key ID (URL)
const cryptoClientFromId = new CryptographyClient(
  "https://my-vault.vault.azure.net/keys/my-key/version",
  credential
);

// From key ID without version (uses latest)
const cryptoClientLatest = new CryptographyClient(
  "https://my-vault.vault.azure.net/keys/my-key",
  credential
);
```

### Encrypt / Decrypt

```typescript
// RSA encryption
const plaintext = Buffer.from("Secret message");

// Encrypt with RSA-OAEP
const encryptResult = await cryptoClient.encrypt({
  algorithm: "RSA-OAEP",
  plaintext
});

console.log(`Encrypted (${encryptResult.result.length} bytes)`);

// Decrypt
const decryptResult = await cryptoClient.decrypt({
  algorithm: "RSA-OAEP",
  ciphertext: encryptResult.result
});

console.log(`Decrypted: ${decryptResult.result.toString()}`);
```

### Encryption Algorithms

| Algorithm | Key Type | Description |
|-----------|----------|-------------|
| `RSA1_5` | RSA | RSA with PKCS#1 v1.5 padding |
| `RSA-OAEP` | RSA | RSA with OAEP padding (SHA-1) |
| `RSA-OAEP-256` | RSA | RSA with OAEP padding (SHA-256) |
| `A128GCM` | oct | AES-128-GCM |
| `A192GCM` | oct | AES-192-GCM |
| `A256GCM` | oct | AES-256-GCM |
| `A128CBC` | oct | AES-128-CBC |
| `A192CBC` | oct | AES-192-CBC |
| `A256CBC` | oct | AES-256-CBC |

### Sign / Verify

```typescript
import { createHash } from "node:crypto";

// Create SHA-256 hash of data to sign
const data = Buffer.from("Data to sign");
const hash = createHash("sha256").update(data).digest();

// Sign with RSA key
const signResult = await cryptoClient.sign("RS256", hash);
console.log(`Signature (${signResult.result.length} bytes)`);

// Verify signature
const verifyResult = await cryptoClient.verify("RS256", hash, signResult.result);
console.log(`Valid: ${verifyResult.result}`);

// Sign data directly (SDK computes hash)
const signDataResult = await cryptoClient.signData("RS256", data);
const verifyDataResult = await cryptoClient.verifyData("RS256", data, signDataResult.result);
```

### Signature Algorithms

| Algorithm | Key Type | Hash | Description |
|-----------|----------|------|-------------|
| `RS256` | RSA | SHA-256 | RSASSA-PKCS1-v1_5 |
| `RS384` | RSA | SHA-384 | RSASSA-PKCS1-v1_5 |
| `RS512` | RSA | SHA-512 | RSASSA-PKCS1-v1_5 |
| `PS256` | RSA | SHA-256 | RSASSA-PSS |
| `PS384` | RSA | SHA-384 | RSASSA-PSS |
| `PS512` | RSA | SHA-512 | RSASSA-PSS |
| `ES256` | EC P-256 | SHA-256 | ECDSA |
| `ES384` | EC P-384 | SHA-384 | ECDSA |
| `ES512` | EC P-521 | SHA-512 | ECDSA |

### Wrap / Unwrap Keys

```typescript
// Key encryption key (KEK) wraps another key
const keyMaterial = Buffer.from("32-byte-key-material-here!!!!!");  // 32 bytes for AES-256

// Wrap (encrypt) the key material
const wrapResult = await cryptoClient.wrapKey("RSA-OAEP", keyMaterial);
console.log(`Wrapped key (${wrapResult.result.length} bytes)`);

// Unwrap (decrypt) the key material
const unwrapResult = await cryptoClient.unwrapKey("RSA-OAEP", wrapResult.result);
console.log(`Unwrapped: ${unwrapResult.result.length} bytes`);
```

## Backup and Restore

```typescript
// Backup key (returns encrypted blob)
const backup = await keyClient.backupKey("my-key");
if (backup) {
  // Store backup securely (e.g., blob storage)
  console.log(`Backup size: ${backup.length} bytes`);
}

// Restore key (can restore to different vault in same region/subscription)
const restoredKey = await keyClient.restoreKeyBackup(backup!);
console.log(`Restored: ${restoredKey.name}`);
```

## Error Handling

```typescript
import { RestError } from "@azure/core-rest-pipeline";

try {
  const key = await keyClient.getKey("non-existent-key");
} catch (error) {
  if (error instanceof RestError) {
    switch (error.statusCode) {
      case 404:
        console.log("Key not found");
        break;
      case 403:
        console.log("Access denied - check RBAC permissions");
        break;
      case 409:
        console.log("Conflict - key already exists or is being deleted");
        break;
      default:
        console.log(`Error ${error.statusCode}: ${error.message}`);
    }
  }
  throw error;
}
```

## Best Practices

1. **Use managed identity in production** - DefaultAzureCredential handles this automatically
2. **Enable soft-delete and purge protection** - Required for production vaults
3. **Set key expiration** - Use `expiresOn` to enforce key lifecycle
4. **Use rotation policies** - Automate key rotation for security compliance
5. **Limit key operations** - Only grant needed operations (`keyOps`)
6. **Use HSM for sensitive keys** - Hardware protection for critical cryptographic material
7. **Backup keys before deletion** - Soft-delete has retention limits
8. **Use specific key versions** - Pin to versions in production for stability

## See Also

- [secrets.md](./secrets.md) - Secret management operations
