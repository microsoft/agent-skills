# Azure.ResourceManager.ApiCenter SDK Acceptance Criteria (.NET)

**SDK**: `Azure.ResourceManager.ApiCenter`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/apicenter/Azure.ResourceManager.ApiCenter
**Package**: https://www.nuget.org/packages/Azure.ResourceManager.ApiCenter
**Purpose**: Skill testing acceptance criteria for validating generated C# code correctness

---

## 1. Correct Using Statements

### 1.1 Core Imports

#### ✅ CORRECT: Basic Client Imports
```csharp
using Azure;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ApiCenter;
using Azure.ResourceManager.ApiCenter.Models;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using Azure.ApiCenter;
using Azure.ResourceManager.ApiCenter.Client;
using ApiCenter;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Create ArmClient
```csharp
ArmClient client = new ArmClient(new DefaultAzureCredential());
```

### 2.2 ✅ CORRECT: Get Resource Group
```csharp
ResourceGroupResource resourceGroup = await client
    .GetDefaultSubscriptionAsync()
    .Result
    .GetResourceGroupAsync("my-resource-group");
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing credential
```csharp
// WRONG - Must provide credential
ArmClient client = new ArmClient();
```

#### ❌ INCORRECT: Wrong client type
```csharp
// WRONG - Use ArmClient, not ApiCenterClient
var client = new ApiCenterClient(endpoint, credential);
```

---

## 3. API Center Service Operations

### 3.1 ✅ CORRECT: Create API Center Service
```csharp
ApiCenterServiceCollection services = resourceGroup.GetApiCenterServices();

ApiCenterServiceData data = new ApiCenterServiceData(AzureLocation.EastUS)
{
    Identity = new ManagedServiceIdentity(ManagedServiceIdentityType.SystemAssigned)
};

ArmOperation<ApiCenterServiceResource> operation = await services
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-api-center", data);

ApiCenterServiceResource service = operation.Value;
```

### 3.2 ✅ CORRECT: Get Existing Service
```csharp
ApiCenterServiceResource service = await resourceGroup
    .GetApiCenterServiceAsync("my-api-center");
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing WaitUntil parameter
```csharp
// WRONG - CreateOrUpdateAsync requires WaitUntil
var operation = await services.CreateOrUpdateAsync("my-api-center", data);
```

#### ❌ INCORRECT: Wrong method name
```csharp
// WRONG - Method is CreateOrUpdateAsync, not CreateAsync
var operation = await services.CreateAsync(WaitUntil.Completed, "name", data);
```

---

## 4. Workspace Operations

### 4.1 ✅ CORRECT: Create Workspace
```csharp
ApiCenterWorkspaceCollection workspaces = service.GetApiCenterWorkspaces();

ApiCenterWorkspaceData workspaceData = new ApiCenterWorkspaceData
{
    Title = "Engineering APIs",
    Description = "APIs owned by the engineering team"
};

ArmOperation<ApiCenterWorkspaceResource> operation = await workspaces
    .CreateOrUpdateAsync(WaitUntil.Completed, "engineering", workspaceData);

ApiCenterWorkspaceResource workspace = operation.Value;
```

### 4.2 ✅ CORRECT: List Workspaces
```csharp
await foreach (ApiCenterWorkspaceResource workspace in service.GetApiCenterWorkspaces())
{
    Console.WriteLine($"Workspace: {workspace.Data.Title}");
}
```

---

## 5. API Operations

### 5.1 ✅ CORRECT: Create API
```csharp
ApiCenterApiCollection apis = workspace.GetApiCenterApis();

ApiCenterApiData apiData = new ApiCenterApiData
{
    Title = "Orders API",
    Description = "API for managing customer orders",
    Kind = ApiKind.Rest,
    LifecycleStage = ApiLifecycleStage.Production
};

ArmOperation<ApiCenterApiResource> operation = await apis
    .CreateOrUpdateAsync(WaitUntil.Completed, "orders-api", apiData);
```

### 5.2 ✅ CORRECT: Add Custom Metadata
```csharp
apiData.CustomProperties = BinaryData.FromObjectAsJson(new
{
    team = "orders-team",
    costCenter = "CC-1234"
});
```

### 5.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong API kind type
```csharp
// WRONG - Use ApiKind enum, not string
Kind = "REST"
```

---

## 6. API Version Operations

### 6.1 ✅ CORRECT: Create API Version
```csharp
ApiCenterApiVersionCollection versions = api.GetApiCenterApiVersions();

ApiCenterApiVersionData versionData = new ApiCenterApiVersionData
{
    Title = "v1.0.0",
    LifecycleStage = ApiLifecycleStage.Production
};

ArmOperation<ApiCenterApiVersionResource> operation = await versions
    .CreateOrUpdateAsync(WaitUntil.Completed, "v1-0-0", versionData);
```

---

## 7. API Definition Operations

### 7.1 ✅ CORRECT: Create and Import Definition
```csharp
ApiCenterApiDefinitionCollection definitions = version.GetApiCenterApiDefinitions();

ApiCenterApiDefinitionData definitionData = new ApiCenterApiDefinitionData
{
    Title = "OpenAPI Specification",
    Description = "Orders API OpenAPI 3.0 definition"
};

ArmOperation<ApiCenterApiDefinitionResource> operation = await definitions
    .CreateOrUpdateAsync(WaitUntil.Completed, "openapi", definitionData);

// Import specification
string openApiSpec = await File.ReadAllTextAsync("orders-api.yaml");

ApiSpecImportContent importContent = new ApiSpecImportContent
{
    Format = ApiSpecImportSourceFormat.Inline,
    Value = openApiSpec,
    Specification = new ApiSpecImportSpecification
    {
        Name = "openapi",
        Version = "3.0.1"
    }
};

await definition.ImportSpecificationAsync(WaitUntil.Completed, importContent);
```

### 7.2 ✅ CORRECT: Export Specification
```csharp
ArmOperation<ApiSpecExportResult> operation = await definition
    .ExportSpecificationAsync(WaitUntil.Completed);

ApiSpecExportResult result = operation.Value;
```

---

## 8. Environment Operations

### 8.1 ✅ CORRECT: Create Environment
```csharp
ApiCenterEnvironmentCollection environments = workspace.GetApiCenterEnvironments();

ApiCenterEnvironmentData envData = new ApiCenterEnvironmentData
{
    Title = "Production",
    Description = "Production environment",
    Kind = ApiCenterEnvironmentKind.Production,
    Server = new ApiCenterEnvironmentServer
    {
        ManagementPortalUris = { new Uri("https://portal.azure.com") }
    }
};

ArmOperation<ApiCenterEnvironmentResource> operation = await environments
    .CreateOrUpdateAsync(WaitUntil.Completed, "production", envData);
```

---

## 9. Deployment Operations

### 9.1 ✅ CORRECT: Create Deployment
```csharp
ApiCenterDeploymentCollection deployments = workspace.GetApiCenterDeployments();

ApiCenterDeploymentData deploymentData = new ApiCenterDeploymentData
{
    Title = "Orders API - Production",
    EnvironmentId = envResourceId,
    DefinitionId = definitionResourceId,
    State = ApiCenterDeploymentState.Active,
    Server = new ApiCenterDeploymentServer
    {
        RuntimeUris = { new Uri("https://api.example.com/orders") }
    }
};

ArmOperation<ApiCenterDeploymentResource> operation = await deployments
    .CreateOrUpdateAsync(WaitUntil.Completed, "orders-api-prod", deploymentData);
```

---

## 10. Metadata Schema Operations

### 10.1 ✅ CORRECT: Create Metadata Schema
```csharp
ApiCenterMetadataSchemaCollection schemas = service.GetApiCenterMetadataSchemas();

string jsonSchema = """
{
    "type": "object",
    "properties": {
        "team": { "type": "string" }
    }
}
""";

ApiCenterMetadataSchemaData schemaData = new ApiCenterMetadataSchemaData
{
    Schema = jsonSchema,
    AssignedTo =
    {
        new MetadataAssignment
        {
            Entity = MetadataAssignmentEntity.Api,
            Required = true
        }
    }
};

ArmOperation<ApiCenterMetadataSchemaResource> operation = await schemas
    .CreateOrUpdateAsync(WaitUntil.Completed, "api-metadata", schemaData);
```

---

## 11. Error Handling Patterns

### 11.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    ArmOperation<ApiCenterApiResource> operation = await apis
        .CreateOrUpdateAsync(WaitUntil.Completed, "my-api", apiData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("API already exists with conflicting configuration");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid request: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Azure error: {ex.Status} - {ex.Message}");
}
```

---

## 12. Key Types Reference

| Type | Purpose |
|------|---------|
| `ArmClient` | Entry point for all ARM operations |
| `ApiCenterServiceResource` | API Center service instance |
| `ApiCenterWorkspaceResource` | Logical grouping of APIs |
| `ApiCenterApiResource` | Individual API |
| `ApiCenterApiVersionResource` | Version of an API |
| `ApiCenterApiDefinitionResource` | API specification (OpenAPI, etc.) |
| `ApiCenterEnvironmentResource` | Deployment environment |
| `ApiCenterDeploymentResource` | API deployment to environment |
| `ApiCenterMetadataSchemaResource` | Custom metadata schema |

## 13. Enum Values Reference

### ApiKind
- `Rest`, `Graphql`, `Grpc`, `Soap`, `Webhook`, `Websocket`

### ApiLifecycleStage
- `Design`, `Development`, `Testing`, `Preview`, `Production`, `Deprecated`, `Retired`

### ApiCenterEnvironmentKind
- `Development`, `Testing`, `Staging`, `Production`

### ApiCenterDeploymentState
- `Active`, `Inactive`

---

## 14. Best Practices Summary

1. **Use ArmClient** — Entry point for all API Center operations
2. **Use async methods** — All operations should use `*Async` methods
3. **Use WaitUntil.Completed** — For synchronous operation completion
4. **Use CreateOrUpdateAsync** — For idempotent resource creation
5. **Navigate hierarchy** — Service → Workspace → API → Version → Definition
6. **Handle errors** — Use RequestFailedException with status code filtering
7. **Use enums** — ApiKind, ApiLifecycleStage instead of strings
8. **Tag resources** — Use tags for organization and cost tracking
