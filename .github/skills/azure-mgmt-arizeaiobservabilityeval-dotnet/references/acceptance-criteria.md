# Azure.ResourceManager.ArizeAIObservabilityEval SDK Acceptance Criteria (.NET)

**SDK**: `Azure.ResourceManager.ArizeAIObservabilityEval`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/arizeaiobservabilityeval/Azure.ResourceManager.ArizeAIObservabilityEval
**Package**: https://www.nuget.org/packages/Azure.ResourceManager.ArizeAIObservabilityEval
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
using Azure.ResourceManager.Resources;
using Azure.ResourceManager.ArizeAIObservabilityEval;
using Azure.ResourceManager.ArizeAIObservabilityEval.Models;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using Azure.ArizeAI;
using ArizeAI.Observability;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Create ArmClient
```csharp
var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);
```

---

## 3. Organization Operations

### 3.1 ✅ CORRECT: Create Arize AI Organization
```csharp
var collection = resourceGroup.Value.GetArizeAIObservabilityEvalOrganizations();

var data = new ArizeAIObservabilityEvalOrganizationData(AzureLocation.EastUS)
{
    Properties = new ArizeAIObservabilityEvalOrganizationProperties
    {
        Marketplace = new ArizeAIObservabilityEvalMarketplaceDetails
        {
            SubscriptionId = "marketplace-subscription-id",
            OfferDetails = new ArizeAIObservabilityEvalOfferDetails
            {
                PublisherId = "arikimlabs1649082416596",
                OfferId = "arize-liftr-1",
                PlanId = "arize-liftr-1-plan",
                PlanName = "Arize AI Plan",
                TermUnit = "P1M",
                TermId = "term-id"
            }
        },
        User = new ArizeAIObservabilityEvalUserDetails
        {
            FirstName = "John",
            LastName = "Doe",
            EmailAddress = "john.doe@example.com"
        }
    }
};

var operation = await collection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-arize-org",
    data);
```

### 3.2 ✅ CORRECT: Get Organization
```csharp
var org = await collection.GetAsync("my-arize-org");
```

### 3.3 ✅ CORRECT: Check If Exists
```csharp
var response = await collection.GetIfExistsAsync("my-arize-org");
if (response.HasValue)
{
    var org = response.Value;
}
```

### 3.4 ✅ CORRECT: List Organizations
```csharp
await foreach (var org in collection.GetAllAsync())
{
    Console.WriteLine($"Org: {org.Data.Name}");
}
```

### 3.5 ✅ CORRECT: Update Organization
```csharp
var updateData = new ArizeAIObservabilityEvalOrganizationPatch
{
    Tags = { ["environment"] = "staging" }
};
var updated = await org.Value.UpdateAsync(updateData);
```

### 3.6 ✅ CORRECT: Delete Organization
```csharp
await org.Value.DeleteAsync(WaitUntil.Completed);
```

---

## 4. Error Handling Patterns

### 4.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    var org = await collection.GetAsync("my-arize-org");
}
catch (Azure.RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Organization not found");
}
catch (Azure.RequestFailedException ex)
{
    Console.WriteLine($"Azure error: {ex.Message}");
}
```

---

## 5. Key Types Reference

| Type | Purpose |
|------|---------|
| `ArizeAIObservabilityEvalOrganizationResource` | Main ARM resource |
| `ArizeAIObservabilityEvalOrganizationCollection` | Collection for CRUD |
| `ArizeAIObservabilityEvalOrganizationData` | Resource data model |
| `ArizeAIObservabilityEvalOrganizationProperties` | Organization properties |
| `ArizeAIObservabilityEvalMarketplaceDetails` | Marketplace subscription info |
| `ArizeAIObservabilityEvalOfferDetails` | Marketplace offer configuration |
| `ArizeAIObservabilityEvalUserDetails` | User contact information |
| `ArizeAIObservabilityEvalOrganizationPatch` | Patch model for updates |

## 6. Provisioning States

| State | Description |
|-------|-------------|
| `Succeeded` | Resource provisioned successfully |
| `Failed` | Provisioning failed |
| `Canceled` | Provisioning was canceled |
| `Provisioning` | Resource is being provisioned |
| `Updating` | Resource is being updated |
| `Deleting` | Resource is being deleted |
| `Accepted` | Request accepted |

---

## 7. Best Practices Summary

1. **Use async methods** — All operations support async/await
2. **Handle long-running operations** — Use `WaitUntil.Completed` or poll manually
3. **Use GetIfExistsAsync** — Avoid exceptions for conditional logic
4. **Implement retry policies** — Configure via `ArmClientOptions`
5. **Use resource identifiers** — For direct resource access
