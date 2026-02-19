# Azure Identity SDK Acceptance Criteria (.NET)

**SDK**: `Azure.Identity`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/identity/Azure.Identity
**Commit**: `main`
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Using Statements

### 1.1 ✅ CORRECT: Core Identity Imports
```csharp
using Azure.Identity;
using Azure.Core;
```

### 1.2 ✅ CORRECT: With Dependency Injection
```csharp
using Azure.Identity;
using Microsoft.Extensions.Azure;
```

### 1.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong namespace
```csharp
// WRONG - Azure.Identity not Microsoft.Azure.Identity
using Microsoft.Azure.Identity;
```

---

## 2. DefaultAzureCredential

### 2.1 ✅ CORRECT: Basic DefaultAzureCredential
```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

var credential = new DefaultAzureCredential();
var client = new SecretClient(new Uri("https://myvault.vault.azure.net"), credential);
```

### 2.2 ✅ CORRECT: Customized DefaultAzureCredential
```csharp
using Azure.Identity;

var credential = new DefaultAzureCredential(
    new DefaultAzureCredentialOptions
    {
        ExcludeEnvironmentCredential = true,
        ExcludeManagedIdentityCredential = false,
        ExcludeVisualStudioCredential = false,
        ExcludeAzureCliCredential = false,
        ExcludeInteractiveBrowserCredential = false,
        TenantId = "<tenant-id>",
        ManagedIdentityClientId = "<user-assigned-mi-client-id>"
    });
```

### 2.3 ✅ CORRECT: ASP.NET Core Dependency Injection
```csharp
using Azure.Identity;
using Microsoft.Extensions.Azure;

builder.Services.AddAzureClients(clientBuilder =>
{
    clientBuilder.AddBlobServiceClient(
        new Uri("https://myaccount.blob.core.windows.net"));
    clientBuilder.AddSecretClient(
        new Uri("https://myvault.vault.azure.net"));
    
    clientBuilder.UseCredential(new DefaultAzureCredential());
});
```

### 2.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded access token
```csharp
// WRONG - never hardcode access tokens
string token = "eyJ0eXAiOiJKV1QiLCJhbGci...";
```

#### ❌ INCORRECT: Not reusing credential instances
```csharp
// WRONG - create credential once and reuse
var blobClient = new BlobServiceClient(uri, new DefaultAzureCredential());
var secretClient = new SecretClient(uri2, new DefaultAzureCredential()); // Creates redundant instance
```

---

## 3. ManagedIdentityCredential

### 3.1 ✅ CORRECT: System-assigned Managed Identity
```csharp
using Azure.Identity;

var credential = new ManagedIdentityCredential(ManagedIdentityId.SystemAssigned);
```

### 3.2 ✅ CORRECT: User-assigned by Client ID
```csharp
using Azure.Identity;

var credential = new ManagedIdentityCredential(
    ManagedIdentityId.FromUserAssignedClientId("<client-id>"));
```

### 3.3 ✅ CORRECT: User-assigned by Resource ID
```csharp
using Azure.Identity;
using Azure.Core;

var credential = new ManagedIdentityCredential(
    ManagedIdentityId.FromUserAssignedResourceId("<resource-id>"));
```

### 3.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using deprecated constructor
```csharp
// WRONG - use ManagedIdentityId instead
var credential = new ManagedIdentityCredential(clientId: "<client-id>");
```

---

## 4. ClientSecretCredential

### 4.1 ✅ CORRECT: Client Secret from Environment
```csharp
using Azure.Identity;

var credential = new ClientSecretCredential(
    tenantId: Environment.GetEnvironmentVariable("AZURE_TENANT_ID"),
    clientId: Environment.GetEnvironmentVariable("AZURE_CLIENT_ID"),
    clientSecret: Environment.GetEnvironmentVariable("AZURE_CLIENT_SECRET"));
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Hardcoded secrets
```csharp
// WRONG - never hardcode secrets
var credential = new ClientSecretCredential(
    tenantId: "my-tenant-id",
    clientId: "my-client-id",
    clientSecret: "super-secret-value");
```

---

## 5. ClientCertificateCredential

### 5.1 ✅ CORRECT: Certificate from File
```csharp
using Azure.Identity;
using System.Security.Cryptography.X509Certificates;

var certificate = X509CertificateLoader.LoadCertificateFromFile("MyCertificate.pfx");
var credential = new ClientCertificateCredential(
    tenantId: "<tenant-id>",
    clientId: "<client-id>",
    certificate);
```

### 5.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using obsolete X509Certificate2 constructor
```csharp
// WRONG - use X509CertificateLoader.LoadCertificateFromFile instead
var certificate = new X509Certificate2("MyCertificate.pfx", "password");
```

---

## 6. ChainedTokenCredential

### 6.1 ✅ CORRECT: Custom Credential Chain
```csharp
using Azure.Identity;

var credential = new ChainedTokenCredential(
    new ManagedIdentityCredential(),
    new AzureCliCredential());

var client = new SecretClient(
    new Uri("https://myvault.vault.azure.net"),
    credential);
```

### 6.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Passing credential types instead of instances
```csharp
// WRONG - ChainedTokenCredential expects credential instances, not types
var credential = new ChainedTokenCredential(
    typeof(ManagedIdentityCredential),
    typeof(AzureCliCredential));
```

---

## 7. Developer Credentials

### 7.1 ✅ CORRECT: Azure CLI Credential
```csharp
using Azure.Identity;

var credential = new AzureCliCredential();
```

### 7.2 ✅ CORRECT: Azure Developer CLI Credential
```csharp
using Azure.Identity;

var credential = new AzureDeveloperCliCredential();
```

### 7.3 ✅ CORRECT: Visual Studio Credential
```csharp
using Azure.Identity;

var credential = new VisualStudioCredential();
```

### 7.4 ✅ CORRECT: Interactive Browser Credential
```csharp
using Azure.Identity;

var credential = new InteractiveBrowserCredential();
```

---

## 8. Sovereign Clouds

### 8.1 ✅ CORRECT: Azure Government
```csharp
using Azure.Identity;

var credential = new DefaultAzureCredential(
    new DefaultAzureCredentialOptions
    {
        AuthorityHost = AzureAuthorityHosts.AzureGovernment
    });
```

### 8.2 ✅ CORRECT: Azure China
```csharp
using Azure.Identity;

var credential = new DefaultAzureCredential(
    new DefaultAzureCredentialOptions
    {
        AuthorityHost = AzureAuthorityHosts.AzureChina
    });
```

---

## 9. Error Handling

### 9.1 ✅ CORRECT: Catching Authentication Errors
```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

var client = new SecretClient(
    new Uri("https://myvault.vault.azure.net"),
    new DefaultAzureCredential());

try
{
    KeyVaultSecret secret = await client.GetSecretAsync("secret1");
}
catch (AuthenticationFailedException e)
{
    Console.WriteLine($"Authentication Failed: {e.Message}");
}
catch (CredentialUnavailableException e)
{
    Console.WriteLine($"Credential Unavailable: {e.Message}");
}
```

### 9.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Swallowing authentication exceptions
```csharp
// WRONG - don't swallow authentication exceptions
try
{
    var secret = await client.GetSecretAsync("secret1");
}
catch (Exception)
{
    // Silent failure
}
```

---

## 10. Environment-Based Credential Selection

### 10.1 ✅ CORRECT: Production vs Development
```csharp
using Azure.Identity;
using Azure.Core;

TokenCredential credential = builder.Environment.IsProduction()
    ? new ManagedIdentityCredential("<client-id>")
    : new DefaultAzureCredential();
```

---

## Key Exceptions

| Exception | Description |
|-----------|-------------|
| `AuthenticationFailedException` | Base exception for authentication errors |
| `CredentialUnavailableException` | Credential cannot authenticate in current environment |
| `AuthenticationRequiredException` | Interactive authentication is required |
