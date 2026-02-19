# @azure/storage-blob - SAS Token Patterns

Reference documentation for generating Shared Access Signatures (SAS) in the Azure Blob Storage TypeScript SDK.

**Source**: [Azure SDK for JS - storage-blob](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/storage/storage-blob)

---

## Installation

```bash
npm install @azure/storage-blob @azure/identity
```

---

## SAS Types Overview

| SAS Type | Scope | Use Case |
|----------|-------|----------|
| **Service SAS** | Single blob or container | Grant access to specific resources |
| **Account SAS** | Entire storage account | Grant broad access to multiple services |
| **User Delegation SAS** | Single blob or container | Most secure, uses Entra ID credentials |

---

## User Delegation SAS (Recommended)

Most secure option—uses Entra ID credentials instead of account keys.

### Generate User Delegation Key

```typescript
import {
  BlobServiceClient,
  generateBlobSASQueryParameters,
  BlobSASPermissions,
  SASProtocol,
} from "@azure/storage-blob";
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();
const blobServiceClient = new BlobServiceClient(
  `https://${accountName}.blob.core.windows.net`,
  credential
);

// Get user delegation key (valid for up to 7 days)
const startsOn = new Date();
const expiresOn = new Date(startsOn.valueOf() + 3600 * 1000); // 1 hour

const userDelegationKey = await blobServiceClient.getUserDelegationKey(
  startsOn,
  expiresOn
);
```

### Generate User Delegation SAS for Blob

```typescript
const containerName = "my-container";
const blobName = "my-blob.txt";

const sasToken = generateBlobSASQueryParameters(
  {
    containerName,
    blobName,
    permissions: BlobSASPermissions.parse("r"), // read only
    startsOn,
    expiresOn,
    protocol: SASProtocol.Https,
  },
  userDelegationKey,
  accountName
).toString();

const sasUrl = `https://${accountName}.blob.core.windows.net/${containerName}/${blobName}?${sasToken}`;
console.log("SAS URL:", sasUrl);
```

---

## Service SAS (Account Key)

Uses storage account key. Less secure but simpler for some scenarios.

### Generate Blob SAS

```typescript
import {
  BlobServiceClient,
  generateBlobSASQueryParameters,
  BlobSASPermissions,
  StorageSharedKeyCredential,
} from "@azure/storage-blob";

const accountName = process.env["STORAGE_ACCOUNT_NAME"]!;
const accountKey = process.env["STORAGE_ACCOUNT_KEY"]!;

const sharedKeyCredential = new StorageSharedKeyCredential(
  accountName,
  accountKey
);

const sasToken = generateBlobSASQueryParameters(
  {
    containerName: "my-container",
    blobName: "my-blob.txt",
    permissions: BlobSASPermissions.parse("racwd"), // read, add, create, write, delete
    startsOn: new Date(),
    expiresOn: new Date(Date.now() + 3600 * 1000), // 1 hour
  },
  sharedKeyCredential
).toString();

const sasUrl = `https://${accountName}.blob.core.windows.net/my-container/my-blob.txt?${sasToken}`;
```

### Generate Container SAS

```typescript
import {
  ContainerSASPermissions,
  generateBlobSASQueryParameters,
} from "@azure/storage-blob";

const containerSasToken = generateBlobSASQueryParameters(
  {
    containerName: "my-container",
    permissions: ContainerSASPermissions.parse("rl"), // read, list
    startsOn: new Date(),
    expiresOn: new Date(Date.now() + 86400 * 1000), // 24 hours
  },
  sharedKeyCredential
).toString();

const containerSasUrl = `https://${accountName}.blob.core.windows.net/my-container?${containerSasToken}`;
```

---

## Account SAS

Grants access to multiple services (blob, queue, table, file).

```typescript
import {
  generateAccountSASQueryParameters,
  AccountSASPermissions,
  AccountSASServices,
  AccountSASResourceTypes,
  StorageSharedKeyCredential,
} from "@azure/storage-blob";

const accountSasToken = generateAccountSASQueryParameters(
  {
    services: AccountSASServices.parse("btqf").toString(), // blob, table, queue, file
    resourceTypes: AccountSASResourceTypes.parse("sco").toString(), // service, container, object
    permissions: AccountSASPermissions.parse("rwdlacupi"), // all permissions
    startsOn: new Date(),
    expiresOn: new Date(Date.now() + 3600 * 1000),
    protocol: SASProtocol.Https,
  },
  sharedKeyCredential
).toString();

const accountSasUrl = `https://${accountName}.blob.core.windows.net?${accountSasToken}`;
```

---

## SAS Permissions

### Blob Permissions (`BlobSASPermissions`)

| Permission | Code | Description |
|------------|------|-------------|
| Read | `r` | Read blob content and metadata |
| Add | `a` | Add blocks to append blob |
| Create | `c` | Create new blob |
| Write | `w` | Write to blob |
| Delete | `d` | Delete blob |
| Delete Version | `x` | Delete blob version |
| Tag | `t` | Read/write blob tags |
| Move | `m` | Move blob |
| Execute | `e` | Execute (for DataLake) |
| Set Immutability | `i` | Set immutability policy |
| Permanent Delete | `y` | Permanently delete (soft-deleted) |

```typescript
// Parse from string
const permissions = BlobSASPermissions.parse("rwd");

// Build programmatically
const permissions = new BlobSASPermissions();
permissions.read = true;
permissions.write = true;
permissions.delete = true;
```

### Container Permissions (`ContainerSASPermissions`)

Same as blob permissions, plus:

| Permission | Code | Description |
|------------|------|-------------|
| List | `l` | List blobs in container |

```typescript
const permissions = ContainerSASPermissions.parse("rl"); // read and list
```

### Account Permissions (`AccountSASPermissions`)

| Permission | Code | Description |
|------------|------|-------------|
| Read | `r` | Read |
| Write | `w` | Write |
| Delete | `d` | Delete |
| Delete Version | `x` | Delete version |
| List | `l` | List |
| Add | `a` | Add |
| Create | `c` | Create |
| Update | `u` | Update |
| Process | `p` | Process messages |
| Tag | `t` | Tags |
| Filter | `f` | Filter by tags |
| Set Immutability | `i` | Immutability policy |

---

## SAS Options

### Content Headers

Override response headers:

```typescript
const sasToken = generateBlobSASQueryParameters(
  {
    containerName: "my-container",
    blobName: "document.pdf",
    permissions: BlobSASPermissions.parse("r"),
    expiresOn: new Date(Date.now() + 3600 * 1000),
    
    // Override response headers
    contentDisposition: "attachment; filename=download.pdf",
    contentType: "application/pdf",
    cacheControl: "max-age=3600",
    contentEncoding: "gzip",
    contentLanguage: "en-US",
  },
  sharedKeyCredential
).toString();
```

### IP Restrictions

Restrict SAS to specific IP addresses:

```typescript
const sasToken = generateBlobSASQueryParameters(
  {
    containerName: "my-container",
    blobName: "my-blob.txt",
    permissions: BlobSASPermissions.parse("r"),
    expiresOn: new Date(Date.now() + 3600 * 1000),
    
    // Single IP
    ipRange: { start: "168.1.5.60" },
    
    // IP range
    // ipRange: { start: "168.1.5.60", end: "168.1.5.70" },
  },
  sharedKeyCredential
).toString();
```

### Protocol Restriction

Require HTTPS:

```typescript
import { SASProtocol } from "@azure/storage-blob";

const sasToken = generateBlobSASQueryParameters(
  {
    containerName: "my-container",
    blobName: "my-blob.txt",
    permissions: BlobSASPermissions.parse("r"),
    expiresOn: new Date(Date.now() + 3600 * 1000),
    protocol: SASProtocol.Https, // HTTPS only
    // protocol: SASProtocol.HttpsAndHttp, // Allow both
  },
  sharedKeyCredential
).toString();
```

### Blob Versioning

Access specific blob version or snapshot:

```typescript
const sasToken = generateBlobSASQueryParameters(
  {
    containerName: "my-container",
    blobName: "my-blob.txt",
    permissions: BlobSASPermissions.parse("r"),
    expiresOn: new Date(Date.now() + 3600 * 1000),
    
    // For snapshots
    snapshotTime: "2023-01-15T10:30:00.0000000Z",
    
    // For versions
    // versionId: "2023-01-15T10:30:00.0000000Z",
  },
  sharedKeyCredential
).toString();
```

---

## Using SAS URLs

### Download with SAS

```typescript
// Client-side (browser or Node.js)
const response = await fetch(sasUrl);
const blob = await response.blob();
```

### Upload with SAS (Write Permission)

```typescript
const sasUrlWithWrite = `https://${accountName}.blob.core.windows.net/container/blob.txt?${writeSasToken}`;

await fetch(sasUrlWithWrite, {
  method: "PUT",
  headers: {
    "x-ms-blob-type": "BlockBlob",
    "Content-Type": "text/plain",
  },
  body: "Hello, World!",
});
```

### Create Anonymous Client with SAS

```typescript
import { BlobClient } from "@azure/storage-blob";

// No credential needed - SAS in URL
const blobClient = new BlobClient(sasUrl);
const downloadResponse = await blobClient.download(0);
```

---

## Complete Example

```typescript
import {
  BlobServiceClient,
  generateBlobSASQueryParameters,
  BlobSASPermissions,
  ContainerSASPermissions,
  SASProtocol,
  StorageSharedKeyCredential,
} from "@azure/storage-blob";
import { DefaultAzureCredential } from "@azure/identity";

async function generateSasTokens() {
  const accountName = process.env["STORAGE_ACCOUNT_NAME"]!;
  const accountKey = process.env["STORAGE_ACCOUNT_KEY"]!;
  
  // Method 1: User Delegation SAS (recommended)
  const credential = new DefaultAzureCredential();
  const blobServiceClient = new BlobServiceClient(
    `https://${accountName}.blob.core.windows.net`,
    credential
  );
  
  const startsOn = new Date();
  const expiresOn = new Date(startsOn.valueOf() + 3600 * 1000);
  
  const userDelegationKey = await blobServiceClient.getUserDelegationKey(
    startsOn,
    expiresOn
  );
  
  const userDelegationSas = generateBlobSASQueryParameters(
    {
      containerName: "uploads",
      blobName: "user-file.txt",
      permissions: BlobSASPermissions.parse("r"),
      startsOn,
      expiresOn,
      protocol: SASProtocol.Https,
    },
    userDelegationKey,
    accountName
  ).toString();
  
  console.log("User Delegation SAS URL:");
  console.log(`https://${accountName}.blob.core.windows.net/uploads/user-file.txt?${userDelegationSas}`);
  
  // Method 2: Service SAS with account key
  const sharedKeyCredential = new StorageSharedKeyCredential(
    accountName,
    accountKey
  );
  
  // Read-only SAS for download
  const readSas = generateBlobSASQueryParameters(
    {
      containerName: "public-files",
      blobName: "document.pdf",
      permissions: BlobSASPermissions.parse("r"),
      expiresOn: new Date(Date.now() + 86400 * 1000), // 24 hours
      contentDisposition: "attachment; filename=download.pdf",
      protocol: SASProtocol.Https,
    },
    sharedKeyCredential
  ).toString();
  
  console.log("\nRead SAS URL:");
  console.log(`https://${accountName}.blob.core.windows.net/public-files/document.pdf?${readSas}`);
  
  // Write SAS for upload
  const writeSas = generateBlobSASQueryParameters(
    {
      containerName: "uploads",
      blobName: "new-upload.txt",
      permissions: BlobSASPermissions.parse("cw"), // create, write
      expiresOn: new Date(Date.now() + 3600 * 1000), // 1 hour
      protocol: SASProtocol.Https,
    },
    sharedKeyCredential
  ).toString();
  
  console.log("\nWrite SAS URL:");
  console.log(`https://${accountName}.blob.core.windows.net/uploads/new-upload.txt?${writeSas}`);
  
  // Container list SAS
  const listSas = generateBlobSASQueryParameters(
    {
      containerName: "public-files",
      permissions: ContainerSASPermissions.parse("rl"), // read, list
      expiresOn: new Date(Date.now() + 3600 * 1000),
      protocol: SASProtocol.Https,
    },
    sharedKeyCredential
  ).toString();
  
  console.log("\nContainer List SAS URL:");
  console.log(`https://${accountName}.blob.core.windows.net/public-files?${listSas}`);
}

generateSasTokens().catch(console.error);
```

---

## Best Practices

1. **Prefer User Delegation SAS** - More secure, tied to Entra ID, auditable
2. **Use shortest possible expiry** - Minimize exposure window
3. **Use HTTPS only** - Set `protocol: SASProtocol.Https`
4. **Apply least privilege** - Grant only necessary permissions
5. **Use IP restrictions** - When client IPs are known
6. **Rotate keys regularly** - If using account key SAS
7. **Store SAS securely** - Never expose in client-side code permanently
8. **Set start time** - Prevent "not yet valid" errors due to clock skew
9. **Use stored access policies** - For container-level SAS management

---

## Security Considerations

| Risk | Mitigation |
|------|------------|
| SAS token leaked | Short expiry, IP restrictions, HTTPS only |
| Over-privileged access | Least privilege permissions |
| Account key compromise | Use User Delegation SAS instead |
| Clock skew issues | Set `startsOn` slightly in the past |
| Token reuse | Use unique blob names or short expiry |

---

## See Also

- [Streaming Patterns](./streaming.md) - Upload/download with SAS
- [Official Documentation](https://learn.microsoft.com/azure/storage/common/storage-sas-overview)
