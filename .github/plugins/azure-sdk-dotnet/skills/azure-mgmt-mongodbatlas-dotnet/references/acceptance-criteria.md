# Azure.ResourceManager.MongoDBAtlas SDK Acceptance Criteria (.NET)

**SDK**: `Azure.ResourceManager.MongoDBAtlas`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/mongodbatlas/Azure.ResourceManager.MongoDBAtlas
**Package**: https://www.nuget.org/packages/Azure.ResourceManager.MongoDBAtlas
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
using Azure.ResourceManager.MongoDBAtlas;
using Azure.ResourceManager.MongoDBAtlas.Models;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using MongoDB.Atlas;
using Azure.MongoDB;
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

### 3.1 ✅ CORRECT: Create MongoDB Atlas Organization
```csharp
var organizationData = new MongoDBAtlasOrganizationData(AzureLocation.EastUS2)
{
    Properties = new MongoDBAtlasOrganizationProperties(
        marketplace: new MongoDBAtlasMarketplaceDetails(
            subscriptionId: "your-azure-subscription-id",
            offerDetails: new MongoDBAtlasOfferDetails(
                publisherId: "mongodb",
                offerId: "mongodb_atlas_azure_native_prod",
                planId: "private_plan",
                planName: "Pay as You Go (Free) (Private)",
                termUnit: "P1M",
                termId: "gmz7xq9ge3py"
            )
        ),
        user: new MongoDBAtlasUserDetails(
            emailAddress: "admin@example.com",
            upn: "admin@example.com"
        )
        {
            FirstName = "Admin",
            LastName = "User"
        }
    )
    {
        PartnerProperties = new MongoDBAtlasPartnerProperties
        {
            OrganizationName = "my-atlas-org"
        }
    }
};

var operation = await organizations.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-atlas-org",
    organizationData
);
```

### 3.2 ✅ CORRECT: Get Organization
```csharp
MongoDBAtlasOrganizationResource org = await organizations.GetAsync("my-atlas-org");
```

### 3.3 ✅ CORRECT: List Organizations
```csharp
await foreach (var org in organizations.GetAllAsync())
{
    Console.WriteLine($"Org: {org.Data.Name}");
}
```

### 3.4 ✅ CORRECT: Update Tags
```csharp
await organization.AddTagAsync("CostCenter", "12345");
await organization.SetTagsAsync(new Dictionary<string, string>
{
    ["Environment"] = "Production"
});
```

---

## 4. Error Handling Patterns

### 4.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    var org = await organizations.GetAsync("my-atlas-org");
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Organization not found");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Azure error: {ex.Message}");
}
```

---

## 5. Key Types Reference

| Type | Purpose |
|------|---------|
| `MongoDBAtlasOrganizationResource` | ARM resource for Atlas organization |
| `MongoDBAtlasOrganizationCollection` | Collection for CRUD |
| `MongoDBAtlasOrganizationData` | Resource data model |
| `MongoDBAtlasOrganizationProperties` | Organization properties |
| `MongoDBAtlasMarketplaceDetails` | Marketplace subscription details |
| `MongoDBAtlasOfferDetails` | Marketplace offer configuration |
| `MongoDBAtlasUserDetails` | User contact information |
| `MongoDBAtlasPartnerProperties` | MongoDB-specific properties |

## 6. Provisioning States

| State | Description |
|-------|-------------|
| `Succeeded` | Provisioned successfully |
| `Failed` | Provisioning failed |
| `Provisioning` | Being provisioned |
| `Updating` | Being updated |
| `Deleting` | Being deleted |

---

## 7. Best Practices Summary

1. **Use async methods** — All operations support async/await
2. **Handle long-running operations** — Use `WaitUntil.Completed`
3. **Use resource identifiers** — For direct resource access
4. **Check provisioning state** — Before performing operations
5. **Use tags** — For cost tracking and organization
