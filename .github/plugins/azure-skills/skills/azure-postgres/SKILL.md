---
name: azure-postgres
description: Create new Azure Database for PostgreSQL Flexible Server instances and configure passwordless authentication with Microsoft Entra ID. Set up developer access, managed identities for apps, group-based permissions, and migrate from password-based to Entra ID authentication. Trigger phrases include "passwordless for postgres", "entra id postgres", "azure ad postgres authentication", "postgres managed identity", "migrate postgres to passwordless".
---

# Azure Database for PostgreSQL

Configure passwordless authentication with Microsoft Entra ID for existing Azure Database for PostgreSQL Flexible Server. This skill focuses on setting up Entra ID authentication, managing user access, and migrating from password-based authentication.

**Primary use cases:**
- Migrating existing PostgreSQL databases from password to Entra ID authentication
- Setting up developer access with Azure identities
- Configuring managed identity access for Azure-hosted applications
- Managing group-based access control and permissions

---

## MCP Tools (Preferred)

When Azure MCP is enabled, use these tools for PostgreSQL operations:

- `azure__postgres` with command `postgres_server_list` - List PostgreSQL servers
- `azure__postgres` with command `postgres_database_list` - List databases on a server
- `azure__postgres` with command `postgres_database_query` - Execute SQL queries
- `azure__postgres` with command `postgres_server_param_get` - Get server parameters
- `azure__postgres` with command `postgres_server_param_set` - Set server parameters

## CLI Commands (Fallback)

```bash
az postgres flexible-server list --output table
az postgres flexible-server db list --server-name SERVER -g RG
az postgres flexible-server show --name SERVER -g RG
az postgres flexible-server create --name SERVER -g RG --location REGION --admin-user ADMIN --version 16
```

---

## Quick Reference

| Property | Value |
|----------|-------|
| CLI prefix | `az postgres flexible-server` |
| MCP tools | `azure__postgres` |
| Best for | Relational data, PostgreSQL compatibility, PostGIS |
| Engine versions | PostgreSQL 11, 12, 13, 14, 15, 16 (recommended) |

---

## Working with Existing PostgreSQL Servers

This skill primarily focuses on configuring authentication for existing PostgreSQL servers. If you need to reference or create servers, use MCP tools or CLI commands, and provide Azure Portal links for easy access.

**Portal Link Format:**
```
https://portal.azure.com/#@{tenant-domain}/resource/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.DBforPostgreSQL/flexibleServers/{server-name}/overview
```

**Example portal link:**
```
View in Azure Portal:
https://portal.azure.com/#resource/subscriptions/abc123.../resourceGroups/myrg/providers/Microsoft.DBforPostgreSQL/flexibleServers/myserver/overview
```

---

## Microsoft Entra ID Authentication (Critical)

**⚠️ ALWAYS use passwordless authentication with Entra ID for production workloads.**

### Complete Setup Guide

**[→ Microsoft Entra ID Authentication Setup Guide](./references/entra-rbac-overview.md)**

This guide covers:
- Enabling Entra ID authentication on PostgreSQL servers
- Creating PostgreSQL roles mapped to Azure identities
- Granting database permissions
- Connecting with access tokens instead of passwords

### Quick Setup Patterns

Use these patterns based on your scenario:

| Scenario | Guide Link | Use When |
|----------|------------|----------|
| **Developer Access** | [Pattern 1](./references/entra-rbac-overview.md#pattern-1-developer-user-access) | Grant developers access with their Azure identity |
| **App Authentication** | [Pattern 2](./references/entra-rbac-overview.md#pattern-2-managed-identity-for-applications) | Passwordless access for Azure-hosted apps (Container Apps, App Service, Functions) |
| **Team Access** | [Pattern 3](./references/entra-rbac-overview.md#pattern-3-group-based-access-control) | Manage permissions via Azure AD groups |
| **Connection Issues** | [Troubleshooting](./references/troubleshooting.md) | Diagnose authentication and connection failures |
| **Migration** | [Pattern 5](./references/entra-rbac-overview.md#pattern-5-migration-from-password-auth) | Transition from password to Entra ID authentication |

## Service Tiers

| Tier | vCores | Memory | Use Case |
|------|--------|--------|----------|
| Burstable | 1-20 | 0.5-4 GB/vCore | Dev/test, low traffic |
| General Purpose | 2-64 | 4 GB/vCore | Most production workloads |
| Memory Optimized | 2-64 | 8 GB/vCore | High-memory workloads |

**Start with Burstable for dev/test, scale up as needed.**

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `role does not exist` | Role not created in database | Run `pgaadauth_create_principal` - [see guide](./references/entra-rbac-overview.md) |
| `password authentication failed` | Token expired (5-60 min validity) | Get fresh token: `az account get-access-token --resource-type oss-rdbms` |
| `permission denied` | Role lacks permissions | Run `GRANT` statements - [see templates](./references/permission-templates.md) |
| Connection timeout | Firewall blocking access | Add firewall rule: `az postgres flexible-server firewall-rule create` |
| Guest user login fails | Wrong UPN format | Use full UPN with `#EXT#` tag from Azure AD |

## SDK Quick References

- **PostgreSQL Client**: [TypeScript](references/sdk/azure-postgres-ts.md)
- **Azure Identity**: [Python](references/sdk/azure-identity-py.md) | [TypeScript](references/sdk/azure-identity-ts.md)
- **PostgreSQL Mgmt**: [.NET](references/sdk/azure-resource-manager-postgresql-dotnet.md)

## References

- [Microsoft Entra ID Authentication Setup](./references/entra-rbac-overview.md) - Complete passwordless authentication guide
- [SQL Functions](./references/sql-functions.md) - Entra ID role management functions
- [Permission Templates](./references/permission-templates.md) - Common permission patterns
- [Troubleshooting](./references/troubleshooting.md) - Connection and auth issues
