# Customize Workflow — Detailed Phase Instructions

> Reference for: `models/deploy-model/customize/SKILL.md`

## Phase 1: Verify Authentication

```bash
az account show --query "{Subscription:name, User:user.name}" -o table
```

If not logged in: `az login`

Set subscription if needed:
```bash
az account list --query "[].[name,id,state]" -o table
az account set --subscription <subscription-id>
```

---

## Phase 2: Get Project Resource ID

Check `PROJECT_RESOURCE_ID` env var. If not set, prompt user.

**Format:** `/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}`

---

## Phase 3: Parse and Verify Project

Parse ARM resource ID to extract components:

```powershell
$SUBSCRIPTION_ID = ($PROJECT_RESOURCE_ID -split '/')[2]
$RESOURCE_GROUP = ($PROJECT_RESOURCE_ID -split '/')[4]
$ACCOUNT_NAME = ($PROJECT_RESOURCE_ID -split '/')[8]
$PROJECT_NAME = ($PROJECT_RESOURCE_ID -split '/')[10]
```

Verify project exists and get region:
```bash
az account set --subscription $SUBSCRIPTION_ID
az cognitiveservices account show \
  --name $ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query location -o tsv
```

---

## Phase 4: Get Model Name

List available models if not provided:
```bash
az cognitiveservices account list-models \
  --name $ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[].name" -o json
```

Present sorted unique list. Allow custom model name entry.

---

## Phase 5: List and Select Model Version

```bash
az cognitiveservices account list-models \
  --name $ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[?name=='$MODEL_NAME'].version" -o json
```

Recommend latest version (first in list). Default to `"latest"` if no versions found.

---

## Phase 6: List and Select SKU

> ⚠️ **Warning:** Never hardcode SKU lists — always query live data.

**Step A — Query model-supported SKUs:**
```bash
az cognitiveservices model list \
  --location $PROJECT_REGION \
  --subscription $SUBSCRIPTION_ID -o json
```

Filter: `model.name == $MODEL_NAME && model.version == $MODEL_VERSION`, extract `model.skus[].name`.

**Step B — Check subscription quota per SKU:**
```bash
az cognitiveservices usage list \
  --location $PROJECT_REGION \
  --subscription $SUBSCRIPTION_ID -o json
```

Quota key pattern: `OpenAI.<SKU>.<model-name>`. Calculate `available = limit - currentValue`.

**Step C — Present only deployable SKUs** (available > 0). If no SKUs have quota, direct user to the [quota skill](../../../../quota/quota.md).

---

## Phase 7: Configure Capacity

**Query capacity via REST API:**
```bash
# Current region capacity
az rest --method GET --url \
  "https://management.azure.com/subscriptions/$SUBSCRIPTION_ID/providers/Microsoft.CognitiveServices/locations/$PROJECT_REGION/modelCapacities?api-version=2024-10-01&modelFormat=OpenAI&modelName=$MODEL_NAME&modelVersion=$MODEL_VERSION"
```

Filter result for `properties.skuName == $SELECTED_SKU`. Read `properties.availableCapacity`.

**Capacity defaults by SKU:**

| SKU | Unit | Min | Max | Step | Default |
|-----|------|-----|-----|------|---------|
| ProvisionedManaged | PTU | 50 | 1000 | 50 | 100 |
| Others (TPM-based) | TPM | 1000 | min(available, 300000) | 1000 | min(10000, available/2) |

Validate user input: must be >= min, <= max, multiple of step. On invalid input, explain constraints.

### Phase 7b: Cross-Region Fallback

If no capacity in current region, query ALL regions:
```bash
az rest --method GET --url \
  "https://management.azure.com/subscriptions/$SUBSCRIPTION_ID/providers/Microsoft.CognitiveServices/modelCapacities?api-version=2024-10-01&modelFormat=OpenAI&modelName=$MODEL_NAME&modelVersion=$MODEL_VERSION"
```

Filter: `properties.skuName == $SELECTED_SKU && properties.availableCapacity > 0`. Sort descending by capacity.

Present available regions. After user selects region, find existing projects there:
```bash
az cognitiveservices account list \
  --query "[?kind=='AIProject' && location=='$PROJECT_REGION'].{Name:name, ResourceGroup:resourceGroup}" \
  -o json
```

If projects exist, let user select one and update `$ACCOUNT_NAME`, `$RESOURCE_GROUP`. If none, direct to project/create skill.

Re-run capacity configuration with new region's available capacity.

If no region has capacity: fail with guidance to request quota increase, check existing deployments, or try different model/SKU.

---

## Phase 8: Select RAI Policy (Content Filter)

Present options:
1. `Microsoft.DefaultV2` — Balanced filtering (recommended). Filters hate, violence, sexual, self-harm.
2. `Microsoft.Prompt-Shield` — Enhanced prompt injection/jailbreak protection.
3. Custom policies — Organization-specific (configured in Azure Portal).

Default: `Microsoft.DefaultV2`.

---

## Phase 9: Configure Advanced Options

Options are SKU-dependent:

**A. Dynamic Quota** (GlobalStandard only)
- Auto-scales beyond base allocation when capacity available
- Default: enabled

**B. Priority Processing** (ProvisionedManaged only)
- Prioritizes requests during high load; additional charges apply
- Default: disabled

**C. Spillover** (any SKU)
- Redirects requests to backup deployment at capacity
- Requires existing deployment; list with:
```bash
az cognitiveservices account deployment list \
  --name $ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[].name" -o json
```
- Default: disabled

---

## Phase 10: Configure Version Upgrade Policy

| Policy | Description |
|--------|-------------|
| `OnceNewDefaultVersionAvailable` | Auto-upgrade to new default (Recommended) |
| `OnceCurrentVersionExpired` | Upgrade only when current expires |
| `NoAutoUpgrade` | Manual upgrade only |

Default: `OnceNewDefaultVersionAvailable`.

---

## Phase 11: Generate Deployment Name

List existing deployments to avoid conflicts:
```bash
az cognitiveservices account deployment list \
  --name $ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[].name" -o json
```

Auto-generate: use model name as base, append `-2`, `-3` etc. if taken. Allow custom override. Validate: `^[\w.-]{2,64}$`.

---

## Phase 12: Review Configuration

Display summary of all selections for user confirmation before proceeding:
- Model, version, deployment name
- SKU, capacity (with unit), region
- RAI policy, version upgrade policy
- Advanced options (dynamic quota, priority, spillover)
- Account, resource group, project

User confirms or cancels.

---

## Phase 13: Execute Deployment

**Create deployment:**
```bash
az cognitiveservices account deployment create \
  --name $ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --deployment-name $DEPLOYMENT_NAME \
  --model-name $MODEL_NAME \
  --model-version $MODEL_VERSION \
  --model-format "OpenAI" \
  --sku-name $SELECTED_SKU \
  --sku-capacity $DEPLOY_CAPACITY
```

**Check status:**
```bash
az cognitiveservices account deployment show \
  --name $ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --deployment-name $DEPLOYMENT_NAME \
  --query "properties.provisioningState" -o tsv
```

Poll until `Succeeded` or `Failed`. Timeout after 5 minutes.

**Get endpoint:**
```bash
az cognitiveservices account show \
  --name $ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.endpoint" -o tsv
```

On success, display deployment name, model, version, SKU, capacity, region, RAI policy, rate limits, endpoint, and Azure AI Foundry portal link.
