# Service Discovery & Networking

How Aspire handles service-to-service communication, endpoint configuration, and networking for JavaScript/TypeScript apps.

---

## How Service Discovery Works

When you call `.WithReference()`, Aspire injects environment variables into the consuming resource with connection details. JS/TS apps read these environment variables at runtime.

```csharp
// AppHost
var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithHttpEndpoint(port: 3000, env: "PORT");

var frontend = builder.AddViteApp("frontend", "./frontend")
    .WithReference(api);
```

The `frontend` resource receives:
- `API_HTTP` → `http://localhost:{proxy_port}`
- `API_HTTPS` → `https://localhost:{proxy_port}` (if HTTPS configured)

---

## Environment Variable Naming Convention

Aspire uses `{RESOURCE_NAME}_{PROPERTY}` format (uppercase):

| Resource Type | Variables |
|---------------|-----------|
| HTTP endpoint | `{NAME}_HTTP`, `{NAME}_HTTPS` |
| Redis | `{NAME}_HOST`, `{NAME}_PORT`, `{NAME}_PASSWORD`, `{NAME}_URI` |
| PostgreSQL server | `{NAME}_HOST`, `{NAME}_PORT`, `{NAME}_URI` |
| PostgreSQL database | `{NAME}_HOST`, `{NAME}_PORT`, `{NAME}_URI`, `{NAME}_DATABASENAME`, `{NAME}_JDBCCONNECTIONSTRING` |
| Connection string | `ConnectionStrings__{name}` |
| Custom env | Whatever you set with `WithEnvironment` |

### Examples in JavaScript

```javascript
// HTTP service reference
const apiBaseUrl = process.env.API_HTTP || process.env.API_HTTPS;

// Redis
const redisClient = redis.createClient({
    socket: {
        host: process.env.CACHE_HOST,
        port: parseInt(process.env.CACHE_PORT),
    },
});

// PostgreSQL
const pgClient = new Client({
    host: process.env.MYDB_HOST,
    port: parseInt(process.env.MYDB_PORT),
    database: process.env.MYDB_DATABASENAME,
});

// Connection string (alternative pattern)
const connectionString = process.env.ConnectionStrings__mydb;
```

---

## Endpoint Configuration

### Basic HTTP endpoint

```csharp
var app = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithHttpEndpoint(port: 3000, env: "PORT");
```

- `port: 3000` → Host port (what external clients connect to)
- `env: "PORT"` → Sets `PORT` env var to the internal target port
- Aspire proxy sits between host port and app port

### HTTPS endpoint

```csharp
var app = builder.AddViteApp("frontend", "./frontend")
    .WithHttpsEndpoint(env: "PORT")
    .WithHttpsDeveloperCertificate();
```

### Named endpoints

```csharp
var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithHttpEndpoint(port: 3000, name: "public", env: "PORT")
    .WithHttpEndpoint(port: 9090, name: "admin", env: "ADMIN_PORT");
```

Named endpoints are resolved with `_endpointName.serviceName` syntax in .NET consumers.

### External endpoints (browser-facing)

```csharp
var frontend = builder.AddViteApp("frontend", "./frontend")
    .WithExternalHttpEndpoints();
```

Without this, endpoints are only accessible within the Aspire network.

---

## Proxy Architecture

Aspire inserts a reverse proxy between the host port and the app:

```
Browser → [Host Port 3000] → Proxy → [Random Port 65001] → Node.js App
```

The app binds to the random port provided via the `PORT` (or custom) env var. The proxy handles:
- Load balancing across replicas
- Port conflict avoidance
- Consistent URLs for service consumers

### Disable proxy (advanced)

```csharp
var app = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithEndpoint("http", endpoint => endpoint.IsProxied = false);
```

---

## Vite Proxy Configuration

For Vite apps that need to proxy API requests during development, configure in `vite.config.ts`:

```typescript
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
    server: {
        port: parseInt(process.env.PORT || '5173'),
        proxy: {
            '/api': {
                target: process.env.API_HTTP || 'http://localhost:3000',
                changeOrigin: true,
            },
        },
    },
});
```

This uses the Aspire-injected `API_HTTP` environment variable for the proxy target.

---

## Container Networks

When containers are involved, Aspire creates a bridge network:

- **Session networks:** `aspire-session-network-{id}-{apphost}`
- **Persistent networks:** `aspire-persistent-network-{hash}-{apphost}`

Containers communicate using resource names as DNS hostnames. Host services (Node.js processes) use exposed container ports instead.

---

## Common Patterns

### Express.js with service discovery

```javascript
// server.js
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

// Use Aspire-injected service URLs
const upstreamApi = process.env.UPSTREAM_HTTP;

app.get('/proxy', async (req, res) => {
    const response = await fetch(`${upstreamApi}/data`);
    const data = await response.json();
    res.json(data);
});

app.listen(port, () => console.log(`Listening on ${port}`));
```

### React with environment variables

```typescript
// In Vite React app, use VITE_ prefix for client-side env vars
// AppHost:
// .WithEnvironment("VITE_API_URL", api.GetEndpoint("http"))

const apiUrl = import.meta.env.VITE_API_URL;

async function fetchData() {
    const res = await fetch(`${apiUrl}/api/data`);
    return res.json();
}
```

> **Note:** Vite only exposes env vars prefixed with `VITE_` to client-side code. Server-side env vars (like `API_HTTP`) are not available in the browser bundle.
