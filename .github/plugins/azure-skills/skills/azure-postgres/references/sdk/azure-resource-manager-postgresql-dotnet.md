# PostgreSQL Management — .NET SDK Quick Reference

> Condensed from **azure-resource-manager-postgresql-dotnet**. Full patterns
> (server creation, firewall rules, HA, backups, parameters, replicas)
> in the **azure-resource-manager-postgresql-dotnet** plugin skill if installed.

## Install
dotnet add package Azure.ResourceManager.PostgreSql
dotnet add package Azure.Identity

## Quick Start
```csharp
using Azure.ResourceManager;
using Azure.Identity;
var armClient = new ArmClient(new DefaultAzureCredential());
```

## Best Practices
- Use Flexible Server — Single Server is deprecated
- Enable zone-redundant HA for production workloads
- Use DefaultAzureCredential — prefer over connection strings
- Configure Entra ID authentication — more secure than SQL auth alone
- Enable both auth methods — Entra ID + password for flexibility
- Set appropriate backup retention — 7-35 days based on compliance
- Use private endpoints for secure network access
- Tune server parameters based on workload characteristics
- Use read replicas for read-heavy workloads
- Stop dev/test servers to save costs when not in use
