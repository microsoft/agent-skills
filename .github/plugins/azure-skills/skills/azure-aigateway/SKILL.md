---
name: azure-aigateway
description: |
  Configure Azure API Management (APIM) as AI Gateway to secure, observe, control AI models, MCP servers, agents. Helps with rate limiting, semantic caching, content safety, load balancing.
  USE FOR: AI Gateway, APIM, setup gateway, configure gateway, add gateway, model gateway, MCP server, rate limit, token limit, semantic cache, content safety, load balance, OpenAPI import, convert API to MCP.
  DO NOT USE FOR: deploy models (use microsoft-foundry), Azure Functions (use azure-functions), databases (use azure-postgres).
---

# Azure AI Gateway

Bootstrap and configure Azure API Management (APIM) as an AI Gateway for securing, observing, and controlling AI models, tools (MCP Servers), and agents.

## Skill Activation Triggers

**Use this skill immediately when the user asks to:**
- "Set up a gateway for my model"
- "Set up a gateway for my tools"
- "Set up a gateway for my agents"
- "Add a gateway to my MCP server"
- "Protect my AI model with a gateway"
- "Secure my AI agents"
- "Ratelimit my model requests"
- "Ratelimit my tool requests"
- "Limit tokens for my model"
- "Add rate limiting to my MCP server"
- "Enable semantic caching for my AI API"
- "Add content safety to my AI endpoint"
- "Add my model behind gateway"
- "Import API from OpenAPI spec"
- "Add API to gateway from swagger"
- "Convert my API to MCP"
- "Expose my API as MCP server"

**Key Indicators:**
- User deploying Azure OpenAI, AI Foundry, or other AI models
- User creating or managing MCP servers
- User needs token limits, rate limiting, or quota management
- User wants to cache AI responses to reduce costs
- User needs content filtering or safety controls
- User wants load balancing across multiple AI backends

**Secondary Triggers (Proactive Recommendations):**
- After model creation: Recommend AI Gateway for security, caching, and token limits
- After MCP server creation: Recommend AI Gateway for rate limiting, content safety, and auth

## Overview

Azure API Management serves as an AI Gateway that provides:
- **Security**: Authentication, authorization, and content safety
- **Observability**: Token metrics, logging, and monitoring
- **Control**: Rate limiting, token limits, and load balancing
- **Optimization**: Semantic caching to reduce costs and latency

```
AI Models ──┐                      ┌── Azure OpenAI
MCP Tools ──┼── AI Gateway (APIM) ──┼── AI Foundry
Agents ─────┘                      └── Custom Models
```

## Key Resources

- **GitHub Repo**: https://github.com/Azure-Samples/AI-Gateway (aka.ms/aigateway)
- **Docs**:
  - [GenAI Gateway Capabilities](https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities)
  - [MCP Server Overview](https://learn.microsoft.com/en-us/azure/api-management/mcp-server-overview)
  - [Azure AI Foundry API](https://learn.microsoft.com/en-us/azure/api-management/azure-ai-foundry-api)
  - [Semantic Caching](https://learn.microsoft.com/en-us/azure/api-management/azure-openai-enable-semantic-caching)
  - [Token Limits & LLM Logs](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-llm-logs)

## Configuration Rules

**Default to `Basicv2` SKU** when creating new APIM instances:
- Cheaper than other tiers
- Creates quickly (~5-10 minutes vs 30+ for Premium)
- Supports all AI Gateway policies

## Pattern 1: Quick Bootstrap AI Gateway

Deploy APIM with Basicv2 SKU for AI workloads.

```bash
# Create resource group
az group create --name rg-aigateway --location eastus2

# Deploy APIM with Bicep
az deployment group create \
  --resource-group rg-aigateway \
  --template-file main.bicep \
  --parameters apimSku=Basicv2
```

### Bicep Template

```bicep
param location string = resourceGroup().location
param apimSku string = 'Basicv2'
param apimManagedIdentityType string = 'SystemAssigned'

// NOTE: Using 2024-06-01-preview because Basicv2 SKU support currently requires this preview API version.
//       Update to the latest stable (GA) API version once Basicv2 is available there.
resource apimService 'Microsoft.ApiManagement/service@2024-06-01-preview' = {
  name: 'apim-aigateway-${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: apimSku
    capacity: 1
  }
  properties: {
    publisherEmail: 'admin@contoso.com'
    publisherName: 'Contoso'
  }
  identity: {
    type: apimManagedIdentityType
  }
}

output gatewayUrl string = apimService.properties.gatewayUrl
output principalId string = apimService.identity.principalId
```

## Pattern 2: Semantic Caching

Cache similar prompts to reduce costs and latency.

```xml
<policies>
    <inbound>
        <base />
        <!-- Cache lookup with 0.8 similarity threshold -->
        <azure-openai-semantic-cache-lookup 
            score-threshold="0.8" 
            embeddings-backend-id="embeddings-backend" 
            embeddings-backend-auth="system-assigned" />
        <set-backend-service backend-id="{backend-id}" />
    </inbound>
    <outbound>
        <!-- Cache responses for 120 seconds -->
        <azure-openai-semantic-cache-store duration="120" />
        <base />
    </outbound>
</policies>
```

**Options:**
| Parameter | Range | Description |
|-----------|-------|-------------|
| `score-threshold` | 0.7-0.95 | Higher = stricter matching |
| `duration` | 60-3600 | Cache TTL in seconds |

## Pattern 3: Token Rate Limiting

Limit tokens per minute to control costs and prevent abuse.

```xml
<policies>
    <inbound>
        <base />
        <set-backend-service backend-id="{backend-id}" />
        <!-- Limit to 500 tokens per minute per subscription -->
        <azure-openai-token-limit 
            counter-key="@(context.Subscription.Id)"
            tokens-per-minute="500" 
            estimate-prompt-tokens="false" 
            remaining-tokens-variable-name="remainingTokens" />
    </inbound>
</policies>
```

**Options:**
| Parameter | Values | Description |
|-----------|--------|-------------|
| `counter-key` | Subscription.Id, Request.IpAddress, custom | Grouping key for limits |
| `tokens-per-minute` | 100-100000 | Token quota |
| `estimate-prompt-tokens` | true/false | true = faster but less accurate |

## Pattern 4: Content Safety

Filter harmful content and detect jailbreak attempts.

```xml
<policies>
    <inbound>
        <base />
        <set-backend-service backend-id="{backend-id}" />
        <!-- Block severity 4+ content, detect jailbreaks -->
        <llm-content-safety backend-id="content-safety-backend" shield-prompt="true">
            <categories output-type="EightSeverityLevels">
                <category name="Hate" threshold="4" />
                <category name="Sexual" threshold="4" />
                <category name="SelfHarm" threshold="4" />
                <category name="Violence" threshold="4" />
            </categories>
            <blocklists>
                <id>custom-blocklist</id>
            </blocklists>
        </llm-content-safety>
    </inbound>
</policies>
```

**Options:**
| Parameter | Range | Description |
|-----------|-------|-------------|
| `threshold` | 0-7 | 0=safe, 7=severe |
| `shield-prompt` | true/false | Detect jailbreak attempts |

## Pattern 5: Rate Limits for MCPs/OpenAPI Tools

Protect MCP servers and tools with request rate limiting.

```xml
<policies>
    <inbound>
        <base />
        <!-- 10 calls per 60 seconds per IP -->
        <rate-limit-by-key 
            calls="10" 
            renewal-period="60" 
            counter-key="@(context.Request.IpAddress)" 
            remaining-calls-variable-name="remainingCalls" />
    </inbound>
    <outbound>
        <set-header name="X-Rate-Limit-Remaining" exists-action="override">
            <value>@(context.Variables.GetValueOrDefault<int>("remainingCalls", 0).ToString())</value>
        </set-header>
        <base />
    </outbound>
</policies>
```

## Pattern 6: Managed Identity Authentication

Secure backend access with managed identity instead of API keys.

```xml
<policies>
    <inbound>
        <base />
        <!-- Managed identity auth to Azure OpenAI -->
        <authentication-managed-identity 
            resource="https://cognitiveservices.azure.com" 
            output-token-variable-name="managed-id-access-token" 
            ignore-error="false" />
        <set-header name="Authorization" exists-action="override">
            <value>@("Bearer " + (string)context.Variables["managed-id-access-token"])</value>
        </set-header>
        <set-backend-service backend-id="{backend-id}" />
        <!-- Emit token metrics for monitoring -->
        <azure-openai-emit-token-metric namespace="openai">
            <dimension name="Subscription ID" value="@(context.Subscription.Id)" />
            <dimension name="Client IP" value="@(context.Request.IpAddress)" />
            <dimension name="API ID" value="@(context.Api.Id)" />
        </azure-openai-emit-token-metric>
    </inbound>
</policies>
```

## Pattern 7: Load Balancing with Retry

Distribute load across multiple backends with automatic failover.

```xml
<policies>
    <inbound>
        <base />
        <set-backend-service backend-id="{backend-pool-id}" />
    </inbound>
    <backend>
        <!-- Retry on 429 (rate limit) or 503 (service unavailable) -->
        <retry count="2" interval="0" first-fast-retry="true" 
            condition="@(context.Response.StatusCode == 429 || context.Response.StatusCode == 503)">
            <set-backend-service backend-id="{backend-pool-id}" />
            <forward-request buffer-request-body="true" />
        </retry>
    </backend>
    <on-error>
        <when condition="@(context.Response.StatusCode == 503)">
            <return-response>
                <set-status code="503" reason="Service Unavailable" />
            </return-response>
        </when>
    </on-error>
</policies>
```

## Pattern 8: Add AI Foundry Model Behind Gateway

When user asks to "add my model behind gateway", first discover available models from Azure AI Foundry, then ask which model to add.

### Step 1: Discover AI Foundry Projects and Available Models

```bash
# Set environment variables
accountName="<ai-foundry-resource-name>"
resourceGroupName="<resource-group>"

# List AI Foundry resources (AI Services accounts)
az cognitiveservices account list --query "[?kind=='AIServices'].{name:name, resourceGroup:resourceGroup, location:location}" -o table

# List available models in the AI Foundry resource
az cognitiveservices account list-models \
  -n $accountName \
  -g $resourceGroupName \
  | jq '.[] | { name: .name, format: .format, version: .version, sku: .skus[0].name, capacity: .skus[0].capacity.default }'

# List already deployed models
az cognitiveservices account deployment list \
  -n $accountName \
  -g $resourceGroupName
```

### Step 2: Ask User Which Model to Add

After listing the available models, **use the ask_user tool** to present the models as choices and let the user select which model to add behind the gateway.

Example choices to present:
- Model deployments from the discovered list
- Include model name, format (provider), version, and SKU info

### Step 3: Deploy the Model (if not already deployed)

```bash
# Deploy the selected model to AI Foundry
az cognitiveservices account deployment create \
  -n $accountName \
  -g $resourceGroupName \
  --deployment-name <model-name> \
  --model-name <model-name> \
  --model-version <version> \
  --model-format <format> \
  --sku-capacity 1 \
  --sku-name <sku>
```

### Step 4: Configure APIM Backend for Selected Model

```bash
# Get the AI Foundry inference endpoint
ENDPOINT=$(az cognitiveservices account show \
  -n $accountName \
  -g $resourceGroupName \
  | jq -r '.properties.endpoints["Azure AI Model Inference API"]')

# Create APIM backend for the selected model
az apim backend create \
  --resource-group <apim-resource-group> \
  --service-name <apim-service-name> \
  --backend-id <model-deployment-name>-backend \
  --protocol http \
  --url "${ENDPOINT}"
```

### Step 5: Create API and Apply Policies

```bash
# Import Azure OpenAI API specification
az apim api import \
  --resource-group <apim-resource-group> \
  --service-name <apim-service-name> \
  --path <model-deployment-name> \
  --specification-format OpenApiJson \
  --specification-url "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/AzureOpenAI/inference/stable/2024-02-01/inference.json"
```

### Step 6: Grant APIM Access to AI Foundry

```bash
# Get APIM managed identity principal ID
APIM_PRINCIPAL_ID=$(az apim show \
  --name <apim-service-name> \
  --resource-group <apim-resource-group> \
  --query "identity.principalId" -o tsv)

# Get AI Foundry resource ID
AI_RESOURCE_ID=$(az cognitiveservices account show \
  -n $accountName \
  -g $resourceGroupName \
  --query "id" -o tsv)

# Assign Cognitive Services User role
az role assignment create \
  --assignee $APIM_PRINCIPAL_ID \
  --role "Cognitive Services User" \
  --scope $AI_RESOURCE_ID
```

### Bicep Template for Backend Configuration

```bicep
param apimServiceName string
param backendId string
param aiFoundryEndpoint string
param modelDeploymentName string

resource apimService 'Microsoft.ApiManagement/service@2024-06-01-preview' existing = {
  name: apimServiceName
}

resource backend 'Microsoft.ApiManagement/service/backends@2024-06-01-preview' = {
  parent: apimService
  name: backendId
  properties: {
    protocol: 'http'
    url: '${aiFoundryEndpoint}openai/deployments/${modelDeploymentName}'
    credentials: {
      header: {}
    }
    tls: {
      validateCertificateChain: true
      validateCertificateName: true
    }
  }
}
```

## Pattern 9: Import API from OpenAPI Specification

Add an API to the gateway from an OpenAPI/Swagger specification, either from a local file or web URL.

### Step 1: Import API from Web URL

```bash
# Import API from a publicly accessible OpenAPI spec URL
az apim api import \
  --resource-group <apim-resource-group> \
  --service-name <apim-service-name> \
  --api-id <api-id> \
  --path <api-path> \
  --display-name "<API Display Name>" \
  --specification-format OpenApiJson \
  --specification-url "https://example.com/openapi.json"
```

### Step 2: Import API from Local File

```bash
# Import API from a local OpenAPI spec file (JSON or YAML)
az apim api import \
  --resource-group <apim-resource-group> \
  --service-name <apim-service-name> \
  --api-id <api-id> \
  --path <api-path> \
  --display-name "<API Display Name>" \
  --specification-format OpenApi \
  --specification-path "./openapi.yaml"
```

### Step 3: Configure Backend for the API

```bash
# Create backend pointing to your API server
az apim backend create \
  --resource-group <apim-resource-group> \
  --service-name <apim-service-name> \
  --backend-id <backend-id> \
  --protocol http \
  --url "https://your-api-server.com"

# Update API to use the backend
az apim api update \
  --resource-group <apim-resource-group> \
  --service-name <apim-service-name> \
  --api-id <api-id> \
  --set properties.serviceUrl="https://your-api-server.com"
```

### Step 4: Apply Policies (Optional)

```xml
<policies>
    <inbound>
        <base />
        <set-backend-service backend-id="{backend-id}" />
        <!-- Add rate limiting -->
        <rate-limit-by-key 
            calls="100" 
            renewal-period="60" 
            counter-key="@(context.Request.IpAddress)" />
    </inbound>
    <outbound>
        <base />
    </outbound>
</policies>
```

### Supported Specification Formats

| Format | Value | File Extension |
|--------|-------|----------------|
| OpenAPI 3.x JSON | `OpenApiJson` | `.json` |
| OpenAPI 3.x YAML | `OpenApi` | `.yaml`, `.yml` |
| Swagger 2.0 JSON | `SwaggerJson` | `.json` |
| Swagger 2.0 (link) | `SwaggerLinkJson` | URL |
| WSDL | `Wsdl` | `.wsdl` |
| WADL | `Wadl` | `.wadl` |

## Pattern 10: Convert API to MCP Server

Convert existing APIM API operations into an MCP (Model Context Protocol) server, enabling AI agents to discover and use your APIs as tools.

### Prerequisites

- APIM instance with Basicv2 SKU or higher
- Existing API imported into APIM
- MCP feature enabled on APIM

### Step 1: List Existing APIs in APIM

```bash
# List all APIs in APIM
az apim api list \
  --resource-group <apim-resource-group> \
  --service-name <apim-service-name> \
  --query "[].{id:name, displayName:displayName, path:path}" \
  -o table
```

### Step 2: Ask User Which API to Convert

After listing the APIs, **use the ask_user tool** to let the user select which API to convert to an MCP server.

### Step 3: List API Operations

```bash
# List all operations for the selected API
az apim api operation list \
  --resource-group <apim-resource-group> \
  --service-name <apim-service-name> \
  --api-id <api-id> \
  --query "[].{operationId:name, displayName:displayName, method:method, urlTemplate:urlTemplate}" \
  -o table
```

### Step 4: Ask User Which Operations to Expose as MCP Tools

After listing the operations, **use the ask_user tool** to present the operations as choices. Let the user select which operations to expose as MCP tools. Users may want to expose all operations or only a subset.

Example choices to present:
- All operations (convert entire API)
- Individual operations from the discovered list
- Include operation name, method, and URL template

### Step 5: Enable MCP Server on APIM

```bash
# Enable MCP server capability (via ARM/Bicep or Portal)
# Note: MCP configuration is done via APIM policies and product configuration
```

### Step 6: Configure MCP Endpoint for API

Create an MCP-compatible endpoint that exposes your API operations as tools:

```xml
<policies>
    <inbound>
        <base />
        <!-- MCP tools/list endpoint handler -->
        <choose>
            <when condition="@(context.Request.Url.Path.EndsWith("/mcp/tools/list"))">
                <return-response>
                    <set-status code="200" reason="OK" />
                    <set-header name="Content-Type" exists-action="override">
                        <value>application/json</value>
                    </set-header>
                    <set-body>@{
                        var tools = new JArray();
                        // Define your API operations as MCP tools
                        tools.Add(new JObject(
                            new JProperty("name", "operation_name"),
                            new JProperty("description", "Description of what this operation does"),
                            new JProperty("inputSchema", new JObject(
                                new JProperty("type", "object"),
                                new JProperty("properties", new JObject(
                                    new JProperty("param1", new JObject(
                                        new JProperty("type", "string"),
                                        new JProperty("description", "Parameter description")
                                    ))
                                ))
                            ))
                        ));
                        return new JObject(new JProperty("tools", tools)).ToString();
                    }</set-body>
                </return-response>
            </when>
        </choose>
    </inbound>
</policies>
```

### Step 7: Bicep Template for MCP-Enabled API

```bicep
param apimServiceName string
param apiId string
param apiDisplayName string
param apiPath string
param backendUrl string

resource apimService 'Microsoft.ApiManagement/service@2024-06-01-preview' existing = {
  name: apimServiceName
}

resource api 'Microsoft.ApiManagement/service/apis@2024-06-01-preview' = {
  parent: apimService
  name: apiId
  properties: {
    displayName: apiDisplayName
    path: apiPath
    protocols: ['https']
    serviceUrl: backendUrl
    subscriptionRequired: true
    // MCP endpoints
    apiType: 'http'
  }
}

// MCP tools/list operation
resource mcpToolsListOperation 'Microsoft.ApiManagement/service/apis/operations@2024-06-01-preview' = {
  parent: api
  name: 'mcp-tools-list'
  properties: {
    displayName: 'MCP Tools List'
    method: 'POST'
    urlTemplate: '/mcp/tools/list'
    description: 'List available MCP tools'
  }
}

// MCP tools/call operation
resource mcpToolsCallOperation 'Microsoft.ApiManagement/service/apis/operations@2024-06-01-preview' = {
  parent: api
  name: 'mcp-tools-call'
  properties: {
    displayName: 'MCP Tools Call'
    method: 'POST'
    urlTemplate: '/mcp/tools/call'
    description: 'Call an MCP tool'
  }
}
```

### Step 8: Test MCP Endpoint

```bash
# Get APIM gateway URL
GATEWAY_URL=$(az apim show \
  --name <apim-service-name> \
  --resource-group <apim-resource-group> \
  --query "gatewayUrl" -o tsv)

# Test MCP tools/list endpoint
curl -X POST "${GATEWAY_URL}/<api-path>/mcp/tools/list" \
  -H "Content-Type: application/json" \
  -H "Ocp-Apim-Subscription-Key: <subscription-key>" \
  -d '{}'
```

### MCP Tool Definition Schema

When converting API operations to MCP tools, use this schema:

```json
{
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather for a location",
      "inputSchema": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name or coordinates"
          }
        },
        "required": ["location"]
      }
    }
  ]
}
```

### Reference

- [MCP Server Overview](https://learn.microsoft.com/en-us/azure/api-management/mcp-server-overview)
- [MCP from API Lab](https://github.com/Azure-Samples/AI-Gateway/tree/main/labs/mcp-from-api)

## Lab References (AI-Gateway Repo)

**Essential Labs to Get Started:**

| Scenario | Lab | Description |
|----------|-----|-------------|
| Semantic Caching | [semantic-caching](https://github.com/Azure-Samples/AI-Gateway/tree/main/labs/semantic-caching) | Cache similar prompts to reduce costs |
| Token Rate Limiting | [token-rate-limiting](https://github.com/Azure-Samples/AI-Gateway/tree/main/labs/token-rate-limiting) | Limit tokens per minute |
| Content Safety | [content-safety](https://github.com/Azure-Samples/AI-Gateway/tree/main/labs/content-safety) | Filter harmful content |
| Load Balancing | [backend-pool-load-balancing](https://github.com/Azure-Samples/AI-Gateway/tree/main/labs/backend-pool-load-balancing) | Distribute load across backends |
| MCP from API | [mcp-from-api](https://github.com/Azure-Samples/AI-Gateway/tree/main/labs/mcp-from-api) | Convert OpenAPI to MCP server |
| Zero to Production | [zero-to-production](https://github.com/Azure-Samples/AI-Gateway/tree/main/labs/zero-to-production) | Complete production setup guide |

**Find more labs at:** https://github.com/Azure-Samples/AI-Gateway/tree/main/labs

## Quick Start Checklist

### Prerequisites
- [ ] Azure subscription created
- [ ] Azure CLI installed and authenticated (`az login`)
- [ ] Resource group created for AI Gateway resources

### Deployment
- [ ] Deploy APIM with Basicv2 SKU
- [ ] Configure managed identity
- [ ] Add backend for Azure OpenAI or AI Foundry
- [ ] Apply policies (caching, rate limits, content safety)

### Verification
- [ ] Test API endpoint through gateway
- [ ] Verify token metrics in Application Insights
- [ ] Check rate limiting headers in response
- [ ] Validate content safety filtering

## Best Practices

| Practice | Description |
|----------|-------------|
| **Default to Basicv2** | Use Basicv2 SKU for cost/speed optimization |
| **Use managed identity** | Prefer managed identity over API keys for backend auth |
| **Enable token metrics** | Use `azure-openai-emit-token-metric` for cost tracking |
| **Semantic caching** | Cache similar prompts to reduce costs (60-80% savings possible) |
| **Rate limit by key** | Use subscription ID or IP for granular rate limiting |
| **Content safety** | Enable `shield-prompt` to detect jailbreak attempts |

## Troubleshooting

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Slow APIM creation** | Deployment takes 30+ minutes | Use Basicv2 SKU instead of Premium |
| **Token limit exceeded** | 429 response | Increase `tokens-per-minute` or add load balancing |
| **Cache not working** | No cache hits | Lower `score-threshold` (e.g., 0.7) |
| **Content blocked** | False positives | Increase category thresholds |
| **Backend auth fails** | 401 from Azure OpenAI | Assign Cognitive Services User role to APIM managed identity |
| **Rate limit too strict** | Legitimate requests blocked | Increase `calls` or `renewal-period` |

## SDK Quick References

- **Content Safety**: [Python](references/sdk/azure-ai-contentsafety-py.md) | [TypeScript](references/sdk/azure-ai-contentsafety-ts.md)
- **API Management**: [Python](references/sdk/azure-mgmt-apimanagement-py.md) | [.NET](references/sdk/azure-mgmt-apimanagement-dotnet.md)

## Additional Resources

- [Azure API Management Documentation](https://learn.microsoft.com/azure/api-management/)
- [AI Gateway Samples Repository](https://github.com/Azure-Samples/AI-Gateway)
- [APIM Policies Reference](https://learn.microsoft.com/azure/api-management/api-management-policies)
- [Azure OpenAI Integration](https://learn.microsoft.com/azure/api-management/azure-openai-api-from-specification)
