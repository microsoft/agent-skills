# PostgreSQL — TypeScript SDK Quick Reference

> Condensed from **azure-postgres-ts**. Full patterns (connection pooling,
> transactions, Entra ID auth, parameterized queries)
> in the **azure-postgres-ts** plugin skill if installed.

## Install
npm install pg @azure/identity
npm install -D @types/pg

## Quick Start
```typescript
import { Pool } from "pg";
const pool = new Pool({ host: process.env.AZURE_POSTGRESQL_HOST, database: process.env.AZURE_POSTGRESQL_DATABASE, port: 5432, ssl: { rejectUnauthorized: true } });
```

## Best Practices
- Always use connection pools for production applications
- Use parameterized queries — never concatenate user input
- Always close connections — use try/finally or connection pools
- Enable SSL — required for Azure (`ssl: { rejectUnauthorized: true }`)
- Handle token refresh — Entra ID tokens expire after ~1 hour
- Set connection timeouts — avoid hanging on network issues
- Use transactions for multi-statement operations
- Monitor pool metrics — track totalCount, idleCount, waitingCount
- Graceful shutdown — call `pool.end()` on application termination
- Use TypeScript generics — type your query results for safety
