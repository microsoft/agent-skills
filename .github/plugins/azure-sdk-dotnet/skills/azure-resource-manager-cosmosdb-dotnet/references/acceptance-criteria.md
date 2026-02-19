# Azure.ResourceManager.CosmosDB (.NET) Acceptance Criteria

**SDK**: `Azure.ResourceManager.CosmosDB`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/cosmosdb/Azure.ResourceManager.CosmosDB
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. ArmClient Creation with DefaultAzureCredential

### ✅ CORRECT: DefaultAzureCredential with ArmClient
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.CosmosDB;

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

### ❌ INCORRECT: Missing using statements
```csharp
// WRONG - missing Azure.Identity and Azure.ResourceManager using statements
var armClient = new ArmClient(new DefaultAzureCredential());
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

// Access Cosmos DB accounts via collection
var accountCollection = resourceGroup.Value.GetCosmosDBAccounts();
```

### ❌ INCORRECT: Skipping Hierarchy
```csharp
// WRONG - cannot directly get accounts without resource group
var accounts = armClient.GetCosmosDBAccounts("my-resource-group");
```

---

## 3. Cosmos DB Account CRUD Operations

### ✅ CORRECT: Create Account with Locations
```csharp
using Azure.ResourceManager.CosmosDB;
using Azure.ResourceManager.CosmosDB.Models;

var accountData = new CosmosDBAccountCreateOrUpdateContent(
    location: AzureLocation.EastUS,
    locations: new[]
    {
        new CosmosDBAccountLocation
        {
            LocationName = AzureLocation.EastUS,
            FailoverPriority = 0,
            IsZoneRedundant = false
        }
    })
{
    Kind = CosmosDBAccountKind.GlobalDocumentDB,
    ConsistencyPolicy = new ConsistencyPolicy(DefaultConsistencyLevel.Session),
    EnableAutomaticFailover = true
};

var operation = await accountCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-cosmos-account",
    accountData);

CosmosDBAccountResource account = operation.Value;
```

### ✅ CORRECT: Get Existing Account
```csharp
var account = await resourceGroup.Value.GetCosmosDBAccountAsync("my-cosmos-account");
Console.WriteLine($"Account: {account.Value.Data.Name}");
Console.WriteLine($"Endpoint: {account.Value.Data.DocumentEndpoint}");
```

### ✅ CORRECT: Update Account
```csharp
var account = await resourceGroup.Value.GetCosmosDBAccountAsync("my-cosmos-account");

var patchData = new CosmosDBAccountPatch
{
    EnableAutomaticFailover = true,
    ConsistencyPolicy = new ConsistencyPolicy(DefaultConsistencyLevel.BoundedStaleness)
    {
        MaxStalenessPrefix = 100000,
        MaxIntervalInSeconds = 300
    }
};
patchData.Tags.Add("Environment", "Production");

var operation = await account.Value.UpdateAsync(WaitUntil.Completed, patchData);
```

### ✅ CORRECT: Delete Account
```csharp
var account = await resourceGroup.Value.GetCosmosDBAccountAsync("my-cosmos-account");
await account.Value.DeleteAsync(WaitUntil.Completed);
```

### ✅ CORRECT: List Accounts
```csharp
await foreach (var account in resourceGroup.Value.GetCosmosDBAccounts())
{
    Console.WriteLine($"Account: {account.Data.Name}");
    Console.WriteLine($"  Location: {account.Data.Location}");
    Console.WriteLine($"  Kind: {account.Data.Kind}");
}
```

### ❌ INCORRECT: Missing Required Locations
```csharp
// WRONG - locations is required in constructor
var accountData = new CosmosDBAccountCreateOrUpdateContent(
    location: AzureLocation.EastUS)
{
    Kind = CosmosDBAccountKind.GlobalDocumentDB
};
```

### ❌ INCORRECT: Wrong WaitUntil Usage
```csharp
// WRONG - using WaitUntil.Started when you need the result immediately
var operation = await accountCollection.CreateOrUpdateAsync(
    WaitUntil.Started,
    "my-cosmos-account",
    accountData);

// This will fail - operation might not be completed yet
var account = operation.Value;
```

---

## 4. SQL Database and Container Operations

### ✅ CORRECT: Create SQL Database
```csharp
var databaseData = new CosmosDBSqlDatabaseCreateOrUpdateContent(
    new CosmosDBSqlDatabaseResourceInfo("my-database"));

var databaseCollection = account.GetCosmosDBSqlDatabases();
var dbOperation = await databaseCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-database",
    databaseData);

CosmosDBSqlDatabaseResource database = dbOperation.Value;
```

### ✅ CORRECT: Create SQL Container with Partition Key
```csharp
var containerData = new CosmosDBSqlContainerCreateOrUpdateContent(
    new CosmosDBSqlContainerResourceInfo("my-container")
    {
        PartitionKey = new CosmosDBContainerPartitionKey
        {
            Paths = { "/partitionKey" },
            Kind = CosmosDBPartitionKind.Hash
        },
        IndexingPolicy = new CosmosDBIndexingPolicy
        {
            Automatic = true,
            IndexingMode = CosmosDBIndexingMode.Consistent
        },
        DefaultTtl = 86400
    });

var containerCollection = database.GetCosmosDBSqlContainers();
var containerOperation = await containerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-container",
    containerData);
```

### ❌ INCORRECT: Container Without Partition Key
```csharp
// WRONG - partition key is required for containers
var containerData = new CosmosDBSqlContainerCreateOrUpdateContent(
    new CosmosDBSqlContainerResourceInfo("my-container"));
```

---

## 5. Throughput Operations

### ✅ CORRECT: Set Manual Throughput
```csharp
var throughputData = new ThroughputSettingsUpdateData(
    new ThroughputSettingsResourceInfo
    {
        Throughput = 400
    });

await database.CreateOrUpdateCosmosDBSqlDatabaseThroughputAsync(
    WaitUntil.Completed,
    throughputData);
```

### ✅ CORRECT: Set Autoscale Throughput
```csharp
var autoscaleData = new ThroughputSettingsUpdateData(
    new ThroughputSettingsResourceInfo
    {
        AutoscaleSettings = new AutoscaleSettingsResourceInfo
        {
            MaxThroughput = 4000
        }
    });

await container.CreateOrUpdateCosmosDBSqlContainerThroughputAsync(
    WaitUntil.Completed,
    autoscaleData);
```

### ❌ INCORRECT: Both Manual and Autoscale
```csharp
// WRONG - cannot specify both Throughput and AutoscaleSettings
var throughputData = new ThroughputSettingsUpdateData(
    new ThroughputSettingsResourceInfo
    {
        Throughput = 400,
        AutoscaleSettings = new AutoscaleSettingsResourceInfo
        {
            MaxThroughput = 4000
        }
    });
```

---

## 6. Async Patterns

### ✅ CORRECT: Proper Async/Await
```csharp
public async Task<CosmosDBAccountResource> CreateAccountAsync(
    ResourceGroupResource resourceGroup,
    string accountName)
{
    var accountData = new CosmosDBAccountCreateOrUpdateContent(
        location: AzureLocation.EastUS,
        locations: new[] { new CosmosDBAccountLocation { LocationName = AzureLocation.EastUS, FailoverPriority = 0 } });

    var operation = await resourceGroup.GetCosmosDBAccounts().CreateOrUpdateAsync(
        WaitUntil.Completed,
        accountName,
        accountData);

    return operation.Value;
}
```

### ✅ CORRECT: Async Enumeration
```csharp
public async Task ListAccountsAsync(ResourceGroupResource resourceGroup)
{
    await foreach (var account in resourceGroup.GetCosmosDBAccounts())
    {
        Console.WriteLine($"Account: {account.Data.Name}");
    }
}
```

### ❌ INCORRECT: Blocking Async Code
```csharp
// WRONG - using .Result blocks the thread
var operation = accountCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, accountName, accountData).Result;

// WRONG - using .Wait() blocks the thread
accountCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, accountName, accountData).Wait();
```

---

## 7. Error Handling

### ✅ CORRECT: Catch RequestFailedException
```csharp
using Azure;

try
{
    var operation = await accountCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, accountName, accountData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Account already exists");
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
    var operation = await accountCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, accountName, accountData);
}
catch (Exception ex)
{
    Console.WriteLine($"Error: {ex.Message}");
}
```

### ❌ INCORRECT: Empty Catch Block
```csharp
// WRONG - swallowing exceptions silently
try
{
    var operation = await accountCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, accountName, accountData);
}
catch (RequestFailedException)
{
    // Silent failure - never do this
}
```

---

## 8. Connection Information

### ✅ CORRECT: Get Keys and Connection Strings
```csharp
// Get keys
var keys = await account.GetKeysAsync();
Console.WriteLine($"Primary Key: {keys.Value.PrimaryMasterKey}");
Console.WriteLine($"Secondary Key: {keys.Value.SecondaryMasterKey}");

// Get connection strings
var connectionStrings = await account.GetConnectionStringsAsync();
foreach (var cs in connectionStrings.Value.ConnectionStrings)
{
    Console.WriteLine($"{cs.Description}: {cs.ConnectionString}");
}

// Regenerate key
await account.RegenerateKeyAsync(
    WaitUntil.Completed,
    new CosmosDBAccountRegenerateKeyContent(CosmosDBAccountKeyKind.Primary));
```

### ❌ INCORRECT: Logging Keys
```csharp
// WRONG - never log secrets
var keys = await account.GetKeysAsync();
_logger.LogInformation($"Primary Key: {keys.Value.PrimaryMasterKey}");
```

---

## 9. Anti-Patterns to Avoid

### ❌ Using Data Plane SDK Types
```csharp
// WRONG - Microsoft.Azure.Cosmos is the data plane SDK
using Microsoft.Azure.Cosmos;

// Azure.ResourceManager.CosmosDB is for management plane only
// Use Microsoft.Azure.Cosmos for document CRUD operations
```

### ❌ Creating Client Per Request
```csharp
// WRONG - ArmClient should be reused
public async Task<CosmosDBAccountResource> GetAccount()
{
    var armClient = new ArmClient(new DefaultAzureCredential()); // Creates new client each time
    // ...
}
```

### ❌ Hardcoding Resource IDs
```csharp
// WRONG - hardcoding subscription/resource group IDs
var resourceId = new ResourceIdentifier(
    "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/my-rg/providers/Microsoft.DocumentDB/databaseAccounts/my-account");

// CORRECT - use CreateResourceIdentifier
var resourceId = CosmosDBAccountResource.CreateResourceIdentifier(
    subscriptionId, resourceGroupName, accountName);
```

---

## Summary Checklist

- [ ] Uses `DefaultAzureCredential` for authentication
- [ ] Uses proper `using` statements for namespaces
- [ ] Navigates resource hierarchy correctly (Subscription → ResourceGroup → Account)
- [ ] Uses `WaitUntil.Completed` when result is needed immediately
- [ ] Includes required parameters (e.g., locations for account, partition key for container)
- [ ] Uses async/await properly (no `.Result` or `.Wait()`)
- [ ] Catches `RequestFailedException` with specific status codes
- [ ] Never logs or hardcodes secrets
- [ ] Uses `CreateOrUpdateAsync` for idempotent operations
- [ ] Distinguishes between management plane (this SDK) and data plane (Microsoft.Azure.Cosmos)
