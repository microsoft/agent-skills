# Azure Bot Service SDK Acceptance Criteria

**SDK**: `Azure.ResourceManager.BotService`  
**Repository**: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/botservice/Azure.ResourceManager.BotService  
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports
#### ✅ CORRECT: Full namespace imports
```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.BotService;
using Azure.ResourceManager.BotService.Models;
```

#### ❌ INCORRECT: Missing required namespaces
```csharp
using Azure.ResourceManager.BotService;
// Missing Azure.Identity, Azure.ResourceManager
```

### 1.2 Model Imports
#### ✅ CORRECT: Models namespace for data types
```csharp
using Azure.ResourceManager.BotService.Models;

BotServiceKind kind = BotServiceKind.Azurebot;
BotServiceSkuName sku = BotServiceSkuName.F0;
```

#### ❌ INCORRECT: Using Bot Builder SDK for resource management
```csharp
using Microsoft.Bot.Builder;  // Wrong - this is for bot logic
```

---

## 2. Client Creation

### 2.1 ArmClient Initialization
#### ✅ CORRECT: Using DefaultAzureCredential
```csharp
var credential = new DefaultAzureCredential();
ArmClient armClient = new ArmClient(credential);
```

#### ❌ INCORRECT: Hardcoded credentials
```csharp
ArmClient armClient = new ArmClient(new ClientSecretCredential(tenantId, clientId, clientSecret));
```

### 2.2 Bot Collection Access
#### ✅ CORRECT: Navigate hierarchy properly
```csharp
SubscriptionResource subscription = await armClient.GetDefaultSubscriptionAsync();
ResourceGroupResource resourceGroup = await subscription.GetResourceGroups().GetAsync("myResourceGroup");
BotCollection botCollection = resourceGroup.GetBots();
```

#### ❌ INCORRECT: Skipping hierarchy
```csharp
var bots = armClient.GetBots();  // Wrong - must go through resource group
```

---

## 3. Core Operations

### 3.1 Create Bot Resource
#### ✅ CORRECT: Full bot configuration
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

#### ❌ INCORRECT: Missing required BotProperties
```csharp
var botData = new BotData(AzureLocation.WestUS2)
{
    Kind = BotServiceKind.Azurebot,
    Sku = new BotServiceSku(BotServiceSkuName.F0)
    // Missing Properties - required for bot creation
};
```

### 3.2 BotProperties Constructor Parameters
#### ✅ CORRECT: All required parameters
```csharp
Properties = new BotProperties(
    displayName: "MyBot",
    endpoint: new Uri("https://mybot.azurewebsites.net/api/messages"),
    msaAppId: "your-msa-app-id")
```

#### ❌ INCORRECT: Missing endpoint
```csharp
Properties = new BotProperties(
    displayName: "MyBot",
    msaAppId: "your-msa-app-id")
// Missing endpoint - constructor requires it
```

---

## 4. Channel Configuration

### 4.1 Configure DirectLine Channel
#### ✅ CORRECT: DirectLine with site configuration
```csharp
BotResource bot = await resourceGroup.GetBots().GetAsync("myBotName");

BotChannelCollection channels = bot.GetBotChannels();

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

#### ❌ INCORRECT: Missing DirectLineChannelProperties
```csharp
var channelData = new BotChannelData(AzureLocation.WestUS2)
{
    Properties = new DirectLineChannel()
    // Missing Properties - channel won't have sites
};
```

### 4.2 Configure Microsoft Teams Channel
#### ✅ CORRECT: Teams channel with calling option
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

#### ❌ INCORRECT: Wrong channel name constant
```csharp
await channels.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "TeamsChannel",  // Wrong - use BotChannelName.MsTeamsChannel
    teamsChannelData);
```

### 4.3 Configure Web Chat Channel
#### ✅ CORRECT: Web Chat with site
```csharp
var webChatChannelData = new BotChannelData(AzureLocation.WestUS2)
{
    Properties = new WebChatChannel()
    {
        Properties = new WebChatChannelProperties()
        {
            Sites =
            {
                new WebChatSite("Default Site")
                {
                    IsEnabled = true
                }
            }
        }
    }
};

await channels.CreateOrUpdateAsync(
    WaitUntil.Completed,
    BotChannelName.WebChatChannel,
    webChatChannelData);
```

---

## 5. Channel Types Reference

### 5.1 Supported Channel Constants
#### ✅ CORRECT: Using BotChannelName constants
```csharp
BotChannelName.DirectLineChannel      // Direct Line
BotChannelName.DirectLineSpeechChannel // Direct Line Speech
BotChannelName.MsTeamsChannel         // Microsoft Teams
BotChannelName.WebChatChannel         // Web Chat
BotChannelName.SlackChannel           // Slack
BotChannelName.FacebookChannel        // Facebook
BotChannelName.EmailChannel           // Email
BotChannelName.TelegramChannel        // Telegram
BotChannelName.TelephonyChannel       // Telephony
```

### 5.2 Channel Class Mapping
| Channel Name | Channel Class | Properties Class |
|--------------|---------------|------------------|
| DirectLineChannel | `DirectLineChannel` | `DirectLineChannelProperties` |
| MsTeamsChannel | `MsTeamsChannel` | `MsTeamsChannelProperties` |
| WebChatChannel | `WebChatChannel` | `WebChatChannelProperties` |
| SlackChannel | `SlackChannel` | `SlackChannelProperties` |

---

## 6. Get and List Operations

### 6.1 Get Bot
#### ✅ CORRECT: Using async Get
```csharp
BotResource bot = await botCollection.GetAsync("myBotName");
Console.WriteLine($"Bot: {bot.Data.Properties.DisplayName}");
Console.WriteLine($"Endpoint: {bot.Data.Properties.Endpoint}");
```

### 6.2 List Channels
#### ✅ CORRECT: Using async enumeration
```csharp
await foreach (BotChannelResource channel in bot.GetBotChannels().GetAllAsync())
{
    Console.WriteLine($"Channel: {channel.Data.Name}");
}
```

#### ❌ INCORRECT: Synchronous enumeration
```csharp
var channels = bot.GetBotChannels().ToList();  // Wrong - blocks async
```

---

## 7. Key Operations

### 7.1 Regenerate DirectLine Keys
#### ✅ CORRECT: Using BotChannelRegenerateKeysContent
```csharp
var regenerateRequest = new BotChannelRegenerateKeysContent(BotChannelName.DirectLineChannel)
{
    SiteName = "Default Site"
};

BotChannelResource channelWithKeys = await bot.GetBotChannelWithRegenerateKeysAsync(regenerateRequest);
```

#### ❌ INCORRECT: Trying to regenerate without site name
```csharp
var regenerateRequest = new BotChannelRegenerateKeysContent(BotChannelName.DirectLineChannel);
// Missing SiteName - required for DirectLine
```

---

## 8. Update and Delete

### 8.1 Update Bot
#### ✅ CORRECT: Using full BotData for update
```csharp
BotResource bot = await botCollection.GetAsync("myBotName");

var updateData = new BotData(bot.Data.Location)
{
    Properties = new BotProperties(
        displayName: "Updated Bot Name",
        endpoint: bot.Data.Properties.Endpoint,
        msaAppId: bot.Data.Properties.MsaAppId)
    {
        Description = "Updated description"
    }
};

await bot.UpdateAsync(updateData);
```

#### ❌ INCORRECT: Modifying Data directly
```csharp
bot.Data.Properties.DisplayName = "Updated Name";  // Data is read-only
```

### 8.2 Delete Bot
#### ✅ CORRECT: Using DeleteAsync with WaitUntil
```csharp
BotResource bot = await botCollection.GetAsync("myBotName");
await bot.DeleteAsync(WaitUntil.Completed);
```

---

## 9. Enum Values

### 9.1 BotServiceKind Values
#### ✅ CORRECT: Valid bot kinds
```csharp
BotServiceKind.Azurebot   // Azure Bot (recommended)
BotServiceKind.Bot        // Legacy Bot Framework bot
BotServiceKind.Designer   // Composer bot
BotServiceKind.Function   // Function bot
BotServiceKind.Sdk        // SDK bot
```

### 9.2 BotServiceSkuName Values
#### ✅ CORRECT: Valid SKU names
```csharp
BotServiceSkuName.F0  // Free tier
BotServiceSkuName.S1  // Standard tier
```

### 9.3 BotMsaAppType Values
#### ✅ CORRECT: Valid MSA app types
```csharp
BotMsaAppType.MultiTenant      // Multi-tenant app
BotMsaAppType.SingleTenant     // Single-tenant app
BotMsaAppType.UserAssignedMSI  // User-assigned managed identity
```

---

## 10. Error Handling

### 10.1 RequestFailedException Handling
#### ✅ CORRECT: Pattern matching on status codes
```csharp
using Azure;

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

#### ❌ INCORRECT: Generic exception handling
```csharp
try
{
    await botCollection.CreateOrUpdateAsync(WaitUntil.Completed, botName, botData);
}
catch (Exception ex)
{
    Console.WriteLine(ex.Message);  // Loses Azure-specific context
}
```

---

## 11. Security Best Practices

### 11.1 MSA App Credentials
#### ✅ CORRECT: Use Key Vault for MSA App credentials
```csharp
// Store MSA App ID in Key Vault or configuration
var msaAppId = configuration["BotConfiguration:MsaAppId"];

Properties = new BotProperties(
    displayName: "MyBot",
    endpoint: new Uri("https://mybot.azurewebsites.net/api/messages"),
    msaAppId: msaAppId)
```

#### ❌ INCORRECT: Hardcoded MSA App ID
```csharp
Properties = new BotProperties(
    displayName: "MyBot",
    endpoint: new Uri("https://mybot.azurewebsites.net/api/messages"),
    msaAppId: "12345678-1234-1234-1234-123456789012")  // Hardcoded
```

### 11.2 Use Managed Identity for Production
#### ✅ CORRECT: User-assigned managed identity
```csharp
Properties = new BotProperties(
    displayName: "MyBot",
    endpoint: new Uri("https://mybot.azurewebsites.net/api/messages"),
    msaAppId: userAssignedMsiClientId)
{
    MsaAppType = BotMsaAppType.UserAssignedMSI,
    MsaAppMSIResourceId = new ResourceIdentifier(
        "/subscriptions/.../resourceGroups/.../providers/Microsoft.ManagedIdentity/userAssignedIdentities/my-identity")
}
```

### 11.3 Enable Secure Sites for DirectLine
#### ✅ CORRECT: SecureSite enabled for production
```csharp
new DirectLineSite("Production Site")
{
    IsEnabled = true,
    IsV3Enabled = true,
    IsSecureSiteEnabled = true  // Enables enhanced auth
}
```

#### ❌ INCORRECT: Secure site disabled in production
```csharp
new DirectLineSite("Production Site")
{
    IsEnabled = true,
    IsSecureSiteEnabled = false  // Security risk in production
}
```

---

## 12. Best Practices Checklist

- [ ] Use `DefaultAzureCredential` for authentication
- [ ] Use `async/await` for all operations
- [ ] Use `WaitUntil.Completed` for synchronous completion
- [ ] Use `BotServiceKind.Azurebot` for new bots
- [ ] Use `BotChannelName` constants for channel names
- [ ] Include all required BotProperties constructor parameters
- [ ] Store MSA App credentials in Key Vault
- [ ] Use managed identity (`BotMsaAppType.UserAssignedMSI`) for production
- [ ] Enable secure sites for DirectLine channels in production
- [ ] Handle `RequestFailedException` with status code matching
- [ ] Use `await foreach` for listing resources
