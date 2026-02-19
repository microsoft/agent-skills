# Azure Integrations for JavaScript/TypeScript

How to connect JS/TS apps to Azure services through Aspire's hosting integrations.

---

## Overview

Azure integrations are configured in the C# AppHost. JS/TS apps consume them via environment variables injected by `.WithReference()`. No Azure SDKs are needed in the AppHost — Aspire provisions and configures everything.

---

## Azure PostgreSQL

### AppHost

```csharp
#:package Aspire.Hosting.Azure.PostgreSQL@13.1.0

var postgres = builder.AddAzurePostgresFlexibleServer("postgres");
var db = postgres.AddDatabase("mydb");

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(db)
    .WaitFor(db);
```

### Run locally as container

```csharp
var postgres = builder.AddAzurePostgresFlexibleServer("postgres")
    .RunAsContainer();  // Uses docker.io/library/postgres locally
var db = postgres.AddDatabase("mydb");
```

### Node.js consumption

```javascript
const { Client } = require('pg');

const client = new Client({
    host: process.env.MYDB_HOST,
    port: parseInt(process.env.MYDB_PORT || '5432'),
    database: process.env.MYDB_DATABASENAME,
    // When using Azure Entra ID auth (default), no username/password needed
    // When using password auth:
    // user: process.env.MYDB_USERNAME,
    // password: process.env.MYDB_PASSWORD,
});

await client.connect();
```

**Injected variables:** `MYDB_HOST`, `MYDB_PORT`, `MYDB_URI`, `MYDB_DATABASENAME`, `MYDB_JDBCCONNECTIONSTRING`

---

## Azure Cache for Redis

### AppHost

```csharp
var cache = builder.AddAzureRedis("cache");

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(cache);
```

### Run locally as container

```csharp
var cache = builder.AddAzureRedis("cache")
    .RunAsContainer();  // Uses docker.io/library/redis locally
```

### Node.js consumption

```javascript
const redis = require('redis');

const client = redis.createClient({
    socket: {
        host: process.env.CACHE_HOST,
        port: parseInt(process.env.CACHE_PORT || '6379'),
    },
});

await client.connect();
```

**Injected variables:** `CACHE_HOST`, `CACHE_PORT`, `CACHE_URI`

---

## Non-Azure Redis (Container)

```csharp
var cache = builder.AddRedis("cache")
    .WithRedisInsight()    // Redis Insights UI
    .WithDataVolume();     // Persist data

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(cache);
```

Same environment variables as Azure Redis. Locally runs as container; publishes as Azure Container App with Redis image.

---

## Azure Storage (Blobs, Queues, Tables)

### AppHost

```csharp
#:package Aspire.Hosting.Azure.Storage@13.1.0

var storage = builder.AddAzureStorage("storage");
var blobs = storage.AddBlobs("blobs");
var queues = storage.AddQueues("queues");

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(blobs)
    .WithReference(queues);
```

### Run locally with Azurite emulator

```csharp
var storage = builder.AddAzureStorage("storage")
    .RunAsEmulator();  // Uses Azurite locally
```

### Node.js consumption

```javascript
const { BlobServiceClient } = require('@azure/storage-blob');

const connectionString = process.env.ConnectionStrings__blobs;
const blobService = BlobServiceClient.fromConnectionString(connectionString);
```

---

## Azure Service Bus

### AppHost

```csharp
#:package Aspire.Hosting.Azure.ServiceBus@13.1.0

var messaging = builder.AddAzureServiceBus("messaging");
messaging.AddQueue("orders");
messaging.AddTopic("notifications");

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(messaging);
```

### Run locally with emulator

```csharp
var messaging = builder.AddAzureServiceBus("messaging")
    .RunAsEmulator();
```

### Node.js consumption

```javascript
const { ServiceBusClient } = require('@azure/service-bus');

const connectionString = process.env.ConnectionStrings__messaging;
const sbClient = new ServiceBusClient(connectionString);
const sender = sbClient.createSender('orders');
```

---

## Azure Cosmos DB

### AppHost

```csharp
#:package Aspire.Hosting.Azure.CosmosDB@13.1.0

var cosmos = builder.AddAzureCosmosDB("cosmos");
var db = cosmos.AddCosmosDatabase("mydb");

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(db);
```

### Run locally with emulator

```csharp
var cosmos = builder.AddAzureCosmosDB("cosmos")
    .RunAsEmulator();
```

### Node.js consumption

```javascript
const { CosmosClient } = require('@azure/cosmos');

const connectionString = process.env.ConnectionStrings__mydb;
const client = new CosmosClient(connectionString);
```

---

## Azure AI Search

### AppHost

```csharp
#:package Aspire.Hosting.Azure.Search@13.1.0

var search = builder.AddAzureSearch("search");

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(search);
```

### Node.js consumption

```javascript
const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

const endpoint = process.env.SEARCH_URI;
const client = new SearchClient(endpoint, 'my-index', new AzureKeyCredential(apiKey));
```

---

## Azure Key Vault

### AppHost

```csharp
#:package Aspire.Hosting.Azure.KeyVault@13.1.0

var vault = builder.AddAzureKeyVault("secrets");

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(vault);
```

### Node.js consumption

```javascript
const { SecretClient } = require('@azure/keyvault-secrets');
const { DefaultAzureCredential } = require('@azure/identity');

const vaultUrl = process.env.ConnectionStrings__secrets;
const client = new SecretClient(vaultUrl, new DefaultAzureCredential());
```

---

## Keycloak (Identity)

### AppHost

```csharp
#:package Aspire.Hosting.Keycloak@13.1.0

var keycloak = builder.AddKeycloak("keycloak", 8080)
    .WithRealmImport("./Realms")
    .WithDataVolume();

var api = builder.AddNodeApp("api", "./api", "server.js")
    .WithNpm()
    .WithReference(keycloak)
    .WaitFor(keycloak);
```

### Node.js consumption

```javascript
const Keycloak = require('keycloak-connect');

// Aspire injects KEYCLOAK connection info
const keycloakConfig = {
    serverUrl: process.env.ConnectionStrings__keycloak,
    realm: 'my-realm',
    clientId: 'my-app',
};
```

---

## Existing Azure Resources

Reference pre-existing Azure resources without provisioning new ones:

```csharp
var existingDbName = builder.AddParameter("existingDbName");
var existingDbRg = builder.AddParameter("existingDbResourceGroup");

var postgres = builder.AddAzurePostgresFlexibleServer("postgres")
    .AsExisting(existingDbName, existingDbRg);

var db = postgres.AddDatabase("mydb");
```

---

## Local vs Production Behavior

| Integration | Local (aspire run) | Production (aspire deploy) |
|-------------|-------------------|---------------------------|
| `AddAzurePostgres().RunAsContainer()` | Docker container | Azure PostgreSQL Flexible Server |
| `AddAzureRedis().RunAsContainer()` | Docker container | Azure Cache for Redis |
| `AddAzureStorage().RunAsEmulator()` | Azurite container | Azure Storage Account |
| `AddAzureServiceBus().RunAsEmulator()` | Emulator container | Azure Service Bus |
| `AddRedis()` | Docker container | Azure Container App with Redis |
| `AddPostgres()` | Docker container | Azure Container App with PostgreSQL |
