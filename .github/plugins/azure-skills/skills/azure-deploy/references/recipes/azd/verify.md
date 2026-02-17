# AZD Verification

```bash
azd show
```

Expected output:
```
Showing deployed resources:
  Resource Group: rg-myapp-dev
  Services:
    api - Endpoint: https://api-xxxx.azurecontainerapps.io
```

## Health Check

```bash
curl -s https://<endpoint>/health | jq .
```

Expected: HTTP 200 response.
