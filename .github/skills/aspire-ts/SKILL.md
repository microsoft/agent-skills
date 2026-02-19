---
name: aspire-ts
description: Orchestrate JavaScript/TypeScript applications with .NET Aspire. Use when building Node.js APIs, React/Vue/Svelte frontends, or Vite apps that need service discovery, telemetry, and deployment orchestration via Aspire's AppHost. Covers AddViteApp, AddNodeApp, AddJavaScriptApp, package managers, OpenTelemetry, and polyglot integration patterns.
---

# .NET Aspire for JavaScript/TypeScript

Orchestrate JavaScript and TypeScript applications using .NET Aspire's AppHost. Aspire treats JS/TS apps as first-class resources alongside .NET services, containers, and cloud infrastructure — providing service discovery, telemetry, health monitoring, and deployment from a single code-first model.

> **Important:** The AppHost is always written in C#, even when orchestrating JS/TS apps. The `Aspire.Hosting.JavaScript` NuGet package provides the hosting APIs.

## Prerequisites

- **.NET SDK 10.0+** — Required for the Aspire AppHost
- **Aspire CLI** installed (`aspire --version`)
- **Node.js 22+** with npm, yarn, or pnpm
- **NuGet package:** `Aspire.Hosting.JavaScript` in your AppHost project

```bash
# Install in AppHost project
dotnet add package Aspire.Hosting.JavaScript

# For file-based AppHost (apphost.cs), use directive:
#:package Aspire.Hosting.JavaScript@13.1.0
```

---

## Resource Types

Three methods to add JS/TS apps to the AppHost:

| Method | Use Case | Entry Point |
|--------|----------|-------------|
| `AddViteApp` | Vite-based apps (React, Vue, Svelte) | npm script (`dev`) |
| `AddNodeApp` | Node.js apps with direct file entry | JavaScript file |
| `AddJavaScriptApp` | General JS apps with npm scripts | npm script (`dev`) |

### AddViteApp — Vite Applications

Best for React, Vue, Svelte, and other Vite-based frontends.

```csharp
var builder = DistributedApplication.CreateBuilder(args);

var api = builder.AddProject<Projects.Api>("api");

var frontend = builder.AddViteApp("frontend", "./packages/web")
    .WithExternalHttpEndpoints()
    .WithReference(api)
    .WaitFor(api);

builder.Build().Run();
```

**Defaults:**
- Runs `dev` script during development
- Runs `build` script when publishing
- Auto-generates Dockerfile for production
- Auto-detects package manager from lockfiles

### AddNodeApp — Node.js Applications

For Node.js servers with a direct JavaScript entry point.

```csharp
var api = builder.AddNodeApp("api", "./packages/api", "src/server.js")
    .WithNpm()
    .WithHttpEndpoint(port: 3000, env: "PORT")
    .WithHttpHealthCheck("/health");
```

**Parameters:**
- `name` — Resource name in Aspire dashboard
- `appDirectory` — Path to directory containing the app
- `scriptPath` — Path to the JS file to run (relative to appDirectory)

### AddJavaScriptApp — Generic JavaScript

For any JS app using npm scripts. Foundation for both `AddViteApp` and `AddNodeApp`.

```csharp
var app = builder.AddJavaScriptApp("app", "./frontend")
    .WithHttpEndpoint(port: 3000, env: "PORT");
```

**Defaults:** Uses npm, runs `dev` script in development, `build` script when publishing.

---

## Package Managers

### npm (Default)

```csharp
var app = builder.AddViteApp("frontend", "./frontend");
// npm is used automatically

// Customize npm behavior:
var app2 = builder.AddViteApp("frontend", "./frontend")
    .WithNpm(installCommand: "ci", installArgs: ["--legacy-peer-deps"]);
```

### yarn

```csharp
var app = builder.AddViteApp("frontend", "./frontend")
    .WithYarn();

// With custom args:
var app2 = builder.AddViteApp("frontend", "./frontend")
    .WithYarn(installArgs: ["--immutable"]);
```

### pnpm

```csharp
var app = builder.AddViteApp("frontend", "./frontend")
    .WithPnpm();

// With custom args:
var app2 = builder.AddViteApp("frontend", "./frontend")
    .WithPnpm(installArgs: ["--frozen-lockfile"]);
```

**Auto-install:** All package managers install dependencies automatically before running. In publish mode, deterministic install commands are used (`npm ci`, `yarn install --immutable`, `pnpm install --frozen-lockfile`) when lockfiles exist.

---

## Service Discovery

When you call `.WithReference(api)`, Aspire injects environment variables into the JS app:

```csharp
var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithHttpEndpoint(port: 3000, env: "PORT");

var frontend = builder.AddViteApp("frontend", "./frontend")
    .WithReference(api)      // Injects API_HTTP and API_HTTPS env vars
    .WaitFor(api);
```

### Consuming in JavaScript/TypeScript

```typescript
// Access injected service URLs
const apiUrl = process.env.API_HTTP || process.env.API_HTTPS;

// For databases and other resources
const redisHost = process.env.CACHE_HOST;
const redisPort = process.env.CACHE_PORT;
const pgConnectionString = process.env.POSTGRESDB_CONNECTIONSTRING;
```

**Environment variable naming:** `{RESOURCE_NAME}_{PROPERTY}` (uppercase, underscores).

| Resource Type | Variables Injected |
|---------------|-------------------|
| HTTP service | `{NAME}_HTTP`, `{NAME}_HTTPS` |
| Redis | `{NAME}_HOST`, `{NAME}_PORT`, `{NAME}_URI` |
| PostgreSQL DB | `{NAME}_HOST`, `{NAME}_PORT`, `{NAME}_URI`, `{NAME}_DATABASENAME` |
| Connection string | `ConnectionStrings__{name}` |

---

## Endpoints & Networking

### Configure HTTP endpoint

```csharp
var app = builder.AddViteApp("frontend", "./frontend")
    .WithHttpEndpoint(port: 3000, env: "PORT");
```

- `port` — Host port (exposed to browser/other services)
- `env` — Environment variable name set to the internal target port
- Aspire inserts a reverse proxy between host port and app port

### External endpoints

Mark endpoints as externally accessible (browser-facing):

```csharp
var frontend = builder.AddViteApp("frontend", "./frontend")
    .WithExternalHttpEndpoints();
```

### HTTPS with developer certificate (Vite)

```csharp
var app = builder.AddViteApp("frontend", "./frontend")
    .WithHttpsEndpoint(env: "PORT")
    .WithHttpsDeveloperCertificate();
```

Aspire auto-injects HTTPS config into Vite without modifying `vite.config.js`.

---

## Scripts & Arguments

### Custom run/build scripts

```csharp
var app = builder.AddJavaScriptApp("app", "./app")
    .WithRunScript("start")      // Use "npm run start" instead of "dev"
    .WithBuildScript("prod");    // Use "npm run prod" instead of "build"
```

### Pass arguments

```csharp
// Option 1: WithArgs
var app = builder.AddViteApp("frontend", "./frontend")
    .WithArgs("--no-open");

// Option 2: Custom script in package.json
// package.json: { "scripts": { "dev:no-open": "vite --no-open" } }
var app2 = builder.AddViteApp("frontend", "./frontend")
    .WithRunScript("dev:no-open");
```

### Custom Vite config file

```csharp
var app = builder.AddViteApp("frontend", "./frontend")
    .WithViteConfig("./vite.production.config.js");
```

---

## OpenTelemetry for Node.js

Configure telemetry so JS/TS apps report to the Aspire dashboard.

### Install packages

```bash
npm install @opentelemetry/api @opentelemetry/sdk-node \
  @opentelemetry/auto-instrumentations-node \
  @opentelemetry/exporter-trace-otlp-grpc \
  @opentelemetry/exporter-metrics-otlp-grpc
```

### Create telemetry.js (must be imported first)

```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-grpc');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { resourceFromAttributes } = require('@opentelemetry/resources');
const { ATTR_SERVICE_NAME } = require('@opentelemetry/semantic-conventions');

const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4317';

const sdk = new NodeSDK({
    resource: resourceFromAttributes({ [ATTR_SERVICE_NAME]: 'frontend' }),
    traceExporter: new OTLPTraceExporter({ url: otlpEndpoint }),
    metricReader: new PeriodicExportingMetricReader({
        exporter: new OTLPMetricExporter({ url: otlpEndpoint }),
    }),
    instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
```

### Import first in app entry point

```javascript
require('./telemetry'); // Must be first!
const express = require('express');
// ... rest of app
```

Aspire auto-sets `OTEL_EXPORTER_OTLP_ENDPOINT` for orchestrated resources.

---

## Integrations (Redis, PostgreSQL, etc.)

### Redis

```csharp
// AppHost
var cache = builder.AddRedis("cache");

var app = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(cache);  // Injects CACHE_HOST, CACHE_PORT, CACHE_URI
```

```javascript
// Node.js
const redis = require('redis');
const client = redis.createClient({
    socket: { host: process.env.CACHE_HOST, port: process.env.CACHE_PORT }
});
```

### PostgreSQL

```csharp
// AppHost
var postgres = builder.AddAzurePostgresFlexibleServer("postgres")
    .RunAsContainer();
var db = postgres.AddDatabase("mydb");

var app = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(db);  // Injects MYDB_HOST, MYDB_PORT, MYDB_URI, etc.
```

```javascript
// Node.js
const { Client } = require('pg');
const client = new Client({
    host: process.env.MYDB_HOST,
    port: process.env.MYDB_PORT,
    database: process.env.MYDB_DATABASENAME,
});
```

---

## Polyglot Patterns

Mix JS/TS apps with .NET, Python, and containers in one AppHost:

```csharp
var builder = DistributedApplication.CreateBuilder(args);

// Infrastructure
var cache = builder.AddRedis("cache");
var db = builder.AddPostgres("postgres").AddDatabase("appdb");

// .NET API
var api = builder.AddProject<Projects.Api>("api")
    .WithReference(db)
    .WithReference(cache);

// Node.js microservice
var worker = builder.AddNodeApp("worker", "./worker", "index.js")
    .WithNpm()
    .WithReference(cache);

// React frontend
var frontend = builder.AddViteApp("frontend", "./frontend")
    .WithExternalHttpEndpoints()
    .WithReference(api)
    .WaitFor(api);

builder.Build().Run();
```

---

## Deployment

### aspire run (Development)

```bash
aspire run
```

JS/TS apps run as Node.js processes (not containerized). Aspire dashboard launches with logs, traces, and metrics.

### aspire deploy (Containerized)

```bash
aspire deploy
```

Aspire auto-generates Dockerfiles, builds container images, and deploys. JS apps become Docker containers.

### aspire publish (CI/CD artifacts)

```bash
aspire publish --output-path ./aspire-output
```

Generates `docker-compose.yaml` and `.env` files for deployment.

### Docker Compose output

Aspire generates production-ready Docker Compose for JS/TS apps:
- Auto-generated multi-stage Dockerfile
- Deterministic dependency install from lockfiles
- Build step runs production build script
- Proper environment variable injection

---

## Common Patterns

### Health checks

```csharp
var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithHttpHealthCheck("/health");
```

### Persistent containers

```csharp
var redis = builder.AddRedis("cache")
    .WithLifetime(ContainerLifetime.Persistent);
```

### Wait for dependencies

```csharp
var frontend = builder.AddViteApp("frontend", "./frontend")
    .WithReference(api)
    .WaitFor(api)       // Wait for API to be ready
    .WaitFor(cache);    // Wait for Redis to be ready
```

### Environment variables

```csharp
var app = builder.AddViteApp("frontend", "./frontend")
    .WithEnvironment("NODE_ENV", "development")
    .WithEnvironment("VITE_API_URL", api.GetEndpoint("http"));
```

---

## Quick Reference

| Task | Code |
|------|------|
| Add Vite app | `builder.AddViteApp("name", "./path")` |
| Add Node.js app | `builder.AddNodeApp("name", "./path", "server.js")` |
| Use yarn | `.WithYarn()` |
| Use pnpm | `.WithPnpm()` |
| Set port via env | `.WithHttpEndpoint(port: 3000, env: "PORT")` |
| Reference service | `.WithReference(otherResource)` |
| Wait for dependency | `.WaitFor(otherResource)` |
| External endpoint | `.WithExternalHttpEndpoints()` |
| Health check | `.WithHttpHealthCheck("/health")` |
| Custom script | `.WithRunScript("start")` |
| Pass args | `.WithArgs("--no-open")` |
| HTTPS dev cert | `.WithHttpsDeveloperCertificate()` |
| Custom Vite config | `.WithViteConfig("./custom.config.js")` |

## References

- [Aspire JavaScript Integration](https://aspire.dev/integrations/frameworks/javascript/)
- [Aspire AppHost](https://aspire.dev/get-started/app-host/)
- [Aspire Service Discovery](https://aspire.dev/fundamentals/service-discovery/)
- [Aspire Dashboard](https://aspire.dev/dashboard/overview/)
- [Aspire CLI](https://aspire.dev/reference/cli/overview/)
