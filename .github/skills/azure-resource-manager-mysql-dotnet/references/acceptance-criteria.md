# Azure.ResourceManager.MySql (.NET) Acceptance Criteria

**SDK**: `Azure.ResourceManager.MySql`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/mysql/Azure.ResourceManager.MySql
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. ArmClient Creation with DefaultAzureCredential

### ✅ CORRECT: DefaultAzureCredential with ArmClient
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.MySql;
using Azure.ResourceManager.MySql.FlexibleServers;

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

// Access MySQL Flexible Servers via collection
var serverCollection = resourceGroup.Value.GetMySqlFlexibleServers();
```

### ❌ INCORRECT: Using Single Server (Deprecated)
```csharp
// WRONG - Single Server is deprecated, use Flexible Server
var servers = resourceGroup.Value.GetMySqlServers(); // Legacy API
```

---

## 3. MySQL Flexible Server CRUD Operations

### ✅ CORRECT: Create Flexible Server
```csharp
using Azure.ResourceManager.MySql.FlexibleServers;
using Azure.ResourceManager.MySql.FlexibleServers.Models;

var serverData = new MySqlFlexibleServerData(AzureLocation.EastUS)
{
    Sku = new MySqlFlexibleServerSku("Standard_D2ds_v4", MySqlFlexibleServerSkuTier.GeneralPurpose),
    AdministratorLogin = "mysqladmin",
    AdministratorLoginPassword = "YourSecurePassword123!",
    Version = MySqlFlexibleServerVersion.Ver8_0_21,
    Storage = new MySqlFlexibleServerStorage
    {
        StorageSizeInGB = 128,
        AutoGrow = MySqlFlexibleServerEnableStatusEnum.Enabled,
        Iops = 3000
    },
    Backup = new MySqlFlexibleServerBackupProperties
    {
        BackupRetentionDays = 7,
        GeoRedundantBackup = MySqlFlexibleServerEnableStatusEnum.Disabled
    },
    HighAvailability = new MySqlFlexibleServerHighAvailability
    {
        Mode = MySqlFlexibleServerHighAvailabilityMode.ZoneRedundant,
        StandbyAvailabilityZone = "2"
    },
    AvailabilityZone = "1"
};

var operation = await serverCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-mysql-server",
    serverData);

MySqlFlexibleServerResource server = operation.Value;
Console.WriteLine($"FQDN: {server.Data.FullyQualifiedDomainName}");
```

### ✅ CORRECT: Get Existing Server
```csharp
var server = await resourceGroup.Value.GetMySqlFlexibleServerAsync("my-mysql-server");
Console.WriteLine($"Server: {server.Value.Data.Name}");
Console.WriteLine($"FQDN: {server.Value.Data.FullyQualifiedDomainName}");
Console.WriteLine($"State: {server.Value.Data.State}");
```

### ✅ CORRECT: Update Server (Scale)
```csharp
var server = await resourceGroup.Value.GetMySqlFlexibleServerAsync("my-mysql-server");

var patch = new MySqlFlexibleServerPatch
{
    Sku = new MySqlFlexibleServerSku("Standard_D4ds_v4", MySqlFlexibleServerSkuTier.GeneralPurpose),
    Storage = new MySqlFlexibleServerStorage
    {
        StorageSizeInGB = 256,
        Iops = 6000
    }
};

var operation = await server.Value.UpdateAsync(WaitUntil.Completed, patch);
```

### ✅ CORRECT: Delete Server
```csharp
var server = await resourceGroup.Value.GetMySqlFlexibleServerAsync("my-mysql-server");
await server.Value.DeleteAsync(WaitUntil.Completed);
```

### ✅ CORRECT: List Servers
```csharp
await foreach (var server in resourceGroup.Value.GetMySqlFlexibleServers())
{
    Console.WriteLine($"Server: {server.Data.Name}");
    Console.WriteLine($"  FQDN: {server.Data.FullyQualifiedDomainName}");
    Console.WriteLine($"  Version: {server.Data.Version}");
    Console.WriteLine($"  SKU: {server.Data.Sku.Name}");
}
```

### ❌ INCORRECT: Missing Required Parameters
```csharp
// WRONG - missing SKU, administrator credentials
var serverData = new MySqlFlexibleServerData(AzureLocation.EastUS);

var operation = await serverCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-mysql-server",
    serverData);
```

### ❌ INCORRECT: Weak Password
```csharp
// WRONG - password doesn't meet complexity requirements
var serverData = new MySqlFlexibleServerData(AzureLocation.EastUS)
{
    AdministratorLogin = "admin",
    AdministratorLoginPassword = "password123"  // Too weak
};
```

---

## 4. Database Operations

### ✅ CORRECT: Create Database
```csharp
var databaseCollection = server.GetMySqlFlexibleServerDatabases();

var dbData = new MySqlFlexibleServerDatabaseData
{
    Charset = "utf8mb4",
    Collation = "utf8mb4_unicode_ci"
};

var operation = await databaseCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "myappdb",
    dbData);

MySqlFlexibleServerDatabaseResource database = operation.Value;
```

### ✅ CORRECT: List Databases
```csharp
await foreach (var db in server.GetMySqlFlexibleServerDatabases())
{
    Console.WriteLine($"Database: {db.Data.Name}");
    Console.WriteLine($"  Charset: {db.Data.Charset}");
    Console.WriteLine($"  Collation: {db.Data.Collation}");
}
```

---

## 5. Firewall Rules

### ✅ CORRECT: Create Firewall Rule
```csharp
var firewallRules = server.GetMySqlFlexibleServerFirewallRules();

var ruleData = new MySqlFlexibleServerFirewallRuleData
{
    StartIPAddress = System.Net.IPAddress.Parse("10.0.0.1"),
    EndIPAddress = System.Net.IPAddress.Parse("10.0.0.255")
};

var operation = await firewallRules.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "allow-internal",
    ruleData);
```

### ✅ CORRECT: Allow Azure Services
```csharp
var azureServicesRule = new MySqlFlexibleServerFirewallRuleData
{
    StartIPAddress = System.Net.IPAddress.Parse("0.0.0.0"),
    EndIPAddress = System.Net.IPAddress.Parse("0.0.0.0")
};

await firewallRules.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "AllowAllAzureServicesAndResourcesWithinAzureIps",
    azureServicesRule);
```

### ❌ INCORRECT: Invalid IP Range
```csharp
// WRONG - start IP greater than end IP
var ruleData = new MySqlFlexibleServerFirewallRuleData
{
    StartIPAddress = System.Net.IPAddress.Parse("10.0.0.255"),
    EndIPAddress = System.Net.IPAddress.Parse("10.0.0.1")
};
```

---

## 6. Server Configuration

### ✅ CORRECT: Update Configuration Parameter
```csharp
var configurations = server.GetMySqlFlexibleServerConfigurations();

var configData = new MySqlFlexibleServerConfigurationData
{
    Value = "500",
    Source = MySqlFlexibleServerConfigurationSource.UserOverride
};

var operation = await configurations.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "max_connections",
    configData);
```

### ✅ CORRECT: List Configurations
```csharp
await foreach (var config in server.GetMySqlFlexibleServerConfigurations())
{
    Console.WriteLine($"Parameter: {config.Data.Name}");
    Console.WriteLine($"  Value: {config.Data.Value}");
    Console.WriteLine($"  Source: {config.Data.Source}");
}
```

---

## 7. Entra ID Administrator

### ✅ CORRECT: Configure Entra ID Admin
```csharp
var admins = server.GetMySqlFlexibleServerAadAdministrators();

var adminData = new MySqlFlexibleServerAadAdministratorData
{
    AdministratorType = MySqlFlexibleServerAdministratorType.ActiveDirectory,
    Login = "aad-admin@contoso.com",
    Sid = Guid.Parse("<entra-object-id>"),
    TenantId = Guid.Parse("<tenant-id>"),
    IdentityResourceId = new ResourceIdentifier("/subscriptions/.../userAssignedIdentities/mysql-identity")
};

var operation = await admins.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "ActiveDirectory",
    adminData);
```

---

## 8. Backup and Restore

### ✅ CORRECT: Point-in-Time Restore
```csharp
var restoreData = new MySqlFlexibleServerData(AzureLocation.EastUS)
{
    CreateMode = MySqlFlexibleServerCreateMode.PointInTimeRestore,
    SourceServerResourceId = server.Id,
    RestorePointInTime = DateTimeOffset.UtcNow.AddHours(-2)
};

var operation = await serverCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-mysql-restored",
    restoreData);
```

### ✅ CORRECT: List Backups
```csharp
await foreach (var backup in server.GetMySqlFlexibleServerBackups())
{
    Console.WriteLine($"Backup: {backup.Data.Name}");
    Console.WriteLine($"  Type: {backup.Data.BackupType}");
    Console.WriteLine($"  Completed: {backup.Data.CompletedOn}");
}
```

---

## 9. Server Operations (Stop/Start/Restart)

### ✅ CORRECT: Stop Server
```csharp
await server.StopAsync(WaitUntil.Completed);
```

### ✅ CORRECT: Start Server
```csharp
await server.StartAsync(WaitUntil.Completed);
```

### ✅ CORRECT: Restart with Failover
```csharp
await server.RestartAsync(WaitUntil.Completed, new MySqlFlexibleServerRestartParameter
{
    RestartWithFailover = MySqlFlexibleServerEnableStatusEnum.Enabled,
    MaxFailoverSeconds = 60
});
```

---

## 10. Async Patterns

### ✅ CORRECT: Proper Async/Await
```csharp
public async Task<MySqlFlexibleServerResource> CreateServerAsync(
    ResourceGroupResource resourceGroup,
    string serverName)
{
    var serverData = new MySqlFlexibleServerData(AzureLocation.EastUS)
    {
        Sku = new MySqlFlexibleServerSku("Standard_D2ds_v4", MySqlFlexibleServerSkuTier.GeneralPurpose),
        AdministratorLogin = "mysqladmin",
        AdministratorLoginPassword = "YourSecurePassword123!",
        Version = MySqlFlexibleServerVersion.Ver8_0_21
    };

    var operation = await resourceGroup.GetMySqlFlexibleServers().CreateOrUpdateAsync(
        WaitUntil.Completed,
        serverName,
        serverData);

    return operation.Value;
}
```

### ❌ INCORRECT: Blocking Async Code
```csharp
// WRONG - using .Result blocks the thread
var operation = serverCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, serverName, serverData).Result;
```

---

## 11. Error Handling

### ✅ CORRECT: Catch RequestFailedException
```csharp
using Azure;

try
{
    var operation = await serverCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, serverName, serverData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Server already exists");
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

## 12. Anti-Patterns to Avoid

### ❌ Using Single Server APIs
```csharp
// WRONG - Single Server is deprecated
using Azure.ResourceManager.MySql;

var servers = resourceGroup.GetMySqlServers();
```

### ❌ Storing Passwords in Code
```csharp
// WRONG - passwords should come from secure configuration
var serverData = new MySqlFlexibleServerData(AzureLocation.EastUS)
{
    AdministratorLoginPassword = "HardcodedPassword123!"  // Never do this
};
```

### ❌ Creating Client Per Request
```csharp
// WRONG - ArmClient should be reused
public async Task<MySqlFlexibleServerResource> GetServer()
{
    var armClient = new ArmClient(new DefaultAzureCredential()); // Creates new client each time
    // ...
}
```

---

## Summary Checklist

- [ ] Uses `DefaultAzureCredential` for authentication
- [ ] Uses Flexible Server APIs (not deprecated Single Server)
- [ ] Uses proper `using` statements for namespaces
- [ ] Navigates resource hierarchy correctly (Subscription → ResourceGroup → Server)
- [ ] Uses `WaitUntil.Completed` when result is needed immediately
- [ ] Includes required SKU and administrator credentials
- [ ] Uses strong passwords meeting complexity requirements
- [ ] Configures appropriate charset/collation for databases
- [ ] Uses async/await properly (no `.Result` or `.Wait()`)
- [ ] Catches `RequestFailedException` with specific status codes
- [ ] Never hardcodes credentials or passwords
