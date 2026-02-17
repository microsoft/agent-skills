# Terraform Recipe

Terraform workflow for Azure deployments.

> 💡 **Consider azd+Terraform:** If you're primarily deploying to Azure and want a simpler workflow, consider using [azd with Terraform](../azd/terraform.md) instead. You get Terraform's IaC with azd's deployment convenience.

## When to Use Pure Terraform

- Multi-cloud deployments (non-Azure-first)
- Complex Terraform modules/workspaces incompatible with azd
- Existing Terraform CI/CD that's hard to migrate
- Organization mandate for pure Terraform workflow

## When to Use azd+Terraform Instead

- Azure-first deployment (even if multi-cloud IaC)
- Want `azd up` simplicity with Terraform IaC
- Multi-service apps needing orchestration
- Team new to Terraform but wants to learn it

→ See [azd+Terraform documentation](../azd/terraform.md)

## Before Generation

**REQUIRED: Research best practices before generating any files.**

| Artifact | Research Action |
|----------|-----------------|
| Terraform patterns | Call `mcp_azure_mcp_azureterraformbestpractices` |
| Azure best practices | Call `mcp_azure_mcp_get_bestpractices` |

## Generation Steps

### 1. Generate Infrastructure

Create Terraform files in `./infra/`.

→ [patterns.md](patterns.md)

**Structure:**
```
infra/
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
├── backend.tf
└── modules/
    └── ...
```

### 2. Set Up State Backend

Azure Storage for remote state.

### 3. Generate Dockerfiles (if containerized)

Manual Dockerfile creation required.

## Output Checklist

| Artifact | Path |
|----------|------|
| Main config | `./infra/main.tf` |
| Variables | `./infra/variables.tf` |
| Outputs | `./infra/outputs.tf` |
| Values | `./infra/terraform.tfvars` |
| Backend | `./infra/backend.tf` |
| Modules | `./infra/modules/` |
| Dockerfiles | `src/<service>/Dockerfile` |

## References

- [Terraform Patterns](patterns.md)

## Next

→ Update `.azure/plan.md` → **azure-validate**
