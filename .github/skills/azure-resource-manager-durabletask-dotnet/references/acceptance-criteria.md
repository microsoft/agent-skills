# Azure.ResourceManager.DurableTask (.NET) Acceptance Criteria

**SDK**: `Azure.ResourceManager.DurableTask`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/durabletask/Azure.ResourceManager.DurableTask
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. ArmClient Creation with DefaultAzureCredential

### ✅ CORRECT: DefaultAzureCredential with ArmClient
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.DurableTask;

var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);

var subscriptionId = Environment.GetEnvironmentVariable("AZURE_SUBSCRIPTION_ID");
var subscription = armClient.GetSubscriptionResource(
    new ResourceIdentifier($"/subscriptions/{subscriptionId}"));
```

### ❌ INCORRECT: Hardcoded Credentials
```csharp
// WRONG - never hardcode credentials
var credential = new ClientSecretCredential(
    "tenant-id",
    "client-id", 
    "hardcoded-secret");
var armClient = new ArmClient(credential);
```

---

## 2. Resource Group Operations

### ✅ CORRECT: Navigate Resource Hierarchy
```csharp
// Get subscription first
var subscription = armClient.GetSubscriptionResource(
    new ResourceIdentifier($"/subscriptions/{subscriptionId}"));

// Then get resource group
var resourceGroup = await subscription.GetResourceGroupAsync("my-resource-group");

// Access schedulers via collection
var schedulerCollection = resourceGroup.Value.GetDurableTaskSchedulers();
```

### ❌ INCORRECT: Skipping Hierarchy
```csharp
// WRONG - cannot directly get schedulers without resource group
var schedulers = armClient.GetDurableTaskSchedulers("my-resource-group");
```

---

## 3. Scheduler CRUD Operations

### ✅ CORRECT: Create Scheduler with Dedicated SKU
```csharp
using Azure.ResourceManager.DurableTask;
using Azure.ResourceManager.DurableTask.Models;

var schedulerData = new DurableTaskSchedulerData(AzureLocation.EastUS)
{
    Properties = new DurableTaskSchedulerProperties
    {
        Sku = new DurableTaskSchedulerSku(DurableTaskSchedulerSkuName.Dedicated)
        {
            Capacity = 1
        },
        IPAllowlist = { "10.0.0.0/24" }
    }
};

var schedulerCollection = resourceGroup.Value.GetDurableTaskSchedulers();
var operation = await schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-scheduler",
    schedulerData);

DurableTaskSchedulerResource scheduler = operation.Value;
Console.WriteLine($"Endpoint: {scheduler.Data.Properties.Endpoint}");
```

### ✅ CORRECT: Create Scheduler with Consumption SKU
```csharp
var schedulerData = new DurableTaskSchedulerData(AzureLocation.EastUS)
{
    Properties = new DurableTaskSchedulerProperties
    {
        Sku = new DurableTaskSchedulerSku(DurableTaskSchedulerSkuName.Consumption)
    }
};

var operation = await schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-serverless-scheduler",
    schedulerData);
```

### ✅ CORRECT: Get Existing Scheduler
```csharp
var scheduler = await schedulerCollection.GetAsync("my-scheduler");
Console.WriteLine($"Scheduler: {scheduler.Value.Data.Name}");
Console.WriteLine($"SKU: {scheduler.Value.Data.Properties.Sku?.Name}");
```

### ✅ CORRECT: Update Scheduler
```csharp
var scheduler = await schedulerCollection.GetAsync("my-scheduler");

var updateData = new DurableTaskSchedulerData(scheduler.Value.Data.Location)
{
    Properties = new DurableTaskSchedulerProperties
    {
        Sku = new DurableTaskSchedulerSku(DurableTaskSchedulerSkuName.Dedicated)
        {
            Capacity = 2  // Scale up
        },
        IPAllowlist = { "10.0.0.0/16" }
    }
};

var updateOperation = await schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-scheduler",
    updateData);
```

### ✅ CORRECT: Delete Scheduler
```csharp
var scheduler = await schedulerCollection.GetAsync("my-scheduler");
await scheduler.Value.DeleteAsync(WaitUntil.Completed);
```

### ✅ CORRECT: List Schedulers
```csharp
// List in subscription
await foreach (var scheduler in subscription.GetDurableTaskSchedulersAsync())
{
    Console.WriteLine($"Scheduler: {scheduler.Data.Name}");
    Console.WriteLine($"  Endpoint: {scheduler.Data.Properties.Endpoint}");
}

// List in resource group
await foreach (var scheduler in schedulerCollection.GetAllAsync())
{
    Console.WriteLine($"Scheduler: {scheduler.Data.Name}");
}
```

### ❌ INCORRECT: Missing SKU Configuration
```csharp
// WRONG - SKU is required for scheduler creation
var schedulerData = new DurableTaskSchedulerData(AzureLocation.EastUS);

var operation = await schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-scheduler",
    schedulerData);
```

### ❌ INCORRECT: Capacity on Consumption SKU
```csharp
// WRONG - Consumption SKU does not support capacity setting
var schedulerData = new DurableTaskSchedulerData(AzureLocation.EastUS)
{
    Properties = new DurableTaskSchedulerProperties
    {
        Sku = new DurableTaskSchedulerSku(DurableTaskSchedulerSkuName.Consumption)
        {
            Capacity = 2  // Not applicable for Consumption
        }
    }
};
```

---

## 4. Task Hub Operations

### ✅ CORRECT: Create Task Hub
```csharp
var taskHubData = new DurableTaskHubData();

var taskHubCollection = scheduler.GetDurableTaskHubs();
var hubOperation = await taskHubCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-taskhub",
    taskHubData);

DurableTaskHubResource taskHub = hubOperation.Value;
Console.WriteLine($"Task Hub: {taskHub.Data.Name}");
```

### ✅ CORRECT: List Task Hubs
```csharp
await foreach (var hub in scheduler.GetDurableTaskHubs())
{
    Console.WriteLine($"Task Hub: {hub.Data.Name}");
}
```

### ✅ CORRECT: Delete Task Hub Before Scheduler
```csharp
// Must delete task hubs before scheduler
var taskHub = await scheduler.GetDurableTaskHubs().GetAsync("my-taskhub");
await taskHub.Value.DeleteAsync(WaitUntil.Completed);

// Now delete scheduler
await scheduler.DeleteAsync(WaitUntil.Completed);
```

### ❌ INCORRECT: Delete Scheduler with Task Hubs
```csharp
// WRONG - will fail if scheduler has task hubs
var scheduler = await schedulerCollection.GetAsync("my-scheduler");
await scheduler.Value.DeleteAsync(WaitUntil.Completed);
// Error: Cannot delete scheduler with existing task hubs
```

---

## 5. Retention Policy Operations

### ✅ CORRECT: Create Retention Policy
```csharp
var retentionPolicies = scheduler.GetDurableTaskRetentionPolicies();

var retentionData = new DurableTaskRetentionPolicyData
{
    Properties = new DurableTaskRetentionPolicyProperties()
};

var retentionOperation = await retentionPolicies.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "default",
    retentionData);
```

---

## 6. Async Patterns

### ✅ CORRECT: Proper Async/Await
```csharp
public async Task<DurableTaskSchedulerResource> CreateSchedulerAsync(
    ResourceGroupResource resourceGroup,
    string schedulerName)
{
    var schedulerData = new DurableTaskSchedulerData(AzureLocation.EastUS)
    {
        Properties = new DurableTaskSchedulerProperties
        {
            Sku = new DurableTaskSchedulerSku(DurableTaskSchedulerSkuName.Dedicated)
            {
                Capacity = 1
            }
        }
    };

    var operation = await resourceGroup.GetDurableTaskSchedulers().CreateOrUpdateAsync(
        WaitUntil.Completed,
        schedulerName,
        schedulerData);

    return operation.Value;
}
```

### ✅ CORRECT: Async Enumeration
```csharp
public async Task ListSchedulersAsync(SubscriptionResource subscription)
{
    await foreach (var scheduler in subscription.GetDurableTaskSchedulersAsync())
    {
        Console.WriteLine($"Scheduler: {scheduler.Data.Name}");
    }
}
```

### ❌ INCORRECT: Blocking Async Code
```csharp
// WRONG - using .Result blocks the thread
var operation = schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, schedulerName, schedulerData).Result;

// WRONG - using .Wait() blocks the thread
schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, schedulerName, schedulerData).Wait();
```

---

## 7. Error Handling

### ✅ CORRECT: Catch RequestFailedException
```csharp
using Azure;

try
{
    var operation = await schedulerCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, schedulerName, schedulerData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Scheduler already exists");
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Resource group not found");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

### ❌ INCORRECT: Generic Exception Only
```csharp
// WRONG - too generic, loses ARM-specific error details
try
{
    var operation = await schedulerCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, schedulerName, schedulerData);
}
catch (Exception ex)
{
    Console.WriteLine($"Error: {ex.Message}");
}
```

---

## 8. Resource Identifier Patterns

### ✅ CORRECT: Use CreateResourceIdentifier
```csharp
var schedulerResource = armClient.GetDurableTaskSchedulerResource(
    DurableTaskSchedulerResource.CreateResourceIdentifier(
        subscriptionId,
        "my-resource-group",
        "my-scheduler"));
var scheduler = await schedulerResource.GetAsync();
```

### ❌ INCORRECT: Hardcoding Resource IDs
```csharp
// WRONG - hardcoding resource IDs is error-prone
var resourceId = new ResourceIdentifier(
    "/subscriptions/12345678/resourceGroups/my-rg/providers/Microsoft.DurableTask/schedulers/my-scheduler");
```

---

## 9. Anti-Patterns to Avoid

### ❌ Using Data Plane SDK Types
```csharp
// WRONG - Microsoft.DurableTask.Client is the data plane SDK
using Microsoft.DurableTask.Client;

// Azure.ResourceManager.DurableTask is for management plane only
// Use Microsoft.DurableTask.Client.AzureManaged for orchestration operations
```

### ❌ Creating Client Per Request
```csharp
// WRONG - ArmClient should be reused
public async Task<DurableTaskSchedulerResource> GetScheduler()
{
    var armClient = new ArmClient(new DefaultAzureCredential()); // Creates new client each time
    // ...
}
```

### ❌ Ignoring Long-Running Operations
```csharp
// WRONG - scheduler creation takes time
var operation = await schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Started,
    schedulerName,
    schedulerData);

// Immediately using the scheduler without waiting
var taskHub = await operation.Value.GetDurableTaskHubs().CreateOrUpdateAsync(...);
// May fail - scheduler provisioning not complete
```

---

## Summary Checklist

- [ ] Uses `DefaultAzureCredential` for authentication
- [ ] Uses proper `using` statements for namespaces
- [ ] Navigates resource hierarchy correctly (Subscription → ResourceGroup → Scheduler → TaskHub)
- [ ] Uses `WaitUntil.Completed` when result is needed immediately
- [ ] Includes required SKU configuration for scheduler creation
- [ ] Uses correct SKU type (Dedicated with Capacity, Consumption without)
- [ ] Deletes task hubs before scheduler deletion
- [ ] Uses async/await properly (no `.Result` or `.Wait()`)
- [ ] Catches `RequestFailedException` with specific status codes
- [ ] Uses `CreateResourceIdentifier` instead of hardcoded IDs
- [ ] Distinguishes between management plane (this SDK) and data plane (Microsoft.DurableTask.Client)
