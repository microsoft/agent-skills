# Python Agent Code Samples

## Common Patterns

These patterns are shared across all providers. Define them once and reuse.

### Tool Definition
``` python
from random import randint
from typing import Annotated

def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."
```

### MCP Tools Setup
```python
from agent_framework import MCPStdioTool, ToolProtocol, MCPStreamableHTTPTool
from typing import Any

def create_mcp_tools() -> list[ToolProtocol | Any]:
    return [
        MCPStdioTool(
            name="Playwright MCP",
            description="provides browser automation capabilities using Playwright",
            command="npx",
            args=["-y", "@playwright/mcp@latest"]
        ),
        MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            description="bring trusted and up-to-date information directly from Microsoft's official documentation",
            url="https://learn.microsoft.com/api/mcp",
        )
    ]
```

### Thread Pattern (Multi-turn Conversation)
``` python
# Create a new thread that will be reused
thread = agent.get_new_thread()

# First conversation
async for chunk in agent.run_stream("What's the weather like in Seattle?", thread=thread):
    if chunk.text:
        print(chunk.text, end="", flush=True)

# Second conversation - maintains context
async for chunk in agent.run_stream("Pardon?", thread=thread):
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

---

## Foundry

Connect foundry model using `AzureAIClient`. (Legacy `AzureAIAgentClient` is deprecated, use `AzureAIClient`)

``` python
from agent_framework.azure import AzureAIClient
from azure.identity.aio import DefaultAzureCredential

async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AzureAIClient(
            project_endpoint="<your-foundry-project-endpoint>",
            model_deployment_name="<your-foundry-model-deployment>",
            credential=credential,
        ).create_agent(
            name="MyAgent",
            instructions="You are a helpful agent.",
            tools=[get_weather],           # add tools
            # tools=create_mcp_tools(),    # or use MCP tools
        ) as agent,
    ):
        thread = agent.get_new_thread()
        async for chunk in agent.run_stream("hello", thread=thread):
            if chunk.text:
                print(chunk.text, end="", flush=True)
```

---

## Important Tips

Agent Framework supports various implementation patterns. These are quite useful tips to ensure stability and avoid common errors:

- If using `AzureAIClient` (e.g., connect to Foundry project), use `DefaultAzureCredential` from `azure.identity.aio` (Not `azure.identity`) since the client requires async credential.
- Agent instance can be created via either `client.create_agent(...)` method or `ChatAgent(...)` constructor.
- If using `AzureAIClient` to create Foundry agent, the agent name "must start and end with alphanumeric characters, can contain hyphens in the middle, and must not exceed 63 characters". E.g., good names: ["SampleAgent", "agent-1", "myagent"], and bad names: ["-agent", "agent-", "sample_agent"].
