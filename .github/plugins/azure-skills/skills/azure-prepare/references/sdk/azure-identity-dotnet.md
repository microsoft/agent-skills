# Authentication — .NET SDK Quick Reference

> Condensed from **azure-identity-dotnet**. Full patterns (ASP.NET DI,
> sovereign clouds, brokered auth, certificate credentials)
> in the **azure-identity-dotnet** plugin skill if installed.

## Install
dotnet add package Azure.Identity

## Quick Start
```csharp
using Azure.Identity;
var credential = new DefaultAzureCredential();
```

## Best Practices
- Use deterministic credentials in production (ManagedIdentityCredential, not DefaultAzureCredential)
- Reuse credential instances — single instance shared across clients
- Configure retry policies for credential operations
- Enable logging with AzureEventSourceListener for debugging auth issues
