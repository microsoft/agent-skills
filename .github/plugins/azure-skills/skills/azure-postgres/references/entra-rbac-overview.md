# Azure PostgreSQL Entra ID RBAC Setup

This guide helps you set up Microsoft Entra ID (formerly Azure AD) authentication for Azure Database for PostgreSQL Flexible Server. It covers the confusing two-layer mapping: **Azure Identity → PostgreSQL Role → Database Permissions**.

## When to Use This Guide

Use this guide when you need to:
- Set up Entra ID authentication for PostgreSQL
- Configure passwordless access to your PostgreSQL database
- Add a user/developer to Azure PostgreSQL using their Azure identity
- Set up managed identity for your app to access PostgreSQL
- Configure group-based access to PostgreSQL
- Troubleshoot authentication errors connecting to PostgreSQL with Entra
- Migrate from password authentication to Entra ID for PostgreSQL

## Overview

Azure Database for PostgreSQL Flexible Server supports Microsoft Entra ID authentication, allowing users to connect using their Azure identities instead of passwords. This involves:

1. **Enabling Entra authentication** on the PostgreSQL server
2. **Creating a PostgreSQL role** mapped to an Azure identity
3. **Granting database permissions** to the PostgreSQL role
4. **Connecting with an access token** instead of a password

### Identity Types Supported

| Identity Type | Use Case | SQL Function |
|--------------|----------|--------------|
| **User** | Developer access, interactive queries | `pgaadauth_create_principal` |
| **Group** | Team-based access management | `pgaadauth_create_principal_with_oid` |
| **Service Principal** | Application authentication | `pgaadauth_create_principal_with_oid` |
| **Managed Identity** | Azure-hosted app passwordless access | `pgaadauth_create_principal_with_oid` |

## Core Workflow
### Step 1: Check Current Authentication Status

Verify if Entra authentication is enabled on the server. If empty, no Entra admin is configured yet.

### Step 2: Add First Entra Administrator

Enable Entra authentication by adding the first admin using Azure CLI.

### Step 3: Connect as Entra Admin

Get an access token and connect using psql with the token as password.

### Step 4: Create PostgreSQL Roles for Identities

Once connected as admin, create roles for other identities using SQL functions.

### Step 5: Grant Database Permissions

Grant appropriate permissions to the new roles using GRANT statements.

**See:** [scripts/az-commands.sh](../scripts/az-commands.sh) for Azure CLI commands, [references/sql-functions.md](sql-functions.md) for SQL functions, and [references/permission-templates.md](permission-templates.md) for permission grants.

## Setup Patterns

### Pattern 1: Developer User Access

Set up a developer to access the database with their Azure identity.

**Required Information:**
- Developer's UPN (e.g., `developer@company.com`)
- Target database name
- Permission level (read-only, read-write, admin)
**Script:** See [scripts/setup-user.sh](../scripts/setup-user.sh)

### Pattern 2: Managed Identity for Applications

Configure passwordless database access for Azure-hosted applications (Container Apps, App Service, Functions).

**Required Information:**
- Managed identity name and resource group
- Target database name
- Permission level needed

**Steps:**

1. Get managed identity object ID
2. Create PostgreSQL role using `pgaadauth_create_principal_with_oid`
3. Grant permissions
4. Configure application to use Azure Identity SDK

**Script:** See [scripts/setup-managed-identity.sh](../scripts/setup-managed-identity.sh)

### Pattern 3: Group-Based Access Control

Manage database permissions through Azure AD groups.

**Required Information:**
- Group display name and object ID
- Whether to enable group sync (`pgaadauth.enable_group_sync`)
- Permission level for the group

**Group Sync Modes:**

| Mode | Behavior | Use Case |
|------|----------|----------|
| **OFF** (default) | Members use group name as username | Simple setup, no individual tracking |
| **ON** | Individual member roles auto-created | Audit trails, per-user permissions |
**Script:** See [scripts/setup-group.sh](../scripts/setup-group.sh)
---

### Pattern 4: Troubleshooting Connection Failures

Diagnose and fix Entra authentication issues.

**Common Errors:**
- `role "user@domain.com" does not exist` - Role not created in database
- `password authentication failed` - Token expired or invalid
- `FATAL: password authentication failed` - Wrong username format
- `could not connect to server` - Network/firewall issues

**See:** [troubleshooting.md](troubleshooting.md) for detailed diagnostic steps

---

### Pattern 5: Migration from Password Auth

Transition existing password-based roles to Entra ID authentication.

**Steps:**
1. Enable "PostgreSQL and Microsoft Entra authentication" mode (parallel auth)
2. Map existing roles to Entra identities using `SECURITY LABEL`
3. Test Entra authentication for each migrated role
4. Disable passwords: `ALTER ROLE "username" PASSWORD NULL`
5. Switch to "Microsoft Entra authentication only" mode

**Script:** See [scripts/migrate-to-entra.sh](../scripts/migrate-to-entra.sh)

## MCP Tools Used

| Tool | Purpose |
|------|---------|
| `postgres_server_list` | List PostgreSQL servers in subscription |
| `postgres_database_list` | List databases on a server |
| `postgres_database_query` | Execute SQL (role creation, permissions) |
| `postgres_server_param_get` | Get server parameter (e.g., group sync) |
| `postgres_server_param_set` | Set server parameter |

## Security Best Practices

| Practice | Recommendation |
|----------|---------------|
| **Least Privilege** | Grant minimum required permissions; avoid admin roles for apps |
| **Use Groups** | Manage access via Entra groups for easier administration |
| **Managed Identity** | Always use managed identity for Azure-hosted apps |
| **MFA for Admins** | Set `isMfa=true` for admin roles if tenant supports optional MFA |
| **Token Handling** | Never store tokens; acquire fresh before each connection |
| **Audit Access** | Use `pgaadauth_list_principals` to review who has access |
| **Private Endpoint** | Use private endpoint for production; configure NSG for AzureActiveDirectory tag |

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `role does not exist` | Role not created in database | Run `pgaadauth_create_principal` or `pgaadauth_create_principal_with_oid` |
| `password authentication failed` | Token expired (5-60 min validity) | Get fresh token with `az account get-access-token` |
| `permission denied` | Role exists but lacks permissions | Run `GRANT` statements for required access |
| Username case mismatch | Entra names are case-sensitive | Use exact case from Azure AD |
| Network timeout | Private endpoint missing NSG rule | Add outbound rule for `AzureActiveDirectory` service tag |
| Guest user login fails | Using wrong UPN format | Use full UPN with `#EXT#` tag |

## References

- [Azure CLI Commands](../scripts/az-commands.sh) - Token acquisition, identity lookups, admin management
- [SQL Functions](sql-functions.md) - Role creation, listing, security labels
- [Permission Templates](permission-templates.md) - Copy-paste SQL for common scenarios
- [Group Sync Guide](group-sync.md) - Group sync configuration details
- [Troubleshooting Guide](troubleshooting.md) - Detailed diagnostic steps
