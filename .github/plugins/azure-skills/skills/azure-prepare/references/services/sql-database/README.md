# Azure SQL Database

Managed relational database with ACID compliance and full SQL Server compatibility.

## When to Use

- Relational data with ACID requirements
- Complex queries and joins
- Existing SQL Server workloads
- Reporting and analytics
- Strong schema enforcement

## Required Supporting Resources

| Resource | Purpose |
|----------|---------|
| Key Vault | Store connection strings |
| Private Endpoint | Secure access (optional) |

## SKU Selection

| Tier | Use Case | Features |
|------|----------|----------|
| **Basic** | Dev/test, light workloads | 5 DTUs, 2GB |
| **Standard** | Production workloads | 10-3000 DTUs |
| **Premium** | High-performance | In-memory OLTP |
| **Serverless** | Variable workloads | Auto-pause, auto-scale |
| **Hyperscale** | Large databases | 100TB+, instant backup |

## Environment Variables

| Variable | Value |
|----------|-------|
| `SQL_SERVER` | `{server}.database.windows.net` |
| `SQL_DATABASE` | Database name |
| `SQL_CONNECTION_STRING` | Full connection string (Key Vault) |

## References

- [Bicep Patterns](bicep.md)
- [Entra ID Auth](auth.md)
- [SDK Patterns](sdk.md)
