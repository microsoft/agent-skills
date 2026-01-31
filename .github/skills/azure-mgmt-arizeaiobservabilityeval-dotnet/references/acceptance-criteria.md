# Azure Arize AI Observability Eval SDK Acceptance Criteria

**SDK**: `Azure.ResourceManager.ArizeAIObservabilityEval`  
**Repository**: https://github.com/Azure/azure-sdk-for-net  
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Full namespace imports
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ArizeAIObservabilityEval;
using Azure.ResourceManager.ArizeAIObservabilityEval.Models;
```

#### ❌ INCORRECT: Missing required namespaces
```csharp
using Azure.ResourceManager.ArizeAIObservabilityEval;
// Missing Azure.Identity, Azure.ResourceManager
```

### 1.2 Model Imports
#### ✅ CORRECT: Models namespace for data types
```csharp
using Azure.ResourceManager.ArizeAIObservabilityEval.Models;

ArizeAIObservabilityEvalOrganizationProperties props;
ArizeAIObservabilityEvalMarketplaceDetails marketplace;
```

#### ❌ INCORRECT: Using wrong SDK namespaces
```csharp
using Arize.Client;  // Wrong - third-party client SDK
```

---

## 2. Client Creation

### 2.1 ArmClient Initialization
#### ✅ CORRECT: Using DefaultAzureCredential
```csharp
var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);
```

#### ❌ INCORRECT: Hardcoded credentials
```csharp
var armClient = new ArmClient(new ClientSecretCredential(tenantId, clientId, clientSecret));
```

### 2.2 Subscription Access
#### ✅ CORRECT: Using CreateResourceIdentifier
```csharp
var subscriptionId = Environment.GetEnvironmentVariable("AZURE_SUBSCRIPTION_ID");
var subscription = await armClient.GetSubscriptionResource(
    SubscriptionResource.CreateResourceIdentifier(subscriptionId)).GetAsync();
```

#### ❌ INCORRECT: Hardcoded subscription ID
```csharp
var subscription = armClient.GetSubscriptionResource(
    SubscriptionResource.CreateResourceIdentifier("12345678-1234-1234-1234-123456789012"));
```

---

## 3. Core Operations

### 3.1 Create Arize AI Organization
#### ✅ CORRECT: Full organization configuration
```csharp
var resourceGroup = await subscription.Value.GetResourceGroupAsync("my-resource-group");

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
    },
    Tags = { ["environment"] = "production" }
};

var operation = await collection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-arize-org",
    data);

var organization = operation.Value;
```

#### ❌ INCORRECT: Missing required Properties
```csharp
var data = new ArizeAIObservabilityEvalOrganizationData(AzureLocation.EastUS);
// Missing Properties - organization creation will fail
```

### 3.2 Marketplace Configuration
#### ✅ CORRECT: Complete offer details
```csharp
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
}
```

#### ❌ INCORRECT: Missing publisher ID
```csharp
Marketplace = new ArizeAIObservabilityEvalMarketplaceDetails
{
    OfferDetails = new ArizeAIObservabilityEvalOfferDetails
    {
        // Missing PublisherId - required field
        OfferId = "arize-liftr-1"
    }
}
```

### 3.3 User Details
#### ✅ CORRECT: Complete user information
```csharp
User = new ArizeAIObservabilityEvalUserDetails
{
    FirstName = "John",
    LastName = "Doe",
    EmailAddress = "john.doe@example.com"
}
```

#### ❌ INCORRECT: Missing required email
```csharp
User = new ArizeAIObservabilityEvalUserDetails
{
    FirstName = "John",
    LastName = "Doe"
    // Missing EmailAddress - typically required
}
```

---

## 4. Resource Access Patterns

### 4.1 Get Organization
#### ✅ CORRECT: Using GetAsync
```csharp
var org = await collection.GetAsync("my-arize-org");
```

### 4.2 Check Existence
#### ✅ CORRECT: Using ExistsAsync
```csharp
var exists = await collection.ExistsAsync("my-arize-org");
if (exists.Value)
{
    var org = await collection.GetAsync("my-arize-org");
}
```

### 4.3 Get If Exists
#### ✅ CORRECT: Using GetIfExistsAsync
```csharp
var response = await collection.GetIfExistsAsync("my-arize-org");
if (response.HasValue)
{
    var org = response.Value;
}
```

#### ❌ INCORRECT: Using try-catch for existence check
```csharp
try
{
    var org = await collection.GetAsync("my-arize-org");
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    // Less efficient than GetIfExistsAsync
}
```

---

## 5. Listing Organizations

### 5.1 List in Resource Group
#### ✅ CORRECT: Using async enumeration
```csharp
await foreach (var org in collection.GetAllAsync())
{
    Console.WriteLine($"Org: {org.Data.Name}, State: {org.Data.Properties?.ProvisioningState}");
}
```

#### ❌ INCORRECT: Converting to list synchronously
```csharp
var orgs = collection.GetAllAsync().ToList();  // Wrong - blocks async
```

### 5.2 List in Subscription
#### ✅ CORRECT: Subscription-level listing
```csharp
await foreach (var org in subscription.Value.GetArizeAIObservabilityEvalOrganizationsAsync())
{
    Console.WriteLine($"Org: {org.Data.Name}");
}
```

---

## 6. Update Operations

### 6.1 Update Tags
#### ✅ CORRECT: Using Patch model
```csharp
var org = await collection.GetAsync("my-arize-org");
var updateData = new ArizeAIObservabilityEvalOrganizationPatch
{
    Tags = { ["environment"] = "staging", ["team"] = "ml-ops" }
};
var updated = await org.Value.UpdateAsync(updateData);
```

#### ❌ INCORRECT: Trying to update with full data model
```csharp
var org = await collection.GetAsync("my-arize-org");
org.Value.Data.Tags["environment"] = "staging";
// Data is read-only - use Patch model
```

---

## 7. Delete Operations

### 7.1 Delete Organization
#### ✅ CORRECT: Using DeleteAsync with WaitUntil
```csharp
var org = await collection.GetAsync("my-arize-org");
await org.Value.DeleteAsync(WaitUntil.Completed);
```

#### ❌ INCORRECT: Missing WaitUntil
```csharp
await org.Value.DeleteAsync();  // Missing WaitUntil parameter
```

---

## 8. Direct Resource Access

### 8.1 Access by Resource ID
#### ✅ CORRECT: Using CreateResourceIdentifier
```csharp
var resourceId = ArizeAIObservabilityEvalOrganizationResource.CreateResourceIdentifier(
    subscriptionId,
    "my-resource-group",
    "my-arize-org");

var org = armClient.GetArizeAIObservabilityEvalOrganizationResource(resourceId);
var data = await org.GetAsync();
```

#### ❌ INCORRECT: Constructing resource ID manually
```csharp
var resourceId = new ResourceIdentifier(
    "/subscriptions/.../resourceGroups/.../providers/ArizeAi.ObservabilityEval/organizations/my-arize-org");
// Use CreateResourceIdentifier for type safety
```

---

## 9. Error Handling

### 9.1 RequestFailedException Handling
#### ✅ CORRECT: Pattern matching on status codes
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

#### ❌ INCORRECT: Generic exception handling
```csharp
try
{
    var org = await collection.GetAsync("my-arize-org");
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);  // Loses Azure-specific context
}
```

---

## 10. Enum Values

### 10.1 Provisioning State Values
#### ✅ CORRECT: Valid provisioning states
```csharp
ArizeAIObservabilityEvalOfferProvisioningState.Succeeded
ArizeAIObservabilityEvalOfferProvisioningState.Failed
ArizeAIObservabilityEvalOfferProvisioningState.Canceled
ArizeAIObservabilityEvalOfferProvisioningState.Provisioning
ArizeAIObservabilityEvalOfferProvisioningState.Updating
ArizeAIObservabilityEvalOfferProvisioningState.Deleting
ArizeAIObservabilityEvalOfferProvisioningState.Accepted
```

### 10.2 Marketplace Subscription Status Values
#### ✅ CORRECT: Valid subscription statuses
```csharp
ArizeAIObservabilityEvalMarketplaceSubscriptionStatus.PendingFulfillmentStart
ArizeAIObservabilityEvalMarketplaceSubscriptionStatus.Subscribed
ArizeAIObservabilityEvalMarketplaceSubscriptionStatus.Suspended
ArizeAIObservabilityEvalMarketplaceSubscriptionStatus.Unsubscribed
```

### 10.3 SSO Configuration
#### ✅ CORRECT: SSO types and states
```csharp
ArizeAIObservabilityEvalSingleSignOnType.Saml
ArizeAIObservabilityEvalSingleSignOnType.OpenId

ArizeAIObservabilityEvalSingleSignOnState.Initial
ArizeAIObservabilityEvalSingleSignOnState.Enable
ArizeAIObservabilityEvalSingleSignOnState.Disable
```

---

## 11. Key Types Reference

| Type | Purpose |
|------|---------|
| `ArizeAIObservabilityEvalOrganizationResource` | Main ARM resource |
| `ArizeAIObservabilityEvalOrganizationCollection` | Collection for CRUD |
| `ArizeAIObservabilityEvalOrganizationData` | Resource data model |
| `ArizeAIObservabilityEvalOrganizationProperties` | Organization properties |
| `ArizeAIObservabilityEvalMarketplaceDetails` | Marketplace subscription info |
| `ArizeAIObservabilityEvalOfferDetails` | Marketplace offer config |
| `ArizeAIObservabilityEvalUserDetails` | User contact information |
| `ArizeAIObservabilityEvalOrganizationPatch` | Patch model for updates |

---

## 12. Best Practices Checklist

- [ ] Use `DefaultAzureCredential` for authentication
- [ ] Use `async/await` for all operations
- [ ] Use `WaitUntil.Completed` for synchronous completion
- [ ] Use `GetIfExistsAsync` for conditional logic
- [ ] Use `CreateResourceIdentifier` for direct resource access
- [ ] Include complete marketplace offer details
- [ ] Include user contact information
- [ ] Use `ArizeAIObservabilityEvalOrganizationPatch` for updates
- [ ] Handle `RequestFailedException` with status code matching
- [ ] Use `await foreach` for listing resources
- [ ] Store subscription IDs in environment variables
