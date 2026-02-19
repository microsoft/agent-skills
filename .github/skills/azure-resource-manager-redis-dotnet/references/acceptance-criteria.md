# Azure.ResourceManager.Redis (.NET) Acceptance Criteria

**SDK**: `Azure.ResourceManager.Redis`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/redis/Azure.ResourceManager.Redis
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. ArmClient Creation with DefaultAzureCredential

### ✅ CORRECT: DefaultAzureCredential with ArmClient
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.Redis;

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

// Access Redis caches via collection
var cacheCollection = resourceGroup.Value.GetAllRedis();
```

### ❌ INCORRECT: Skipping Hierarchy
```csharp
// WRONG - cannot directly get caches without resource group
var caches = armClient.GetAllRedis("my-resource-group");
```

---

## 3. Redis Cache CRUD Operations

### ✅ CORRECT: Create Standard Cache
```csharp
using Azure.ResourceManager.Redis;
using Azure.ResourceManager.Redis.Models;

var cacheData = new RedisCreateOrUpdateContent(
    location: AzureLocation.EastUS,
    sku: new RedisSku(RedisSkuName.Standard, RedisSkuFamily.BasicOrStandard, 1))
{
    EnableNonSslPort = false,
    MinimumTlsVersion = RedisTlsVersion.Tls1_2,
    RedisConfiguration = new RedisCommonConfiguration
    {
        MaxMemoryPolicy = "volatile-lru"
    },
    Tags =
    {
        ["environment"] = "production"
    }
};

var cacheCollection = resourceGroup.Value.GetAllRedis();
var operation = await cacheCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-redis-cache",
    cacheData);

RedisResource cache = operation.Value;
Console.WriteLine($"Host: {cache.Data.HostName}");
Console.WriteLine($"SSL Port: {cache.Data.SslPort}");
```

### ✅ CORRECT: Create Premium Cache with Clustering
```csharp
var premiumCacheData = new RedisCreateOrUpdateContent(
    location: AzureLocation.EastUS,
    sku: new RedisSku(RedisSkuName.Premium, RedisSkuFamily.Premium, 1))
{
    EnableNonSslPort = false,
    MinimumTlsVersion = RedisTlsVersion.Tls1_2,
    ShardCount = 2,  // Only for Premium
    RedisConfiguration = new RedisCommonConfiguration
    {
        MaxMemoryPolicy = "volatile-lru",
        IsRdbBackupEnabled = "true",
        RdbBackupFrequency = "60"
    }
};

var operation = await cacheCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-premium-redis",
    premiumCacheData);
```

### ✅ CORRECT: Get Existing Cache
```csharp
var cache = await resourceGroup.Value.GetRedisAsync("my-redis-cache");
Console.WriteLine($"Host: {cache.Value.Data.HostName}");
Console.WriteLine($"Port: {cache.Value.Data.Port}");
Console.WriteLine($"SSL Port: {cache.Value.Data.SslPort}");
Console.WriteLine($"Provisioning State: {cache.Value.Data.ProvisioningState}");
```

### ✅ CORRECT: Update Cache
```csharp
var patchData = new RedisPatch
{
    Sku = new RedisSku(RedisSkuName.Standard, RedisSkuFamily.BasicOrStandard, 2),
    RedisConfiguration = new RedisCommonConfiguration
    {
        MaxMemoryPolicy = "allkeys-lru"
    }
};

var updateOperation = await cache.Value.UpdateAsync(
    WaitUntil.Completed,
    patchData);
```

### ✅ CORRECT: Delete Cache
```csharp
await cache.Value.DeleteAsync(WaitUntil.Completed);
```

### ✅ CORRECT: List Caches
```csharp
await foreach (var redis in resourceGroup.Value.GetAllRedis())
{
    Console.WriteLine($"Cache: {redis.Data.Name}");
    Console.WriteLine($"  Host: {redis.Data.HostName}");
    Console.WriteLine($"  SKU: {redis.Data.Sku.Name} {redis.Data.Sku.Family} C{redis.Data.Sku.Capacity}");
    Console.WriteLine($"  State: {redis.Data.ProvisioningState}");
}
```

### ❌ INCORRECT: Missing Required SKU
```csharp
// WRONG - SKU is required
var cacheData = new RedisCreateOrUpdateContent(
    location: AzureLocation.EastUS);

var operation = await cacheCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-cache", cacheData);
```

### ❌ INCORRECT: Enabling Non-SSL Port
```csharp
// WRONG - non-SSL port should be disabled for security
var cacheData = new RedisCreateOrUpdateContent(
    location: AzureLocation.EastUS,
    sku: new RedisSku(RedisSkuName.Standard, RedisSkuFamily.BasicOrStandard, 1))
{
    EnableNonSslPort = true  // Security risk
};
```

### ❌ INCORRECT: Using TLS 1.0/1.1
```csharp
// WRONG - always use TLS 1.2 minimum
var cacheData = new RedisCreateOrUpdateContent(
    location: AzureLocation.EastUS,
    sku: new RedisSku(RedisSkuName.Standard, RedisSkuFamily.BasicOrStandard, 1))
{
    MinimumTlsVersion = RedisTlsVersion.Tls1_0  // Deprecated, insecure
};
```

---

## 4. Access Keys Operations

### ✅ CORRECT: Get Access Keys
```csharp
var keys = await cache.Value.GetKeysAsync();
Console.WriteLine($"Primary Key: {keys.Value.PrimaryKey}");
Console.WriteLine($"Secondary Key: {keys.Value.SecondaryKey}");
```

### ✅ CORRECT: Regenerate Keys
```csharp
var regenerateContent = new RedisRegenerateKeyContent(RedisRegenerateKeyType.Primary);
var newKeys = await cache.Value.RegenerateKeyAsync(regenerateContent);
Console.WriteLine($"New Primary Key: {newKeys.Value.PrimaryKey}");
```

### ❌ INCORRECT: Logging Keys
```csharp
// WRONG - never log secrets
var keys = await cache.Value.GetKeysAsync();
_logger.LogInformation($"Redis Key: {keys.Value.PrimaryKey}");
```

---

## 5. Firewall Rules

### ✅ CORRECT: Create Firewall Rule
```csharp
var firewallData = new RedisFirewallRuleData(
    startIP: System.Net.IPAddress.Parse("10.0.0.1"),
    endIP: System.Net.IPAddress.Parse("10.0.0.255"));

var firewallCollection = cache.Value.GetRedisFirewallRules();
var firewallOperation = await firewallCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "allow-internal-network",
    firewallData);
```

### ✅ CORRECT: List Firewall Rules
```csharp
await foreach (var rule in cache.Value.GetRedisFirewallRules())
{
    Console.WriteLine($"Rule: {rule.Data.Name} ({rule.Data.StartIP} - {rule.Data.EndIP})");
}
```

### ✅ CORRECT: Delete Firewall Rule
```csharp
var ruleToDelete = await firewallCollection.GetAsync("allow-internal-network");
await ruleToDelete.Value.DeleteAsync(WaitUntil.Completed);
```

---

## 6. Patch Schedule (Premium Only)

### ✅ CORRECT: Configure Patch Schedule
```csharp
var scheduleData = new RedisPatchScheduleData(
    new[]
    {
        new RedisPatchScheduleSetting(RedisDayOfWeek.Saturday, 2) // 2 AM Saturday
        {
            MaintenanceWindow = TimeSpan.FromHours(5)
        },
        new RedisPatchScheduleSetting(RedisDayOfWeek.Sunday, 2) // 2 AM Sunday
        {
            MaintenanceWindow = TimeSpan.FromHours(5)
        }
    });

var scheduleCollection = cache.Value.GetRedisPatchSchedules();
await scheduleCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    RedisPatchScheduleDefaultName.Default,
    scheduleData);
```

### ❌ INCORRECT: Patch Schedule on Non-Premium
```csharp
// WRONG - patch schedules require Premium SKU
// This will fail on Basic/Standard caches
var scheduleCollection = basicCache.GetRedisPatchSchedules();
await scheduleCollection.CreateOrUpdateAsync(...);
```

---

## 7. Import/Export Data (Premium Only)

### ✅ CORRECT: Import Data
```csharp
var importContent = new ImportRdbContent(
    files: new[] { "https://mystorageaccount.blob.core.windows.net/container/dump.rdb" },
    format: "RDB");

await cache.Value.ImportDataAsync(WaitUntil.Completed, importContent);
```

### ✅ CORRECT: Export Data
```csharp
var exportContent = new ExportRdbContent(
    prefix: "backup",
    container: "https://mystorageaccount.blob.core.windows.net/container?sastoken",
    format: "RDB");

await cache.Value.ExportDataAsync(WaitUntil.Completed, exportContent);
```

---

## 8. Force Reboot

### ✅ CORRECT: Reboot Cache
```csharp
var rebootContent = new RedisRebootContent
{
    RebootType = RedisRebootType.AllNodes,
    ShardId = 0 // For clustered caches
};

await cache.Value.ForceRebootAsync(rebootContent);
```

---

## 9. Async Patterns

### ✅ CORRECT: Proper Async/Await
```csharp
public async Task<RedisResource> CreateCacheAsync(
    ResourceGroupResource resourceGroup,
    string cacheName)
{
    var cacheData = new RedisCreateOrUpdateContent(
        location: AzureLocation.EastUS,
        sku: new RedisSku(RedisSkuName.Standard, RedisSkuFamily.BasicOrStandard, 1))
    {
        EnableNonSslPort = false,
        MinimumTlsVersion = RedisTlsVersion.Tls1_2
    };

    var operation = await resourceGroup.GetAllRedis().CreateOrUpdateAsync(
        WaitUntil.Completed,
        cacheName,
        cacheData);

    return operation.Value;
}
```

### ❌ INCORRECT: Blocking Async Code
```csharp
// WRONG - using .Result blocks the thread
var operation = cacheCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, cacheName, cacheData).Result;
```

---

## 10. Error Handling

### ✅ CORRECT: Catch RequestFailedException
```csharp
using Azure;

try
{
    var operation = await cacheCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, cacheName, cacheData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Cache already exists");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid configuration: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

---

## 11. Connecting with StackExchange.Redis

### ✅ CORRECT: Build Connection String from Management SDK
```csharp
using StackExchange.Redis;

// Get connection info from management SDK
var cache = await resourceGroup.Value.GetRedisAsync("my-redis-cache");
var keys = await cache.Value.GetKeysAsync();

// Connect with StackExchange.Redis
var connectionString = $"{cache.Value.Data.HostName}:{cache.Value.Data.SslPort}," +
    $"password={keys.Value.PrimaryKey}," +
    "ssl=True," +
    "abortConnect=False";
    
var connection = ConnectionMultiplexer.Connect(connectionString);
var db = connection.GetDatabase();

// Data operations
await db.StringSetAsync("key", "value");
var value = await db.StringGetAsync("key");
```

### ❌ INCORRECT: Connection Without SSL
```csharp
// WRONG - always use SSL
var connectionString = $"{cache.Value.Data.HostName}:{cache.Value.Data.Port}," +
    $"password={keys.Value.PrimaryKey}";
// Missing ssl=True
```

---

## 12. SKU Reference

### SKU Tiers and Capacities
```csharp
// Basic - single node, no SLA, dev/test only
new RedisSku(RedisSkuName.Basic, RedisSkuFamily.BasicOrStandard, capacity: 0); // 250 MB
new RedisSku(RedisSkuName.Basic, RedisSkuFamily.BasicOrStandard, capacity: 1); // 1 GB
new RedisSku(RedisSkuName.Basic, RedisSkuFamily.BasicOrStandard, capacity: 6); // 53 GB

// Standard - two nodes (primary/replica), SLA
new RedisSku(RedisSkuName.Standard, RedisSkuFamily.BasicOrStandard, capacity: 1); // 1 GB
new RedisSku(RedisSkuName.Standard, RedisSkuFamily.BasicOrStandard, capacity: 6); // 53 GB

// Premium - clustering, geo-replication, VNet, persistence
new RedisSku(RedisSkuName.Premium, RedisSkuFamily.Premium, capacity: 1); // 6 GB/shard
new RedisSku(RedisSkuName.Premium, RedisSkuFamily.Premium, capacity: 5); // 120 GB/shard
```

### ❌ INCORRECT: SKU Downgrade
```csharp
// WRONG - cannot downgrade from Premium to Standard/Basic
// This will fail at runtime
var patchData = new RedisPatch
{
    Sku = new RedisSku(RedisSkuName.Standard, RedisSkuFamily.BasicOrStandard, 1)
};
await premiumCache.UpdateAsync(WaitUntil.Completed, patchData);
```

---

## 13. Anti-Patterns to Avoid

### ❌ Using Data Plane SDK for Management
```csharp
// WRONG - StackExchange.Redis is the data plane SDK
// Use Azure.ResourceManager.Redis for management operations
using StackExchange.Redis;

// Cannot create/delete caches with StackExchange.Redis
```

### ❌ Creating Client Per Request
```csharp
// WRONG - ArmClient should be reused
public async Task<RedisResource> GetCache()
{
    var armClient = new ArmClient(new DefaultAzureCredential()); // Creates new client each time
    // ...
}
```

### ❌ Ignoring Long Provisioning Times
```csharp
// WRONG - cache creation takes 15-20 minutes
var operation = await cacheCollection.CreateOrUpdateAsync(
    WaitUntil.Started,  // Returns immediately
    cacheName,
    cacheData);

// Immediately trying to use cache
var keys = await operation.Value.GetKeysAsync(); // May fail - not ready yet
```

---

## Summary Checklist

- [ ] Uses `DefaultAzureCredential` for authentication
- [ ] Uses proper `using` statements for namespaces
- [ ] Navigates resource hierarchy correctly (Subscription → ResourceGroup → Cache)
- [ ] Uses `WaitUntil.Completed` when result is needed immediately
- [ ] Includes required SKU configuration
- [ ] Disables non-SSL port (`EnableNonSslPort = false`)
- [ ] Sets minimum TLS version to 1.2
- [ ] Uses async/await properly (no `.Result` or `.Wait()`)
- [ ] Catches `RequestFailedException` with specific status codes
- [ ] Never logs access keys
- [ ] Uses SSL connection strings for StackExchange.Redis
- [ ] Understands SKU limitations (Premium-only features)
- [ ] Distinguishes between management plane (this SDK) and data plane (StackExchange.Redis)
