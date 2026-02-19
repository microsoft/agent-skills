# Secrets Reference

Secret management operations using @azure/keyvault-secrets SDK.

## Overview

The SecretClient provides operations for managing secrets in Azure Key Vault:
- Create, update, and delete secrets
- List secrets and versions
- Soft-delete and purge operations
- Backup and restore capabilities

## Core Types

```typescript
import {
  SecretClient,
  KeyVaultSecret,
  SecretProperties,
  DeletedSecret,
  SetSecretOptions,
  GetSecretOptions,
  UpdateSecretPropertiesOptions,
  BeginDeleteSecretOptions,
  BeginRecoverDeletedSecretOptions,
  ListPropertiesOfSecretsOptions,
  ListPropertiesOfSecretVersionsOptions,
  ListDeletedSecretsOptions
} from "@azure/keyvault-secrets";
```

## SecretClient Initialization

```typescript
import { SecretClient } from "@azure/keyvault-secrets";
import { DefaultAzureCredential } from "@azure/identity";

const vaultUrl = `https://${process.env.AZURE_KEYVAULT_NAME}.vault.azure.net`;
const credential = new DefaultAzureCredential();

const secretClient = new SecretClient(vaultUrl, credential);
```

## Creating and Updating Secrets

### Set Secret (Create or Update)

```typescript
// Basic secret
const secret = await secretClient.setSecret("MySecret", "secret-value");
console.log(`Secret: ${secret.name}, Version: ${secret.properties.version}`);

// Secret with options
const secretWithOptions = await secretClient.setSecret("MySecret", "secret-value", {
  enabled: true,
  expiresOn: new Date("2025-12-31"),
  notBefore: new Date("2024-01-01"),
  contentType: "text/plain",
  tags: {
    environment: "production",
    application: "my-app",
    owner: "team-a"
  }
});
```

### Content Types

```typescript
// JSON content
const jsonSecret = await secretClient.setSecret(
  "config-secret",
  JSON.stringify({ apiKey: "xyz", endpoint: "https://api.example.com" }),
  { contentType: "application/json" }
);

// Connection string
const connString = await secretClient.setSecret(
  "db-connection",
  "Server=tcp:myserver.database.windows.net;Database=mydb;...",
  { contentType: "text/plain; charset=utf-8" }
);

// Base64 encoded binary
const binarySecret = await secretClient.setSecret(
  "certificate-data",
  Buffer.from(certificateBytes).toString("base64"),
  { contentType: "application/x-pkcs12" }
);
```

### Versioning Behavior

```typescript
// Each setSecret creates a new version
const v1 = await secretClient.setSecret("MySecret", "value-1");
console.log(`Version 1: ${v1.properties.version}`);

const v2 = await secretClient.setSecret("MySecret", "value-2");
console.log(`Version 2: ${v2.properties.version}`);

// v1 still exists and is accessible by version ID
const v1Retrieved = await secretClient.getSecret("MySecret", {
  version: v1.properties.version
});
```

## Retrieving Secrets

### Get Secret

```typescript
// Get latest version
const secret = await secretClient.getSecret("MySecret");
console.log(`Value: ${secret.value}`);
console.log(`Version: ${secret.properties.version}`);
console.log(`Created: ${secret.properties.createdOn}`);

// Get specific version
const specificVersion = await secretClient.getSecret("MySecret", {
  version: "abc123def456..."
});
```

### KeyVaultSecret Structure

```typescript
interface KeyVaultSecret {
  name: string;
  value?: string;  // Only present when retrieved, not in list operations
  properties: SecretProperties;
}

interface SecretProperties {
  id?: string;                    // Full secret identifier URL
  name: string;
  version?: string;
  vaultUrl: string;
  enabled?: boolean;
  notBefore?: Date;
  expiresOn?: Date;
  createdOn?: Date;
  updatedOn?: Date;
  contentType?: string;
  tags?: { [key: string]: string };
  managed?: boolean;              // True if managed by Key Vault (e.g., storage account keys)
  recoverableDays?: number;
  recoveryLevel?: string;
}
```

## Listing Secrets

### List All Secrets

```typescript
// List secret properties (not values - use getSecret for values)
for await (const secretProperties of secretClient.listPropertiesOfSecrets()) {
  console.log(`Secret: ${secretProperties.name}`);
  console.log(`  Enabled: ${secretProperties.enabled}`);
  console.log(`  Content Type: ${secretProperties.contentType}`);
  console.log(`  Tags: ${JSON.stringify(secretProperties.tags)}`);
}
```

### List Secret Versions

```typescript
// List all versions of a specific secret
for await (const version of secretClient.listPropertiesOfSecretVersions("MySecret")) {
  console.log(`Version: ${version.version}`);
  console.log(`  Created: ${version.createdOn}`);
  console.log(`  Enabled: ${version.enabled}`);
  console.log(`  Expires: ${version.expiresOn}`);
}
```

### Collect to Array

```typescript
// Collect all secrets to array
const allSecrets: SecretProperties[] = [];
for await (const secret of secretClient.listPropertiesOfSecrets()) {
  allSecrets.push(secret);
}

// Or use byPage for pagination control
const pages = secretClient.listPropertiesOfSecrets().byPage({ maxPageSize: 25 });
for await (const page of pages) {
  console.log(`Page with ${page.length} secrets`);
}
```

### Filter by Tags

```typescript
// SDK doesn't support server-side filtering, filter client-side
const productionSecrets: SecretProperties[] = [];
for await (const secret of secretClient.listPropertiesOfSecrets()) {
  if (secret.tags?.environment === "production") {
    productionSecrets.push(secret);
  }
}
```

## Updating Secret Properties

```typescript
// Update properties without changing value
const updated = await secretClient.updateSecretProperties("MySecret", "version-id", {
  enabled: false,
  expiresOn: new Date("2026-12-31"),
  tags: { status: "deprecated", deprecatedOn: new Date().toISOString() }
});

// Update latest version (get version first)
const current = await secretClient.getSecret("MySecret");
await secretClient.updateSecretProperties("MySecret", current.properties.version!, {
  enabled: true
});
```

## Soft Delete Operations

### Delete Secret

```typescript
// Begin delete (long-running operation)
const deletePoller = await secretClient.beginDeleteSecret("MySecret");

// Option 1: Wait for completion
const deletedSecret = await deletePoller.pollUntilDone();
console.log(`Deleted: ${deletedSecret.name}`);
console.log(`Scheduled purge: ${deletedSecret.scheduledPurgeDate}`);
console.log(`Deleted on: ${deletedSecret.deletedOn}`);

// Option 2: Non-blocking with periodic checks
const poller = await secretClient.beginDeleteSecret("MySecret");
while (!poller.isDone()) {
  await poller.poll();
  const state = poller.getOperationState();
  console.log(`Delete status: ${state.isStarted ? "in progress" : "pending"}`);
  await new Promise(resolve => setTimeout(resolve, 2000));
}
```

### Get Deleted Secret

```typescript
// Get info about a deleted secret
const deleted = await secretClient.getDeletedSecret("MySecret");
console.log(`Recovery ID: ${deleted.recoveryId}`);
console.log(`Scheduled purge: ${deleted.scheduledPurgeDate}`);
```

### List Deleted Secrets

```typescript
// List all deleted secrets in vault
for await (const deletedSecret of secretClient.listDeletedSecrets()) {
  console.log(`Deleted secret: ${deletedSecret.name}`);
  console.log(`  Deleted on: ${deletedSecret.deletedOn}`);
  console.log(`  Purge date: ${deletedSecret.scheduledPurgeDate}`);
}
```

### Recover Deleted Secret

```typescript
// Recover a soft-deleted secret
const recoverPoller = await secretClient.beginRecoverDeletedSecret("MySecret");
const recoveredSecret = await recoverPoller.pollUntilDone();
console.log(`Recovered: ${recoveredSecret.name}`);
```

### Purge Secret (Permanent Delete)

```typescript
// Permanently delete - IRREVERSIBLE
// Requires "purge" permission in RBAC
await secretClient.purgeDeletedSecret("MySecret");

// Common pattern: delete then purge
const deletePoller = await secretClient.beginDeleteSecret("MySecret");
await deletePoller.pollUntilDone();
await secretClient.purgeDeletedSecret("MySecret");
```

## Backup and Restore

### Backup Secret

```typescript
// Backup returns encrypted blob containing all versions
const backup = await secretClient.backupSecret("MySecret");

if (backup) {
  // Store backup securely (e.g., blob storage, local file)
  console.log(`Backup size: ${backup.length} bytes`);
  
  // Save to file
  import { writeFileSync } from "node:fs";
  writeFileSync("secret-backup.bin", backup);
}
```

### Restore Secret

```typescript
import { readFileSync } from "node:fs";

// Read backup from storage
const backupData = readFileSync("secret-backup.bin");

// Restore to vault (can be different vault in same region/subscription)
const restoredSecret = await secretClient.restoreSecretBackup(backupData);
console.log(`Restored: ${restoredSecret.name}`);
```

### Backup Constraints

| Constraint | Description |
|------------|-------------|
| Same subscription | Backup can only be restored to vault in same Azure subscription |
| Same geography | Target vault must be in same Azure geography |
| All versions | Backup includes all versions of the secret |
| Encrypted | Backup blob is encrypted with Microsoft-managed keys |

## Error Handling

```typescript
import { RestError } from "@azure/core-rest-pipeline";

async function getSecretSafely(name: string): Promise<KeyVaultSecret | null> {
  try {
    return await secretClient.getSecret(name);
  } catch (error) {
    if (error instanceof RestError) {
      switch (error.statusCode) {
        case 404:
          console.log(`Secret '${name}' not found`);
          return null;
        case 403:
          console.log("Access denied - check RBAC permissions");
          throw error;
        case 409:
          console.log("Conflict - secret is being deleted or already exists");
          throw error;
        default:
          console.log(`Error ${error.statusCode}: ${error.message}`);
          throw error;
      }
    }
    throw error;
  }
}
```

### Common Error Codes

| Code | Meaning |
|------|---------|
| 404 | Secret not found (or deleted) |
| 403 | Access denied (RBAC permission missing) |
| 409 | Conflict (secret exists in deleted state) |
| 429 | Rate limited (too many requests) |

## Common Patterns

### Secret Rotation

```typescript
async function rotateSecret(name: string, newValue: string): Promise<KeyVaultSecret> {
  // Get current secret to preserve metadata
  const current = await secretClient.getSecret(name);
  
  // Disable old version
  await secretClient.updateSecretProperties(name, current.properties.version!, {
    enabled: false,
    tags: {
      ...current.properties.tags,
      rotatedOn: new Date().toISOString(),
      status: "rotated"
    }
  });
  
  // Create new version with same settings
  const newSecret = await secretClient.setSecret(name, newValue, {
    enabled: true,
    contentType: current.properties.contentType,
    expiresOn: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000), // 90 days
    tags: {
      ...current.properties.tags,
      status: "active",
      createdOn: new Date().toISOString()
    }
  });
  
  return newSecret;
}
```

### Bulk Secret Operations

```typescript
async function exportAllSecrets(): Promise<Map<string, string>> {
  const secrets = new Map<string, string>();
  
  for await (const properties of secretClient.listPropertiesOfSecrets()) {
    if (properties.enabled) {
      const secret = await secretClient.getSecret(properties.name);
      if (secret.value) {
        secrets.set(properties.name, secret.value);
      }
    }
  }
  
  return secrets;
}

async function importSecrets(secrets: Map<string, string>, tags?: Record<string, string>): Promise<void> {
  for (const [name, value] of secrets) {
    await secretClient.setSecret(name, value, { tags });
    console.log(`Imported: ${name}`);
  }
}
```

### Check Secret Expiration

```typescript
async function getExpiringSecrets(daysThreshold: number = 30): Promise<SecretProperties[]> {
  const expiringSecrets: SecretProperties[] = [];
  const thresholdDate = new Date(Date.now() + daysThreshold * 24 * 60 * 60 * 1000);
  
  for await (const secret of secretClient.listPropertiesOfSecrets()) {
    if (secret.enabled && secret.expiresOn && secret.expiresOn <= thresholdDate) {
      expiringSecrets.push(secret);
    }
  }
  
  return expiringSecrets;
}
```

## Best Practices

1. **Use managed identity** - DefaultAzureCredential handles MI in Azure, dev credentials locally
2. **Set expiration dates** - Enforce secret rotation with `expiresOn`
3. **Use content types** - Helps consumers understand secret format
4. **Tag secrets** - Environment, application, owner for organization
5. **Enable soft-delete** - Required for production vaults (default for new vaults)
6. **Enable purge protection** - Prevents accidental permanent deletion
7. **Backup before rotation** - Backup secrets before making changes
8. **Least privilege** - Grant only needed permissions (Get vs List vs Set)
9. **Monitor expiration** - Alert on secrets expiring within threshold
10. **Avoid storing in code** - Use Key Vault references in App Service/Functions

## RBAC Permissions

| Operation | Required Permission |
|-----------|---------------------|
| Get secret | `Microsoft.KeyVault/vaults/secrets/getSecret/action` |
| List secrets | `Microsoft.KeyVault/vaults/secrets/readMetadata/action` |
| Set secret | `Microsoft.KeyVault/vaults/secrets/setSecret/action` |
| Delete secret | `Microsoft.KeyVault/vaults/secrets/delete` |
| Purge secret | `Microsoft.KeyVault/vaults/secrets/purge/action` |
| Backup | `Microsoft.KeyVault/vaults/secrets/backup/action` |
| Restore | `Microsoft.KeyVault/vaults/secrets/restore/action` |

## See Also

- [keys.md](./keys.md) - Cryptographic key management
