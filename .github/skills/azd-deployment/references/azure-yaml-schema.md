# azure.yaml Complete Schema Reference

## Table of Contents

1. [Root Properties](#root-properties)
2. [Services Configuration](#services-configuration)
3. [Infrastructure Configuration](#infrastructure-configuration)
4. [Hooks Configuration](#hooks-configuration)
5. [Complete Example](#complete-example)

---

## Root Properties

```yaml
# Required: Project name (used for resource naming)
name: my-project

# Optional: Template metadata
metadata:
  template: my-project@1.0.0

# Optional: Workflow customization
workflow:
  # Skip interactive prompts
  # NOTE: Requires env vars to be pre-set
  interactivity: "none"

# Optional: Default Azure settings
azure:
  location: eastus2  # Default region
```

---

## Services Configuration

### Minimal Service

```yaml
services:
  backend:
    project: ./src/backend     # Path to service code
    language: python           # python, ts, js, csharp, java, go
    host: containerapp         # containerapp, appservice, function, staticwebapp
```

### Full Service Options

```yaml
services:
  backend:
    # Required
    project: ./src/backend
    language: python
    host: containerapp

    # Docker configuration (for containerapp/appservice)
    docker:
      path: ./Dockerfile       # Relative to project path
      context: .               # Build context relative to project
      remoteBuild: true        # Build in Azure (recommended)
      # platform: linux/amd64  # Optional: target platform

    # Resource configuration
    resourceName: my-backend-app  # Override auto-generated name

    # Hooks specific to this service
    hooks:
      prepackage:
        shell: sh
        run: |
          echo "Before packaging..."
      
      postdeploy:
        shell: sh
        run: |
          echo "After deploying..."
```

### Service Languages

| Language | Value | Notes |
|----------|-------|-------|
| Python | `python` | Uses requirements.txt or pyproject.toml |
| TypeScript | `ts` | Uses package.json |
| JavaScript | `js` | Uses package.json |
| C# | `csharp` | Uses .csproj |
| Java | `java` | Uses pom.xml or build.gradle |
| Go | `go` | Uses go.mod |

### Service Hosts

| Host | Value | Description |
|------|-------|-------------|
| Container Apps | `containerapp` | Azure Container Apps |
| App Service | `appservice` | Azure App Service |
| Functions | `function` | Azure Functions |
| Static Web Apps | `staticwebapp` | Azure Static Web Apps |
| AKS | `aks` | Azure Kubernetes Service |

---

## Infrastructure Configuration

### Bicep Provider

```yaml
infra:
  provider: bicep
  path: ./infra              # Path to infra folder
  module: main               # Optional: main module name (default: main)
```

### Terraform Provider

```yaml
infra:
  provider: terraform
  path: ./infra
```

### Parameters Override

```yaml
infra:
  provider: bicep
  path: ./infra
  # Override parameters for specific environments
  parameters:
    - name: environmentName
      value: ${AZURE_ENV_NAME}
    - name: location
      value: eastus2
```

---

## Hooks Configuration

### Available Hook Points

| Hook | Timing | Use Case |
|------|--------|----------|
| `prerestore` | Before package restore | Pre-install setup |
| `postrestore` | After package restore | Post-install setup |
| `preprovision` | Before infra deployment | Save existing state |
| `postprovision` | After infra deployment | RBAC, DNS, config |
| `prepackage` | Before app packaging | Build steps |
| `postpackage` | After app packaging | Verification |
| `predeploy` | Before app deployment | Pre-deploy checks |
| `postdeploy` | After app deployment | Smoke tests, notifications |
| `predown` | Before resource deletion | Backup, confirmation |
| `postdown` | After resource deletion | Cleanup |

### Hook Properties

```yaml
hooks:
  postprovision:
    # Shell to use (sh, bash, pwsh, powershell)
    shell: sh
    
    # Inline script
    run: |
      echo "Running post-provision..."
      az role assignment create ...
    
    # OR external script
    # run: ./scripts/post-provision.sh
    
    # Continue on error (default: false)
    continueOnError: false
    
    # Run interactively (default: false)
    interactive: false
    
    # Working directory (default: project root)
    cwd: ./scripts
```

### Hook Environment Variables

Available in all hooks:

```bash
# Azure context
${AZURE_ENV_NAME}           # Current environment name
${AZURE_LOCATION}           # Deployment location
${AZURE_SUBSCRIPTION_ID}    # Subscription ID
${AZURE_RESOURCE_GROUP}     # Resource group name

# Service URLs (after provision/deploy)
${SERVICE_<NAME>_URI}       # e.g., SERVICE_BACKEND_URI
${SERVICE_<NAME>_IMAGE_NAME} # Full image path

# Bicep outputs (after provision)
# Any output from main.bicep becomes an env var
${BACKEND_PRINCIPAL_ID}     # If output in Bicep
```

### Service-Specific Hooks

```yaml
services:
  backend:
    project: ./src/backend
    hooks:
      predeploy:
        shell: sh
        run: |
          echo "Deploying backend..."
```

---

## Complete Example

```yaml
# azure.yaml - Full configuration example
name: wef-foundry-demos

metadata:
  template: wef-foundry-demos@1.0.0

infra:
  provider: bicep
  path: ./infra

azure:
  location: eastus2

services:
  frontend:
    project: ./src/frontend
    language: ts
    host: containerapp
    docker:
      path: ./Dockerfile
      context: .
      remoteBuild: true

  backend:
    project: ./src/backend
    language: python
    host: containerapp
    docker:
      path: ./Dockerfile
      context: .
      remoteBuild: true

hooks:
  preprovision:
    shell: sh
    run: |
      echo "=== Pre-Provision ==="
      # Save custom domains before provision might reset them
      FRONTEND_NAME="ca-frontend-$(echo ${AZURE_ENV_NAME} | tr '[:upper:]' '[:lower:]')"
      RG_NAME="${AZURE_RESOURCE_GROUP:-rg-${AZURE_ENV_NAME}}"
      
      if az containerapp show -n "$FRONTEND_NAME" -g "$RG_NAME" &>/dev/null; then
        az containerapp show -n "$FRONTEND_NAME" -g "$RG_NAME" \
          --query "properties.configuration.ingress.customDomains" \
          -o json > /tmp/domains.json 2>/dev/null || echo "[]" > /tmp/domains.json
      fi

  postprovision:
    shell: sh
    run: |
      echo "=== Post-Provision ==="
      echo "Setting up RBAC for managed identity..."
      
      PRINCIPAL_ID="${BACKEND_PRINCIPAL_ID}"
      
      if [ -n "$PRINCIPAL_ID" ]; then
        # Azure OpenAI access
        if [ -n "$AZURE_OPENAI_ENDPOINT" ]; then
          OPENAI_NAME=$(echo "$AZURE_OPENAI_ENDPOINT" | sed 's|https://||' | sed 's|\..*||')
          OPENAI_ID=$(az cognitiveservices account list \
            --query "[?name=='$OPENAI_NAME'].id" -o tsv 2>/dev/null | head -1)
          
          if [ -n "$OPENAI_ID" ]; then
            az role assignment create \
              --assignee-object-id "$PRINCIPAL_ID" \
              --assignee-principal-type ServicePrincipal \
              --role "Cognitive Services OpenAI User" \
              --scope "$OPENAI_ID" 2>/dev/null || echo "Role may already exist"
          fi
        fi
        
        # Azure AI Search access
        if [ -n "$AZURE_SEARCH_ENDPOINT" ]; then
          SEARCH_NAME=$(echo "$AZURE_SEARCH_ENDPOINT" | sed 's|https://||' | sed 's|\..*||')
          SEARCH_ID=$(az resource list \
            --resource-type "Microsoft.Search/searchServices" \
            --query "[?name=='$SEARCH_NAME'].id" -o tsv 2>/dev/null | head -1)
          
          if [ -n "$SEARCH_ID" ]; then
            az role assignment create \
              --assignee-object-id "$PRINCIPAL_ID" \
              --assignee-principal-type ServicePrincipal \
              --role "Search Index Data Reader" \
              --scope "$SEARCH_ID" 2>/dev/null || true
          fi
        fi
        
        echo "RBAC setup complete."
      fi

  predeploy:
    shell: sh
    run: |
      echo "=== Pre-Deploy ==="
      echo "Building and deploying services..."

  postdeploy:
    shell: sh
    run: |
      echo ""
      echo "=========================================="
      echo "         Deployment Complete!            "
      echo "=========================================="
      echo ""
      echo "Frontend: ${SERVICE_FRONTEND_URI}"
      echo "Backend:  ${SERVICE_BACKEND_URI}"
      echo ""
      echo "Health:   ${SERVICE_BACKEND_URI}/api/health"
      echo ""
```

---

## Environment-Specific Configuration

### Using Multiple Environments

```bash
# Create environments
azd env new dev
azd env new staging  
azd env new prod

# Set environment-specific values
azd env select dev
azd env set AZURE_OPENAI_ENDPOINT "https://dev-openai.openai.azure.com"

azd env select prod
azd env set AZURE_OPENAI_ENDPOINT "https://prod-openai.openai.azure.com"

# Deploy specific environment
azd env select prod
azd up
```

### Environment Files

```
.azure/
├── config.json              # {"defaultEnvironment": "prod"}
├── dev/
│   ├── .env                 # Auto-generated from Bicep outputs
│   └── config.json          # Environment metadata
├── staging/
│   ├── .env
│   └── config.json
└── prod/
    ├── .env
    └── config.json
```
