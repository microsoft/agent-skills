# Azure Identity Java SDK Acceptance Criteria

**SDK**: `com.azure:azure-identity`
**Repository**: https://github.com/Azure/azure-sdk-for-java
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. DefaultAzureCredential (Recommended)

### ✅ CORRECT: Basic DefaultAzureCredential

```java
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;

DefaultAzureCredential credential = new DefaultAzureCredentialBuilder().build();

// Use with any Azure client
BlobServiceClient blobClient = new BlobServiceClientBuilder()
    .endpoint("https://mystorageaccount.blob.core.windows.net")
    .credential(credential)
    .buildClient();

KeyClient keyClient = new KeyClientBuilder()
    .vaultUrl("https://myvault.vault.azure.net")
    .credential(credential)
    .buildClient();
```

### ✅ CORRECT: Configured DefaultAzureCredential

```java
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder()
    .managedIdentityClientId(System.getenv("AZURE_CLIENT_ID"))  // User-assigned MI
    .tenantId(System.getenv("AZURE_TENANT_ID"))
    .build();
```

### ✅ CORRECT: Excluding Credential Types

```java
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder()
    .excludeEnvironmentCredential()   // Skip env vars
    .excludeAzureCliCredential()      // Skip Azure CLI
    .excludeAzurePowerShellCredential()
    .build();
```

### ❌ INCORRECT: Using Hardcoded Credentials

```java
// WRONG - use DefaultAzureCredential or environment variables
ClientSecretCredential credential = new ClientSecretCredentialBuilder()
    .tenantId("12345678-1234-1234-1234-123456789012")
    .clientId("87654321-4321-4321-4321-210987654321")
    .clientSecret("mySecretValue123!")  // NEVER hardcode secrets
    .build();
```

---

## 2. ManagedIdentityCredential

### ✅ CORRECT: System-Assigned Managed Identity

```java
import com.azure.identity.ManagedIdentityCredential;
import com.azure.identity.ManagedIdentityCredentialBuilder;

ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder()
    .build();

CosmosClient cosmosClient = new CosmosClientBuilder()
    .endpoint(System.getenv("COSMOS_ENDPOINT"))
    .credential(credential)
    .buildClient();
```

### ✅ CORRECT: User-Assigned Managed Identity by Client ID

```java
ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder()
    .clientId(System.getenv("AZURE_CLIENT_ID"))
    .build();
```

### ✅ CORRECT: User-Assigned Managed Identity by Resource ID

```java
ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder()
    .resourceId("/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<name>")
    .build();
```

### ❌ INCORRECT: Both Client ID and Resource ID

```java
// WRONG - specify only one identifier
ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder()
    .clientId("client-id")
    .resourceId("resource-id")  // Conflict
    .build();
```

---

## 3. ClientSecretCredential (Service Principal)

### ✅ CORRECT: Service Principal from Environment

```java
import com.azure.identity.ClientSecretCredential;
import com.azure.identity.ClientSecretCredentialBuilder;

ClientSecretCredential credential = new ClientSecretCredentialBuilder()
    .tenantId(System.getenv("AZURE_TENANT_ID"))
    .clientId(System.getenv("AZURE_CLIENT_ID"))
    .clientSecret(System.getenv("AZURE_CLIENT_SECRET"))
    .build();
```

### ❌ INCORRECT: Hardcoded Secret

```java
// WRONG - secrets must come from environment or Key Vault
ClientSecretCredential credential = new ClientSecretCredentialBuilder()
    .tenantId("tenant-id")
    .clientId("client-id")
    .clientSecret("hardcoded-secret-value")  // Security risk
    .build();
```

---

## 4. ClientCertificateCredential

### ✅ CORRECT: Certificate from PEM File

```java
import com.azure.identity.ClientCertificateCredential;
import com.azure.identity.ClientCertificateCredentialBuilder;

ClientCertificateCredential credential = new ClientCertificateCredentialBuilder()
    .tenantId(System.getenv("AZURE_TENANT_ID"))
    .clientId(System.getenv("AZURE_CLIENT_ID"))
    .pemCertificate(System.getenv("AZURE_CLIENT_CERTIFICATE_PATH"))
    .build();
```

### ✅ CORRECT: Certificate with SNI (Certificate Chain)

```java
ClientCertificateCredential credential = new ClientCertificateCredentialBuilder()
    .tenantId(System.getenv("AZURE_TENANT_ID"))
    .clientId(System.getenv("AZURE_CLIENT_ID"))
    .pemCertificate(System.getenv("AZURE_CLIENT_CERTIFICATE_PATH"))
    .sendCertificateChain(true)
    .build();
```

### ✅ CORRECT: PFX Certificate with Password

```java
ClientCertificateCredential credential = new ClientCertificateCredentialBuilder()
    .tenantId(System.getenv("AZURE_TENANT_ID"))
    .clientId(System.getenv("AZURE_CLIENT_ID"))
    .pfxCertificate(System.getenv("AZURE_CLIENT_CERTIFICATE_PATH"),
                    System.getenv("AZURE_CLIENT_CERTIFICATE_PASSWORD"))
    .build();
```

---

## 5. EnvironmentCredential

### ✅ CORRECT: EnvironmentCredential with Proper Env Vars

```java
import com.azure.identity.EnvironmentCredential;
import com.azure.identity.EnvironmentCredentialBuilder;

// Requires AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
EnvironmentCredential credential = new EnvironmentCredentialBuilder().build();
```

### Environment Variables for Service Principal with Secret:
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>
```

### Environment Variables for Service Principal with Certificate:
```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_CERTIFICATE_PATH=/path/to/cert.pem
AZURE_CLIENT_CERTIFICATE_PASSWORD=<optional-password>
```

---

## 6. ChainedTokenCredential

### ✅ CORRECT: Custom Credential Chain

```java
import com.azure.identity.ChainedTokenCredential;
import com.azure.identity.ChainedTokenCredentialBuilder;

ChainedTokenCredential credential = new ChainedTokenCredentialBuilder()
    .addFirst(new ManagedIdentityCredentialBuilder().build())
    .addLast(new AzureCliCredentialBuilder().build())
    .build();
```

### ✅ CORRECT: Production-Ready Chain

```java
ChainedTokenCredential credential = new ChainedTokenCredentialBuilder()
    .addFirst(new ManagedIdentityCredentialBuilder()
        .clientId(System.getenv("AZURE_CLIENT_ID"))
        .build())
    .addLast(new EnvironmentCredentialBuilder().build())
    .addLast(new AzureCliCredentialBuilder().build())
    .build();
```

---

## 7. WorkloadIdentityCredential (AKS)

### ✅ CORRECT: Workload Identity for AKS

```java
import com.azure.identity.WorkloadIdentityCredential;
import com.azure.identity.WorkloadIdentityCredentialBuilder;

// Reads from AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_FEDERATED_TOKEN_FILE
WorkloadIdentityCredential credential = new WorkloadIdentityCredentialBuilder().build();
```

### ✅ CORRECT: Explicit Workload Identity Configuration

```java
WorkloadIdentityCredential credential = new WorkloadIdentityCredentialBuilder()
    .tenantId(System.getenv("AZURE_TENANT_ID"))
    .clientId(System.getenv("AZURE_CLIENT_ID"))
    .tokenFilePath("/var/run/secrets/azure/tokens/azure-identity-token")
    .build();
```

---

## 8. AzureCliCredential (Local Development)

### ✅ CORRECT: Azure CLI for Development

```java
import com.azure.identity.AzureCliCredential;
import com.azure.identity.AzureCliCredentialBuilder;

// Requires `az login` to be run first
AzureCliCredential credential = new AzureCliCredentialBuilder()
    .tenantId(System.getenv("AZURE_TENANT_ID"))  // Optional
    .build();
```

---

## 9. Interactive Credentials

### ✅ CORRECT: Interactive Browser Login

```java
import com.azure.identity.InteractiveBrowserCredential;
import com.azure.identity.InteractiveBrowserCredentialBuilder;

InteractiveBrowserCredential credential = new InteractiveBrowserCredentialBuilder()
    .clientId(System.getenv("AZURE_CLIENT_ID"))
    .redirectUrl("http://localhost:8080")
    .build();
```

### ✅ CORRECT: Device Code Flow

```java
import com.azure.identity.DeviceCodeCredential;
import com.azure.identity.DeviceCodeCredentialBuilder;

DeviceCodeCredential credential = new DeviceCodeCredentialBuilder()
    .clientId(System.getenv("AZURE_CLIENT_ID"))
    .challengeConsumer(challenge -> {
        System.out.println(challenge.getMessage());
        // "To sign in, use a web browser to open the page https://microsoft.com/devicelogin
        //  and enter the code XXXXXX to authenticate."
    })
    .build();
```

---

## 10. Sovereign Clouds

### ✅ CORRECT: Azure Government

```java
import com.azure.identity.AzureAuthorityHosts;

DefaultAzureCredential credential = new DefaultAzureCredentialBuilder()
    .authorityHost(AzureAuthorityHosts.AZURE_GOVERNMENT)
    .build();
```

### ✅ CORRECT: Azure China

```java
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder()
    .authorityHost(AzureAuthorityHosts.AZURE_CHINA)
    .build();
```

---

## 11. Error Handling

### ✅ CORRECT: Handling Authentication Errors

```java
import com.azure.identity.CredentialUnavailableException;
import com.azure.core.exception.ClientAuthenticationException;
import com.azure.core.credential.AccessToken;
import com.azure.core.credential.TokenRequestContext;

try {
    DefaultAzureCredential credential = new DefaultAzureCredentialBuilder().build();
    AccessToken token = credential.getToken(new TokenRequestContext()
        .addScopes("https://management.azure.com/.default"));

    System.out.println("Token acquired, expires: " + token.getExpiresAt());

} catch (CredentialUnavailableException e) {
    System.err.println("No credential could authenticate: " + e.getMessage());
} catch (ClientAuthenticationException e) {
    System.err.println("Authentication failed: " + e.getMessage());
}
```

### ❌ INCORRECT: Catching Generic Exception

```java
// WRONG - loses specific error information
try {
    credential.getToken(context);
} catch (Exception e) {
    System.out.println("Error: " + e.getMessage());
}
```

---

## 12. Logging and Debugging

### ✅ CORRECT: Enable Logging

```java
// Via environment variable
// AZURE_LOG_LEVEL=verbose

// Or programmatically
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder()
    .enableAccountIdentifierLogging()  // Log account info for debugging
    .build();
```

---

## Credential Selection Matrix

| Environment | Recommended Credential |
|-------------|----------------------|
| Local Development | `DefaultAzureCredential` (uses Azure CLI) |
| Azure App Service | `DefaultAzureCredential` (uses Managed Identity) |
| Azure Functions | `DefaultAzureCredential` (uses Managed Identity) |
| Azure Kubernetes Service | `WorkloadIdentityCredential` |
| Azure VMs | `DefaultAzureCredential` (uses Managed Identity) |
| CI/CD Pipeline | `EnvironmentCredential` |
| Desktop Application | `InteractiveBrowserCredential` |
| CLI Tool | `DeviceCodeCredential` |
