#!/bin/bash
# Azure CLI commands for Azure PostgreSQL Entra ID authentication
# This file contains commonly used commands - copy/paste and modify as needed

# =============================================================================
# ENTRA ADMIN MANAGEMENT
# =============================================================================

# List Entra admins
# This will fail if Entra auth is not enabled yet
az postgres flexible-server microsoft-entra-admin list \
  --resource-group <resource-group> \
  --server-name <server-name>

# Get your own object ID (current signed-in user)
OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

# IMPORTANT: Must enable Entra auth before attempting to create an admin
az postgres flexible-server update \
  --subscription <subscription-id> \
  --resource-group <resource-group> \
  --name <server-name> \
  --microsoft-entra-auth Enabled

# Add Entra admin
# This will fail if Entra auth is not enabled yet
az postgres flexible-server microsoft-entra-admin create \
  --resource-group <resource-group> \
  --server-name <server-name> \
  --display-name "admin@domain.com" \
  --object-id $OBJECT_ID \
  --type User

# Remove Entra admin
az postgres flexible-server microsoft-entra-admin delete \
  --resource-group <resource-group> \
  --server-name <server-name> \
  --object-id <object-id>

# =============================================================================
# TOKEN ACQUISITION & CONNECTION
# =============================================================================

# Get access token (use as password)
az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv

# Connect to PostgreSQL with token
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)
psql "host=<server>.postgres.database.azure.com user=<user>@domain.com dbname=<database> sslmode=require"

# For sovereign clouds, find resource URL
az cloud show --query endpoints.ossrdbmsResourceId

# =============================================================================
# IDENTITY LOOKUPS
# =============================================================================

# Get user object ID
az ad user show --id user@domain.com --query id -o tsv

# Get group object ID
az ad group show --group "Group Name" --query id -o tsv

# Get managed identity object ID
az identity show --name <identity-name> --resource-group <rg> --query principalId -o tsv

# Get service principal object ID (use Enterprise App, not App Registration)
az ad sp show --id <app-id> --query id -o tsv

# =============================================================================
# SERVER PARAMETERS
# =============================================================================

# Enable group sync
az postgres flexible-server parameter set \
  --resource-group <resource-group> \
  --server-name <server-name> \
  --source user-override \
  --name pgaadauth.enable_group_sync \
  --value ON

# Disable group sync
az postgres flexible-server parameter set \
  --resource-group <resource-group> \
  --server-name <server-name> \
  --source user-override \
  --name pgaadauth.enable_group_sync \
  --value OFF

# Check current value
az postgres flexible-server parameter show \
  --resource-group <resource-group> \
  --server-name <server-name> \
  --name pgaadauth.enable_group_sync

# =============================================================================
# AUTHENTICATION MODE
# =============================================================================

# !!!IMPORTANT: Must enable Entra auth before attempting to create an admin

# Enable Entra-only authentication (disable password auth)
az postgres flexible-server update \
  --resource-group <resource-group> \
  --name <server-name> \
  --microsoft-entra-auth Enabled \
  --password-auth Disabled

# Enable both Entra and password authentication
az postgres flexible-server update \
  --resource-group <resource-group> \
  --name <server-name> \
  --microsoft-entra-auth Enabled \
  --password-auth Enabled

# Disable Entra authentication (password-only)
az postgres flexible-server update \
  --resource-group <resource-group> \
  --name <server-name> \
  --microsoft-entra-auth Disabled \
  --password-auth Enabled
