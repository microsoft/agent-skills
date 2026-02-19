# Azure Identity SDK for TypeScript Acceptance Criteria

**SDK**: `@azure/identity`
**Repository**: https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/identity/identity
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 ✅ CORRECT: ESM Imports

```typescript
import { DefaultAzureCredential } from "@azure/identity";
import { 
  ManagedIdentityCredential,
  ClientSecretCredential,
  InteractiveBrowserCredential,
  ChainedTokenCredential,
  AzureCliCredential,
  DeviceCodeCredential,
} from "@azure/identity";
```

### 1.2 ✅ CORRECT: Type Imports

```typescript
import type { TokenCredential, AccessToken, GetTokenOptions } from "@azure/core-auth";
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: CommonJS require

```typescript
// WRONG - Use ESM imports
const { DefaultAzureCredential } = require("@azure/identity");
```

#### ❌ INCORRECT: Wrong package name

```typescript
// WRONG - Package name is @azure/identity, not azure-identity
import { DefaultAzureCredential } from "azure-identity";
```

---

## 2. DefaultAzureCredential

### 2.1 ✅ CORRECT: Basic DefaultAzureCredential

```typescript
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();

// Use with any Azure SDK client
import { BlobServiceClient } from "@azure/storage-blob";
const blobClient = new BlobServiceClient(
  "https://<account>.blob.core.windows.net",
  credential
);
```

### 2.2 ✅ CORRECT: Get Token Directly

```typescript
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();
const token = await credential.getToken("https://management.azure.com/.default");
console.log(token.expiresOnTimestamp);
```

### 2.3 ✅ CORRECT: DefaultAzureCredential with Options

```typescript
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential({
  managedIdentityClientId: "<user-assigned-client-id>",
  tenantId: "<tenant-id>",
});
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded access token

```typescript
// WRONG - Never hardcode access tokens
const token = "eyJ0eXAiOiJKV1QiLCJhbGci...";
```

---

## 3. ManagedIdentityCredential

### 3.1 ✅ CORRECT: System-Assigned Managed Identity

```typescript
import { ManagedIdentityCredential } from "@azure/identity";

const credential = new ManagedIdentityCredential();
```

### 3.2 ✅ CORRECT: User-Assigned Managed Identity (Client ID)

```typescript
import { ManagedIdentityCredential } from "@azure/identity";

const credential = new ManagedIdentityCredential({
  clientId: "<user-assigned-client-id>"
});
```

### 3.3 ✅ CORRECT: User-Assigned Managed Identity (Resource ID)

```typescript
import { ManagedIdentityCredential } from "@azure/identity";

const credential = new ManagedIdentityCredential({
  resourceId: "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<name>"
});
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Passing tenantId to ManagedIdentityCredential

```typescript
// WRONG - ManagedIdentityCredential doesn't accept tenantId
const credential = new ManagedIdentityCredential({
  tenantId: "<tenant-id>"  // This option doesn't exist
});
```

---

## 4. ClientSecretCredential

### 4.1 ✅ CORRECT: Client Secret Auth with Environment Variables

```typescript
import { ClientSecretCredential } from "@azure/identity";

const credential = new ClientSecretCredential(
  process.env.AZURE_TENANT_ID!,
  process.env.AZURE_CLIENT_ID!,
  process.env.AZURE_CLIENT_SECRET!
);
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded secrets

```typescript
// WRONG - Never hardcode secrets
const credential = new ClientSecretCredential(
  "tenant-id",
  "client-id",
  "super-secret-value"  // SECURITY RISK
);
```

---

## 5. ClientCertificateCredential

### 5.1 ✅ CORRECT: Certificate Path

```typescript
import { ClientCertificateCredential } from "@azure/identity";

const credential = new ClientCertificateCredential(
  process.env.AZURE_TENANT_ID!,
  process.env.AZURE_CLIENT_ID!,
  { certificatePath: "/path/to/cert.pem" }
);
```

### 5.2 ✅ CORRECT: Certificate with Password

```typescript
import { ClientCertificateCredential } from "@azure/identity";

const credential = new ClientCertificateCredential(
  process.env.AZURE_TENANT_ID!,
  process.env.AZURE_CLIENT_ID!,
  { 
    certificatePath: "/path/to/cert.pem",
    certificatePassword: process.env.CERTIFICATE_PASSWORD
  }
);
```

---

## 6. Interactive Authentication

### 6.1 ✅ CORRECT: InteractiveBrowserCredential

```typescript
import { InteractiveBrowserCredential } from "@azure/identity";

const credential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  loginHint: "user@example.com"
});
```

### 6.2 ✅ CORRECT: DeviceCodeCredential

```typescript
import { DeviceCodeCredential } from "@azure/identity";

const credential = new DeviceCodeCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  userPromptCallback: (info) => {
    console.log(info.message);
  }
});
```

---

## 7. ChainedTokenCredential

### 7.1 ✅ CORRECT: Custom Credential Chain

```typescript
import { 
  ChainedTokenCredential,
  ManagedIdentityCredential,
  AzureCliCredential
} from "@azure/identity";

const credential = new ChainedTokenCredential(
  new ManagedIdentityCredential(),
  new AzureCliCredential()
);
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Passing strings instead of credential instances

```typescript
// WRONG - ChainedTokenCredential expects credential instances
const credential = new ChainedTokenCredential(
  "ManagedIdentityCredential",  // WRONG - not a string
  "AzureCliCredential"          // WRONG - not a string
);
```

---

## 8. Developer Credentials

### 8.1 ✅ CORRECT: Azure CLI Credential

```typescript
import { AzureCliCredential } from "@azure/identity";

const credential = new AzureCliCredential();
// Uses: az login
```

### 8.2 ✅ CORRECT: Azure Developer CLI Credential

```typescript
import { AzureDeveloperCliCredential } from "@azure/identity";

const credential = new AzureDeveloperCliCredential();
// Uses: azd auth login
```

### 8.3 ✅ CORRECT: Azure PowerShell Credential

```typescript
import { AzurePowerShellCredential } from "@azure/identity";

const credential = new AzurePowerShellCredential();
// Uses: Connect-AzAccount
```

---

## 9. Sovereign Clouds

### 9.1 ✅ CORRECT: Azure Government

```typescript
import { ClientSecretCredential, AzureAuthorityHosts } from "@azure/identity";

const credential = new ClientSecretCredential(
  process.env.AZURE_TENANT_ID!,
  process.env.AZURE_CLIENT_ID!,
  process.env.AZURE_CLIENT_SECRET!,
  { authorityHost: AzureAuthorityHosts.AzureGovernment }
);
```

### 9.2 ✅ CORRECT: Azure China

```typescript
import { ClientSecretCredential, AzureAuthorityHosts } from "@azure/identity";

const credential = new ClientSecretCredential(
  process.env.AZURE_TENANT_ID!,
  process.env.AZURE_CLIENT_ID!,
  process.env.AZURE_CLIENT_SECRET!,
  { authorityHost: AzureAuthorityHosts.AzureChina }
);
```

---

## 10. Bearer Token Provider

### 10.1 ✅ CORRECT: Get Bearer Token Provider

```typescript
import { DefaultAzureCredential, getBearerTokenProvider } from "@azure/identity";

const credential = new DefaultAzureCredential();
const getAccessToken = getBearerTokenProvider(
  credential,
  "https://cognitiveservices.azure.com/.default"
);

const token = await getAccessToken();
```

---

## 11. Custom Credential Implementation

### 11.1 ✅ CORRECT: Implement TokenCredential Interface

```typescript
import type { TokenCredential, AccessToken, GetTokenOptions } from "@azure/core-auth";

class CustomCredential implements TokenCredential {
  async getToken(
    scopes: string | string[],
    options?: GetTokenOptions
  ): Promise<AccessToken | null> {
    return {
      token: "<access-token>",
      expiresOnTimestamp: Date.now() + 3600000
    };
  }
}
```

---

## 12. Debugging and Logging

### 12.1 ✅ CORRECT: Enable Verbose Logging

```typescript
import { setLogLevel, AzureLogger } from "@azure/logger";

setLogLevel("verbose");

// Custom log handler
AzureLogger.log = (...args) => {
  console.log("[Azure]", ...args);
};
```
