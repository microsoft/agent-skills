# Workflow with Agents and Streaming

Wrap chat agents (via `AzureAIClient`) inside workflow executors and consume streaming events. Use this when building workflows where each node is backed by an AI agent.

> 💡 **Tip:** Use `DefaultAzureCredential` from `azure.identity.aio` (not `azure.identity`) — `AzureAIClient` requires async credentials.

## Pattern: Writer → Reviewer Pipeline

A Writer agent generates content, then a Reviewer agent finalizes the result. Uses `run_stream` to observe events in real-time.

```python
from agent_framework import (
    ChatAgent, ChatMessage, Executor, ExecutorFailedEvent,
    WorkflowBuilder, WorkflowContext, WorkflowFailedEvent,
    WorkflowOutputEvent, WorkflowRunState, WorkflowStatusEvent, handler,
)
from agent_framework.azure import AzureAIClient
from azure.identity.aio import DefaultAzureCredential
from typing_extensions import Never

class Writer(Executor):
    agent: ChatAgent

    def __init__(self, client: AzureAIClient, id: str = "writer"):
        self.agent = client.create_agent(
            name="ContentWriterAgent",
            instructions="You are an excellent content writer.",
        )
        super().__init__(id=id)

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[list[ChatMessage]]) -> None:
        messages: list[ChatMessage] = [message]
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        await ctx.send_message(messages)

class Reviewer(Executor):
    agent: ChatAgent

    def __init__(self, client: AzureAIClient, id: str = "reviewer"):
        self.agent = client.create_agent(
            name="ContentReviewerAgent",
            instructions="You are an excellent content reviewer.",
        )
        super().__init__(id=id)

    @handler
    async def handle(self, messages: list[ChatMessage], ctx: WorkflowContext[Never, str]) -> None:
        response = await self.agent.run(messages)
        await ctx.yield_output(response.text)

async def main():
    client = AzureAIClient(credential=DefaultAzureCredential())
    writer = Writer(client)
    reviewer = Reviewer(client)
    workflow = WorkflowBuilder().set_start_executor(writer).add_edge(writer, reviewer).build()

    async for event in workflow.run_stream(
        ChatMessage(role="user", text="Create a slogan for a new electric SUV.")
    ):
        if isinstance(event, WorkflowOutputEvent):
            print(f"Output: {event.data}")
        elif isinstance(event, WorkflowStatusEvent):
            print(f"State: {event.state}")
        elif isinstance(event, (ExecutorFailedEvent, WorkflowFailedEvent)):
            print(f"Error: {event.details.message}")
```

Sample output:
```
State: WorkflowRunState.IN_PROGRESS
Output: Drive the Future. Affordable Adventure, Electrified.
State: WorkflowRunState.IDLE
```
