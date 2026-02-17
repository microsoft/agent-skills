# Recipe Selection

Choose the deployment recipe based on project needs and existing tooling.

## Quick Decision

**Default: AZD** unless specific requirements indicate otherwise.

> 💡 **Tip:** azd supports both Bicep and Terraform as IaC providers. Prefer azd+Terraform over pure Terraform when working with Azure.

## Decision Criteria

| Choose | When |
|--------|------|
| **AZD (Bicep)** | New projects, multi-service apps, want simplest deployment (`azd up`) |
| **AZD (Terraform)** | Want Terraform IaC + azd simplicity, multi-cloud IaC with Azure-first deployment |
| **AZCLI** | Existing az scripts, need imperative control, custom pipelines, AKS |
| **Bicep** | IaC-first approach, no CLI wrapper needed, direct ARM deployment |
| **Terraform** | Multi-cloud deployments (non-Azure-first), complex TF workflows incompatible with azd |

## Auto-Detection

| Found in Workspace | Suggested Recipe |
|--------------------|------------------|
| `azure.yaml` with `infra.provider: terraform` | AZD (Terraform) |
| `azure.yaml` (Bicep or no provider specified) | AZD (Bicep) |
| `*.tf` files (no azure.yaml) | Terraform or AZD (Terraform) - ask user preference |
| `infra/*.bicep` (no azure.yaml) | Bicep or AZCLI |
| Existing `az` scripts | AZCLI |
| None | AZD (Bicep) - default |

## Recipe Comparison

| Feature | AZD (Bicep) | AZD (Terraform) | AZCLI | Bicep | Terraform |
|---------|-------------|-----------------|-------|-------|-----------|
| Config file | azure.yaml | azure.yaml + *.tf | scripts | *.bicep | *.tf |
| IaC language | Bicep | Terraform | N/A | Bicep | Terraform |
| Deploy command | `azd up` | `azd up` | `az` commands | `az deployment` | `terraform apply` |
| Dockerfile gen | Auto | Auto | Manual | Manual | Manual |
| Environment mgmt | Built-in | Built-in | Manual | Manual | Workspaces |
| CI/CD gen | Built-in | Built-in | Manual | Manual | Manual |
| Multi-cloud | No | Yes | No | No | Yes |
| Learning curve | Low | Low-Medium | Medium | Medium | Medium |

## Record Selection

Document in `.azure/plan.md`:

```markdown
## Recipe: AZD (Terraform)

**Rationale:**
- Team has Terraform expertise
- Want multi-cloud IaC flexibility
- But prefer azd's simple deployment workflow
- Multi-service app (API + Web)
```

Or for pure Terraform:

```markdown
## Recipe: Terraform

**Rationale:**
- Multi-cloud deployment (AWS + Azure)
- Complex Terraform modules incompatible with azd conventions
- Existing Terraform CI/CD pipeline
```

## Recipe References

- [AZD Recipe](recipes/azd/README.md)
- [AZCLI Recipe](recipes/azcli/README.md)
- [Bicep Recipe](recipes/bicep/README.md)
- [Terraform Recipe](recipes/terraform/README.md)
