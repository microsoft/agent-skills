# Troubleshooting Azure PostgreSQL Entra ID Authentication

This guide helps diagnose and resolve common authentication issues when connecting to Azure Database for PostgreSQL using Microsoft Entra ID.

## Quick Diagnostic Checklist

Run through this checklist when authentication fails:

| Check | Command | Expected |
|-------|---------|----------|
| Role exists in database | `SELECT * FROM pgaadauth_list_principals(false);` | Your role appears in list |
| Token is fresh | Check timestamp from `az account get-access-token` | `expiresOn` is in the future |
| Username format correct | Compare with role name in database | Exact match (case-sensitive) |
| Network connectivity | `nslookup login.microsoftonline.com` | Resolves to IP address |
| DNS for Graph API | `nslookup graph.microsoft.com` | Resolves to IP address |
| Entra admin exists | `az postgres flexible-server microsoft-entra-admin list` | At least one admin |

## Common Errors and Solutions

### Error: `role "user@domain.com" does not exist`

**Cause:** The PostgreSQL role hasn't been created for this Entra identity.

**Solution:**

1. Connect as an Entra admin:
```bash
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)
psql "host=<server>.postgres.database.azure.com user=admin@domain.com dbname=postgres sslmode=require"
```

2. Create the role:
```sql
-- By name (for users)
SELECT * FROM pgaadauth_create_principal('user@domain.com', false, false);

-- By object ID (for managed identities/service principals)
SELECT * FROM pgaadauth_create_principal_with_oid('my-identity', '<object-id>', 'service', false, false);
```

---

### Error: `password authentication failed for user "user@domain.com"`

**Cause:** Token is expired, invalid, or wrong format.

**Solution:**

1. Get a fresh token:
```bash
# Bash
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)

# PowerShell
$env:PGPASSWORD = az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv
```

2. Verify token validity:
```bash
az account get-access-token --resource-type oss-rdbms --query expiresOn -o tsv
```

3. Ensure you're logged in as the correct user:
```bash
az account show --query user.name -o tsv
```

---

### Error: `FATAL: password authentication failed` (no username in error)

**Cause:** Username format is incorrect or doesn't match the database role.

**Solution:**

1. Check the exact role name in the database:
```sql
SELECT * FROM pgaadauth_list_principals(false);
```

2. Use the **exact** role name (case-sensitive) in your connection:
```bash
# If role is "Developer@Company.com", use exactly that
psql "host=<server>.postgres.database.azure.com user=Developer@Company.com dbname=mydb sslmode=require"
```

3. For guest users, use the full UPN with `#EXT#`:
```bash
psql "host=<server>.postgres.database.azure.com user=guest_user_example.com#EXT#@tenant.onmicrosoft.com dbname=mydb sslmode=require"
```

---

### Error: `could not connect to server: Connection timed out`

**Cause:** Network/firewall blocking connection or incorrect server name.

**Solution:**

1. Verify server FQDN:
```bash
az postgres flexible-server show --resource-group <rg> --name <server> --query fullyQualifiedDomainName -o tsv
```

2. Check firewall rules:
```bash
az postgres flexible-server firewall-rule list --resource-group <rg> --name <server>
```

3. For private endpoint, verify NSG allows outbound to `AzureActiveDirectory` service tag:
```bash
# Check NSG rules
az network nsg rule list --resource-group <rg> --nsg-name <nsg-name>
```

4. Verify DNS resolution:
```bash
nslookup <server>.postgres.database.azure.com
nslookup login.microsoftonline.com
nslookup graph.microsoft.com
```

---

### Error: `SSL SYSCALL error: Connection reset by peer`

**Cause:** TLS/SSL connection issue, often network-related.

**Solution:**

1. Ensure `sslmode=require` is in connection string
2. Check if proxy/firewall is intercepting TLS traffic
3. For private endpoint, verify route table has `AzureActiveDirectory` → `Internet`

---

### Error: Token acquisition fails

**Cause:** Not logged into Azure CLI or wrong account.

**Solution:**

1. Log in to Azure:
```bash
az login
```

2. Select the correct subscription:
```bash
az account set --subscription <subscription-id>
```

3. Verify you have access:
```bash
az account show
```

4. For service principal authentication:
```bash
az login --service-principal -u <client-id> -p <client-secret> --tenant <tenant-id>
```

---

### Error: `Cannot validate Microsoft Entra ID user because its name isn't unique`

**Cause:** Multiple objects in Azure AD have the same display name.

**Solution:**

Use `pgaadauth_create_principal_with_oid` instead:

```sql
-- Get the object ID first
-- az ad user show --id user@domain.com --query id -o tsv

SELECT * FROM pgaadauth_create_principal_with_oid('unique-role-name', '<object-id>', 'user', false, false);
```

---

### Error: Group member can't connect (group sync enabled)

**Cause:** Group sync hasn't run yet (runs every 30 minutes).

**Solution:**

1. Manually trigger sync:
```sql
SELECT * FROM pgaadauth_sync_roles_for_group_members();
```

2. Wait a few seconds and check roles:
```sql
SELECT * FROM pgaadauth_list_principals(false);
```

3. Verify the user is actually in the Azure AD group:
```bash
az ad group member list --group "Group Name" --query "[].userPrincipalName" -o tsv
```

---

### Error: Managed identity can't connect from Azure-hosted app

**Cause:** Application not using Azure Identity SDK correctly.

**Solution:**

1. Verify managed identity is enabled on the app:
```bash
# For Container Apps
az containerapp identity show --name <app> --resource-group <rg>

# For App Service
az webapp identity show --name <app> --resource-group <rg>
```

2. Ensure the correct role name is used (must match exactly what was created in PostgreSQL)

3. Check application code uses Azure Identity SDK

4. Verify managed identity object ID matches what's in PostgreSQL:
```bash
# Get MI object ID
az identity show --name <identity> --resource-group <rg> --query principalId -o tsv

# Compare with database
psql -c "SELECT * FROM pgaadauth_list_principals(false);"
```

---

## Diagnostic Commands Reference

### Check Entra Admin Status
```bash
az postgres flexible-server microsoft-entra-admin list \
  --resource-group <rg> \
  --server-name <server>
```

### List All Entra-Mapped Roles
```sql
SELECT * FROM pgaadauth_list_principals(false);
```

### Check Role Permissions
```sql
-- List all roles
\du

-- Check grants on a database
\l

-- Check table permissions
\dp

-- Detailed permission check
SELECT * FROM information_schema.role_table_grants WHERE grantee = 'user@domain.com';
```

### Verify Token
```bash
# Get token and check expiration
az account get-access-token --resource-type oss-rdbms

# Decode token (optional, for debugging)
# The accessToken is a JWT - you can decode it at jwt.io to verify claims
```

### Test Network Connectivity
```bash
# DNS resolution
nslookup <server>.postgres.database.azure.com
nslookup login.microsoftonline.com
nslookup graph.microsoft.com

# TCP connectivity (port 5432)
nc -zv <server>.postgres.database.azure.com 5432

# Or using telnet
telnet <server>.postgres.database.azure.com 5432
```

### Check Server Parameters
```bash
# Check group sync setting
az postgres flexible-server parameter show \
  --resource-group <rg> \
  --server-name <server> \
  --name pgaadauth.enable_group_sync
```

## Still Having Issues?

1. **Enable diagnostic logging** on the PostgreSQL server in Azure Portal
2. **Check Azure Monitor logs** for authentication failures
3. **Verify RBAC permissions** - you may need `Contributor` or specific PostgreSQL roles
4. **Contact support** with diagnostic output from the commands above