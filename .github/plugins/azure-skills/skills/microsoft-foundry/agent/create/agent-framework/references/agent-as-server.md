# Agent as HTTP Server Best Practices

Converting an Agent-Framework-based Agent/Workflow/App to run as an HTTP server requires code changes to host the agent as a RESTful HTTP server.

(This doc applies to Python SDK only)

## Code Changes

### Run Workflow as Agent

Agent Framework provides a way to run a whole workflow as agent, via appending `.as_agent()` to the `WorkflowBuilder`, like:

```python
agent = (
    WorkflowBuilder()
    .add_edge(...)
    ...
    .set_start_executor(...)
    .build()
    .as_agent() # here it is
)
```

Then, `azure.ai.agentserver.agentframework` package provides way to run above agent as an http server and receives user input direct from http request:

```text
# requirements.txt
# pin version to avoid breaking changes or compatibility issues
azure-ai-agentserver-agentframework==1.0.0b10
azure-ai-agentserver-core==1.0.0b10
```

```python
from azure.ai.agentserver.agentframework import from_agent_framework

# async method
await from_agent_framework(agent).run_async()

# or, sync method
from_agent_framework(agent).run()
```

Notes:
- User may or may not have `azure.ai.agentserver.agentframework` installed, if not, install it via or equivalent with other package managers:
  `pip install azure-ai-agentserver-core==1.0.0b10 azure-ai-agentserver-agentframework==1.0.0b10`

- When changing the startup command line, make sure the http server mode is the default one (without any additional flag), which is better for further development (like local debugging) and deployment (like containerization and deploy to Microsoft Foundry).

- If loading env variables from `.env` file, like `load_dotenv()`, make sure set `override=True` to let the env variables work in deployed environment, like `load_dotenv(override=True)`

### Request/Response Requirements

To handle http request as user input, the workflow's starter executor should have handler to support `list[ChatMessage]` as input, like:

```python
    @handler
    async def some_handler(self, messages: list[ChatMessage], ctx: WorkflowContext[...]) -> ...:
```

Also, to let http response returns agent output, need to add `AgentRunUpdateEvent` to context, like:

```python
    from agent_framework import AgentRunUpdateEvent, AgentRunResponseUpdate, TextContent, Role
    ...
    response = await self.agent.run(messages)
    for message in response.messages:
        if message.role == Role.ASSISTANT:
            await ctx.add_event(
                AgentRunUpdateEvent(
                    self.id,
                    data=AgentRunResponseUpdate(
                        contents=[TextContent(text=f"Agent: {message.contents[-1].text}")],
                        role=Role.ASSISTANT,
                        response_id=str(uuid4()),
                    ),
                )
            )
```

## Notes

- This step focuses on code changes to prepare an HTTP server-based agent, not actually containerizing or deploying, thus no need to generate extra files.
- Pin `agent-framework` to version `1.0.0b260107` to avoid breaking renaming changes like `AgentRunResponseUpdate`/`AgentResponseUpdate`, `create_agent`/`as_agent`, etc.
