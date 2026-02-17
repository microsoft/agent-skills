#!/bin/bash
# Setup Entra ID user access for Azure PostgreSQL Flexible Server
# Usage: ./setup-user.sh <resource-group> <server-name> <user-upn> <database> <permission-level>
# Permission levels: readonly, readwrite, admin

set -e

# Parameters
RESOURCE_GROUP="${1:?Resource group required}"
SERVER_NAME="${2:?Server name required}"
USER_UPN="${3:?User UPN required (e.g., user@domain.com)}"
DATABASE="${4:?Database name required}"
PERMISSION_LEVEL="${5:-readonly}"

echo "=== Azure PostgreSQL Entra User Setup ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Server: $SERVER_NAME"
echo "User: $USER_UPN"
echo "Database: $DATABASE"
echo "Permission Level: $PERMISSION_LEVEL"
echo ""

# Step 1: Verify server exists and get FQDN
echo "[1/6] Verifying server..."
SERVER_FQDN=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --query fullyQualifiedDomainName -o tsv)

if [ -z "$SERVER_FQDN" ]; then
  echo "ERROR: Server not found or not accessible"
  exit 1
fi
echo "Server FQDN: $SERVER_FQDN"

# Step 2: Check if Entra admin exists
echo ""
echo "[2/6] Checking Entra admin status..."
ADMIN_COUNT=$(az postgres flexible-server microsoft-entra-admin list \
  --resource-group "$RESOURCE_GROUP" \
  --server-name "$SERVER_NAME" \
  --query "length(@)" -o tsv)

if [ "$ADMIN_COUNT" -eq 0 ]; then
  echo "ERROR: No Entra admin configured. Add an Entra admin first:"
  echo "  az postgres flexible-server microsoft-entra-admin create \\"
  echo "    --resource-group $RESOURCE_GROUP \\"
  echo "    --server-name $SERVER_NAME \\"
  echo "    --display-name <admin-upn> \\"
  echo "    --object-id <admin-object-id> \\"
  echo "    --type User"
  exit 1
fi
echo "Entra admin configured: $ADMIN_COUNT admin(s)"

# Step 3: Get current user info (must be Entra admin)
echo ""
echo "[3/6] Getting current user info..."
CURRENT_USER=$(az ad signed-in-user show --query userPrincipalName -o tsv)
echo "Current user: $CURRENT_USER"

# Step 4: Get access token
echo ""
echo "[4/6] Acquiring access token..."
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)

if [ -z "$PGPASSWORD" ]; then
  echo "ERROR: Failed to acquire access token"
  exit 1
fi
echo "Token acquired (valid for 5-60 minutes)"

# Step 5: Create PostgreSQL role for the user
echo ""
echo "[5/6] Creating PostgreSQL role for $USER_UPN..."

# Check if role already exists
ROLE_EXISTS=$(psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -t -c \
  "SELECT 1 FROM pgaadauth_list_principals(false) WHERE rolename = '$USER_UPN';" 2>/dev/null | tr -d ' ')

if [ "$ROLE_EXISTS" = "1" ]; then
  echo "Role already exists for $USER_UPN"
else
  psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -c \
    "SELECT * FROM pgaadauth_create_principal('$USER_UPN', false, false);"
  echo "Role created successfully"
fi

# Step 6: Grant permissions based on level
echo ""
echo "[6/6] Granting $PERMISSION_LEVEL permissions on $DATABASE..."

case "$PERMISSION_LEVEL" in
  readonly)
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=$DATABASE sslmode=require" <<EOF
GRANT CONNECT ON DATABASE $DATABASE TO "$USER_UPN";
GRANT USAGE ON SCHEMA public TO "$USER_UPN";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "$USER_UPN";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO "$USER_UPN";
EOF
    ;;
  readwrite)
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=$DATABASE sslmode=require" <<EOF
GRANT CONNECT ON DATABASE $DATABASE TO "$USER_UPN";
GRANT USAGE ON SCHEMA public TO "$USER_UPN";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "$USER_UPN";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "$USER_UPN";
EOF
    ;;
  admin)
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=$DATABASE sslmode=require" <<EOF
GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO "$USER_UPN";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "$USER_UPN";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "$USER_UPN";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "$USER_UPN";
EOF
    psql "host=$SERVER_FQDN user=$CURRENT_USER dbname=postgres sslmode=require" -c \
      "GRANT azure_pg_admin TO \"$USER_UPN\";"
    ;;
  *)
    echo "ERROR: Invalid permission level. Use: readonly, readwrite, or admin"
    exit 1
    ;;
esac

echo ""
echo "=== Setup Complete ==="
echo ""
echo "User $USER_UPN can now connect using:"
echo ""
echo "  # Get token"
echo "  export PGPASSWORD=\$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)"
echo ""
echo "  # Connect"
echo "  psql \"host=$SERVER_FQDN user=$USER_UPN dbname=$DATABASE sslmode=require\""
