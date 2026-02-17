# MCP Server Templates

Templates for hosting MCP (Model Context Protocol) servers on Azure Functions.

**Indicators**: `mcp_tool_trigger`, `MCPTrigger`, `@app.mcp_tool`, project name contains "mcp"

## Standard MCP Templates

| Language | Template |
|----------|----------|
| Python | `azd init -t remote-mcp-functions-python` |
| TypeScript | `azd init -t remote-mcp-functions-typescript` |
| C# (.NET) | `azd init -t remote-mcp-functions-dotnet` |
| Java | `azd init -t remote-mcp-functions-java` |

## MCP + API Management (OAuth)

| Language | Template |
|----------|----------|
| Python | `azd init -t remote-mcp-apim-functions-python` |

## Self-Hosted MCP SDK

| Language | Template |
|----------|----------|
| Python | `azd init -t remote-mcp-sdk-functions-hosting-python` |
| TypeScript | `azd init -t remote-mcp-sdk-functions-hosting-node` |
| C# | `azd init -t remote-mcp-sdk-functions-hosting-dotnet` |
