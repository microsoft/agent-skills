# Azure.ResourceManager.WeightsAndBiases SDK Acceptance Criteria (.NET)

**SDK**: `Azure.ResourceManager.WeightsAndBiases`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/weightsandbiases/Azure.ResourceManager.WeightsAndBiases
**Package**: https://www.nuget.org/packages/Azure.ResourceManager.WeightsAndBiases
**Purpose**: Skill testing acceptance criteria for validating generated C# code correctness

---

## 1. Correct Using Statements

### 1.1 Core Imports

#### ✅ CORRECT: Basic Client Imports
```csharp
using Azure;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.WeightsAndBiases;
using Azure.ResourceManager.WeightsAndBiases.Models;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using WandB.Azure;
using Azure.WeightsAndBiases;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Create ArmClient
```csharp
ArmClient client = new ArmClient(new DefaultAzureCredential());
```

---

## 3. Instance Operations

### 3.1 ✅ CORRECT: Create W&B Instance
```csharp
WeightsAndBiasesInstanceCollection instances = resourceGroup.GetWeightsAndBiasesInstances();

WeightsAndBiasesInstanceData data = new WeightsAndBiasesInstanceData(AzureLocation.EastUS)
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

ArmOperation<WeightsAndBiasesInstanceResource> operation = await instances
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-wandb-instance", data);
```

### 3.2 ✅ CORRECT: Configure SSO
```csharp
updateData.Properties.SingleSignOnPropertiesV2 = new WeightsAndBiasSingleSignOnPropertiesV2
{
    Type = WeightsAndBiasSingleSignOnType.Saml,
    State = WeightsAndBiasSingleSignOnState.Enable,
    EnterpriseAppId = "<entra-app-id>",
    AadDomains = { "example.com" }
};
```

### 3.3 ✅ CORRECT: Update Instance
```csharp
WeightsAndBiasesInstancePatch patch = new WeightsAndBiasesInstancePatch
{
    Tags =
    {
        { "environment", "production" },
        { "team", "ml-platform" }
    }
};

instance = await instance.UpdateAsync(patch);
```

---

## 4. Error Handling Patterns

### 4.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    ArmOperation<WeightsAndBiasesInstanceResource> operation = await instances
        .CreateOrUpdateAsync(WaitUntil.Completed, "my-wandb", data);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Instance already exists");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Azure error: {ex.Status} - {ex.Message}");
}
```

---

## 5. Key Types Reference

| Type | Purpose |
|------|---------|
| `WeightsAndBiasesInstanceResource` | W&B instance resource |
| `WeightsAndBiasesInstanceData` | Instance configuration |
| `WeightsAndBiasesInstanceCollection` | Collection of instances |
| `WeightsAndBiasesInstanceProperties` | Instance properties |
| `WeightsAndBiasesMarketplaceDetails` | Marketplace subscription info |
| `WeightsAndBiasesOfferDetails` | Marketplace offer details |
| `WeightsAndBiasesUserDetails` | Admin user information |
| `WeightsAndBiasesPartnerProperties` | W&B-specific configuration |
| `WeightsAndBiasSingleSignOnPropertiesV2` | SSO configuration |
| `WeightsAndBiasesInstancePatch` | Patch for updates |
| `WeightsAndBiasesRegion` | Supported regions |

## 6. Available Regions

| Region Enum | Azure Region |
|-------------|--------------|
| `EastUS` | East US |
| `CentralUS` | Central US |
| `WestUS` | West US |
| `WestEurope` | West Europe |
| `JapanEast` | Japan East |
| `KoreaCentral` | Korea Central |

---

## 7. Best Practices Summary

1. **Use DefaultAzureCredential** — Supports multiple auth methods
2. **Enable managed identity** — For secure Azure resource access
3. **Configure SSO** — Enable Entra ID SSO for enterprise security
4. **Tag resources** — For cost tracking and organization
5. **Check provisioning state** — Wait for `Succeeded` before using
6. **Use appropriate region** — Choose closest to compute
