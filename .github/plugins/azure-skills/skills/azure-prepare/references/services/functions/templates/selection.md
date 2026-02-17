# Template Selection Decision Tree

**CRITICAL**: Check for specific integration indicators IN ORDER before defaulting to HTTP.

Cross-reference with [top Azure Functions scenarios](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scenarios) and [official AZD gallery templates](https://azure.github.io/awesome-azd/?tags=msft&tags=functions).

```
1. Is this an MCP server?
   Indicators: mcp_tool_trigger, MCPTrigger, @app.mcp_tool, "mcp" in project name
   └─► YES → Use MCP Template

2. Does it use Cosmos DB?
   Indicators: CosmosDBTrigger, @app.cosmos_db, cosmos_db_input, cosmos_db_output
   └─► YES → Use Cosmos DB Template

3. Does it use Azure SQL?
   Indicators: SqlTrigger, @app.sql, sql_input, sql_output, SqlInput, SqlOutput
   └─► YES → Use SQL Template

4. Does it use AI/OpenAI?
   Indicators: openai, AzureOpenAI, azure-ai-openai, langchain, langgraph,
               semantic_kernel, Microsoft.Agents, azure-ai-projects,
               CognitiveServices, text_completion, embeddings_input,
               ChatCompletions, azure.ai.inference, @azure/openai
   └─► YES → Use AI Template

5. Is it a full-stack app with SWA?
   Indicators: staticwebapp.config.json, swa-cli, @azure/static-web-apps
   └─► YES → Use SWA+Functions Template

6. Does it use Service Bus?
   Indicators: ServiceBusTrigger, @app.service_bus_queue, @app.service_bus_topic
   └─► YES → Use Service Bus Template

7. Is it for orchestration or workflows?
   Indicators: DurableOrchestrationTrigger, orchestrator, durable_functions
   └─► YES → Use Durable Functions Template

8. Does it use Event Hubs?
   Indicators: EventHubTrigger, @app.event_hub, event_hub_output
   └─► YES → Use Event Hubs Template

9. Does it use Event Grid?
   Indicators: EventGridTrigger, @app.event_grid, event_grid_output
   └─► YES → Use Event Grid Template

10. Is it for file processing with Blob Storage?
    Indicators: BlobTrigger, @app.blob, blob_input, blob_output
    └─► YES → Use Blob Template

11. Is it for scheduled tasks?
    Indicators: TimerTrigger, @app.schedule, cron, scheduled task
    └─► YES → Use Timer Template

12. DEFAULT → Use HTTP Template by runtime
```
