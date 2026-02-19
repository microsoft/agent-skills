# Azure.ResourceManager.BotService SDK Acceptance Criteria (.NET)

**SDK**: `Azure.ResourceManager.BotService`
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/botservice/Azure.ResourceManager.BotService
**Package**: https://www.nuget.org/packages/Azure.ResourceManager.BotService
**Purpose**: Skill testing acceptance criteria for validating generated C# code correctness

---

## 1. Correct Using Statements

### 1.1 Core Imports

#### ✅ CORRECT: Basic Client Imports
```csharp
using Azure;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.BotService;
using Azure.ResourceManager.BotService.Models;
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using non-existent namespaces
```csharp
// WRONG - These don't exist
using Azure.BotService;
using Microsoft.Bot.Builder.Management;
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Create ArmClient
```csharp
var credential = new DefaultAzureCredential();
ArmClient armClient = new ArmClient(credential);
```

---

## 3. Bot Resource Operations

### 3.1 ✅ CORRECT: Create Bot Resource
```csharp
var botData = new BotData(AzureLocation.WestUS2)
{
    Kind = BotServiceKind.Azurebot,
    Sku = new BotServiceSku(BotServiceSkuName.F0),
    Properties = new BotProperties(
        displayName: "MyBot",
        endpoint: new Uri("https://mybot.azurewebsites.net/api/messages"),
        msaAppId: "<your-msa-app-id>")
    {
        Description = "My Azure Bot",
        MsaAppType = BotMsaAppType.MultiTenant
    }
};

ArmOperation<BotResource> operation = await botCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, 
    "myBotName", 
    botData);
    
BotResource bot = operation.Value;
```

### 3.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing required properties
```csharp
// WRONG - Missing displayName, endpoint, msaAppId
var botData = new BotData(AzureLocation.WestUS2)
{
    Kind = BotServiceKind.Azurebot
};
```

---

## 4. Channel Operations

### 4.1 ✅ CORRECT: Configure DirectLine Channel
```csharp
var channelData = new BotChannelData(AzureLocation.WestUS2)
{
    Properties = new DirectLineChannel()
    {
        Properties = new DirectLineChannelProperties()
        {
            Sites = 
            {
                new DirectLineSite("Default Site")
                {
                    IsEnabled = true,
                    IsV1Enabled = false,
                    IsV3Enabled = true,
                    IsSecureSiteEnabled = true
                }
            }
        }
    }
};

ArmOperation<BotChannelResource> channelOp = await channels.CreateOrUpdateAsync(
    WaitUntil.Completed,
    BotChannelName.DirectLineChannel,
    channelData);
```

### 4.2 ✅ CORRECT: Configure Teams Channel
```csharp
var teamsChannelData = new BotChannelData(AzureLocation.WestUS2)
{
    Properties = new MsTeamsChannel()
    {
        Properties = new MsTeamsChannelProperties()
        {
            IsEnabled = true,
            EnableCalling = false
        }
    }
};

await channels.CreateOrUpdateAsync(
    WaitUntil.Completed,
    BotChannelName.MsTeamsChannel,
    teamsChannelData);
```

---

## 5. Error Handling Patterns

### 5.1 ✅ CORRECT: Handle RequestFailedException
```csharp
try
{
    var operation = await botCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, 
        botName, 
        botData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Bot already exists");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

---

## 6. Key Types Reference

| Type | Purpose |
|------|---------|
| `ArmClient` | Entry point for ARM operations |
| `BotResource` | Represents an Azure Bot resource |
| `BotCollection` | Collection for bot CRUD |
| `BotData` | Bot resource definition |
| `BotProperties` | Bot configuration |
| `BotChannelResource` | Channel configuration |
| `BotChannelData` | Channel data |
| `DirectLineChannel` | DirectLine channel type |
| `MsTeamsChannel` | Teams channel type |

## 7. Supported Channels

| Channel | Class | Constant |
|---------|-------|----------|
| Direct Line | `DirectLineChannel` | `BotChannelName.DirectLineChannel` |
| Teams | `MsTeamsChannel` | `BotChannelName.MsTeamsChannel` |
| Web Chat | `WebChatChannel` | `BotChannelName.WebChatChannel` |
| Slack | `SlackChannel` | `BotChannelName.SlackChannel` |

## 8. BotServiceKind Values

| Value | Description |
|-------|-------------|
| `Azurebot` | Azure Bot (recommended) |
| `Bot` | Legacy Bot Framework |
| `Designer` | Composer bot |
| `Function` | Function bot |

## 9. BotServiceSkuName Values

| Value | Description |
|-------|-------------|
| `F0` | Free tier |
| `S1` | Standard tier |

---

## 10. Best Practices Summary

1. **Use DefaultAzureCredential** — Supports multiple auth methods
2. **Use WaitUntil.Completed** — For synchronous operations
3. **Handle RequestFailedException** — For API errors
4. **Use async methods** — All operations support async
5. **Use managed identity** — For production bots
6. **Enable secure sites** — For DirectLine in production
