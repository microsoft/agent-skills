#!/bin/bash
# Migrate existing PostgreSQL roles from password auth to Entra ID
# Usage: ./migrate-to-entra.sh <resource-group> <server-name>

set -e

# Parameters
RESOURCE_GROUP="${1:?Resource group required}"
SERVER_NAME="${2:?Server name required}"

echo "=== Azure PostgreSQL Migration to Entra ID ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Server: $SERVER_NAME"
echo ""
echo "WARNING: This script will help migrate password-based roles to Entra ID."
echo "Please ensure you have tested Entra authentication before running this."
echo ""

# Step 1: Verify server exists and get FQDN
echo "[1/5] Verifying server..."
SERVER_FQDN=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --query fullyQualifiedDomainName -o tsv)

if [ -z "$SERVER_FQDN" ]; then
  echo "ERROR: Server not found or not accessible"
  exit 1
fi
echo "Server FQDN: $SERVER_FQDN"

# Step 2: Check current authentication mode
echo ""
echo "[2/5] Checking authentication mode..."
AUTH_CONFIG=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --query authConfig -o json)

echo "Current auth config:"
echo "$AUTH_CONFIG" | jq .

# Step 3: Get admin credentials
echo ""
echo "[3/5] Getting current user info..."
CURRENT_USER=$(az ad signed-in-user show --query userPrincipalName -o tsv)
echo "Current user (Entra admin): $CURRENT_USER"

export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)
if [ -z "$PGPASSWORD" ]; then
  echo "ERROR: Failed to acquire access token. Are you an Entra admin?"
  exit 1
fi
echo "Token acquired"

# Step 4: List existing roles
echo ""
echo "[4/5] Listing existing PostgreSQL roles..."
echo ""
echo "=== Current PostgreSQL Roles ==="
psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -c \
  "SELECT rolname, rolcanlogin, rolsuper, rolcreatedb, rolcreaterole 
   FROM pg_roles 
   WHERE rolname NOT LIKE 'pg_%' 
   AND rolname NOT LIKE 'azure%' 
   AND rolname != 'replication'
   ORDER BY rolname;"

echo ""
echo "=== Existing Entra-Mapped Roles ==="
psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -c \
  "SELECT * FROM pgaadauth_list_principals(false);" 2>/dev/null || echo "No Entra roles found"

# Step 5: Provide migration instructions
echo ""
echo "[5/5] Migration Instructions"
echo ""
echo "=== Migration Steps ==="
echo ""
echo "For EACH role you want to migrate to Entra ID:"
echo ""
echo "1. Find the Azure AD object ID for the user/group/service principal:"
echo "   # For a user:"
echo "   az ad user show --id user@domain.com --query id -o tsv"
echo ""
echo "   # For a group:"
echo "   az ad group show --group 'Group Name' --query id -o tsv"
echo ""
echo "   # For a managed identity:"
echo "   az identity show --name <identity-name> --resource-group <rg> --query principalId -o tsv"
echo ""
echo "2. Map the existing role to the Entra identity using SECURITY LABEL:"
echo "   SECURITY LABEL for \"pgaadauth\" on role \"existing_role_name\" is 'aadauth,oid=<object-id>,type=user';"
echo ""
echo "   Object types: user, group, service (for managed identities and service principals)"
echo ""
echo "3. Test Entra authentication for the migrated role:"
echo "   export PGPASSWORD=\$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)"
echo "   psql \"host=$SERVER_FQDN user=user@domain.com dbname=<database> sslmode=require\""
echo ""
echo "4. After verifying Entra auth works, disable the password:"
echo "   ALTER ROLE \"existing_role_name\" PASSWORD NULL;"
echo ""
echo "5. Once all roles are migrated, switch to 'Microsoft Entra authentication only' mode:"
echo "   az postgres flexible-server update \\"
echo "     --resource-group $RESOURCE_GROUP \\"
echo "     --name $SERVER_NAME \\"
echo "     --microsoft-entra-auth Enabled \\"
echo "     --password-auth Disabled"
echo ""
echo "=== Example Migration Commands ==="
echo ""
echo "# Connect as Entra admin"
echo "export PGPASSWORD=\$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)"
echo "psql \"host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require\""
echo ""
echo "# Inside psql, run for each role:"
echo "-- Get object ID first: az ad user show --id developer@company.com --query id -o tsv"
echo "SECURITY LABEL for \"pgaadauth\" on role \"developer_role\" is 'aadauth,oid=abc12345-1234-1234-1234-123456789012,type=user';"
echo ""
echo "# Verify the mapping"
echo "SELECT * FROM pgaadauth_list_principals(false);"
echo ""
echo "# After testing Entra auth, disable password"
echo "ALTER ROLE \"developer_role\" PASSWORD NULL;"
