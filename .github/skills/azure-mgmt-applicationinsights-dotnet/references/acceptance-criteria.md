# Azure Application Insights SDK Acceptance Criteria

**SDK**: `Azure.ResourceManager.ApplicationInsights`  
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/applicationinsights/Azure.ResourceManager.ApplicationInsights  
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Full namespace imports
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ApplicationInsights;
using Azure.ResourceManager.ApplicationInsights.Models;
```

#### ❌ INCORRECT: Missing required namespaces
```csharp
using Azure.ResourceManager.ApplicationInsights;
// Missing Azure.Identity, Azure.ResourceManager
```

### 1.2 Model Imports
#### ✅ CORRECT: Models namespace for data types
```csharp
using Azure.ResourceManager.ApplicationInsights.Models;

ApplicationInsightsApplicationType appType = ApplicationInsightsApplicationType.Web;
IngestionMode mode = IngestionMode.LogAnalytics;
```

#### ❌ INCORRECT: Using old telemetry SDK namespaces for resource management
```csharp
using Microsoft.ApplicationInsights;  // Wrong - this is telemetry SDK
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

### 3.1 Create Workspace-Based Application Insights Component
#### ✅ CORRECT: Full configuration with Log Analytics workspace
```csharp
ApplicationInsightsComponentCollection components = resourceGroup.GetApplicationInsightsComponents();

ApplicationInsightsComponentData data = new ApplicationInsightsComponentData(
    AzureLocation.EastUS,
    ApplicationInsightsApplicationType.Web)
{
    Kind = "web",
    WorkspaceResourceId = new ResourceIdentifier(
        "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace-name>"),
    IngestionMode = IngestionMode.LogAnalytics,
    PublicNetworkAccessForIngestion = PublicNetworkAccessType.Enabled,
    PublicNetworkAccessForQuery = PublicNetworkAccessType.Enabled,
    RetentionInDays = 90,
    SamplingPercentage = 100,
    DisableIPMasking = false,
    Tags =
    {
        { "environment", "production" }
    }
};

ArmOperation<ApplicationInsightsComponentResource> operation = await components
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-appinsights", data);

ApplicationInsightsComponentResource component = operation.Value;
```

#### ❌ INCORRECT: Missing required location and application type
```csharp
ApplicationInsightsComponentData data = new ApplicationInsightsComponentData();
// Missing location and application type - constructor requires them
```

### 3.2 Create Classic Application Insights (Deprecated)
#### ✅ CORRECT: Use workspace-based instead
```csharp
// Workspace-based is recommended for all new deployments
ApplicationInsightsComponentData data = new ApplicationInsightsComponentData(
    AzureLocation.EastUS,
    ApplicationInsightsApplicationType.Web)
{
    Kind = "web",
    WorkspaceResourceId = workspaceResourceId,
    IngestionMode = IngestionMode.LogAnalytics
};
```

#### ❌ INCORRECT: Classic mode without workspace
```csharp
ApplicationInsightsComponentData data = new ApplicationInsightsComponentData(
    AzureLocation.EastUS,
    ApplicationInsightsApplicationType.Web)
{
    // Missing WorkspaceResourceId - creates deprecated classic resource
    IngestionMode = IngestionMode.ApplicationInsights
};
```

### 3.3 Get Connection String and Keys
#### ✅ CORRECT: Access from component data
```csharp
ApplicationInsightsComponentResource component = await resourceGroup
    .GetApplicationInsightsComponentAsync("my-appinsights");

string connectionString = component.Data.ConnectionString;
string instrumentationKey = component.Data.InstrumentationKey;
string appId = component.Data.AppId;

Console.WriteLine($"Connection String: {connectionString}");
Console.WriteLine($"Instrumentation Key: {instrumentationKey}");
Console.WriteLine($"App ID: {appId}");
```

#### ❌ INCORRECT: Trying to get keys separately
```csharp
var keys = await component.GetKeysAsync();  // Wrong method
```

---

## 4. API Keys

### 4.1 Create API Key for Reading Telemetry
#### ✅ CORRECT: Using LinkedReadProperties
```csharp
ApplicationInsightsComponentResource component = await resourceGroup
    .GetApplicationInsightsComponentAsync("my-appinsights");

ApplicationInsightsComponentApiKeyCollection apiKeys = component.GetApplicationInsightsComponentApiKeys();

ApplicationInsightsApiKeyContent keyContent = new ApplicationInsightsApiKeyContent
{
    Name = "ReadTelemetryKey",
    LinkedReadProperties =
    {
        $"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/microsoft.insights/components/{component.Data.Name}/api",
        $"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/microsoft.insights/components/{component.Data.Name}/agentconfig"
    }
};

ApplicationInsightsComponentApiKeyResource apiKey = await apiKeys
    .CreateOrUpdateAsync(WaitUntil.Completed, keyContent);

Console.WriteLine($"API Key Name: {apiKey.Data.Name}");
Console.WriteLine($"API Key: {apiKey.Data.ApiKey}"); // Only shown once!
```

#### ❌ INCORRECT: Missing linked properties
```csharp
ApplicationInsightsApiKeyContent keyContent = new ApplicationInsightsApiKeyContent
{
    Name = "ReadTelemetryKey"
    // Missing LinkedReadProperties - key won't have permissions
};
```

---

## 5. Web Tests (Availability Tests)

### 5.1 Create URL Ping Test
#### ✅ CORRECT: Full ping test configuration
```csharp
WebTestCollection webTests = resourceGroup.GetWebTests();

WebTestData urlPingTest = new WebTestData(AzureLocation.EastUS)
{
    Kind = WebTestKind.Ping,
    SyntheticMonitorId = "webtest-ping-myapp",
    WebTestName = "Homepage Availability",
    Description = "Checks if homepage is available",
    IsEnabled = true,
    Frequency = 300, // 5 minutes
    Timeout = 120,   // 2 minutes
    WebTestKind = WebTestKind.Ping,
    IsRetryEnabled = true,
    Locations =
    {
        new WebTestGeolocation { WebTestLocationId = "us-ca-sjc-azr" },
        new WebTestGeolocation { WebTestLocationId = "us-tx-sn1-azr" },
        new WebTestGeolocation { WebTestLocationId = "emea-gb-db3-azr" }
    },
    Configuration = new WebTestConfiguration
    {
        WebTest = """
            <WebTest Name="Homepage" Enabled="True" Timeout="120" 
                     xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010">
                <Items>
                    <Request Method="GET" Version="1.1" Url="https://myapp.example.com" 
                             ThinkTime="0" Timeout="120" ParseDependentRequests="False" 
                             FollowRedirects="True" RecordResult="True" Cache="False" 
                             ExpectedHttpStatusCode="200" />
                </Items>
            </WebTest>
        """
    },
    Tags =
    {
        { $"hidden-link:/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/microsoft.insights/components/my-appinsights", "Resource" }
    }
};

ArmOperation<WebTestResource> operation = await webTests
    .CreateOrUpdateAsync(WaitUntil.Completed, "webtest-homepage", urlPingTest);
```

#### ❌ INCORRECT: Missing hidden-link tag
```csharp
WebTestData urlPingTest = new WebTestData(AzureLocation.EastUS)
{
    WebTestName = "Homepage Availability"
    // Missing hidden-link tag - won't associate with App Insights
};
```

### 5.2 Valid Web Test Locations
#### ✅ CORRECT: Using valid location IDs
```csharp
Locations =
{
    new WebTestGeolocation { WebTestLocationId = "us-ca-sjc-azr" },  // West US
    new WebTestGeolocation { WebTestLocationId = "us-tx-sn1-azr" },  // South Central US
    new WebTestGeolocation { WebTestLocationId = "us-il-ch1-azr" },  // North Central US
    new WebTestGeolocation { WebTestLocationId = "emea-gb-db3-azr" }, // UK South
    new WebTestGeolocation { WebTestLocationId = "apac-sg-sin-azr" }  // Southeast Asia
}
```

#### ❌ INCORRECT: Invalid location IDs
```csharp
Locations =
{
    new WebTestGeolocation { WebTestLocationId = "eastus" },  // Wrong format
    new WebTestGeolocation { WebTestLocationId = "westus" }
}
```

---

## 6. Workbooks

### 6.1 Create Shared Workbook
#### ✅ CORRECT: Workbook with serialized data
```csharp
WorkbookCollection workbooks = resourceGroup.GetWorkbooks();

WorkbookData workbookData = new WorkbookData(AzureLocation.EastUS)
{
    DisplayName = "Application Performance Dashboard",
    Category = "workbook",
    Kind = WorkbookSharedTypeKind.Shared,
    SerializedData = """
    {
        "version": "Notebook/1.0",
        "items": [
            {
                "type": 1,
                "content": {
                    "json": "# Application Performance"
                },
                "name": "header"
            },
            {
                "type": 3,
                "content": {
                    "version": "KqlItem/1.0",
                    "query": "requests | summarize count() by bin(timestamp, 1h) | render timechart",
                    "size": 0,
                    "title": "Requests per Hour"
                },
                "name": "requestsChart"
            }
        ],
        "isLocked": false
    }
    """,
    SourceId = component.Id
};

string workbookId = Guid.NewGuid().ToString();

ArmOperation<WorkbookResource> operation = await workbooks
    .CreateOrUpdateAsync(WaitUntil.Completed, workbookId, workbookData);
```

#### ❌ INCORRECT: Missing GUID for workbook ID
```csharp
await workbooks.CreateOrUpdateAsync(
    WaitUntil.Completed, 
    "my-workbook",  // Wrong - should be a GUID
    workbookData);
```

---

## 7. Linked Storage Account

### 7.1 Link Storage Account for Profiler
#### ✅ CORRECT: Using ComponentLinkedStorageAccount
```csharp
ApplicationInsightsComponentResource component = await resourceGroup
    .GetApplicationInsightsComponentAsync("my-appinsights");

ComponentLinkedStorageAccountCollection linkedStorage = component.GetComponentLinkedStorageAccounts();

ComponentLinkedStorageAccountData storageData = new ComponentLinkedStorageAccountData
{
    LinkedStorageAccount = new ResourceIdentifier(
        "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<storage-account>")
};

ArmOperation<ComponentLinkedStorageAccountResource> operation = await linkedStorage
    .CreateOrUpdateAsync(WaitUntil.Completed, StorageType.ServiceProfiler, storageData);
```

#### ❌ INCORRECT: Using string instead of ResourceIdentifier
```csharp
ComponentLinkedStorageAccountData storageData = new ComponentLinkedStorageAccountData
{
    LinkedStorageAccount = "/subscriptions/.../storageAccounts/myaccount"  // Wrong type
};
```

---

## 8. Listing Resources

### 8.1 List Components
#### ✅ CORRECT: Using async enumeration
```csharp
await foreach (ApplicationInsightsComponentResource component in 
    resourceGroup.GetApplicationInsightsComponents())
{
    Console.WriteLine($"Component: {component.Data.Name}");
    Console.WriteLine($"  App ID: {component.Data.AppId}");
    Console.WriteLine($"  Type: {component.Data.ApplicationType}");
    Console.WriteLine($"  Ingestion Mode: {component.Data.IngestionMode}");
    Console.WriteLine($"  Retention: {component.Data.RetentionInDays} days");
}
```

#### ❌ INCORRECT: Converting to list synchronously
```csharp
var components = resourceGroup.GetApplicationInsightsComponents().ToList();  // Wrong - blocks async
```

### 8.2 List Web Tests
#### ✅ CORRECT: Using async enumeration
```csharp
await foreach (WebTestResource webTest in resourceGroup.GetWebTests())
{
    Console.WriteLine($"Web Test: {webTest.Data.WebTestName}");
    Console.WriteLine($"  Enabled: {webTest.Data.IsEnabled}");
    Console.WriteLine($"  Frequency: {webTest.Data.Frequency}s");
}
```

---

## 9. Error Handling

### 9.1 RequestFailedException Handling
#### ✅ CORRECT: Pattern matching on status codes
```csharp
using Azure;

try
{
    ArmOperation<ApplicationInsightsComponentResource> operation = await components
        .CreateOrUpdateAsync(WaitUntil.Completed, "my-appinsights", data);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Component already exists");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid configuration: {ex.Message}");
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
    await components.CreateOrUpdateAsync(WaitUntil.Completed, "my-appinsights", data);
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);  // Loses Azure-specific context
}
```

---

## 10. Application Types

### 10.1 Valid Application Types
#### ✅ CORRECT: Using ApplicationInsightsApplicationType enum
```csharp
ApplicationInsightsApplicationType.Web     // Web application
ApplicationInsightsApplicationType.iOS     // iOS application
ApplicationInsightsApplicationType.Java    // Java application
ApplicationInsightsApplicationType.NodeJS  // Node.js application
ApplicationInsightsApplicationType.MRT     // .NET application
ApplicationInsightsApplicationType.Other   // Other type
```

### 10.2 Ingestion Modes
#### ✅ CORRECT: Using IngestionMode enum
```csharp
IngestionMode.LogAnalytics        // Workspace-based (recommended)
IngestionMode.ApplicationInsights // Classic (deprecated)
```

---

## 11. SDK Integration

### 11.1 Using Connection String with Telemetry SDK
#### ✅ CORRECT: ASP.NET Core configuration
```csharp
// Program.cs
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.ConnectionString = configuration["ApplicationInsights:ConnectionString"];
});
```

#### ✅ CORRECT: Environment variable
```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...
```

#### ❌ INCORRECT: Using instrumentation key directly (deprecated)
```csharp
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.InstrumentationKey = "your-key";  // Deprecated - use ConnectionString
});
```

---

## 12. Best Practices Checklist

- [ ] Use `DefaultAzureCredential` for authentication
- [ ] Use `async/await` for all operations
- [ ] Use `WaitUntil.Completed` for synchronous completion
- [ ] Create workspace-based components (not classic)
- [ ] Set `IngestionMode.LogAnalytics` for workspace-based
- [ ] Include `hidden-link` tag for web tests
- [ ] Use GUID for workbook IDs
- [ ] Use valid web test location IDs
- [ ] Store connection strings securely (Key Vault)
- [ ] Handle `RequestFailedException` with status code matching
- [ ] Use `await foreach` for listing resources