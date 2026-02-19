# Acceptance Criteria: aspire-ts

## AppHost File-Based Setup

### Correct
```csharp
#:sdk Aspire.AppHost.Sdk@13.1.0
#:package Aspire.Hosting.JavaScript@13.1.0

var builder = DistributedApplication.CreateBuilder(args);
```

### Incorrect
```csharp
// WRONG - Missing JavaScript hosting package
#:sdk Aspire.AppHost.Sdk@13.1.0

var builder = DistributedApplication.CreateBuilder(args);
builder.AddViteApp("web", "./frontend"); // Will fail without Aspire.Hosting.JavaScript
```

## Vite Application (React, Vue, Svelte)

### Correct
```csharp
var web = builder.AddViteApp("web", "./frontend")
    .WithExternalHttpEndpoints()
    .WithReference(api)
    .WaitFor(api);
```

### Incorrect
```csharp
// WRONG - AddNpmApp is deprecated in Aspire 13+, use AddViteApp or AddJavaScriptApp
var web = builder.AddNpmApp("web", "./frontend", "dev")
    .WithExternalHttpEndpoints();
```

## Node.js Application

### Correct
```csharp
var api = builder.AddNodeApp("api", "./packages/api", "src/server.js")
    .WithNpm()
    .WithHttpHealthCheck("/health");
```

### Incorrect
```csharp
// WRONG - AddNodeApp requires entry file as third parameter
var api = builder.AddNodeApp("api", "./packages/api")
    .WithNpm();
```

## Generic JavaScript Application

### Correct
```csharp
var service = builder.AddJavaScriptApp("service", "./packages/service")
    .WithNpm()
    .WithRunScript("start");
```

### Incorrect
```csharp
// WRONG - No package manager specified
var service = builder.AddJavaScriptApp("service", "./packages/service");
```

## Package Manager Selection

### Correct
```csharp
// npm
builder.AddViteApp("web", "./frontend").WithNpm();

// yarn
builder.AddViteApp("web", "./frontend").WithYarn();

// pnpm
builder.AddViteApp("web", "./frontend").WithPnpm();
```

### Incorrect
```csharp
// WRONG - packageManager is not a valid parameter
builder.AddViteApp("web", "./frontend", packageManager: "npm");
```

## Service Discovery (Node.js Consumer)

### Correct
```javascript
// Aspire injects env vars: services__api__http__0 or API_HTTP
const apiUrl = process.env["services__api__http__0"];
const response = await fetch(`${apiUrl}/items`);
```

### Incorrect
```javascript
// WRONG - Hardcoded URL instead of using Aspire service discovery
const apiUrl = "http://localhost:5000";
const response = await fetch(`${apiUrl}/items`);
```

## Endpoint Configuration

### Correct
```csharp
var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithHttpEndpoint(port: 3000, env: "PORT")
    .WithExternalHttpEndpoints();
```

### Incorrect
```csharp
// WRONG - Using targetPort instead of port for JS apps
var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithHttpEndpoint(targetPort: 3000);
```

## OpenTelemetry Setup (Node.js)

### Correct
```javascript
// telemetry.js - MUST be imported before any other code
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT
  }),
  instrumentations: [getNodeAutoInstrumentations()]
});
sdk.start();

// app.js entry point
require('./telemetry'); // Must be FIRST import
const express = require('express');
```

### Incorrect
```javascript
// WRONG - Importing telemetry AFTER application code
const express = require('express');
const app = express();

require('./telemetry'); // Too late - express won't be instrumented
```

## Azure Integration (Redis)

### Correct
```csharp
// AppHost
var cache = builder.AddRedis("cache")
    .RunAsContainer();

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(cache);
```

```javascript
// Node.js consumer - reads connection from env var
const { createClient } = require('redis');
const connectionString = process.env["ConnectionStrings__cache"];
const client = createClient({ url: connectionString });
await client.connect();
```

### Incorrect
```javascript
// WRONG - Hardcoded Redis connection instead of using injected env vars
const { createClient } = require('redis');
const client = createClient({ url: "redis://localhost:6379" });
```

## Azure Integration (PostgreSQL)

### Correct
```csharp
// AppHost
var db = builder.AddPostgres("pg")
    .RunAsContainer()
    .AddDatabase("appdb");

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(db);
```

```javascript
// Node.js consumer
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env["ConnectionStrings__appdb"]
});
```

### Incorrect
```javascript
// WRONG - Hardcoded connection string
const pool = new Pool({
  connectionString: "postgresql://user:pass@localhost:5432/appdb"
});
```

## AppHost Language

### Correct
```csharp
// AppHost is ALWAYS written in C#, even for JS/TS apps
var builder = DistributedApplication.CreateBuilder(args);
builder.AddViteApp("frontend", "./frontend");
```

### Incorrect
```javascript
// WRONG - AppHost cannot be written in JavaScript/TypeScript
import { DistributedApplication } from '@aspire/hosting';
const builder = DistributedApplication.createBuilder();
```

## Script Arguments

### Correct
```csharp
// Option 1: WithArgs
builder.AddViteApp("frontend", "./frontend")
    .WithArgs("--no-open");

// Option 2: Custom package.json script
builder.AddViteApp("frontend", "./frontend")
    .WithRunScript("dev:no-open");
```

### Incorrect
```csharp
// WRONG - Constructor args parameter not supported in Aspire 13+
builder.AddViteApp("frontend", "./frontend", "--no-open");
```

## Polyglot AppHost (Mixed Languages)

### Correct
```csharp
#:sdk Aspire.AppHost.Sdk@13.1.0
#:package Aspire.Hosting.JavaScript@13.1.0
#:package Aspire.Hosting.Python@13.1.0

var builder = DistributedApplication.CreateBuilder(args);

var cache = builder.AddRedis("cache").RunAsContainer();

// .NET API
var api = builder.AddProject<Projects.MyApi>("api")
    .WithReference(cache);

// React frontend
var web = builder.AddViteApp("web", "./frontend")
    .WithExternalHttpEndpoints()
    .WithReference(api);

// Python worker
var worker = builder.AddUvicornApp("worker", "./worker", "main:app")
    .WithUv()
    .WithReference(cache);

builder.Build().Run();
```
