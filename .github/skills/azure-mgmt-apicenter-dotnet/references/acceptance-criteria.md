# Azure API Center SDK Acceptance Criteria

**SDK**: `Azure.ResourceManager.ApiCenter`  
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/apicenter/Azure.ResourceManager.ApiCenter  
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Full namespace imports
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ApiCenter;
using Azure.ResourceManager.ApiCenter.Models;
```

#### ❌ INCORRECT: Missing required namespaces
```csharp
using Azure.ResourceManager.ApiCenter;
// Missing Azure.Identity, Azure.ResourceManager
```

### 1.2 Model Imports
#### ✅ CORRECT: Models namespace for data types
```csharp
using Azure.ResourceManager.ApiCenter.Models;

ApiKind kind = ApiKind.Rest;
ApiLifecycleStage stage = ApiLifecycleStage.Production;
```

#### ❌ INCORRECT: Using fully qualified names unnecessarily
```csharp
Azure.ResourceManager.ApiCenter.Models.ApiKind kind = Azure.ResourceManager.ApiCenter.Models.ApiKind.Rest;
```

---

## 2. Client Creation

### 2.1 ArmClient Initialization
#### ✅ CORRECT: Using DefaultAzureCredential
```csharp
ArmClient client = new ArmClient(new DefaultAzureCredential());
```

#### ❌ INCORRECT: Hardcoded credentials
```csharp
ArmClient client = new ArmClient(new ClientSecretCredential(tenantId, clientId, clientSecret));
```

### 2.2 Resource Group Access
#### ✅ CORRECT: Async navigation through hierarchy
```csharp
ResourceGroupResource resourceGroup = await client
    .GetDefaultSubscriptionAsync()
    .Result
    .GetResourceGroupAsync("my-resource-group");
```

#### ❌ INCORRECT: Synchronous blocking calls
```csharp
var resourceGroup = client.GetDefaultSubscription().GetResourceGroup("my-resource-group");
```

---

## 3. Core Operations

### 3.1 Create API Center Service
#### ✅ CORRECT: Using CreateOrUpdateAsync with WaitUntil
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

#### ❌ INCORRECT: Missing WaitUntil parameter
```csharp
var operation = await services.CreateOrUpdateAsync("my-api-center", data);
```

### 3.2 Create Workspace
#### ✅ CORRECT: Proper workspace data initialization
```csharp
ApiCenterWorkspaceCollection workspaces = service.GetApiCenterWorkspaces();

ApiCenterWorkspaceData workspaceData = new ApiCenterWorkspaceData
{
    Title = "Engineering APIs",
    Description = "APIs owned by the engineering team"
};

ArmOperation<ApiCenterWorkspaceResource> operation = await workspaces
    .CreateOrUpdateAsync(WaitUntil.Completed, "engineering", workspaceData);
```

#### ❌ INCORRECT: Using wrong resource type
```csharp
var workspace = new ApiCenterApiData { Title = "Engineering APIs" };
```

### 3.3 Create API
#### ✅ CORRECT: Full API configuration with metadata
```csharp
ApiCenterApiCollection apis = workspace.GetApiCenterApis();

ApiCenterApiData apiData = new ApiCenterApiData
{
    Title = "Orders API",
    Description = "API for managing customer orders",
    Kind = ApiKind.Rest,
    LifecycleStage = ApiLifecycleStage.Production,
    Contacts =
    {
        new ApiContact
        {
            Name = "API Support",
            Email = "api-support@example.com"
        }
    }
};

apiData.CustomProperties = BinaryData.FromObjectAsJson(new
{
    team = "orders-team",
    costCenter = "CC-1234"
});

ArmOperation<ApiCenterApiResource> operation = await apis
    .CreateOrUpdateAsync(WaitUntil.Completed, "orders-api", apiData);
```

#### ❌ INCORRECT: Missing required Kind property
```csharp
ApiCenterApiData apiData = new ApiCenterApiData
{
    Title = "Orders API"
    // Missing Kind - required property
};
```

### 3.4 Create API Version
#### ✅ CORRECT: Version with lifecycle stage
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

#### ❌ INCORRECT: Accessing versions from wrong parent
```csharp
var versions = workspace.GetApiCenterApiVersions(); // Wrong - should be from API
```

### 3.5 Import API Definition
#### ✅ CORRECT: Using ApiSpecImportContent
```csharp
ApiCenterApiDefinitionCollection definitions = version.GetApiCenterApiDefinitions();

ApiCenterApiDefinitionData definitionData = new ApiCenterApiDefinitionData
{
    Title = "OpenAPI Specification",
    Description = "Orders API OpenAPI 3.0 definition"
};

ArmOperation<ApiCenterApiDefinitionResource> operation = await definitions
    .CreateOrUpdateAsync(WaitUntil.Completed, "openapi", definitionData);

ApiCenterApiDefinitionResource definition = operation.Value;

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

#### ❌ INCORRECT: Setting spec content directly on definition data
```csharp
ApiCenterApiDefinitionData definitionData = new ApiCenterApiDefinitionData
{
    Title = "OpenAPI Specification",
    Value = openApiSpec  // Wrong property
};
```

---

## 4. Resource Hierarchy Navigation

### 4.1 Correct Hierarchy
#### ✅ CORRECT: Following Service → Workspace → API → Version → Definition
```csharp
// Service level
ApiCenterServiceResource service = await resourceGroup.GetApiCenterServiceAsync("my-service");

// Workspace level
ApiCenterWorkspaceResource workspace = await service.GetApiCenterWorkspaceAsync("default");

// API level
ApiCenterApiResource api = await workspace.GetApiCenterApiAsync("my-api");

// Version level
ApiCenterApiVersionResource version = await api.GetApiCenterApiVersionAsync("v1-0-0");

// Definition level
ApiCenterApiDefinitionResource definition = await version.GetApiCenterApiDefinitionAsync("openapi");
```

#### ❌ INCORRECT: Skipping hierarchy levels
```csharp
// Cannot access API directly from service
var api = await service.GetApiCenterApiAsync("my-api");
```

---

## 5. Environment and Deployment

### 5.1 Create Environment
#### ✅ CORRECT: Environment with onboarding details
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
    },
    Onboarding = new EnvironmentOnboardingModel
    {
        Instructions = "Contact platform team for access",
        DeveloperPortalUris = { new Uri("https://developer.example.com") }
    }
};

ArmOperation<ApiCenterEnvironmentResource> operation = await environments
    .CreateOrUpdateAsync(WaitUntil.Completed, "production", envData);
```

#### ❌ INCORRECT: Missing Kind property
```csharp
ApiCenterEnvironmentData envData = new ApiCenterEnvironmentData
{
    Title = "Production"
    // Missing Kind
};
```

### 5.2 Create Deployment
#### ✅ CORRECT: Linking environment and definition by resource ID
```csharp
ResourceIdentifier envResourceId = ApiCenterEnvironmentResource.CreateResourceIdentifier(
    subscriptionId, resourceGroupName, serviceName, workspaceName, "production");

ResourceIdentifier definitionResourceId = ApiCenterApiDefinitionResource.CreateResourceIdentifier(
    subscriptionId, resourceGroupName, serviceName, workspaceName, 
    "orders-api", "v1-0-0", "openapi");

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
```

#### ❌ INCORRECT: Using string IDs instead of ResourceIdentifier
```csharp
ApiCenterDeploymentData deploymentData = new ApiCenterDeploymentData
{
    EnvironmentId = "/subscriptions/.../environments/production",  // Wrong - use ResourceIdentifier
    DefinitionId = "openapi"  // Wrong - needs full resource ID
};
```

---

## 6. Metadata Schema

### 6.1 Create Custom Metadata Schema
#### ✅ CORRECT: JSON Schema with assignments
```csharp
ApiCenterMetadataSchemaCollection schemas = service.GetApiCenterMetadataSchemas();

string jsonSchema = """
{
    "type": "object",
    "properties": {
        "team": { "type": "string", "title": "Owning Team" },
        "costCenter": { "type": "string", "title": "Cost Center" }
    },
    "required": ["team"]
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

#### ❌ INCORRECT: Invalid JSON schema format
```csharp
ApiCenterMetadataSchemaData schemaData = new ApiCenterMetadataSchemaData
{
    Schema = "team: string"  // Wrong - must be valid JSON Schema
};
```

---

## 7. Listing and Enumeration

### 7.1 List Resources
#### ✅ CORRECT: Using async enumeration
```csharp
await foreach (ApiCenterApiResource api in workspace.GetApiCenterApis())
{
    Console.WriteLine($"API: {api.Data.Title}");
    Console.WriteLine($"  Kind: {api.Data.Kind}");
    Console.WriteLine($"  Stage: {api.Data.LifecycleStage}");
}
```

#### ❌ INCORRECT: Converting to list synchronously
```csharp
var apis = workspace.GetApiCenterApis().ToList();  // Wrong - blocks async
```

---

## 8. Error Handling

### 8.1 RequestFailedException Handling
#### ✅ CORRECT: Pattern matching on status codes
```csharp
using Azure;

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

#### ❌ INCORRECT: Generic exception handling
```csharp
try
{
    await apis.CreateOrUpdateAsync(WaitUntil.Completed, "my-api", apiData);
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);  // Loses Azure-specific context
}
```

---

## 9. Enum Values

### 9.1 ApiKind Values
#### ✅ CORRECT: Valid API kinds
```csharp
ApiKind.Rest      // REST API
ApiKind.Graphql   // GraphQL API
ApiKind.Grpc      // gRPC API
ApiKind.Soap      // SOAP API
ApiKind.Webhook   // Webhook
ApiKind.Websocket // WebSocket
```

### 9.2 ApiLifecycleStage Values
#### ✅ CORRECT: Valid lifecycle stages
```csharp
ApiLifecycleStage.Design      // In design phase
ApiLifecycleStage.Development // In development
ApiLifecycleStage.Testing     // Being tested
ApiLifecycleStage.Preview     // Preview release
ApiLifecycleStage.Production  // Production ready
ApiLifecycleStage.Deprecated  // Deprecated
ApiLifecycleStage.Retired     // Retired
```

### 9.3 ApiCenterEnvironmentKind Values
#### ✅ CORRECT: Valid environment kinds
```csharp
ApiCenterEnvironmentKind.Development  // Dev environment
ApiCenterEnvironmentKind.Testing      // Test environment
ApiCenterEnvironmentKind.Staging      // Staging environment
ApiCenterEnvironmentKind.Production   // Production environment
```

---

## 10. Best Practices Checklist

- [ ] Use `DefaultAzureCredential` for authentication
- [ ] Use `async/await` for all operations
- [ ] Use `WaitUntil.Completed` for synchronous completion
- [ ] Navigate hierarchy correctly: Service → Workspace → API → Version → Definition
- [ ] Use `ResourceIdentifier` for resource references
- [ ] Handle `RequestFailedException` with status code matching
- [ ] Use `await foreach` for listing resources
- [ ] Set `Kind` property on APIs and environments
- [ ] Use valid JSON Schema for metadata schemas
- [ ] Apply custom metadata via `BinaryData.FromObjectAsJson`
