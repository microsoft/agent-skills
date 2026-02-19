# Azure.ResourceManager.ApiManagement SDK Acceptance Criteria (.NET)

**SDK**: `Azure.ResourceManager.ApiManagement`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/apimanagement/Azure.ResourceManager.ApiManagement
**Package**: https://www.nuget.org/packages/Azure.ResourceManager.ApiManagement
**Purpose**: Skill testing acceptance criteria for validating generated C# code correctness

---

## 1. Correct Using Statements

### 1.1 Core Imports

#### ✅ CORRECT: Basic Client Imports
```csharp
using Azure;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ApiManagement;
using Azure.ResourceManager.ApiManagement.Models;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using Azure.ApiManagement;
using Azure.ResourceManager.ApiManagement.Client;
using ApiManagement;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Create ArmClient
```csharp
var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);
```

### 2.2 ✅ CORRECT: Get Subscription
```csharp
var subscriptionId = Environment.GetEnvironmentVariable("AZURE_SUBSCRIPTION_ID");
var subscription = armClient.GetSubscriptionResource(
    new ResourceIdentifier($"/subscriptions/{subscriptionId}"));
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing credential
```csharp
// WRONG - Must provide credential
ArmClient client = new ArmClient();
```

---

## 3. API Management Service Operations

### 3.1 ✅ CORRECT: Create APIM Service
```csharp
var serviceData = new ApiManagementServiceData(
    location: AzureLocation.EastUS,
    sku: new ApiManagementServiceSkuProperties(
        ApiManagementServiceSkuType.Developer, 
        capacity: 1),
    publisherEmail: "admin@contoso.com",
    publisherName: "Contoso");

var serviceCollection = resourceGroup.Value.GetApiManagementServices();
var operation = await serviceCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-apim-service",
    serviceData);

ApiManagementServiceResource service = operation.Value;
```

### 3.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing required parameters
```csharp
// WRONG - Missing publisherEmail and publisherName
var serviceData = new ApiManagementServiceData(
    location: AzureLocation.EastUS,
    sku: new ApiManagementServiceSkuProperties(ApiManagementServiceSkuType.Developer, 1));
```

#### ❌ INCORRECT: Wrong SKU type
```csharp
// WRONG - Use ApiManagementServiceSkuType enum
sku: new ApiManagementServiceSkuProperties("Developer", 1)
```

---

## 4. API Operations

### 4.1 ✅ CORRECT: Create API
```csharp
var apiData = new ApiCreateOrUpdateContent
{
    DisplayName = "My API",
    Path = "myapi",
    Protocols = { ApiOperationInvokableProtocol.Https },
    ServiceUri = new Uri("https://backend.contoso.com/api")
};

var apiCollection = service.GetApis();
var apiOperation = await apiCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-api",
    apiData);

ApiResource api = apiOperation.Value;
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using wrong content type
```csharp
// WRONG - Use ApiCreateOrUpdateContent, not ApiData
var apiData = new ApiData { ... };
```

---

## 5. Product Operations

### 5.1 ✅ CORRECT: Create Product
```csharp
var productData = new ApiManagementProductData
{
    DisplayName = "Starter",
    Description = "Starter tier with limited access",
    IsSubscriptionRequired = true,
    IsApprovalRequired = false,
    SubscriptionsLimit = 1,
    State = ApiManagementProductState.Published
};

var productCollection = service.GetApiManagementProducts();
var productOperation = await productCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "starter",
    productData);

ApiManagementProductResource product = productOperation.Value;
```

### 5.2 ✅ CORRECT: Add API to Product
```csharp
await product.GetProductApis().CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-api");
```

---

## 6. Subscription Operations

### 6.1 ✅ CORRECT: Create Subscription
```csharp
var subscriptionData = new ApiManagementSubscriptionCreateOrUpdateContent
{
    DisplayName = "My Subscription",
    Scope = $"/products/{product.Data.Name}",
    State = ApiManagementSubscriptionState.Active
};

var subscriptionCollection = service.GetApiManagementSubscriptions();
var subOperation = await subscriptionCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-subscription",
    subscriptionData);

ApiManagementSubscriptionResource subscription = subOperation.Value;
```

### 6.2 ✅ CORRECT: Get Subscription Keys
```csharp
var keys = await subscription.GetSecretsAsync();
Console.WriteLine($"Primary Key: {keys.Value.PrimaryKey}");
```

---

## 7. Policy Operations

### 7.1 ✅ CORRECT: Set API Policy
```csharp
var policyXml = @"
<policies>
    <inbound>
        <rate-limit calls=""100"" renewal-period=""60"" />
        <base />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>";

var policyData = new PolicyContractData
{
    Value = policyXml,
    Format = PolicyContentFormat.Xml
};

await api.GetApiPolicy().CreateOrUpdateAsync(
    WaitUntil.Completed,
    policyData);
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing base element
```csharp
// WRONG - Policy should include <base /> in each section
var policyXml = @"<policies><inbound><rate-limit /></inbound></policies>";
```

---

## 8. Error Handling Patterns

### 8.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    var operation = await serviceCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, serviceName, serviceData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Service already exists");
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

---

## 9. Key Types Reference

| Type | Purpose |
|------|---------|
| `ArmClient` | Entry point for all ARM operations |
| `ApiManagementServiceResource` | APIM service instance |
| `ApiResource` | Represents an API |
| `ApiManagementProductResource` | Represents a product |
| `ApiManagementSubscriptionResource` | Represents a subscription |
| `ApiManagementPolicyResource` | Service-level policy |
| `ApiPolicyResource` | API-level policy |
| `PolicyContractData` | Policy configuration |

## 10. SKU Types

| SKU | Purpose |
|-----|---------|
| `Developer` | Development/testing (no SLA) |
| `Basic` | Entry-level production |
| `Standard` | Medium workloads |
| `Premium` | High availability, multi-region |
| `Consumption` | Serverless, pay-per-call |

---

## 11. Best Practices Summary

1. **Use ArmClient** — Entry point for all APIM operations
2. **Use async methods** — All operations should use `*Async` methods
3. **Use WaitUntil.Completed** — For synchronous completion
4. **Use WaitUntil.Started** — For long operations like service creation (30+ min)
5. **Handle errors** — Use RequestFailedException with status filtering
6. **Use CreateOrUpdateAsync** — For idempotent operations
7. **Policy format** — Use XML format with proper structure
8. **SKU selection** — Developer SKU is fastest for testing (~15-30 min)
