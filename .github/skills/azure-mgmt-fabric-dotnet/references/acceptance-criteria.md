# Azure.ResourceManager.Fabric Acceptance Criteria

**SDK**: `Azure.ResourceManager.Fabric`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/fabric/Azure.ResourceManager.Fabric
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Standard ARM Fabric imports
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.Fabric;
using Azure.ResourceManager.Fabric.Models;
using Azure.Core;
```

#### ❌ INCORRECT: Missing core imports
```csharp
using Azure.ResourceManager.Fabric;
// Missing Azure.Identity, Azure.ResourceManager, Azure.Core
```

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
using Azure.Fabric;
using Microsoft.Fabric.ResourceManager;
```

---

## 2. Client Creation

### 2.1 ARM Client Initialization
#### ✅ CORRECT: Using DefaultAzureCredential
```csharp
var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);
var subscription = await armClient.GetDefaultSubscriptionAsync();
```

#### ❌ INCORRECT: Hardcoded credentials
```csharp
var credential = new ClientSecretCredential(tenantId, clientId, "hardcoded-secret");
var armClient = new ArmClient(credential);
```

#### ❌ INCORRECT: Missing credential
```csharp
var armClient = new ArmClient();  // No credential parameter
```

---

## 3. Core Operations

### 3.1 Create Fabric Capacity
#### ✅ CORRECT: Full capacity creation with all required properties
```csharp
var resourceGroup = await subscription.GetResourceGroupAsync("my-resource-group");
var administration = new FabricCapacityAdministration(new[] { "admin@contoso.com" });
var properties = new FabricCapacityProperties(administration);
var sku = new FabricSku("F64", FabricSkuTier.Fabric);
var capacityData = new FabricCapacityData(AzureLocation.WestUS2, properties, sku);

var capacityCollection = resourceGroup.Value.GetFabricCapacities();
var operation = await capacityCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-capacity", capacityData);
```

#### ❌ INCORRECT: Missing required properties
```csharp
var capacityData = new FabricCapacityData(AzureLocation.WestUS2);
// Missing properties and sku - will fail
```

#### ❌ INCORRECT: Invalid SKU tier
```csharp
var sku = new FabricSku("F64", "StandardTier");  // Invalid tier
```

### 3.2 Get Capacity
#### ✅ CORRECT: Proper async retrieval
```csharp
var capacity = await resourceGroup.Value.GetFabricCapacityAsync("my-capacity");
Console.WriteLine($"State: {capacity.Value.Data.Properties.State}");
```

#### ❌ INCORRECT: Synchronous call
```csharp
var capacity = resourceGroup.Value.GetFabricCapacity("my-capacity");  // Use async
```

### 3.3 Update Capacity (Scale/Change Admins)
#### ✅ CORRECT: Using FabricCapacityPatch
```csharp
var patch = new FabricCapacityPatch
{
    Sku = new FabricSku("F128", FabricSkuTier.Fabric),
    Properties = new FabricCapacityUpdateProperties
    {
        Administration = new FabricCapacityAdministration(
            new[] { "admin@contoso.com", "newadmin@contoso.com" })
    }
};
var operation = await capacity.Value.UpdateAsync(WaitUntil.Completed, patch);
```

#### ❌ INCORRECT: Trying to update with full data object
```csharp
var operation = await capacityCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-capacity", fullCapacityData);  // Use patch for updates
```

### 3.4 Suspend and Resume
#### ✅ CORRECT: Proper suspend/resume operations
```csharp
await capacity.Value.SuspendAsync(WaitUntil.Completed);
var resumeOperation = await capacity.Value.ResumeAsync(WaitUntil.Completed);
```

#### ❌ INCORRECT: Not waiting for completion
```csharp
await capacity.Value.SuspendAsync(WaitUntil.Started);
// Immediately using capacity without waiting
```

### 3.5 List Capacities
#### ✅ CORRECT: Using async enumeration
```csharp
await foreach (var cap in resourceGroup.Value.GetFabricCapacities())
{
    Console.WriteLine($"- {cap.Data.Name} ({cap.Data.Sku.Name})");
}
```

#### ❌ INCORRECT: Trying to materialize as List synchronously
```csharp
var capacities = resourceGroup.Value.GetFabricCapacities().ToList();  // Use async
```

### 3.6 Check Name Availability
#### ✅ CORRECT: Proper name availability check
```csharp
var checkContent = new FabricNameAvailabilityContent
{
    Name = "my-new-capacity",
    ResourceType = "Microsoft.Fabric/capacities"
};
var result = await subscription.CheckFabricCapacityNameAvailabilityAsync(
    AzureLocation.WestUS2, checkContent);
```

#### ❌ INCORRECT: Wrong resource type
```csharp
var checkContent = new FabricNameAvailabilityContent
{
    Name = "my-new-capacity",
    ResourceType = "Fabric/capacities"  // Missing Microsoft. prefix
};
```

### 3.7 List Available SKUs
#### ✅ CORRECT: List SKUs in subscription
```csharp
await foreach (var skuDetails in subscription.GetSkusFabricCapacitiesAsync())
{
    Console.WriteLine($"SKU: {skuDetails.Name}");
}
```

---

## 4. Error Handling

### 4.1 RequestFailedException Handling
#### ✅ CORRECT: Proper exception handling with status codes
```csharp
try
{
    var operation = await capacityCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, capacityName, capacityData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Capacity already exists or conflict");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid configuration: {ex.Message}");
}
catch (RequestFailedException ex) when (ex.Status == 403)
{
    Console.WriteLine("Insufficient permissions or quota exceeded");
}
```

#### ❌ INCORRECT: Catching generic Exception
```csharp
try
{
    var operation = await capacityCollection.CreateOrUpdateAsync(...);
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);  // Too broad, loses specific error info
}
```

---

## 5. Long-Running Operations

### 5.1 WaitUntil Options
#### ✅ CORRECT: Using WaitUntil.Completed for blocking operations
```csharp
var operation = await capacityCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, capacityName, capacityData);
FabricCapacityResource capacity = operation.Value;  // Safe to access
```

#### ✅ CORRECT: Using WaitUntil.Started for manual polling
```csharp
var operation = await capacityCollection.CreateOrUpdateAsync(
    WaitUntil.Started, capacityName, capacityData);
while (!operation.HasCompleted)
{
    await Task.Delay(5000);
    await operation.UpdateStatusAsync();
}
```

#### ❌ INCORRECT: Not waiting before accessing Value
```csharp
var operation = await capacityCollection.CreateOrUpdateAsync(
    WaitUntil.Started, capacityName, capacityData);
var capacity = operation.Value;  // May throw if not completed
```

---

## 6. Resource Hierarchy Navigation

### 6.1 Proper Hierarchy
#### ✅ CORRECT: Navigate through resource hierarchy
```csharp
var subscription = await armClient.GetDefaultSubscriptionAsync();
var resourceGroup = await subscription.GetResourceGroupAsync("my-rg");
var capacityCollection = resourceGroup.Value.GetFabricCapacities();
```

#### ❌ INCORRECT: Trying to get capacities directly from client
```csharp
var capacities = armClient.GetFabricCapacities();  // Not valid
```

---

## 7. Provisioning and Resource States

### 7.1 State Checking
#### ✅ CORRECT: Check provisioning state before operations
```csharp
var capacity = await resourceGroup.Value.GetFabricCapacityAsync("my-capacity");
if (capacity.Value.Data.Properties.ProvisioningState == FabricProvisioningState.Succeeded)
{
    // Safe to perform operations
}
```

#### ❌ INCORRECT: Ignoring provisioning state
```csharp
var capacity = await resourceGroup.Value.GetFabricCapacityAsync("my-capacity");
await capacity.Value.SuspendAsync(WaitUntil.Completed);  // May fail if not Active
```

---

## 8. Best Practices

### 8.1 Idempotent Operations
#### ✅ CORRECT: Use CreateOrUpdateAsync for idempotency
```csharp
var operation = await capacityCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-capacity", capacityData);
```

### 8.2 Tags
#### ✅ CORRECT: Include tags for resource management
```csharp
var capacityData = new FabricCapacityData(location, properties, sku)
{
    Tags = { ["Environment"] = "Production", ["Team"] = "DataPlatform" }
};
```

### 8.3 Valid SKU Names
#### ✅ CORRECT: Use valid Fabric SKU names
```csharp
// Valid: F2, F4, F8, F16, F32, F64, F128, F256, F512, F1024, F2048
var sku = new FabricSku("F64", FabricSkuTier.Fabric);
```

#### ❌ INCORRECT: Invalid SKU names
```csharp
var sku = new FabricSku("Standard_F64", FabricSkuTier.Fabric);  // Wrong format
```

---

## Summary Checklist

- [ ] Uses `DefaultAzureCredential` for authentication
- [ ] Imports `Azure.ResourceManager.Fabric` and `Azure.ResourceManager.Fabric.Models`
- [ ] Creates `ArmClient` with credential
- [ ] Navigates hierarchy: Subscription → ResourceGroup → FabricCapacities
- [ ] Uses `async/await` for all operations
- [ ] Uses `WaitUntil.Completed` or properly handles `WaitUntil.Started`
- [ ] Handles `RequestFailedException` with specific status codes
- [ ] Uses valid SKU names (F2, F4, F8, F16, F32, F64, F128, F256, F512, F1024, F2048)
- [ ] Checks provisioning state before dependent operations
- [ ] Uses `CreateOrUpdateAsync` for idempotent operations
