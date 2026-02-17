#!/bin/bash
# Setup Group-based access for Azure PostgreSQL Flexible Server
# Usage: ./setup-group.sh <resource-group> <server-name> <group-name> <database> <permission-level> [enable-sync]
# Permission levels: readonly, readwrite, admin
# enable-sync: true/false (default: false)

set -e

# Parameters
RESOURCE_GROUP="${1:?Resource group required}"
SERVER_NAME="${2:?Server name required}"
GROUP_NAME="${3:?Group name required}"
DATABASE="${4:?Database name required}"
PERMISSION_LEVEL="${5:-readonly}"
ENABLE_SYNC="${6:-false}"

echo "=== Azure PostgreSQL Group Access Setup ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Server: $SERVER_NAME"
echo "Group: $GROUP_NAME"
echo "Database: $DATABASE"
echo "Permission Level: $PERMISSION_LEVEL"
echo "Enable Group Sync: $ENABLE_SYNC"
echo ""

# Step 1: Verify server exists and get FQDN
echo "[1/8] Verifying server..."
SERVER_FQDN=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --query fullyQualifiedDomainName -o tsv)

if [ -z "$SERVER_FQDN" ]; then
  echo "ERROR: Server not found or not accessible"
  exit 1
fi
echo "Server FQDN: $SERVER_FQDN"

# Step 2: Get group details from Azure AD
echo ""
echo "[2/8] Getting group details from Azure AD..."
GROUP_INFO=$(az ad group show --group "$GROUP_NAME" --query "{id:id, displayName:displayName}" -o json 2>/dev/null || echo "")

if [ -z "$GROUP_INFO" ] || [ "$GROUP_INFO" = "" ]; then
  echo "ERROR: Group '$GROUP_NAME' not found in Azure AD"
  exit 1
fi

GROUP_ID=$(echo "$GROUP_INFO" | jq -r '.id')
GROUP_DISPLAY_NAME=$(echo "$GROUP_INFO" | jq -r '.displayName')

echo "Group ID: $GROUP_ID"
echo "Group Display Name: $GROUP_DISPLAY_NAME"

# List group members
echo ""
echo "Group members:"
az ad group member list --group "$GROUP_NAME" --query "[].{displayName:displayName, userPrincipalName:userPrincipalName}" -o table

# Step 3: Check if Entra admin exists
echo ""
echo "[3/8] Checking Entra admin status..."
ADMIN_COUNT=$(az postgres flexible-server microsoft-entra-admin list \
  --resource-group "$RESOURCE_GROUP" \
  --server-name "$SERVER_NAME" \
  --query "length(@)" -o tsv)

if [ "$ADMIN_COUNT" -eq 0 ]; then
  echo "ERROR: No Entra admin configured. Add an Entra admin first."
  exit 1
fi
echo "Entra admin configured: $ADMIN_COUNT admin(s)"

# Step 4: Get current user info (must be Entra admin)
echo ""
echo "[4/8] Getting current user info..."
CURRENT_USER=$(az ad signed-in-user show --query userPrincipalName -o tsv)
echo "Current user: $CURRENT_USER"

# Step 5: Get access token
echo ""
echo "[5/8] Acquiring access token..."
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)

if [ -z "$PGPASSWORD" ]; then
  echo "ERROR: Failed to acquire access token"
  exit 1
fi
echo "Token acquired (valid for 5-60 minutes)"

# Step 6: Configure group sync parameter if requested
echo ""
echo "[6/8] Configuring group sync..."
if [ "$ENABLE_SYNC" = "true" ]; then
  az postgres flexible-server parameter set \
    --resource-group "$RESOURCE_GROUP" \
    --server-name "$SERVER_NAME" \
    --source user-override \
    --name pgaadauth.enable_group_sync \
    --value ON \
    --output none
  echo "Group sync ENABLED (members will get individual roles, auto-synced every 30 min)"
else
  echo "Group sync DISABLED (members use group name as username)"
fi

# Step 7: Create PostgreSQL role for the group
echo ""
echo "[7/8] Creating PostgreSQL role for group..."

# Check if role already exists
ROLE_EXISTS=$(psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -t -c \
  "SELECT 1 FROM pgaadauth_list_principals(false) WHERE objectid = '$GROUP_ID';" 2>/dev/null | tr -d ' ')

if [ "$ROLE_EXISTS" = "1" ]; then
  echo "Role already exists for group '$GROUP_DISPLAY_NAME'"
else
  # Create role using object ID
  psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -c \
    "SELECT * FROM pgaadauth_create_principal_with_oid('$GROUP_DISPLAY_NAME', '$GROUP_ID', 'group', false, false);"
  echo "Role created successfully"
fi

# If sync is enabled, trigger manual sync
if [ "$ENABLE_SYNC" = "true" ]; then
  echo ""
  echo "Triggering manual group member sync..."
  psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -c \
    "SELECT * FROM pgaadauth_sync_roles_for_group_members();" || echo "Note: Sync may take a moment to complete"
fi

# Step 8: Grant permissions based on level
echo ""
echo "[8/8] Granting $PERMISSION_LEVEL permissions on $DATABASE..."

# Escape the group name for PostgreSQL (handle spaces)
ESCAPED_GROUP_NAME=$(echo "$GROUP_DISPLAY_NAME" | sed 's/"/\\"/g')

case "$PERMISSION_LEVEL" in
  readonly)
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=$DATABASE sslmode=require" <<EOF
GRANT CONNECT ON DATABASE $DATABASE TO "$ESCAPED_GROUP_NAME";
GRANT USAGE ON SCHEMA public TO "$ESCAPED_GROUP_NAME";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "$ESCAPED_GROUP_NAME";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO "$ESCAPED_GROUP_NAME";
EOF
    ;;
  readwrite)
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=$DATABASE sslmode=require" <<EOF
GRANT CONNECT ON DATABASE $DATABASE TO "$ESCAPED_GROUP_NAME";
GRANT USAGE ON SCHEMA public TO "$ESCAPED_GROUP_NAME";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "$ESCAPED_GROUP_NAME";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "$ESCAPED_GROUP_NAME";
EOF
    ;;
  admin)
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=$DATABASE sslmode=require" <<EOF
GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO "$ESCAPED_GROUP_NAME";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "$ESCAPED_GROUP_NAME";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "$ESCAPED_GROUP_NAME";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "$ESCAPED_GROUP_NAME";
EOF
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -c \
      "GRANT azure_pg_admin TO \"$ESCAPED_GROUP_NAME\";"
    ;;
  *)
    echo "ERROR: Invalid permission level. Use: readonly, readwrite, or admin"
    exit 1
    ;;
esac

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Group: $GROUP_DISPLAY_NAME"
echo "Group ID: $GROUP_ID"
echo "Group Sync: $ENABLE_SYNC"
echo ""

if [ "$ENABLE_SYNC" = "true" ]; then
  echo "Group members can connect using their individual UPN:"
  echo "  export PGPASSWORD=\$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)"
  echo "  psql \"host=$SERVER_FQDN user=member@domain.com dbname=$DATABASE sslmode=require\""
  echo ""
  echo "Note: New group members are synced automatically every 30 minutes."
  echo "To force sync: SELECT * FROM pgaadauth_sync_roles_for_group_members();"
else
  echo "Group members connect using the GROUP NAME as username:"
  echo "  export PGPASSWORD=\$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)"
  echo "  psql \"host=$SERVER_FQDN user='$GROUP_DISPLAY_NAME' dbname=$DATABASE sslmode=require\""
  echo ""
  echo "Note: Spaces in group name must be escaped: 'Group\\ Name'"
fi
