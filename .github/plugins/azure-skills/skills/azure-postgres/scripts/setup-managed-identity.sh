#!/bin/bash
# Setup Managed Identity access for Azure PostgreSQL Flexible Server
# Usage: ./setup-managed-identity.sh <resource-group> <server-name> <identity-name> <identity-resource-group> <database> <permission-level>
# Permission levels: readonly, readwrite, admin

set -e

# Parameters
RESOURCE_GROUP="${1:?Resource group required}"
SERVER_NAME="${2:?Server name required}"
IDENTITY_NAME="${3:?Managed identity name required}"
IDENTITY_RG="${4:?Identity resource group required}"
DATABASE="${5:?Database name required}"
PERMISSION_LEVEL="${6:-readwrite}"

echo "=== Azure PostgreSQL Managed Identity Setup ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Server: $SERVER_NAME"
echo "Managed Identity: $IDENTITY_NAME (in $IDENTITY_RG)"
echo "Database: $DATABASE"
echo "Permission Level: $PERMISSION_LEVEL"
echo ""

# Step 1: Verify server exists and get FQDN
echo "[1/7] Verifying server..."
SERVER_FQDN=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --query fullyQualifiedDomainName -o tsv)

if [ -z "$SERVER_FQDN" ]; then
  echo "ERROR: Server not found or not accessible"
  exit 1
fi
echo "Server FQDN: $SERVER_FQDN"

# Step 2: Get managed identity details
echo ""
echo "[2/7] Getting managed identity details..."
IDENTITY_INFO=$(az identity show \
  --name "$IDENTITY_NAME" \
  --resource-group "$IDENTITY_RG" \
  --query "{principalId:principalId, clientId:clientId}" -o json)

PRINCIPAL_ID=$(echo "$IDENTITY_INFO" | jq -r '.principalId')
CLIENT_ID=$(echo "$IDENTITY_INFO" | jq -r '.clientId')

if [ -z "$PRINCIPAL_ID" ] || [ "$PRINCIPAL_ID" = "null" ]; then
  echo "ERROR: Managed identity not found"
  exit 1
fi

echo "Principal ID (Object ID): $PRINCIPAL_ID"
echo "Client ID: $CLIENT_ID"

# Step 3: Check if Entra admin exists
echo ""
echo "[3/7] Checking Entra admin status..."
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
echo "[4/7] Getting current user info..."
CURRENT_USER=$(az ad signed-in-user show --query userPrincipalName -o tsv)
echo "Current user: $CURRENT_USER"

# Step 5: Get access token
echo ""
echo "[5/7] Acquiring access token..."
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)

if [ -z "$PGPASSWORD" ]; then
  echo "ERROR: Failed to acquire access token"
  exit 1
fi
echo "Token acquired (valid for 5-60 minutes)"

# Step 6: Create PostgreSQL role for the managed identity
echo ""
echo "[6/7] Creating PostgreSQL role for managed identity..."

# Check if role already exists
ROLE_EXISTS=$(psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -t -c \
  "SELECT 1 FROM pgaadauth_list_principals(false) WHERE objectid = '$PRINCIPAL_ID';" 2>/dev/null | tr -d ' ')

if [ "$ROLE_EXISTS" = "1" ]; then
  echo "Role already exists for this managed identity"
  ROLE_NAME=$(psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -t -c \
    "SELECT rolename FROM pgaadauth_list_principals(false) WHERE objectid = '$PRINCIPAL_ID';" | tr -d ' ')
else
  # Create role using object ID (more reliable for managed identities)
  psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -c \
    "SELECT * FROM pgaadauth_create_principal_with_oid('$IDENTITY_NAME', '$PRINCIPAL_ID', 'service', false, false);"
  ROLE_NAME="$IDENTITY_NAME"
  echo "Role created successfully"
fi

echo "PostgreSQL role name: $ROLE_NAME"

# Step 7: Grant permissions based on level
echo ""
echo "[7/7] Granting $PERMISSION_LEVEL permissions on $DATABASE..."

case "$PERMISSION_LEVEL" in
  readonly)
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=$DATABASE sslmode=require" <<EOF
GRANT CONNECT ON DATABASE $DATABASE TO "$ROLE_NAME";
GRANT USAGE ON SCHEMA public TO "$ROLE_NAME";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "$ROLE_NAME";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO "$ROLE_NAME";
EOF
    ;;
  readwrite)
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=$DATABASE sslmode=require" <<EOF
GRANT CONNECT ON DATABASE $DATABASE TO "$ROLE_NAME";
GRANT USAGE ON SCHEMA public TO "$ROLE_NAME";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "$ROLE_NAME";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "$ROLE_NAME";
EOF
    ;;
  admin)
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=$DATABASE sslmode=require" <<EOF
GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO "$ROLE_NAME";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "$ROLE_NAME";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "$ROLE_NAME";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "$ROLE_NAME";
EOF
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -c \
      "GRANT azure_pg_admin TO \"$ROLE_NAME\";"
    ;;
  *)
    echo "ERROR: Invalid permission level. Use: readonly, readwrite, or admin"
    exit 1
    ;;
esac

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Managed Identity: $IDENTITY_NAME"
echo "PostgreSQL Role: $ROLE_NAME"
echo "Client ID: $CLIENT_ID"
echo ""
echo "Your application can now connect using Azure Identity SDK."
echo "See the examples/ folder for code samples in different languages."
echo ""
echo "Connection string format:"
echo "  host=$SERVER_FQDN;database=$DATABASE;user=$ROLE_NAME;sslmode=require"
