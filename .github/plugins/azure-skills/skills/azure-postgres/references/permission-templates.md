# PostgreSQL Permission Templates

Copy-paste SQL templates for common permission scenarios when setting up Entra ID authentication.

## Permission Levels

### Read-Only Access

Grants SELECT access to all tables in the public schema.

```sql
-- Replace <database> and <role-name> with actual values
-- <role-name> should be the UPN (user@domain.com) or custom role name

GRANT CONNECT ON DATABASE <database> TO "<role-name>";
GRANT USAGE ON SCHEMA public TO "<role-name>";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "<role-name>";
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO "<role-name>";

-- Grant permissions on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO "<role-name>";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO "<role-name>";
```

---

### Read-Write Access

Grants SELECT, INSERT, UPDATE, DELETE on all tables.

```sql
GRANT CONNECT ON DATABASE <database> TO "<role-name>";
GRANT USAGE ON SCHEMA public TO "<role-name>";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "<role-name>";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "<role-name>";

-- Grant permissions on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "<role-name>";
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
  GRANT USAGE, SELECT ON SEQUENCES TO "<role-name>";
```

---

### Full Admin Access

Grants all privileges including ability to create objects.

```sql
GRANT ALL PRIVILEGES ON DATABASE <database> TO "<role-name>";
GRANT ALL PRIVILEGES ON SCHEMA public TO "<role-name>";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "<role-name>";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "<role-name>";
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO "<role-name>";

-- Grant permissions on future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "<role-name>";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "<role-name>";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO "<role-name>";

-- Add to azure_pg_admin role (Azure PostgreSQL admin group)
GRANT azure_pg_admin TO "<role-name>";
```

---

### Application-Specific Access

For applications that need access to specific tables only.

```sql
-- Connect permission
GRANT CONNECT ON DATABASE <database> TO "<role-name>";
GRANT USAGE ON SCHEMA public TO "<role-name>";

-- Specific tables only
GRANT SELECT, INSERT, UPDATE ON <table1> TO "<role-name>";
GRANT SELECT, INSERT, UPDATE, DELETE ON <table2> TO "<role-name>";
GRANT SELECT ON <readonly_table> TO "<role-name>";

-- Specific sequences
GRANT USAGE, SELECT ON <table1>_id_seq TO "<role-name>";
GRANT USAGE, SELECT ON <table2>_id_seq TO "<role-name>";
```

---

### Schema-Specific Access

For multi-tenant or multi-schema databases.

```sql
-- Grant access to a specific schema
GRANT CONNECT ON DATABASE <database> TO "<role-name>";
GRANT USAGE ON SCHEMA <schema-name> TO "<role-name>";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA <schema-name> TO "<role-name>";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA <schema-name> TO "<role-name>";

-- Future tables in that schema
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema-name> 
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "<role-name>";
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema-name> 
  GRANT USAGE, SELECT ON SEQUENCES TO "<role-name>";
```

---

## Quick Copy Templates

### For User (developer@company.com)

```sql
-- Read-Only
GRANT CONNECT ON DATABASE mydb TO "developer@company.com";
GRANT USAGE ON SCHEMA public TO "developer@company.com";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "developer@company.com";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO "developer@company.com";

-- Read-Write
GRANT CONNECT ON DATABASE mydb TO "developer@company.com";
GRANT USAGE ON SCHEMA public TO "developer@company.com";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "developer@company.com";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "developer@company.com";
```

### For Managed Identity (my-app-identity)

```sql
-- Read-Write (typical for applications)
GRANT CONNECT ON DATABASE mydb TO "my-app-identity";
GRANT USAGE ON SCHEMA public TO "my-app-identity";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "my-app-identity";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "my-app-identity";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "my-app-identity";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO "my-app-identity";
```

### For Group (Database Readers)

```sql
-- Note: Group names with spaces must be quoted
GRANT CONNECT ON DATABASE mydb TO "Database Readers";
GRANT USAGE ON SCHEMA public TO "Database Readers";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "Database Readers";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO "Database Readers";
```

---

## Revoking Permissions

### Revoke All Permissions

```sql
-- Revoke grants
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM "<role-name>";
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM "<role-name>";
REVOKE USAGE ON SCHEMA public FROM "<role-name>";
REVOKE CONNECT ON DATABASE <database> FROM "<role-name>";

-- Remove default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM "<role-name>";
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM "<role-name>";
```

### Drop Role Completely

```sql
-- First revoke all privileges
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM "<role-name>";
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM "<role-name>";
REVOKE ALL PRIVILEGES ON DATABASE <database> FROM "<role-name>";
REVOKE USAGE ON SCHEMA public FROM "<role-name>";

-- Then drop the role
DROP ROLE "<role-name>";
```

---

## Checking Existing Permissions

```sql
-- List all roles
\du

-- Show grants for a specific role
SELECT 
  grantee,
  table_schema,
  table_name,
  privilege_type
FROM information_schema.role_table_grants 
WHERE grantee = '<role-name>';

-- Show database-level permissions
SELECT datname, datacl FROM pg_database WHERE datname = '<database>';

-- Show schema permissions
SELECT nspname, nspacl FROM pg_namespace WHERE nspname = 'public';

-- List Entra-mapped roles with their properties
SELECT * FROM pgaadauth_list_principals(false);
```