# MCP Builder Acceptance Criteria

**Tool**: Model Context Protocol (MCP) Server Development
**Specification**: https://modelcontextprotocol.io
**Purpose**: Skill testing acceptance criteria for validating MCP server implementations

---

## 1. Project Structure

### 1.1 TypeScript Project

#### ✅ CORRECT: Standard TypeScript MCP structure
```
my-mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts           # Main entry point
│   ├── tools/             # Tool implementations
│   │   ├── index.ts
│   │   └── my-tool.ts
│   └── utils/             # Shared utilities
│       └── api-client.ts
└── README.md
```

### 1.2 Python Project

#### ✅ CORRECT: Standard Python MCP structure
```
my-mcp-server/
├── pyproject.toml
├── src/
│   └── my_mcp_server/
│       ├── __init__.py
│       ├── __main__.py    # Entry point
│       ├── server.py      # MCP server setup
│       └── tools/
│           └── my_tool.py
└── README.md
```

---

## 2. Tool Definition

### 2.1 TypeScript Tool

#### ✅ CORRECT: Proper tool definition with Zod schema
```typescript
import { z } from "zod";

const GetUserSchema = z.object({
  userId: z.string().describe("The unique identifier of the user"),
  includeDetails: z.boolean().optional().describe("Include extended details")
});

server.tool(
  "get_user",
  "Retrieves user information by ID",
  GetUserSchema,
  async ({ userId, includeDetails }) => {
    // Implementation
    return {
      content: [{ type: "text", text: JSON.stringify(user) }]
    };
  }
);
```

#### ❌ INCORRECT: Missing schema or description
```typescript
server.tool("get_user", async (args) => {
  // No schema, no description
});
```

### 2.2 Python Tool

#### ✅ CORRECT: FastMCP tool definition
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def get_user(
    user_id: str,
    include_details: bool = False
) -> str:
    """Retrieves user information by ID.
    
    Args:
        user_id: The unique identifier of the user
        include_details: Include extended details (default: False)
    """
    user = await fetch_user(user_id)
    return json.dumps(user)
```

#### ❌ INCORRECT: Missing docstring
```python
@mcp.tool()
async def get_user(user_id: str) -> str:
    # No docstring - tool description will be empty
    return fetch_user(user_id)
```

---

## 3. Input Validation

### 3.1 TypeScript with Zod

#### ✅ CORRECT: Comprehensive validation
```typescript
const CreateIssueSchema = z.object({
  title: z.string().min(1).max(256).describe("Issue title"),
  body: z.string().optional().describe("Issue body in markdown"),
  labels: z.array(z.string()).optional().describe("Labels to apply"),
  assignees: z.array(z.string()).optional().describe("GitHub usernames")
});
```

### 3.2 Python with Pydantic

#### ✅ CORRECT: Pydantic model for complex inputs
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class CreateIssueInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=256, description="Issue title")
    body: Optional[str] = Field(None, description="Issue body in markdown")
    labels: Optional[List[str]] = Field(None, description="Labels to apply")
    assignees: Optional[List[str]] = Field(None, description="GitHub usernames")
```

---

## 4. Error Handling

### 4.1 TypeScript Error Handling

#### ✅ CORRECT: Actionable error messages
```typescript
server.tool("get_user", "Get user by ID", GetUserSchema, async ({ userId }) => {
  try {
    const user = await apiClient.getUser(userId);
    return { content: [{ type: "text", text: JSON.stringify(user) }] };
  } catch (error) {
    if (error.status === 404) {
      return {
        content: [{ type: "text", text: `User not found: ${userId}. Verify the user ID exists.` }],
        isError: true
      };
    }
    if (error.status === 401) {
      return {
        content: [{ type: "text", text: "Authentication failed. Check API credentials." }],
        isError: true
      };
    }
    throw error;
  }
});
```

#### ❌ INCORRECT: Generic error handling
```typescript
try {
  // ...
} catch (error) {
  return { content: [{ type: "text", text: "Error occurred" }], isError: true };
}
```

### 4.2 Python Error Handling

#### ✅ CORRECT: Specific exception handling
```python
@mcp.tool()
async def get_user(user_id: str) -> str:
    """Get user by ID."""
    try:
        user = await api_client.get_user(user_id)
        return json.dumps(user)
    except NotFoundError:
        raise McpError(f"User not found: {user_id}. Verify the user ID exists.")
    except AuthenticationError:
        raise McpError("Authentication failed. Check API credentials.")
```

---

## 5. Tool Annotations

### 5.1 Tool Hints

#### ✅ CORRECT: Proper annotations
```typescript
server.tool(
  "delete_resource",
  "Permanently deletes a resource",
  DeleteSchema,
  async (args) => { /* ... */ },
  {
    annotations: {
      readOnlyHint: false,
      destructiveHint: true,
      idempotentHint: false,
      openWorldHint: false
    }
  }
);
```

#### ✅ CORRECT: Read-only tool
```typescript
server.tool(
  "list_resources",
  "Lists all resources",
  ListSchema,
  async (args) => { /* ... */ },
  {
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    }
  }
);
```

---

## 6. Transport Configuration

### 6.1 stdio Transport (Local)

#### ✅ CORRECT: stdio for local servers
```typescript
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const transport = new StdioServerTransport();
await server.connect(transport);
```

#### ✅ CORRECT: Python stdio
```python
mcp.run(transport="stdio")
```

### 6.2 Streamable HTTP Transport (Remote)

#### ✅ CORRECT: HTTP for remote servers
```typescript
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamable-http.js";

const transport = new StreamableHTTPServerTransport({
  sessionIdHeader: "X-Session-Id"
});
```

---

## 7. Authentication

### 7.1 API Key from Environment

#### ✅ CORRECT: Read from environment
```typescript
const apiKey = process.env.MY_SERVICE_API_KEY;
if (!apiKey) {
  throw new Error("MY_SERVICE_API_KEY environment variable required");
}
```

```python
import os

api_key = os.environ.get("MY_SERVICE_API_KEY")
if not api_key:
    raise ValueError("MY_SERVICE_API_KEY environment variable required")
```

#### ❌ INCORRECT: Hardcoded credentials
```typescript
const apiKey = "sk-hardcoded-key";  // Never do this
```

---

## 8. Response Format

### 8.1 Text Content

#### ✅ CORRECT: Structured text response
```typescript
return {
  content: [{
    type: "text",
    text: JSON.stringify(result, null, 2)
  }]
};
```

### 8.2 Multiple Content Items

#### ✅ CORRECT: Multiple content types
```typescript
return {
  content: [
    { type: "text", text: "## Results\n" },
    { type: "text", text: JSON.stringify(data) }
  ]
};
```

---

## 9. Output Schema

### 9.1 Structured Output

#### ✅ CORRECT: Define output schema for structured data
```typescript
const OutputSchema = z.object({
  users: z.array(z.object({
    id: z.string(),
    name: z.string(),
    email: z.string()
  })),
  total: z.number()
});

server.tool(
  "list_users",
  "List all users",
  InputSchema,
  async (args) => {
    const result = await fetchUsers();
    return {
      content: [{ type: "text", text: JSON.stringify(result) }],
      structuredContent: result
    };
  },
  { outputSchema: OutputSchema }
);
```

---

## 10. Testing

### 10.1 MCP Inspector

#### ✅ CORRECT: Test with inspector
```bash
# TypeScript
npx @modelcontextprotocol/inspector node dist/index.js

# Python
npx @modelcontextprotocol/inspector python -m my_mcp_server
```

### 10.2 Syntax Verification

#### ✅ CORRECT: Pre-flight checks
```bash
# TypeScript
npm run build

# Python
python -m py_compile src/my_mcp_server/server.py
```
