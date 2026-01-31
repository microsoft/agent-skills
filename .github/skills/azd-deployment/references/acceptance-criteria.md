# Azure Developer CLI (azd) Deployment Acceptance Criteria

**Tool**: `azd` (Azure Developer CLI)
**Repository**: https://github.com/Azure/azure-dev
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. azure.yaml Configuration

### 1.1 Service Configuration

#### ✅ CORRECT: Minimal Container App Service
```yaml
name: my-project
services:
  backend:
    project: ./src/backend
    language: python
    host: containerapp
    docker:
      path: ./Dockerfile
      remoteBuild: true
```

#### ✅ CORRECT: Full Service with Context
```yaml
services:
  frontend:
    project: ./src/frontend
    language: ts
    host: containerapp
    docker:
      path: ./Dockerfile
      context: .
      remoteBuild: true
```

#### ❌ INCORRECT: Missing host specification
```yaml
services:
  backend:
    project: ./src/backend
    language: python
    docker:
      path: ./Dockerfile
```

#### ❌ INCORRECT: Local build without Docker config
```yaml
services:
  backend:
    project: ./src/backend
    host: containerapp
```

---

## 2. Bicep Infrastructure

### 2.1 Main Bicep File

#### ✅ CORRECT: Parameterized main.bicep
```bicep
targetScope = 'subscription'

@minLength(1)
@maxLength(64)
param environmentName string

@minLength(1)
param location string

param resourceGroupName string = ''

var abbrs = loadJsonContent('./abbreviations.json')
var tags = { 'azd-env-name': environmentName }

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}
```

#### ❌ INCORRECT: Hardcoded values
```bicep
targetScope = 'subscription'

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'my-hardcoded-rg'
  location: 'eastus'
}
```

### 2.2 Container App Module

#### ✅ CORRECT: Container App with Environment
```bicep
param name string
param location string = resourceGroup().location
param tags object = {}
param containerAppsEnvironmentId string
param containerRegistryName string
param imageName string

resource app 'Microsoft.App/containerApps@2023-05-01' = {
  name: name
  location: location
  tags: union(tags, { 'azd-service-name': name })
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
      }
    }
    template: {
      containers: [
        {
          image: imageName
          name: name
        }
      ]
    }
  }
}

output uri string = 'https://${app.properties.configuration.ingress.fqdn}'
```

#### ❌ INCORRECT: Missing azd-service-name tag
```bicep
resource app 'Microsoft.App/containerApps@2023-05-01' = {
  name: name
  location: location
  properties: {
    // Missing 'azd-service-name' tag breaks azd deploy
  }
}
```

---

## 3. Environment Variables

### 3.1 Parameter Injection

#### ✅ CORRECT: main.parameters.json
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environmentName": {
      "value": "${AZURE_ENV_NAME}"
    },
    "location": {
      "value": "${AZURE_LOCATION}"
    },
    "openAiEndpoint": {
      "value": "${AZURE_OPENAI_ENDPOINT}"
    }
  }
}
```

#### ✅ CORRECT: With default values
```json
{
  "parameters": {
    "location": {
      "value": "${AZURE_LOCATION=eastus2}"
    }
  }
}
```

#### ❌ INCORRECT: Hardcoded secrets
```json
{
  "parameters": {
    "apiKey": {
      "value": "sk-1234567890abcdef"
    }
  }
}
```

---

## 4. Hooks Configuration

### 4.1 Lifecycle Hooks

#### ✅ CORRECT: Pre/Post Hooks
```yaml
hooks:
  preprovision:
    shell: sh
    run: |
      echo "Setting up prerequisites..."
      
  postprovision:
    shell: sh
    run: |
      echo "Provisioning complete"
      echo "Setting up RBAC..."
      
  postdeploy:
    shell: sh
    run: |
      echo "Frontend: ${SERVICE_FRONTEND_URI}"
      echo "Backend: ${SERVICE_BACKEND_URI}"
```

#### ❌ INCORRECT: Windows-only hooks
```yaml
hooks:
  preprovision:
    shell: pwsh
    windows:
      run: |
        # Only works on Windows
```

---

## 5. CLI Commands

### 5.1 Authentication

#### ✅ CORRECT: Standard auth flow
```bash
azd auth login
azd auth login --use-device-code  # For headless environments
```

### 5.2 Environment Management

#### ✅ CORRECT: Environment setup
```bash
azd env new dev
azd env set AZURE_OPENAI_ENDPOINT "https://my-openai.openai.azure.com"
azd env select dev
```

#### ❌ INCORRECT: Hardcoded in commands
```bash
azd env set API_KEY "sk-hardcoded-key"
```

### 5.3 Deployment

#### ✅ CORRECT: Full deployment
```bash
azd up                    # Provision + deploy
azd provision             # Infrastructure only
azd deploy                # Application only
azd down --purge          # Clean up everything
```

---

## 6. Remote Build Configuration

### 6.1 ACR Remote Build

#### ✅ CORRECT: Remote build setup
```yaml
services:
  api:
    docker:
      remoteBuild: true   # Build in ACR, not locally
```

#### ❌ INCORRECT: Local build with large images
```yaml
services:
  api:
    docker:
      remoteBuild: false  # Requires Docker locally, slow for large images
```

---

## 7. Multi-Service Configuration

### 7.1 Frontend + Backend

#### ✅ CORRECT: Multi-service azure.yaml
```yaml
name: fullstack-app
services:
  frontend:
    project: ./src/frontend
    language: ts
    host: containerapp
    docker:
      path: ./Dockerfile
      remoteBuild: true
      
  backend:
    project: ./src/backend
    language: python
    host: containerapp
    docker:
      path: ./Dockerfile
      remoteBuild: true
```

#### ✅ CORRECT: Service references in Bicep outputs
```bicep
output SERVICE_FRONTEND_URI string = frontend.outputs.uri
output SERVICE_BACKEND_URI string = backend.outputs.uri
```
