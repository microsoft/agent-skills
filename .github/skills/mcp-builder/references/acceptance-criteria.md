# MCP Server Builder Acceptance Criteria

**Skill**: `mcp-builder`
**Purpose**: Build high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services
**Focus**: Tool definitions, server structure, transport configuration, Python/Node/C# implementations

---

## 1. Server Initialization

### 1.1 ✅ CORRECT: Python FastMCP Server

```python
from mcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def get_data(query: str) -> str:
    """Fetch data based on query.
    
    Args:
        query: Search query string
    
    Returns:
        Matching data results
    """
    return f"Results for: {query}"

if __name__ == "__main__":
    mcp.run()
```

### 1.2 ✅ CORRECT: TypeScript MCP Server

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "my-server",
  version: "1.0.0",
});

server.registerTool({
  name: "get_data",
  description: "Fetch data based on query",
  inputSchema: {
    type: "object",
    properties: {
      query: { type: "string", description: "Search query" }
    },
    required: ["query"]
  },
  handler: async (params) => {
    return { content: [{ type: "text", text: `Results for: ${params.query}` }] };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### 1.3 ✅ CORRECT: C# MCP Server

```csharp
using Microsoft.Mcp.Core;
using Microsoft.Mcp.Server;

var builder = McpServerBuilder.Create("my-server", "1.0.0");

builder.AddTool("get_data", "Fetch data based on query", async (context) => {
    var query = context.GetParameter<string>("query");
    return new ToolResult($"Results for: {query}");
});

var server = builder.Build();
await server.RunAsync();
```

### 1.4 ❌ INCORRECT: Missing Server Name

```python
# WRONG - Server needs a name for identification
from mcp import FastMCP
mcp = FastMCP()  # Missing server name
```

---

## 2. Tool Definitions

### 2.1 ✅ CORRECT: Python Tool with Docstring

```python
@mcp.tool()
def search_documents(
    query: str,
    limit: int = 10,
    include_metadata: bool = False
) -> str:
    """Search for documents matching the query.
    
    Args:
        query: The search query string
        limit: Maximum number of results (default: 10)
        include_metadata: Whether to include document metadata
    
    Returns:
        JSON string with matching documents
    """
    results = perform_search(query, limit, include_metadata)
    return json.dumps(results)
```

### 2.2 ✅ CORRECT: TypeScript Tool with Schema

```typescript
server.registerTool({
  name: "search_documents",
  description: "Search for documents matching the query",
  inputSchema: {
    type: "object",
    properties: {
      query: { 
        type: "string", 
        description: "The search query string" 
      },
      limit: { 
        type: "integer", 
        description: "Maximum number of results",
        default: 10 
      },
      include_metadata: { 
        type: "boolean", 
        description: "Whether to include document metadata",
        default: false 
      }
    },
    required: ["query"]
  },
  handler: async (params) => {
    const results = await performSearch(params.query, params.limit, params.include_metadata);
    return { content: [{ type: "text", text: JSON.stringify(results) }] };
  }
});
```

### 2.3 ✅ CORRECT: Tool Annotations

```typescript
server.registerTool({
  name: "delete_item",
  description: "Delete an item by ID",
  annotations: {
    readOnlyHint: false,
    destructiveHint: true,
    idempotentHint: true,
    openWorldHint: false
  },
  inputSchema: {
    type: "object",
    properties: {
      item_id: { type: "string", description: "The item ID to delete" }
    },
    required: ["item_id"]
  },
  handler: async (params) => {
    await deleteItem(params.item_id);
    return { content: [{ type: "text", text: "Item deleted" }] };
  }
});
```

### 2.4 ❌ INCORRECT: Missing Tool Description

```python
# WRONG - No description for the tool
@mcp.tool()
def search(query: str) -> str:
    return do_search(query)
```

### 2.5 ❌ INCORRECT: Untyped Parameters

```python
# WRONG - Missing type hints
@mcp.tool()
def process_data(data):  # Should be: data: dict
    """Process input data."""
    return str(data)
```

---

## 3. Tool Naming Conventions

### 3.1 ✅ CORRECT: Consistent Prefixed Names

```python
@mcp.tool()
def github_create_issue(repo: str, title: str, body: str) -> str:
    """Create a GitHub issue."""
    pass

@mcp.tool()
def github_list_issues(repo: str, state: str = "open") -> str:
    """List GitHub issues."""
    pass

@mcp.tool()
def github_close_issue(repo: str, issue_number: int) -> str:
    """Close a GitHub issue."""
    pass
```

### 3.2 ❌ INCORRECT: Inconsistent Naming

```python
# WRONG - Inconsistent naming pattern
@mcp.tool()
def createIssue(repo: str, title: str) -> str:  # camelCase
    pass

@mcp.tool()
def list_github_issues(repo: str) -> str:  # Different prefix position
    pass

@mcp.tool()
def close(repo: str, issue: int) -> str:  # Too generic
    pass
```

---

## 4. Error Handling

### 4.1 ✅ CORRECT: Actionable Error Messages

```python
@mcp.tool()
def get_document(doc_id: str) -> str:
    """Retrieve a document by ID.
    
    Args:
        doc_id: The document identifier
    
    Returns:
        Document content as JSON
    """
    try:
        doc = fetch_document(doc_id)
        if doc is None:
            return json.dumps({
                "error": "Document not found",
                "suggestion": "Verify the document ID or list available documents with list_documents()"
            })
        return json.dumps(doc)
    except ConnectionError:
        return json.dumps({
            "error": "Unable to connect to document service",
            "suggestion": "Check network connectivity and try again"
        })
```

### 4.2 ❌ INCORRECT: Generic Error Messages

```python
# WRONG - Error doesn't help the agent recover
@mcp.tool()
def get_document(doc_id: str) -> str:
    """Get document."""
    try:
        return fetch_document(doc_id)
    except Exception as e:
        return "Error"  # Not actionable
```

---

## 5. Response Formatting

### 5.1 ✅ CORRECT: Structured JSON Response

```python
@mcp.tool()
def search_users(query: str) -> str:
    """Search for users by name or email.
    
    Args:
        query: Search query
    
    Returns:
        JSON with matching users
    """
    users = find_users(query)
    return json.dumps({
        "total": len(users),
        "results": [{"id": u.id, "name": u.name, "email": u.email} for u in users]
    })
```

### 5.2 ✅ CORRECT: Markdown for Human-Readable Output

```python
@mcp.tool()
def get_user_profile(user_id: str) -> str:
    """Get detailed user profile.
    
    Args:
        user_id: The user identifier
    
    Returns:
        Markdown formatted user profile
    """
    user = get_user(user_id)
    return f"""# {user.name}

**Email:** {user.email}
**Role:** {user.role}
**Joined:** {user.created_at}

## Recent Activity
{format_activity(user.recent_activity)}
"""
```

### 5.3 ❌ INCORRECT: Inconsistent Response Format

```python
# WRONG - Mixing formats, no structure
@mcp.tool()
def get_data(id: str) -> str:
    """Get data."""
    data = fetch(id)
    return str(data)  # Raw string, not structured
```

---

## 6. Resource Definitions

### 6.1 ✅ CORRECT: Python Resource

```python
@mcp.resource("config://settings")
def get_settings() -> str:
    """Server configuration settings."""
    return json.dumps({
        "api_version": "1.0",
        "features": ["search", "analytics"]
    })
```

### 6.2 ✅ CORRECT: TypeScript Resource

```typescript
server.registerResource({
  uri: "config://settings",
  name: "Settings",
  description: "Server configuration settings",
  mimeType: "application/json",
  handler: async () => {
    return {
      contents: [{
        uri: "config://settings",
        mimeType: "application/json",
        text: JSON.stringify({ api_version: "1.0" })
      }]
    };
  }
});
```

---

## 7. Transport Configuration

### 7.1 ✅ CORRECT: stdio Transport (Local)

```python
# For local/desktop use with stdio
if __name__ == "__main__":
    mcp.run()  # Defaults to stdio
```

### 7.2 ✅ CORRECT: HTTP Transport (Remote)

```python
# For remote/multi-tenant use
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

if __name__ == "__main__":
    mcp.run(transport="http", port=8080)
```

### 7.3 Transport Selection Guide

| Transport | Use Case | Characteristics |
|-----------|----------|-----------------|
| stdio | Local servers, desktop apps | Simple, single-user |
| HTTP | Remote servers, cloud | Scalable, requires auth |

---

## 8. Input Validation

### 8.1 ✅ CORRECT: Pydantic Validation (Python)

```python
from pydantic import BaseModel, Field

class SearchParams(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

@mcp.tool()
def search(params: SearchParams) -> str:
    """Search with validated parameters."""
    return perform_search(params.query, params.limit, params.offset)
```

### 8.2 ✅ CORRECT: Zod Validation (TypeScript)

```typescript
import { z } from "zod";

const SearchParamsSchema = z.object({
  query: z.string().min(1).max(500),
  limit: z.number().int().min(1).max(100).default(10),
  offset: z.number().int().min(0).default(0)
});

server.registerTool({
  name: "search",
  inputSchema: SearchParamsSchema,
  handler: async (params) => {
    // params are validated
    return performSearch(params.query, params.limit, params.offset);
  }
});
```

---

## 9. Async Patterns

### 9.1 ✅ CORRECT: Async Tool Handler

```python
@mcp.tool()
async def fetch_data(url: str) -> str:
    """Fetch data from URL asynchronously.
    
    Args:
        url: The URL to fetch
    
    Returns:
        Response content
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

### 9.2 ❌ INCORRECT: Blocking in Async Context

```python
# WRONG - Using sync requests in async tool
@mcp.tool()
async def fetch_data(url: str) -> str:
    """Fetch data."""
    import requests
    return requests.get(url).text  # Blocks event loop
```

---

## 10. Project Structure

### 10.1 ✅ CORRECT: Python MCP Server Structure

```
my-mcp-server/
├── pyproject.toml
├── src/
│   └── my_mcp_server/
│       ├── __init__.py
│       ├── server.py      # Server initialization
│       ├── tools/         # Tool implementations
│       │   ├── __init__.py
│       │   ├── search.py
│       │   └── crud.py
│       └── utils/         # Shared utilities
│           ├── __init__.py
│           └── api_client.py
└── tests/
    └── test_tools.py
```

### 10.2 ✅ CORRECT: TypeScript MCP Server Structure

```
my-mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts          # Server entry point
│   ├── tools/            # Tool implementations
│   │   ├── search.ts
│   │   └── crud.ts
│   └── utils/            # Shared utilities
│       └── api-client.ts
└── tests/
    └── tools.test.ts
```

---

## 11. Anti-Patterns Summary

| Anti-Pattern | Impact | Fix |
|--------------|--------|-----|
| Missing tool descriptions | Agent can't discover capabilities | Add docstrings/descriptions |
| Untyped parameters | Validation fails, agent errors | Add type hints everywhere |
| Generic error messages | Agent can't recover | Include actionable suggestions |
| Inconsistent naming | Tool discovery confusion | Use `{service}_{action}` pattern |
| Blocking I/O in async | Performance degradation | Use async/await throughout |
| Missing server name | Client can't identify server | Always provide server name |

---

## 12. Checklist for MCP Server

- [ ] Server has descriptive name and version
- [ ] All tools have clear descriptions
- [ ] All parameters have type hints
- [ ] Tool names follow `{service}_{action}` convention
- [ ] Error messages include actionable suggestions
- [ ] Responses use consistent format (JSON or Markdown)
- [ ] Async operations use proper async/await
- [ ] Input validation with Pydantic (Python) or Zod (TypeScript)
- [ ] Tool annotations specify readOnly/destructive hints
- [ ] Transport selected based on use case (stdio vs HTTP)
