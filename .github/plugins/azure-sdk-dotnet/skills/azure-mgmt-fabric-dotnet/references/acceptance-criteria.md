# Azure.ResourceManager.Fabric SDK Acceptance Criteria (.NET)

**SDK**: `Azure.ResourceManager.Fabric`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/fabric/Azure.ResourceManager.Fabric
**Package**: https://www.nuget.org/packages/Azure.ResourceManager.Fabric
**Purpose**: Skill testing acceptance criteria for validating generated C# code correctness

---

## 1. Correct Using Statements

### 1.1 Core Imports

#### ✅ CORRECT: Basic Client Imports
```csharp
using Azure;
using Azure.Core;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.Fabric;
using Azure.ResourceManager.Fabric.Models;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using Azure.Fabric;
using Microsoft.Fabric.Management;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Create ArmClient
```csharp
var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);
```

---

## 3. Fabric Capacity Operations

### 3.1 ✅ CORRECT: Create Fabric Capacity
```csharp
var administration = new FabricCapacityAdministration(
    new[] { "admin@contoso.com" }
);

var properties = new FabricCapacityProperties(administration);

var sku = new FabricSku("F64", FabricSkuTier.Fabric);

var capacityData = new FabricCapacityData(
    AzureLocation.WestUS2,
    properties,
    sku);

var capacityCollection = resourceGroup.Value.GetFabricCapacities();
var operation = await capacityCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-fabric-capacity",
    capacityData);

FabricCapacityResource capacity = operation.Value;
```

### 3.2 ✅ CORRECT: Update Capacity (Scale)
```csharp
var patch = new FabricCapacityPatch
{
    Sku = new FabricSku("F128", FabricSkuTier.Fabric)
};

var updateOperation = await capacity.Value.UpdateAsync(
    WaitUntil.Completed,
    patch);
```

### 3.3 ✅ CORRECT: Suspend and Resume
```csharp
// Suspend
await capacity.Value.SuspendAsync(WaitUntil.Completed);

// Resume
var resumeOperation = await capacity.Value.ResumeAsync(WaitUntil.Completed);
```

### 3.4 ✅ CORRECT: Check Name Availability
```csharp
var checkContent = new FabricNameAvailabilityContent
{
    Name = "my-new-capacity",
    ResourceType = "Microsoft.Fabric/capacities"
};

var result = await subscription.CheckFabricCapacityNameAvailabilityAsync(
    AzureLocation.WestUS2,
    checkContent);
```

### 3.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing required parameters
```csharp
// WRONG - Missing administration and sku
var capacityData = new FabricCapacityData(AzureLocation.WestUS2);
```

---

## 4. Error Handling Patterns

### 4.1 ✅ CORRECT: Handle RequestFailedException
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
catch (RequestFailedException ex) when (ex.Status == 403)
{
    Console.WriteLine("Insufficient permissions or quota exceeded");
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
| `FabricCapacityResource` | Represents a Fabric capacity |
| `FabricCapacityCollection` | Collection for CRUD |
| `FabricCapacityData` | Capacity data model |
| `FabricCapacityPatch` | Update payload |
| `FabricCapacityProperties` | Capacity properties |
| `FabricCapacityAdministration` | Admin configuration |
| `FabricSku` | SKU configuration |
| `FabricSkuTier` | Pricing tier |

## 6. SKU Reference

| SKU Name | Capacity Units |
|----------|----------------|
| F2 | 2 |
| F4 | 4 |
| F8 | 8 |
| F16 | 16 |
| F32 | 32 |
| F64 | 64 |
| F128 | 128 |
| F256 | 256 |
| F512 | 512 |
| F1024 | 1024 |
| F2048 | 2048 |

## 7. Resource States

| State | Description |
|-------|-------------|
| `Active` | Capacity is running |
| `Suspended` | Not billing for compute |
| `Provisioning` | Being provisioned |
| `Updating` | Being updated |
| `Scaling` | Scaling to different SKU |

---

## 8. Best Practices Summary

1. **Use WaitUntil.Completed** — For synchronous completion
2. **Use DefaultAzureCredential** — Never hardcode credentials
3. **Handle RequestFailedException** — For ARM API errors
4. **Suspend when not in use** — Fabric bills for compute even when idle
5. **Check provisioning state** — Before performing operations
6. **Use appropriate SKU** — Start small for dev/test
