# Authentication — Python SDK Quick Reference

> Condensed from **azure-identity-py**. Full patterns (async,
> ChainedTokenCredential, token caching, all credential types)
> in the **azure-identity-py** plugin skill if installed.

## Install
```bash
pip install azure-identity
```

## Quick Start
```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
```

## Best Practices
- Use DefaultAzureCredential for code that runs locally and in Azure
- Never hardcode credentials — use environment variables or managed identity
- Prefer managed identity in production Azure deployments
- Use ChainedTokenCredential when you need a custom credential order
- Close async credentials explicitly or use context managers
- Set AZURE_CLIENT_ID env var for user-assigned managed identities
- Exclude unused credentials to speed up authentication
