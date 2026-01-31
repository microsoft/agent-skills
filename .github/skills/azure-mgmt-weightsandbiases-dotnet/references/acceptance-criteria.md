# Azure.ResourceManager.WeightsAndBiases Acceptance Criteria

**SDK**: `Azure.ResourceManager.WeightsAndBiases`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/weightsandbiases
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Standard ARM Weights & Biases imports
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.WeightsAndBiases;
using Azure.ResourceManager.WeightsAndBiases.Models;
```

#### ❌ INCORRECT: Missing core imports
```csharp
using Azure.ResourceManager.WeightsAndBiases;
// Missing Azure.Identity and Azure.ResourceManager
```

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
using WandB.Azure;
using Azure.WeightsAndBiases;
```

---

## 2. Client Creation

### 2.1 ARM Client Initialization
#### ✅ CORRECT: Using DefaultAzureCredential
```csharp
ArmClient client = new ArmClient(new DefaultAzureCredential());
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

### 3.1 Create W&B Instance
#### ✅ CORRECT: Full instance creation with all required properties
```csharp
var resourceGroup = await client.GetDefaultSubscriptionAsync()
    .Result.GetResourceGroupAsync("my-resource-group");

var instances = resourceGroup.Value.GetWeightsAndBiasesInstances();

var data = new WeightsAndBiasesInstanceData(AzureLocation.EastUS)
{
    Properties = new WeightsAndBiasesInstanceProperties
    {
        Marketplace = new WeightsAndBiasesMarketplaceDetails
        {
            SubscriptionId = "<marketplace-subscription-id>",
            OfferDetails = new WeightsAndBiasesOfferDetails
            {
                PublisherId = "wandb",
                OfferId = "wandb-pay-as-you-go",
                PlanId = "wandb-payg",
                PlanName = "Pay As You Go",
                TermId = "monthly",
                TermUnit = "P1M"
            }
        },
        User = new WeightsAndBiasesUserDetails
        {
            FirstName = "Admin",
            LastName = "User",
            EmailAddress = "admin@example.com",
            Upn = "admin@example.com"
        },
        PartnerProperties = new WeightsAndBiasesPartnerProperties
        {
            Region = WeightsAndBiasesRegion.EastUS,
            Subdomain = "my-company-wandb"
        }
    }
};

var operation = await instances.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-wandb-instance", data);
```

#### ❌ INCORRECT: Missing required properties
```csharp
var data = new WeightsAndBiasesInstanceData(AzureLocation.EastUS);
// Missing Properties - will fail
```

#### ❌ INCORRECT: Wrong publisher ID
```csharp
var offerDetails = new WeightsAndBiasesOfferDetails
{
    PublisherId = "weights-and-biases",  // Wrong - should be "wandb"
    OfferId = "wandb-pay-as-you-go",
    // ...
};
```

### 3.2 Get W&B Instance
#### ✅ CORRECT: Async retrieval
```csharp
var instance = await resourceGroup.GetWeightsAndBiasesInstanceAsync("my-wandb-instance");
Console.WriteLine($"Instance: {instance.Value.Data.Name}");
Console.WriteLine($"State: {instance.Value.Data.Properties.ProvisioningState}");
```

#### ❌ INCORRECT: Synchronous call
```csharp
var instance = resourceGroup.GetWeightsAndBiasesInstance("my-wandb-instance");  // Use async
```

### 3.3 List W&B Instances
#### ✅ CORRECT: Async enumeration in resource group
```csharp
await foreach (var instance in resourceGroup.GetWeightsAndBiasesInstances())
{
    Console.WriteLine($"Instance: {instance.Data.Name}");
    Console.WriteLine($"  Location: {instance.Data.Location}");
    Console.WriteLine($"  State: {instance.Data.Properties.ProvisioningState}");
}
```

#### ✅ CORRECT: Async enumeration across subscription
```csharp
var subscription = await client.GetDefaultSubscriptionAsync();
await foreach (var instance in subscription.GetWeightsAndBiasesInstancesAsync())
{
    Console.WriteLine($"{instance.Data.Name} in {instance.Id.ResourceGroupName}");
}
```

#### ❌ INCORRECT: Blocking call
```csharp
var instances = resourceGroup.GetWeightsAndBiasesInstances().ToList();  // Use async
```

### 3.4 Configure Single Sign-On (SSO)
#### ✅ CORRECT: SSO configuration with SAML
```csharp
var instance = await resourceGroup.GetWeightsAndBiasesInstanceAsync("my-wandb-instance");
var updateData = instance.Value.Data;

updateData.Properties.SingleSignOnPropertiesV2 = new WeightsAndBiasSingleSignOnPropertiesV2
{
    Type = WeightsAndBiasSingleSignOnType.Saml,
    State = WeightsAndBiasSingleSignOnState.Enable,
    EnterpriseAppId = "<entra-app-id>",
    AadDomains = { "example.com", "contoso.com" }
};

var operation = await resourceGroup.GetWeightsAndBiasesInstances()
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-wandb-instance", updateData);
```

#### ❌ INCORRECT: Missing SSO type
```csharp
updateData.Properties.SingleSignOnPropertiesV2 = new WeightsAndBiasSingleSignOnPropertiesV2
{
    State = WeightsAndBiasSingleSignOnState.Enable,
    // Missing Type - required for SSO
};
```

### 3.5 Update Instance Tags
#### ✅ CORRECT: Using patch object
```csharp
var patch = new WeightsAndBiasesInstancePatch
{
    Tags =
    {
        { "environment", "production" },
        { "team", "ml-platform" },
        { "costCenter", "CC-ML-001" }
    }
};

var updatedInstance = await instance.Value.UpdateAsync(patch);
```

#### ❌ INCORRECT: Modifying Data.Tags directly
```csharp
instance.Data.Tags["NewTag"] = "Value";  // Won't persist
```

### 3.6 Delete Instance
#### ✅ CORRECT: Delete with wait
```csharp
await instance.Value.DeleteAsync(WaitUntil.Completed);
```

#### ❌ INCORRECT: Not waiting for deletion
```csharp
await instance.Value.DeleteAsync(WaitUntil.Started);
// Immediately trying to recreate - may fail
```

---

## 4. Error Handling

### 4.1 RequestFailedException Handling
#### ✅ CORRECT: Specific exception handling
```csharp
try
{
    var operation = await instances.CreateOrUpdateAsync(
        WaitUntil.Completed, "my-wandb", data);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Instance already exists or name conflict");
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

#### ❌ INCORRECT: Catching generic Exception
```csharp
try
{
    var operation = await instances.CreateOrUpdateAsync(...);
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
var operation = await instances.CreateOrUpdateAsync(
    WaitUntil.Completed, instanceName, data);
var instance = operation.Value;  // Safe to access
```

#### ✅ CORRECT: Start and poll manually
```csharp
var operation = await instances.CreateOrUpdateAsync(
    WaitUntil.Started, instanceName, data);

while (!operation.HasCompleted)
{
    await Task.Delay(TimeSpan.FromSeconds(5));
    await operation.UpdateStatusAsync();
}
```

#### ❌ INCORRECT: Accessing Value before completion
```csharp
var operation = await instances.CreateOrUpdateAsync(
    WaitUntil.Started, instanceName, data);
var instance = operation.Value;  // May throw
```

---

## 6. Resource Hierarchy Navigation

### 6.1 Proper Hierarchy
#### ✅ CORRECT: Navigate through ARM hierarchy
```csharp
var subscription = await client.GetDefaultSubscriptionAsync();
var resourceGroup = await subscription.GetResourceGroupAsync("my-rg");
var instances = resourceGroup.Value.GetWeightsAndBiasesInstances();
```

#### ❌ INCORRECT: Direct access attempt
```csharp
var instances = client.GetWeightsAndBiasesInstances();  // Not valid
```

---

## 7. Available Regions

### 7.1 Valid Region Values
#### ✅ CORRECT: Use WeightsAndBiasesRegion enum
```csharp
var partnerProperties = new WeightsAndBiasesPartnerProperties
{
    Region = WeightsAndBiasesRegion.EastUS,  // Valid
    Subdomain = "my-subdomain"
};
```

#### ❌ INCORRECT: Using string for region
```csharp
var partnerProperties = new WeightsAndBiasesPartnerProperties
{
    Region = "East US",  // Wrong - use enum
    Subdomain = "my-subdomain"
};
```

**Valid Regions:**
- `WeightsAndBiasesRegion.EastUS`
- `WeightsAndBiasesRegion.CentralUS`
- `WeightsAndBiasesRegion.WestUS`
- `WeightsAndBiasesRegion.WestEurope`
- `WeightsAndBiasesRegion.JapanEast`
- `WeightsAndBiasesRegion.KoreaCentral`

---

## 8. Marketplace Configuration

### 8.1 Offer Details
#### ✅ CORRECT: Standard W&B marketplace offer
```csharp
var offerDetails = new WeightsAndBiasesOfferDetails
{
    PublisherId = "wandb",
    OfferId = "wandb-pay-as-you-go",
    PlanId = "wandb-payg",
    PlanName = "Pay As You Go",
    TermId = "monthly",
    TermUnit = "P1M"
};
```

---

## 9. Managed Identity

### 9.1 Enable System-Assigned Identity
#### ✅ CORRECT: Add managed identity
```csharp
var data = new WeightsAndBiasesInstanceData(AzureLocation.EastUS)
{
    Properties = new WeightsAndBiasesInstanceProperties { /* ... */ },
    Identity = new ManagedServiceIdentity(ManagedServiceIdentityType.SystemAssigned)
};
```

---

## Summary Checklist

- [ ] Uses `DefaultAzureCredential` for authentication
- [ ] Imports `Azure.ResourceManager.WeightsAndBiases` and models namespace
- [ ] Creates `ArmClient` with credential
- [ ] Navigates hierarchy: Subscription → ResourceGroup → Instances
- [ ] Uses `async/await` for all operations
- [ ] Provides complete `WeightsAndBiasesInstanceProperties` with marketplace and user details
- [ ] Uses correct publisher ID: `wandb`
- [ ] Uses `WeightsAndBiasesRegion` enum for region values
- [ ] Handles `RequestFailedException` with status codes
- [ ] Uses `WaitUntil.Completed` for blocking operations
- [ ] Checks provisioning state before dependent operations
- [ ] Uses `WeightsAndBiasesInstancePatch` for updates
