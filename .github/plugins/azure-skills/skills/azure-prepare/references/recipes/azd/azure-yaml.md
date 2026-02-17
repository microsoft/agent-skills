# azure.yaml Generation

Create `azure.yaml` in project root for AZD.

## Structure

### Basic (Bicep - default)

```yaml
name: <project-name>
metadata:
  template: azd-init

services:
  <service-name>:
    project: <path-to-source>
    language: <python|js|ts|java|dotnet|go>
    host: <containerapp|appservice|function|staticwebapp|aks>
```

### With Terraform Provider

```yaml
name: <project-name>
metadata:
  template: azd-init

# Specify Terraform as IaC provider
infra:
  provider: terraform
  path: ./infra

services:
  <service-name>:
    project: <path-to-source>
    language: <python|js|ts|java|dotnet|go>
    host: <containerapp|appservice|function|staticwebapp|aks>
```

> 💡 **Tip:** Omit `infra` section to use Bicep (default). Add `infra.provider: terraform` to use Terraform. See [terraform.md](terraform.md) for details.

## Host Types

| Host | Azure Service | Use For |
|------|---------------|---------|
| `containerapp` | Container Apps | APIs, microservices, workers |
| `appservice` | App Service | Traditional web apps |
| `function` | Azure Functions | Serverless functions |
| `staticwebapp` | Static Web Apps | SPAs, static sites |
| `aks` | AKS | Kubernetes workloads |

## Examples

### Container App with Bicep (default)

```yaml
name: myapp

services:
  api:
    project: ./src/api
    language: python
    host: containerapp
    docker:
      path: ./src/api/Dockerfile
```

### Container App with Terraform

```yaml
name: myapp

infra:
  provider: terraform
  path: ./infra

services:
  api:
    project: ./src/api
    language: python
    host: containerapp
    docker:
      path: ./src/api/Dockerfile
```

### Azure Functions

```yaml
services:
  functions:
    project: ./src/functions
    language: js
    host: function
```

### Static Web App (with framework build)

For React, Vue, Angular, Next.js, etc. that require `npm run build`:

```yaml
services:
  web:
    project: ./src/web     # folder containing package.json
    language: js           # triggers: npm install && npm run build
    host: staticwebapp
    dist: dist             # build output folder (e.g., dist, build, out)
```

### Static Web App (pure HTML/CSS - no build)

For pure HTML sites without a framework build step:

**Static files in subfolder (recommended):**
```yaml
services:
  web:
    project: ./src/web     # folder containing index.html
    host: staticwebapp
    dist: .                # works when project != root
```

**Static files in root - requires build script:**

> ⚠️ **SWA CLI Limitation:** When `project: .`, you cannot use `dist: .`. Files must be copied to a separate output folder.

Add a minimal `package.json` with a build script:
```json
{
  "scripts": {
    "build": "node -e \"require('fs').mkdirSync('public',{recursive:true});require('fs').readdirSync('.').filter(f=>/\\.(html|css|js|png|jpe?g|gif|svg|ico|json|xml|txt|webmanifest|map)$/i.test(f)).forEach(f=>require('fs').copyFileSync(f,'public/'+f))\""
  }
}
```

Then configure azure.yaml with `language: js` to trigger the build:
```yaml
services:
  web:
    project: .
    language: js           # triggers npm install && npm run build
    host: staticwebapp
    dist: public
```

### SWA Project Structure Detection

| Layout | Configuration |
|--------|---------------|
| Static in root | `project: .`, `language: js`, `dist: public` + package.json build script |
| Framework in root | `project: .`, `language: js`, `dist: <output>` |
| Static in subfolder | `project: ./path`, `dist: .` |
| Framework in subfolder | `project: ./path`, `language: js`, `dist: <output>` |

> **Key rules:**
> - `dist` is **relative to `project`** path
> - **SWA CLI limitation**: When `project: .`, cannot use `dist: .` - must use a distinct folder
> - For static files in root, add `package.json` with build script to copy files to dist folder
> - Use `language: js` to trigger npm build even for pure static sites in root
> - `language: html` and `language: static` are **NOT valid** - will fail

### SWA Bicep Requirement

Bicep must include the `azd-service-name` tag:
```bicep
resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: name
  location: location
  tags: union(tags, { 'azd-service-name': 'web' })}
```
}
```

### App Service

```yaml
services:
  api:
    project: ./src/api
    language: dotnet
    host: appservice
```

## Hooks (Optional)

```yaml
hooks:
  preprovision:
    shell: sh
    run: ./scripts/setup.sh
  postprovision:
    shell: sh
    run: ./scripts/seed-data.sh
```

## Valid Values

| Field | Options |
|-------|---------|
| `language` | python, js, ts, java, dotnet, go (omit for staticwebapp without build) |
| `host` | containerapp, appservice, function, staticwebapp, aks |

## Output

- `./azure.yaml`
