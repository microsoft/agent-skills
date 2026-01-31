# Azure API Management SDK Acceptance Criteria

**SDK**: `Azure.ResourceManager.ApiManagement`  
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/apimanagement/Azure.ResourceManager.ApiManagement  
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Full namespace imports
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ApiManagement;
using Azure.ResourceManager.ApiManagement.Models;
```

#### ❌ INCORRECT: Missing required namespaces
```csharp
using Azure.ResourceManager.ApiManagement;
// Missing Azure.Identity, Azure.ResourceManager
```

### 1.2 Model Imports
#### ✅ CORRECT: Models namespace for data types
```csharp
using Azure.ResourceManager.ApiManagement.Models;

ApiManagementServiceSkuType skuType = ApiManagementServiceSkuType.Developer;
```

#### ❌ INCORRECT: Old/deprecated namespaces
```csharp
using Microsoft.Azure.Management.ApiManagement;  // Wrong - old SDK
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
#### ✅ CORRECT: Using ResourceIdentifier
```csharp
var subscriptionId = Environment.GetEnvironmentVariable("AZURE_SUBSCRIPTION_ID");
var subscription = armClient.GetSubscriptionResource(
    new ResourceIdentifier($"/subscriptions/{subscriptionId}"));
```

#### ❌ INCORRECT: Hardcoded subscription ID
```csharp
var subscription = armClient.GetSubscriptionResource(
    new ResourceIdentifier("/subscriptions/12345678-1234-1234-1234-123456789012"));
```

---

## 3. Core Operations

### 3.1 Create API Management Service
#### ✅ CORRECT: Full service configuration with SKU
```csharp
var resourceGroup = await subscription.GetResourceGroupAsync("my-resource-group");

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

#### ❌ INCORRECT: Missing required SKU properties
```csharp
var serviceData = new ApiManagementServiceData(AzureLocation.EastUS);
// Missing sku, publisherEmail, publisherName
```

### 3.2 Create an API
#### ✅ CORRECT: Using ApiCreateOrUpdateContent
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

#### ❌ INCORRECT: Missing Path property
```csharp
var apiData = new ApiCreateOrUpdateContent
{
    DisplayName = "My API"
    // Missing Path - required property
};
```

### 3.3 Create a Product
#### ✅ CORRECT: Product with subscription settings
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

#### ❌ INCORRECT: Missing State property
```csharp
var productData = new ApiManagementProductData
{
    DisplayName = "Starter"
    // Product will be in draft state without State = Published
};
```

### 3.4 Add API to Product
#### ✅ CORRECT: Using ProductApis collection
```csharp
await product.GetProductApis().CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-api");
```

#### ❌ INCORRECT: Trying to set on product directly
```csharp
productData.Apis.Add("my-api");  // Wrong approach
```

### 3.5 Create a Subscription
#### ✅ CORRECT: Subscription with scope
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

#### ❌ INCORRECT: Missing Scope
```csharp
var subscriptionData = new ApiManagementSubscriptionCreateOrUpdateContent
{
    DisplayName = "My Subscription"
    // Missing Scope - required for subscription
};
```

### 3.6 Get Subscription Keys
#### ✅ CORRECT: Using GetSecretsAsync
```csharp
var keys = await subscription.GetSecretsAsync();
Console.WriteLine($"Primary Key: {keys.Value.PrimaryKey}");
Console.WriteLine($"Secondary Key: {keys.Value.SecondaryKey}");
```

#### ❌ INCORRECT: Accessing keys directly
```csharp
var key = subscription.Data.PrimaryKey;  // Wrong - keys are secrets
```

---

## 4. Policy Management

### 4.1 Set API Policy
#### ✅ CORRECT: XML policy format
```csharp
var policyXml = @"
<policies>
    <inbound>
        <rate-limit calls=""100"" renewal-period=""60"" />
        <set-header name=""X-Custom-Header"" exists-action=""override"">
            <value>CustomValue</value>
        </set-header>
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

#### ❌ INCORRECT: Invalid policy structure
```csharp
var policyXml = @"<rate-limit calls=""100"" />";  // Missing policies wrapper
```

### 4.2 Policy Format Options
#### ✅ CORRECT: Specifying format explicitly
```csharp
// XML format
var policyData = new PolicyContractData
{
    Value = policyXml,
    Format = PolicyContentFormat.Xml
};

// XML with link
var policyData = new PolicyContractData
{
    Value = "https://raw.githubusercontent.com/.../policy.xml",
    Format = PolicyContentFormat.XmlLink
};

// Raw XML (no escaping)
var policyData = new PolicyContractData
{
    Value = rawPolicyXml,
    Format = PolicyContentFormat.RawXml
};
```

#### ❌ INCORRECT: Missing format specification
```csharp
var policyData = new PolicyContractData
{
    Value = policyXml
    // Missing Format - may default incorrectly
};
```

---

## 5. Resource Hierarchy Navigation

### 5.1 Correct Hierarchy
#### ✅ CORRECT: Following Service → API → Operation structure
```csharp
// Service level
ApiManagementServiceResource service = await resourceGroup.GetApiManagementServiceAsync("my-apim");

// API level
ApiResource api = await service.GetApiAsync("my-api");

// Operation level
ApiOperationResource operation = await api.GetApiOperationAsync("get-users");

// Policy at operation level
ApiOperationPolicyResource policy = await operation.GetApiOperationPolicyAsync();
```

#### ❌ INCORRECT: Skipping hierarchy levels
```csharp
var operation = await service.GetApiOperationAsync("get-users");  // Wrong
```

---

## 6. Backup and Restore

### 6.1 Backup Service
#### ✅ CORRECT: Using managed identity for storage access
```csharp
var backupParams = new ApiManagementServiceBackupRestoreContent(
    storageAccount: "mystorageaccount",
    containerName: "apim-backups",
    backupName: "backup-2024-01-15")
{
    AccessType = StorageAccountAccessType.SystemAssignedManagedIdentity
};

await service.BackupAsync(WaitUntil.Completed, backupParams);
```

#### ❌ INCORRECT: Using hardcoded access key
```csharp
var backupParams = new ApiManagementServiceBackupRestoreContent(
    storageAccount: "mystorageaccount",
    containerName: "apim-backups",
    backupName: "backup")
{
    AccessKey = "hardcoded-storage-key"  // Security risk
};
```

### 6.2 Restore Service
#### ✅ CORRECT: Restore from backup
```csharp
await service.RestoreAsync(WaitUntil.Completed, backupParams);
```

---

## 7. SKU Types

### 7.1 Valid SKU Configurations
#### ✅ CORRECT: Developer SKU for testing
```csharp
var sku = new ApiManagementServiceSkuProperties(
    ApiManagementServiceSkuType.Developer, 
    capacity: 1);
```

#### ✅ CORRECT: Premium SKU for production
```csharp
var sku = new ApiManagementServiceSkuProperties(
    ApiManagementServiceSkuType.Premium, 
    capacity: 2);
```

#### ❌ INCORRECT: Invalid capacity for SKU
```csharp
var sku = new ApiManagementServiceSkuProperties(
    ApiManagementServiceSkuType.Developer, 
    capacity: 5);  // Developer only supports capacity 1
```

---

## 8. Error Handling

### 8.1 RequestFailedException Handling
#### ✅ CORRECT: Pattern matching on status codes
```csharp
using Azure;

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

#### ❌ INCORRECT: Generic exception handling
```csharp
try
{
    await serviceCollection.CreateOrUpdateAsync(WaitUntil.Completed, serviceName, serviceData);
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);  // Loses Azure-specific error details
}
```

---

## 9. WaitUntil Best Practices

### 9.1 Long-Running Operations
#### ✅ CORRECT: Use WaitUntil.Started for service creation
```csharp
// Service creation can take 30+ minutes
var operation = await serviceCollection.CreateOrUpdateAsync(
    WaitUntil.Started,
    serviceName,
    serviceData);

// Poll for completion
while (!operation.HasCompleted)
{
    await operation.UpdateStatusAsync();
    await Task.Delay(TimeSpan.FromSeconds(30));
}
```

#### ✅ CORRECT: Use WaitUntil.Completed for quick operations
```csharp
// API creation is fast
var operation = await apiCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-api",
    apiData);
```

#### ❌ INCORRECT: Blocking indefinitely on service creation
```csharp
// May timeout or block for 30+ minutes
var operation = await serviceCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    serviceName,
    serviceData);
```

---

## 10. Enum Values

### 10.1 ApiManagementServiceSkuType Values
#### ✅ CORRECT: Valid SKU types
```csharp
ApiManagementServiceSkuType.Developer    // Development/testing
ApiManagementServiceSkuType.Basic        // Entry-level production
ApiManagementServiceSkuType.Standard     // Medium workloads
ApiManagementServiceSkuType.Premium      // High availability
ApiManagementServiceSkuType.Consumption  // Serverless
```

### 10.2 ApiManagementProductState Values
#### ✅ CORRECT: Valid product states
```csharp
ApiManagementProductState.NotPublished  // Draft state
ApiManagementProductState.Published     // Available to subscribers
```

### 10.3 ApiManagementSubscriptionState Values
#### ✅ CORRECT: Valid subscription states
```csharp
ApiManagementSubscriptionState.Active     // Can call APIs
ApiManagementSubscriptionState.Suspended  // Temporarily disabled
ApiManagementSubscriptionState.Cancelled  // Permanently cancelled
ApiManagementSubscriptionState.Submitted  // Pending approval
ApiManagementSubscriptionState.Rejected   // Approval rejected
```

---

## 11. Best Practices Checklist

- [ ] Use `DefaultAzureCredential` for authentication
- [ ] Use `async/await` for all operations
- [ ] Use `WaitUntil.Started` for service creation (30+ min)
- [ ] Use `WaitUntil.Completed` for quick operations (APIs, products)
- [ ] Navigate hierarchy correctly: Service → API → Operation → Policy
- [ ] Use `GetSecretsAsync` to retrieve subscription keys
- [ ] Include `<base />` tags in policy XML
- [ ] Handle `RequestFailedException` with status code matching
- [ ] Use managed identity for backup/restore storage access
- [ ] Specify `PolicyContentFormat` explicitly
