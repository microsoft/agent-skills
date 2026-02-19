# Azure Bot Service Management SDK Acceptance Criteria

**SDK**: `azure-mgmt-botservice`
**Repository**: https://github.com/Azure/azure-sdk-for-python
**Purpose**: Skill testing acceptance criteria for validating generated code correctness

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Client with Credential
```python
from azure.mgmt.botservice import AzureBotService
from azure.identity import DefaultAzureCredential
```

#### ✅ CORRECT: Model Imports for Bot
```python
from azure.mgmt.botservice.models import Bot, BotProperties, Sku
```

#### ✅ CORRECT: Channel Model Imports
```python
from azure.mgmt.botservice.models import (
    BotChannel,
    MsTeamsChannel,
    MsTeamsChannelProperties,
    DirectLineChannel,
    DirectLineChannelProperties,
    DirectLineSite,
    WebChatChannel,
    WebChatChannelProperties,
    WebChatSite,
)
```

#### ✅ CORRECT: Connection Setting Imports
```python
from azure.mgmt.botservice.models import (
    ConnectionSetting,
    ConnectionSettingProperties,
)
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Importing directly from azure.botservice
```python
# WRONG - incorrect module path
from azure.botservice import AzureBotService
```

#### ❌ INCORRECT: Hardcoded credentials
```python
# WRONG - credentials should use DefaultAzureCredential
client = AzureBotService(
    subscription_id=subscription_id,
    credentials="hardcoded-key"
)
```

#### ❌ INCORRECT: Missing subscription_id
```python
# WRONG - subscription_id is required
client = AzureBotService(credential=credential)
```

---

## 2. Client Creation Patterns

### 2.1 ✅ CORRECT: Standard Client Creation
```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.botservice import AzureBotService
import os

credential = DefaultAzureCredential()
client = AzureBotService(
    credential=credential,
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
)
```

### 2.2 ✅ CORRECT: Using Context Manager (Best Practice)
```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.botservice import AzureBotService
import os

credential = DefaultAzureCredential()
with AzureBotService(
    credential=credential,
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
) as client:
    # Use client here
    bots = client.bots.list_by_resource_group(resource_group_name="my-group")
```

### 2.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Using old API path
```python
# WRONG - should use client.bots, not client.list_bots
client.list_bots(resource_group_name="my-group")
```

#### ❌ INCORRECT: Missing context manager
```python
# WRONG - client should be closed after use
client = AzureBotService(credential=credential, subscription_id=sub_id)
bots = client.bots.list()
# Missing: client.close() or use 'with' statement
```

---

## 3. Bot Creation Patterns

### 3.1 ✅ CORRECT: Basic Bot Creation
```python
from azure.mgmt.botservice.models import Bot, BotProperties, Sku

bot = client.bots.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    parameters=Bot(
        location="global",
        sku=Sku(name="F0"),  # Free tier
        kind="azurebot",
        properties=BotProperties(
            display_name="My Chat Bot",
            description="A conversational AI bot",
            endpoint="https://my-bot-app.azurewebsites.net/api/messages",
            msa_app_id="<your-app-id>",
            msa_app_type="MultiTenant"
        )
    )
)
```

### 3.2 ✅ CORRECT: Bot with S1 SKU (Production)
```python
bot = client.bots.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    parameters=Bot(
        location="global",
        sku=Sku(name="S1"),  # Standard tier
        kind="azurebot",
        properties=BotProperties(
            display_name="Production Bot",
            description="Production conversational AI bot",
            endpoint="https://prod-bot-app.azurewebsites.net/api/messages",
            msa_app_id="<prod-app-id>",
            msa_app_type="MultiTenant"
        )
    )
)
```

### 3.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing required Bot fields
```python
# WRONG - Bot requires location, sku, kind, and properties
bot = client.bots.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    parameters=Bot(display_name="My Bot")
)
```

#### ❌ INCORRECT: Invalid SKU name
```python
# WRONG - SKU name must be "F0" or "S1"
bot = client.bots.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    parameters=Bot(
        location="global",
        sku=Sku(name="free"),  # Should be "F0"
        kind="azurebot",
        properties=BotProperties(...)
    )
)
```

#### ❌ INCORRECT: Missing endpoint
```python
# WRONG - endpoint is required in BotProperties
bot = client.bots.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    parameters=Bot(
        location="global",
        sku=Sku(name="F0"),
        kind="azurebot",
        properties=BotProperties(
            display_name="My Bot",
            msa_app_id="<app-id>",
            msa_app_type="MultiTenant"
            # Missing: endpoint
        )
    )
)
```

---

## 4. Bot Retrieval Patterns

### 4.1 ✅ CORRECT: Get Bot by Name
```python
bot = client.bots.get(
    resource_group_name=resource_group,
    resource_name=bot_name
)
print(f"Bot: {bot.properties.display_name}")
print(f"Endpoint: {bot.properties.endpoint}")
print(f"SKU: {bot.sku.name}")
```

### 4.2 ✅ CORRECT: List Bots in Resource Group
```python
bots = client.bots.list_by_resource_group(
    resource_group_name=resource_group
)
for bot in bots:
    print(f"Bot: {bot.name} - {bot.properties.display_name}")
```

### 4.3 ✅ CORRECT: List All Bots in Subscription
```python
all_bots = client.bots.list()
for bot in all_bots:
    print(f"Bot: {bot.name}")
```

### 4.4 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Accessing properties directly without attribute
```python
# WRONG - properties.display_name is correct
print(f"Bot: {bot.display_name}")  # Should be bot.properties.display_name
```

#### ❌ INCORRECT: Wrong method name
```python
# WRONG - should be get, not get_bot
bot = client.bots.get_bot(resource_group_name=rg, resource_name=name)
```

---

## 5. Bot Update Patterns

### 5.1 ✅ CORRECT: Update Bot Properties
```python
from azure.mgmt.botservice.models import Bot, BotProperties

updated_bot = client.bots.update(
    resource_group_name=resource_group,
    resource_name=bot_name,
    parameters=Bot(
        location="global",
        properties=BotProperties(
            display_name="Updated Bot Name",
            description="Updated description"
        )
    )
)
```

### 5.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Partial update without location
```python
# WRONG - location is required even for updates
client.bots.update(
    resource_group_name=resource_group,
    resource_name=bot_name,
    parameters=BotProperties(
        display_name="Updated Name"
    )
)
```

---

## 6. Channel Configuration Patterns

### 6.1 ✅ CORRECT: Add Teams Channel
```python
from azure.mgmt.botservice.models import (
    BotChannel,
    MsTeamsChannel,
    MsTeamsChannelProperties,
)

channel = client.channels.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="MsTeamsChannel",
    parameters=BotChannel(
        location="global",
        properties=MsTeamsChannel(
            properties=MsTeamsChannelProperties(
                is_enabled=True
            )
        )
    )
)
```

### 6.2 ✅ CORRECT: Add Direct Line Channel
```python
from azure.mgmt.botservice.models import (
    BotChannel,
    DirectLineChannel,
    DirectLineChannelProperties,
    DirectLineSite,
)

channel = client.channels.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="DirectLineChannel",
    parameters=BotChannel(
        location="global",
        properties=DirectLineChannel(
            properties=DirectLineChannelProperties(
                sites=[
                    DirectLineSite(
                        site_name="Default Site",
                        is_enabled=True,
                        is_v1_enabled=False,
                        is_v3_enabled=True
                    )
                ]
            )
        )
    )
)
```

### 6.3 ✅ CORRECT: Add Web Chat Channel
```python
from azure.mgmt.botservice.models import (
    BotChannel,
    WebChatChannel,
    WebChatChannelProperties,
    WebChatSite,
)

channel = client.channels.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="WebChatChannel",
    parameters=BotChannel(
        location="global",
        properties=WebChatChannel(
            properties=WebChatChannelProperties(
                sites=[
                    WebChatSite(
                        site_name="Default Site",
                        is_enabled=True
                    )
                ]
            )
        )
    )
)
```

### 6.4 ✅ CORRECT: Get Channel Details
```python
channel = client.channels.get(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="DirectLineChannel"
)
print(f"Channel enabled: {channel.properties.is_enabled}")
```

### 6.5 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Nested properties structure
```python
# WRONG - properties should wrap channel-specific properties
parameters=BotChannel(
    location="global",
    properties={  # Should be MsTeamsChannel or similar
        "properties": {
            "is_enabled": True
        }
    }
)
```

#### ❌ INCORRECT: Missing location in BotChannel
```python
# WRONG - location is required
channel = client.channels.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="MsTeamsChannel",
    parameters=BotChannel(
        properties=MsTeamsChannel(...)
    )
)
```

---

## 7. Channel Keys Patterns

### 7.1 ✅ CORRECT: List Channel Keys
```python
keys = client.channels.list_with_keys(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="DirectLineChannel"
)

if hasattr(keys.properties, 'properties'):
    for site in keys.properties.properties.sites:
        print(f"Site: {site.site_name}")
        print(f"Key: {site.key}")
```

### 7.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong channel name format
```python
# WRONG - channel name should match created name
keys = client.channels.list_with_keys(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="directline"  # Should be "DirectLineChannel"
)
```

---

## 8. Bot Connections (OAuth) Patterns

### 8.1 ✅ CORRECT: Create Connection Setting
```python
from azure.mgmt.botservice.models import (
    ConnectionSetting,
    ConnectionSettingProperties,
)

connection = client.bot_connection.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    connection_name="graph-connection",
    parameters=ConnectionSetting(
        location="global",
        properties=ConnectionSettingProperties(
            client_id="<oauth-client-id>",
            client_secret="<oauth-client-secret>",
            scopes="User.Read",
            service_provider_id="<service-provider-id>"
        )
    )
)
```

### 8.2 ✅ CORRECT: List Connections
```python
connections = client.bot_connection.list_by_bot_service(
    resource_group_name=resource_group,
    resource_name=bot_name
)

for conn in connections:
    print(f"Connection: {conn.name}")
```

### 8.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Missing client_secret in production
```python
# WRONG - client_secret should not be hardcoded; use Key Vault
connection = client.bot_connection.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    connection_name="graph-connection",
    parameters=ConnectionSetting(
        location="global",
        properties=ConnectionSettingProperties(
            client_id="hardcoded-id",
            client_secret="hardcoded-secret",  # SECURITY ISSUE
            scopes="User.Read",
            service_provider_id="azure-active-directory"
        )
    )
)
```

---

## 9. Bot Deletion Patterns

### 9.1 ✅ CORRECT: Delete Bot
```python
client.bots.delete(
    resource_group_name=resource_group,
    resource_name=bot_name
)
```

### 9.2 ✅ CORRECT: Delete with Cleanup
```python
# Delete all connections first
connections = client.bot_connection.list_by_bot_service(
    resource_group_name=resource_group,
    resource_name=bot_name
)
for conn in connections:
    client.bot_connection.delete(
        resource_group_name=resource_group,
        resource_name=bot_name,
        connection_name=conn.name
    )

# Then delete bot
client.bots.delete(
    resource_group_name=resource_group,
    resource_name=bot_name
)
```

### 9.3 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Wrong method name
```python
# WRONG - should be delete, not remove
client.bots.remove(
    resource_group_name=resource_group,
    resource_name=bot_name
)
```

---

## 10. Environment Variables

### Required Variables
```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=<your-resource-group>
```

### Optional Variables
```bash
BOT_NAME=my-chat-bot
BOT_ENDPOINT=https://my-bot-app.azurewebsites.net/api/messages
AZURE_AD_APP_ID=<your-app-id>
```

---

## 11. SKU Reference

| SKU | Tier | Description | Limits |
|-----|------|-------------|--------|
| `F0` | Free | Development/testing | Limited messages |
| `S1` | Standard | Production | Unlimited messages |

---

## 12. Channel Types Reference

| Channel | Class Name | Purpose | Configuration |
|---------|-----------|---------|----------------|
| **Teams** | `MsTeamsChannel` | Microsoft Teams integration | `MsTeamsChannelProperties` |
| **Direct Line** | `DirectLineChannel` | Custom client integration | `DirectLineChannelProperties` with `DirectLineSite` |
| **Web Chat** | `WebChatChannel` | Embeddable web widget | `WebChatChannelProperties` with `WebChatSite` |
| **Slack** | `SlackChannel` | Slack workspace integration | Requires OAuth setup |
| **Facebook** | `FacebookChannel` | Messenger integration | Requires OAuth setup |
| **Email** | `EmailChannel` | Email communication | Requires SMTP config |

---

## 13. Common Patterns Checklist

### Bot Management
- [ ] Client creation with DefaultAzureCredential
- [ ] Bot creation with required fields (location, sku, kind, properties)
- [ ] Bot retrieval (get, list_by_resource_group, list)
- [ ] Bot update with partial properties
- [ ] Bot deletion with cleanup
- [ ] Proper context manager usage

### Channel Configuration
- [ ] Teams channel creation
- [ ] Direct Line channel with sites
- [ ] Web Chat channel with sites
- [ ] Channel retrieval by name
- [ ] Channel key listing

### Bot Connections
- [ ] Connection setting creation with OAuth
- [ ] Connection listing by bot service
- [ ] Secure credential handling (no hardcoding)

### Error Handling
- [ ] Check for HTTP errors (404, 400, etc.)
- [ ] Handle missing bots gracefully
- [ ] Validate channel names before use

---

## 14. Quick Reference: Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `InvalidName` | Bot name format incorrect | Use alphanumeric + hyphens, 3-24 chars |
| `SkuNotValid` | Invalid SKU name | Use "F0" or "S1" only |
| `MissingLocation` | Bot location not specified | Always use "global" |
| `InvalidEndpoint` | Malformed endpoint URL | Ensure valid HTTPS URL |
| `AuthenticationFailed` | Credentials invalid or expired | Use DefaultAzureCredential or check permissions |
| `ChannelNotFound` | Channel doesn't exist | Check exact channel name (case-sensitive) |
| `SubscriptionNotFound` | Invalid subscription ID | Verify subscription exists and is active |
| `ResourceGroupNotFound` | Resource group doesn't exist | Create resource group first |
