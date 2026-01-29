# Tool Calling with Azure AI Inference

Patterns for function/tool calling with chat completions.

## Basic Tool Definition

```python
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage, UserMessage, AssistantMessage, ToolMessage,
    ChatCompletionsToolDefinition, FunctionDefinition
)
from azure.core.credentials import AzureKeyCredential
import json

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

# Define tools
tools = [
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_weather",
            description="Get the current weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g., 'Seattle, WA'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        )
    )
]
```

## Tool Call Flow

```python
def process_with_tools(client, user_message: str, tools: list) -> str:
    """Complete tool call flow: request -> execute -> respond."""
    messages = [
        SystemMessage(content="You are a helpful assistant with tool access."),
        UserMessage(content=user_message)
    ]
    
    # Step 1: Initial request
    response = client.complete(messages=messages, tools=tools)
    assistant_message = response.choices[0].message
    
    # Step 2: Check for tool calls
    if not assistant_message.tool_calls:
        return assistant_message.content
    
    # Step 3: Execute tools and collect results
    messages.append(AssistantMessage(
        content=assistant_message.content,
        tool_calls=assistant_message.tool_calls
    ))
    
    for tool_call in assistant_message.tool_calls:
        # Execute the tool
        result = execute_tool(
            tool_call.function.name,
            json.loads(tool_call.function.arguments)
        )
        
        # Add result to messages
        messages.append(ToolMessage(
            tool_call_id=tool_call.id,
            content=json.dumps(result)
        ))
    
    # Step 4: Get final response
    final_response = client.complete(messages=messages, tools=tools)
    return final_response.choices[0].message.content


def execute_tool(name: str, args: dict) -> dict:
    """Execute a tool by name with given arguments."""
    if name == "get_weather":
        # Simulated weather lookup
        return {
            "location": args["location"],
            "temperature": 72,
            "unit": args.get("unit", "fahrenheit"),
            "condition": "sunny"
        }
    raise ValueError(f"Unknown tool: {name}")
```

## Multiple Tools

```python
tools = [
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_weather",
            description="Get current weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        )
    ),
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="search_web",
            description="Search the web for information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        )
    ),
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="calculate",
            description="Perform mathematical calculations",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        )
    )
]
```

## Parallel Tool Calls

```python
def process_parallel_tools(client, messages: list, tools: list) -> str:
    """Handle multiple tool calls in a single response."""
    response = client.complete(messages=messages, tools=tools)
    assistant_message = response.choices[0].message
    
    if not assistant_message.tool_calls:
        return assistant_message.content
    
    # Add assistant message with all tool calls
    messages.append(AssistantMessage(
        content=assistant_message.content,
        tool_calls=assistant_message.tool_calls
    ))
    
    # Execute all tools (can be parallelized)
    for tool_call in assistant_message.tool_calls:
        result = execute_tool(
            tool_call.function.name,
            json.loads(tool_call.function.arguments)
        )
        
        messages.append(ToolMessage(
            tool_call_id=tool_call.id,
            content=json.dumps(result)
        ))
    
    # Get response incorporating all tool results
    final_response = client.complete(messages=messages, tools=tools)
    return final_response.choices[0].message.content
```

## Async Tool Execution

```python
import asyncio
from azure.ai.inference.aio import ChatCompletionsClient

async def process_tools_async(client, user_message: str, tools: list) -> str:
    """Async tool processing with parallel execution."""
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content=user_message)
    ]
    
    response = await client.complete(messages=messages, tools=tools)
    assistant_message = response.choices[0].message
    
    if not assistant_message.tool_calls:
        return assistant_message.content
    
    messages.append(AssistantMessage(
        content=assistant_message.content,
        tool_calls=assistant_message.tool_calls
    ))
    
    # Execute tools in parallel
    async def execute_and_format(tool_call):
        result = await execute_tool_async(
            tool_call.function.name,
            json.loads(tool_call.function.arguments)
        )
        return ToolMessage(
            tool_call_id=tool_call.id,
            content=json.dumps(result)
        )
    
    tool_messages = await asyncio.gather(*[
        execute_and_format(tc) for tc in assistant_message.tool_calls
    ])
    
    messages.extend(tool_messages)
    
    final_response = await client.complete(messages=messages, tools=tools)
    return final_response.choices[0].message.content
```

## Tool Choice Control

```python
from azure.ai.inference.models import ChatCompletionsToolChoicePreset

# Let model decide (default)
response = client.complete(
    messages=messages,
    tools=tools,
    tool_choice=ChatCompletionsToolChoicePreset.AUTO
)

# Force no tools
response = client.complete(
    messages=messages,
    tools=tools,
    tool_choice=ChatCompletionsToolChoicePreset.NONE
)

# Force specific tool
response = client.complete(
    messages=messages,
    tools=tools,
    tool_choice={
        "type": "function",
        "function": {"name": "get_weather"}
    }
)

# Require at least one tool call
response = client.complete(
    messages=messages,
    tools=tools,
    tool_choice=ChatCompletionsToolChoicePreset.REQUIRED
)
```

## Tool Choice Options

| Value | Behavior |
|-------|----------|
| `AUTO` | Model decides whether to call tools |
| `NONE` | Model won't call any tools |
| `REQUIRED` | Model must call at least one tool |
| `{"type": "function", "function": {"name": "..."}}` | Force specific tool |

## Structured Tool Registry

```python
from typing import Callable, Any
from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    handler: Callable[..., Any]

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(
        self,
        name: str,
        description: str,
        parameters: dict
    ) -> Callable:
        """Decorator to register a tool handler."""
        def decorator(func: Callable) -> Callable:
            self._tools[name] = Tool(
                name=name,
                description=description,
                parameters=parameters,
                handler=func
            )
            return func
        return decorator
    
    def get_definitions(self) -> list[ChatCompletionsToolDefinition]:
        """Get tool definitions for API call."""
        return [
            ChatCompletionsToolDefinition(
                function=FunctionDefinition(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.parameters
                )
            )
            for tool in self._tools.values()
        ]
    
    def execute(self, name: str, arguments: dict) -> Any:
        """Execute a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name].handler(**arguments)


# Usage
registry = ToolRegistry()

@registry.register(
    name="get_weather",
    description="Get weather for a location",
    parameters={
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
)
def get_weather(location: str) -> dict:
    return {"location": location, "temp": 72, "condition": "sunny"}

@registry.register(
    name="calculate",
    description="Evaluate math expression",
    parameters={
        "type": "object",
        "properties": {
            "expression": {"type": "string"}
        },
        "required": ["expression"]
    }
)
def calculate(expression: str) -> dict:
    # Safe eval for math only
    result = eval(expression, {"__builtins__": {}}, {})
    return {"expression": expression, "result": result}
```

## Multi-Turn Tool Conversation

```python
class ToolConversation:
    def __init__(self, client, tools: list, system_prompt: str = ""):
        self.client = client
        self.tools = tools
        self.messages = []
        if system_prompt:
            self.messages.append(SystemMessage(content=system_prompt))
    
    def chat(self, user_input: str) -> str:
        """Process user input with potential tool calls."""
        self.messages.append(UserMessage(content=user_input))
        
        while True:
            response = self.client.complete(
                messages=self.messages,
                tools=self.tools
            )
            assistant_message = response.choices[0].message
            
            # No tool calls - return response
            if not assistant_message.tool_calls:
                self.messages.append(AssistantMessage(
                    content=assistant_message.content
                ))
                return assistant_message.content
            
            # Process tool calls
            self.messages.append(AssistantMessage(
                content=assistant_message.content,
                tool_calls=assistant_message.tool_calls
            ))
            
            for tool_call in assistant_message.tool_calls:
                result = self._execute_tool(tool_call)
                self.messages.append(ToolMessage(
                    tool_call_id=tool_call.id,
                    content=json.dumps(result)
                ))
    
    def _execute_tool(self, tool_call) -> dict:
        """Override to implement tool execution."""
        raise NotImplementedError
```

## Error Handling

```python
def safe_tool_execution(tool_call) -> ToolMessage:
    """Execute tool with error handling."""
    try:
        args = json.loads(tool_call.function.arguments)
        result = execute_tool(tool_call.function.name, args)
        return ToolMessage(
            tool_call_id=tool_call.id,
            content=json.dumps(result)
        )
    except json.JSONDecodeError as e:
        return ToolMessage(
            tool_call_id=tool_call.id,
            content=json.dumps({
                "error": "Invalid JSON in arguments",
                "details": str(e)
            })
        )
    except ValueError as e:
        return ToolMessage(
            tool_call_id=tool_call.id,
            content=json.dumps({
                "error": "Tool execution failed",
                "details": str(e)
            })
        )
    except Exception as e:
        return ToolMessage(
            tool_call_id=tool_call.id,
            content=json.dumps({
                "error": "Unexpected error",
                "type": type(e).__name__,
                "details": str(e)
            })
        )
```

## Streaming with Tools

```python
def stream_with_tools(client, messages: list, tools: list):
    """Handle streaming responses with tool calls."""
    content_chunks = []
    tool_calls = {}
    
    response = client.complete(
        stream=True,
        messages=messages,
        tools=tools
    )
    
    for update in response:
        if not update.choices:
            continue
        
        delta = update.choices[0].delta
        
        # Collect content
        if delta.content:
            content_chunks.append(delta.content)
            print(delta.content, end="", flush=True)
        
        # Collect tool calls incrementally
        if delta.tool_calls:
            for tc in delta.tool_calls:
                idx = tc.index
                if idx not in tool_calls:
                    tool_calls[idx] = {
                        "id": tc.id,
                        "function": {"name": "", "arguments": ""}
                    }
                if tc.function:
                    if tc.function.name:
                        tool_calls[idx]["function"]["name"] = tc.function.name
                    if tc.function.arguments:
                        tool_calls[idx]["function"]["arguments"] += tc.function.arguments
    
    print()
    return {
        "content": "".join(content_chunks),
        "tool_calls": list(tool_calls.values()) if tool_calls else None
    }
```

## Best Practices

1. **Validate arguments** — Don't trust model-generated JSON blindly
2. **Handle errors gracefully** — Return error info as tool result, let model adapt
3. **Use descriptive names** — Clear function names help model choose correctly
4. **Limit tool count** — Too many tools confuse the model (aim for <10)
5. **Provide examples** — Include example values in parameter descriptions
6. **Set timeouts** — External tool calls should have timeouts
7. **Log tool usage** — Track which tools are called for debugging
8. **Use tool_choice** — Force specific tools when intent is clear
