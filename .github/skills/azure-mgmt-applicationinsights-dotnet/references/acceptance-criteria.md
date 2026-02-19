# Azure.ResourceManager.ApplicationInsights SDK Acceptance Criteria (.NET)

**SDK**: `Azure.ResourceManager.ApplicationInsights`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/applicationinsights/Azure.ResourceManager.ApplicationInsights
**Package**: https://www.nuget.org/packages/Azure.ResourceManager.ApplicationInsights
**Purpose**: Skill testing acceptance criteria for validating generated C# code correctness

---

## 1. Correct Using Statements

### 1.1 Core Imports

#### ✅ CORRECT: Basic Client Imports
```csharp
using Azure;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ApplicationInsights;
using Azure.ResourceManager.ApplicationInsights.Models;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using Azure.ApplicationInsights;
using Microsoft.ApplicationInsights.Management;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Create ArmClient
```csharp
ArmClient client = new ArmClient(new DefaultAzureCredential());
```

### 2.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing credential
```csharp
// WRONG - Must provide credential
ArmClient client = new ArmClient();
```

---

## 3. Application Insights Component Operations

### 3.1 ✅ CORRECT: Create Workspace-based Component (Recommended)
```csharp
ApplicationInsightsComponentCollection components = resourceGroup.GetApplicationInsightsComponents();

ApplicationInsightsComponentData data = new ApplicationInsightsComponentData(
    AzureLocation.EastUS,
    ApplicationInsightsApplicationType.Web)
{
    Kind = "web",
    WorkspaceResourceId = new ResourceIdentifier(
        "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace>"),
    IngestionMode = IngestionMode.LogAnalytics,
    RetentionInDays = 90
};

ArmOperation<ApplicationInsightsComponentResource> operation = await components
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-appinsights", data);

ApplicationInsightsComponentResource component = operation.Value;
```

### 3.2 ✅ CORRECT: Get Connection String
```csharp
ApplicationInsightsComponentResource component = await resourceGroup
    .GetApplicationInsightsComponentAsync("my-appinsights");

string connectionString = component.Data.ConnectionString;
string instrumentationKey = component.Data.InstrumentationKey;
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing ApplicationType
```csharp
// WRONG - ApplicationType is required
ApplicationInsightsComponentData data = new ApplicationInsightsComponentData(AzureLocation.EastUS);
```

---

## 4. Web Test Operations

### 4.1 ✅ CORRECT: Create URL Ping Test
```csharp
WebTestCollection webTests = resourceGroup.GetWebTests();

WebTestData urlPingTest = new WebTestData(AzureLocation.EastUS)
{
    Kind = WebTestKind.Ping,
    SyntheticMonitorId = "webtest-ping-myapp",
    WebTestName = "Homepage Availability",
    IsEnabled = true,
    Frequency = 300,
    Timeout = 120,
    WebTestKind = WebTestKind.Ping,
    IsRetryEnabled = true,
    Locations =
    {
        new WebTestGeolocation { WebTestLocationId = "us-ca-sjc-azr" },
        new WebTestGeolocation { WebTestLocationId = "emea-gb-db3-azr" }
    },
    Configuration = new WebTestConfiguration
    {
        WebTest = @"<WebTest Name=""Homepage"" ...>...</WebTest>"
    }
};

ArmOperation<WebTestResource> operation = await webTests
    .CreateOrUpdateAsync(WaitUntil.Completed, "webtest-homepage", urlPingTest);
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing locations
```csharp
// WRONG - Must specify at least one test location
WebTestData test = new WebTestData(AzureLocation.EastUS)
{
    WebTestName = "Test"
    // Missing Locations
};
```

---

## 5. API Key Operations

### 5.1 ✅ CORRECT: Create API Key
```csharp
ApplicationInsightsComponentApiKeyCollection apiKeys = component.GetApplicationInsightsComponentApiKeys();

ApplicationInsightsApiKeyContent keyContent = new ApplicationInsightsApiKeyContent
{
    Name = "ReadTelemetryKey",
    LinkedReadProperties =
    {
        $"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/microsoft.insights/components/{componentName}/api"
    }
};

ApplicationInsightsComponentApiKeyResource apiKey = await apiKeys
    .CreateOrUpdateAsync(WaitUntil.Completed, keyContent);
```

---

## 6. Workbook Operations

### 6.1 ✅ CORRECT: Create Workbook
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
        "items": [...]
    }
    """,
    SourceId = component.Id
};

string workbookId = Guid.NewGuid().ToString();
ArmOperation<WorkbookResource> operation = await workbooks
    .CreateOrUpdateAsync(WaitUntil.Completed, workbookId, workbookData);
```

---

## 7. Error Handling Patterns

### 7.1 ✅ CORRECT: Handle RequestFailedException
```csharp
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

---

## 8. Key Types Reference

| Type | Purpose |
|------|---------|
| `ArmClient` | Entry point for ARM operations |
| `ApplicationInsightsComponentResource` | App Insights component |
| `ApplicationInsightsComponentData` | Component configuration |
| `ApplicationInsightsComponentApiKeyResource` | API key |
| `WebTestResource` | Availability/web test |
| `WebTestData` | Web test configuration |
| `WorkbookResource` | Analysis workbook |
| `WorkbookData` | Workbook configuration |

## 9. Application Types

| Type | Enum Value |
|------|------------|
| Web Application | `Web` |
| iOS Application | `iOS` |
| Java Application | `Java` |
| Other | `Other` |

## 10. Web Test Locations

| Location ID | Region |
|-------------|--------|
| `us-ca-sjc-azr` | West US |
| `us-tx-sn1-azr` | South Central US |
| `emea-gb-db3-azr` | UK South |
| `apac-sg-sin-azr` | Southeast Asia |

---

## 11. Best Practices Summary

1. **Use workspace-based** — Workspace-based App Insights is recommended
2. **Link to Log Analytics** — Store data in Log Analytics for better querying
3. **Set appropriate retention** — Balance cost vs. data availability
4. **Use multiple test locations** — For accurate availability monitoring
5. **Store connection string securely** — Use Key Vault or managed identity
6. **Tag resources** — For cost allocation and organization
