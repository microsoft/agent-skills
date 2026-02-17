# Azure PostgreSQL Group Sync Configuration

This guide explains how group-based access control works with Microsoft Entra ID authentication in Azure Database for PostgreSQL.

## Overview

When you create a PostgreSQL role mapped to an Entra group, group members can access the database. There are two modes:

| Mode | Setting | Behavior | Best For |
|------|---------|----------|----------|
| **Sync Disabled** | `pgaadauth.enable_group_sync=OFF` | Members use group name as username | Simple setups, shared audit trail |
| **Sync Enabled** | `pgaadauth.enable_group_sync=ON` | Individual member roles auto-created | Per-user auditing, fine-grained permissions |

## Mode 1: Group Sync Disabled (Default)

### How It Works

1. Create a group role in PostgreSQL
2. Grant permissions to the group
3. Group members sign in using the **group name** as their username
4. All members share the same PostgreSQL role

### Setup

```bash
# Get group object ID
GROUP_ID=$(az ad group show --group "Database Readers" --query id -o tsv)

# Connect as admin
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)
psql "host=<server>.postgres.database.azure.com user=admin@domain.com dbname=postgres sslmode=require"
```

```sql
-- Create group role
SELECT * FROM pgaadauth_create_principal_with_oid('Database Readers', '<group-id>', 'group', false, false);

-- Grant permissions
GRANT CONNECT ON DATABASE mydb TO "Database Readers";
GRANT USAGE ON SCHEMA public TO "Database Readers";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "Database Readers";
```

### Member Connection

Group members connect using the **group name** as their username:

```bash
# Bash
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)
psql "host=<server>.postgres.database.azure.com user='Database Readers' dbname=mydb sslmode=require"
```

```powershell
# PowerShell
$env:PGPASSWORD = az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv
psql "host=<server>.postgres.database.azure.com user='Database Readers' dbname=mydb sslmode=require"
```

**Note:** For group names with spaces, escape or quote the name:
- `user='Database Readers'`
- `user=Database\ Readers`

### Pros and Cons

| Pros | Cons |
|------|------|
| Simple setup | Can't distinguish users in audit logs |
| Instant membership effect | Can't grant per-user permissions |
| Single role to manage | Username is the group name, not intuitive |

---

## Mode 2: Group Sync Enabled

### How It Works

1. Create a group role in PostgreSQL
2. Enable group sync server parameter
3. Individual PostgreSQL roles are auto-created for each group member
4. Sync runs automatically every 30 minutes
5. Members sign in with their own UPN

### Setup

```bash
# Enable group sync
az postgres flexible-server parameter set \
  --resource-group <rg> \
  --server-name <server> \
  --name pgaadauth.enable_group_sync \
  --value ON

# Get group object ID
GROUP_ID=$(az ad group show --group "Database Readers" --query id -o tsv)

# Connect as admin
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)
psql "host=<server>.postgres.database.azure.com user=admin@domain.com dbname=postgres sslmode=require"
```

```sql
-- Create group role
SELECT * FROM pgaadauth_create_principal_with_oid('Database Readers', '<group-id>', 'group', false, false);

-- Grant permissions to the group (inherited by synced members)
GRANT CONNECT ON DATABASE mydb TO "Database Readers";
GRANT USAGE ON SCHEMA public TO "Database Readers";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "Database Readers";

-- Trigger manual sync (optional, otherwise wait 30 min)
SELECT * FROM pgaadauth_sync_roles_for_group_members();
```

### Member Connection

With sync enabled, members connect using their **own UPN**:

```bash
# Bash
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)
psql "host=<server>.postgres.database.azure.com user=developer@company.com dbname=mydb sslmode=require"
```

```powershell
# PowerShell
$env:PGPASSWORD = az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv
psql "host=<server>.postgres.database.azure.com user=developer@company.com dbname=mydb sslmode=require"
```

### Pros and Cons

| Pros | Cons |
|------|------|
| Individual audit trails | 30-min sync delay for new members |
| Can grant per-user permissions | More roles to manage |
| Users sign in with their own name | Group role must NOT be deleted |

---

## Important Considerations

### Group Role Management

**DO NOT delete the group role** when sync is enabled. The group role is needed to maintain the member-group relationship.

```sql
-- WRONG: Don't do this
DROP ROLE "Database Readers";  -- Breaks sync!

-- CORRECT: Disable login if needed, but keep the role
ALTER ROLE "Database Readers" NOLOGIN;
```

### Manual Sync

Trigger sync immediately instead of waiting 30 minutes:

```sql
SELECT * FROM pgaadauth_sync_roles_for_group_members();
```

### Checking Sync Status

View all synced member roles:

```sql
SELECT * FROM pgaadauth_list_principals(false);
```

### Permission Inheritance

When sync is enabled:
- Permissions granted to the group are inherited by member roles
- You can also grant additional permissions to individual member roles
- Revoking from the group affects all synced members

### Nested Groups

- Nested groups (groups within groups) are **not** supported
- Only direct members of the group are synced
- If you need hierarchical access, create separate group roles

---

## Switching Modes

### Enable Sync (OFF → ON)

```bash
az postgres flexible-server parameter set \
  --resource-group <rg> \
  --server-name <server> \
  --name pgaadauth.enable_group_sync \
  --value ON
```

Then trigger sync:
```sql
SELECT * FROM pgaadauth_sync_roles_for_group_members();
```

### Disable Sync (ON → OFF)

```bash
az postgres flexible-server parameter set \
  --resource-group <rg> \
  --server-name <server> \
  --name pgaadauth.enable_group_sync \
  --value OFF
```

**Note:** Existing synced member roles remain; they won't be deleted automatically.

---

## Troubleshooting

### New group member can't connect (sync enabled)

1. Wait up to 30 minutes, or trigger manual sync:
   ```sql
   SELECT * FROM pgaadauth_sync_roles_for_group_members();
   ```

2. Verify user is in the Azure AD group:
   ```bash
   az ad group member list --group "Database Readers" --query "[].userPrincipalName"
   ```

3. Check if role was created:
   ```sql
   SELECT * FROM pgaadauth_list_principals(false) WHERE rolename = 'user@domain.com';
   ```

### Group login fails (sync disabled)

1. Ensure username is the **group name**, not individual UPN
2. Escape spaces in group name: `user='Group Name'` or `user=Group\ Name`
3. Check group role exists:
   ```sql
   SELECT * FROM pgaadauth_list_principals(false) WHERE principaltype = 'group';
   ```

### Changes to group membership not reflected

1. Check the `pgaadauth.enable_group_sync` setting:
   ```bash
   az postgres flexible-server parameter show \
     --resource-group <rg> \
     --server-name <server> \
     --name pgaadauth.enable_group_sync
   ```

2. If sync is OFF, changes are immediate (members use group name)
3. If sync is ON, wait 30 min or run manual sync