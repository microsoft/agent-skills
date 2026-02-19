# Connections Reference

Working with Azure AI Foundry project connections to access linked Azure resources.

## Overview

Connections represent linked Azure resources (Azure OpenAI, AI Search, Storage, etc.) configured in your Foundry project. The SDK provides methods to list, retrieve, and access credentials for these connections.

## Connection Types

| Type | Description | Use Case |
|------|-------------|----------|
| `AzureOpenAI` | Azure OpenAI Service | Chat completions, embeddings |
| `AzureAISearch` | Azure AI Search | Vector search, RAG |
| `AzureBlob` | Blob Storage | File storage for agents |
| `AzureAIServices` | Cognitive Services | Speech, Vision, etc. |
| `Custom` | Custom connections | External APIs |

## List Connections

```typescript
import { AIProjectClient } from "@azure/ai-projects";
import { DefaultAzureCredential } from "@azure/identity";

const client = new AIProjectClient(
  process.env.AZURE_AI_PROJECT_ENDPOINT!,
  new DefaultAzureCredential()
);

// List all connections
for await (const connection of client.connections.list()) {
  console.log(`Name: ${connection.name}`);
  console.log(`Type: ${connection.type}`);
  console.log(`---`);
}

// Filter by category
for await (const conn of client.connections.list({ 
  category: "AzureOpenAI" 
})) {
  console.log(`OpenAI Connection: ${conn.name}`);
}
```

## Get Connection by Name

```typescript
// Get connection metadata (no credentials)
const connection = await client.connections.get("my-openai-connection");
console.log(`Endpoint: ${connection.target}`);
console.log(`Type: ${connection.type}`);

// Get connection with credentials
const connWithCreds = await client.connections.getWithCredentials(
  "my-openai-connection"
);

// Access credentials based on auth type
if (connWithCreds.credentials.type === "ApiKey") {
  console.log(`API Key: ${connWithCreds.credentials.key}`);
} else if (connWithCreds.credentials.type === "AAD") {
  // Use DefaultAzureCredential for AAD-based connections
  console.log("Uses Entra ID authentication");
}
```

## Get Default Connection

```typescript
// Get default connection of a specific type
const defaultOpenAI = await client.connections.getDefault(
  "AzureOpenAI",
  true // withCredentials
);

const defaultSearch = await client.connections.getDefault(
  "AzureAISearch",
  true
);

// Use the connection endpoint
console.log(`OpenAI Endpoint: ${defaultOpenAI.target}`);
console.log(`Search Endpoint: ${defaultSearch.target}`);
```

## Connection Interface

```typescript
interface Connection {
  /** Connection name */
  name: string;
  
  /** Connection type (e.g., "AzureOpenAI", "AzureAISearch") */
  type: string;
  
  /** Target endpoint URL */
  target: string;
  
  /** Authentication type */
  authType: "ApiKey" | "AAD" | "SAS" | "CustomKeys";
  
  /** Additional metadata */
  metadata?: Record<string, string>;
}

interface ConnectionWithCredentials extends Connection {
  credentials: ApiKeyCredentials | AADCredentials | SASCredentials;
}

interface ApiKeyCredentials {
  type: "ApiKey";
  key: string;
}

interface AADCredentials {
  type: "AAD";
  // Use DefaultAzureCredential to get tokens
}
```

## Using Connections with Agents

```typescript
// Get Search connection for agent tool
const searchConn = await client.connections.getWithCredentials("my-search");

// Create agent with Azure AI Search tool
const agent = await client.agents.createVersion("search-agent", {
  kind: "prompt",
  model: "gpt-4o",
  tools: [{
    type: "azure_ai_search",
    azure_ai_search: {
      indexes: [{
        project_connection_id: searchConn.name,
        index_name: "my-index",
        query_type: "vector_semantic_hybrid"
      }]
    }
  }]
});
```

## Using Connections for Direct SDK Access

```typescript
// Get Azure OpenAI connection
const openAIConn = await client.connections.getWithCredentials("my-openai");

// Create Azure OpenAI client directly
import { AzureOpenAI } from "openai";

const openAIClient = new AzureOpenAI({
  endpoint: openAIConn.target,
  apiKey: openAIConn.credentials.type === "ApiKey" 
    ? openAIConn.credentials.key 
    : undefined,
  // Or use credential for AAD
  azureADTokenProvider: openAIConn.credentials.type === "AAD"
    ? () => getAccessToken() 
    : undefined,
});

// Get AI Search connection
const searchConn = await client.connections.getWithCredentials("my-search");

// Create Search client directly
import { SearchClient, AzureKeyCredential } from "@azure/search-documents";

const searchClient = new SearchClient(
  searchConn.target,
  "my-index",
  new AzureKeyCredential(searchConn.credentials.key)
);
```

## Error Handling

```typescript
import { RestError } from "@azure/core-rest-pipeline";

try {
  const conn = await client.connections.get("non-existent");
} catch (error) {
  if (error instanceof RestError) {
    if (error.statusCode === 404) {
      console.log("Connection not found");
    } else if (error.statusCode === 403) {
      console.log("Not authorized to access connection");
    }
  }
  throw error;
}
```

## Best Practices

1. **Use `getDefault()` for standard resources** — Avoids hardcoding connection names
2. **Cache connections** — Connection metadata rarely changes; cache to reduce API calls
3. **Use AAD when possible** — Prefer `AAD` auth over `ApiKey` for better security
4. **Never log credentials** — Avoid logging `getWithCredentials()` responses
5. **Validate connection type** — Check `type` before casting credentials

## See Also

- [AIProjectClient Reference](../SKILL.md)
- [Agents with Tools](../../agents/references/tools.md)
- [Azure OpenAI Integration](https://learn.microsoft.com/azure/ai-services/openai/)
