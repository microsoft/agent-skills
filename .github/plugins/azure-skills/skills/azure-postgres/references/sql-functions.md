-- =============================================================================
-- SQL Functions for Azure PostgreSQL Entra ID Authentication
-- Run these commands after connecting as an Entra admin
-- =============================================================================

-- =============================================================================
-- CREATE ROLES
-- =============================================================================

-- Create role for a user (by name - must match UPN exactly)
SELECT * FROM pgaadauth_create_principal('user@domain.com', false, false);
-- Arguments:
--   'user@domain.com' = roleName (must match Entra principal name exactly)
--   false = isAdmin (true = azure_pg_admin member)
--   false = isMfa (true = require MFA claim in token)

-- Create role for a user as admin
SELECT * FROM pgaadauth_create_principal('admin@domain.com', true, false);

-- Create role using object ID (more reliable for managed identities, service principals, groups)
SELECT * FROM pgaadauth_create_principal_with_oid(
  'my-custom-role-name',  -- roleName: any name you choose
  'abc12345-1234-1234-1234-123456789012',  -- objectId: Entra object ID (GUID)
  'service',              -- objectType: 'user', 'group', or 'service'
  false,                  -- isAdmin
  false                   -- isMfa
);

-- Object Types:
--   'user'    = Entra users (including guests)
--   'group'   = Entra groups
--   'service' = Service principals and managed identities

-- =============================================================================
-- LIST ROLES
-- =============================================================================

-- List all Entra-mapped roles
SELECT * FROM pgaadauth_list_principals(false);

-- List only admin roles
SELECT * FROM pgaadauth_list_principals(true);

-- Returns: rolename, principalType, objectId, tenantId, isMfa, isAdmin

-- =============================================================================
-- ENABLE ENTRA ON EXISTING ROLE (SECURITY LABEL)
-- =============================================================================

-- Map an existing PostgreSQL role to an Entra identity
SECURITY LABEL for "pgaadauth" on role "existing_role" 
  is 'aadauth,oid=<object-id>,type=user';

-- With admin privileges
SECURITY LABEL for "pgaadauth" on role "existing_admin" 
  is 'aadauth,oid=<object-id>,type=user,admin';

-- For a group
SECURITY LABEL for "pgaadauth" on role "existing_group_role" 
  is 'aadauth,oid=<group-object-id>,type=group';

-- For a service principal or managed identity
SECURITY LABEL for "pgaadauth" on role "existing_app_role" 
  is 'aadauth,oid=<service-principal-object-id>,type=service';

-- =============================================================================
-- MANUAL GROUP SYNC
-- =============================================================================

-- Trigger manual sync of group members (if group sync is enabled)
SELECT * FROM pgaadauth_sync_roles_for_group_members();

-- =============================================================================
-- DROP ROLES
-- =============================================================================

-- Drop an Entra-mapped role
DROP ROLE "user@domain.com";

-- Note: For groups with sync enabled, do NOT delete the group role
-- Instead, disable login if needed:
ALTER ROLE "Group Name" NOLOGIN;