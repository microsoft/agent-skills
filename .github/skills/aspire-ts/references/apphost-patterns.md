# AppHost Patterns for JavaScript/TypeScript

The AppHost is always C# — even when orchestrating JS/TS apps. This reference covers the AppHost patterns most relevant to JS/TS developers.

---

## File-Based vs Project-Based AppHost

| Type | File | When to Use |
|------|------|-------------|
| **File-based** | `apphost.cs` | Polyglot projects (JS, Python, mixed) |
| **Project-based** | `AppHost.csproj` + `AppHost.cs` | .NET-heavy solutions |

### File-Based AppHost (Recommended for JS/TS)

Created by `aspire init` in non-.NET projects:

```csharp
// apphost.cs
#:sdk Aspire.AppHost.Sdk@13.1.0
#:package Aspire.Hosting.JavaScript@13.1.0
#:package Aspire.Hosting.Redis@13.1.0

var builder = DistributedApplication.CreateBuilder(args);

var cache = builder.AddRedis("cache");

var api = builder.AddNodeApp("api", "./packages/api", "src/server.js")
    .WithNpm()
    .WithHttpEndpoint(port: 3000, env: "PORT")
    .WithReference(cache);

var frontend = builder.AddViteApp("frontend", "./packages/web")
    .WithExternalHttpEndpoints()
    .WithReference(api)
    .WaitFor(api);

builder.Build().Run();
```

**Key directives:**
- `#:sdk` — Aspire SDK version
- `#:package` — NuGet package dependencies (no .csproj needed)

### Project-Based AppHost

For solutions with .NET projects alongside JS/TS:

```xml
<!-- AppHost.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <Sdk Name="Aspire.AppHost.Sdk" Version="13.1.0" />
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Aspire.Hosting.JavaScript" Version="13.1.0" />
  </ItemGroup>
</Project>
```

---

## Resource Lifecycle Methods

### WithReference — Service Dependencies

Declares a dependency and injects connection info as environment variables:

```csharp
var frontend = builder.AddViteApp("frontend", "./frontend")
    .WithReference(api)       // Injects API_HTTP, API_HTTPS
    .WithReference(cache)     // Injects CACHE_HOST, CACHE_PORT, CACHE_URI
    .WithReference(db);       // Injects DB_HOST, DB_PORT, DB_URI, DB_DATABASENAME
```

### WaitFor — Startup Order

Delays resource startup until dependencies are healthy:

```csharp
var frontend = builder.AddViteApp("frontend", "./frontend")
    .WaitFor(api)      // Wait for API health check to pass
    .WaitFor(cache);   // Wait for Redis to accept connections
```

### WithExternalHttpEndpoints — Browser Access

Marks endpoints as externally accessible:

```csharp
var frontend = builder.AddViteApp("frontend", "./frontend")
    .WithExternalHttpEndpoints();
```

### WithEnvironment — Custom Environment Variables

```csharp
var app = builder.AddViteApp("frontend", "./frontend")
    .WithEnvironment("NODE_ENV", "development")
    .WithEnvironment("VITE_FEATURE_FLAG", "true");
```

### WithHttpHealthCheck — Health Monitoring

```csharp
var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithHttpHealthCheck("/health");
```

---

## Monorepo Pattern

```
my-monorepo/
├── apphost.cs
├── packages/
│   ├── api/
│   │   ├── src/server.js
│   │   └── package.json
│   ├── web/
│   │   ├── src/App.tsx
│   │   ├── vite.config.ts
│   │   └── package.json
│   └── admin/
│       ├── src/main.ts
│       └── package.json
└── package.json (workspace root)
```

```csharp
#:sdk Aspire.AppHost.Sdk@13.1.0
#:package Aspire.Hosting.JavaScript@13.1.0
#:package Aspire.Hosting.Redis@13.1.0

var builder = DistributedApplication.CreateBuilder(args);

var cache = builder.AddRedis("cache");

var api = builder.AddNodeApp("api", "./packages/api", "src/server.js")
    .WithNpm()
    .WithHttpEndpoint(port: 3000, env: "PORT")
    .WithHttpHealthCheck("/health")
    .WithReference(cache);

var web = builder.AddViteApp("web", "./packages/web")
    .WithExternalHttpEndpoints()
    .WithReference(api)
    .WaitFor(api);

var admin = builder.AddViteApp("admin", "./packages/admin")
    .WithExternalHttpEndpoints()
    .WithReference(api)
    .WaitFor(api);

builder.Build().Run();
```

---

## Execution Context

The AppHost can behave differently in run vs publish mode:

```csharp
if (builder.ExecutionContext.IsRunMode)
{
    // Development: use local containers
    var db = builder.AddPostgres("db").AddDatabase("mydb");
}
else
{
    // Production: use Azure
    var db = builder.AddAzurePostgresFlexibleServer("db").AddDatabase("mydb");
}
```

---

## Parameters & Secrets

```csharp
// Define parameters (prompted if not configured)
var apiKey = builder.AddParameter("api-key", secret: true);

var app = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithEnvironment("API_KEY", apiKey);
```

Configure via user secrets:
```bash
dotnet user-secrets set "Parameters:api-key" "my-secret-value" --project ./AppHost
```

Or via `appsettings.json`:
```json
{
  "Parameters": {
    "api-key": "my-value"
  }
}
```

---

## Container Resources Alongside JS Apps

```csharp
// Redis
var cache = builder.AddRedis("cache")
    .WithRedisInsight()          // Add Redis Insights UI
    .WithDataVolume();           // Persist data across restarts

// PostgreSQL
var postgres = builder.AddPostgres("postgres")
    .WithPgAdmin()               // Add pgAdmin UI
    .WithDataVolume();
var db = postgres.AddDatabase("appdb");

// Custom container
var meilisearch = builder.AddContainer("search", "getmeili/meilisearch", "latest")
    .WithHttpEndpoint(port: 7700, targetPort: 7700);
```
