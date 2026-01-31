# Azure Developer CLI (azd) Deployment Acceptance Criteria

**Skill**: `azd-deployment`
**Purpose**: Deploy containerized applications to Azure Container Apps using Azure Developer CLI (azd)
**Focus**: `azure.yaml` configuration, Bicep templates, Container Apps deployment, `azd up` workflow

---

## 1. azure.yaml Configuration

### 1.1 ✅ CORRECT: Basic Service Configuration

```yaml
name: my-app
services:
  backend:
    project: ./src/backend
    language: python
    host: containerapp
    docker:
      path: ./Dockerfile
      remoteBuild: true
```

### 1.2 ✅ CORRECT: Full Configuration with Hooks

```yaml
name: my-app
metadata:
  template: my-project@1.0.0

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
      echo "Before provisioning..."

  postprovision:
    shell: sh
    run: |
      echo "After provisioning"

  postdeploy:
    shell: sh
    run: |
      echo "Frontend: ${SERVICE_FRONTEND_URI}"
```

### 1.3 ❌ INCORRECT: Missing remoteBuild

```yaml
# WRONG - Missing remoteBuild: true causes issues on ARM Macs
services:
  backend:
    project: ./src/backend
    language: python
    host: containerapp
    docker:
      path: ./Dockerfile
```

### 1.4 ❌ INCORRECT: Wrong host type

```yaml
# WRONG - Using appservice instead of containerapp
services:
  backend:
    project: ./src/backend
    host: appservice  # Should be containerapp
```

---

## 2. Bicep Infrastructure Patterns

### 2.1 ✅ CORRECT: Container App Module

```bicep
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  tags: {
    'azd-service-name': serviceName
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    environmentId: containerAppEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
      }
      registries: [
        {
          server: containerRegistryLoginServer
          identity: 'system'
        }
      ]
    }
    template: {
      containers: [
        {
          name: containerAppName
          image: imageName
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: envVars
        }
      ]
    }
  }
}

output uri string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output principalId string = containerApp.identity.principalId
```

### 2.2 ✅ CORRECT: Parameter Injection from Environment

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environmentName": { "value": "${AZURE_ENV_NAME}" },
    "location": { "value": "${AZURE_LOCATION=eastus2}" },
    "azureOpenAiEndpoint": { "value": "${AZURE_OPENAI_ENDPOINT}" }
  }
}
```

### 2.3 ✅ CORRECT: azd Service Tag for Discovery

```bicep
tags: {
  'azd-service-name': serviceName  // Required for azd to find Container Apps
}
```

### 2.4 ❌ INCORRECT: Missing azd-service-name Tag

```bicep
// WRONG - Missing the required tag for azd
tags: {
  'environment': 'production'
}
// azd won't be able to find this Container App
```

### 2.5 ❌ INCORRECT: Hardcoded Values

```bicep
// WRONG - Hardcoded location
location: 'eastus2'  // Should use parameter

// WRONG - Hardcoded credentials
env: [
  {
    name: 'API_KEY'
    value: 'sk-12345'  // NEVER hardcode secrets
  }
]
```

---

## 3. Environment Variable Management

### 3.1 ✅ CORRECT: Using azd env set

```bash
# Set environment variables for deployment
azd env set AZURE_OPENAI_ENDPOINT "https://my-openai.openai.azure.com"
azd env set AZURE_SEARCH_ENDPOINT "https://my-search.search.windows.net"
```

### 3.2 ✅ CORRECT: Bicep Output to Environment

```bicep
// Outputs auto-populate .azure/<env>/.env
output SERVICE_FRONTEND_URI string = frontend.outputs.uri
output SERVICE_BACKEND_URI string = backend.outputs.uri
output BACKEND_PRINCIPAL_ID string = backend.outputs.principalId
```

### 3.3 ❌ INCORRECT: Editing .azure/<env>/.env Manually

```bash
# WRONG - Never manually edit azd-managed files
echo "MY_VAR=value" >> .azure/dev/.env
# Use azd env set instead
```

---

## 4. Deployment Commands

### 4.1 ✅ CORRECT: Full Deployment Flow

```bash
# Initialize project
azd auth login
azd init
azd env new dev

# Set environment-specific values
azd env set AZURE_OPENAI_ENDPOINT "https://..."

# Deploy everything
azd up
```

### 4.2 ✅ CORRECT: Deploy Single Service

```bash
# Deploy only the backend service
azd deploy --service backend
```

### 4.3 ✅ CORRECT: Separate Provision and Deploy

```bash
# Infrastructure only
azd provision

# Code deployment only
azd deploy
```

### 4.4 ❌ INCORRECT: Using az CLI Instead of azd

```bash
# WRONG - Don't mix az and azd for container app deployment
az containerapp up --name my-app
# Should use azd deploy
```

---

## 5. Hooks and Post-Deployment

### 5.1 ✅ CORRECT: Post-Provision RBAC Assignment

```yaml
hooks:
  postprovision:
    shell: sh
    run: |
      PRINCIPAL_ID="${BACKEND_PRINCIPAL_ID}"
      
      # Azure OpenAI access
      az role assignment create \
        --assignee-object-id "$PRINCIPAL_ID" \
        --assignee-principal-type ServicePrincipal \
        --role "Cognitive Services OpenAI User" \
        --scope "$OPENAI_RESOURCE_ID" 2>/dev/null || true
```

### 5.2 ✅ CORRECT: Hook Error Handling

```yaml
hooks:
  postprovision:
    shell: sh
    run: |
      # Use || true to prevent "already exists" from failing deploy
      az role assignment create ... 2>/dev/null || true
```

### 5.3 ❌ INCORRECT: Missing Error Suppression

```yaml
# WRONG - RBAC "already exists" errors will fail the deployment
hooks:
  postprovision:
    shell: sh
    run: |
      az role assignment create \
        --assignee-object-id "$PRINCIPAL_ID" \
        --role "Cognitive Services OpenAI User" \
        --scope "$OPENAI_RESOURCE_ID"
      # Missing || true
```

---

## 6. Container Apps Service Discovery

### 6.1 ✅ CORRECT: Internal Service Communication

```bicep
// In frontend env vars, reference backend via internal DNS
env: [
  {
    name: 'BACKEND_URL'
    value: 'http://ca-backend-${resourceToken}'  // Internal DNS
  }
]
```

### 6.2 ❌ INCORRECT: Using External URL for Internal Communication

```bicep
// WRONG - Using external URL for service-to-service communication
env: [
  {
    name: 'BACKEND_URL'
    value: 'https://ca-backend.azurecontainerapps.io'  // Should use internal DNS
  }
]
```

---

## 7. Project Structure

### 7.1 ✅ CORRECT: Standard azd Project Structure

```
project/
├── azure.yaml              # azd service definitions
├── infra/
│   ├── main.bicep          # Root infrastructure module
│   ├── main.parameters.json # Parameter injection
│   └── modules/
│       ├── container-apps-environment.bicep
│       └── container-app.bicep
├── .azure/
│   └── <env-name>/
│       └── .env            # azd-managed environment values
└── src/
    ├── frontend/
    │   └── Dockerfile
    └── backend/
        └── Dockerfile
```

### 7.2 ❌ INCORRECT: Missing infra Directory

```
# WRONG - Missing infrastructure definition
project/
├── azure.yaml
└── src/
    └── backend/
        └── Dockerfile
# No infra/ directory - azd can't provision
```

---

## 8. Managed Identity Configuration

### 8.1 ✅ CORRECT: System-Assigned Identity

```bicep
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  identity: {
    type: 'SystemAssigned'
  }
}

// Export principal ID for RBAC assignments
output principalId string = containerApp.identity.principalId
```

### 8.2 ✅ CORRECT: ACR Pull with Managed Identity

```bicep
configuration: {
  registries: [
    {
      server: containerRegistryLoginServer
      identity: 'system'  // Use managed identity for ACR pull
    }
  ]
}
```

### 8.3 ❌ INCORRECT: Using Admin Credentials for ACR

```bicep
// WRONG - Don't use admin credentials
configuration: {
  registries: [
    {
      server: containerRegistryLoginServer
      username: registryUsername
      passwordSecretRef: 'acr-password'  // Should use managed identity
    }
  ]
}
```

---

## 9. Anti-Patterns Summary

| Anti-Pattern | Impact | Fix |
|--------------|--------|-----|
| Missing `remoteBuild: true` | Build fails on ARM Macs | Add `remoteBuild: true` to docker config |
| Missing `azd-service-name` tag | azd can't discover Container Apps | Add tag to Bicep resource |
| Hardcoded secrets in Bicep | Security vulnerability | Use `azd env set` and Key Vault |
| Manual `.azure/.env` edits | Values overwritten by azd | Use `azd env set` |
| Missing `|| true` in hooks | RBAC errors fail deployment | Add error suppression |
| External URLs for internal services | Unnecessary network hops | Use internal DNS |
| ACR admin credentials | Security risk | Use managed identity |

---

## 10. Checklist for azd Deployment

- [ ] `azure.yaml` has `remoteBuild: true` for all services
- [ ] `host: containerapp` specified for Container Apps
- [ ] `infra/` directory contains Bicep modules
- [ ] `main.parameters.json` uses `${VAR}` syntax for env injection
- [ ] All Container Apps have `azd-service-name` tag
- [ ] System-assigned managed identity enabled
- [ ] ACR pull uses managed identity, not admin credentials
- [ ] Hooks use `|| true` for idempotent RBAC assignments
- [ ] Internal service communication uses internal DNS
- [ ] No hardcoded credentials or endpoints in Bicep
- [ ] Environment-specific values set via `azd env set`
