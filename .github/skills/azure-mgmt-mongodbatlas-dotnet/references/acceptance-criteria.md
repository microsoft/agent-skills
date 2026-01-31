# Azure.ResourceManager.MongoDBAtlas Acceptance Criteria

**SDK**: `Azure.ResourceManager.MongoDBAtlas`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/mongodbatlas
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Standard ARM MongoDB Atlas imports
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.MongoDBAtlas;
using Azure.ResourceManager.MongoDBAtlas.Models;
```

#### ❌ INCORRECT: Missing core imports
```csharp
using Azure.ResourceManager.MongoDBAtlas;
// Missing Azure.Identity and Azure.ResourceManager
```

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
using MongoDB.Atlas.Azure;
using Azure.MongoDBAtlas;
```

---

## 2. Client Creation

### 2.1 ARM Client Initialization
#### ✅ CORRECT: Using DefaultAzureCredential
```csharp
var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);
```

#### ❌ INCORRECT: Hardcoded credentials
```csharp
var credential = new ClientSecretCredential(tenantId, clientId, "my-secret");
```

#### ❌ INCORRECT: Missing credential
```csharp
var armClient = new ArmClient();
```

---

## 3. Core Operations

### 3.1 Create MongoDB Atlas Organization
#### ✅ CORRECT: Full organization creation with marketplace details
```csharp
var resourceGroup = await subscription.GetResourceGroupAsync("my-resource-group");
var organizations = resourceGroup.Value.GetMongoDBAtlasOrganizations();

var organizationData = new MongoDBAtlasOrganizationData(AzureLocation.EastUS2)
{
    Properties = new MongoDBAtlasOrganizationProperties(
        marketplace: new MongoDBAtlasMarketplaceDetails(
            subscriptionId: "your-subscription-id",
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
    )
};

var operation = await organizations.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-atlas-org", organizationData);
```

#### ❌ INCORRECT: Missing required marketplace details
```csharp
var organizationData = new MongoDBAtlasOrganizationData(AzureLocation.EastUS2);
// Missing Properties with marketplace and user details
```

#### ❌ INCORRECT: Wrong offer details
```csharp
var offerDetails = new MongoDBAtlasOfferDetails(
    publisherId: "mongo",  // Wrong - should be "mongodb"
    offerId: "atlas",      // Wrong format
    planId: "free",
    planName: "Free",
    termUnit: "monthly",   // Wrong - should be "P1M"
    termId: "term1"
);
```

### 3.2 Get Organization
#### ✅ CORRECT: Get from collection
```csharp
var org = await organizations.GetAsync("my-atlas-org");
Console.WriteLine($"Org: {org.Value.Data.Name}");
Console.WriteLine($"State: {org.Value.Data.Properties?.ProvisioningState}");
```

#### ✅ CORRECT: Get using resource identifier
```csharp
var resourceId = MongoDBAtlasOrganizationResource.CreateResourceIdentifier(
    subscriptionId: "subscription-id",
    resourceGroupName: "my-resource-group",
    organizationName: "my-atlas-org"
);
var orgResource = armClient.GetMongoDBAtlasOrganizationResource(resourceId);
await orgResource.GetAsync();
```

#### ❌ INCORRECT: Synchronous access
```csharp
var org = organizations.Get("my-atlas-org");  // Use async
```

### 3.3 List Organizations
#### ✅ CORRECT: Async enumeration in resource group
```csharp
await foreach (var org in organizations.GetAllAsync())
{
    Console.WriteLine($"Org: {org.Data.Name}");
    Console.WriteLine($"  State: {org.Data.Properties?.ProvisioningState}");
}
```

#### ✅ CORRECT: Async enumeration across subscription
```csharp
await foreach (var org in subscription.GetMongoDBAtlasOrganizationsAsync())
{
    Console.WriteLine($"Org: {org.Data.Name} in {org.Data.Id}");
}
```

#### ❌ INCORRECT: Blocking enumeration
```csharp
var orgs = organizations.GetAllAsync().ToListAsync().Result;  // Don't block
```

### 3.4 Update Tags
#### ✅ CORRECT: Tag operations
```csharp
// Add single tag
await organization.AddTagAsync("CostCenter", "12345");

// Replace all tags
await organization.SetTagsAsync(new Dictionary<string, string>
{
    ["Environment"] = "Production",
    ["Team"] = "Platform"
});

// Remove tag
await organization.RemoveTagAsync("OldTag");
```

#### ❌ INCORRECT: Modifying Data.Tags directly
```csharp
organization.Data.Tags["NewTag"] = "Value";  // Won't persist
```

### 3.5 Update Organization Properties
#### ✅ CORRECT: Using patch object
```csharp
var patch = new MongoDBAtlasOrganizationPatch
{
    Tags = { ["UpdatedAt"] = DateTime.UtcNow.ToString("o") },
    Properties = new MongoDBAtlasOrganizationUpdateProperties
    {
        User = new MongoDBAtlasUserDetails(
            emailAddress: "newadmin@example.com",
            upn: "newadmin@example.com"
        )
    }
};

var operation = await organization.UpdateAsync(WaitUntil.Completed, patch);
```

### 3.6 Delete Organization
#### ✅ CORRECT: Delete with wait
```csharp
await organization.DeleteAsync(WaitUntil.Completed);
```

#### ❌ INCORRECT: Not waiting for deletion
```csharp
await organization.DeleteAsync(WaitUntil.Started);
// Immediately trying to recreate - may fail
```

---

## 4. Error Handling

### 4.1 RequestFailedException Handling
#### ✅ CORRECT: Specific exception handling
```csharp
try
{
    var operation = await organizations.CreateOrUpdateAsync(
        WaitUntil.Completed, orgName, orgData);
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Organization not found");
}
catch (RequestFailedException ex) when (ex.Status == 403)
{
    Console.WriteLine("Authorization failed - check RBAC roles");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid parameters: {ex.Message}");
}
```

#### ❌ INCORRECT: Swallowing exceptions
```csharp
try
{
    var operation = await organizations.CreateOrUpdateAsync(...);
}
catch { }  // Never do this
```

---

## 5. Long-Running Operations

### 5.1 Wait Options
#### ✅ CORRECT: Wait for completion
```csharp
var operation = await organizations.CreateOrUpdateAsync(
    WaitUntil.Completed, orgName, orgData);
var org = operation.Value;  // Safe to access
```

#### ✅ CORRECT: Manual polling
```csharp
var operation = await organizations.CreateOrUpdateAsync(
    WaitUntil.Started, orgName, orgData);

while (!operation.HasCompleted)
{
    await Task.Delay(TimeSpan.FromSeconds(5));
    await operation.UpdateStatusAsync();
}
```

#### ❌ INCORRECT: Accessing Value before completion
```csharp
var operation = await organizations.CreateOrUpdateAsync(
    WaitUntil.Started, orgName, orgData);
var org = operation.Value;  // May throw
```

---

## 6. Resource Hierarchy Navigation

### 6.1 Proper Hierarchy
#### ✅ CORRECT: Navigate through ARM hierarchy
```csharp
var subscription = await armClient.GetDefaultSubscriptionAsync();
var resourceGroup = await subscription.GetResourceGroupAsync("my-rg");
var organizations = resourceGroup.Value.GetMongoDBAtlasOrganizations();
```

#### ❌ INCORRECT: Direct access attempt
```csharp
var orgs = armClient.GetMongoDBAtlasOrganizations();  // Not valid
```

---

## 7. Provisioning States

### 7.1 Check Provisioning State
#### ✅ CORRECT: Check state before operations
```csharp
var org = await organizations.GetAsync("my-org");
if (org.Value.Data.Properties?.ProvisioningState == 
    MongoDBAtlasResourceProvisioningState.Succeeded)
{
    Console.WriteLine("Organization is ready");
}
```

---

## 8. Marketplace Configuration

### 8.1 Offer Details
#### ✅ CORRECT: Standard MongoDB Atlas marketplace offer
```csharp
var offerDetails = new MongoDBAtlasOfferDetails(
    publisherId: "mongodb",
    offerId: "mongodb_atlas_azure_native_prod",
    planId: "private_plan",
    planName: "Pay as You Go (Free) (Private)",
    termUnit: "P1M",
    termId: "gmz7xq9ge3py"
);
```

### 8.2 User Details
#### ✅ CORRECT: User with all fields
```csharp
var user = new MongoDBAtlasUserDetails(
    emailAddress: "admin@example.com",
    upn: "admin@example.com"
)
{
    FirstName = "Admin",
    LastName = "User"
};
```

---

## Summary Checklist

- [ ] Uses `DefaultAzureCredential` for authentication
- [ ] Imports `Azure.ResourceManager.MongoDBAtlas` and models namespace
- [ ] Creates `ArmClient` with credential
- [ ] Navigates hierarchy: Subscription → ResourceGroup → Organizations
- [ ] Uses `async/await` for all operations
- [ ] Provides complete `MongoDBAtlasOrganizationProperties` with marketplace and user details
- [ ] Uses correct publisher ID: `mongodb`
- [ ] Uses correct term unit format: `P1M`
- [ ] Handles `RequestFailedException` with status codes
- [ ] Uses `WaitUntil.Completed` for blocking operations
- [ ] Checks provisioning state before dependent operations
