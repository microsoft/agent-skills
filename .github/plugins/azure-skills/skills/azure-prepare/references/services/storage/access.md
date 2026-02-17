# Storage - Access Patterns

## Managed Identity Role Assignment

```bicep
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, principalId, 'Storage Blob Data Contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}
```

## Storage Roles

| Role | Permissions |
|------|-------------|
| Storage Blob Data Reader | Read blobs |
| Storage Blob Data Contributor | Read/write blobs |
| Storage Queue Data Contributor | Read/write queues |
| Storage Table Data Contributor | Read/write tables |

## SDK Connection Patterns

### Node.js

```javascript
const { BlobServiceClient } = require("@azure/storage-blob");

const blobServiceClient = BlobServiceClient.fromConnectionString(
  process.env.AZURE_STORAGE_CONNECTION_STRING
);
const containerClient = blobServiceClient.getContainerClient("uploads");
```

### Python

```python
from azure.storage.blob import BlobServiceClient

blob_service_client = BlobServiceClient.from_connection_string(
    os.environ["AZURE_STORAGE_CONNECTION_STRING"]
)
container_client = blob_service_client.get_container_client("uploads")
```

### .NET

```csharp
var blobServiceClient = new BlobServiceClient(
    Environment.GetEnvironmentVariable("AZURE_STORAGE_CONNECTION_STRING")
);
var containerClient = blobServiceClient.GetBlobContainerClient("uploads");
```

## Managed Identity Access

Use `DefaultAzureCredential` instead of connection strings:

```javascript
const { DefaultAzureCredential } = require("@azure/identity");
const { BlobServiceClient } = require("@azure/storage-blob");

const client = new BlobServiceClient(
  `https://${accountName}.blob.core.windows.net`,
  new DefaultAzureCredential()
);
```
