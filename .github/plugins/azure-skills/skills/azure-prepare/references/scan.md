# Codebase Scan

Analyze workspace to identify components, technologies, and dependencies.

## Detection Patterns

### Languages & Frameworks

| File | Indicates |
|------|-----------|
| `package.json` | Node.js |
| `requirements.txt`, `pyproject.toml` | Python |
| `*.csproj`, `*.sln` | .NET |
| `pom.xml`, `build.gradle` | Java |
| `go.mod` | Go |

### Component Types

| Pattern | Component Type |
|---------|----------------|
| React/Vue/Angular in package.json | SPA Frontend |
| Only .html/.css/.js files, no package.json | Pure Static Site |
| Express/Fastify/Koa | API Service |
| Flask/FastAPI/Django | API Service |
| Next.js/Nuxt | SSR Web App |
| Celery/Bull/Agenda | Background Worker |
| azure-functions SDK | Azure Function |

**Pure Static Site Detection:**
- No package.json, requirements.txt, or build configuration
- Contains only HTML, CSS, JavaScript, and asset files
- No framework dependencies (React, Vue, Angular, etc.)
- ⚠️ For pure static sites, do NOT add `language` field to azure.yaml to avoid triggering build steps

### Existing Tooling

| Found | Tooling |
|-------|---------|
| `azure.yaml` | AZD configured |
| `infra/*.bicep` | Bicep IaC |
| `infra/*.tf` | Terraform IaC |
| `Dockerfile` | Containerized |
| `.github/workflows/` | GitHub Actions CI/CD |
| `azure-pipelines.yml` | Azure DevOps CI/CD |

## Output

Document findings:

```markdown
## Components

| Component | Type | Technology | Path |
|-----------|------|------------|------|
| api | API Service | Node.js/Express | src/api |
| web | SPA | React | src/web |
| worker | Background | Python | src/worker |

## Dependencies

| Component | Depends On | Type |
|-----------|-----------|------|
| api | PostgreSQL | Database |
| web | api | HTTP |
| worker | Service Bus | Queue |

## Existing Infrastructure

| Item | Status |
|------|--------|
| azure.yaml | Not found |
| infra/ | Not found |
| Dockerfiles | Found: src/api/Dockerfile |
```
