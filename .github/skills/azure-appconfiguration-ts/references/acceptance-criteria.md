# Acceptance Criteria: azure-appconfiguration-ts

## Overview

This document defines the acceptance criteria for code generated using the `@azure/app-configuration` SDK for TypeScript/JavaScript.

**Package:** `@azure/app-configuration`  
**Repository:** https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/appconfiguration/app-configuration

---

## 1. Import Statements

### ✅ MUST

```typescript
// ESM imports
import { AppConfigurationClient } from "@azure/app-configuration";
import { DefaultAzureCredential } from "@azure/identity";
```

### ❌ MUST NOT

```typescript
// CommonJS require
const { AppConfigurationClient } = require("@azure/app-configuration");

// Old package names
import { ConfigurationClient } from "azure-app-configuration";
```

---

## 2. Client Instantiation

### ✅ MUST

```typescript
// With DefaultAzureCredential (recommended)
const credential = new DefaultAzureCredential();
const endpoint = "https://example.azconfig.io";
const client = new AppConfigurationClient(endpoint, credential);

// With connection string
const connectionString = process.env.APPCONFIG_CONNECTION_STRING!;
const client = new AppConfigurationClient(connectionString);
```

### Sovereign Clouds

```typescript
import { KnownAppConfigAudience } from "@azure/app-configuration";

const client = new AppConfigurationClient(endpoint, credential, {
  audience: KnownAppConfigAudience.AzureChina,
});
```

### ❌ MUST NOT

```typescript
// Hardcoded connection strings
const client = new AppConfigurationClient("Endpoint=https://example.azconfig.io;Id=xxx;Secret=yyy");

// Missing credential
const client = new AppConfigurationClient(endpoint);
```

---

## 3. Configuration Setting Operations

### Set Configuration Setting

```typescript
// ✅ Correct - set a setting
const setting = await client.setConfigurationSetting({
  key: "testkey",
  value: "testvalue",
  label: "optional-label",
});

// ✅ Correct - with additional properties
const setting = await client.setConfigurationSetting({
  key: "database/connectionString",
  value: "Server=localhost;Database=mydb",
  label: "production",
  contentType: "application/json",
  tags: { environment: "prod" },
});
```

### Add Configuration Setting (Create Only)

```typescript
// ✅ Correct - fails if setting already exists
const setting = await client.addConfigurationSetting({
  key: "newkey",
  value: "newvalue",
});
```

### Get Configuration Setting

```typescript
// ✅ Correct
const setting = await client.getConfigurationSetting({
  key: "testkey",
  label: "optional-label",
});

console.log(setting.value);
```

### Delete Configuration Setting

```typescript
// ✅ Correct
await client.deleteConfigurationSetting({
  key: "testkey",
  label: "optional-label",
});
```

---

## 4. List Operations

### List Configuration Settings

```typescript
// ✅ Correct - async iteration
for await (const setting of client.listConfigurationSettings({
  keyFilter: "app/*",
  labelFilter: "production",
})) {
  console.log(`${setting.key}: ${setting.value}`);
}

// ✅ Correct - paginated
for await (const page of client.listConfigurationSettings().byPage()) {
  for (const setting of page.items) {
    console.log(setting.key);
  }
}
```

### List Revisions

```typescript
// ✅ Correct
for await (const revision of client.listRevisions({
  keyFilter: "testkey",
})) {
  console.log(`Version: ${revision.etag}, Value: ${revision.value}`);
}
```

---

## 5. Read-Only Settings

### Set Read-Only

```typescript
// ✅ Correct - lock a setting
await client.setReadOnly(setting, true);

// ✅ Correct - unlock a setting
await client.setReadOnly(setting, false);

// ✅ Correct - using setting identifier
await client.setReadOnly({ key: "testkey", label: "prod" }, true);
```

---

## 6. Snapshots

### Create Snapshot

```typescript
// ✅ Correct - using poller
const poller = await client.beginCreateSnapshot({
  name: "testsnapshot",
  retentionPeriod: 2592000, // 30 days in seconds
  filters: [{ keyFilter: "app/*", labelFilter: "production" }],
});
const snapshot = await poller.pollUntilDone();

// ✅ Correct - convenience method
const snapshot = await client.beginCreateSnapshotAndWait({
  name: "testsnapshot",
  retentionPeriod: 2592000,
  filters: [{ keyFilter: "app/*" }],
});
```

### Get Snapshot

```typescript
// ✅ Correct
const snapshot = await client.getSnapshot("testsnapshot");
console.log(snapshot.status);
```

### List Snapshot Settings

```typescript
// ✅ Correct
for await (const setting of client.listConfigurationSettingsForSnapshot("testsnapshot")) {
  console.log(`${setting.key}: ${setting.value}`);
}
```

### List Snapshots

```typescript
// ✅ Correct
for await (const snapshot of client.listSnapshots()) {
  console.log(`Snapshot: ${snapshot.name}, Status: ${snapshot.status}`);
}
```

### Archive/Recover Snapshot

```typescript
// ✅ Correct - archive
const archivedSnapshot = await client.archiveSnapshot("testsnapshot");

// ✅ Correct - recover
const recoveredSnapshot = await client.recoverSnapshot("testsnapshot");
```

---

## 7. Feature Flags

### Set Feature Flag

```typescript
import { featureFlagPrefix, featureFlagContentType } from "@azure/app-configuration";

// ✅ Correct
const featureFlag = await client.setConfigurationSetting({
  key: `${featureFlagPrefix}beta-feature`,
  value: JSON.stringify({
    id: "beta-feature",
    enabled: true,
    conditions: {
      client_filters: [],
    },
  }),
  contentType: featureFlagContentType,
});
```

---

## 8. Secret References

### Set Secret Reference

```typescript
import { secretReferenceContentType } from "@azure/app-configuration";

// ✅ Correct
const secretRef = await client.setConfigurationSetting({
  key: "database/password",
  value: JSON.stringify({
    uri: "https://myvault.vault.azure.net/secrets/db-password",
  }),
  contentType: secretReferenceContentType,
});
```

---

## 9. Conditional Operations (ETags)

### Optimistic Concurrency

```typescript
// ✅ Correct - update only if not modified
const setting = await client.getConfigurationSetting({ key: "testkey" });

try {
  await client.setConfigurationSetting(
    { ...setting, value: "new value" },
    { onlyIfUnchanged: true }
  );
} catch (error) {
  if (error.statusCode === 412) {
    console.log("Setting was modified by another process");
  }
}
```

### Get Only If Changed

```typescript
// ✅ Correct - conditional get
const response = await client.getConfigurationSetting(
  { key: "testkey" },
  { onlyIfChanged: true, etag: lastKnownEtag }
);

if (response.statusCode === 304) {
  console.log("Setting has not changed");
}
```

---

## 10. Error Handling

### ✅ MUST

```typescript
import { RestError } from "@azure/core-rest-pipeline";

try {
  const setting = await client.getConfigurationSetting({ key: "nonexistent" });
} catch (error) {
  if (error instanceof RestError) {
    if (error.statusCode === 404) {
      console.log("Setting not found");
    } else if (error.statusCode === 412) {
      console.log("Precondition failed (etag mismatch)");
    } else {
      console.log(`Error: ${error.message}`);
    }
  } else {
    throw error;
  }
}
```

---

## 11. Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| `require("@azure/app-configuration")` | `import { AppConfigurationClient } from "@azure/app-configuration"` |
| Hardcoded connection strings | Use environment variables or `DefaultAzureCredential` |
| Sync iteration | Use `for await` for all list operations |
| Missing error handling | Handle `RestError` with specific status codes |
| `createSnapshot()` | Use `beginCreateSnapshot()` or `beginCreateSnapshotAndWait()` |

---

## 12. Type Imports

```typescript
import {
  AppConfigurationClient,
  ConfigurationSetting,
  ConfigurationSettingId,
  ConfigurationSnapshot,
  SetConfigurationSettingOptions,
  GetConfigurationSettingOptions,
  ListConfigurationSettingsOptions,
  featureFlagPrefix,
  featureFlagContentType,
  secretReferenceContentType,
  KnownAppConfigAudience,
} from "@azure/app-configuration";
```

---

## References

- [Official SDK README](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/appconfiguration/app-configuration)
- [API Reference](https://learn.microsoft.com/javascript/api/@azure/app-configuration)
- [Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/appconfiguration/app-configuration/samples)
