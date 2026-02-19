# Deployment & CI/CD for JavaScript/TypeScript Apps

How Aspire builds, publishes, and deploys JS/TS applications.

---

## Lifecycle Phases

| Phase | Command | JS/TS Apps Run As | Purpose |
|-------|---------|-------------------|---------|
| **Development** | `aspire run` | Node.js process | Local dev with dashboard |
| **Local Deploy** | `aspire deploy` | Docker container | Test containerized locally |
| **Publish** | `aspire publish` | Docker Compose artifacts | Generate deployment files |
| **CI/CD** | `aspire do push` | Container image push | Build & push to registry |

---

## Development: aspire run

```bash
aspire run
```

- JS/TS apps run as **Node.js processes** (not containers)
- Package manager installs deps automatically
- Dev script runs (e.g., `vite` or `node server.js`)
- Aspire dashboard provides logs, traces, metrics
- Hot reload works normally (Vite HMR, nodemon, etc.)

---

## Production Builds

When publishing, Aspire automatically:

1. **Generates a Dockerfile** for each JS/TS resource
2. **Installs dependencies** using deterministic commands:
   - npm: `npm ci` (if `package-lock.json` exists)
   - yarn: `yarn install --immutable` (v2+) or `--frozen-lockfile` (v1)
   - pnpm: `pnpm install --frozen-lockfile` (if `pnpm-lock.yaml` exists)
3. **Runs the build script** (typically `npm run build`)
4. **Creates a production container** with built assets

### Custom build script

```csharp
var app = builder.AddViteApp("frontend", "./frontend")
    .WithBuildScript("build:production");  // Instead of default "build"
```

---

## Docker Compose Deployment

### Generate artifacts

```bash
aspire publish --output-path ./aspire-output
```

Generates:
```
aspire-output/
├── docker-compose.yaml    # All services defined
└── .env                   # Environment variable template
```

### Deploy with Docker Compose

```bash
cd aspire-output
# Edit .env with production values
docker compose up -d
```

---

## Container Registry Integration

### Add registry to AppHost

```csharp
var endpoint = builder.AddParameter("registry-endpoint");
var repository = builder.AddParameter("registry-repository");
builder.AddContainerRegistry("container-registry", endpoint, repository);
```

### Push images via CI/CD

```bash
# Set parameters via environment variables
export Parameters__registry_endpoint=ghcr.io
export Parameters__registry_repository=myorg/myrepo

aspire do push
```

---

## GitHub Actions Workflow

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install Aspire CLI
        run: |
          curl -sSL https://aspire.dev/install.sh | bash
          echo "$HOME/.aspire/bin" >> $GITHUB_PATH

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push
        env:
          Parameters__registry_endpoint: ghcr.io
          Parameters__registry_repository: ${{ github.repository_owner }}/${{ github.event.repository.name }}
        run: aspire do push

      - name: Publish Artifacts
        run: aspire publish --output-path ./aspire-output

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: deployment-files
          path: ./aspire-output/
          include-hidden-files: true
```

---

## Azure Container Apps Deployment

### Publish as ACA

```csharp
// For .NET projects (JS apps are automatically containerized)
var api = builder.AddProject<Projects.Api>("api")
    .PublishAsAzureContainerApp<Projects.Api>((infra, app) => {
        // Customize ACA settings
    });
```

### Add ACA environment

```csharp
var acaEnv = builder.AddAzureContainerAppEnvironment("aca-env");
```

### Deploy to Azure

```bash
aspire deploy
```

Aspire will:
1. Build container images for all resources
2. Push to configured container registry
3. Generate Azure infrastructure (Bicep)
4. Deploy to Azure Container Apps

---

## Docker Compose with Volumes

For JS apps that need persistent storage:

```csharp
var app = builder.AddProject<Projects.Api>("api")
    .PublishAsDockerComposeService((resource, service) =>
    {
        service.AddVolume(new Volume
        {
            Name = "uploads",
            Source = "uploads",
            Target = "/app/uploads",
            Type = "volume",
            ReadOnly = false
        });
    });
```

---

## Environment Variables in Production

Parameters can be provided via environment variables in CI/CD:

```bash
# Parameter naming: Parameters__{parameter_name}
# Dashes in parameter names become underscores
export Parameters__registry_endpoint=ghcr.io
export Parameters__registry_repository=myorg/myrepo
export Parameters__api_key=secret-value
```

Priority order:
1. Environment variables (`Parameters__*`)
2. Configuration files (`appsettings.json`)
3. User prompts (interactive)

---

## Production Checklist

- [ ] Lockfiles committed (`package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`)
- [ ] Build script defined in `package.json`
- [ ] Health check endpoint exposed (`/health`)
- [ ] OpenTelemetry configured for production OTLP endpoint
- [ ] Container registry configured and authenticated
- [ ] Secrets stored securely (not in source code)
- [ ] Environment-specific config via parameters, not hardcoded
- [ ] Persistent volumes for stateful data
- [ ] HTTPS configured for external endpoints
