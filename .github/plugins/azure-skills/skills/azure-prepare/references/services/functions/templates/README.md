# Azure Functions Templates

AZD template selection for Azure Functions deployments.

## Template Selection

**Check integration indicators IN ORDER before defaulting to HTTP.**

| Priority | Integration | Indicators | Template |
|----------|-------------|------------|----------|
| 1 | MCP Server | `MCPTrigger`, `@app.mcp_tool`, "mcp" in name | [mcp.md](mcp.md) |
| 2 | Cosmos DB | `CosmosDBTrigger`, `@app.cosmos_db` | [Awesome AZD](https://azure.github.io/awesome-azd/?tags=functions&name=cosmos) |
| 3 | Azure SQL | `SqlTrigger`, `@app.sql` | [Awesome AZD](https://azure.github.io/awesome-azd/?tags=functions&name=sql) |
| 4 | AI/OpenAI | `openai`, `langchain`, `semantic_kernel` | [Awesome AZD](https://azure.github.io/awesome-azd/?tags=functions&name=ai) |
| 5 | SWA | `staticwebapp.config.json` | [integrations.md](integrations.md) |
| 6 | Service Bus | `ServiceBusTrigger` | [Flex Samples](https://github.com/Azure-Samples/azure-functions-flex-consumption-samples) |
| 7 | Durable | `DurableOrchestrationTrigger` | [Awesome AZD](https://azure.github.io/awesome-azd/?tags=functions&name=durable) |
| 8 | Event Hubs | `EventHubTrigger` | [Flex Samples](https://github.com/Azure-Samples/azure-functions-flex-consumption-samples) |
| 9 | Blob | `BlobTrigger` | [Awesome AZD](https://azure.github.io/awesome-azd/?tags=functions&name=blob) |
| 10 | Timer | `TimerTrigger`, `@app.schedule` | [Awesome AZD](https://azure.github.io/awesome-azd/?tags=functions&name=timer) |
| 11 | **HTTP (default)** | No specific indicators | [http.md](http.md) |

See [selection.md](selection.md) for detailed indicator patterns.

## Template Usage

```bash
# Non-interactive initialization (REQUIRED for agents)
ENV_NAME="$(basename "$PWD" | tr '[:upper:]' '[:lower:]' | tr ' _' '-')-dev"
azd init -t <TEMPLATE> -e "$ENV_NAME" --no-prompt
```

| Flag | Purpose |
|------|---------|
| `-e <name>` | Set environment name |
| `-t <template>` | Specify template |
| `--no-prompt` | Skip confirmations (required) |

## What azd Creates

- Flex Consumption plan (default)
- User-assigned managed identity
- RBAC role assignments (no connection strings)
- Storage with `allowSharedKeyAccess: false`
- App Insights with `disableLocalAuth: true`

## References

- [MCP Server Templates](mcp.md)
- [HTTP Templates](http.md)
- [Integration Templates](integrations.md)
- [Detailed Selection Tree](selection.md)

**Browse all:** [Awesome AZD Functions](https://azure.github.io/awesome-azd/?tags=functions)

