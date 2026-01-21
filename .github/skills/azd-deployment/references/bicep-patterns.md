# Bicep Patterns for Azure Container Apps

## Table of Contents

1. [Main Bicep Structure](#main-bicep-structure)
2. [Container Apps Environment Module](#container-apps-environment-module)
3. [Container App Module](#container-app-module)
4. [Resource Naming Conventions](#resource-naming-conventions)
5. [Environment Variables Pattern](#environment-variables-pattern)

---

## Main Bicep Structure

### Subscription-Scoped Deployment

```bicep
targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the resource group')
param resourceGroupName string = ''

// External service parameters
@description('Azure OpenAI service endpoint')
param azureOpenAiEndpoint string = ''

@description('Azure AI Search endpoint')
param azureSearchEndpoint string = ''

// Tags applied to all resources
var tags = {
  'azd-env-name': environmentName
  project: 'my-project'
}

// Generate unique suffix for resource names
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : 'rg-${environmentName}'
  location: location
  tags: tags
}

// Container Apps Environment (includes ACR and Log Analytics)
module containerAppsEnvironment 'modules/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  scope: rg
  params: {
    name: 'cae-${resourceToken}'
    location: location
    tags: tags
  }
}

// Backend Container App
module backend 'modules/container-app.bicep' = {
  name: 'backend'
  scope: rg
  params: {
    name: 'ca-backend-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'backend' })
    containerAppsEnvironmentId: containerAppsEnvironment.outputs.id
    containerRegistryName: containerAppsEnvironment.outputs.registryName
    containerImage: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
    targetPort: 8000
    env: [
      { name: 'AZURE_OPENAI_ENDPOINT', value: azureOpenAiEndpoint }
      { name: 'AZURE_SEARCH_ENDPOINT', value: azureSearchEndpoint }
    ]
  }
}

// Frontend Container App (depends on backend for internal URL)
module frontend 'modules/container-app.bicep' = {
  name: 'frontend'
  scope: rg
  params: {
    name: 'ca-frontend-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'frontend' })
    containerAppsEnvironmentId: containerAppsEnvironment.outputs.id
    containerRegistryName: containerAppsEnvironment.outputs.registryName
    containerImage: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
    targetPort: 80
    env: [
      { name: 'BACKEND_URL', value: 'http://ca-backend-${resourceToken}' }
    ]
  }
}

// Outputs - these auto-populate .azure/<env>/.env
output AZURE_LOCATION string = location
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerAppsEnvironment.outputs.registryEndpoint
output SERVICE_FRONTEND_URI string = frontend.outputs.uri
output SERVICE_BACKEND_URI string = backend.outputs.uri
output BACKEND_PRINCIPAL_ID string = backend.outputs.principalId
```

---

## Container Apps Environment Module

```bicep
// modules/container-apps-environment.bicep

@description('Name of the Container Apps environment')
param name string

@description('Location for the resource')
param location string = resourceGroup().location

@description('Tags for the resource')
param tags object = {}

// Log Analytics workspace for Container Apps
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'log-${name}'
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

// Container Registry for image storage
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: replace('acr${name}', '-', '')  // ACR names can't have hyphens
  location: location
  tags: tags
  sku: { name: 'Basic' }
  properties: {
    adminUserEnabled: true  // Required for Container Apps pull
  }
}

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

output id string = containerAppsEnvironment.id
output name string = containerAppsEnvironment.name
output registryEndpoint string = containerRegistry.properties.loginServer
output registryName string = containerRegistry.name
```

---

## Container App Module

```bicep
// modules/container-app.bicep

@description('Name of the Container App')
param name string

@description('Location for the resource')
param location string = resourceGroup().location

@description('Tags for the resource')
param tags object = {}

@description('Container Apps Environment ID')
param containerAppsEnvironmentId string

@description('Container Registry name')
param containerRegistryName string

@description('Container image to deploy')
param containerImage string

@description('Target port for the container')
param targetPort int = 80

@description('Environment variables')
param env array = []

@description('CPU cores')
param cpu string = '0.5'

@description('Memory')
param memory string = '1Gi'

@description('Minimum replicas')
param minReplicas int = 1

@description('Maximum replicas')
param maxReplicas int = 3

@description('Custom domains (empty preserves Portal-added domains)')
param customDomains array = []

// Reference existing ACR
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: containerRegistryName
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
        allowInsecure: false
        // null preserves existing Portal-added domains
        customDomains: empty(customDomains) ? null : customDomains
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          username: containerRegistry.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'main'
          image: containerImage
          resources: {
            cpu: json(cpu)
            memory: memory
          }
          env: env
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-scale-rule'
            http: {
              metadata: { concurrentRequests: '100' }
            }
          }
        ]
      }
    }
  }
}

output id string = containerApp.id
output name string = containerApp.name
output fqdn string = containerApp.properties.configuration.ingress.fqdn
output uri string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output principalId string = containerApp.identity.principalId
```

---

## Resource Naming Conventions

```bicep
// Generate unique, deterministic suffix
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

// Resource naming patterns
var names = {
  resourceGroup: 'rg-${environmentName}'
  containerAppsEnv: 'cae-${resourceToken}'
  containerRegistry: 'acr${replace(resourceToken, '-', '')}'  // No hyphens
  logAnalytics: 'log-cae-${resourceToken}'
  backendApp: 'ca-backend-${resourceToken}'
  frontendApp: 'ca-frontend-${resourceToken}'
}
```

---

## Environment Variables Pattern

### Passing Secrets via azd env

```bicep
// In main.bicep - reference from parameters
param azureOpenAiApiKey string = ''

// In container env
env: [
  {
    name: 'AZURE_OPENAI_API_KEY'
    secretRef: 'openai-key'  // Reference secret
  }
]

// In secrets array
secrets: [
  {
    name: 'openai-key'
    value: azureOpenAiApiKey
  }
]
```

### Using Key Vault References (Production)

```bicep
@description('Key Vault name')
param keyVaultName string

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' existing = {
  name: keyVaultName
}

// In container app secrets
secrets: [
  {
    name: 'openai-key'
    keyVaultUrl: '${keyVault.properties.vaultUri}secrets/openai-api-key'
    identity: 'system'
  }
]
```

### Static vs Dynamic Env Vars

```bicep
env: [
  // Static - known at deploy time
  { name: 'PORT', value: '8000' }
  
  // Dynamic - from parameters
  { name: 'AZURE_OPENAI_ENDPOINT', value: azureOpenAiEndpoint }
  
  // Internal service discovery
  { name: 'BACKEND_URL', value: 'http://ca-backend-${resourceToken}' }
  
  // Secret reference
  { name: 'API_KEY', secretRef: 'api-key-secret' }
]
```
