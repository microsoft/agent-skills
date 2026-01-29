# Streaming Reference

Streaming patterns for real-time responses in the Azure AI Agents SDK.

## Table of Contents

- [Basic Streaming](#basic-streaming)
- [Event Handler Class](#event-handler-class)
- [Event Handler with Functions](#event-handler-with-functions)
- [Iteration-Based Streaming](#iteration-based-streaming)
- [Async Streaming](#async-streaming)
- [Event Types Reference](#event-types-reference)

---

## Basic Streaming

Simple streaming with a custom event handler.

```python
from azure.ai.agents import AgentEventHandler

class MyHandler(AgentEventHandler):
    def on_message_delta(self, delta):
        if delta.text:
            print(delta.text.value, end="", flush=True)

# Use streaming context manager
with client.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
    event_handler=MyHandler(),
) as stream:
    stream.until_done()
```

---

## Event Handler Class

Complete event handler with all callback methods.

```python
from azure.ai.agents import AgentEventHandler
from typing import Any

class StreamHandler(AgentEventHandler):
    """Full-featured event handler for streaming."""
    
    def on_thread_message(self, message):
        """Called when a message is created or completed."""
        print(f"Message {message.status}: {message.id}")
    
    def on_thread_run(self, run):
        """Called when run status changes."""
        print(f"Run status: {run.status}")
    
    def on_run_step(self, step):
        """Called when a run step is created or completed."""
        print(f"Step {step.type}: {step.status}")
    
    def on_message_delta(self, delta):
        """Called for each text chunk during streaming."""
        if delta.text:
            print(delta.text.value, end="", flush=True)
    
    def on_error(self, data: str):
        """Called when an error occurs."""
        print(f"Error: {data}")
    
    def on_done(self):
        """Called when streaming completes."""
        print("\nDone!")
    
    def on_unhandled_event(self, event_type: str, event_data: Any):
        """Called for any unhandled event types."""
        print(f"Unhandled: {event_type}")
```

---

## Event Handler with Functions

Handle function calls during streaming.

```python
from azure.ai.agents import AgentEventHandler, FunctionTool, ToolSet

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72F, sunny"

functions = FunctionTool(functions=[get_weather])
toolset = ToolSet()
toolset.add(functions)

class FunctionHandler(AgentEventHandler):
    def __init__(self):
        super().__init__()
        self.current_text = ""
    
    def on_message_delta(self, delta):
        if delta.text:
            self.current_text += delta.text.value
            print(delta.text.value, end="", flush=True)
    
    def on_thread_run(self, run):
        if run.status == "requires_action":
            print(f"\nFunction called, handling...")

# Create agent with toolset
agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    toolset=toolset,
)

# Stream with toolset for auto function execution
with client.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
    toolset=toolset,  # Enables auto function execution
    event_handler=FunctionHandler(),
) as stream:
    stream.until_done()
```

---

## Iteration-Based Streaming

Alternative to event handler - iterate over events directly.

```python
# Iterate without handler
with client.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
) as stream:
    for event_type, event_data, _ in stream:
        if event_type == "thread.message.delta":
            delta = event_data
            if delta.delta.content:
                for content_part in delta.delta.content:
                    if content_part.type == "text" and content_part.text:
                        print(content_part.text.value, end="", flush=True)
        elif event_type == "thread.run.completed":
            print("\nCompleted!")
        elif event_type == "error":
            print(f"\nError: {event_data}")
```

### With Run ID Access

```python
with client.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
) as stream:
    # Access run ID immediately
    print(f"Run ID: {stream.get_run_id()}")
    
    for event_type, event_data, _ in stream:
        # Process events...
        pass
```

---

## Async Streaming

Streaming with the async client.

```python
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents import AsyncAgentEventHandler

class AsyncHandler(AsyncAgentEventHandler):
    async def on_message_delta(self, delta):
        if delta.text:
            print(delta.text.value, end="", flush=True)
    
    async def on_error(self, data: str):
        print(f"Error: {data}")

async def main():
    async with AgentsClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    ) as client:
        agent = await client.create_agent(...)
        thread = await client.threads.create()
        await client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello!",
        )
        
        async with client.runs.stream(
            thread_id=thread.id,
            agent_id=agent.id,
            event_handler=AsyncHandler(),
        ) as stream:
            await stream.until_done()
```

### Async Iteration

```python
async with client.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
) as stream:
    async for event_type, event_data, _ in stream:
        if event_type == "thread.message.delta":
            # Handle delta
            pass
```

---

## Event Types Reference

| Event Type | Event Data | Description |
|------------|------------|-------------|
| `thread.run.created` | `Run` | Run was created |
| `thread.run.queued` | `Run` | Run is queued |
| `thread.run.in_progress` | `Run` | Run started executing |
| `thread.run.requires_action` | `Run` | Run needs function call results |
| `thread.run.completed` | `Run` | Run finished successfully |
| `thread.run.failed` | `Run` | Run failed |
| `thread.run.cancelling` | `Run` | Run is being cancelled |
| `thread.run.cancelled` | `Run` | Run was cancelled |
| `thread.run.expired` | `Run` | Run expired |
| `thread.run.step.created` | `RunStep` | Step was created |
| `thread.run.step.in_progress` | `RunStep` | Step started |
| `thread.run.step.delta` | `RunStepDelta` | Step incremental update |
| `thread.run.step.completed` | `RunStep` | Step finished |
| `thread.run.step.failed` | `RunStep` | Step failed |
| `thread.message.created` | `Message` | Message was created |
| `thread.message.in_progress` | `Message` | Message being generated |
| `thread.message.delta` | `MessageDelta` | Message text chunk |
| `thread.message.completed` | `Message` | Message finished |
| `error` | `str` | Error occurred |
| `done` | `str` | Stream completed |

### MessageDelta Structure

```python
# delta from on_message_delta
delta.id            # Message ID
delta.text          # TextDeltaBlock or None
delta.text.value    # Actual text content
delta.text.annotations  # Any annotations
```

### Run Structure for requires_action

```python
# run from on_thread_run when status == "requires_action"
run.required_action.submit_tool_outputs.tool_calls  # List of tool calls
# Each tool call has:
#   .id            - Tool call ID
#   .type          - "function"
#   .function.name - Function name
#   .function.arguments - JSON string of arguments
```

---

## Complete Example

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient, AgentEventHandler, FunctionTool, ToolSet

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72F, sunny"

class FullHandler(AgentEventHandler):
    def __init__(self):
        super().__init__()
        self.response_text = ""
    
    def on_thread_run(self, run):
        if run.status == "completed":
            print(f"\n[Run completed]")
        elif run.status == "failed":
            print(f"\n[Run failed: {run.last_error}]")
    
    def on_message_delta(self, delta):
        if delta.text:
            self.response_text += delta.text.value
            print(delta.text.value, end="", flush=True)
    
    def on_error(self, data):
        print(f"\n[Error: {data}]")

# Setup
functions = FunctionTool(functions=[get_weather])
toolset = ToolSet()
toolset.add(functions)

client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

agent = client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="streaming-agent",
    instructions="You help with weather queries.",
    toolset=toolset,
)

thread = client.threads.create()
client.messages.create(
    thread_id=thread.id,
    role="user",
    content="What's the weather in Seattle?",
)

handler = FullHandler()
with client.runs.stream(
    thread_id=thread.id,
    agent_id=agent.id,
    toolset=toolset,
    event_handler=handler,
) as stream:
    stream.until_done()

print(f"\nFull response: {handler.response_text}")

# Cleanup
client.delete_agent(agent.id)
```
