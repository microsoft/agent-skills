# Azure Functions

Serverless compute for event-driven workloads, APIs, and scheduled tasks.

## When to Use

- Event-driven workloads
- Scheduled tasks (cron jobs)
- HTTP APIs with variable traffic
- Message/queue processing
- Real-time file processing
- MCP servers for AI agents
- Real-time streaming and event processing
- Orchestrations and workflows (Durable Functions)

## Service Type in azure.yaml

```yaml
services:
  my-function:
    host: function
    project: ./src/my-function
```

## Required Supporting Resources

| Resource | Purpose |
|----------|---------|
| Storage Account | Function runtime state |
| App Service Plan | Hosting (Consumption or Premium) |
| Application Insights | Monitoring |

## Hosting Plans

**Use Flex Consumption for new deployments** (all AZD templates default to Flex).

| Plan | Use Case | Scaling | VNET |
|------|----------|---------|------|
| **Flex Consumption** ⭐ | Default for new projects | Auto, pay-per-execution | ✅ |
| Consumption (Y1) | Variable workloads, cost optimization | Auto, scale to zero | ❌ |
| Premium (EP1-EP3) | No cold starts, longer execution | Auto, min instances | ✅ |
| Dedicated | Predictable load, existing App Service | Manual or auto | ✅ |

## Runtime Stacks

| Language | FUNCTIONS_WORKER_RUNTIME | linuxFxVersion |
|----------|-------------------------|----------------|
| Node.js | `node` | `Node\|18` |
| Python | `python` | `Python\|3.11` |
| .NET | `dotnet` | `DOTNET\|8.0` |
| Java | `java` | `Java\|17` |

## References

- [AZD Templates](templates/README.md)
- [Bicep Patterns](bicep.md)
- [Trigger Types](triggers.md)
- [Durable Functions](durable.md)
