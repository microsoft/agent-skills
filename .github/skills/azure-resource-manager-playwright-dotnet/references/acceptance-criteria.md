# Azure.ResourceManager.Playwright SDK Acceptance Criteria (.NET)

**SDK**: `Azure.ResourceManager.Playwright`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/playwright/Azure.ResourceManager.Playwright
**Package**: https://www.nuget.org/packages/Azure.ResourceManager.Playwright
**Purpose**: Skill testing acceptance criteria for validating generated C# code correctness

---

## 1. Correct Using Statements

### 1.1 Core Imports

#### ✅ CORRECT: Basic Client Imports
```csharp
using Azure;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.Playwright;
using Azure.ResourceManager.Playwright.Models;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using Azure.Playwright;
using Microsoft.Playwright.Testing;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Create ArmClient
```csharp
var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);
```

---

## 3. Workspace Operations

### 3.1 ✅ CORRECT: Create Playwright Workspace
```csharp
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
    WaitUntil.Completed,
    "my-playwright-workspace",
    workspaceData);

PlaywrightWorkspaceResource workspace = operation.Value;
Console.WriteLine($"Data Plane URI: {workspace.Data.DataplaneUri}");
```

### 3.2 ✅ CORRECT: Check Name Availability
```csharp
var checkRequest = new PlaywrightCheckNameAvailabilityContent
{
    Name = "my-new-workspace",
    ResourceType = "Microsoft.LoadTestService/playwrightWorkspaces"
};

var result = await subscription.CheckPlaywrightNameAvailabilityAsync(checkRequest);
```

### 3.3 ✅ CORRECT: Get Quota Information
```csharp
await foreach (var quota in subscription.GetPlaywrightQuotasAsync(AzureLocation.WestUS3))
{
    Console.WriteLine($"Quota: {quota.Data.Name}");
    Console.WriteLine($"  Limit: {quota.Data.Limit}");
    Console.WriteLine($"  Used: {quota.Data.Used}");
}
```

---

## 4. Error Handling Patterns

### 4.1 ✅ CORRECT: Handle RequestFailedException
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
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

---

## 5. Key Types Reference

| Type | Purpose |
|------|---------|
| `ArmClient` | Entry point for ARM operations |
| `PlaywrightWorkspaceResource` | Playwright Testing workspace |
| `PlaywrightWorkspaceCollection` | Collection for CRUD |
| `PlaywrightWorkspaceData` | Workspace configuration |
| `PlaywrightWorkspacePatch` | Update payload |
| `PlaywrightQuotaResource` | Subscription-level quotas |
| `PlaywrightWorkspaceQuotaResource` | Workspace quotas |
| `PlaywrightCheckNameAvailabilityContent` | Name check request |

## 6. Workspace Properties

| Property | Description |
|----------|-------------|
| `DataplaneUri` | URI for running tests |
| `WorkspaceId` | Unique workspace identifier |
| `RegionalAffinity` | Enable/disable regional affinity |
| `LocalAuth` | Enable/disable local authentication |
| `ProvisioningState` | Current provisioning state |

---

## 7. Best Practices Summary

1. **Use WaitUntil.Completed** — For synchronous completion
2. **Use DefaultAzureCredential** — Never hardcode credentials
3. **Handle RequestFailedException** — For ARM API errors
4. **Store the DataplaneUri** — After workspace creation for test execution
5. **Check name availability** — Before creating workspaces
