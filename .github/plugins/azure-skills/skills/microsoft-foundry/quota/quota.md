# Microsoft Foundry Quota Management

Quota and capacity management for Microsoft Foundry. Quotas are **subscription + region** level.

> **Agent Rule:** Query REGIONAL quota summary, NOT individual resources. Don't run `az cognitiveservices account list` for quota queries.

## Quota Types

| Type | Description |
|------|-------------|
| **TPM** | Tokens Per Minute, pay-per-token, subject to rate limits |
| **PTU** | Provisioned Throughput Units, monthly commitment, no rate limits |
| **Region** | Max capacity per region, shared across subscription |
| **Slots** | 10-20 deployment slots per resource |

**When to use PTU:** Consistent high-volume production workloads where monthly commitment is cost-effective.

## Core Workflows

### 1. Check Regional Quota

**Command Pattern:** "Show my Microsoft Foundry quota usage"

```bash
subId=$(az account show --query id -o tsv)
az rest --method get \
  --url "https://management.azure.com/subscriptions/$subId/providers/Microsoft.CognitiveServices/locations/eastus/usages?api-version=2023-05-01" \
  --query "value[?contains(name.value,'OpenAI')].{Model:name.value, Used:currentValue, Limit:limit}" -o table
```

Change region as needed: `eastus`, `eastus2`, `westus`, `westus2`, `swedencentral`, `uksouth`.

See [Detailed Workflow Steps](./references/workflows.md) for complete instructions including multi-region checks and resource-specific queries.

---

### 2. Find Best Region for Deployment

**Command Pattern:** "Which region has available quota for GPT-4o?"

Check specific regions one at a time:

```bash
subId=$(az account show --query id -o tsv)
region="eastus"
az rest --method get \
  --url "https://management.azure.com/subscriptions/$subId/providers/Microsoft.CognitiveServices/locations/$region/usages?api-version=2023-05-01" \
  --query "value[?name.value=='OpenAI.Standard.gpt-4o'].{Model:name.value, Used:currentValue, Limit:limit, Available:(limit-currentValue)}" -o table
```

See [Detailed Workflow Steps](./references/workflows.md) for multi-region comparison.

---

### 3. Deploy with PTU

**Command Pattern:** "Deploy GPT-4o with PTU"

Use Foundry Portal capacity calculator first, then deploy:

```bash
az cognitiveservices account deployment create --name <resource> --resource-group <rg> \
  --deployment-name gpt-4o-ptu --model-name gpt-4o --model-version "2024-05-13" \
  --model-format OpenAI --sku-name ProvisionedManaged --sku-capacity 100
```

See [PTU Guide](./references/ptu-guide.md) for capacity planning and when to use PTU.

---

### 4. Delete Deployment (Free Quota)

**Command Pattern:** "Delete unused deployment to free quota"

```bash
az cognitiveservices account deployment delete --name <resource> --resource-group <rg> \
  --deployment-name <deployment>
```

---

## Troubleshooting

| Error | Quick Fix |
|-------|-----------|
| `QuotaExceeded` | Delete unused deployments or request increase |
| `InsufficientQuota` | Reduce capacity or try different region |
| `DeploymentLimitReached` | Delete unused deployments |
| `429 Rate Limit` | Increase TPM or migrate to PTU |

See [Troubleshooting Guide](./references/troubleshooting.md) for detailed error resolution steps.

---

## Request Quota Increase

Azure Portal → Foundry resource → **Quotas** → **Request quota increase**. Include business justification. Processing: 1-2 days.

---

## References

- [Detailed Workflows](./references/workflows.md) - Complete workflow steps and multi-region checks
- [PTU Guide](./references/ptu-guide.md) - Provisioned throughput capacity planning
- [Troubleshooting](./references/troubleshooting.md) - Error resolution and diagnostics
- [Quota Management](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota)
- [Rate Limits](https://learn.microsoft.com/azure/ai-services/openai/quotas-limits)
