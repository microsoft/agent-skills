# Azure.ResourceManager.Playwright Acceptance Criteria

**SDK**: `Azure.ResourceManager.Playwright`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/playwright
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Standard ARM Playwright imports
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.Playwright;
using Azure.ResourceManager.Playwright.Models;
```

#### ❌ INCORRECT: Missing core imports
```csharp
using Azure.ResourceManager.Playwright;
// Missing Azure.Identity and Azure.ResourceManager
```

#### ❌ INCORRECT: Confusing with test execution SDK
```csharp
using Azure.Developer.MicrosoftPlaywrightTesting.NUnit;  // Wrong - this is for test execution
using Microsoft.Playwright;  // Wrong - this is the base Playwright library
```

---

## 2. Client Creation

### 2.1 ARM Client Initialization
#### ✅ CORRECT: Using DefaultAzureCredential
```csharp
var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);
var subscriptionId = Environment.GetEnvironmentVariable("AZURE_SUBSCRIPTION_ID");
var subscription = armClient.GetSubscriptionResource(
    new ResourceIdentifier($"/subscriptions/{subscriptionId}"));
```

#### ❌ INCORRECT: Hardcoded credentials
```csharp
var credential = new ClientSecretCredential(tenantId, clientId, "secret");
```

#### ❌ INCORRECT: Missing credential
```csharp
var armClient = new ArmClient();  // No credential
```

---

## 3. Core Operations

### 3.1 Create Playwright Workspace
#### ✅ CORRECT: Full workspace creation
```csharp
var resourceGroup = await subscription.GetResourceGroupAsync("my-resource-group");

var workspaceData = new PlaywrightWorkspaceData(AzureLocation.WestUS3)
{
    RegionalAffinity = PlaywrightRegionalAffinity.Enabled,
    LocalAuth = PlaywrightLocalAuth.Enabled,
    Tags =
    {
        ["Team"] = "Dev Exp",
        ["Environment"] = "Production"
    }
};

var workspaceCollection = resourceGroup.Value.GetPlaywrightWorkspaces();
var operation = await workspaceCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-playwright-workspace", workspaceData);

Console.WriteLine($"Data Plane URI: {operation.Value.Data.DataplaneUri}");
```

#### ❌ INCORRECT: Missing location
```csharp
var workspaceData = new PlaywrightWorkspaceData();  // Location required
```

### 3.2 Get Workspace
#### ✅ CORRECT: Get existing workspace
```csharp
var workspace = await workspaceCollection.GetAsync("my-playwright-workspace");
Console.WriteLine($"Name: {workspace.Value.Data.Name}");
Console.WriteLine($"State: {workspace.Value.Data.ProvisioningState}");
Console.WriteLine($"Data Plane URI: {workspace.Value.Data.DataplaneUri}");
```

#### ✅ CORRECT: Check existence before get
```csharp
bool exists = await workspaceCollection.ExistsAsync("my-playwright-workspace");
if (exists)
{
    var workspace = await workspaceCollection.GetAsync("my-playwright-workspace");
}
```

#### ❌ INCORRECT: Synchronous access
```csharp
var workspace = workspaceCollection.Get("my-playwright-workspace");  // Use async
```

### 3.3 List Workspaces
#### ✅ CORRECT: Async enumeration in resource group
```csharp
await foreach (var workspace in workspaceCollection.GetAllAsync())
{
    Console.WriteLine($"Workspace: {workspace.Data.Name}");
    Console.WriteLine($"  Location: {workspace.Data.Location}");
    Console.WriteLine($"  State: {workspace.Data.ProvisioningState}");
    Console.WriteLine($"  Data Plane URI: {workspace.Data.DataplaneUri}");
}
```

#### ✅ CORRECT: Async enumeration across subscription
```csharp
await foreach (var workspace in subscription.GetPlaywrightWorkspacesAsync())
{
    Console.WriteLine($"Workspace: {workspace.Data.Name}");
}
```

#### ❌ INCORRECT: Blocking enumeration
```csharp
var workspaces = workspaceCollection.GetAllAsync().ToListAsync().Result;  // Don't block
```

### 3.4 Update Workspace
#### ✅ CORRECT: Using patch object
```csharp
var patch = new PlaywrightWorkspacePatch
{
    Tags =
    {
        ["Team"] = "Dev Exp",
        ["Environment"] = "Staging",
        ["UpdatedAt"] = DateTime.UtcNow.ToString("o")
    }
};

var updatedWorkspace = await workspace.Value.UpdateAsync(patch);
```

#### ❌ INCORRECT: Modifying Data.Tags directly
```csharp
workspace.Data.Tags["NewTag"] = "Value";  // Won't persist
```

### 3.5 Check Name Availability
#### ✅ CORRECT: Proper name availability check
```csharp
var checkRequest = new PlaywrightCheckNameAvailabilityContent
{
    Name = "my-new-workspace",
    ResourceType = "Microsoft.LoadTestService/playwrightWorkspaces"
};

var result = await subscription.CheckPlaywrightNameAvailabilityAsync(checkRequest);

if (result.Value.IsNameAvailable == true)
{
    Console.WriteLine("Name is available!");
}
else
{
    Console.WriteLine($"Name unavailable: {result.Value.Message}");
}
```

#### ❌ INCORRECT: Wrong resource type
```csharp
var checkRequest = new PlaywrightCheckNameAvailabilityContent
{
    Name = "my-new-workspace",
    ResourceType = "Microsoft.Playwright/workspaces"  // Wrong provider
};
```

### 3.6 Get Quota Information
#### ✅ CORRECT: Subscription-level quotas
```csharp
await foreach (var quota in subscription.GetPlaywrightQuotasAsync(AzureLocation.WestUS3))
{
    Console.WriteLine($"Quota: {quota.Data.Name}");
    Console.WriteLine($"  Limit: {quota.Data.Limit}");
    Console.WriteLine($"  Used: {quota.Data.Used}");
}
```

#### ✅ CORRECT: Workspace-level quotas
```csharp
var workspaceQuotas = workspace.Value.GetAllPlaywrightWorkspaceQuota();
await foreach (var quota in workspaceQuotas.GetAllAsync())
{
    Console.WriteLine($"Workspace Quota: {quota.Data.Name}");
}
```

### 3.7 Delete Workspace
#### ✅ CORRECT: Delete with wait
```csharp
await workspace.Value.DeleteAsync(WaitUntil.Completed);
```

#### ❌ INCORRECT: Not waiting for deletion
```csharp
await workspace.Value.DeleteAsync(WaitUntil.Started);
// Immediately trying to use workspace - may fail
```

---

## 4. Error Handling

### 4.1 RequestFailedException Handling
#### ✅ CORRECT: Specific exception handling
```csharp
try
{
    var operation = await workspaceCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, workspaceName, workspaceData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Workspace already exists");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Bad request: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

#### ❌ INCORRECT: Catching generic Exception
```csharp
try
{
    var operation = await workspaceCollection.CreateOrUpdateAsync(...);
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);  // Too broad
}
```

---

## 5. Long-Running Operations

### 5.1 Wait Options
#### ✅ CORRECT: Wait for completion
```csharp
var operation = await workspaceCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, workspaceName, workspaceData);
var workspace = operation.Value;  // Safe to access
```

#### ✅ CORRECT: Start and poll manually
```csharp
var operation = await workspaceCollection.CreateOrUpdateAsync(
    WaitUntil.Started, workspaceName, workspaceData);

while (!operation.HasCompleted)
{
    await Task.Delay(TimeSpan.FromSeconds(5));
    await operation.UpdateStatusAsync();
}
```

#### ❌ INCORRECT: Accessing Value before completion
```csharp
var operation = await workspaceCollection.CreateOrUpdateAsync(
    WaitUntil.Started, workspaceName, workspaceData);
var workspace = operation.Value;  // May throw
```

---

## 6. Resource Hierarchy Navigation

### 6.1 Proper Hierarchy
#### ✅ CORRECT: Navigate through ARM hierarchy
```csharp
var subscription = armClient.GetSubscriptionResource(
    new ResourceIdentifier($"/subscriptions/{subscriptionId}"));
var resourceGroup = await subscription.GetResourceGroupAsync("my-rg");
var workspaceCollection = resourceGroup.Value.GetPlaywrightWorkspaces();
```

#### ❌ INCORRECT: Direct access attempt
```csharp
var workspaces = armClient.GetPlaywrightWorkspaces();  // Not valid
```

---

## 7. Workspace Properties

### 7.1 Regional Affinity
#### ✅ CORRECT: Enable regional affinity
```csharp
var workspaceData = new PlaywrightWorkspaceData(AzureLocation.WestUS3)
{
    RegionalAffinity = PlaywrightRegionalAffinity.Enabled
};
```

### 7.2 Local Authentication
#### ✅ CORRECT: Enable local auth
```csharp
var workspaceData = new PlaywrightWorkspaceData(AzureLocation.WestUS3)
{
    LocalAuth = PlaywrightLocalAuth.Enabled
};
```

---

## 8. Integration with Test Execution

### 8.1 Using DataplaneUri
#### ✅ CORRECT: Configure tests with DataplaneUri
```csharp
// Create workspace (this SDK)
var workspace = await workspaceCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-workspace", workspaceData);

// Get service URL for test execution
var serviceUrl = workspace.Value.Data.DataplaneUri;

// Set environment variable for test execution SDK
Environment.SetEnvironmentVariable("PLAYWRIGHT_SERVICE_URL", serviceUrl.ToString());
```

---

## 9. API Information

### 9.1 Resource Type
#### ✅ CORRECT: Use proper resource type
```csharp
// Resource Provider: Microsoft.LoadTestService
// Resource Type: Microsoft.LoadTestService/playwrightWorkspaces
```

#### ❌ INCORRECT: Wrong resource type
```csharp
// Microsoft.Playwright/workspaces  // Wrong
// Microsoft.PlaywrightTesting/workspaces  // Wrong
```

---

## Summary Checklist

- [ ] Uses `DefaultAzureCredential` for authentication
- [ ] Imports `Azure.ResourceManager.Playwright` and models namespace
- [ ] Creates `ArmClient` with credential
- [ ] Navigates hierarchy: Subscription → ResourceGroup → PlaywrightWorkspaces
- [ ] Uses `async/await` for all operations
- [ ] Uses correct resource type: `Microsoft.LoadTestService/playwrightWorkspaces`
- [ ] Handles `RequestFailedException` with status codes
- [ ] Uses `WaitUntil.Completed` for blocking operations
- [ ] Stores `DataplaneUri` for test execution configuration
- [ ] Uses `PlaywrightWorkspacePatch` for updates
- [ ] Distinguishes between management SDK (this) and test execution SDK
