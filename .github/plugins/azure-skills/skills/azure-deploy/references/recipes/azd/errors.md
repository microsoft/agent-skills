# AZD Errors

## Deployment Runtime Errors

These errors occur **during** `azd up` execution:

| Error | Cause | Resolution |
|-------|-------|------------|
| `unknown flag: --location` | `azd up` doesn't accept `--location` | Use `azd env set AZURE_LOCATION <region>` before `azd up` |
| Provision failed | Bicep template errors | Check detailed error in output |
| Deploy failed | Build or Docker errors | Check build logs |
| Package failed | Missing Dockerfile or deps | Verify Dockerfile exists and dependencies |
| Quota exceeded | Subscription limits | Request increase or change region |

> ℹ️ **Pre-flight validation**: Run `azure-validate` before deployment to catch configuration errors early. See [Pre-Deploy Checklist](../../pre-deploy-checklist.md).

## Retry

After fixing the issue:
```bash
azd up --no-prompt
```

## Cleanup (DESTRUCTIVE)

```bash
azd down --force --purge
```

⚠️ Permanently deletes ALL resources including databases and Key Vaults.
