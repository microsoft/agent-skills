# Credential Types Reference

Azure Identity credential types for authenticating to Azure services using the @azure/identity TypeScript SDK.

## Overview

The Azure Identity library provides various credential classes for different authentication scenarios. Choose the right credential based on your environment and security requirements.

## Credential Selection Guide

| Scenario | Recommended Credential |
|----------|------------------------|
| Production (any environment) | `DefaultAzureCredential` |
| Azure VM/App Service | `ManagedIdentityCredential` |
| Service Principal (secret) | `ClientSecretCredential` |
| Service Principal (cert) | `ClientCertificateCredential` |
| Local development | `AzureCliCredential` or `AzureDeveloperCliCredential` |
| Browser application | `InteractiveBrowserCredential` |
| CI/CD pipeline | `ClientSecretCredential` or `WorkloadIdentityCredential` |
| Kubernetes (AKS) | `WorkloadIdentityCredential` |

## DefaultAzureCredential (Recommended)

The most versatile credential - automatically tries multiple authentication methods.

```typescript
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();

// Works in all environments - dev and production
import { BlobServiceClient } from "@azure/storage-blob";
const blobClient = new BlobServiceClient(
  "https://myaccount.blob.core.windows.net",
  credential
);
```

**Credential Chain Order:**
1. `EnvironmentCredential` — Service principal from env vars
2. `WorkloadIdentityCredential` — Kubernetes workload identity
3. `ManagedIdentityCredential` — Azure managed identity
4. `AzureDeveloperCliCredential` — `azd auth login`
5. `AzureCliCredential` — `az login`
6. `AzurePowerShellCredential` — `Connect-AzAccount`

### Customizing DefaultAzureCredential

```typescript
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential({
  // Exclude specific credentials
  excludeAzureCliCredential: true,
  excludeAzurePowerShellCredential: true,
  
  // For user-assigned managed identity
  managedIdentityClientId: "<client-id>",
  
  // Tenant hint for multi-tenant
  tenantId: "<tenant-id>",
});
```

## ManagedIdentityCredential

For Azure-hosted resources (VMs, App Service, Functions, AKS).

```typescript
import { ManagedIdentityCredential } from "@azure/identity";

// System-assigned managed identity
const credential = new ManagedIdentityCredential();

// User-assigned managed identity (by client ID)
const credentialByClientId = new ManagedIdentityCredential({
  clientId: "<user-assigned-client-id>"
});

// User-assigned managed identity (by resource ID)
const credentialByResourceId = new ManagedIdentityCredential({
  resourceId: "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<name>"
});
```

## ClientSecretCredential

For service principal authentication with a client secret.

```typescript
import { ClientSecretCredential } from "@azure/identity";

const credential = new ClientSecretCredential(
  "<tenant-id>",
  "<client-id>",
  "<client-secret>"
);

// From environment variables
const credentialFromEnv = new ClientSecretCredential(
  process.env.AZURE_TENANT_ID!,
  process.env.AZURE_CLIENT_ID!,
  process.env.AZURE_CLIENT_SECRET!
);
```

**Required Environment Variables:**
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>
```

## ClientCertificateCredential

For service principal authentication with a certificate (more secure than secret).

```typescript
import { ClientCertificateCredential } from "@azure/identity";

// Certificate from file path
const credential = new ClientCertificateCredential(
  "<tenant-id>",
  "<client-id>",
  { certificatePath: "/path/to/cert.pem" }
);

// Certificate with password
const credentialWithPassword = new ClientCertificateCredential(
  "<tenant-id>",
  "<client-id>",
  {
    certificatePath: "/path/to/cert.pfx",
    certificatePassword: "<password>"
  }
);

// Certificate from PEM string
const credentialFromString = new ClientCertificateCredential(
  "<tenant-id>",
  "<client-id>",
  { certificate: "-----BEGIN CERTIFICATE-----\n..." }
);
```

## WorkloadIdentityCredential

For Kubernetes workload identity (AKS, Azure Arc).

```typescript
import { WorkloadIdentityCredential } from "@azure/identity";

// Uses environment variables automatically set by AKS
const credential = new WorkloadIdentityCredential();

// Explicit configuration
const credentialExplicit = new WorkloadIdentityCredential({
  tenantId: "<tenant-id>",
  clientId: "<client-id>",
  tokenFilePath: "/var/run/secrets/azure/tokens/azure-identity-token"
});
```

**Required Environment Variables (set by AKS):**
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_FEDERATED_TOKEN_FILE=/var/run/secrets/tokens/azure-identity
```

## Developer Credentials

### AzureCliCredential

```typescript
import { AzureCliCredential } from "@azure/identity";

// Uses token from: az login
const credential = new AzureCliCredential();

// With tenant hint
const credentialWithTenant = new AzureCliCredential({
  tenantId: "<tenant-id>"
});
```

### AzureDeveloperCliCredential

```typescript
import { AzureDeveloperCliCredential } from "@azure/identity";

// Uses token from: azd auth login
const credential = new AzureDeveloperCliCredential();
```

### AzurePowerShellCredential

```typescript
import { AzurePowerShellCredential } from "@azure/identity";

// Uses token from: Connect-AzAccount
const credential = new AzurePowerShellCredential();
```

### VisualStudioCodeCredential

```typescript
import { VisualStudioCodeCredential } from "@azure/identity";

// Uses Azure Account extension in VS Code
const credential = new VisualStudioCodeCredential();
```

## ChainedTokenCredential

Create custom credential chains for specific scenarios.

```typescript
import {
  ChainedTokenCredential,
  ManagedIdentityCredential,
  AzureCliCredential,
  ClientSecretCredential
} from "@azure/identity";

// Try managed identity first, then CLI
const credential = new ChainedTokenCredential(
  new ManagedIdentityCredential(),
  new AzureCliCredential()
);

// Production: managed identity → service principal fallback
const productionCredential = new ChainedTokenCredential(
  new ManagedIdentityCredential(),
  new ClientSecretCredential(
    process.env.AZURE_TENANT_ID!,
    process.env.AZURE_CLIENT_ID!,
    process.env.AZURE_CLIENT_SECRET!
  )
);
```

## EnvironmentCredential

Automatically selects credential based on environment variables.

```typescript
import { EnvironmentCredential } from "@azure/identity";

// Checks env vars and creates appropriate credential
const credential = new EnvironmentCredential();
```

**Supported Environment Variable Sets:**

Service Principal (Secret):
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>
```

Service Principal (Certificate):
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_CERTIFICATE_PATH=/path/to/cert.pem
AZURE_CLIENT_CERTIFICATE_PASSWORD=<optional>
```

Username/Password (not recommended):
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_USERNAME=<username>
AZURE_PASSWORD=<password>
```

## TokenCredential Interface

All credentials implement `TokenCredential`:

```typescript
import type { TokenCredential, AccessToken, GetTokenOptions } from "@azure/core-auth";

interface TokenCredential {
  getToken(
    scopes: string | string[],
    options?: GetTokenOptions
  ): Promise<AccessToken | null>;
}

interface AccessToken {
  token: string;
  expiresOnTimestamp: number;
}
```

### Custom Credential Implementation

```typescript
import type { TokenCredential, AccessToken, GetTokenOptions } from "@azure/core-auth";

class CustomCredential implements TokenCredential {
  async getToken(
    scopes: string | string[],
    options?: GetTokenOptions
  ): Promise<AccessToken | null> {
    // Custom token acquisition logic
    const token = await fetchTokenFromCustomSource(scopes);
    
    return {
      token: token.accessToken,
      expiresOnTimestamp: token.expiresOn.getTime()
    };
  }
}
```

## Sovereign Clouds

```typescript
import { 
  ClientSecretCredential, 
  AzureAuthorityHosts 
} from "@azure/identity";

// Azure Government
const govCredential = new ClientSecretCredential(
  "<tenant>", "<client>", "<secret>",
  { authorityHost: AzureAuthorityHosts.AzureGovernment }
);

// Azure China (21Vianet)
const chinaCredential = new ClientSecretCredential(
  "<tenant>", "<client>", "<secret>",
  { authorityHost: AzureAuthorityHosts.AzureChina }
);

// Available authority hosts
// AzureAuthorityHosts.AzurePublicCloud (default)
// AzureAuthorityHosts.AzureGovernment
// AzureAuthorityHosts.AzureChina
```

## Bearer Token Provider

For APIs that need raw tokens:

```typescript
import { DefaultAzureCredential, getBearerTokenProvider } from "@azure/identity";

const credential = new DefaultAzureCredential();

// Create token provider for specific scope
const getAccessToken = getBearerTokenProvider(
  credential,
  "https://cognitiveservices.azure.com/.default"
);

// Get token when needed
const token = await getAccessToken();
console.log(`Bearer ${token}`);
```

## Debugging

```typescript
import { setLogLevel, AzureLogger } from "@azure/logger";

// Enable verbose logging
setLogLevel("verbose");

// Custom log handler
AzureLogger.log = (...args) => {
  console.log("[Azure Identity]", ...args);
};
```

## Best Practices

1. **Use DefaultAzureCredential** — Works across all environments
2. **Never hardcode credentials** — Use environment variables or managed identity
3. **Prefer managed identity** — No secrets to manage
4. **Use certificates over secrets** — More secure, easier to rotate
5. **Scope user-assigned identity** — Use for multi-tenant or specific permissions
6. **Enable logging for debugging** — Helps diagnose auth issues
7. **Handle token refresh** — Azure SDK handles this automatically

## See Also

- [Browser Authentication Reference](./browser-auth.md)
- [Azure Identity Best Practices](https://learn.microsoft.com/azure/developer/javascript/sdk/authentication/)
- [Managed Identity Overview](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)
