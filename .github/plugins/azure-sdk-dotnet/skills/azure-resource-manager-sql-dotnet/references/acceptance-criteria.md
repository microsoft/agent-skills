# Azure.ResourceManager.Sql (.NET) Acceptance Criteria

**SDK**: `Azure.ResourceManager.Sql`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/sqlmanagement/Azure.ResourceManager.Sql
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. ArmClient Creation with DefaultAzureCredential

### ✅ CORRECT: DefaultAzureCredential with ArmClient
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.Sql;

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

// Access SQL servers via collection
var serverCollection = resourceGroup.Value.GetSqlServers();
```

### ❌ INCORRECT: Skipping Hierarchy
```csharp
// WRONG - cannot directly get servers without resource group
var servers = armClient.GetSqlServers("my-resource-group");
```

---

## 3. SQL Server CRUD Operations

### ✅ CORRECT: Create Server with Azure AD Authentication
```csharp
using Azure.ResourceManager.Sql;
using Azure.ResourceManager.Sql.Models;

var serverData = new SqlServerData(AzureLocation.EastUS)
{
    AdministratorLogin = "sqladmin",
    AdministratorLoginPassword = "YourSecurePassword123!",
    Administrators = new ServerExternalAdministrator
    {
        AdministratorType = SqlAdministratorType.ActiveDirectory,
        Login = "admin@contoso.com",
        Sid = Guid.Parse("<azure-ad-user-object-id>"),
        TenantId = Guid.Parse("<azure-ad-tenant-id>"),
        AzureADOnlyAuthentication = false
    },
    Version = "12.0",
    MinimalTlsVersion = SqlMinimalTlsVersion.Tls1_2
};

var operation = await serverCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-sql-server",
    serverData);

SqlServerResource server = operation.Value;
Console.WriteLine($"FQDN: {server.Data.FullyQualifiedDomainName}");
```

### ✅ CORRECT: Get Existing Server
```csharp
var server = await serverCollection.GetAsync("my-sql-server");
Console.WriteLine($"Server: {server.Value.Data.Name}");
Console.WriteLine($"FQDN: {server.Value.Data.FullyQualifiedDomainName}");
Console.WriteLine($"State: {server.Value.Data.State}");
```

### ✅ CORRECT: Delete Server
```csharp
var server = await serverCollection.GetAsync("my-sql-server");
await server.Value.DeleteAsync(WaitUntil.Completed);
```

### ✅ CORRECT: List Servers
```csharp
await foreach (var server in resourceGroup.Value.GetSqlServers())
{
    Console.WriteLine($"Server: {server.Data.Name}");
    Console.WriteLine($"  FQDN: {server.Data.FullyQualifiedDomainName}");
    Console.WriteLine($"  Version: {server.Data.Version}");
}
```

### ❌ INCORRECT: Missing Administrator Credentials
```csharp
// WRONG - administrator login and password required
var serverData = new SqlServerData(AzureLocation.EastUS);

var operation = await serverCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-sql-server", serverData);
```

### ❌ INCORRECT: Weak TLS Version
```csharp
// WRONG - always use TLS 1.2 minimum
var serverData = new SqlServerData(AzureLocation.EastUS)
{
    MinimalTlsVersion = SqlMinimalTlsVersion.Tls1_0  // Insecure
};
```

---

## 4. SQL Database Operations

### ✅ CORRECT: Create Database
```csharp
var databaseData = new SqlDatabaseData(AzureLocation.EastUS)
{
    Sku = new SqlSku("GP_S_Gen5_2") // General Purpose, Serverless, Gen5, 2 vCores
    {
        Tier = "GeneralPurpose"
    },
    MaxSizeBytes = 34359738368, // 32 GB
    AutoPauseDelay = 60,  // Minutes
    MinCapacity = 0.5     // Minimum vCores
};

var databaseCollection = server.GetSqlDatabases();
var operation = await databaseCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-database",
    databaseData);

SqlDatabaseResource database = operation.Value;
```

### ✅ CORRECT: Create DTU-Based Database
```csharp
var databaseData = new SqlDatabaseData(AzureLocation.EastUS)
{
    Sku = new SqlSku("S1") // Standard tier, S1
    {
        Tier = "Standard"
    }
};

var operation = await databaseCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-dtu-database",
    databaseData);
```

### ✅ CORRECT: List Databases
```csharp
await foreach (var db in server.GetSqlDatabases())
{
    Console.WriteLine($"Database: {db.Data.Name}");
    Console.WriteLine($"  SKU: {db.Data.Sku?.Name}");
    Console.WriteLine($"  Status: {db.Data.Status}");
    Console.WriteLine($"  Size: {db.Data.MaxSizeBytes} bytes");
}
```

### ✅ CORRECT: Delete Database
```csharp
var database = await databaseCollection.GetAsync("my-database");
await database.Value.DeleteAsync(WaitUntil.Completed);
```

---

## 5. Elastic Pool Operations

### ✅ CORRECT: Create Elastic Pool
```csharp
var poolData = new ElasticPoolData(AzureLocation.EastUS)
{
    Sku = new SqlSku("GP_Gen5")
    {
        Tier = "GeneralPurpose",
        Family = "Gen5",
        Capacity = 2  // vCores
    },
    PerDatabaseSettings = new ElasticPoolPerDatabaseSettings
    {
        MinCapacity = 0,
        MaxCapacity = 2
    }
};

var poolCollection = server.GetElasticPools();
var operation = await poolCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-elastic-pool",
    poolData);

ElasticPoolResource pool = operation.Value;
```

### ✅ CORRECT: Add Database to Elastic Pool
```csharp
var databaseData = new SqlDatabaseData(AzureLocation.EastUS)
{
    ElasticPoolId = pool.Id
};

var operation = await databaseCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "pooled-database",
    databaseData);
```

### ✅ CORRECT: List Elastic Pools
```csharp
await foreach (var pool in server.GetElasticPools())
{
    Console.WriteLine($"Pool: {pool.Data.Name}");
    Console.WriteLine($"  SKU: {pool.Data.Sku?.Name}");
    Console.WriteLine($"  State: {pool.Data.State}");
}
```

---

## 6. Firewall Rules

### ✅ CORRECT: Create Firewall Rule
```csharp
var firewallData = new SqlFirewallRuleData
{
    StartIPAddress = "10.0.0.1",
    EndIPAddress = "10.0.0.255"
};

var firewallCollection = server.GetSqlFirewallRules();
var operation = await firewallCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "allow-internal",
    firewallData);
```

### ✅ CORRECT: Allow Azure Services
```csharp
var azureServicesRule = new SqlFirewallRuleData
{
    StartIPAddress = "0.0.0.0",
    EndIPAddress = "0.0.0.0"
};

await firewallCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "AllowAllWindowsAzureIps",
    azureServicesRule);
```

### ✅ CORRECT: List Firewall Rules
```csharp
await foreach (var rule in server.GetSqlFirewallRules())
{
    Console.WriteLine($"Rule: {rule.Data.Name} ({rule.Data.StartIPAddress} - {rule.Data.EndIPAddress})");
}
```

---

## 7. Virtual Network Rules

### ✅ CORRECT: Create VNet Rule
```csharp
var vnetRuleData = new SqlServerVirtualNetworkRuleData
{
    VirtualNetworkSubnetId = new ResourceIdentifier(
        "/subscriptions/{sub}/resourceGroups/{rg}/providers/" +
        "Microsoft.Network/virtualNetworks/{vnet}/subnets/{subnet}"),
    IgnoreMissingVnetServiceEndpoint = false
};

var vnetRuleCollection = server.GetSqlServerVirtualNetworkRules();
await vnetRuleCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "allow-app-subnet",
    vnetRuleData);
```

---

## 8. Server Auditing

### ✅ CORRECT: Configure Blob Auditing
```csharp
var auditingData = new SqlServerBlobAuditingPolicyData
{
    State = BlobAuditingPolicyState.Enabled,
    StorageEndpoint = "https://mystorageaccount.blob.core.windows.net",
    StorageAccountAccessKey = "<storage-account-key>",
    RetentionDays = 90,
    IsStorageSecondaryKeyInUse = false,
    IsAzureMonitorTargetEnabled = true
};

var auditingPolicy = server.GetSqlServerBlobAuditingPolicy();
await auditingPolicy.CreateOrUpdateAsync(WaitUntil.Completed, auditingData);
```

---

## 9. Transparent Data Encryption

### ✅ CORRECT: Enable TDE with Customer-Managed Key
```csharp
var protectorData = new EncryptionProtectorData
{
    ServerKeyType = SqlServerKeyType.AzureKeyVault,
    ServerKeyName = "mykeyvault_mykey_abc123",
    AutoRotationEnabled = true
};

var protector = server.GetEncryptionProtector();
await protector.CreateOrUpdateAsync(WaitUntil.Completed, protectorData);
```

---

## 10. Check Name Availability

### ✅ CORRECT: Check Server Name
```csharp
var checkRequest = new SqlNameAvailabilityContent
{
    Name = "proposed-server-name",
    ResourceType = "Microsoft.Sql/servers"
};

var result = await subscription.CheckSqlNameAvailabilityAsync(checkRequest);

if (result.Value.IsAvailable == true)
{
    Console.WriteLine("Name is available");
}
else
{
    Console.WriteLine($"Name unavailable: {result.Value.Reason}");
}
```

---

## 11. Async Patterns

### ✅ CORRECT: Proper Async/Await
```csharp
public async Task<SqlServerResource> CreateServerAsync(
    ResourceGroupResource resourceGroup,
    string serverName)
{
    var serverData = new SqlServerData(AzureLocation.EastUS)
    {
        AdministratorLogin = "sqladmin",
        AdministratorLoginPassword = "YourSecurePassword123!",
        Version = "12.0",
        MinimalTlsVersion = SqlMinimalTlsVersion.Tls1_2
    };

    var operation = await resourceGroup.GetSqlServers().CreateOrUpdateAsync(
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

## 12. Error Handling

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

## 13. Connection String

### ✅ CORRECT: Build Connection String
```csharp
// ADO.NET connection string
string connectionString = $"Server=tcp:{server.Data.FullyQualifiedDomainName},1433;" +
    "Initial Catalog=my-database;" +
    "Persist Security Info=False;" +
    "User ID=sqladmin;" +
    "Password=YourSecurePassword123!;" +
    "MultipleActiveResultSets=False;" +
    "Encrypt=True;" +
    "TrustServerCertificate=False;" +
    "Connection Timeout=30;";
```

### ✅ CORRECT: Connect with Entra ID Token
```csharp
using Microsoft.Data.SqlClient;

var credential = new DefaultAzureCredential();
var token = await credential.GetTokenAsync(
    new TokenRequestContext(new[] { "https://database.windows.net/.default" }));

using var connection = new SqlConnection(
    $"Server=tcp:{server.Data.FullyQualifiedDomainName},1433;Initial Catalog=my-database;");
connection.AccessToken = token.Token;
await connection.OpenAsync();
```

### ❌ INCORRECT: Connection Without Encryption
```csharp
// WRONG - always encrypt connections
string connectionString = $"Server=tcp:{server.Data.FullyQualifiedDomainName},1433;" +
    "Initial Catalog=my-database;" +
    "User ID=sqladmin;" +
    "Password=YourSecurePassword123!;";
// Missing Encrypt=True
```

---

## 14. Resource Identifier Patterns

### ✅ CORRECT: Use CreateResourceIdentifier
```csharp
var resourceId = SqlServerResource.CreateResourceIdentifier(
    subscriptionId,
    "my-resource-group",
    "my-sql-server");

var server = armClient.GetSqlServerResource(resourceId);
var serverData = await server.GetAsync();
```

### ❌ INCORRECT: Hardcoding Resource IDs
```csharp
// WRONG - hardcoding resource IDs is error-prone
var resourceId = new ResourceIdentifier(
    "/subscriptions/12345678/resourceGroups/my-rg/providers/Microsoft.Sql/servers/my-server");
```

---

## 15. Anti-Patterns to Avoid

### ❌ Storing Passwords in Code
```csharp
// WRONG - passwords should come from secure configuration
var serverData = new SqlServerData(AzureLocation.EastUS)
{
    AdministratorLoginPassword = "HardcodedPassword123!"  // Never do this
};
```

### ❌ Creating Client Per Request
```csharp
// WRONG - ArmClient should be reused
public async Task<SqlServerResource> GetServer()
{
    var armClient = new ArmClient(new DefaultAzureCredential()); // Creates new client each time
    // ...
}
```

### ❌ Ignoring Azure AD Authentication
```csharp
// WRONG - prefer Azure AD authentication over SQL authentication
var serverData = new SqlServerData(AzureLocation.EastUS)
{
    AdministratorLogin = "sqladmin",
    AdministratorLoginPassword = "Password123!"
    // Missing Administrators configuration for Azure AD
};
```

---

## Summary Checklist

- [ ] Uses `DefaultAzureCredential` for authentication
- [ ] Uses proper `using` statements for namespaces
- [ ] Navigates resource hierarchy correctly (Subscription → ResourceGroup → Server → Database)
- [ ] Uses `WaitUntil.Completed` when result is needed immediately
- [ ] Includes administrator credentials for server creation
- [ ] Configures Azure AD authentication for production
- [ ] Sets minimum TLS version to 1.2
- [ ] Uses encrypted connections in connection strings
- [ ] Uses async/await properly (no `.Result` or `.Wait()`)
- [ ] Catches `RequestFailedException` with specific status codes
- [ ] Uses `CreateResourceIdentifier` instead of hardcoded IDs
- [ ] Never hardcodes credentials or passwords
- [ ] Checks name availability before creating servers
