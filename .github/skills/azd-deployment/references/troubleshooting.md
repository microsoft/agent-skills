# Azure Developer CLI (azd) Troubleshooting Guide

## Table of Contents

1. [Build Failures](#build-failures)
2. [Deployment Failures](#deployment-failures)
3. [Environment Configuration](#environment-configuration)
4. [Container App Issues](#container-app-issues)
5. [Networking Issues](#networking-issues)
6. [RBAC and Permissions](#rbac-and-permissions)

---

## Build Failures

### Remote Build Fails - "Cannot find Dockerfile"

**Symptom:**
```
Error: cannot find Dockerfile at ./Dockerfile
```

**Solution:** Ensure `docker.path` is relative to `project` path:
```yaml
services:
  backend:
    project: ./src/backend
    docker:
      path: ./Dockerfile      # Relative to ./src/backend
      context: .              # Build context is ./src/backend
```

### ARM64 Build on x86 Failure

**Symptom:**
```
exec format error
```

**Solution:** Use remote builds (executed on Azure's x86 infrastructure):
```yaml
services:
  backend:
    docker:
      remoteBuild: true    # Always use for M1/M2 Macs
```

### ACR Push Fails - "Unauthorized"

**Symptom:**
```
denied: requested access to the resource is denied
```

**Solutions:**
1. Verify ACR admin credentials enabled:
   ```bicep
   properties: {
     adminUserEnabled: true
   }
   ```

2. Re-authenticate:
   ```bash
   azd auth login
   az acr login --name <acr-name>
   ```

---

## Deployment Failures

### Service Not Found After Deploy

**Symptom:** `azd deploy` succeeds but service not updated

**Solution:** Ensure `azd-service-name` tag matches azure.yaml service name:
```bicep
tags: union(tags, { 'azd-service-name': 'backend' })  // Must match
```

```yaml
services:
  backend:   # This name must match the tag
    project: ./src/backend
```

### Provision Completes but Deploy Fails

**Symptom:**
```
Error: could not find container app for service 'frontend'
```

**Solution:** Run provision again to create the Container Apps:
```bash
azd provision
azd deploy
```

Or run both:
```bash
azd up
```

### Hook Script Fails

**Symptom:**
```
Error: hook 'postprovision' failed with exit code 1
```

**Solutions:**
1. Add error handling to hooks:
   ```yaml
   hooks:
     postprovision:
       shell: sh
       run: |
         set -e  # Exit on error (optional)
         az role assignment create ... 2>/dev/null || true  # Ignore "exists" errors
   ```

2. Debug by running hook commands manually

---

## Environment Configuration

### Environment Variable Not Available in Container

**Symptom:** App can't read expected environment variable

**Diagnosis:**
```bash
# Check what's in .azure/<env>/.env
azd env get-values

# Check container app env vars
az containerapp show -n <app-name> -g <rg> \
  --query "properties.template.containers[0].env"
```

**Solutions:**

1. **Variable not in parameters.json:**
   ```json
   {
     "parameters": {
       "myVar": { "value": "${MY_VAR}" }
     }
   }
   ```

2. **Variable not passed to Bicep:**
   ```bicep
   param myVar string = ''
   
   env: [
     { name: 'MY_VAR', value: myVar }
   ]
   ```

3. **Variable not set in environment:**
   ```bash
   azd env set MY_VAR "value"
   ```

### Resetting an Environment

```bash
# Delete and recreate
azd env delete <env-name>
azd env new <env-name>

# Or manually clear
rm -rf .azure/<env-name>
```

---

## Container App Issues

### Container Keeps Restarting

**Symptom:** Container in restart loop, never healthy

**Diagnosis:**
```bash
# Check logs
az containerapp logs show -n <app> -g <rg> --type system
az containerapp logs show -n <app> -g <rg> --type console
```

**Common Causes:**

1. **Health check failing:**
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
     CMD curl -f http://localhost:8000/health || exit 1
   ```

2. **Missing environment variable:**
   - App crashes on startup due to missing config
   - Check env vars passed in Bicep

3. **Port mismatch:**
   ```bicep
   targetPort: 8000  // Must match Dockerfile EXPOSE and app listen port
   ```

### Custom Domain Lost After Redeploy

**Symptom:** Custom domain configured in Portal disappears after `azd up`

**Solution:** Set `customDomains` to `null` in Bicep to preserve:
```bicep
configuration: {
  ingress: {
    customDomains: empty(customDomainsParam) ? null : customDomainsParam
  }
}
```

And save/restore in hooks (see azure.yaml patterns).

### Scaling Not Working

**Symptom:** App doesn't scale despite load

**Solution:** Verify scale rules:
```bicep
scale: {
  minReplicas: 1
  maxReplicas: 10
  rules: [
    {
      name: 'http-scale-rule'
      http: {
        metadata: { concurrentRequests: '100' }
      }
    }
  ]
}
```

---

## Networking Issues

### Frontend Can't Reach Backend

**Symptom:** 502/504 errors on /api calls

**Diagnosis:**
```bash
# Check backend is running
az containerapp show -n <backend> -g <rg> \
  --query "properties.runningStatus"

# Check internal URL
az containerapp show -n <backend> -g <rg> \
  --query "properties.configuration.ingress.fqdn"
```

**Solutions:**

1. **Use internal HTTP, not HTTPS:**
   ```bicep
   env: [
     { name: 'BACKEND_URL', value: 'http://ca-backend-${token}' }  // HTTP!
   ]
   ```

2. **Verify same Container Apps environment:**
   ```bicep
   // Both must use same environment
   containerAppsEnvironmentId: containerAppsEnvironment.outputs.id
   ```

3. **Check nginx proxy config:**
   ```nginx
   location /api {
       proxy_pass $BACKEND_URL;
       proxy_set_header Host $proxy_host;  // Important for internal routing
   }
   ```

### CORS Errors

**Symptom:** Browser blocks cross-origin requests

**Solution:** Set CORS in backend env:
```bicep
env: [
  { name: 'CORS_ORIGINS', value: '*' }  // Or specific origins in production
]
```

---

## RBAC and Permissions

### Role Assignment Fails in Hook

**Symptom:**
```
The role assignment already exists
```

**Solution:** Suppress error:
```yaml
hooks:
  postprovision:
    run: |
      az role assignment create ... 2>/dev/null || true
```

### Backend Can't Access Azure OpenAI

**Symptom:**
```
AuthenticationError: DefaultAzureCredential failed
```

**Diagnosis:**
```bash
# Check managed identity exists
az containerapp show -n <app> -g <rg> \
  --query "identity.principalId"

# Check role assignments
az role assignment list --assignee <principal-id>
```

**Solution:** Assign role in postprovision hook:
```yaml
postprovision:
  run: |
    az role assignment create \
      --assignee-object-id "${BACKEND_PRINCIPAL_ID}" \
      --assignee-principal-type ServicePrincipal \
      --role "Cognitive Services OpenAI User" \
      --scope "$OPENAI_RESOURCE_ID"
```

### Getting Resource IDs for RBAC

```bash
# Azure OpenAI
OPENAI_ID=$(az cognitiveservices account list \
  --query "[?name=='$OPENAI_NAME'].id" -o tsv)

# Azure AI Search
SEARCH_ID=$(az resource list \
  --resource-type "Microsoft.Search/searchServices" \
  --query "[?name=='$SEARCH_NAME'].id" -o tsv)
```

---

## Common Commands for Debugging

```bash
# Show project state
azd show

# Stream container logs
az containerapp logs show -n <app> -g <rg> --follow

# Check deployment status
az containerapp revision list -n <app> -g <rg> \
  --query "[].{name:name, active:active, traffic:trafficWeight}"

# Get container app URL
az containerapp show -n <app> -g <rg> --query "properties.configuration.ingress.fqdn"

# List all env vars
azd env get-values

# Manual deploy single service
azd deploy --service backend

# Verbose output
azd up --debug
```
